from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any

try:
    from openai import APIError, AsyncOpenAI  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore[misc,assignment]

    class APIError(Exception):  # type: ignore[no-redef]
        pass

from .config import settings
from . import ai_settings


logger = logging.getLogger(__name__)

MAX_CONCURRENT_REQUESTS_PER_USER = 2
_user_semaphores: dict[str, asyncio.Semaphore] = {}
_semaphore_lock = asyncio.Lock()


class UserConcurrencyLimitExceeded(Exception):
    pass


async def _get_user_semaphore(user_id: str) -> asyncio.Semaphore:
    async with _semaphore_lock:
        if user_id not in _user_semaphores:
            _user_semaphores[user_id] = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS_PER_USER)
        return _user_semaphores[user_id]


client: AsyncOpenAI | None = None
if AsyncOpenAI is None:
    logger.warning('未安装 openai 依赖，OpenAI 客户端不可用。')
elif settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your_openai_api_key_here':
    try:
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        logger.info('OpenAI 客户端初始化成功。')
    except Exception as exc:
        logger.error('初始化 OpenAI 客户端失败: %s', exc)
        client = None
else:
    logger.warning('OPENAI_API_KEY 未设置或为占位符，OpenAI 客户端未初始化。')


def is_text_ai_enabled(user_id: str | None = None) -> bool:
    return client is not None or ai_settings.get_custom_ai_config(user_id) is not None


def _extract_json_from_response(response_str: str) -> str | None:
    if '```json' in response_str:
        start_pos = response_str.find('```json') + 7
        end_pos = response_str.find('```', start_pos)
        if end_pos != -1:
            return response_str[start_pos:end_pos].strip()
    start_pos = response_str.find('{')
    end_pos = response_str.rfind('}')
    if start_pos != -1 and end_pos != -1 and end_pos > start_pos:
        return response_str[start_pos:end_pos + 1].strip()
    return None


async def get_ai_response(
    prompt: str,
    history: list[dict] | None = None,
    model=settings.OPENAI_MODEL,
    force_json=True,
    user_id: str | None = None,
) -> str:
    custom_config = ai_settings.get_custom_ai_config(user_id)
    if not client and not custom_config:
        return '错误：OpenAI客户端未初始化。请在 backend/.env 文件中正确设置您的 OPENAI_API_KEY。'
    request_client = client
    request_model = model
    if custom_config:
        if AsyncOpenAI is None:
            return '错误：未安装 openai 依赖，无法使用自定义 API。'
        request_client = AsyncOpenAI(
            api_key=custom_config['api_key'],
            base_url=custom_config['base_url'],
        )
        request_model = custom_config['model'] or model

    if user_id:
        semaphore = await _get_user_semaphore(user_id)
        async with semaphore:
            logger.debug('用户 %s 获取 LLM 请求槽位，当前可用: %s', user_id, semaphore._value)
            return await _get_ai_response_impl(prompt, history, request_model, force_json, request_client)
    return await _get_ai_response_impl(prompt, history, request_model, force_json, request_client)


def _test_config(user_id: str | None, payload: dict[str, Any] | None = None) -> dict[str, str]:
    payload = payload or {}
    profile_id = str(payload.get('profile_id') or '').strip()
    if profile_id:
        custom_config = ai_settings.get_profile_ai_config(user_id, profile_id, include_disabled=True)
        api_key = str(payload.get('api_key') or (custom_config or {}).get('api_key') or '').strip()
    else:
        custom_config = ai_settings.get_custom_ai_config(user_id)
        api_key = str(payload.get('api_key') or (custom_config or {}).get('api_key') or settings.OPENAI_API_KEY or '').strip()
    base_url = str(payload.get('base_url') or (custom_config or {}).get('base_url') or settings.OPENAI_BASE_URL).strip()
    model = str(payload.get('model') or (custom_config or {}).get('model') or settings.OPENAI_MODEL).strip()
    return {'api_key': api_key, 'base_url': base_url, 'model': model}


async def test_text_ai_connection(user_id: str | None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    config = _test_config(user_id, payload)
    if not config['api_key'] or config['api_key'] == 'your_openai_api_key_here':
        raise ValueError('请先填写或保存 API Key。')
    if AsyncOpenAI is None:
        raise ValueError('未安装 openai 依赖，无法测试自定义 API。')

    request_client = AsyncOpenAI(
        api_key=config['api_key'],
        base_url=config['base_url'],
        timeout=15.0,
    )
    try:
        response = await request_client.chat.completions.create(
            model=config['model'],
            messages=[
                {'role': 'system', 'content': '你是一个连接测试助手。'},
                {'role': 'user', 'content': '请只回复“连接成功”。'},
            ],
        )
        content = (response.choices[0].message.content or '').strip()
        return {
            'ok': True,
            'message': '连接成功' + (('：' + content) if content else ''),
            'base_url': config['base_url'],
            'model': config['model'],
        }
    except Exception as exc:
        logger.error('AI API 连接测试失败: %s', exc, exc_info=True)
        return {
            'ok': False,
            'message': '连接失败：' + str(exc),
            'base_url': config['base_url'],
            'model': config['model'],
        }


async def _get_ai_response_impl(
    prompt: str,
    history: list[dict] | None = None,
    model=settings.OPENAI_MODEL,
    force_json=True,
    api_client: Any | None = None,
) -> str:
    active_client = api_client or client
    if not active_client:
        return '错误：OpenAI客户端未初始化。'
    messages = []
    if history:
        messages.extend(history)
    messages.append({'role': 'user', 'content': prompt})

    total_tokens = sum(len(message['content']) for message in messages)
    logger.debug('发送到 OpenAI 的消息总字符数: %s', total_tokens)

    max_loop = 10000
    while total_tokens > 100000 and max_loop > 0:
        if len(messages) <= 2:
            break
        random_id = random.randint(1, len(messages) - 2)
        total_tokens -= len(messages[random_id]['content'])
        messages.pop(random_id)
        max_loop -= 1

    if max_loop == 0:
        raise ValueError('对话历史过长，无法通过删除消息节省足够的上下文。')

    max_retries = 7
    base_delay = 1

    for attempt in range(max_retries):
        selected_model = model
        if ',' in model:
            model_options = [item.strip() for item in model.split(',') if item.strip()]
            if model_options:
                selected_model = model_options[0] if attempt == 0 else random.choice(model_options)
        try:
            response = await active_client.chat.completions.create(
                model=selected_model,
                messages=messages,
            )
            ai_message = response.choices[0].message.content
            if not ai_message:
                raise ValueError('AI 响应为空')
            ret = ai_message.strip()
            if '<think>' in ret and '</think>' in ret:
                ret = ret[ret.rfind('</think>') + 8:].strip()

            if force_json:
                try:
                    json_part = _extract_json_from_response(ret)
                    if json_part and json.loads(json_part):
                        return ret
                    raise ValueError('未找到有效的 JSON 部分')
                except Exception as exc:
                    raise ValueError('解析 AI 响应时出错: ' + str(exc)) from exc
            return ret

        except APIError as exc:
            logger.error('OpenAI API 错误 (尝试 %s/%s): %s', attempt + 1, max_retries, exc)
            if attempt == max_retries - 1:
                return '错误：AI服务出现问题。详情: ' + str(exc)
            delay = base_delay * (2**attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)

        except Exception as exc:
            logger.error('联系 OpenAI 时发生意外错误 (尝试 %s/%s): %s', attempt + 1, max_retries, exc, exc_info=True)
            if attempt == max_retries - 1:
                return '错误：发生意外错误。详情: ' + str(exc)
            delay = base_delay * (2**attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)

    return '错误：AI服务未返回可用结果。'
