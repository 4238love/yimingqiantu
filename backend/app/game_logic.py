from __future__ import annotations

import asyncio
import ast
import logging
from copy import deepcopy
from typing import Any

from . import ai_enrichment, bazi_engine, ending_resolution, fate_mapper, game_command_router, half_year_resolution, life_context_projection, life_session, openai_client, state_manager, state_publication

logger = logging.getLogger(__name__)

ACTION_OPTIONS = half_year_resolution.ACTION_OPTIONS

ENDING_CODEX_CATALOG = life_session.ENDING_CODEX_CATALOG
INTRO_TEXT = life_session.INTRO_TEXT

ACTION_DETAIL = {
    '专注学业': '你把时间投入学习、训练和作品积累，短期可能牺牲娱乐与社交，但会为后续选择打开更多筹码。这个选择通常表现为固定作息、反复练习、主动请教和阶段复盘；真正的难点不是开始，而是在焦虑或外界诱惑出现时仍能守住节奏。',
    '发展事业': '你把注意力放在职位、项目和专业信誉上，机会来自承担更清晰的责任，压力也来自更高的外界期待。这个半年会更像一场能力与边界的拉扯：你需要证明自己能交付，也要避免把所有价值都押在一次评价上。',
    '经营感情': '你主动处理亲密关系中的表达、承诺和边界，关系的温度会影响情绪稳定，也会暴露长期回避的问题。行动的重点不只是制造浪漫，而是能不能把需求、误会、未来安排和安全感说清楚。',
    '陪伴家人': '你把精力转回家庭和亲人，稳定感会被重新修补，但也需要在责任与个人发展之间做细致分配。这个选择常常带来柔软的支持，也可能让旧有家庭模式、代际期待或照护压力重新浮出水面。',
    '投资理财': '你开始审视收入、资产和风险承受力，收益不只来自运气，更来自是否能守住节奏与纪律。真正的考验在于分清机会、诱惑与恐惧：该行动时不能犹豫，该止损时也不能被情绪拖住。',
    '调养身体': '你把睡眠、运动、治疗和压力管理放到前面，这会降低短期爆发力，却能修复未来几年的底盘。这个半年更看重连续的小改变：体检、休息、饮食、训练和情绪出口都会影响后续选择的承受力。',
    '社交拓展': '你尝试扩大圈层、合作和表达机会，人脉带来新资源，也会考验你识人和维持边界的能力。你需要在展示自己与保留锋芒之间拿捏分寸，避免为了融入而答应过多消耗性的关系。',
    '创业冒险': '你选择把不确定性变成主动权，事业与名望可能因此上升，但财富、健康和关系都会承受更高波动。这个半年会要求你同时面对资源、产品、客户、信任和现金流，任何一个环节都可能放大成关键转折。',
    '搬迁远行': '你通过城市、环境或生活半径的改变寻找新局面，迁移带来视野，也会暂时削弱熟悉的支持系统。它不只是地理位置变化，更是人际网络、生活成本、身份认同和未来机会的一次重新洗牌。',
    '随缘而行': '你没有强行推动某个目标，而是顺着事件流动调整自己，这可能积累福德，也可能错过需要主动争取的窗口。这个选择适合修复、观察和等待信号，但若长期如此，也容易把主动权交给外部环境。',
}

ACTION_SCENE_DETAIL = {
    '专注学业': '你可能把桌面重新整理，把手机放远，给自己排出课程、阅读、刷题或作品集清单；当同龄人的娱乐和比较声靠近时，你要不断确认这份投入究竟服务于哪一个更长远的目标。',
    '发展事业': '你可能接下一个更棘手的项目、争取一次汇报机会，或开始向上级和同事展示更稳定的专业判断；同时，工作之外的休息、关系和身体会提醒你，事业推进不是无限透支。',
    '经营感情': '你可能安排一次认真交谈，解释过去的沉默、试探或不安，也可能重新讨论边界、承诺和未来节奏；关系的变化会直接牵动情绪，让你看见自己真正害怕失去的东西。',
    '陪伴家人': '你可能回到饭桌、病床、家务或孩子的日常里，处理那些看似琐碎却长期积累的需求；家庭带来的归属感与束缚感会同时出现，逼你重新分配责任。',
    '投资理财': '你可能开始记账、复盘收入结构、研究投资计划或清理债务；每一次买入、卖出或延迟消费，都在训练你面对风险和欲望时的稳定度。',
    '调养身体': '你可能预约体检、调整作息、恢复运动，或者承认自己已经不能再靠硬撑解决问题；身体反馈会比计划更诚实，它会迫使你降低噪音，重新安排优先级。',
    '社交拓展': '你可能参加活动、主动联系旧识、加入新的合作圈，或第一次在陌生人面前表达自己的价值；新的关系会带来信息差，也会筛出谁只是热闹，谁真正能共同做事。',
    '创业冒险': '你可能写下商业模型、寻找第一批用户、谈合作或投入储蓄启动项目；激情会推你向前，但合同、现金流、信任和执行细节会不断要求你落地。',
    '搬迁远行': '你可能开始看房、换城市、办理手续，或为一次远行重新整理所有生活物件；离开熟悉环境后，新的机会会出现，孤独和成本也会变得更具体。',
    '随缘而行': '你可能没有给自己设定硬目标，而是更多观察、整理、休息和等待外界信号；这样的留白能恢复弹性，但也需要警惕把犹豫包装成顺其自然。',
}

AGE_STAGE_PROFILES = half_year_resolution.AGE_STAGE_PROFILES
LIFE_GOAL_TEMPLATES = half_year_resolution.LIFE_GOAL_TEMPLATES
ACHIEVEMENT_DEFINITIONS = half_year_resolution.ACHIEVEMENT_DEFINITIONS

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
    main_text = str(event.get('event') or event.get('text') or event.get('summary') or event.get('description') or '').strip()
    impact = str(event.get('impact') or event.get('effect') or event.get('influence') or '').strip()
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
    source = value if isinstance(value, list) else fallback or []
    result = [_event_text(item) for item in source]
    result = [item for item in result if item]
    return result[:limit] or list(fallback or [])

def _format_prelude_history(prelude: dict[str, Any]) -> str:
    early_events = _event_string_list(prelude.get('early_events'), [], 12)
    event_block = '\n- '.join(early_events)
    return '【人生前传】\n\n' + str(prelude.get('text') or '') + (('\n\n- ' + event_block) if event_block else '')

def _ensure_prelude_detail(prelude: dict[str, Any], fallback: dict[str, Any], start_age: int) -> dict[str, Any]:
    detailed = dict(prelude)
    text = str(detailed.get('text') or '').strip()
    fallback_text = str(fallback.get('text') or '').strip()
    if len(text) < 220 and fallback_text:
        detailed['text'] = (text + '\n\n补充底色：' + fallback_text).strip() if text else fallback_text
    else:
        detailed['text'] = text

    required_events = 6 if start_age >= 18 else 4
    events = _event_string_list(detailed.get('early_events'), [], 12)
    fallback_events = _event_string_list(fallback.get('early_events'), [], 12)
    for item in fallback_events:
        if len(events) >= required_events:
            break
        if item not in events:
            events.append(item)
    detailed['early_events'] = events[:12]

    strengths = _string_list(detailed.get('hidden_strengths'), [], 5)
    for item in _string_list(fallback.get('hidden_strengths'), [], 5):
        if len(strengths) >= 2:
            break
        if item not in strengths:
            strengths.append(item)
    weaknesses = _string_list(detailed.get('hidden_weaknesses'), [], 5)
    for item in _string_list(fallback.get('hidden_weaknesses'), [], 5):
        if len(weaknesses) >= 2:
            break
        if item not in weaknesses:
            weaknesses.append(item)
    detailed['hidden_strengths'] = strengths
    detailed['hidden_weaknesses'] = weaknesses
    return detailed

def _merge_string_lists(*values: Any, limit: int = 12) -> list[str]:
    result: list[str] = []
    for value in values:
        if not isinstance(value, list):
            continue
        for item in value:
            text = str(item).strip()
            if text and text not in result:
                result.append(text)
    return result[:limit]

def _coerce_life_state(value: Any, fallback: dict[str, int]) -> dict[str, int]:
    state = fallback.copy()
    if not isinstance(value, dict):
        return state
    for key in state:
        if key in value:
            try:
                state[key] = fate_mapper.clamp(int(value[key]))
            except (TypeError, ValueError):
                continue
    return state

def _replace_latest_history_entry(session: dict[str, Any], prefix: str, new_text: str) -> None:
    history = session.get('display_history') or []
    for index in range(len(history) - 1, -1, -1):
        if isinstance(history[index], str) and history[index].startswith(prefix):
            history[index] = new_text
            return
    history.append(new_text)

def _insert_history_before_latest_prefix(session: dict[str, Any], prefix: str, new_text: str) -> None:
    history = session.get('display_history') or []
    for index in range(len(history) - 1, -1, -1):
        if isinstance(history[index], str) and history[index].startswith(prefix):
            history.insert(index, new_text)
            return
    history.append(new_text)

def _player_id(current_user: dict[str, Any]) -> str:
    return str(current_user.get('username') or current_user.get('sub') or 'guest')

def _format_goal_progress(progress: dict[str, Any]) -> str:
    if not progress:
        return '人生愿望尚未确定。'
    return (
        '人生愿望“' + str(progress.get('title') or '') + '”当前为' +
        str(progress.get('score') or 0) + '/' + str(progress.get('threshold') or 0) +
        '，进度' + str(progress.get('percent') or 0) + '%，状态为' + str(progress.get('status') or '未知') + '。'
    )

def _choice_display(record: dict[str, Any], focuses: list[str]) -> str:
    raw_text = str(record.get('raw_choice_text') or '').strip()
    intent = record.get('choice_intent') or {}
    if raw_text and intent.get('is_custom'):
        return raw_text
    return '、'.join(focuses)

def _choice_classification_note(record: dict[str, Any], focuses: list[str]) -> str:
    display = _choice_display(record, focuses)
    normalized = '、'.join(_string_list(record.get('normalized_focuses'), focuses, 3))
    if display and normalized and display != normalized:
        return '系统将它归入“' + normalized + '”。'
    return ''

def _format_memory_feedback(record: dict[str, Any]) -> str:
    memory = record.get('life_memory') or {}
    echoes = record.get('memory_echoes') or []
    parts = []
    if memory.get('text'):
        parts.append('新伏笔：' + str(memory.get('text')))
    if echoes:
        parts.append('旧回声：' + '；'.join(str(item.get('text') or '') for item in echoes if item.get('text')))
    return '伏笔与回声：' + (' '.join(parts) if parts else '这次选择会进入人生记忆，等待后续阶段再次回响。')

async def get_or_create_session(current_user: dict[str, Any]) -> dict[str, Any]:
    player_id = _player_id(current_user)
    session = await state_manager.get_session(player_id)
    if session:
        life_session.ensure_defaults(session, ACTION_DETAIL)
        if session.get('is_processing'):
            session['is_processing'] = False
            await state_manager.save_session(player_id, session)
        return session
    session = life_session.new_session(player_id)
    await state_manager.save_session(player_id, session)
    return session

def _fallback_chart_analysis(session: dict[str, Any]) -> dict[str, Any]:
    chart = session.get('bazi_chart', {})
    counts = chart.get('five_elements') or {}
    balance = {
        '木': int(counts.get('wood', 0)),
        '火': int(counts.get('fire', 0)),
        '土': int(counts.get('earth', 0)),
        '金': int(counts.get('metal', 0)),
        '水': int(counts.get('water', 0)),
    }
    useful = _string_list(chart.get('useful_elements'), [], 5)
    unfavorable = _string_list(chart.get('unfavorable_elements'), [], 5)
    ten_god_focus = _merge_string_lists(list((chart.get('ten_gods') or {}).values()), limit=8)
    topic_by_element = {'木': '学习成长', '火': '表达名望', '土': '家庭责任', '金': '事业规则', '水': '心智流动'}
    direction_by_element = {'木': '深耕学习与长期技能', '火': '公开表达与作品展示', '土': '稳定家庭与资产基础', '金': '规则清晰的职业路径', '水': '研究、流动与跨界机会'}
    risk_by_element = {'木': '计划过满导致消耗', '火': '名望压力与情绪波动', '土': '家庭责任与固化负担', '金': '职场规则冲突', '水': '犹豫漂移与边界不清'}
    life_topics = [topic_by_element[element] for element in useful if element in topic_by_element]
    suitable_directions = [direction_by_element[element] for element in useful if element in direction_by_element]
    high_risk_fields = [risk_by_element[element] for element in unfavorable if element in risk_by_element]
    if chart.get('mode') == '三柱模式':
        life_topics.append('未知时辰带来的不确定性')
        high_risk_fields.append('子女线、晚年线与隐性性格需保守处理')
    luck_cycle_themes = []
    for cycle in session.get('luck_cycles', [])[:4]:
        theme = '、'.join(cycle.get('theme') or [])
        luck_cycle_themes.append(str(cycle.get('pillar', '')) + '：' + theme)
    chart_tags = _string_list(session.get('chart_tags'), bazi_engine.build_chart_tags(chart), 10)
    return {
        'five_element_balance': balance,
        'day_master_status': str(chart.get('day_strength') or '中和'),
        'useful_elements': useful,
        'unfavorable_elements': unfavorable,
        'ten_god_focus': ten_god_focus,
        'luck_cycle_themes': luck_cycle_themes,
        'life_topics': life_topics or ['在选择中修正命盘倾向'],
        'suitable_directions': suitable_directions or ['稳步积累，再择机突破'],
        'high_risk_fields': high_risk_fields or ['压力累积时的冲动决策'],
        'chart_tags': chart_tags,
        'source': 'deterministic',
    }

def _apply_chart_analysis(session: dict[str, Any], data: dict[str, Any], source: str) -> None:
    fallback = session.get('bazi_analysis') or _fallback_chart_analysis(session)
    balance = data.get('five_element_balance')
    if not isinstance(balance, dict):
        balance = fallback.get('five_element_balance', {})
    analysis = {
        'five_element_balance': balance,
        'day_master_status': str(data.get('day_master_status') or fallback.get('day_master_status') or '中和'),
        'useful_elements': _string_list(data.get('useful_elements'), fallback.get('useful_elements', []), 5),
        'unfavorable_elements': _string_list(data.get('unfavorable_elements'), fallback.get('unfavorable_elements', []), 5),
        'ten_god_focus': _string_list(data.get('ten_god_focus'), fallback.get('ten_god_focus', []), 8),
        'luck_cycle_themes': _string_list(data.get('luck_cycle_themes'), fallback.get('luck_cycle_themes', []), 8),
        'life_topics': _string_list(data.get('life_topics'), fallback.get('life_topics', []), 8),
        'suitable_directions': _string_list(data.get('suitable_directions'), fallback.get('suitable_directions', []), 8),
        'high_risk_fields': _string_list(data.get('high_risk_fields'), fallback.get('high_risk_fields', []), 8),
        'chart_tags': _merge_string_lists(fallback.get('chart_tags', []), data.get('chart_tags'), limit=10),
        'source': source,
    }
    session['bazi_analysis'] = analysis
    session['chart_tags'] = analysis['chart_tags']
    session['life_topics'] = analysis['life_topics']
    session['suitable_directions'] = analysis['suitable_directions']
    session['high_risk_fields'] = analysis['high_risk_fields']

def _handle_generate_chart(session: dict[str, Any], payload: dict[str, Any]) -> None:
    birth_info = dict(payload.get('birth_info') or {})
    start_age = int(birth_info.get('start_age') or payload.get('start_age') or 22)
    birth_info['start_age'] = max(6, min(60, start_age))
    chart_data = bazi_engine.generate_bazi_chart(birth_info)
    session['phase'] = 'chart_ready'
    session['birth_info'] = chart_data['birth_info']
    session['bazi_chart'] = chart_data['bazi_chart']
    session['luck_cycles'] = chart_data['luck_cycles']
    session['annual_cycles'] = chart_data['annual_cycles']
    session['monthly_cycles'] = chart_data.get('monthly_cycles', [])
    session['start_age'] = chart_data['start_age']
    session['current_year'] = chart_data['current_year']
    session['chart_tags'] = chart_data['tags']
    _apply_chart_analysis(session, _fallback_chart_analysis(session), 'deterministic')
    session['display_history'].append('【命盘已生成】四柱：' + session['bazi_chart']['year_pillar'] + ' ' + session['bazi_chart']['month_pillar'] + ' ' + session['bazi_chart']['day_pillar'] + ' ' + str(session['bazi_chart'].get('hour_pillar') or '未知时柱') + '。点击生成前传，进入正式人生之前的回望。')

async def _try_ai_chart_analysis(session: dict[str, Any]) -> None:
    adapter = ai_enrichment.adapter_for_session(session)
    data = await adapter.enrich_chart_analysis(session, session.get('bazi_analysis', {}))
    if not data:
        return
    _apply_chart_analysis(session, data, 'ai')
    topics = '、'.join(session.get('life_topics') or [])
    directions = '、'.join(session.get('suitable_directions') or [])
    session['display_history'].append('【命盘分析】人生课题：' + topics + '。适合方向：' + directions + '。')

async def _handle_generate_chart_async(session: dict[str, Any], payload: dict[str, Any]) -> None:
    _handle_generate_chart(session, payload)
    await _try_ai_chart_analysis(session)

def _handle_generate_prelude(session: dict[str, Any]) -> None:
    if not session.get('bazi_chart'):
        session['display_history'].append('【系统提示】请先生成命盘。')
        return
    chart_data = {'bazi_chart': session['bazi_chart'], 'tags': session.get('chart_tags', [])}
    prelude = fate_mapper.generate_prelude(chart_data, int(session.get('start_age') or 22))
    session['phase'] = 'prelude_ready'
    session['prelude'] = prelude
    session['life_state'] = prelude['life_state']
    session['personality'] = prelude['personality']
    session['major_events'] = _event_string_list(prelude.get('early_events'), [], 12)
    half_year_resolution.refresh_life_systems(session)
    half_year_resolution.ensure_life_goals(session)
    half_year_resolution.refresh_goal_progress(session)
    session['display_history'].append(_format_prelude_history(prelude))

async def _try_ai_prelude(session: dict[str, Any]) -> None:
    fallback = session['prelude']
    adapter = ai_enrichment.adapter_for_session(session)
    prelude = await adapter.enrich_prelude(session, fallback)
    if not prelude:
        return
    prelude = _ensure_prelude_detail(prelude, fallback, int(session.get('start_age') or 22))
    prelude['source'] = 'ai'
    session['prelude'] = prelude
    session['life_state'] = prelude['life_state']
    session['personality'] = prelude['personality']
    session['major_events'] = prelude['early_events'][:]
    half_year_resolution.refresh_life_systems(session)
    half_year_resolution.ensure_life_goals(session)
    half_year_resolution.refresh_goal_progress(session)
    _replace_latest_history_entry(
        session,
        '【人生前传】',
        _format_prelude_history(prelude),
    )

async def _handle_generate_prelude_async(session: dict[str, Any]) -> None:
    _handle_generate_prelude(session)
    await _try_ai_prelude(session)

def _handle_set_life_goal(session: dict[str, Any], goal_id: str) -> None:
    half_year_resolution.ensure_life_goals(session)
    selected = half_year_resolution.goal_template(goal_id)
    if not selected:
        session['display_history'].append('【系统提示】未识别的人生愿望。')
        return
    session['active_life_goal_id'] = selected['id']
    progress = half_year_resolution.refresh_goal_progress(session)
    session['display_history'].append('【人生愿望】你将这一生的主愿望定为“' + progress['title'] + '”。' + progress['summary'] + '系统会在半年度总结和最终结局中追踪它的达成情况。')

def _handle_accept_prelude(session: dict[str, Any]) -> None:
    if not session.get('prelude'):
        _handle_generate_prelude(session)
    if not session.get('prelude'):
        return
    session['phase'] = 'life_simulation'
    session['current_age'] = int(session.get('start_age') or 22)
    session['current_half'] = 1
    session['current_half_label'] = '上半年'
    session['focus_memory'] = half_year_resolution.empty_focus_memory()
    session['focus_streak'] = {}
    session['streak_warning'] = ''
    if not session.get('current_year'):
        session['current_year'] = int(session['birth_info']['datetime'][:4]) + session['current_age']
    half_year_resolution.ensure_life_goals(session)
    life_context_projection.refresh_current_context(session, ACTION_DETAIL)
    annual = session.get('current_annual_cycle') or {}
    stage = session.get('current_stage') or {}
    goals = '、'.join(_string_list(stage.get('goals'), [], 3))
    goal_progress = session.get('goal_progress') or {}
    session['display_history'].append(
        '【正式开局】你站在' + str(session['current_age']) + '岁这一年的门口。' +
        '当前阶段是“' + str(stage.get('label') or '人生转折') + '”，' + str(stage.get('summary') or '') +
        ('阶段目标：' + goals + '。' if goals else '') +
        '你为这一生暂定的人生愿望是“' + str(goal_progress.get('title') or '稳定富足') + '”：' + str(goal_progress.get('summary') or '') +
        '流年' + str(annual.get('pillar', '未知')) + '，主题是' + '、'.join(annual.get('events', [])) +
        '。人生将按上、下半年推进，请根据命盘底色、时运和现实处境，选择本半年的1到3个人生抉择。'
    )

def _handle_retrospect_life(session: dict[str, Any]) -> None:
    if session.get('phase') != 'life_simulation':
        session['display_history'].append('【系统提示】只有正式开始人生模拟后，才能主动回望一生。')
        return
    life_context_projection.refresh_current_context(session, ACTION_DETAIL)
    age = str(session.get('current_age') or '')
    half_label = str(session.get('current_half_label') or '')
    session['major_events'].append(age + '岁' + half_label + '，你主动选择回望一生。')
    ending_resolution.finish_session(session, 'retrospect')

def _format_state_transition(record: dict[str, Any]) -> str:
    before = record.get('state_before') or {}
    after = record.get('state_after') or {}
    changes = record.get('state_effect') or {}
    parts = []
    for key, value in changes.items():
        try:
            before_value = int(before.get(key, 0))
            after_value = int(after.get(key, before_value + int(value)))
        except (TypeError, ValueError):
            continue
        parts.append(str(key) + ' ' + str(before_value) + '→' + str(after_value))
    return '、'.join(parts) if parts else '主要状态保持稳定'

def _format_modifier_detail(modifiers: dict[str, Any]) -> str:
    parts = []
    for key, value in (modifiers or {}).items():
        try:
            number = int(value)
        except (TypeError, ValueError):
            continue
        sign = '+' if number > 0 else ''
        parts.append(str(key) + ' ' + sign + str(number))
    return '、'.join(parts) if parts else '无明显修正'

def _format_streak_feedback(record: dict[str, Any]) -> str:
    feedback = record.get('focus_streak') or {}
    action = str(feedback.get('action') or record.get('main_focus') or '随缘而行')
    try:
        count = int(feedback.get('count') or 1)
    except (TypeError, ValueError):
        count = 1
    try:
        bonus = int(record.get('streak_bonus') if record.get('streak_bonus') is not None else feedback.get('streak_bonus') or 0)
    except (TypeError, ValueError):
        bonus = 0
    warning = str(record.get('streak_warning') or feedback.get('streak_warning') or '')
    effect = record.get('streak_effect') or feedback.get('state_effect') or {}
    if count <= 1:
        return '连续选择反馈：本次开启“' + action + '”的新节奏；若后续继续投入，会逐步形成习惯优势，同时记录机会成本。'
    detail = '连续选择反馈：你已连续' + str(count) + '个半年把主重点放在“' + action + '”'
    if bonus:
        detail += '，本次获得连续投入带来的后台推演修正 +' + str(bonus)
    if effect:
        detail += '，状态惯性为' + half_year_resolution.format_state_effect(effect)
    if warning:
        detail += '。' + warning
    return detail + '。'

def _format_cycle_detail(record: dict[str, Any]) -> str:
    luck = record.get('luck_cycle') or {}
    annual = record.get('annual_cycle') or {}
    months = record.get('monthly_cycles') or []
    luck_text = str(luck.get('pillar') or '未知大运')
    if luck.get('theme'):
        luck_text += '（' + '、'.join(_string_list(luck.get('theme'), [], 3)) + '）'
    annual_text = str(annual.get('pillar') or '未知流年')
    if annual.get('events'):
        annual_text += '（' + '、'.join(_string_list(annual.get('events'), [], 3)) + '）'
    month_names = '、'.join(str(item.get('month_name', '')) + str(item.get('pillar', '')) for item in months if item.get('pillar'))
    opportunities = _merge_string_lists(*[item.get('opportunity') for item in months], limit=4)
    risks = _merge_string_lists(*[item.get('risk') for item in months], limit=4)
    month_text = month_names or '流月资料不足'
    if opportunities:
        month_text += '；机会：' + '、'.join(opportunities)
    if risks:
        month_text += '；风险：' + '、'.join(risks)
    return '大运' + luck_text + '，流年' + annual_text + '，本半年流月经过' + month_text + '。'

def _stage_narrative_body(record: dict[str, Any]) -> str:
    action = str(record.get('main_focus') or '随缘而行')
    focuses = _string_list(record.get('focuses'), [action], 3)
    choice_display = _choice_display(record, focuses)
    classification_note = _choice_classification_note(record, focuses)
    roll_event = record.get('roll_event') or {}
    outcome = str(roll_event.get('outcome') or '未知')
    action_detail = ACTION_DETAIL.get(action, ACTION_DETAIL['随缘而行'])
    scene_detail = ACTION_SCENE_DETAIL.get(action, ACTION_SCENE_DETAIL['随缘而行'])
    stage_event = record.get('stage_event') or {}
    stage_label = str(record.get('stage_label') or stage_event.get('stage_label') or '')
    goal_progress = record.get('goal_progress_after') or record.get('goal_progress_before') or {}
    cycle_detail = _format_cycle_detail(record)
    fate_explanation = record.get('fate_explanation') or {}
    life_scene = str(fate_explanation.get('life_scene') or '').strip()
    bazi_life_detail = str(fate_explanation.get('bazi_life_detail') or '').strip()
    month_life_detail = str(fate_explanation.get('month_life_detail') or '').strip()
    result_line = (
        '后台 D100 目标值为' + str(roll_event.get('target', '-')) +
        '，投掷结果为' + str(roll_event.get('result', '-')) +
        '，最终落在“' + outcome + '”。'
    )
    if outcome in ['大成功', '成功']:
        outcome_line = '这不是简单的顺利，而是你的既有积累、阶段运势和这次选择短暂站到了一起；它会让你在接下来的半年里更容易相信自己的判断。'
    else:
        outcome_line = '这次阻力让你看见短板：有些消耗不是立刻失败，而是会在之后几个半年里继续索取代价，提醒你调整节奏和求助方式。'
    event_title = str(stage_event.get('title') or '')
    event_clue = str(stage_event.get('clue') or '')
    event_line = ''
    if stage_event.get('event'):
        event_line = (
            '阶段事件：' +
            ('《' + event_title + '》：' if event_title else '') +
            str(stage_event.get('event')) +
            str(stage_event.get('result_note') or '') +
            (' 伏笔：' + event_clue if event_clue else '')
        )
    return (
        ('人生阶段：' + stage_label + '。' + str(stage_event.get('stage_summary') or '') + '\n\n' if stage_label else '') +
        (_format_goal_progress(goal_progress) + '\n\n' if goal_progress else '') +
        '人生抉择：你本阶段选择“' + choice_display + '”。' + classification_note + action_detail + '\n\n' +
        (('生活片段：' + life_scene + '\n\n') if life_scene else '') +
        (event_line + '\n\n' if event_line else '') +
        _format_streak_feedback(record) + '\n\n' +
        '具体场景：' + scene_detail + '\n\n' +
        '命盘影响：' + str(bazi_life_detail or fate_explanation.get('bazi_influence') or '命盘提供底色，但不替你做决定。') + '\n\n' +
        '时运影响：' + str(month_life_detail or fate_explanation.get('fortune_influence') or cycle_detail) + '\n\n' +
        '选择影响：' + str(fate_explanation.get('choice_influence') or ('你把本半年压在“' + action + '”上。')) + '\n\n' +
        _format_memory_feedback(record) + '\n\n' +
        '命盘与时势：' + cycle_detail + '\n\n' +
        '推演结果：' + result_line + outcome_line + '\n\n' +
        '状态余波：' + _format_state_transition(record) + '。这些变化不会只停留在数值上，它们会表现为精力分配、关系反馈、资源余量和下一次选择时的心理惯性。'
    )

def _format_stage_narrative(record: dict[str, Any]) -> str:
    action = str(record.get('main_focus') or '随缘而行')
    title = str(record.get('age') or '') + '岁' + str(record.get('half_label') or '') + ' · ' + action
    return '【阶段叙事】' + title + '\n\n' + _stage_narrative_body(record)

def _format_detailed_half_year_summary(record: dict[str, Any]) -> str:
    action = str(record.get('main_focus') or '随缘而行')
    focuses = _string_list(record.get('focuses'), [action], 3)
    choice_display = _choice_display(record, focuses)
    classification_note = _choice_classification_note(record, focuses)
    roll_event = record.get('roll_event') or {}
    age_half = str(record.get('age') or '') + '岁' + str(record.get('half_label') or '')
    stage_event = record.get('stage_event') or {}
    systems_after = record.get('life_systems_after') or {}
    goal_progress = record.get('goal_progress_after') or {}
    new_achievements = record.get('new_achievements') or []
    fate_explanation = record.get('fate_explanation') or {}
    life_scene = str(fate_explanation.get('life_scene') or '').strip()
    scene_detail = ACTION_SCENE_DETAIL.get(action, ACTION_SCENE_DETAIL['随缘而行'])
    event_title = str(stage_event.get('title') or '')
    event_intro = ('《' + event_title + '》：' if event_title else '')
    streak_detail = _format_streak_feedback(record)
    stage_intro = ''
    if stage_event.get('stage_label'):
        stage_intro = '这一段人生还处在“' + str(stage_event.get('stage_label')) + '”：' + '、'.join(_string_list(stage_event.get('stage_goals'), [], 3)) + '会反复回到日常里。'
    event_line = ''
    if stage_event.get('event'):
        clue_text = str(stage_event.get('clue') or '').rstrip('。；;,.， ')
        event_line = '后来能被记住的触发点，是' + event_intro + str(stage_event.get('event')) + str(stage_event.get('result_note') or '') + ('伏笔：' + clue_text + '。' if clue_text else '')
    summary = (
        '半年回顾：' + age_half + '，你选择“' + choice_display + '”。' +
        (classification_note if classification_note else '这个选择会进入后续人生记忆。') +
        (('\n\n生活叙事：' + life_scene) if life_scene else ('\n\n生活叙事：' + scene_detail)) +
        (('\n\n' + stage_intro) if stage_intro else '') +
        (('\n\n' + event_line) if event_line else '') +
        (('\n\n' + _format_goal_progress(goal_progress)) if goal_progress else '') +
        '\n\n命盘与时势背景：' + _format_cycle_detail(record)
    )
    fate_detail = (
        '事后解读：\n\n命盘影响：' + str(fate_explanation.get('bazi_life_detail') or fate_explanation.get('bazi_influence') or '命盘提供人生底色，影响你更容易在哪些领域形成优势、惯性和反复课题。') +
        '\n\n时运影响：' + str(fate_explanation.get('month_life_detail') or fate_explanation.get('fortune_influence') or _format_cycle_detail(record)) +
        '\n\n选择影响：' + str(fate_explanation.get('choice_influence') or ('你选择' + '、'.join(focuses) + '，这会进入后续人生记忆。')) +
        '\n\n人生变化：' + str(fate_explanation.get('life_change') or ('状态走向：' + _format_state_transition(record) + '。'))
    )
    roll_detail = (
        '后台判定细节：' + str(roll_event.get('type') or 'D100') +
        '目标值' + str(roll_event.get('target', '-')) +
        '，投掷' + str(roll_event.get('result', '-')) +
        '，结果为' + str(roll_event.get('outcome') or '未知') +
        '；修正来源包括' + _format_modifier_detail(record.get('roll_modifiers') or {}) + '。'
    )
    state_detail = (
        '状态走向：' + _format_state_transition(record) + '。' +
        '如果某项属性上升，代表这个方向已经形成可复用的经验、资源或信心；如果压力、健康或关系出现消耗，则会在后续半年转化成更高的机会成本。'
    )
    impact = (
        '阶段影响：' + ACTION_DETAIL.get(action, ACTION_DETAIL['随缘而行']) +
        '这条选择会进入后续记忆，影响下一次面对同类机会时的底气、风险承受力和关系反馈。' +
        _format_memory_feedback(record) +
        (_format_goal_progress(goal_progress) if goal_progress else '') +
        ('本阶段解锁成就：' + '、'.join(str(item.get('title')) for item in new_achievements if item.get('title')) + '。' if new_achievements else '') +
        ('长期系统：' + '；'.join(str(item.get('label')) + str(item.get('score')) + '分，' + str(item.get('stage')) + '，趋势' + str(item.get('trend')) for item in systems_after.values()) + '。' if isinstance(systems_after, dict) and systems_after else '') +
        '后续伏笔：系统会把本次行动、判定结果和状态变化纳入长期历史；当相似的大运、流年或流月再次出现时，它们会成为新的加分、阻力或叙事回声。'
    )
    return summary + '\n\n' + fate_detail + '\n\n' + roll_detail + '\n\n' + streak_detail + '\n\n' + state_detail + '\n\n' + impact

def _ensure_summary_detail(record: dict[str, Any], summary: str) -> str:
    text = str(summary or '').strip()
    if len(text) >= 180 and ('判定' in text or 'D100' in text) and '状态' in text and ('大运' in text or '流月' in text):
        return text
    fallback = _format_detailed_half_year_summary(record)
    if not text:
        return fallback
    return text + '\n\n补充观察：' + fallback

def _ensure_narrative_detail(record: dict[str, Any], narrative: str) -> str:
    text = str(narrative or '').strip()
    if len(text) >= 180 and ('判定' in text or 'D100' in text) and ('状态' in text or '资源' in text or '关系' in text):
        return text
    fallback = _stage_narrative_body(record)
    if not text:
        return fallback
    return text + '\n\n补充场景：' + fallback

def _handle_annual_action(session: dict[str, Any], action_payload: dict[str, Any] | str) -> None:
    if session.get('phase') != 'life_simulation':
        session['display_history'].append('【系统提示】请先接受人生前传并开始模拟。')
        return
    life_context_projection.refresh_current_context(session, ACTION_DETAIL)
    half_record = half_year_resolution.resolve_authoritative_record(session, action_payload)
    roll_event = half_record['roll_event']
    changes = half_record['state_effect']
    half_year_resolution.complete_authoritative_record(session, half_record)
    new_achievements = half_record.get('new_achievements') or []
    half_record['summary'] = _format_detailed_half_year_summary(half_record)
    session['half_year_summaries'].append(half_record)
    session['annual_summaries'].append(half_record.copy())
    session['major_events'].append(half_record['summary'])
    session['display_history'].append(roll_event['result_text'])
    session['display_history'].append(_format_stage_narrative(half_record))
    if new_achievements:
        session['display_history'].append('【新成就】' + '、'.join(item['title'] for item in new_achievements) + '\n\n' + '\n'.join(item['description'] for item in new_achievements))
    session['display_history'].append('【半年度总结】\n\n' + half_record['summary'] + '\n\n状态变化：' + half_year_resolution.format_state_effect(changes))
    if ending_resolution.finish_if_needed(session):
        life_context_projection.refresh_current_context(session, ACTION_DETAIL)
        return
    half_year_resolution.advance_turn_cursor(session, half_record)
    life_context_projection.refresh_current_context(session, ACTION_DETAIL)
    ending_resolution.finish_if_needed(session)

async def _try_ai_life_gm_latest_narrative(session: dict[str, Any]) -> None:
    if not session.get('annual_summaries'):
        return
    latest = session['annual_summaries'][-1]
    adapter = ai_enrichment.adapter_for_session(session)
    data = await adapter.enrich_half_year_narrative(session, latest)
    if not data:
        return
    narrative = str(data.get('narrative') or '').strip()
    if not narrative:
        return
    narrative = _ensure_narrative_detail(latest, narrative)
    latest['gm_narrative'] = narrative
    latest['gm_scene_title'] = str(data.get('scene_title') or '')
    latest['gm_memory_tags'] = _string_list(data.get('memory_tags'), [], 8)
    latest['gm_state_update_suggestion'] = data.get('state_update_suggestion') if isinstance(data.get('state_update_suggestion'), dict) else {}
    latest['gm_source'] = 'ai'
    title = latest['gm_scene_title'] or str(latest.get('age', '')) + '岁' + str(latest.get('half_label', '')) + '叙事'
    display_text = '【阶段叙事】' + title + '\n\n' + narrative
    if latest['gm_memory_tags']:
        display_text += '\n\n记忆标签：' + '、'.join(latest['gm_memory_tags'])
    _replace_latest_history_entry(session, '【阶段叙事】', display_text)

async def _try_ai_latest_annual_summary(session: dict[str, Any]) -> None:
    if not session.get('annual_summaries'):
        return
    latest = session['annual_summaries'][-1]
    adapter = ai_enrichment.adapter_for_session(session)
    data = await adapter.enrich_half_year_summary(session, latest)
    if not data:
        return
    original_summary = str(latest.get('summary') or '').strip()
    summary = str(data.get('summary') or original_summary or '').strip()
    summary = _ensure_summary_detail(latest, summary)
    if not summary:
        return
    latest['summary'] = summary
    latest['long_term_impact'] = str(data.get('long_term_impact') or '')
    latest['memory_tags'] = _string_list(data.get('memory_tags'), [], 8)
    latest['source'] = 'ai'
    focus_line = ''
    focuses = _string_list(latest.get('focuses'), [], 3)
    if focuses:
        choice_display = _choice_display(latest, focuses)
        classification_note = _choice_classification_note(latest, focuses)
        focus_line = (
            str(latest.get('age') or '') + '岁' +
            str(latest.get('half_label') or '') +
            '，你选择“' + choice_display + '”。' + classification_note
        )
    display_parts = []
    if focus_line and focus_line not in summary:
        display_parts.append(focus_line)
    display_parts.append(summary)
    display_text = '【半年度总结】\n\n' + '\n\n'.join(display_parts) + '\n\n状态变化：' + half_year_resolution.format_state_effect(latest.get('state_effect', {}))
    if latest.get('long_term_impact'):
        display_text += '\n\n长期影响：' + latest['long_term_impact']
    _replace_latest_history_entry(session, '【半年度总结】', display_text)

async def _handle_annual_action_async(session: dict[str, Any], action_payload: dict[str, Any] | str) -> None:
    before_count = len(session.get('annual_summaries', []))
    _handle_annual_action(session, action_payload)
    if len(session.get('annual_summaries', [])) > before_count:
        await _try_ai_life_gm_latest_narrative(session)
        await _try_ai_latest_annual_summary(session)

def _reset_session_in_place(session: dict[str, Any]) -> dict[str, Any]:
    player_id = str(session.get('player_id') or 'guest')
    ending_codex = life_session.normalize_ending_codex(session.get('ending_codex'))
    replacement = life_session.new_session(player_id)
    replacement['ending_codex'] = ending_codex
    session.clear()
    session.update(replacement)
    return session

def _handle_generate_prelude_command(session: dict[str, Any], payload: dict[str, Any]) -> None:
    _handle_generate_prelude(session)

async def _handle_generate_prelude_command_async(session: dict[str, Any], payload: dict[str, Any]) -> None:
    await _handle_generate_prelude_async(session)

def _handle_set_life_goal_command(session: dict[str, Any], payload: dict[str, Any]) -> None:
    _handle_set_life_goal(session, str(payload.get('goal_id') or payload.get('id') or ''))

def _handle_accept_prelude_command(session: dict[str, Any], payload: dict[str, Any]) -> None:
    if not session.get('prelude'):
        _handle_generate_prelude(session)
    _handle_accept_prelude(session)

async def _handle_accept_prelude_command_async(session: dict[str, Any], payload: dict[str, Any]) -> None:
    if not session.get('prelude'):
        await _handle_generate_prelude_async(session)
    _handle_accept_prelude(session)

def _handle_retrospect_life_command(session: dict[str, Any], payload: dict[str, Any]) -> None:
    _handle_retrospect_life(session)

def _handle_reset_game_command(session: dict[str, Any], payload: dict[str, Any]) -> None:
    _reset_session_in_place(session)

def _handle_unknown_command(session: dict[str, Any], payload: dict[str, Any]) -> None:
    action_type = game_command_router.action_type(payload)
    session['display_history'].append('【系统提示】未识别的行动：' + action_type)

def _annual_action_handler(action_name: str | None = None):
    def handler(session: dict[str, Any], payload: dict[str, Any]) -> None:
        _handle_annual_action(session, action_name or payload)
    return handler

def _annual_action_handler_async(action_name: str | None = None):
    async def handler(session: dict[str, Any], payload: dict[str, Any]) -> None:
        await _handle_annual_action_async(session, action_name or payload)
    return handler

def _build_command_router() -> game_command_router.GameCommandRouter:
    router = game_command_router.GameCommandRouter()
    router.register('generate_chart', _handle_generate_chart, _handle_generate_chart_async)
    router.register('generate_prelude', _handle_generate_prelude_command, _handle_generate_prelude_command_async)
    router.register('set_life_goal', _handle_set_life_goal_command)
    for command in ['accept_prelude', 'start_life']:
        router.register(command, _handle_accept_prelude_command, _handle_accept_prelude_command_async)
    for command in ['annual_action', 'year_action']:
        router.register(command, _annual_action_handler(), _annual_action_handler_async())
    for command in ['retrospect_life', 'look_back_life', 'finish_life']:
        router.register(command, _handle_retrospect_life_command)
    router.register('reset_game', _handle_reset_game_command)
    for action_name in ACTION_OPTIONS:
        router.register(action_name, _annual_action_handler(action_name), _annual_action_handler_async(action_name))
    router.set_default(_handle_unknown_command)
    return router

COMMAND_ROUTER = _build_command_router()

def apply_player_action(session: dict[str, Any], action: Any) -> dict[str, Any]:
    """Apply one deterministic player action to an in-memory life session.

    This is the public test surface for the人生模拟编排 Module. Network
    entrypoints use the async variant so AI enrichment can decorate the same
    flow, but tests should not couple to private `_handle_*` implementation
    branches.
    """
    life_session.ensure_defaults(session, ACTION_DETAIL)
    return COMMAND_ROUTER.dispatch(session, action)

async def apply_player_action_async(session: dict[str, Any], action: Any) -> dict[str, Any]:
    """Apply one player action to an in-memory life session, including AI enrichment."""
    life_session.ensure_defaults(session, ACTION_DETAIL)
    return await COMMAND_ROUTER.dispatch_async(session, action)

async def _process_player_action_async(current_user: dict[str, Any], action: Any) -> None:
    player_id = _player_id(current_user)
    session = await state_manager.get_session(player_id)
    if not session:
        return
    life_session.ensure_defaults(session, ACTION_DETAIL)
    try:
        await apply_player_action_async(session, action)
    except Exception as exc:
        logger.error('Error processing action for %s: %s', player_id, exc, exc_info=True)
        session['display_history'].append('【命书紊乱】本次行动处理失败，请检查输入后重试。')
    finally:
        session['is_processing'] = False
        await state_publication.commit_session(player_id, session)

async def process_player_action(current_user: dict[str, Any], action: Any) -> None:
    player_id = _player_id(current_user)
    session = await state_manager.get_session(player_id)
    if not session:
        session = life_session.new_session(player_id)
    life_session.ensure_defaults(session, ACTION_DETAIL)
    if session.get('is_processing'):
        return
    if session.get('is_finished') and not (isinstance(action, dict) and action.get('type') == 'reset_game'):
        return
    session['is_processing'] = True
    await state_publication.commit_session(player_id, session)
    asyncio.create_task(_process_player_action_async(current_user, action))
