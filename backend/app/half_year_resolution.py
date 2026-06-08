from __future__ import annotations

import random
import time
from copy import deepcopy
from typing import Any

from . import event_pool, fate_mapper


ACTION_OPTIONS = list(fate_mapper.ACTION_PROFILES.keys())

AGE_STAGE_PROFILES = [
    {
        'id': 'childhood',
        'label': '童年启蒙',
        'age_min': 6,
        'age_max': 12,
        'summary': '家庭安全感、学习习惯、身体底盘和同伴关系正在成形。',
        'goals': ['建立安全感', '养成学习节奏', '保护身体底盘'],
        'action_options': ['专注学业', '陪伴家人', '调养身体', '社交拓展', '搬迁远行', '随缘而行'],
    },
    {
        'id': 'adolescence',
        'label': '少年转折',
        'age_min': 13,
        'age_max': 18,
        'summary': '考试、兴趣、亲子边界、友情和自我认同开始互相拉扯。',
        'goals': ['完成关键升学', '建立自我认同', '处理亲子与同伴压力'],
        'action_options': ['专注学业', '经营感情', '陪伴家人', '调养身体', '社交拓展', '搬迁远行', '随缘而行'],
    },
    {
        'id': 'early_adult',
        'label': '成年起步',
        'age_min': 19,
        'age_max': 25,
        'summary': '专业、城市、职业入口、亲密关系和独立生活一起打开。',
        'goals': ['确定发展方向', '积累第一批资源', '建立成熟关系边界'],
        'action_options': ['专注学业', '发展事业', '经营感情', '陪伴家人', '投资理财', '调养身体', '社交拓展', '搬迁远行', '随缘而行'],
    },
    {
        'id': 'building',
        'label': '立业成家',
        'age_min': 26,
        'age_max': 35,
        'summary': '职业上升、婚恋选择、资产起步和家庭责任进入密集交汇期。',
        'goals': ['稳住职业路线', '经营亲密与家庭', '建立资产安全垫'],
        'action_options': ACTION_OPTIONS,
    },
    {
        'id': 'midlife',
        'label': '中年经营',
        'age_min': 36,
        'age_max': 50,
        'summary': '转型、子女、健康、财富压力和社会角色让人生进入结构性取舍。',
        'goals': ['升级事业结构', '守住健康与资产', '平衡家庭责任'],
        'action_options': ACTION_OPTIONS,
    },
    {
        'id': 'late_life',
        'label': '后半生收束',
        'age_min': 51,
        'age_max': 60,
        'summary': '健康、资产安全、家庭关系、精神追求和传承感成为主线。',
        'goals': ['降低长期风险', '修复重要关系', '完成精神与经验传承'],
        'action_options': ['专注学业', '发展事业', '经营感情', '陪伴家人', '投资理财', '调养身体', '社交拓展', '搬迁远行', '随缘而行'],
    },
]


def age_stage(age: int | None) -> dict[str, Any]:
    value = int(age or 22)
    for stage in AGE_STAGE_PROFILES:
        if int(stage['age_min']) <= value <= int(stage['age_max']):
            return dict(stage)
    return dict(AGE_STAGE_PROFILES[-1])


def stage_action_options(age: int | None) -> list[str]:
    return list(age_stage(age).get('action_options') or ACTION_OPTIONS)


def stage_safe_action(age: int | None, action: str) -> str:
    allowed = stage_action_options(age)
    if action in allowed:
        return action
    safe_age = int(age or 22)
    if safe_age <= 18 and action in ['发展事业', '投资理财', '创业冒险']:
        return '专注学业'
    if safe_age <= 12 and action == '经营感情':
        return '社交拓展'
    return '随缘而行'


def pick_stage_event(player_id: str, age: int, half: int, action: str, outcome: str) -> dict[str, Any]:
    stage = age_stage(age)
    return event_pool.pick_stage_event(player_id, age, half, action, outcome, stage)


def empty_focus_memory() -> dict[str, Any]:
    return {'last_focus': '', 'streak': 0, 'total_counts': {}, 'recent_focuses': []}


def normalize_focus_memory(value: Any) -> dict[str, Any]:
    memory = value if isinstance(value, dict) else {}
    total_counts: dict[str, int] = {}
    for key, count in (memory.get('total_counts') or {}).items():
        if str(key) in ACTION_OPTIONS:
            try:
                total_counts[str(key)] = max(0, int(count))
            except (TypeError, ValueError):
                continue
    recent_focuses = []
    for item in memory.get('recent_focuses') or []:
        if not isinstance(item, dict):
            continue
        focus = str(item.get('focus') or '')
        if focus not in ACTION_OPTIONS:
            continue
        recent_focuses.append({
            'age': item.get('age'),
            'half': item.get('half'),
            'half_label': str(item.get('half_label') or ''),
            'focus': focus,
            'outcome': str(item.get('outcome') or ''),
            'streak': int(item.get('streak') or 1),
        })
    last_focus = str(memory.get('last_focus') or '')
    if last_focus not in ACTION_OPTIONS:
        last_focus = ''
    try:
        streak = max(0, int(memory.get('streak') or 0)) if last_focus else 0
    except (TypeError, ValueError):
        streak = 0
    return {
        'last_focus': last_focus,
        'streak': streak,
        'total_counts': total_counts,
        'recent_focuses': recent_focuses[-8:],
    }


def focus_streak_roll_bonus(count: int) -> int:
    if count >= 4:
        return 8
    if count == 3:
        return 5
    if count == 2:
        return 3
    return 0


def focus_streak_state_effect(action: str, count: int) -> dict[str, int]:
    if count < 2:
        return {}
    profile = fate_mapper.ACTION_PROFILES.get(action, fate_mapper.ACTION_PROFILES['随缘而行'])
    effects: dict[str, int] = {}
    primary = str(profile.get('primary') or '')
    if primary:
        effects[primary] = effects.get(primary, 0) + 1
    if count >= 3:
        if action in ['调养身体', '随缘而行']:
            effects['压力'] = effects.get('压力', 0) - 1
        elif action in ['经营感情', '陪伴家人']:
            effects['情绪'] = effects.get('情绪', 0) + 1
        else:
            effects['压力'] = effects.get('压力', 0) + 1
    if count >= 4:
        opportunity_cost = {
            '专注学业': '社交',
            '发展事业': '健康',
            '经营感情': '事业',
            '陪伴家人': '事业',
            '投资理财': '情绪',
            '调养身体': '财富',
            '社交拓展': '情绪',
            '创业冒险': '健康',
            '搬迁远行': '家庭',
            '随缘而行': '事业',
        }.get(action)
        if opportunity_cost:
            effects[opportunity_cost] = effects.get(opportunity_cost, 0) - 1
        if action in ['专注学业', '发展事业', '投资理财', '创业冒险']:
            effects['压力'] = effects.get('压力', 0) + 1
    return {key: value for key, value in effects.items() if key in fate_mapper.BASE_LIFE_STATE and value != 0}


def format_state_effect(changes: dict[str, Any]) -> str:
    parts = []
    for key, value in (changes or {}).items():
        try:
            number = int(value)
        except (TypeError, ValueError):
            parts.append(str(key) + ' ' + str(value))
            continue
        sign = '+' if number > 0 else ''
        parts.append(str(key) + ' ' + sign + str(number))
    return '、'.join(parts) if parts else '无明显变化'


def build_focus_streak_feedback(session: dict[str, Any], action: str) -> dict[str, Any]:
    memory = normalize_focus_memory(session.get('focus_memory'))
    previous_focus = str(memory.get('last_focus') or '')
    previous_streak = int(memory.get('streak') or 0)
    count = previous_streak + 1 if previous_focus == action else 1
    bonus = focus_streak_roll_bonus(count)
    state_effect = focus_streak_state_effect(action, count)
    if count <= 1:
        warning = '这是“' + action + '”的新一轮投入；如果后续继续选择同一重点，会逐步形成判定加成，也会积累机会成本。'
    elif count == 2:
        warning = '连续2个半年投入“' + action + '”，惯性开始成形：本次 D100 获得小幅加成。'
    elif count == 3:
        warning = '连续3个半年投入“' + action + '”，路线更清晰，判定加成提高，但生活其他面向开始要求补偿。'
    else:
        warning = '连续' + str(count) + '个半年投入“' + action + '”，专精已经明显；请留意压力、关系、健康或资产中的机会成本。'
    return {
        'action': action,
        'previous_focus': previous_focus,
        'count': count,
        'is_continuing': previous_focus == action and count > 1,
        'streak_bonus': bonus,
        'streak_warning': warning,
        'state_effect': state_effect,
        'state_effect_text': format_state_effect(state_effect) if state_effect else '无额外状态惯性',
        'summary': '连续选择反馈：' + warning + (' 额外状态影响：' + format_state_effect(state_effect) + '。' if state_effect else ''),
    }


def commit_focus_streak(session: dict[str, Any], feedback: dict[str, Any], age: int, half: int, half_label: str, outcome: str) -> dict[str, Any]:
    memory = normalize_focus_memory(session.get('focus_memory'))
    action = str(feedback.get('action') or '随缘而行')
    total_counts = dict(memory.get('total_counts') or {})
    total_counts[action] = int(total_counts.get(action, 0)) + 1
    recent_focuses = list(memory.get('recent_focuses') or [])
    count = int(feedback.get('count') or 1)
    recent_focuses.append({
        'age': age,
        'half': half,
        'half_label': half_label,
        'focus': action,
        'outcome': outcome,
        'streak': count,
    })
    session['focus_memory'] = {
        'last_focus': action,
        'streak': count,
        'total_counts': total_counts,
        'recent_focuses': recent_focuses[-8:],
    }
    session['focus_streak'] = deepcopy(feedback)
    session['streak_warning'] = str(feedback.get('streak_warning') or '')
    return session['focus_memory']


def merge_state_effect(changes: dict[str, int], extra: dict[str, Any]) -> dict[str, int]:
    for key, value in (extra or {}).items():
        if key not in fate_mapper.BASE_LIFE_STATE:
            continue
        try:
            delta = int(value)
        except (TypeError, ValueError):
            continue
        if delta:
            changes[key] = int(changes.get(key, 0)) + delta
    return changes


def stage_event_state_bias(stage_event: dict[str, Any], outcome: str) -> dict[str, int]:
    raw = stage_event.get('state_bias') or {}
    if not isinstance(raw, dict):
        return {}
    bias: dict[str, int] = {}
    for key, value in raw.items():
        if key not in fate_mapper.BASE_LIFE_STATE:
            continue
        try:
            delta = int(value)
        except (TypeError, ValueError):
            continue
        if outcome in ['大成功', '成功']:
            applied = delta
        elif key == '压力' and delta > 0:
            applied = delta
        elif delta < 0:
            applied = delta
        else:
            applied = 0
        if applied:
            bias[str(key)] = applied
    return bias


def roll(player_id: str, roll_type: str, target: int, description: str) -> dict[str, Any]:
    sides = 100
    result = random.randint(1, sides)
    if result <= 5:
        outcome = '大成功'
    elif result <= target:
        outcome = '成功'
    elif result >= 96:
        outcome = '大失败'
    else:
        outcome = '失败'
    return {
        'id': player_id + '_' + str(int(time.time() * 1000)),
        'type': roll_type,
        'target': target,
        'sides': sides,
        'result': result,
        'outcome': outcome,
        'description': description,
        'result_text': '【系统提示：' + roll_type + ' D100 判定；目标值 ' + str(target) + '，投掷 ' + str(result) + '，结果 ' + outcome + '】',
    }


def normalize_focuses(action_payload: dict[str, Any] | str) -> list[str]:
    if isinstance(action_payload, str):
        return [fate_mapper.infer_action_from_text(action_payload)]
    focuses = action_payload.get('focuses') or action_payload.get('actions') or []
    if isinstance(focuses, str):
        focuses = [focuses]
    cleaned = []
    for item in focuses:
        action = fate_mapper.infer_action_from_text(str(item))
        if action not in cleaned:
            cleaned.append(action)
    return cleaned[:3] or ['随缘而行']


def resolve_core(session: dict[str, Any], action_payload: dict[str, Any] | str) -> dict[str, Any]:
    """Resolve the authoritative deterministic half-year choice.

    Interface invariants:
    - caller has already refreshed current luck/year/month/stage context;
    - session is in life_simulation;
    - this function mutates only authoritative state for the half-year choice:
      life_state, roll_event, focus_memory/focus_streak/streak_warning.
    """
    focuses = normalize_focuses(action_payload)
    state_before = dict(session.get('life_state', {}))
    life_systems_before = deepcopy(session.get('life_systems') or {})
    relationships_before = deepcopy(session.get('relationships') or [])
    goal_progress_before = deepcopy(session.get('goal_progress') or {})
    luck = dict(session.get('current_luck_cycle') or {})
    annual = dict(session.get('current_annual_cycle') or {})
    monthly_cycles = [dict(item) for item in session.get('current_monthly_cycles') or []]
    age = int(session.get('current_age') or session.get('start_age') or 22)
    year = session.get('current_year')
    half = int(session.get('current_half') or 1)
    half_label = fate_mapper.half_label(half)

    normalized = []
    for focus in focuses:
        safe_focus = stage_safe_action(age, focus)
        if safe_focus not in normalized:
            normalized.append(safe_focus)
    focuses = normalized[:3] or ['随缘而行']
    main_focus = focuses[0]

    focus_feedback = build_focus_streak_feedback(session, main_focus)
    target, modifiers = fate_mapper.compute_roll_target(session, main_focus)
    if int(focus_feedback.get('streak_bonus') or 0):
        modifiers['连续投入'] = int(focus_feedback.get('streak_bonus') or 0)
        target = fate_mapper.clamp(target + int(focus_feedback.get('streak_bonus') or 0), 20, 95)
    roll_event = roll(session['player_id'], fate_mapper.ACTION_PROFILES[main_focus]['roll'], target, str(age) + '岁' + half_label + '行动')
    roll_event['modifiers'] = modifiers

    stage_event = pick_stage_event(str(session.get('player_id') or 'guest'), age, half, main_focus, roll_event['outcome'])
    changes = fate_mapper.scale_changes(fate_mapper.apply_annual_result(session, main_focus, roll_event['outcome']))
    for extra_focus in focuses[1:]:
        profile = fate_mapper.ACTION_PROFILES[extra_focus]
        changes[profile['primary']] = changes.get(profile['primary'], 0) + 1
        changes['压力'] = changes.get('压力', 0) + 1

    event_state_bias = stage_event_state_bias(stage_event, roll_event['outcome'])
    merge_state_effect(changes, event_state_bias)
    merge_state_effect(changes, focus_feedback.get('state_effect') or {})
    session['life_state'] = fate_mapper.apply_changes(session.get('life_state', {}), changes)
    session['roll_event'] = roll_event
    focus_memory_after = commit_focus_streak(session, focus_feedback, age, half, half_label, roll_event['outcome'])

    month_pillars = '、'.join(str(item.get('month_name', '')) + str(item.get('pillar', '')) for item in monthly_cycles)
    summary = str(age) + '岁' + half_label + '，你选择' + '、'.join(focuses) + '。流年' + str(annual.get('pillar', '未知')) + '之下，流月经过' + month_pillars + '，判定结果为' + roll_event['outcome'] + '。'
    return {
        'age': age,
        'year': year,
        'half': half,
        'half_label': half_label,
        'summary': summary,
        'state_effect': changes,
        'focuses': focuses,
        'main_focus': main_focus,
        'roll_event': roll_event,
        'roll_modifiers': modifiers,
        'focus_streak': deepcopy(focus_feedback),
        'streak_bonus': int(focus_feedback.get('streak_bonus') or 0),
        'streak_warning': str(focus_feedback.get('streak_warning') or ''),
        'streak_effect': deepcopy(focus_feedback.get('state_effect') or {}),
        'focus_memory_after': deepcopy(focus_memory_after),
        'event_state_bias': event_state_bias,
        'state_before': state_before,
        'state_after': dict(session.get('life_state', {}),
        ),
        'life_systems_before': life_systems_before,
        'relationships_before': relationships_before,
        'goal_progress_before': goal_progress_before,
        'luck_cycle': luck,
        'annual_cycle': annual,
        'monthly_cycles': monthly_cycles,
        'stage_label': stage_event.get('stage_label'),
        'stage_event': stage_event,
    }
