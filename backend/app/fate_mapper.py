from __future__ import annotations

from typing import Any


BASE_LIFE_STATE = {
    '健康': 70, '心智': 70, '情绪': 70, '学识': 50, '事业': 30, '财富': 20,
    '家庭': 50, '感情': 30, '社交': 40, '名望': 10, '福德': 0, '压力': 20,
}

ACTION_PROFILES = {
    '专注学业': {'primary': '学识', 'secondary': '心智', 'risk': '压力', 'roll': '学业判定'},
    '发展事业': {'primary': '事业', 'secondary': '财富', 'risk': '压力', 'roll': '事业判定'},
    '经营感情': {'primary': '感情', 'secondary': '情绪', 'risk': '压力', 'roll': '感情判定'},
    '陪伴家人': {'primary': '家庭', 'secondary': '情绪', 'risk': '事业', 'roll': '家庭判定'},
    '投资理财': {'primary': '财富', 'secondary': '名望', 'risk': '压力', 'roll': '财富判定'},
    '调养身体': {'primary': '健康', 'secondary': '心智', 'risk': '财富', 'roll': '健康判定'},
    '社交拓展': {'primary': '社交', 'secondary': '事业', 'risk': '情绪', 'roll': '社交判定'},
    '创业冒险': {'primary': '事业', 'secondary': '名望', 'risk': '财富', 'roll': '创业判定'},
    '搬迁远行': {'primary': '社交', 'secondary': '心智', 'risk': '家庭', 'roll': '迁移判定'},
    '随缘而行': {'primary': '福德', 'secondary': '情绪', 'risk': '事业', 'roll': '机缘判定'},
}

ACTION_KEYWORDS = {
    '专注学业': ['学', '考试', '考研', '读书', '课程', '技能', '证书', '研究', '论文', '培训'],
    '发展事业': ['工作', '事业', '职场', '升职', '职位', '项目', '跳槽', '老板', '绩效', '专业'],
    '经营感情': ['感情', '恋爱', '伴侣', '对象', '婚', '约会', '亲密', '表白', '分手', '关系'],
    '陪伴家人': ['家庭', '父母', '孩子', '亲人', '家人', '陪伴', '照顾', '亲子', '回家'],
    '投资理财': ['投资', '理财', '股票', '基金', '买房', '资产', '存钱', '赚钱', '副业', '财务'],
    '调养身体': ['健康', '身体', '运动', '休息', '睡眠', '体检', '治疗', '养生', '减压', '康复'],
    '社交拓展': ['社交', '朋友', '人脉', '合作', '贵人', '聚会', '圈子', '沟通', '团队'],
    '创业冒险': ['创业', '冒险', '公司', '合伙', '融资', '辞职', '开店', '产品', '市场'],
    '搬迁远行': ['搬家', '迁移', '远行', '旅行', '出国', '城市', '异地', '留学', '调动'],
}


def clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(value)))


def infer_action_from_text(action_text: str) -> str:
    text = str(action_text or '').strip()
    if text in ACTION_PROFILES:
        return text
    if not text:
        return '随缘而行'
    for action, keywords in ACTION_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return action
    return '随缘而行'


def find_luck_cycle(session: dict[str, Any], age: int) -> dict[str, Any]:
    for cycle in session.get('luck_cycles', []):
        if 'age_start_months' in cycle and 'age_end_months' in cycle:
            age_months = int(age) * 12
            if int(cycle.get('age_start_months') or 0) <= age_months <= int(cycle.get('age_end_months') or 0):
                return cycle
            continue
        if cycle.get('age_start', 0) <= age <= cycle.get('age_end', 0):
            return cycle
    cycles = session.get('luck_cycles') or []
    return cycles[-1] if cycles else {}


def find_annual_cycle(session: dict[str, Any], age: int) -> dict[str, Any]:
    for cycle in session.get('annual_cycles', []):
        if cycle.get('age') == age:
            return cycle
    return {}


def half_label(half: int | str | None) -> str:
    return '下半年' if int(half or 1) == 2 else '上半年'


def find_monthly_cycles(session: dict[str, Any], age: int, half: int | str | None) -> list[dict[str, Any]]:
    selected_half = int(half or 1)
    return [
        cycle for cycle in session.get('monthly_cycles', [])
        if int(cycle.get('age') or -1) == int(age) and int(cycle.get('half') or 0) == selected_half
    ]


def build_initial_life_state(chart_data: dict[str, Any], start_age: int) -> dict[str, int]:
    state = BASE_LIFE_STATE.copy()
    chart = chart_data.get('bazi_chart', {})
    counts = chart.get('five_elements', {})
    useful = chart.get('useful_elements', [])

    element_bonus = {'木': '学识', '火': '名望', '土': '家庭', '金': '事业', '水': '心智'}
    for element in useful:
        key = element_bonus.get(element)
        if key:
            state[key] += 8
    state['健康'] += (counts.get('wood', 0) + counts.get('water', 0)) * 2
    state['财富'] += counts.get('metal', 0) * 3 + max(0, start_age - 20) // 2
    state['事业'] += max(0, start_age - 18)
    state['感情'] += max(0, start_age - 16) // 2
    state['压力'] += max(0, start_age - 22) // 2
    if chart.get('mode') == '三柱模式':
        state['心智'] -= 4
        state['情绪'] -= 3
    return {key: clamp(value) for key, value in state.items()}


def generate_prelude(chart_data: dict[str, Any], start_age: int) -> dict[str, Any]:
    chart = chart_data.get('bazi_chart', {})
    tags = chart_data.get('tags', [])
    state = build_initial_life_state(chart_data, start_age)
    personality = ['自省', '遇压成长']
    if '偏强' in chart.get('day_strength', ''):
        personality.append('主见强')
    elif '偏弱' in chart.get('day_strength', ''):
        personality.append('敏感谨慎')
    else:
        personality.append('能屈能伸')

    early_events = [
        '0-3岁：你对照料者的情绪和家庭气氛很敏感，哭闹、安静或黏人的反应背后，是在确认这个世界是否可靠。',
        '3-6岁：你开始形成自己的喜好和边界。一次被表扬、被忽略或被误解的经历，让你学会用某种方式争取关注。',
        '5-6岁：入学前后的规则、同伴和作息变化，让你第一次意识到自己不只属于家庭，也要在更大的环境里寻找位置。',
        '6岁开局前夕：你已经能感受到“被期待”和“想按自己方式来”之间的差别。家庭的照顾、身体的舒适度、启蒙老师或同伴的一句话，都会成为你正式踏入人生模拟时的最初性格底稿。',
    ]
    if start_age >= 8:
        early_events.append('6-8岁：进入更稳定的学习环境后，你逐渐发现自己在规则、兴趣和同伴关系中的位置，学会比较，也开始在意输赢。')
    if start_age >= 12:
        early_events.append('9-12岁：学业、兴趣或亲子关系出现一次明显转折。你第一次意识到，努力不只是为了被肯定，也是在为未来的选择攒筹码。')
    if start_age >= 16:
        early_events.append('13-16岁：青春期让情绪、友谊和自我认同同时变得尖锐。你在一次冲突或分离中，学会把真实想法藏起来，或开始主动表达。')
    if start_age >= 18:
        early_events.append('17-18岁：升学、离家或方向选择让你第一次接近成年世界。你看见家庭期待与个人愿望之间的缝隙，也开始承担选择的后果。')
    if start_age >= 22:
        early_events.append('19-22岁：你在专业、城市、人际圈或第一段重要关系中重新定位自己，既得到新的自由，也留下关于金钱、亲密或成就的焦虑。')
    if start_age >= 30:
        early_events.append('23-30岁：你逐渐明白稳定并不等于安心。工作、感情、家庭责任和自我实现互相拉扯，塑造了你进入正式模拟时的资源与包袱。')
    if start_age >= 40:
        early_events.append('30岁以后：你已经积累了若干身份、资产或关系承诺，也经历过错过、妥协与重新开始。真正困住你的，往往不是命盘，而是惯性。')
    text = (
        '你的命盘关键词为：' + '、'.join(tags) + '。从出生到' + str(start_age) +
        '岁，命盘提供的是底色而不是结论：它让你更早感受到某些吸引、压力和反复出现的课题。' +
        '你的早年不是单线成长，而是在家庭安全感、身体状态、学习反馈、人际评价和自我期待之间逐渐成形。' +
        '家庭里谁更严格、谁更温柔，身体在季节变化时是否容易疲惫，启蒙阶段得到的是鼓励还是比较，都会改变你面对世界时的第一反应。' +
        '你也逐渐形成一套保护自己的方式：有时靠观察和沉默避免冲突，有时靠表现和努力换取认可，有时则会在亲近关系里反复确认自己是否被稳定地接住。' +
        '有些优势已经沉入习惯，例如长期积累、观察局势或在变化中寻找机会；也有些弱点仍会在关键选择时出现，例如压力过高时失衡、关系经营不够主动，或在应该争取时先退一步。' +
        '正式人生开始时，你带着这些既定经历进入新的半年选择：过去会影响你，但不会替你完成接下来的决定。'
    )
    return {'text': text, 'personality': personality, 'life_state': state, 'early_events': early_events, 'hidden_strengths': ['长期积累能力', '在变化中寻找机会'], 'hidden_weaknesses': ['压力过高时容易失衡', '关系经营需要主动投入']}


def compute_roll_target(session: dict[str, Any], action: str) -> tuple[int, dict[str, int]]:
    profile = ACTION_PROFILES.get(action, ACTION_PROFILES['随缘而行'])
    life_state = session.get('life_state', {})
    age = int(session.get('current_age', session.get('start_age', 22)))
    luck = find_luck_cycle(session, age)
    annual = find_annual_cycle(session, age)
    modifiers = {'基础': 55}
    modifiers['属性积累'] = (int(life_state.get(profile['primary'], 50)) - 50) // 3
    modifiers['心智支撑'] = (int(life_state.get('心智', 50)) - 50) // 5
    modifiers['健康压力'] = -10 if int(life_state.get('健康', 70)) < 40 else 0
    modifiers['压力负担'] = -15 if int(life_state.get('压力', 20)) > 80 else -5 if int(life_state.get('压力', 20)) > 60 else 0
    modifiers['大运'] = int((luck.get('modifiers') or {}).get(profile['roll'], 0)) + int((luck.get('modifiers') or {}).get('事业判定', 0) if '事业' in profile['roll'] else 0)
    modifiers['流年'] = 8 if annual.get('opportunity') else -4 if annual.get('risk') else 0
    monthly_cycles = session.get('current_monthly_cycles') or find_monthly_cycles(session, age, session.get('current_half') or 1)
    month_score = 0
    for cycle in monthly_cycles:
        cycle_modifiers = cycle.get('modifiers') or {}
        month_score += int(cycle_modifiers.get(profile['roll'], 0))
        month_score -= 1 if int(cycle_modifiers.get('压力', 0)) >= 3 else 0
    modifiers['流月'] = clamp(month_score, -10, 10)
    target = clamp(sum(modifiers.values()), 20, 95)
    return target, modifiers


def apply_annual_result(session: dict[str, Any], action: str, outcome: str) -> dict[str, int]:
    profile = ACTION_PROFILES.get(action, ACTION_PROFILES['随缘而行'])
    delta_by_outcome = {'大成功': (12, 7, -8), '成功': (7, 3, -3), '失败': (-2, 1, 8), '大失败': (-8, -3, 15)}
    primary_delta, secondary_delta, pressure_delta = delta_by_outcome.get(outcome, delta_by_outcome['失败'])
    changes = {profile['primary']: primary_delta, profile['secondary']: secondary_delta, '压力': pressure_delta}
    if outcome in ['失败', '大失败']:
        changes[profile['risk']] = changes.get(profile['risk'], 0) - (4 if outcome == '失败' else 9)
    if action == '调养身体':
        changes['压力'] -= 6
    if action == '创业冒险':
        changes['压力'] += 6
    return changes


def scale_changes(changes: dict[str, int], factor: float = 0.58) -> dict[str, int]:
    scaled = {}
    for key, value in changes.items():
        if value == 0:
            continue
        adjusted = int(round(value * factor))
        if adjusted == 0:
            adjusted = 1 if value > 0 else -1
        scaled[key] = adjusted
    return scaled


def apply_changes(life_state: dict[str, int], changes: dict[str, int]) -> dict[str, int]:
    updated = life_state.copy()
    for key, delta in changes.items():
        if key in updated:
            updated[key] = clamp(updated[key] + int(delta))
    return updated
