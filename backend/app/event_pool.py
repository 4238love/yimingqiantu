from __future__ import annotations

from typing import Any


ACTION_META = {
    '专注学业': {'id': 'study', 'primary': '学识', 'tags': ['积累', '学习'], 'clue': '长期学习会在后续职业与名望判定里留下伏笔。'},
    '发展事业': {'id': 'career', 'primary': '事业', 'tags': ['职场', '责任'], 'clue': '事业推进越稳定，越容易触发长期系统里的职业上升。'},
    '经营感情': {'id': 'romance', 'primary': '感情', 'tags': ['亲密', '边界'], 'clue': '亲密关系会影响情绪、家庭与部分隐藏结局。'},
    '陪伴家人': {'id': 'family', 'primary': '家庭', 'tags': ['家庭', '照护'], 'clue': '家庭线会改变安全感，也会拉动责任与事业之间的取舍。'},
    '投资理财': {'id': 'wealth', 'primary': '财富', 'tags': ['资产', '风险'], 'clue': '财富线不是只看收益，也会记录风险承受力和现金余量。'},
    '调养身体': {'id': 'health', 'primary': '健康', 'tags': ['身体', '修复'], 'clue': '健康是提前终局的底线，也是高压路线的承载力。'},
    '社交拓展': {'id': 'network', 'primary': '社交', 'tags': ['人脉', '合作'], 'clue': '社交线会把信息差、贵人和关系消耗同时带进后续回合。'},
    '创业冒险': {'id': 'venture', 'primary': '事业', 'tags': ['创业', '波动'], 'clue': '创业会放大成功收益，也会放大财富、健康和关系成本。'},
    '搬迁远行': {'id': 'move', 'primary': '社交', 'tags': ['迁移', '视野'], 'clue': '迁移会改变机会半径，也会改变原有支持系统。'},
    '随缘而行': {'id': 'flow', 'primary': '福德', 'tags': ['留白', '机缘'], 'clue': '留白能恢复弹性，但长期交出主动权会留下另一种代价。'},
}

STAGE_FLAVORS = {
    'childhood': {'label': '童年启蒙', 'texture': '课堂、饭桌、操场和熟悉大人的目光', 'anchor': '启蒙习惯', 'tags': ['童年']},
    'adolescence': {'label': '少年转折', 'texture': '考试、同伴比较、亲子边界和自我认同', 'anchor': '青春期压力', 'tags': ['少年']},
    'early_adult': {'label': '成年起步', 'texture': '专业选择、城市入口、第一份责任和独立生活', 'anchor': '成年入口', 'tags': ['起步']},
    'building': {'label': '立业成家', 'texture': '职位、伴侣、资产起步和家庭责任交错', 'anchor': '成家立业', 'tags': ['立业']},
    'midlife': {'label': '中年经营', 'texture': '转型、现金流、健康警讯和照护责任', 'anchor': '结构性取舍', 'tags': ['中年']},
    'late_life': {'label': '后半生收束', 'texture': '经验传承、身体余量、资产安全和关系和解', 'anchor': '晚年整理', 'tags': ['后半生']},
}

ACTION_EVENT_TEMPLATES = {
    '专注学业': [
        {'title': '旧题重做', 'event': '围绕{anchor}，你把{texture}里的杂音暂时压低，反复训练一项能被检验的能力。', 'state_bias': {'学识': 1}, 'tags': ['复盘']},
        {'title': '师友点灯', 'event': '{texture}中出现一位愿意指出问题的人，你开始明白真正的学习不是被夸，而是能承受修正。', 'state_bias': {'学识': 1, '心智': 1}, 'tags': ['师友']},
        {'title': '沉默积累', 'event': '这个半年没有立刻显眼的成果，但你在{anchor}上留下了稳定记录，未来会反复调用这段底气。', 'state_bias': {'学识': 1, '压力': 1}, 'tags': ['长期']},
    ],
    '发展事业': [
        {'title': '责任上桌', 'event': '一个更清晰的任务被推到你面前，{texture}让你意识到能力必须通过交付而不是想象来证明。', 'state_bias': {'事业': 1, '压力': 1}, 'tags': ['交付']},
        {'title': '规则入局', 'event': '你开始读懂组织、客户或行业的隐性规则，在{anchor}里学会把努力转化成可被认可的结果。', 'state_bias': {'事业': 1, '名望': 1}, 'tags': ['规则']},
        {'title': '台前一刻', 'event': '{texture}给了你一次被看见的窗口，也让你第一次认真计算可见度背后的代价。', 'state_bias': {'事业': 1, '压力': 1}, 'tags': ['曝光']},
    ],
    '经营感情': [
        {'title': '认真谈话', 'event': '一次绕不开的谈话让你把需求、害怕和边界说得更具体，{texture}里的温度因此改变。', 'state_bias': {'感情': 1, '情绪': 1}, 'tags': ['沟通']},
        {'title': '误会显影', 'event': '{anchor}让某个误会浮到台面，你不再只猜对方的心意，而是尝试确认彼此真正想要什么。', 'state_bias': {'感情': 1, '压力': 1}, 'tags': ['边界']},
        {'title': '承诺试金', 'event': '关系进入需要实际安排的阶段，{texture}提醒你：亲密不是情绪高涨，而是能不能共同承担细节。', 'state_bias': {'感情': 1, '家庭': 1}, 'tags': ['承诺']},
    ],
    '陪伴家人': [
        {'title': '饭桌回声', 'event': '你把时间交还给家人，在{texture}里听见一些过去被忽略的需求，也重新理解自己的责任。', 'state_bias': {'家庭': 1, '情绪': 1}, 'tags': ['陪伴']},
        {'title': '旧模式松动', 'event': '{anchor}触发了熟悉的家庭模式，但这次你试着不只顺从或逃开，而是重新分配边界。', 'state_bias': {'家庭': 1, '心智': 1}, 'tags': ['和解']},
        {'title': '照护成本', 'event': '家庭事务占据了具体时间，{texture}让你感到被需要，也让其他人生线暂时放慢。', 'state_bias': {'家庭': 1, '压力': 1}, 'tags': ['责任']},
    ],
    '投资理财': [
        {'title': '账本见底', 'event': '你把收入、支出和风险摊开重算，{texture}中的安全感第一次被具体数字衡量。', 'state_bias': {'财富': 1, '心智': 1}, 'tags': ['预算']},
        {'title': '机会诱惑', 'event': '{anchor}带来一个看似不错的财务机会，你开始区分真正的机会、跟风的兴奋和恐惧驱动的决定。', 'state_bias': {'财富': 1, '压力': 1}, 'tags': ['风险']},
        {'title': '延迟满足', 'event': '你放弃一部分即时消费，把资源挪向更长期的安排；{texture}因此多了一点可控的余量。', 'state_bias': {'财富': 1}, 'tags': ['纪律']},
    ],
    '调养身体': [
        {'title': '身体示警', 'event': '一次疲惫、病痛或体检结果让你停下来，{texture}提醒你底盘不是可以无限透支的资源。', 'state_bias': {'健康': 1, '压力': -1}, 'tags': ['修复']},
        {'title': '作息重排', 'event': '你把睡眠、饮食、运动或治疗重新排进日程，在{anchor}里用小而连续的动作修补承载力。', 'state_bias': {'健康': 1, '心智': 1}, 'tags': ['节律']},
        {'title': '慢下来', 'event': '{texture}里的噪音被你主动降下来，恢复不再被视为偷懒，而是下一阶段行动的前提。', 'state_bias': {'健康': 1, '情绪': 1}, 'tags': ['恢复']},
    ],
    '社交拓展': [
        {'title': '新圈入口', 'event': '一个活动、合作或旧识重逢让你进入新的信息流，{texture}因此出现了更多可能性。', 'state_bias': {'社交': 1, '事业': 1}, 'tags': ['人脉']},
        {'title': '边界筛选', 'event': '{anchor}让你发现有些关系只是热闹，有些关系能真正共事；你开始筛选而不是一味迎合。', 'state_bias': {'社交': 1, '心智': 1}, 'tags': ['筛选']},
        {'title': '公开表达', 'event': '你在{texture}中更主动地表达自己的价值，新的反馈带来资源，也带来被评价的压力。', 'state_bias': {'社交': 1, '压力': 1}, 'tags': ['表达']},
    ],
    '创业冒险': [
        {'title': '第一张草图', 'event': '一个想法被写成计划、产品或合伙邀约，{texture}让你从想象进入真实成本。', 'state_bias': {'事业': 1, '压力': 1}, 'tags': ['启动']},
        {'title': '现金流试炼', 'event': '{anchor}把热情拉回账面：客户、合同、交付和现金流开始决定这次冒险能走多远。', 'state_bias': {'名望': 1, '财富': -1, '压力': 1}, 'tags': ['现金流']},
        {'title': '主动权交换', 'event': '你用稳定感换取主动权，{texture}中的每个细节都可能放大成机会或漏洞。', 'state_bias': {'事业': 1, '健康': -1, '压力': 1}, 'tags': ['冒险']},
    ],
    '搬迁远行': [
        {'title': '行囊重整', 'event': '你开始整理证件、住处、路线或城市选择，{texture}被迫离开熟悉的惯性。', 'state_bias': {'社交': 1, '心智': 1}, 'tags': ['迁移']},
        {'title': '陌生坐标', 'event': '{anchor}把你放到新的坐标里，机会变得更近，孤独和成本也变得更具体。', 'state_bias': {'社交': 1, '家庭': -1}, 'tags': ['城市']},
        {'title': '视野扩容', 'event': '一次远行或环境切换让你看见原来生活的边界，{texture}因此出现新的解释方式。', 'state_bias': {'心智': 1, '福德': 1}, 'tags': ['视野']},
    ],
    '随缘而行': [
        {'title': '留白观察', 'event': '你没有强推目标，而是在{texture}里观察局势，给自己留出重新感受方向的空隙。', 'state_bias': {'福德': 1, '情绪': 1}, 'tags': ['留白']},
        {'title': '顺水转弯', 'event': '{anchor}没有给出明确答案，但一个偶然信号让你避开了过度用力的惯性。', 'state_bias': {'福德': 1, '压力': -1}, 'tags': ['机缘']},
        {'title': '慢半拍', 'event': '这个半年像是把速度降下来：{texture}仍在变化，你选择先修补消耗，再决定下一步。', 'state_bias': {'情绪': 1}, 'tags': ['恢复']},
    ],
}


def _render_template(stage_id: str, action: str, index: int, template: dict[str, Any]) -> dict[str, Any]:
    stage = STAGE_FLAVORS.get(stage_id, STAGE_FLAVORS['late_life'])
    meta = ACTION_META.get(action, ACTION_META['随缘而行'])
    title = str(template.get('title') or action)
    event = str(template.get('event') or '').format(
        stage=stage['label'],
        texture=stage['texture'],
        anchor=stage['anchor'],
        action=action,
    )
    tags = []
    for item in [stage_id, *stage.get('tags', []), *meta.get('tags', []), *template.get('tags', [])]:
        if item and item not in tags:
            tags.append(str(item))
    return {
        'id': f"{stage_id}_{meta['id']}_{index + 1}",
        'title': title,
        'event': event,
        'tags': tags,
        'state_bias': dict(template.get('state_bias') or {}),
        'clue': str(template.get('clue') or meta.get('clue') or ''),
    }


def _build_event_pool() -> dict[str, dict[str, list[dict[str, Any]]]]:
    pool: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for stage_id in STAGE_FLAVORS:
        pool[stage_id] = {}
        for action, templates in ACTION_EVENT_TEMPLATES.items():
            pool[stage_id][action] = [_render_template(stage_id, action, index, template) for index, template in enumerate(templates)]
    return pool


STAGE_EVENT_POOL = _build_event_pool()

FALLBACK_EVENT = {
    'id': 'fallback_flow_1',
    'title': '日常暗流',
    'event': '这个半年没有单一的大事，却在日常细节里改变了你的惯性。',
    'tags': ['fallback'],
    'state_bias': {},
    'clue': '看似平淡的半年也会进入长期历史。',
}


def pick_stage_event(player_id: str, age: int, half: int, action: str, outcome: str, stage: dict[str, Any]) -> dict[str, Any]:
    """Pick a deterministic structured event while preserving the old return shape."""
    stage_id = str(stage.get('id') or 'late_life')
    stage_pool = STAGE_EVENT_POOL.get(stage_id) or STAGE_EVENT_POOL.get('late_life') or {}
    options = stage_pool.get(action) or stage_pool.get('随缘而行') or [FALLBACK_EVENT]
    seed = str(player_id) + str(age) + str(half) + str(action) + str(outcome) + stage_id
    index = sum(ord(char) for char in seed) % len(options)
    selected = dict(options[index])
    if outcome in ['大成功', '成功']:
        result_note = '判定顺利让这件事成为可继续利用的经验。'
    else:
        result_note = '判定受阻让这件事留下需要后续修补的成本。'
    return {
        'stage_id': stage_id,
        'stage_label': stage.get('label') or STAGE_FLAVORS.get(stage_id, {}).get('label') or '',
        'stage_summary': stage.get('summary') or '',
        'stage_goals': list(stage.get('goals') or []),
        'event': selected.get('event') or FALLBACK_EVENT['event'],
        'result_note': result_note,
        'event_id': selected.get('id') or FALLBACK_EVENT['id'],
        'title': selected.get('title') or FALLBACK_EVENT['title'],
        'tags': list(selected.get('tags') or []),
        'state_bias': dict(selected.get('state_bias') or {}),
        'clue': selected.get('clue') or FALLBACK_EVENT['clue'],
    }
