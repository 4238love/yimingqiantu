from __future__ import annotations

from datetime import datetime
from typing import Any


HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
MONTH_BRANCHES = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
FLOW_MONTH_NAMES = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']

STEM_ELEMENTS = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
STEM_YIN_YANG = {'甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'}
BRANCH_ELEMENTS = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}
ELEMENT_KEYS = {'木': 'wood', '火': 'fire', '土': 'earth', '金': 'metal', '水': 'water'}
ELEMENT_LABELS = {v: k for k, v in ELEMENT_KEYS.items()}
GENERATES = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
CONTROLS = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
GENERATED_BY = {v: k for k, v in GENERATES.items()}
CONTROLLED_BY = {v: k for k, v in CONTROLS.items()}
YANG_STEMS = {'甲', '丙', '戊', '庚', '壬'}


def _pillar_from_index(index: int) -> str:
    return HEAVENLY_STEMS[index % 10] + EARTHLY_BRANCHES[index % 12]


def _pillar_index(pillar: str) -> int:
    for index in range(60):
        if _pillar_from_index(index) == pillar:
            return index
    raise ValueError('invalid pillar: ' + str(pillar))


def _parse_birth_datetime(birth_info: dict[str, Any]) -> tuple[datetime, bool]:
    birth_date = str(birth_info.get('birth_date') or birth_info.get('date') or '').strip()
    if not birth_date:
        raise ValueError('birth_date is required')
    unknown_time = bool(birth_info.get('unknown_time'))
    birth_time = str(birth_info.get('birth_time') or '').strip()
    if not birth_time:
        unknown_time = True
        birth_time = '12:00'
    year, month, day = [int(part) for part in birth_date.split('-')]
    time_parts = birth_time.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    return datetime(year, month, day, hour, minute), unknown_time


def _year_pillar(dt: datetime) -> str:
    year = dt.year - (1 if (dt.month, dt.day) < (2, 4) else 0)
    return _pillar_from_index(year - 4)


def _month_index(dt: datetime) -> int:
    boundaries = [(1, 6, 11), (2, 4, 0), (3, 6, 1), (4, 5, 2), (5, 6, 3), (6, 6, 4), (7, 7, 5), (8, 8, 6), (9, 8, 7), (10, 8, 8), (11, 7, 9), (12, 7, 10)]
    month_idx = 10
    for month, day, idx in boundaries:
        if (dt.month, dt.day) >= (month, day):
            month_idx = idx
    return month_idx


def _solar_term_boundaries(year: int) -> list[datetime]:
    # MVP approximate "节" boundaries used by the existing month-pillar model.
    # These are enough for gameplay and keep 大运起运 independent from game start age.
    boundaries = [(1, 6), (2, 4), (3, 6), (4, 5), (5, 6), (6, 6), (7, 7), (8, 8), (9, 8), (10, 8), (11, 7), (12, 7)]
    return [datetime(year, month, day) for month, day in boundaries]


def _adjacent_solar_terms(dt: datetime) -> tuple[datetime, datetime]:
    candidates = _solar_term_boundaries(dt.year - 1) + _solar_term_boundaries(dt.year) + _solar_term_boundaries(dt.year + 1)
    previous_terms = [term for term in candidates if term <= dt]
    next_terms = [term for term in candidates if term > dt]
    previous_term = max(previous_terms) if previous_terms else candidates[0]
    next_term = min(next_terms) if next_terms else candidates[-1]
    return previous_term, next_term


def _format_age_months(months: int) -> str:
    safe_months = max(0, int(months))
    years = safe_months // 12
    month = safe_months % 12
    if month == 0:
        return str(years) + '岁'
    return str(years) + '岁' + str(month) + '个月'


def _month_pillar(dt: datetime, year_pillar: str) -> str:
    month_idx = _month_index(dt)
    return _month_pillar_by_index(year_pillar, month_idx)


def _month_pillar_by_index(year_pillar: str, month_idx: int) -> str:
    year_stem_idx = HEAVENLY_STEMS.index(year_pillar[0])
    start_stem_by_year = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}
    stem = HEAVENLY_STEMS[(start_stem_by_year[year_stem_idx] + month_idx) % 10]
    return stem + MONTH_BRANCHES[month_idx]


def _julian_day_number(dt: datetime) -> int:
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    return dt.day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _day_pillar(dt: datetime) -> str:
    return _pillar_from_index(_julian_day_number(dt) + 49)


def _hour_branch(hour: int) -> str:
    if hour == 23:
        return '子'
    return EARTHLY_BRANCHES[((hour + 1) // 2) % 12]


def _hour_pillar(dt: datetime, day_pillar: str, unknown_time: bool) -> str | None:
    if unknown_time:
        return None
    branch = _hour_branch(dt.hour)
    day_stem_idx = HEAVENLY_STEMS.index(day_pillar[0])
    start_stem_by_day = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}
    branch_idx = EARTHLY_BRANCHES.index(branch)
    stem = HEAVENLY_STEMS[(start_stem_by_day[day_stem_idx] + branch_idx) % 10]
    return stem + branch


def _count_five_elements(pillars: list[str | None]) -> dict[str, int]:
    counts = {'wood': 0, 'fire': 0, 'earth': 0, 'metal': 0, 'water': 0}
    for pillar in pillars:
        if not pillar:
            continue
        stem, branch = pillar[0], pillar[1]
        counts[ELEMENT_KEYS[STEM_ELEMENTS[stem]]] += 1
        counts[ELEMENT_KEYS[BRANCH_ELEMENTS[branch]]] += 1
    return counts


def _useful_elements(day_stem: str, counts: dict[str, int]) -> tuple[list[str], list[str], str]:
    day_element = STEM_ELEMENTS[day_stem]
    chinese_counts = {ELEMENT_LABELS[key]: value for key, value in counts.items()}
    support_score = chinese_counts[day_element] + chinese_counts[GENERATED_BY[day_element]]
    if support_score <= 2:
        return [GENERATED_BY[day_element], day_element], [CONTROLLED_BY[day_element], CONTROLS[day_element]], '偏弱'
    if support_score >= 5:
        return [CONTROLS[day_element], GENERATES[day_element]], [GENERATED_BY[day_element], day_element], '偏强'
    return [day_element, GENERATED_BY[day_element]], [CONTROLLED_BY[day_element]], '中和'


def _ten_god(day_stem: str, other_stem: str) -> str:
    day_element = STEM_ELEMENTS[day_stem]
    other_element = STEM_ELEMENTS[other_stem]
    same_polarity = STEM_YIN_YANG[day_stem] == STEM_YIN_YANG[other_stem]
    if other_element == day_element:
        return '比肩' if same_polarity else '劫财'
    if GENERATES[day_element] == other_element:
        return '食神' if same_polarity else '伤官'
    if CONTROLS[day_element] == other_element:
        return '偏财' if same_polarity else '正财'
    if CONTROLS[other_element] == day_element:
        return '七杀' if same_polarity else '正官'
    return '偏印' if same_polarity else '正印'


def _ten_gods(day_pillar: str, pillars: list[str | None]) -> dict[str, str]:
    names = ['year', 'month', 'day', 'hour']
    result: dict[str, str] = {}
    for name, pillar in zip(names, pillars):
        if pillar:
            result[name] = '日主' if name == 'day' else _ten_god(day_pillar[0], pillar[0])
    return result


def _cycle_theme(pillar: str, useful: list[str]) -> tuple[list[str], dict[str, int]]:
    elements = [STEM_ELEMENTS[pillar[0]], BRANCH_ELEMENTS[pillar[1]]]
    helpful = sum(1 for element in elements if element in useful)
    if helpful >= 2:
        return ['顺势成长', '贵人显现', '资源回流'], {'事业判定': 10, '财富机会': 8, '压力': -5}
    if helpful == 1:
        return ['有得有失', '转折频仍', '需要取舍'], {'事业判定': 3, '感情稳定': 2, '压力': 5}
    return ['逆势磨炼', '关系考验', '健康与压力课题'], {'事业判定': -8, '感情稳定': -6, '财富机会': -5, '压力': 12}


def _luck_start_months(dt: datetime, forward: bool) -> int:
    previous_term, next_term = _adjacent_solar_terms(dt)
    target = next_term if forward else previous_term
    days = abs((target - dt).total_seconds()) / 86400
    # Traditional conversion: 3 days ≈ 1 year, therefore 1 day ≈ 4 months.
    return max(1, int(round(days * 4)))


def _luck_cycles(dt: datetime, month_pillar: str, year_pillar: str, gender: str, useful: list[str]) -> list[dict[str, Any]]:
    year_stem = year_pillar[0]
    forward = (gender == 'male' and year_stem in YANG_STEMS) or (gender == 'female' and year_stem not in YANG_STEMS)
    month_index = _pillar_index(month_pillar)
    luck_start_months = _luck_start_months(dt, forward)
    cycles = []
    for i in range(8):
        offset = i + 1 if forward else -(i + 1)
        pillar = _pillar_from_index(month_index + offset)
        age_start_months = luck_start_months + i * 120
        age_end_exclusive_months = age_start_months + 120
        age_end_months = age_end_exclusive_months - 1
        age_start = age_start_months // 12
        age_end = age_end_months // 12
        theme, modifiers = _cycle_theme(pillar, useful)
        cycles.append({
            'age_start': age_start,
            'age_end': age_end,
            'age_start_months': age_start_months,
            'age_end_months': age_end_months,
            'age_start_label': _format_age_months(age_start_months),
            'age_end_label': _format_age_months(age_end_months),
            'pillar': pillar,
            'direction': '顺行' if forward else '逆行',
            'theme': theme,
            'modifiers': modifiers,
        })
    return cycles


def _annual_cycle(age: int, year: int, useful: list[str]) -> dict[str, Any]:
    pillar = _pillar_from_index(year - 4)
    elements = [STEM_ELEMENTS[pillar[0]], BRANCH_ELEMENTS[pillar[1]]]
    helpful = any(element in useful for element in elements)
    return {
        'age': age,
        'year': year,
        'pillar': pillar,
        'events': ['职业转折', '关系选择'] if helpful else ['压力累积', '资源消耗'],
        'risk': ['贪多失衡'] if helpful else ['过劳', '错误投资'],
        'opportunity': ['贵人引荐', '学习突破'] if helpful else ['逆境成长'],
    }


def _monthly_cycle(age: int, year: int, month: int, useful: list[str]) -> dict[str, Any]:
    year_pillar = _pillar_from_index(year - 4)
    month_idx = (month - 1) % 12
    pillar = _month_pillar_by_index(year_pillar, month_idx)
    elements = [STEM_ELEMENTS[pillar[0]], BRANCH_ELEMENTS[pillar[1]]]
    helpful_count = sum(1 for element in elements if element in useful)
    if helpful_count >= 2:
        theme = ['顺势推进', '资源聚拢']
        risk = ['节奏过快']
        opportunity = ['关键助力', '短期突破']
        modifiers = {'事业判定': 3, '学业判定': 3, '财富判定': 2, '压力': -1}
    elif helpful_count == 1:
        theme = ['有进有退', '需要取舍']
        risk = ['分心消耗']
        opportunity = ['局部机会']
        modifiers = {'事业判定': 1, '感情判定': 1, '社交判定': 1, '压力': 1}
    else:
        theme = ['逆势调整', '压力浮现']
        risk = ['判断失准', '体力透支']
        opportunity = ['修正旧局']
        modifiers = {'事业判定': -2, '财富判定': -2, '健康判定': -1, '压力': 3}
    return {
        'age': age,
        'year': year,
        'month': month,
        'month_name': FLOW_MONTH_NAMES[month_idx],
        'half': 1 if month <= 6 else 2,
        'pillar': pillar,
        'theme': theme,
        'risk': risk,
        'opportunity': opportunity,
        'modifiers': modifiers,
    }


def build_chart_tags(chart: dict[str, Any]) -> list[str]:
    counts = chart.get('five_elements', {})
    strongest = max(counts, key=counts.get) if counts else 'earth'
    weakest = min(counts, key=counts.get) if counts else 'water'
    tags = [
        '日主' + str(chart.get('day_master', '')),
        '身势' + str(chart.get('day_strength', '中和')),
        str(ELEMENT_LABELS.get(strongest, strongest)) + '气显',
        str(ELEMENT_LABELS.get(weakest, weakest)) + '气弱',
    ]
    useful = chart.get('useful_elements') or []
    if useful:
        tags.append('喜' + '、'.join(useful))
    return tags


def generate_bazi_chart(birth_info: dict[str, Any]) -> dict[str, Any]:
    dt, unknown_time = _parse_birth_datetime(birth_info)
    gender = str(birth_info.get('gender') or 'unknown')
    year_pillar = _year_pillar(dt)
    month_pillar = _month_pillar(dt, year_pillar)
    day_pillar = _day_pillar(dt)
    hour_pillar = _hour_pillar(dt, day_pillar, unknown_time)
    pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]
    counts = _count_five_elements(pillars)
    useful, unfavorable, day_strength = _useful_elements(day_pillar[0], counts)
    start_age = max(6, min(60, int(birth_info.get('start_age') or 22)))
    current_year = dt.year + start_age
    luck_cycles = _luck_cycles(dt, month_pillar, year_pillar, gender, useful)
    annual_cycles = [_annual_cycle(age, dt.year + age, useful) for age in range(start_age, 61)]
    monthly_cycles = [
        _monthly_cycle(age, dt.year + age, month, useful)
        for age in range(start_age, 61)
        for month in range(1, 13)
    ]
    chart = {
        'year_pillar': year_pillar,
        'month_pillar': month_pillar,
        'day_pillar': day_pillar,
        'hour_pillar': hour_pillar,
        'day_master': day_pillar[0] + STEM_ELEMENTS[day_pillar[0]],
        'day_strength': day_strength,
        'five_elements': counts,
        'useful_elements': useful,
        'unfavorable_elements': unfavorable,
        'ten_gods': _ten_gods(day_pillar, pillars),
        'mode': '三柱模式' if unknown_time else '四柱模式',
        'luck_start_label': luck_cycles[0]['age_start_label'] if luck_cycles else '',
        'luck_start_months': luck_cycles[0]['age_start_months'] if luck_cycles else 0,
    }
    return {'birth_info': {'calendar': birth_info.get('calendar', 'solar'), 'datetime': dt.isoformat(timespec='minutes'), 'unknown_time': unknown_time, 'gender': gender, 'timezone': birth_info.get('timezone', 'Asia/Shanghai'), 'birth_place': birth_info.get('birth_place') or ''}, 'bazi_chart': chart, 'luck_cycles': luck_cycles, 'annual_cycles': annual_cycles, 'monthly_cycles': monthly_cycles, 'start_age': start_age, 'current_year': current_year, 'tags': build_chart_tags(chart)}
