from __future__ import annotations

import random
import time
from copy import deepcopy
from typing import Any

from . import achievement_resolution, event_pool, fate_mapper, life_goal_progress, life_metrics, life_stage_policy, life_systems

ACTION_OPTIONS = life_stage_policy.ACTION_OPTIONS
AGE_STAGE_PROFILES = life_stage_policy.AGE_STAGE_PROFILES
LIFE_GOAL_TEMPLATES = life_goal_progress.LIFE_GOAL_TEMPLATES
ACHIEVEMENT_DEFINITIONS = achievement_resolution.ACHIEVEMENT_DEFINITIONS


def age_stage(age: int | None) -> dict[str, Any]:
    return life_stage_policy.age_stage(age)


def stage_action_options(age: int | None) -> list[str]:
    return life_stage_policy.stage_action_options(age)


def stage_safe_action(age: int | None, action: str) -> str:
    return life_stage_policy.stage_safe_action(age, action)

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

def score_label(score: int) -> str:
    return life_metrics.score_label(score)


def trend_label(delta: int) -> str:
    return life_metrics.trend_label(delta)


def average_state(state: dict[str, Any], keys: list[str], fallback: int = 50) -> int:
    return life_metrics.average_state(state, keys, fallback)


def system_stage(kind: str, age: int, score: int) -> str:
    return life_metrics.system_stage(kind, age, score)


def _string_list(value: Any, fallback: list[str] | None = None, limit: int = 12) -> list[str]:
    return life_metrics.string_list(value, fallback, limit)

def goal_template(goal_id: str | None) -> dict[str, Any] | None:
    return life_goal_progress.goal_template(goal_id)


def goal_score(state: dict[str, Any], goal: dict[str, Any]) -> int:
    return life_goal_progress.goal_score(state, goal)


def goal_stage(score: int, threshold: int) -> str:
    return life_goal_progress.goal_stage(score, threshold)


def build_life_goals(session: dict[str, Any]) -> list[dict[str, Any]]:
    return life_goal_progress.build_life_goals(session)


def default_life_goal_id(session: dict[str, Any]) -> str:
    return life_goal_progress.default_life_goal_id(session)


def ensure_life_goals(session: dict[str, Any]) -> list[dict[str, Any]]:
    return life_goal_progress.ensure_life_goals(session)


def active_life_goal(session: dict[str, Any]) -> dict[str, Any]:
    return life_goal_progress.active_life_goal(session)


def refresh_goal_progress(session: dict[str, Any]) -> dict[str, Any]:
    return life_goal_progress.refresh_goal_progress(session)

def ensure_life_systems(session: dict[str, Any]) -> dict[str, Any]:
    return life_systems.ensure_life_systems(session)


def refresh_relationships(session: dict[str, Any]) -> None:
    life_systems.refresh_relationships(session)


def refresh_life_systems(session: dict[str, Any], record: dict[str, Any] | None = None) -> None:
    life_systems.refresh_life_systems(session, record)

def refresh_authoritative_context(session: dict[str, Any]) -> None:
    """Refresh deterministic context needed by authoritative half-year resolution.

    Advisory action_guides and current_life display projection live in the
    Life Context Projection Module so this Module keeps a narrow authority seam.
    """
    age = session.get('current_age')
    if age is None:
        return
    session['current_luck_cycle'] = fate_mapper.find_luck_cycle(session, int(age))
    session['current_annual_cycle'] = fate_mapper.find_annual_cycle(session, int(age))
    current_half = int(session.get('current_half') or 1)
    session['current_half'] = 2 if current_half == 2 else 1
    session['current_half_label'] = fate_mapper.half_label(session['current_half'])
    session['current_monthly_cycles'] = fate_mapper.find_monthly_cycles(session, int(age), session['current_half'])
    session['current_stage'] = age_stage(int(age))
    session['action_options'] = stage_action_options(int(age))
    refresh_life_systems(session)
    refresh_goal_progress(session)

def refresh_current_context(session: dict[str, Any], action_summaries: dict[str, str] | None = None) -> None:
    """Backward-compatible alias for deterministic context refresh.

    The action_summaries argument is intentionally ignored. Use
    life_context_projection.refresh_current_context() when callers need the
    player-facing action guide projection.
    """
    refresh_authoritative_context(session)

def build_current_life_projection(session: dict[str, Any]) -> dict[str, Any]:
    """Build the authoritative subset of current_life without advisory fields."""
    session['current_life'] = {
        '年龄': session.get('current_age'),
        '年份': session.get('current_year'),
        '当前半年': session.get('current_half_label'),
        '人生阶段': session.get('current_stage'),
        '当前大运': session.get('current_luck_cycle'),
        '当前流年': session.get('current_annual_cycle'),
        '当前流月': session.get('current_monthly_cycles'),
        '人生状态': session.get('life_state', {}),
        '人生愿望': session.get('goal_progress', {}),
        '长期系统': session.get('life_systems', {}),
        '关系': session.get('relationships', []),
        '连续选择': session.get('focus_streak', {}),
        '行动记忆': session.get('focus_memory', {}),
        '成就': session.get('achievements', []),
        '里程碑': session.get('milestones', [])[-10:],
        '性格': session.get('personality', []),
    }
    return session['current_life']

def advance_turn_cursor(session: dict[str, Any], record: dict[str, Any]) -> None:
    half = int(record.get('half') or session.get('current_half') or 1)
    age = int(record.get('age') or session.get('current_age') or session.get('start_age') or 22)
    if half == 1:
        session['current_half'] = 2
        session['current_half_label'] = '下半年'
        return
    session['current_half'] = 1
    session['current_half_label'] = '上半年'
    session['current_age'] = age + 1
    session['current_year'] = int(session.get('current_year') or record.get('year') or 0) + 1

def finish_reason(session: dict[str, Any]) -> str:
    if int(session.get('life_state', {}).get('健康', 1)) <= 0:
        return 'health_zero'
    if int(session.get('current_age') or 0) >= 60:
        return 'age_60'
    return ''

def achievement_unlocked(session: dict[str, Any], achievement_id: str) -> bool:
    return any(isinstance(item, dict) and item.get('id') == achievement_id for item in session.get('achievements') or [])

def unlock_achievement(session: dict[str, Any], achievement_id: str, age: int, half_label: str) -> dict[str, Any] | None:
    if achievement_unlocked(session, achievement_id):
        return None
    definition = ACHIEVEMENT_DEFINITIONS.get(achievement_id)
    if not definition:
        return None
    achievement = {
        'id': achievement_id,
        'title': definition['title'],
        'description': definition['description'],
        'category': definition['category'],
        'age': age,
        'half_label': half_label,
        'unlocked_at': str(age) + '岁' + str(half_label),
    }
    session.setdefault('achievements', []).append(achievement)
    return achievement

def evaluate_achievements(session: dict[str, Any], record: dict[str, Any]) -> list[dict[str, Any]]:
    age = int(record.get('age') or session.get('current_age') or 0)
    half_label = str(record.get('half_label') or '')
    roll_event = record.get('roll_event') or {}
    outcome = str(roll_event.get('outcome') or '')
    state = session.get('life_state') or {}
    active_goal = active_life_goal(session)
    support_actions = _string_list(active_goal.get('support_actions'), [], 8)
    previous = session.get('annual_summaries') or []
    previous_outcome = ''
    if previous:
        previous_outcome = str(((previous[-1] or {}).get('roll_event') or {}).get('outcome') or '')
    candidates = ['first_choice']
    if outcome in ['成功', '大成功']:
        candidates.append('first_success')
    if outcome == '大成功':
        candidates.append('great_success')
    if previous_outcome in ['失败', '大失败'] and outcome in ['成功', '大成功']:
        candidates.append('comeback')
    if int(state.get('学识', 0)) >= 75:
        candidates.append('scholar_seed')
    if int(state.get('事业', 0)) >= 70:
        candidates.append('career_foundation')
    if int(state.get('财富', 0)) >= 65:
        candidates.append('wealth_buffer')
    if int(state.get('家庭', 0)) + int(state.get('感情', 0)) >= 140:
        candidates.append('warm_anchor')
    if int(state.get('健康', 0)) >= 82:
        candidates.append('health_guardian')
    if str(record.get('main_focus') or '') in support_actions:
        candidates.append('goal_aligned')
    unlocked = []
    for achievement_id in candidates:
        achievement = unlock_achievement(session, achievement_id, age, half_label)
        if achievement:
            unlocked.append(achievement)
    session['latest_achievements'] = unlocked
    return unlocked

def append_milestone(session: dict[str, Any], record: dict[str, Any], achievements: list[dict[str, Any]]) -> dict[str, Any]:
    stage_event = record.get('stage_event') or {}
    roll_event = record.get('roll_event') or {}
    age_half = str(record.get('age') or '') + '岁' + str(record.get('half_label') or '')
    milestone = {
        'id': 'milestone_' + str(int(time.time() * 1000)) + '_' + str(len(session.get('milestones') or [])),
        'age': record.get('age'),
        'year': record.get('year'),
        'half_label': record.get('half_label'),
        'title': age_half + ' · ' + str(record.get('main_focus') or '随缘而行') + ' · ' + str(roll_event.get('outcome') or '未知'),
        'text': str(stage_event.get('event') or record.get('summary') or '')[:180],
        'stage_label': stage_event.get('stage_label') or record.get('stage_label') or '',
        'goal_title': (record.get('goal_progress_after') or {}).get('title') or '',
        'achievement_titles': [item.get('title') for item in achievements if item.get('title')],
    }
    milestones = session.setdefault('milestones', [])
    milestones.append(milestone)
    session['milestones'] = milestones[-80:]
    return milestone

def complete_authoritative_record(session: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """Attach deterministic progress artifacts to an authoritative half-year record."""
    refresh_life_systems(session, record)
    goal_progress_after = refresh_goal_progress(session)
    record['life_systems_after'] = deepcopy(session.get('life_systems') or {})
    record['relationships_after'] = deepcopy(session.get('relationships') or [])
    record['goal_progress_after'] = deepcopy(goal_progress_after)
    new_achievements = evaluate_achievements(session, record)
    record['new_achievements'] = deepcopy(new_achievements)
    milestone = append_milestone(session, record, new_achievements)
    record['milestone'] = deepcopy(milestone)
    return record

def build_focus_streak_feedback(session: dict[str, Any], action: str) -> dict[str, Any]:
    memory = normalize_focus_memory(session.get('focus_memory'))
    previous_focus = str(memory.get('last_focus') or '')
    previous_streak = int(memory.get('streak') or 0)
    count = previous_streak + 1 if previous_focus == action else 1
    bonus = focus_streak_roll_bonus(count)
    state_effect = focus_streak_state_effect(action, count)
    if count <= 1:
        warning = '这是“' + action + '”的新一轮投入；如果后续继续选择同一重点，会逐步形成习惯优势，也会积累机会成本。'
    elif count == 2:
        warning = '连续2个半年投入“' + action + '”，惯性开始成形：本次后台推演获得小幅连续投入修正。'
    elif count == 3:
        warning = '连续3个半年投入“' + action + '”，路线更清晰，习惯优势提高，但生活其他面向开始要求补偿。'
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

def _cycle_text(luck: dict[str, Any], annual: dict[str, Any], monthly_cycles: list[dict[str, Any]]) -> str:
    parts = []
    if luck.get('pillar'):
        themes = _string_list(luck.get('theme'), [], 3)
        parts.append('大运' + str(luck.get('pillar')) + ('带来' + '、'.join(themes) if themes else '给出十年基调'))
    if annual.get('pillar'):
        events = _string_list(annual.get('events'), [], 3)
        parts.append('流年' + str(annual.get('pillar')) + ('牵动' + '、'.join(events) if events else '带来年度变化'))
    opportunities = []
    risks = []
    for month in monthly_cycles:
        opportunities.extend(_string_list(month.get('opportunity'), [], 2))
        risks.extend(_string_list(month.get('risk'), [], 2))
    if opportunities:
        parts.append('流月机会集中在' + '、'.join(list(dict.fromkeys(opportunities))[:3]))
    if risks:
        parts.append('风险集中在' + '、'.join(list(dict.fromkeys(risks))[:3]))
    return '；'.join(parts) if parts else '时运信息暂不完整'


ELEMENT_LIFE_TEXTURES = {
    '木': '木气让你更容易被“成长、兴趣、同伴比较”牵动，遇到新任务时会先想办法往前伸展。',
    '火': '火气让你在被看见、被表扬或被评价时反应更快，热情能点燃行动，也容易被急躁推着走。',
    '土': '土气让你格外需要稳定的作息、熟悉的大人和可预期的环境，安全感会直接影响投入程度。',
    '金': '金气让你对规则、标准、对错和输赢更敏感，愿意把一件事磨到“合格”为止。',
    '水': '水气让你习惯先观察情绪和环境，再决定投入多少；安静、信息和休息会帮你恢复判断力。',
}

USEFUL_ELEMENT_TEXTURES = {
    '木': '靠持续练习、兴趣生长和一点点被鼓励来打开局面',
    '火': '靠表达、热情、被看见的反馈来维持动力',
    '土': '靠稳定作息、家庭支持和清楚边界来托住自己',
    '金': '靠规则、标准、专门训练和可验证结果来积累底气',
    '水': '靠安静思考、信息整理、休息和灵活转弯来恢复弹性',
}

TEN_GOD_LIFE_TEXTURES = {
    '正官': '面对老师、上级或规则时，你会更在意“这样做是否被认可”。',
    '七杀': '压力来得急时，你反而容易被逼出行动力，但也会绷得更紧。',
    '正印': '来自长辈、老师或制度的保护感，会让你更敢慢慢学。',
    '偏印': '你会用自己的方式理解世界，偶尔显得安静、绕远，但能留下独特记忆。',
    '正财': '具体资源、作息和现实回报会让你更安心，空泛鼓励不如看得见的进展。',
    '偏财': '新鲜机会和外部变化容易吸引你，也考验你是否能守住节奏。',
    '食神': '稳定的兴趣、表达和作品感会缓冲压力，让日子不只是完成任务。',
    '伤官': '你不太愿意只按别人说的做，若被压得太紧，就会在细节里反抗。',
    '比肩': '同伴比较会激起你的自尊，也可能让你更固执地想证明自己。',
    '劫财': '朋友、同学或合伙人的影响会放大选择的波动，热闹里也有消耗。',
    '日主': '你会把外界变化先放回“我能不能承受、我要不要继续”这个问题里。',
}

DEFAULT_ACTION_DAILY_SCENES = {
    '专注学业': '你把日子切成一小段一小段：摊开课本、补错题、整理笔记，遇到不会的地方就反复回到同一个知识点。',
    '发展事业': '你把更多时间交给任务、会议、交付和复盘，开始在别人的评价里确认自己的专业位置。',
    '经营感情': '你把一些含混的情绪说出口，约见、解释、等待回复，也重新学习怎样给亲密关系留边界。',
    '陪伴家人': '你回到饭桌、家务、探望和日常照料里，听见家人没有明说的担心，也看见自己能承担多少。',
    '投资理财': '你开始翻账本、看余额、拆分收入和风险，某些消费被延后，某些计划第一次变得具体。',
    '调养身体': '你把睡眠、饮食、运动或检查重新排进日程，身体的疲惫不再被当成可以无限拖延的小事。',
    '社交拓展': '你主动走进新的活动、聊天和合作里，在热闹与筛选之间判断谁能同行、谁只会消耗。',
    '创业冒险': '你把想法写成计划，联系资源、试探市场、计算成本，兴奋感和不确定性一起压到桌面上。',
    '搬迁远行': '你整理证件、路线、住处和行李，熟悉的支持系统暂时退后，新的坐标开始改变你的日常。',
    '随缘而行': '你没有把自己推得太紧，而是在休息、观察、整理和偶然出现的信号里慢慢调整方向。',
}

CHILDHOOD_ACTION_DAILY_SCENES = {
    '专注学业': '最具体的变化，是放学后先摊开本子：铅笔字、拼音、算式和老师画下的红圈，慢慢变成你理解世界的秩序。',
    '陪伴家人': '你更多待在家人身边：饭桌上的问答、睡前的叮嘱、被牵着过马路的小动作，都在确认自己是否被稳定接住。',
    '调养身体': '你开始被提醒按时吃饭、早点睡、少逞强；一次咳嗽、摔跤或疲惫，会让大人重新安排你的节奏。',
    '社交拓展': '你在同桌、玩伴和小组活动里学习靠近别人：分享文具、排队、争抢和和好，都会留下关系的第一批经验。',
    '搬迁远行': '环境变化会先落在书包、座位、路线和陌生面孔上；你要重新判断谁可靠，哪里能让自己放松。',
    '随缘而行': '你没有特别用力，只是在课堂、游戏、饭桌和午睡之间观察大人的脸色，也观察自己真正喜欢什么。',
}

ADOLESCENCE_ACTION_DAILY_SCENES = {
    '专注学业': '你把更多时间压进试卷、排名、错题本和自习铃声里，成绩不再只是表扬，而是通往下一段人生的门票。',
    '经营感情': '你开始在友情、朦胧心动和自我保护之间摇摆；一句话、一次等候、一个眼神都会被反复咀嚼。',
    '陪伴家人': '你和家人的距离变得敏感：有些话想说又忍住，有些照顾明明需要，却又不想显得依赖。',
    '调养身体': '身体、睡眠和情绪开始影响成绩与关系，你逐渐发现硬撑并不总能换来更好的结果。',
    '社交拓展': '同伴圈层变得重要，你在加入、拒绝、被比较和被认可之间，重新确认自己是谁。',
    '搬迁远行': '换班、转学、住校或远行让你离开原来的标签，新环境给你重来的机会，也放大孤独感。',
    '随缘而行': '你暂时不急着给未来定论，而是在兴趣、朋友、家庭期待和自我怀疑之间给自己留一点缓冲。',
}

STATE_LIFE_EFFECTS = {
    '健康': ('身体更能承受日程变化', '身体提醒你必须慢下来'),
    '心智': ('处理问题时更能沉住气', '判断力被压力和噪音拖慢'),
    '情绪': ('情绪更容易被安放', '情绪更容易被小事牵动'),
    '学识': ('学习和理解的底气增加', '学习节奏受到干扰'),
    '事业': ('责任和交付经验增加', '事业线暂时被牵制'),
    '财富': ('资源余量变得更清楚', '财务安全感被削弱'),
    '家庭': ('家庭支持感更稳', '家庭责任或距离感带来消耗'),
    '感情': ('亲密表达更具体', '亲密关系里出现新的不安'),
    '社交': ('新的关系入口被打开', '关系热闹里夹着消耗'),
    '名望': ('被看见的机会增加', '外界评价带来压力'),
    '福德': ('生活里多了一点缓冲和机缘', '留白减少，喘息感变少'),
    '压力': ('压力被释放了一些', '压力在日常细节里继续累积'),
}


def _unique_strings(*values: Any, limit: int = 6) -> list[str]:
    result: list[str] = []
    for value in values:
        for item in _string_list(value, [], limit):
            if item not in result:
                result.append(item)
            if len(result) >= limit:
                return result
    return result


def _stage_action_scene(stage_event: dict[str, Any], action: str) -> str:
    stage_id = str(stage_event.get('stage_id') or '')
    if stage_id == 'childhood':
        return CHILDHOOD_ACTION_DAILY_SCENES.get(action, DEFAULT_ACTION_DAILY_SCENES.get(action, DEFAULT_ACTION_DAILY_SCENES['随缘而行']))
    if stage_id == 'adolescence':
        return ADOLESCENCE_ACTION_DAILY_SCENES.get(action, DEFAULT_ACTION_DAILY_SCENES.get(action, DEFAULT_ACTION_DAILY_SCENES['随缘而行']))
    return DEFAULT_ACTION_DAILY_SCENES.get(action, DEFAULT_ACTION_DAILY_SCENES['随缘而行'])


def _day_master_element(day_master: str) -> str:
    for element in ['木', '火', '土', '金', '水']:
        if element in day_master:
            return element
    return ''


def _ten_god_focuses(session: dict[str, Any], chart: dict[str, Any]) -> list[str]:
    analysis = session.get('bazi_analysis') or {}
    focuses = _string_list(analysis.get('ten_god_focus'), [], 3)
    if focuses:
        return focuses
    values = list((chart.get('ten_gods') or {}).values())
    return _unique_strings(values, limit=3)


def _build_bazi_life_detail(session: dict[str, Any], main_focus: str) -> str:
    chart = session.get('bazi_chart') or {}
    chart_tags = _string_list(session.get('chart_tags'), [], 4)
    day_master = str(chart.get('day_master') or '日主')
    day_strength = str(chart.get('day_strength') or '中和')
    element = _day_master_element(day_master)
    element_text = ELEMENT_LIFE_TEXTURES.get(element, '命盘底色会先表现为你处理压力、机会和亲近关系时的惯性。')
    useful = _string_list(chart.get('useful_elements'), [], 3)
    useful_texts = [USEFUL_ELEMENT_TEXTURES[element_name] for element_name in useful if element_name in USEFUL_ELEMENT_TEXTURES]
    ten_gods = _ten_god_focuses(session, chart)
    ten_god_texts = [TEN_GOD_LIFE_TEXTURES[item] for item in ten_gods if item in TEN_GOD_LIFE_TEXTURES]
    strength_text = '身势偏强时，你更容易先坚持自己的判断；需要有人帮你把劲用到合适的地方。'
    if '偏弱' in day_strength:
        strength_text = '身势偏弱时，你会更依赖环境的稳定和鼓励；压力太满时，行动会先变慢。'
    elif '中和' in day_strength:
        strength_text = '身势中和时，你能在顺从规则和保留自己之间调整，但也容易被当下气氛带走。'
    profile = fate_mapper.ACTION_PROFILES.get(main_focus, fate_mapper.ACTION_PROFILES['随缘而行'])
    return (
        '命盘落在生活里，不是给出一句结论，而是改变你对细节的反应：' +
        element_text + strength_text +
        (('对你来说，补偏的方式更像是' + '、'.join(useful_texts) + '。') if useful_texts else '') +
        (('十神气质会把课题带到日常：' + ''.join(ten_god_texts[:2])) if ten_god_texts else '') +
        ('所以当你选择“' + main_focus + '”时，它会先牵动' + str(profile.get('primary') or '主线') +
         '，再影响' + str(profile.get('secondary') or '副线') + '；' + '、'.join(chart_tags) + '这些标签会以习惯、偏好和压力点的形式出现。' if chart_tags else
         '所以当你选择“' + main_focus + '”时，它会先牵动' + str(profile.get('primary') or '主线') + '，再影响' + str(profile.get('secondary') or '副线') + '。')
    )


def _build_month_life_detail(luck: dict[str, Any], annual: dict[str, Any], monthly_cycles: list[dict[str, Any]]) -> str:
    month_names = [str(item.get('month_name', '')) + str(item.get('pillar', '')) for item in monthly_cycles if item.get('pillar')]
    opportunities = _unique_strings(*[item.get('opportunity') for item in monthly_cycles], limit=4)
    risks = _unique_strings(*[item.get('risk') for item in monthly_cycles], limit=4)
    luck_themes = _string_list(luck.get('theme'), [], 3)
    annual_events = _string_list(annual.get('events'), [], 3)
    month_text = '、'.join(month_names[:3])
    if len(month_names) > 3:
        month_text += '到' + '、'.join(month_names[-2:])
    if not month_text:
        month_text = '本半年几个流月'
    return (
        ('大运' + str(luck.get('pillar')) + '像一层长期天气，' + '、'.join(luck_themes) + '不是写在纸上，而是表现为家里和环境给你的推力与限制。' if luck.get('pillar') else '') +
        ('流年' + str(annual.get('pillar')) + ('把' + '、'.join(annual_events) + '推到眼前，' if annual_events else '让日常节奏发生变化，') if annual.get('pillar') else '') +
        month_text + '并不是单纯的干支列表：机会会变成' + ('、'.join(opportunities) if opportunities else '几次可以顺势而为的小窗口') +
        '，风险则更像' + ('、'.join(risks) if risks else '分心、疲惫和误判') + '，在作息、关系和情绪里一点点显形。'
    )


def _build_state_life_detail(changes: dict[str, int]) -> str:
    details = []
    for key, value in (changes or {}).items():
        try:
            delta = int(value)
        except (TypeError, ValueError):
            continue
        if not delta:
            continue
        effect = STATE_LIFE_EFFECTS.get(str(key))
        if not effect:
            continue
        if str(key) == '压力':
            details.append(effect[1] if delta > 0 else effect[0])
        else:
            details.append(effect[0] if delta > 0 else effect[1])
        if len(details) >= 3:
            break
    if not details:
        return '这半年没有立刻改变外在轨迹，但它会以记忆、偏好和下一次选择时的犹豫或底气留下痕迹。'
    return '、'.join(details) + '。'


def _build_life_scene(
    session: dict[str, Any],
    focuses: list[str],
    main_focus: str,
    roll_event: dict[str, Any],
    changes: dict[str, int],
    luck: dict[str, Any],
    annual: dict[str, Any],
    monthly_cycles: list[dict[str, Any]],
    stage_event: dict[str, Any],
) -> str:
    age = str(session.get('current_age') or '')
    half_label = str(session.get('current_half_label') or fate_mapper.half_label(session.get('current_half') or 1))
    stage_label = str(stage_event.get('stage_label') or '')
    daily_scene = _stage_action_scene(stage_event, main_focus)
    event_title = str(stage_event.get('title') or '')
    event_text = str(stage_event.get('event') or '')
    outcome = str(roll_event.get('outcome') or '未知')
    if outcome in ['大成功', '成功']:
        outcome_text = '这次结果顺利，生活里的反馈来得比较快：有人看见你的变化，或者你自己第一次确认“这样做是有用的”。'
    else:
        outcome_text = '这次推进并不顺，阻力不是突然砸下来，而是藏在拖延、疲惫、误会或一次没有达标的反馈里。'
    goal = session.get('goal_progress') or {}
    goal_text = ''
    if goal.get('title'):
        goal_text = '你未必能清楚说出“' + str(goal.get('title')) + '”意味着什么，但这个愿望已经在选择背后发出很轻的牵引。'
    return (
        (age + '岁' + half_label if age else '这个半年') +
        ('，你还在“' + stage_label + '”里生活。' if stage_label else '，生活先从具体日子开始。') +
        daily_scene +
        (('触发这段变化的，是《' + event_title + '》：' + event_text) if event_text and event_title else (event_text if event_text else '')) +
        outcome_text +
        _build_month_life_detail(luck, annual, monthly_cycles) +
        _build_state_life_detail(changes) +
        goal_text
    )


def build_fate_explanation(
    session: dict[str, Any],
    focuses: list[str],
    main_focus: str,
    roll_event: dict[str, Any],
    changes: dict[str, int],
    luck: dict[str, Any],
    annual: dict[str, Any],
    monthly_cycles: list[dict[str, Any]],
    stage_event: dict[str, Any],
) -> dict[str, str]:
    chart = session.get('bazi_chart') or {}
    tags = _string_list(session.get('chart_tags'), [], 5)
    useful = _string_list(chart.get('useful_elements'), [], 3)
    profile = fate_mapper.ACTION_PROFILES.get(main_focus, fate_mapper.ACTION_PROFILES['随缘而行'])
    day_master = str(chart.get('day_master') or '日主')
    bazi_life_detail = _build_bazi_life_detail(session, main_focus)
    life_scene = _build_life_scene(session, focuses, main_focus, roll_event, changes, luck, annual, monthly_cycles, stage_event)
    month_life_detail = _build_month_life_detail(luck, annual, monthly_cycles)
    chart_text = (
        '你的命盘以' + day_master + '为底色' +
        ('，关键词是“' + '、'.join(tags) + '”' if tags else '') +
        ('，喜' + '、'.join(useful) if useful else '') +
        '。' + bazi_life_detail
    )
    fortune_text = _cycle_text(luck, annual, monthly_cycles) + '。' + month_life_detail
    outcome = str(roll_event.get('outcome') or '未知')
    if outcome in ['大成功', '成功']:
        choice_result = '这次选择被当前状态承接住了，日常反馈会更像一次温和的确认'
    else:
        choice_result = '这次选择触碰到现实阻力，挫败感会先从小事里冒出来'
    daily_scene = _stage_action_scene(stage_event, main_focus)
    choice_text = (
        '你选择“' + '、'.join(focuses) + '”。' + daily_scene + choice_result +
        '：主线推向“' + str(profile.get('primary') or '') + '”，副线牵动“' +
        str(profile.get('secondary') or '') + '”，同时把“' + str(profile.get('risk') or '机会成本') +
        '”带入账本。' + str(stage_event.get('event') or '')
    )
    change_text = format_state_effect(changes)
    life_text = (
        '人生变化表现为：' + change_text + '。' + _build_state_life_detail(changes) +
        '这些变化会转化成下一次选择时的资源余量、关系反馈、身体承载力和心理惯性。'
    )
    return {
        'life_scene': life_scene,
        'bazi_life_detail': bazi_life_detail,
        'month_life_detail': month_life_detail,
        'bazi_influence': chart_text,
        'fortune_influence': fortune_text,
        'choice_influence': choice_text,
        'life_change': life_text,
        'hidden_roll': '后台 D100：目标' + str(roll_event.get('target', '-')) + '，投掷' + str(roll_event.get('result', '-')) + '，结果' + outcome + '。',
    }


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

def resolve_authoritative_record(session: dict[str, Any], action_payload: dict[str, Any] | str) -> dict[str, Any]:
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
    fate_explanation = build_fate_explanation(session, focuses, main_focus, roll_event, changes, luck, annual, monthly_cycles, stage_event)
    return {
        'age': age,
        'year': year,
        'half': half,
        'half_label': half_label,
        'summary': summary,
        'fate_explanation': fate_explanation,
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
        'state_after': dict(session.get('life_state', {})),
        'life_systems_before': life_systems_before,
        'relationships_before': relationships_before,
        'goal_progress_before': goal_progress_before,
        'luck_cycle': luck,
        'annual_cycle': annual,
        'monthly_cycles': monthly_cycles,
        'stage_label': stage_event.get('stage_label'),
        'stage_event': stage_event,
    }

def resolve_core(session: dict[str, Any], action_payload: dict[str, Any] | str) -> dict[str, Any]:
    return resolve_authoritative_record(session, action_payload)
