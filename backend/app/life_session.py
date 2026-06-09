from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

from . import half_year_resolution, life_context_projection

ENDING_CODEX_CATALOG = [
    {'id': 'early_broken', 'title': '命途早折之局', 'rarity': '普通', 'category': '基础结局', 'hint': '身体底盘被长期透支，人生会提前收束。', 'description': '健康归零时触发的提前终局，提醒玩家照看身体与压力。'},
    {'id': 'high_peak', 'title': '高处见山之一生', 'rarity': '普通', 'category': '基础结局', 'hint': '事业和名望一起走高，会抵达被看见的位置。', 'description': '事业与名望长期积累，最终站到更高处看见人生全景。'},
    {'id': 'wealthy_guardian', 'title': '富足守成之命', 'rarity': '普通', 'category': '基础结局', 'hint': '资产基础足够厚时，晚景会更安稳。', 'description': '财富经营成为一生安全感来源，守成比冒进更有价值。'},
    {'id': 'warm_family', 'title': '烟火圆满之一生', 'rarity': '普通', 'category': '基础结局', 'hint': '家庭与感情都被认真经营，会点亮烟火气。', 'description': '亲密关系和家庭责任相互支撑，人生在烟火中收束。'},
    {'id': 'inner_peace_ending', 'title': '心有所安之一生', 'rarity': '普通', 'category': '基础结局', 'hint': '心智、情绪和福德能让人从波折里安顿下来。', 'description': '精神维度稳定而丰厚，外在起伏没有夺走内在安处。'},
    {'id': 'many_changes', 'title': '一生多变，晚景自明', 'rarity': '普通', 'category': '基础结局', 'hint': '没有单项极致时，人生会以复杂和平衡收束。', 'description': '多条路径交错，没有绝对圆满，也没有彻底失败。'},
    {'id': 'cloud_road_legacy', 'title': '云路留名之命', 'rarity': '稀有', 'category': '隐藏结局', 'hint': '把专业积累和公众信誉一起推高。', 'description': '你把长期学习、专业交付和公开信誉连成一条路，最终留下可被他人引用或追随的名字。'},
    {'id': 'warm_hearth', 'title': '灯火可亲之一生', 'rarity': '稀有', 'category': '隐藏结局', 'hint': '亲密与家庭都足够高，同时不要让压力吞掉温度。', 'description': '你没有把圆满只押在外部成就上，而是在亲密关系与家庭责任里留下了可回去的灯火。'},
    {'id': 'hidden_gold', 'title': '厚土藏金之局', 'rarity': '稀有', 'category': '隐藏结局', 'hint': '财富要足够高，但健康和压力也必须守得住。', 'description': '你守住身体和节奏，也把资产基础慢慢夯实，富足不是骤得，而是长期稳住的结果。'},
    {'id': 'quiet_merit', 'title': '无名有福之人', 'rarity': '隐藏', 'category': '隐藏结局', 'hint': '高福德、低名望，也能走出另一种圆满。', 'description': '你未必站在众人目光中央，却在一次次善意、照护和留白里积下了柔软的转机。'},
    {'id': 'solitary_peak', 'title': '孤峰照雪之命', 'rarity': '隐藏', 'category': '隐藏结局', 'hint': '极高事业名望背后，可能需要付出关系代价。', 'description': '你抵达了高处，也清楚高处的风会带走一些陪伴；这不是单纯胜利，而是一种有代价的成就。'},
    {'id': 'free_roamer', 'title': '万里随心之途', 'rarity': '隐藏', 'category': '隐藏结局', 'hint': '自由探索愿望，或社交、心智、压力与财富之间的特殊平衡。', 'description': '你没有把人生压缩成单一答案，而是在关系、见闻和自我节奏之间，活出可进可退的自由。'},
    {'id': 'many_paths_master', 'title': '千途自明之卷', 'rarity': '传奇', 'category': '隐藏结局', 'hint': '大量成就、达成人生愿望，并守住身心底盘。', 'description': '你不是只赢下一条线，而是在愿望、身体、心智和多次过程反馈之间，把人生经营成完整的卷轴。'},
]
ENDING_CODEX_BY_ID = {item['id']: item for item in ENDING_CODEX_CATALOG}
ENDING_CODEX_ID_BY_TITLE = {item['title']: item['id'] for item in ENDING_CODEX_CATALOG}

INTRO_TEXT = '''
# 《一命千途》

命盘提供人生底色，选择改变人生路径。

请先填写出生日期、出生时间、性别与开始年龄。系统会生成八字命盘、大运流年、流月和人生前传；正式开始后，你将以半年为一回合，在学业、事业、感情、家庭、健康与财富之间做取舍。
'''

def normalize_ending_codex(raw: Any = None) -> dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    raw_entries = raw.get('entries') if isinstance(raw.get('entries'), list) else []
    raw_by_id = {str(item.get('id')): item for item in raw_entries if isinstance(item, dict) and item.get('id')}
    entries = []
    unlocked_ids = []
    for catalog in ENDING_CODEX_CATALOG:
        saved = raw_by_id.get(catalog['id'], {})
        unlocked = bool(saved.get('unlocked'))
        entry = {
            **catalog,
            'unlocked': unlocked,
            'unlocked_at': str(saved.get('unlocked_at') or ''),
            'unlock_count': int(saved.get('unlock_count') or 0),
            'last_reason': str(saved.get('last_reason') or ''),
            'last_age': saved.get('last_age'),
        }
        if unlocked:
            unlocked_ids.append(catalog['id'])
        entries.append(entry)
    latest = raw.get('latest_unlocks') if isinstance(raw.get('latest_unlocks'), list) else []
    latest = [item for item in latest if isinstance(item, dict)]
    return {
        'total_count': len(ENDING_CODEX_CATALOG),
        'unlocked_count': len(unlocked_ids),
        'unlocked_ids': unlocked_ids,
        'latest_unlocks': latest[:5],
        'entries': entries,
    }

def new_session(player_id: str) -> dict[str, Any]:
    return {
        'player_id': player_id,
        'session_date': date.today().isoformat(),
        'phase': 'birth_input',
        'birth_info': {},
        'bazi_chart': {},
        'bazi_analysis': {},
        'chart_tags': [],
        'life_topics': [],
        'suitable_directions': [],
        'high_risk_fields': [],
        'luck_cycles': [],
        'annual_cycles': [],
        'monthly_cycles': [],
        'start_age': None,
        'current_age': None,
        'current_year': None,
        'current_half': 1,
        'current_half_label': '上半年',
        'current_stage': {},
        'current_luck_cycle': {},
        'current_annual_cycle': {},
        'current_monthly_cycles': [],
        'life_state': {},
        'life_systems': {},
        'life_goals': [],
        'active_life_goal_id': '',
        'goal_progress': {},
        'achievements': [],
        'latest_achievements': [],
        'milestones': [],
        'personality': [],
        'relationships': [],
        'major_events': [],
        'half_year_summaries': [],
        'annual_summaries': [],
        'display_history': [INTRO_TEXT],
        'internal_history': [],
        'roll_event': None,
        'is_processing': False,
        'is_finished': False,
        'ending_reason': '',
        'ending': None,
        'ending_codex': normalize_ending_codex(),
        'focus_memory': half_year_resolution.empty_focus_memory(),
        'focus_streak': {},
        'streak_warning': '',
        'action_options': half_year_resolution.ACTION_OPTIONS,
        'action_guides': [],
        'current_life': None,
    }

def ensure_defaults(session: dict[str, Any], action_summaries: dict[str, str] | None = None) -> dict[str, Any]:
    session.setdefault('phase', 'birth_input')
    session.setdefault('display_history', [INTRO_TEXT])
    session.setdefault('internal_history', [])
    session.setdefault('current_stage', {})
    session.setdefault('life_systems', {})
    session.setdefault('life_goals', [])
    session.setdefault('active_life_goal_id', '')
    session.setdefault('goal_progress', {})
    session.setdefault('achievements', [])
    session.setdefault('latest_achievements', [])
    session.setdefault('milestones', [])
    session.setdefault('relationships', [])
    session.setdefault('ending_reason', '')
    session.setdefault('action_options', half_year_resolution.ACTION_OPTIONS)
    session.setdefault('action_guides', [])
    session.setdefault('current_life', None)
    session['focus_memory'] = half_year_resolution.normalize_focus_memory(session.get('focus_memory'))
    session.setdefault('focus_streak', {})
    session.setdefault('streak_warning', '')
    session['ending_codex'] = normalize_ending_codex(session.get('ending_codex'))
    if session.get('life_state'):
        half_year_resolution.ensure_life_goals(session)
        half_year_resolution.refresh_goal_progress(session)
    if session.get('phase') == 'life_simulation' and session.get('current_age') is not None:
        half_year_resolution.refresh_life_systems(session)
        session['action_options'] = half_year_resolution.stage_action_options(int(session.get('current_age') or 22))
        life_context_projection.refresh_current_context(session, action_summaries)
    return session
