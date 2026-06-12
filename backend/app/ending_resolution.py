from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import fate_mapper, half_year_resolution, life_session

def format_goal_progress(progress: dict[str, Any]) -> str:
    if not progress:
        return '人生愿望尚未确定。'
    return (
        '人生愿望“' + str(progress.get('title') or '') + '”当前为' +
        str(progress.get('score') or 0) + '/' + str(progress.get('threshold') or 0) +
        '，进度' + str(progress.get('percent') or 0) + '%，状态为' + str(progress.get('status') or '未知') + '。'
    )

def ending_dimension(label: str, value: int) -> dict[str, Any]:
    score = fate_mapper.clamp(value)
    if score >= 85:
        grade = '圆满'
        comment = label + '成为这一生最稳的成果之一。'
    elif score >= 70:
        grade = '丰厚'
        comment = label + '有清晰积累，也留下继续经营的空间。'
    elif score >= 50:
        grade = '平衡'
        comment = label + '没有完全失守，但也谈不上无憾。'
    elif score >= 30:
        grade = '亏欠'
        comment = label + '长期受到挤压，成为回望时绕不开的遗憾。'
    else:
        grade = '断裂'
        comment = label + '在多次取舍中被严重透支。'
    return {'label': label, 'score': score, 'grade': grade, 'comment': comment}

def ending_turning_points(session: dict[str, Any]) -> list[str]:
    candidates = []
    for item in session.get('annual_summaries') or []:
        roll = item.get('roll_event') or {}
        changes = item.get('state_effect') or {}
        change_score = sum(abs(int(value)) for value in changes.values() if isinstance(value, int))
        outcome = str(roll.get('outcome') or '')
        weight = change_score + (12 if outcome in ['大成功', '大失败'] else 5 if outcome in ['成功', '失败'] else 0)
        candidates.append((weight, item))
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    points = []
    for _, item in candidates[:6]:
        stage_event = item.get('stage_event') or {}
        roll = item.get('roll_event') or {}
        points.append(
            str(item.get('age')) + '岁' + str(item.get('half_label') or '') +
            '，' + str(item.get('main_focus') or '随缘而行') +
            '，' + str(roll.get('outcome') or '未知结果') +
            '：' + str(stage_event.get('event') or item.get('summary') or '')[:64]
        )
    return points

def ending_achievements_and_regrets(state: dict[str, Any]) -> tuple[list[str], list[str]]:
    achievements = []
    regrets = []
    achievement_rules = [
        ('事业', '把事业经营成可被看见的成果'),
        ('财富', '为自己和家人留下较稳定的物质余量'),
        ('家庭', '在家庭责任里保留了温度和连接'),
        ('感情', '学会经营亲密关系中的表达与承诺'),
        ('健康', '守住身体底盘，没有让透支吞掉全部选择'),
        ('名望', '留下被他人记住的作品、信誉或影响力'),
        ('福德', '在顺逆之间保留了善意、弹性和转机'),
    ]
    regret_rules = [
        ('事业', '事业路线仍有未竟之处'),
        ('财富', '资产安全感不够稳固'),
        ('家庭', '家庭陪伴或照护留下亏欠'),
        ('感情', '亲密关系仍有未说出口的遗憾'),
        ('健康', '健康被长期压力消耗过多'),
        ('情绪', '情绪稳定性多次影响重要关系'),
    ]
    for key, text in achievement_rules:
        if int(state.get(key, 0)) >= 75:
            achievements.append(text)
    for key, text in regret_rules:
        if int(state.get(key, 100)) <= 40:
            regrets.append(text)
    if int(state.get('压力', 0)) >= 75:
        regrets.append('压力长期偏高，许多选择带着硬撑的痕迹')
    return achievements[:6] or ['在反复选择中保留了继续修正人生的能力'], regrets[:6] or ['没有单一遗憾压倒整个人生，但仍有一些未完成的愿望']

def hidden_ending_candidates(session: dict[str, Any], state: dict[str, Any], goal_progress: dict[str, Any]) -> list[dict[str, Any]]:
    def score(key: str) -> int:
        return int(state.get(key, 0))

    candidates: list[dict[str, Any]] = []
    goal_id = str(goal_progress.get('goal_id') or session.get('active_life_goal_id') or '')
    goal_achieved = bool(goal_progress.get('achieved'))
    achievement_count = len(session.get('achievements') or [])

    def add(ending_id: str, title: str, rarity: str, condition: bool, description: str, unlock_reason: str, priority: int) -> None:
        if not condition:
            return
        candidates.append({
            'id': ending_id,
            'title': title,
            'rarity': rarity,
            'description': description,
            'unlock_reason': unlock_reason,
            'priority': priority,
        })

    add(
        'cloud_road_legacy',
        '云路留名之命',
        '稀有',
        score('事业') + score('名望') >= 165 and score('学识') >= 70,
        '你把长期学习、专业交付和公开信誉连成一条路，最终留下可被他人引用或追随的名字。',
        '事业与名望合计达到 165，且学识不低于 70。',
        90,
    )
    add(
        'warm_hearth',
        '灯火可亲之一生',
        '稀有',
        score('家庭') + score('感情') >= 165 and score('压力') <= 60,
        '你没有把圆满只押在外部成就上，而是在亲密关系与家庭责任里留下了可回去的灯火。',
        '家庭与感情合计达到 165，且压力不高于 60。',
        86,
    )
    add(
        'hidden_gold',
        '厚土藏金之局',
        '稀有',
        score('财富') >= 88 and score('健康') >= 60 and score('压力') <= 55,
        '你守住身体和节奏，也把资产基础慢慢夯实，富足不是骤得，而是长期稳住的结果。',
        '财富达到 88，同时健康不低于 60、压力不高于 55。',
        82,
    )
    add(
        'quiet_merit',
        '无名有福之人',
        '隐藏',
        score('福德') >= 80 and score('名望') <= 60 and score('家庭') >= 60,
        '你未必站在众人目光中央，却在一次次善意、照护和留白里积下了柔软的转机。',
        '福德达到 80，名望不高于 60，且家庭不低于 60。',
        88,
    )
    add(
        'solitary_peak',
        '孤峰照雪之命',
        '隐藏',
        score('事业') + score('名望') >= 170 and score('家庭') + score('感情') <= 95,
        '你抵达了高处，也清楚高处的风会带走一些陪伴；这不是单纯胜利，而是一种有代价的成就。',
        '事业与名望合计达到 170，但家庭与感情合计不高于 95。',
        91,
    )
    add(
        'free_roamer',
        '万里随心之途',
        '隐藏',
        (goal_id == 'free_explorer' and goal_achieved) or (score('社交') + score('心智') >= 150 and score('压力') <= 50 and score('财富') >= 45),
        '你没有把人生压缩成单一答案，而是在关系、见闻和自我节奏之间，活出可进可退的自由。',
        '达成“自由探索”愿望，或社交与心智合计达到 150、压力不高于 50、财富不低于 45。',
        84,
    )
    add(
        'many_paths_master',
        '千途自明之卷',
        '传奇',
        achievement_count >= 8 and goal_achieved and half_year_resolution.average_state(state, ['心智', '情绪', '健康'], 0) >= 70,
        '你不是只赢下一条线，而是在愿望、身体、心智和多次过程反馈之间，把人生经营成完整的卷轴。',
        '解锁至少 8 项成就、人生愿望达成，且心智/情绪/健康平均不低于 70。',
        100,
    )
    candidates.sort(key=lambda item: int(item.get('priority', 0)), reverse=True)
    return candidates[:3]

def build_ending(session: dict[str, Any]) -> dict[str, Any]:
    state = session.get('life_state', {})
    goal_progress = half_year_resolution.refresh_goal_progress(session) if state else {}
    reason = str(session.get('ending_reason') or '')
    dimensions = {
        '事业': ending_dimension('事业', int(state.get('事业', 0))),
        '财富': ending_dimension('财富', int(state.get('财富', 0))),
        '家庭': ending_dimension('家庭', int(state.get('家庭', 0))),
        '感情': ending_dimension('感情', int(state.get('感情', 0))),
        '健康': ending_dimension('健康', int(state.get('健康', 0))),
        '精神': ending_dimension('精神', half_year_resolution.average_state(state, ['心智', '情绪', '福德'])),
        '名望': ending_dimension('名望', int(state.get('名望', 0))),
    }
    achievements, regrets = ending_achievements_and_regrets(state)
    turning_points = ending_turning_points(session)
    systems = session.get('life_systems') or {}
    hidden_endings = hidden_ending_candidates(session, state, goal_progress)
    primary_hidden = hidden_endings[0] if hidden_endings and reason != 'health_zero' else {}
    if int(state.get('健康', 0)) <= 0:
        title = '命途早折之局'
    elif primary_hidden:
        title = str(primary_hidden.get('title') or '隐藏结局')
    elif int(state.get('事业', 0)) + int(state.get('名望', 0)) >= 150:
        title = '高处见山之一生'
    elif int(state.get('财富', 0)) >= 85:
        title = '富足守成之命'
    elif int(state.get('家庭', 0)) + int(state.get('感情', 0)) >= 150:
        title = '烟火圆满之一生'
    elif dimensions['精神']['score'] >= 75:
        title = '心有所安之一生'
    else:
        title = '一生多变，晚景自明'
    reason_line = {
        'retrospect': '这是你主动选择停下脚步、回望当下人生时生成的档案；它不是失败，而是本周目在此刻的定格。',
        'health_zero': '这一生因健康归零而提前收束，身体底盘成为最终结局里最沉重的注脚。',
        'age_60': '这一生已走到六十岁节点，命书按照当前积累生成阶段性终章。',
    }.get(reason, '')
    dimension_line = '、'.join(label + str(item['score']) + '分（' + item['grade'] + '）' for label, item in dimensions.items())
    system_line = '；'.join(str(item.get('label')) + '：' + str(item.get('stage')) for item in systems.values()) if isinstance(systems, dict) else ''
    summary = (
        (reason_line + ' ' if reason_line else '') +
        '回望这一生，你最终留下的状态是：' + dimension_line + '。' +
        '命盘给了底色，大运、流年和流月给了每个阶段的风向，但真正留下痕迹的是你在半年又半年里反复选择、承担后果、修补关系和重新分配精力的方式。' +
        ('长期系统收束为：' + system_line + '。' if system_line else '') +
        (format_goal_progress(goal_progress) + ('这个愿望最终达成。' if goal_progress.get('achieved') else '这个愿望尚未完全达成。') if goal_progress else '') +
        ('一生共解锁' + str(len(session.get('achievements') or [])) + '项成就。' if session.get('achievements') else '') +
        (('隐藏结局“' + str(primary_hidden.get('title')) + '”已点亮：' + str(primary_hidden.get('description')) + '。') if primary_hidden else '') +
        '主要成就：' + '；'.join(achievements) + '。' +
        '主要遗憾：' + '；'.join(regrets) + '。' +
        ('关键转折包括：' + '；'.join(turning_points[:4]) + '。' if turning_points else '') +
        '如果重来一次，命盘仍会给出相似的底色，但不同的长期投入、关系选择和风险节奏，仍可能把这一生命名为另一种结局。'
    )
    return {
        'title': title,
        'reason': reason or 'natural',
        'summary': summary,
        'final_state': state,
        'dimensions': dimensions,
        'achievements': achievements,
        'regrets': regrets,
        'key_turning_points': turning_points,
        'life_systems': deepcopy(systems),
        'relationships': deepcopy(session.get('relationships') or []),
        'life_goal': deepcopy(goal_progress),
        'life_goal_achieved': bool(goal_progress.get('achieved')),
        'hidden_ending': deepcopy(primary_hidden),
        'hidden_endings': deepcopy(hidden_endings),
        'achievements_unlocked': deepcopy(session.get('achievements') or []),
        'milestones': deepcopy(session.get('milestones') or []),
    }

def finish_session(session: dict[str, Any], reason: str = 'natural') -> bool:
    if session.get('is_finished') and session.get('ending'):
        return True
    session['ending_reason'] = reason
    session['phase'] = 'ending'
    session['is_finished'] = True
    session['ending'] = build_ending(session)
    resolve_codex_delta(session)
    if reason == 'retrospect':
        prefix = '【回望一生：'
    else:
        prefix = '【结局：'
    session['display_history'].append(prefix + session['ending']['title'] + '】\n\n' + session['ending']['summary'])
    return True

def finish_if_needed(session: dict[str, Any]) -> bool:
    reason = half_year_resolution.finish_reason(session)
    return finish_session(session, reason) if reason else False

def ending_codex_unlock_id(ending: dict[str, Any]) -> str:
    hidden = ending.get('hidden_ending') if isinstance(ending.get('hidden_ending'), dict) else {}
    hidden_id = str(hidden.get('id') or '')
    if hidden_id in life_session.ENDING_CODEX_BY_ID:
        return hidden_id
    return life_session.ENDING_CODEX_ID_BY_TITLE.get(str(ending.get('title') or ''), 'many_changes')

def resolve_codex_delta(session: dict[str, Any]) -> list[dict[str, Any]]:
    ending = session.get('ending') if isinstance(session.get('ending'), dict) else {}
    if not ending:
        return []
    codex = life_session.normalize_ending_codex(session.get('ending_codex'))
    unlock_id = ending_codex_unlock_id(ending)
    new_unlocks = []
    for entry in codex['entries']:
        if entry['id'] != unlock_id:
            continue
        was_unlocked = bool(entry.get('unlocked'))
        entry['unlocked'] = True
        entry['unlock_count'] = int(entry.get('unlock_count') or 0) + 1
        entry['unlocked_at'] = entry.get('unlocked_at') or (str(session.get('current_age') or '') + '岁' + str(session.get('current_half_label') or ''))
        entry['last_reason'] = str(ending.get('reason') or session.get('ending_reason') or '')
        entry['last_age'] = session.get('current_age')
        if not was_unlocked:
            new_unlocks.append(deepcopy(entry))
        break
    codex = life_session.normalize_ending_codex({'entries': codex['entries'], 'latest_unlocks': new_unlocks})
    session['ending_codex'] = codex
    ending['codex_unlocks'] = deepcopy(new_unlocks)
    ending['codex_progress'] = {'unlocked_count': codex['unlocked_count'], 'total_count': codex['total_count']}
    return new_unlocks
