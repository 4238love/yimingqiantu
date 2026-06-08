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


LIFE_GOAL_TEMPLATES = [
    {
        'id': 'stable_abundance',
        'title': '稳定富足',
        'summary': '希望一生有足够的物质余量、稳定生活和可抵御风险的安全感。',
        'score_keys': ['财富', '事业', '健康', '福德'],
        'support_actions': ['投资理财', '发展事业', '调养身体', '陪伴家人'],
        'ending_threshold': 72,
    },
    {
        'id': 'recognized_work',
        'title': '事业有成',
        'summary': '希望把学识、专业和长期投入转化成被看见的事业成果。',
        'score_keys': ['事业', '学识', '名望', '心智'],
        'support_actions': ['专注学业', '发展事业', '社交拓展', '创业冒险'],
        'ending_threshold': 74,
    },
    {
        'id': 'warm_bonds',
        'title': '亲密圆满',
        'summary': '希望在家庭、伴侣、朋友和重要关系里获得稳定连接。',
        'score_keys': ['家庭', '感情', '社交', '情绪'],
        'support_actions': ['经营感情', '陪伴家人', '社交拓展', '调养身体'],
        'ending_threshold': 72,
    },
    {
        'id': 'inner_peace',
        'title': '身心安稳',
        'summary': '希望不被压力吞没，在健康、情绪和精神余量里过完这一生。',
        'score_keys': ['健康', '心智', '情绪', '福德'],
        'support_actions': ['调养身体', '随缘而行', '陪伴家人', '搬迁远行'],
        'ending_threshold': 72,
    },
    {
        'id': 'free_explorer',
        'title': '自由探索',
        'summary': '希望拥有更广阔的生活半径，在迁移、社交和冒险中寻找另一种可能。',
        'score_keys': ['社交', '心智', '名望', '福德'],
        'support_actions': ['搬迁远行', '社交拓展', '创业冒险', '随缘而行'],
        'ending_threshold': 70,
    },
]


ACHIEVEMENT_DEFINITIONS = {
    'first_choice': {
        'title': '命途初定',
        'description': '完成第一次半年度选择，真正把命盘底色交到自己手里。',
        'category': '旅程',
    },
    'first_success': {
        'title': '初见顺风',
        'description': '第一次在 D100 判定中取得成功，证明积累与时势可以互相借力。',
        'category': '判定',
    },
    'great_success': {
        'title': '天光乍破',
        'description': '触发一次大成功，人生里出现罕见的高光窗口。',
        'category': '判定',
    },
    'scholar_seed': {
        'title': '学识成种',
        'description': '学识积累突破 75，学习与专业能力成为可靠筹码。',
        'category': '成长',
    },
    'career_foundation': {
        'title': '立业有基',
        'description': '事业积累突破 70，职业或社会角色开始形成稳定基础。',
        'category': '事业',
    },
    'wealth_buffer': {
        'title': '余粮在仓',
        'description': '财富突破 65，生活开始拥有抵御风险的物质余量。',
        'category': '资产',
    },
    'warm_anchor': {
        'title': '灯火可归',
        'description': '家庭与感情形成稳定支点，关系不再只是消耗。',
        'category': '关系',
    },
    'health_guardian': {
        'title': '身心护城',
        'description': '健康保持在高位，身体底盘成为长期选择的保护层。',
        'category': '健康',
    },
    'goal_aligned': {
        'title': '愿望同频',
        'description': '一次行动清晰贴合当前人生愿望，让选择更有方向。',
        'category': '愿望',
    },
    'comeback': {
        'title': '逆风回身',
        'description': '在失败之后重新取得成功，把挫折转化成下一段路的经验。',
        'category': '韧性',
    },
}


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


def score_label(score: int) -> str:
    if score >= 80:
        return '稳固'
    if score >= 65:
        return '向好'
    if score >= 45:
        return '摇摆'
    if score >= 25:
        return '吃紧'
    return '危急'


def trend_label(delta: int) -> str:
    if delta >= 3:
        return '上升'
    if delta <= -3:
        return '下滑'
    return '平稳'


def average_state(state: dict[str, Any], keys: list[str], fallback: int = 50) -> int:
    values = []
    for key in keys:
        try:
            values.append(int(state.get(key, fallback)))
        except (TypeError, ValueError):
            values.append(fallback)
    return fate_mapper.clamp(round(sum(values) / max(1, len(values))))


def system_stage(kind: str, age: int, score: int) -> str:
    if kind == 'career':
        if age <= 12:
            base = '启蒙学习'
        elif age <= 18:
            base = '升学准备'
        elif age <= 25:
            base = '职业入口'
        elif age <= 35:
            base = '事业定型'
        elif age <= 50:
            base = '转型经营'
        else:
            base = '经验传承'
    elif kind == 'assets':
        if age <= 18:
            base = '家庭供养'
        elif age <= 25:
            base = '独立起步'
        elif age <= 35:
            base = '资产起盘'
        elif age <= 50:
            base = '结构配置'
        else:
            base = '安全守成'
    else:
        if age <= 12:
            base = '家庭依附'
        elif age <= 18:
            base = '同伴成形'
        elif age <= 25:
            base = '亲密探索'
        elif age <= 40:
            base = '承诺经营'
        else:
            base = '关系修复'
    return base + ' · ' + score_label(score)


def _string_list(value: Any, fallback: list[str] | None = None, limit: int = 12) -> list[str]:
    if not isinstance(value, list):
        return list(fallback or [])
    result = [str(item).strip() for item in value if str(item).strip()]
    return result[:limit] or list(fallback or [])


def goal_template(goal_id: str | None) -> dict[str, Any] | None:
    for goal in LIFE_GOAL_TEMPLATES:
        if goal['id'] == goal_id:
            return dict(goal)
    return None


def goal_score(state: dict[str, Any], goal: dict[str, Any]) -> int:
    return average_state(state, _string_list(goal.get('score_keys'), [], 8), 50)


def goal_stage(score: int, threshold: int) -> str:
    if score >= threshold:
        return '接近达成'
    if score >= threshold - 12:
        return '稳步推进'
    if score >= threshold - 28:
        return '仍在积累'
    return '偏离目标'


def build_life_goals(session: dict[str, Any]) -> list[dict[str, Any]]:
    state = session.get('life_state') or {}
    stage = age_stage(session.get('start_age') or session.get('current_age') or 22)
    goals = []
    for template in LIFE_GOAL_TEMPLATES:
        score = goal_score(state, template)
        threshold = int(template.get('ending_threshold') or 72)
        goals.append({
            'id': template['id'],
            'title': template['title'],
            'summary': template['summary'],
            'score_keys': list(template.get('score_keys') or []),
            'support_actions': list(template.get('support_actions') or []),
            'ending_threshold': threshold,
            'recommended_for_stage': any(action in stage.get('action_options', []) for action in template.get('support_actions', [])),
            'current_score': score,
            'status': goal_stage(score, threshold),
        })
    return goals


def default_life_goal_id(session: dict[str, Any]) -> str:
    state = session.get('life_state') or {}
    if int(state.get('财富', 0)) >= 55 and int(state.get('健康', 0)) >= 55:
        return 'stable_abundance'
    if int(state.get('事业', 0)) + int(state.get('学识', 0)) >= int(state.get('家庭', 0)) + int(state.get('感情', 0)):
        return 'recognized_work'
    if int(state.get('家庭', 0)) + int(state.get('感情', 0)) >= 110:
        return 'warm_bonds'
    if int(state.get('压力', 0)) >= 45 or int(state.get('健康', 0)) <= 55:
        return 'inner_peace'
    return 'stable_abundance'


def ensure_life_goals(session: dict[str, Any]) -> list[dict[str, Any]]:
    goals: list[dict[str, Any]] = []
    existing = session.get('life_goals')
    if isinstance(existing, list) and existing:
        goals = existing
    else:
        goals = build_life_goals(session)
        session['life_goals'] = goals
    active_id = str(session.get('active_life_goal_id') or '')
    if not active_id or not any(goal.get('id') == active_id for goal in goals if isinstance(goal, dict)):
        session['active_life_goal_id'] = default_life_goal_id(session)
    return session.get('life_goals') or []


def active_life_goal(session: dict[str, Any]) -> dict[str, Any]:
    goals = ensure_life_goals(session)
    active_id = str(session.get('active_life_goal_id') or '')
    for goal in goals:
        if isinstance(goal, dict) and goal.get('id') == active_id:
            return goal
    return goals[0] if goals and isinstance(goals[0], dict) else dict(LIFE_GOAL_TEMPLATES[0])


def refresh_goal_progress(session: dict[str, Any]) -> dict[str, Any]:
    goals = build_life_goals(session)
    session['life_goals'] = goals
    active_id = str(session.get('active_life_goal_id') or '')
    if not active_id or not any(goal['id'] == active_id for goal in goals):
        active_id = default_life_goal_id(session)
        session['active_life_goal_id'] = active_id
    active = next((goal for goal in goals if goal['id'] == active_id), goals[0])
    threshold = int(active.get('ending_threshold') or 72)
    score = int(active.get('current_score') or 0)
    progress = {
        'goal_id': active['id'],
        'title': active['title'],
        'summary': active['summary'],
        'score': score,
        'threshold': threshold,
        'percent': fate_mapper.clamp(round(score / max(1, threshold) * 100)),
        'status': goal_stage(score, threshold),
        'support_actions': active.get('support_actions') or [],
        'achieved': score >= threshold,
    }
    session['goal_progress'] = progress
    return progress


def action_goal_alignment(session: dict[str, Any], action: str) -> dict[str, Any]:
    progress = session.get('goal_progress') or {}
    goal = active_life_goal(session) if session.get('life_state') else {}
    support_actions = _string_list(progress.get('support_actions') or goal.get('support_actions'), [], 8)
    score_keys = _string_list(goal.get('score_keys'), [], 8)
    profile = fate_mapper.ACTION_PROFILES.get(action, fate_mapper.ACTION_PROFILES['随缘而行'])
    primary = str(profile.get('primary') or '')
    secondary = str(profile.get('secondary') or '')
    risk = str(profile.get('risk') or '')
    if action in support_actions:
        return {
            'level': '高度契合',
            'score': 3,
            'reason': '直接支持当前人生愿望“' + str(progress.get('title') or goal.get('title') or '未命名愿望') + '”。',
        }
    if primary in score_keys or secondary in score_keys:
        return {
            'level': '间接助力',
            'score': 2,
            'reason': '会提升愿望看重的“' + (primary if primary in score_keys else secondary) + '”。',
        }
    if risk in score_keys:
        return {
            'level': '需要权衡',
            'score': 1,
            'reason': '可能消耗愿望看重的“' + risk + '”，适合作为阶段性取舍而非长期单押。',
        }
    return {
        'level': '中性探索',
        'score': 1,
        'reason': '不直接推动当前愿望，但可能补足长期人生结构。',
    }


def action_preview_summary(action: str, action_summaries: dict[str, str] | None = None) -> str:
    summaries = action_summaries or {}
    text = summaries.get(action) or summaries.get('随缘而行') or str(event_pool.ACTION_META.get(action, {}).get('clue') or '')
    first_sentence = str(text).split('。')[0].strip()
    return first_sentence + '。' if first_sentence else str(text)


def build_action_guides(session: dict[str, Any], action_summaries: dict[str, str] | None = None) -> list[dict[str, Any]]:
    age = session.get('current_age') if session.get('current_age') is not None else session.get('start_age')
    if age is None:
        return []
    guides = []
    state = session.get('life_state') or {}
    stage = age_stage(int(age))
    for action in stage_action_options(int(age)):
        profile = fate_mapper.ACTION_PROFILES.get(action, fate_mapper.ACTION_PROFILES['随缘而行'])
        target, modifiers = fate_mapper.compute_roll_target(session, action)
        predicted_count = 1
        memory = normalize_focus_memory(session.get('focus_memory'))
        if str(memory.get('last_focus') or '') == action:
            predicted_count = int(memory.get('streak') or 0) + 1
        streak_bonus = focus_streak_roll_bonus(predicted_count)
        target_preview = fate_mapper.clamp(target + streak_bonus, 20, 95)
        primary = str(profile.get('primary') or '')
        secondary = str(profile.get('secondary') or '')
        risk = str(profile.get('risk') or '')
        meta = event_pool.ACTION_META.get(action, {})
        guides.append({
            'action': action,
            'stage_id': stage.get('id'),
            'stage_label': stage.get('label'),
            'primary': primary,
            'secondary': secondary,
            'risk': risk,
            'primary_score': int(state.get(primary, 0)) if primary else 0,
            'secondary_score': int(state.get(secondary, 0)) if secondary else 0,
            'risk_score': int(state.get(risk, 0)) if risk else 0,
            'goal_alignment': action_goal_alignment(session, action),
            'roll_target_base': target,
            'roll_target_preview': target_preview,
            'roll_modifiers': modifiers,
            'streak_preview': {
                'count': predicted_count,
                'bonus': streak_bonus,
                'will_continue': str(memory.get('last_focus') or '') == action and predicted_count > 1,
            },
            'tags': list(meta.get('tags') or []),
            'clue': str(meta.get('clue') or ''),
            'summary': action_preview_summary(action, action_summaries),
        })
    guides.sort(key=lambda item: (int(item.get('goal_alignment', {}).get('score') or 0), int(item.get('streak_preview', {}).get('bonus') or 0), int(item.get('roll_target_preview') or 0)), reverse=True)
    return guides


def ensure_life_systems(session: dict[str, Any]) -> dict[str, Any]:
    systems = session.get('life_systems')
    if isinstance(systems, dict) and {'relationship', 'career', 'assets'} <= set(systems):
        return systems
    session['life_systems'] = {
        'relationship': {'label': '关系网络', 'score': 50, 'stage': '未展开', 'trend': '平稳', 'notes': []},
        'career': {'label': '学业/职业', 'score': 50, 'stage': '未展开', 'trend': '平稳', 'notes': []},
        'assets': {'label': '资产基础', 'score': 50, 'stage': '未展开', 'trend': '平稳', 'notes': []},
    }
    return session['life_systems']


def refresh_relationships(session: dict[str, Any]) -> None:
    state = session.get('life_state') or {}
    age = int(session.get('current_age') or session.get('start_age') or 22)
    peer_name = '同伴关系' if age <= 18 else '伴侣/亲密关系'
    mentor_name = '师长支持' if age <= 18 else '贵人与合作'
    session['relationships'] = [
        {
            'name': '家庭支持',
            'type': '家庭',
            'closeness': fate_mapper.clamp(int(state.get('家庭', 50))),
            'status': score_label(int(state.get('家庭', 50))),
        },
        {
            'name': peer_name,
            'type': '同伴/亲密',
            'closeness': average_state(state, ['感情', '社交', '情绪']),
            'status': score_label(average_state(state, ['感情', '社交', '情绪'])),
        },
        {
            'name': mentor_name,
            'type': '机会',
            'closeness': average_state(state, ['社交', '名望', '事业']),
            'status': score_label(average_state(state, ['社交', '名望', '事业'])),
        },
    ]


def refresh_life_systems(session: dict[str, Any], record: dict[str, Any] | None = None) -> None:
    systems = ensure_life_systems(session)
    state = session.get('life_state') or {}
    age = int(session.get('current_age') or session.get('start_age') or 22)
    scores = {
        'relationship': average_state(state, ['家庭', '感情', '社交', '情绪']),
        'career': average_state(state, ['学识', '事业', '名望', '心智']),
        'assets': average_state(state, ['财富', '事业', '福德']),
    }
    note = ''
    if record:
        stage_event = record.get('stage_event') or {}
        note = (
            str(record.get('age')) + '岁' + str(record.get('half_label') or '') +
            ' · ' + str(record.get('main_focus') or '随缘而行') +
            '：' + str(stage_event.get('event') or record.get('summary') or '')[:48]
        )
    for key, score in scores.items():
        previous = int((systems.get(key) or {}).get('score', score))
        item = systems.get(key) or {}
        item['score'] = score
        item['stage'] = system_stage(key, age, score)
        item['trend'] = trend_label(score - previous)
        item['label'] = item.get('label') or {'relationship': '关系网络', 'career': '学业/职业', 'assets': '资产基础'}[key]
        notes = _string_list(item.get('notes'), [], 8)
        if note and note not in notes:
            notes.append(note)
        item['notes'] = notes[-5:]
        systems[key] = item
    session['life_systems'] = systems
    refresh_relationships(session)


def refresh_current_context(session: dict[str, Any], action_summaries: dict[str, str] | None = None) -> None:
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
    session['action_guides'] = build_action_guides(session, action_summaries)
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
        '行动预览': session.get('action_guides', []),
        '长期系统': session.get('life_systems', {}),
        '关系': session.get('relationships', []),
        '连续选择': session.get('focus_streak', {}),
        '行动记忆': session.get('focus_memory', {}),
        '成就': session.get('achievements', []),
        '里程碑': session.get('milestones', [])[-10:],
        '性格': session.get('personality', []),
    }


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
