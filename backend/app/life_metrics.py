from __future__ import annotations

from typing import Any

from . import fate_mapper


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


def string_list(value: Any, fallback: list[str] | None = None, limit: int = 12) -> list[str]:
    if not isinstance(value, list):
        return list(fallback or [])
    result = [str(item).strip() for item in value if str(item).strip()]
    return result[:limit] or list(fallback or [])
