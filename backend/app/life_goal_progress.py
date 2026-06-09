from __future__ import annotations

from typing import Any

from . import fate_mapper, life_metrics, life_stage_policy


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


def goal_template(goal_id: str | None) -> dict[str, Any] | None:
    for goal in LIFE_GOAL_TEMPLATES:
        if goal['id'] == goal_id:
            return dict(goal)
    return None


def goal_score(state: dict[str, Any], goal: dict[str, Any]) -> int:
    return life_metrics.average_state(state, life_metrics.string_list(goal.get('score_keys'), [], 8), 50)


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
    stage = life_stage_policy.age_stage(session.get('start_age') or session.get('current_age') or 22)
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
