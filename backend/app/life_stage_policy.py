from __future__ import annotations

from typing import Any

from . import fate_mapper


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
