from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from . import fate_mapper, openai_client


PROMPT_DIR = Path(__file__).parent / 'prompts'


def _load_prompt(filename: str) -> str:
    try:
        return (PROMPT_DIR / filename).read_text(encoding='utf-8')
    except OSError:
        return ''


def _extract_json_object(text: str) -> dict[str, Any] | None:
    raw = str(text or '').strip()
    if not raw:
        return None
    if '```json' in raw:
        start = raw.find('```json') + 7
        end = raw.find('```', start)
        if end != -1:
            raw = raw[start:end].strip()
    else:
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1 and end > start:
            raw = raw[start:end + 1]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _string_list(value: Any, fallback: list[str] | None = None, limit: int = 12) -> list[str]:
    if not isinstance(value, list):
        return list(fallback or [])
    result = [str(item).strip() for item in value if str(item).strip()]
    return result[:limit] or list(fallback or [])


def _event_object(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip().startswith('{') and value.strip().endswith('}'):
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _event_text(value: Any) -> str:
    event = _event_object(value)
    if not event:
        return str(value or '').strip()
    age = event.get('age')
    year = event.get('year')
    main_text = str(event.get('event') or event.get('text') or event.get('summary') or event.get('description') or event.get('title') or '').strip()
    impact = str(event.get('impact') or event.get('effect') or event.get('influence') or event.get('state_effect') or '').strip()
    prefix_parts = []
    if age not in [None, '']:
        prefix_parts.append(str(age) + '岁')
    if year not in [None, '']:
        prefix_parts.append(str(year) + '年')
    prefix = '（'.join(prefix_parts)
    if len(prefix_parts) == 2:
        prefix = prefix_parts[0] + '（' + prefix_parts[1] + '）'
    if prefix and main_text:
        main_text = prefix + '：' + main_text
    elif prefix:
        main_text = prefix
    if impact:
        main_text += ' 影响：' + impact
    return main_text.strip()


def _event_string_list(value: Any, fallback: list[str] | None = None, limit: int = 12) -> list[str]:
    if not isinstance(value, list):
        return list(fallback or [])
    result = [_event_text(item) for item in value]
    result = [item for item in result if item]
    return result[:limit] or list(fallback or [])


def _coerce_life_state(value: Any, fallback: dict[str, int]) -> dict[str, int]:
    if not isinstance(value, dict):
        return fallback.copy()
    result = fallback.copy()
    for key in result.keys():
        if key in value:
            try:
                result[key] = fate_mapper.clamp(int(value[key]))
            except (TypeError, ValueError):
                continue
    return result


class NoAiEnrichmentAdapter:
    async def enrich_chart_analysis(self, session: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any] | None:
        return None

    async def enrich_prelude(self, session: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any] | None:
        return None

    async def enrich_half_year_narrative(self, session: dict[str, Any], latest: dict[str, Any]) -> dict[str, Any] | None:
        return None

    async def enrich_half_year_summary(self, session: dict[str, Any], latest: dict[str, Any]) -> dict[str, Any] | None:
        return None


class OpenAIEnrichmentAdapter(NoAiEnrichmentAdapter):
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def _request_json(self, prompt_file: str, request_data: dict[str, Any], extra_instruction: str = '') -> dict[str, Any] | None:
        prompt = _load_prompt(prompt_file)
        if not prompt:
            return None
        response = await openai_client.get_ai_response(
            prompt + extra_instruction + '\n\n输入 JSON：\n' + json.dumps(request_data, ensure_ascii=False),
            force_json=True,
            user_id=self.user_id,
        )
        return _extract_json_object(response)

    async def enrich_chart_analysis(self, session: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any] | None:
        if not session.get('bazi_chart'):
            return None
        data = await self._request_json(
            'bazi_analyst.txt',
            {
                'birth_info': session.get('birth_info', {}),
                'bazi_chart': session.get('bazi_chart', {}),
                'luck_cycles': session.get('luck_cycles', [])[:6],
                'annual_cycles': session.get('annual_cycles', [])[:10],
                'deterministic_analysis': fallback,
            },
        )
        if not data:
            return None
        balance = data.get('five_element_balance')
        if not isinstance(balance, dict):
            balance = fallback.get('five_element_balance', {})
        return {
            'five_element_balance': balance,
            'day_master_status': str(data.get('day_master_status') or fallback.get('day_master_status') or '中和'),
            'useful_elements': _string_list(data.get('useful_elements'), fallback.get('useful_elements', []), 5),
            'unfavorable_elements': _string_list(data.get('unfavorable_elements'), fallback.get('unfavorable_elements', []), 5),
            'ten_god_focus': _string_list(data.get('ten_god_focus'), fallback.get('ten_god_focus', []), 8),
            'luck_cycle_themes': _string_list(data.get('luck_cycle_themes'), fallback.get('luck_cycle_themes', []), 8),
            'life_topics': _string_list(data.get('life_topics'), fallback.get('life_topics', []), 8),
            'suitable_directions': _string_list(data.get('suitable_directions'), fallback.get('suitable_directions', []), 8),
            'high_risk_fields': _string_list(data.get('high_risk_fields'), fallback.get('high_risk_fields', []), 8),
            'chart_tags': _string_list(data.get('chart_tags'), [], 10),
            'source': 'ai',
        }

    async def enrich_prelude(self, session: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any] | None:
        if not fallback:
            return None
        data = await self._request_json(
            'life_prelude.txt',
            {
                'birth_info': session.get('birth_info', {}),
                'bazi_chart': session.get('bazi_chart', {}),
                'bazi_analysis': session.get('bazi_analysis', {}),
                'chart_tags': session.get('chart_tags', []),
                'luck_cycles': session.get('luck_cycles', [])[:4],
                'annual_cycles': session.get('annual_cycles', [])[:8],
                'start_age': session.get('start_age'),
                'fallback_state': fallback,
            },
        )
        if not data:
            return None
        return {
            'text': str(data.get('text') or fallback.get('text') or ''),
            'personality': _string_list(data.get('personality'), fallback.get('personality', []), 8),
            'life_state': _coerce_life_state(data.get('life_state'), fallback.get('life_state', {})),
            'early_events': _event_string_list(data.get('early_events'), fallback.get('early_events', []), 12),
            'hidden_strengths': _string_list(data.get('hidden_strengths'), fallback.get('hidden_strengths', []), 8),
            'hidden_weaknesses': _string_list(data.get('hidden_weaknesses'), fallback.get('hidden_weaknesses', []), 8),
            'source': 'ai',
        }

    async def enrich_half_year_narrative(self, session: dict[str, Any], latest: dict[str, Any]) -> dict[str, Any] | None:
        data = await self._request_json(
            'life_game_master.txt',
            {
                'mode': 'post_authoritative_roll',
                'instruction': 'D100 判定和 state_effect 已由后端完成。只生成年度叙事；state_update 仅作为建议记录，不会直接写入玩家状态。',
                'bazi_analysis': session.get('bazi_analysis', {}),
                'personality': session.get('personality', []),
                'latest_year': latest,
                'authoritative_roll_event': latest.get('roll_event', {}),
                'authoritative_state_effect': latest.get('state_effect', {}),
                'state_before': latest.get('state_before', {}),
                'state_after': latest.get('state_after', {}),
                'current_stage': session.get('current_stage', {}),
                'stage_event': latest.get('stage_event', {}),
                'goal_progress': session.get('goal_progress', {}),
                'life_systems': session.get('life_systems', {}),
                'relationships': session.get('relationships', []),
                'achievements': session.get('achievements', []),
                'latest_achievements': latest.get('new_achievements', []),
                'milestone': latest.get('milestone', {}),
                'recent_summaries': session.get('annual_summaries', [])[-5:],
                'major_events': session.get('major_events', [])[-8:],
            },
            '\n\n请按第二阶段输出 JSON，字段可包含 scene_title、narrative、state_update、memory_tags。',
        )
        if not data:
            return None
        narrative = str(data.get('narrative') or '').strip()
        if not narrative:
            return None
        return {
            'narrative': narrative,
            'scene_title': str(data.get('scene_title') or ''),
            'memory_tags': _string_list(data.get('memory_tags'), [], 8),
            'state_update_suggestion': data.get('state_update') if isinstance(data.get('state_update'), dict) else {},
            'source': 'ai',
        }

    async def enrich_half_year_summary(self, session: dict[str, Any], latest: dict[str, Any]) -> dict[str, Any] | None:
        data = await self._request_json(
            'annual_summary.txt',
            {
                'latest_year': latest,
                'life_state': session.get('life_state', {}),
                'current_stage': session.get('current_stage', {}),
                'goal_progress': session.get('goal_progress', {}),
                'life_systems': session.get('life_systems', {}),
                'relationships': session.get('relationships', []),
                'achievements': session.get('achievements', []),
                'latest_achievements': latest.get('new_achievements', []),
                'milestone': latest.get('milestone', {}),
                'current_luck_cycle': session.get('current_luck_cycle', {}),
                'current_annual_cycle': session.get('current_annual_cycle', {}),
                'recent_summaries': session.get('annual_summaries', [])[-5:],
                'major_events': session.get('major_events', [])[-10:],
            },
        )
        if not data:
            return None
        summary = str(data.get('summary') or latest.get('summary') or '').strip()
        if not summary:
            return None
        return {
            'summary': summary,
            'long_term_impact': str(data.get('long_term_impact') or ''),
            'memory_tags': _string_list(data.get('memory_tags'), [], 8),
            'source': 'ai',
        }


def adapter_for_session(session: dict[str, Any]) -> NoAiEnrichmentAdapter:
    user_id = str(session.get('player_id') or 'guest')
    if not openai_client.is_text_ai_enabled(user_id):
        return NoAiEnrichmentAdapter()
    return OpenAIEnrichmentAdapter(user_id)
