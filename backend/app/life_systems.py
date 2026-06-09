from __future__ import annotations

from typing import Any

from . import fate_mapper, life_metrics


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
            'status': life_metrics.score_label(int(state.get('家庭', 50))),
        },
        {
            'name': peer_name,
            'type': '同伴/亲密',
            'closeness': life_metrics.average_state(state, ['感情', '社交', '情绪']),
            'status': life_metrics.score_label(life_metrics.average_state(state, ['感情', '社交', '情绪'])),
        },
        {
            'name': mentor_name,
            'type': '机会',
            'closeness': life_metrics.average_state(state, ['社交', '名望', '事业']),
            'status': life_metrics.score_label(life_metrics.average_state(state, ['社交', '名望', '事业'])),
        },
    ]


def refresh_life_systems(session: dict[str, Any], record: dict[str, Any] | None = None) -> None:
    systems = ensure_life_systems(session)
    state = session.get('life_state') or {}
    age = int(session.get('current_age') or session.get('start_age') or 22)
    scores = {
        'relationship': life_metrics.average_state(state, ['家庭', '感情', '社交', '情绪']),
        'career': life_metrics.average_state(state, ['学识', '事业', '名望', '心智']),
        'assets': life_metrics.average_state(state, ['财富', '事业', '福德']),
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
        item['stage'] = life_metrics.system_stage(key, age, score)
        item['trend'] = life_metrics.trend_label(score - previous)
        item['label'] = item.get('label') or {'relationship': '关系网络', 'career': '学业/职业', 'assets': '资产基础'}[key]
        notes = life_metrics.string_list(item.get('notes'), [], 8)
        if note and note not in notes:
            notes.append(note)
        item['notes'] = notes[-5:]
        systems[key] = item
    session['life_systems'] = systems
    refresh_relationships(session)
