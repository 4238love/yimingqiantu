from __future__ import annotations

from typing import Any

from . import event_pool, fate_mapper


CHOICE_COPY = {
    '专注学业': {
        'short': '把半年交给专业训练',
        'title': '暂时收住外界诱惑，把半年交给学习、考试或作品积累',
        'decision': '你选择把时间投入一项能被检验的能力：课程、证书、作品集、考试或长期训练。',
    },
    '发展事业': {
        'short': '去更大的局里试一试',
        'title': '进入更明确的职业战场，争取项目、岗位或可见履历',
        'decision': '你选择把自己推到真实交付面前，用职位、项目、客户或作品证明能力。',
    },
    '经营感情': {
        'short': '认真经营一段关系',
        'title': '不再只等关系自然发展，主动处理亲密、承诺和边界',
        'decision': '你选择把精力交给亲密关系：沟通需求、确认边界，或让一段关系进入更真实的阶段。',
    },
    '陪伴家人': {
        'short': '回到家人身边',
        'title': '把时间留给家人，修补旧模式或承担现实照护',
        'decision': '你选择回应家庭里的需要：陪伴、照护、和解，或重新划定自己与家人的边界。',
    },
    '投资理财': {
        'short': '重算钱和风险',
        'title': '把安全感落到现金流、资产和风险承受力上',
        'decision': '你选择认真处理钱：储蓄、投资、买房、副业、债务或未来的安全垫。',
    },
    '调养身体': {
        'short': '先把身体养回来',
        'title': '承认身体不是无限资源，主动修复作息、健康和压力',
        'decision': '你选择把身体放回优先级：睡眠、运动、治疗、体检，或减少长期透支。',
    },
    '社交拓展': {
        'short': '进入新的关系场',
        'title': '走进新的圈层、合作和信息流，寻找贵人与机会',
        'decision': '你选择主动接触人：参加活动、合作表达、维护旧识，或让自己被新的圈层看见。',
    },
    '创业冒险': {
        'short': '赌一次主动权',
        'title': '用稳定感交换主动权，尝试创业、合伙或高波动机会',
        'decision': '你选择把想法推向现实成本：产品、客户、现金流、合伙关系和不确定性。',
    },
    '搬迁远行': {
        'short': '换一个坐标生活',
        'title': '离开熟悉环境，去新的城市、学校、岗位或远方寻找答案',
        'decision': '你选择改变地理坐标：搬迁、远行、异地机会，或让环境替你打破旧惯性。',
    },
    '随缘而行': {
        'short': '留白观察局势',
        'title': '不急着下注，给自己一个观察、恢复和顺势转弯的半年',
        'decision': '你选择不把人生塞满目标，而是降低噪音，观察局势，等待更清楚的信号。',
    },
}


def _string_list(value: Any, fallback: list[str] | None = None, limit: int = 12) -> list[str]:

    if not isinstance(value, list):

        return list(fallback or [])

    result = [str(item).strip() for item in value if str(item).strip()]

    return result[:limit] or list(fallback or [])

def action_goal_alignment(session: dict[str, Any], action: str) -> dict[str, Any]:

    from . import half_year_resolution

    progress = session.get('goal_progress') or {}

    goal = half_year_resolution.active_life_goal(session) if session.get('life_state') else {}

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


def _chart_hint(session: dict[str, Any], action: str) -> str:
    chart = session.get('bazi_chart') or {}
    tags = _string_list(session.get('chart_tags'), [], 4)
    day_master = str(chart.get('day_master') or '')
    useful = _string_list(chart.get('useful_elements'), [], 3)
    profile = fate_mapper.ACTION_PROFILES.get(action, fate_mapper.ACTION_PROFILES['随缘而行'])
    base = '命盘关键词' + ('“' + '、'.join(tags) + '”' if tags else '尚未完全显影')
    if day_master:
        base = '你以' + day_master + '为日主，' + base
    if useful:
        base += '，喜' + '、'.join(useful)
    return base + '；这会让“' + str(profile.get('primary') or '这个方向') + '”更像一种人生底色，而不是单次加分。'


def _fortune_hint(session: dict[str, Any]) -> str:
    luck = session.get('current_luck_cycle') or {}
    annual = session.get('current_annual_cycle') or {}
    months = session.get('current_monthly_cycles') or []
    parts = []
    if luck.get('pillar'):
        themes = _string_list(luck.get('theme'), [], 2)
        parts.append('大运' + str(luck.get('pillar')) + ('偏向' + '、'.join(themes) if themes else '提供长期背景'))
    if annual.get('pillar'):
        events = _string_list(annual.get('events'), [], 2)
        parts.append('流年' + str(annual.get('pillar')) + ('牵动' + '、'.join(events) if events else '带来年度转折'))
    opportunities = []
    risks = []
    for month in months:
        opportunities.extend(_string_list(month.get('opportunity'), [], 2))
        risks.extend(_string_list(month.get('risk'), [], 2))
    if opportunities:
        parts.append('本半年机会在' + '、'.join(dict.fromkeys(opportunities).keys())[:36])
    if risks:
        parts.append('风险在' + '、'.join(dict.fromkeys(risks).keys())[:36])
    return '；'.join(parts) + '。' if parts else '本半年时运信息不足，选择会更多依赖当前状态和过往惯性。'


def build_life_choice(session: dict[str, Any], action: str, stage: dict[str, Any]) -> dict[str, str]:
    copy = CHOICE_COPY.get(action, CHOICE_COPY['随缘而行'])
    stage_label = str(stage.get('label') or '当前阶段')
    stage_summary = str(stage.get('summary') or '人生处在新的岔口。')
    alignment = action_goal_alignment(session, action)
    profile = fate_mapper.ACTION_PROFILES.get(action, fate_mapper.ACTION_PROFILES['随缘而行'])
    impact = (
        '主要推向“' + str(profile.get('primary') or '人生经验') + '”，也会牵动“' +
        str(profile.get('secondary') or '长期状态') + '”；代价多半落在“' +
        str(profile.get('risk') or '机会成本') + '”。' + str(alignment.get('reason') or '')
    )
    return {
        'short_label': copy['short'],
        'title': copy['title'],
        'situation': stage_label + '：' + stage_summary,
        'decision': copy['decision'],
        'bazi_hint': _chart_hint(session, action),
        'fortune_hint': _fortune_hint(session),
        'choice_impact': impact,
    }


def build_event_preview(session: dict[str, Any], action: str, stage: dict[str, Any], age: int) -> dict[str, Any]:
    """Preview the bazi-weighted event tendency without committing a turn."""
    from . import half_year_resolution

    half = int(session.get('current_half') or 1)
    context = half_year_resolution._event_context(
        session,
        session.get('current_luck_cycle') or {},
        session.get('current_annual_cycle') or {},
    )
    preview = event_pool.pick_stage_event(
        str(session.get('player_id') or 'guest'),
        age,
        half,
        action,
        '成功',
        stage,
        context,
    )
    return {
        'title': preview.get('title') or '',
        'event_id': preview.get('event_id') or '',
        'life_domains': list(preview.get('life_domains') or [])[:5],
        'elements': list(preview.get('elements') or [])[:5],
        'ten_gods': list(preview.get('ten_gods') or [])[:5],
        'bazi_event_influence': preview.get('bazi_event_influence') or '',
        'clue': preview.get('clue') or '',
    }


def build_decision_support(session: dict[str, Any], action_summaries: dict[str, str] | None = None) -> list[dict[str, Any]]:

    """Build the advisory action-guide artifact without mutating authoritative records."""

    from . import half_year_resolution

    age = session.get('current_age') if session.get('current_age') is not None else session.get('start_age')

    if age is None:

        return []

    guides = []

    state = session.get('life_state') or {}

    stage = half_year_resolution.age_stage(int(age))

    for action in half_year_resolution.stage_action_options(int(age)):

        profile = fate_mapper.ACTION_PROFILES.get(action, fate_mapper.ACTION_PROFILES['随缘而行'])

        target, modifiers = fate_mapper.compute_roll_target(session, action)

        predicted_count = 1

        memory = half_year_resolution.normalize_focus_memory(session.get('focus_memory'))

        if str(memory.get('last_focus') or '') == action:

            predicted_count = int(memory.get('streak') or 0) + 1

        streak_bonus = half_year_resolution.focus_streak_roll_bonus(predicted_count)

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

            'life_choice': build_life_choice(session, action, stage),

            'event_preview': build_event_preview(session, action, stage, int(age)),

        })

    guides.sort(key=lambda item: (int(item.get('goal_alignment', {}).get('score') or 0), int(item.get('streak_preview', {}).get('bonus') or 0), int(item.get('roll_target_preview') or 0)), reverse=True)

    return guides
