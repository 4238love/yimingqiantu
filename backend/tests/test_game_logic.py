import asyncio
from pathlib import Path

from backend.app import action_guide, bazi_engine, ending_resolution, event_pool, game_command_router, game_logic, half_year_resolution, life_context_projection, life_goal_progress, life_session, life_stage_policy

def _generate_chart(session: dict, birth_info: dict) -> None:
    payload = {'type': 'generate_chart', **birth_info} if 'birth_info' in birth_info else {'type': 'generate_chart', 'birth_info': birth_info}
    game_logic.apply_player_action(session, payload)

async def _generate_chart_async(session: dict, birth_info: dict) -> None:
    payload = {'type': 'generate_chart', **birth_info} if 'birth_info' in birth_info else {'type': 'generate_chart', 'birth_info': birth_info}
    await game_logic.apply_player_action_async(session, payload)

def _generate_prelude(session: dict) -> None:
    game_logic.apply_player_action(session, {'type': 'generate_prelude'})

async def _generate_prelude_async(session: dict) -> None:
    await game_logic.apply_player_action_async(session, {'type': 'generate_prelude'})

def _accept_prelude(session: dict) -> None:
    game_logic.apply_player_action(session, {'type': 'accept_prelude'})

def _set_life_goal(session: dict, goal_id: str) -> None:
    game_logic.apply_player_action(session, {'type': 'set_life_goal', 'goal_id': goal_id})

def _choose_focuses(session: dict, focuses: list[str]) -> None:
    game_logic.apply_player_action(session, {'type': 'annual_action', 'focuses': focuses})

async def _choose_focuses_async(session: dict, focuses: list[str]) -> None:
    await game_logic.apply_player_action_async(session, {'type': 'annual_action', 'focuses': focuses})

def _retrospect_life(session: dict) -> None:
    game_logic.apply_player_action(session, {'type': 'retrospect_life'})

def _chart_session() -> dict:
    session = life_session.new_session('test_player')
    _generate_chart(
        session,
        {
            'birth_date': '2000-03-15',
            'birth_time': '08:30',
            'gender': 'male',
            'start_age': 22,
            'calendar': 'solar',
        },
    )
    return session

def test_custom_focus_text_maps_to_action_profile():
    assert half_year_resolution.normalize_focuses({'focuses': ['准备考研并考一个专业证书']}) == ['专注学业']
    assert half_year_resolution.normalize_focuses({'focuses': ['辞职创业，尝试做自己的产品']}) == ['创业冒险']
    assert half_year_resolution.normalize_focuses({'focuses': ['今年多陪父母和孩子']}) == ['陪伴家人']

def test_luck_cycle_start_is_independent_from_game_start_age():
    birth_info = {
        'birth_date': '2000-02-05',
        'birth_time': '08:30',
        'gender': 'male',
        'calendar': 'solar',
    }

    chart_from_8 = bazi_engine.generate_bazi_chart({**birth_info, 'start_age': 8})
    chart_from_30 = bazi_engine.generate_bazi_chart({**birth_info, 'start_age': 30})

    assert chart_from_8['start_age'] == 8
    assert chart_from_30['start_age'] == 30
    assert chart_from_8['luck_cycles'] == chart_from_30['luck_cycles']
    assert chart_from_30['luck_cycles'][0]['age_start'] != 30
    assert chart_from_30['luck_cycles'][0]['age_start_label'] == '9岁11个月'

def test_start_age_can_begin_at_six():
    session = life_session.new_session('age_6_player')
    _generate_chart(
        session,
        {
            'birth_info': {
                'birth_date': '2018-04-10',
                'birth_time': '09:00',
                'gender': 'unknown',
                'start_age': 6,
                'calendar': 'solar',
            }
        },
    )

    assert session['start_age'] == 6
    assert session['annual_cycles'][0]['age'] == 6
    assert session['monthly_cycles'][0]['age'] == 6

def test_childhood_stage_limits_adult_actions_after_start():
    session = life_session.new_session('stage_player')
    _generate_chart(
        session,
        {
            'birth_info': {
                'birth_date': '2018-04-10',
                'birth_time': '09:00',
                'gender': 'unknown',
                'start_age': 6,
                'calendar': 'solar',
            }
        },
    )
    _generate_prelude(session)
    _accept_prelude(session)

    assert session['current_stage']['label'] == '童年启蒙'
    assert '创业冒险' not in session['action_options']
    assert '投资理财' not in session['action_options']
    assert '专注学业' in session['action_options']
    assert session['life_systems']['career']['stage'].startswith('启蒙学习')
    assert session['relationships']
    assert session['life_goals']
    assert session['goal_progress']['title']
    assert session['action_guides']
    assert all('roll_target_preview' in guide for guide in session['action_guides'])
    assert all((guide.get('life_choice') or {}).get('decision') for guide in session['action_guides'])
    assert all((guide.get('event_preview') or {}).get('bazi_event_influence') for guide in session['action_guides'])

    _choose_focuses(session, ['想创业赚钱'])
    assert session['annual_summaries'][-1]['main_focus'] == '专注学业'
    assert session['annual_summaries'][-1]['goal_progress_after']['goal_id'] == session['active_life_goal_id']
    assert session['achievements']
    assert session['milestones']
    assert session['annual_summaries'][-1]['new_achievements']
    assert session['annual_summaries'][-1]['milestone']['title']

def test_player_can_select_life_goal_before_starting_life():
    session = life_session.new_session('goal_player')
    _generate_chart(
        session,
        {
            'birth_info': {
                'birth_date': '2000-03-15',
                'birth_time': '08:30',
                'gender': 'male',
                'start_age': 22,
                'calendar': 'solar',
            }
        },
    )
    _generate_prelude(session)
    _set_life_goal(session, 'warm_bonds')

    assert session['active_life_goal_id'] == 'warm_bonds'
    assert session['goal_progress']['title'] == '亲密圆满'
    assert any('【人生愿望】' in item for item in session['display_history'])

def test_current_luck_cycle_uses_real_luck_start_not_simulation_start_age():
    session = life_session.new_session('luck_cycle_player')
    _generate_chart(
        session,
        {
            'birth_info': {
                'birth_date': '2000-02-05',
                'birth_time': '08:30',
                'gender': 'male',
                'start_age': 30,
                'calendar': 'solar',
            }
        },
    )
    _generate_prelude(session)
    _accept_prelude(session)

    assert session['current_age'] == 30
    assert session['current_luck_cycle']['age_start_label'] == '29岁11个月'
    assert session['current_luck_cycle']['age_start'] != session['start_age']

def test_chart_async_falls_back_when_ai_disabled(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = life_session.new_session('chart_player')

    asyncio.run(_generate_chart_async(
        session,
        {
            'birth_info': {
                'birth_date': '2000-03-15',
                'birth_time': '08:30',
                'gender': 'male',
                'start_age': 22,
                'calendar': 'solar',
            }
        },
    ))

    assert session['phase'] == 'chart_ready'
    assert session['bazi_analysis']['source'] == 'deterministic'
    assert session['life_topics']
    assert session['suitable_directions']
    assert session['high_risk_fields']

def test_prelude_async_falls_back_when_ai_disabled(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = _chart_session()

    asyncio.run(_generate_prelude_async(session))

    assert session['phase'] == 'prelude_ready'
    assert session['prelude']['text']
    assert len(session['prelude']['text']) >= 220
    assert len(session['prelude']['early_events']) >= 4
    assert session['life_state']['健康'] >= 0

def test_annual_action_accepts_custom_text(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)

    _choose_focuses(session, ['准备考研并提升专业技能'])

    latest = session['annual_summaries'][-1]
    assert latest['focuses'] == ['专注学业']
    assert latest['roll_event']['type'] == '学业判定'
    assert latest['stage_event']['event']
    assert latest['fate_explanation']['bazi_influence']
    assert latest['fate_explanation']['fortune_influence']
    assert latest['fate_explanation']['choice_influence']
    assert latest['fate_explanation']['life_scene']
    assert latest['fate_explanation']['bazi_life_detail']
    assert latest['life_systems_after']['career']['score'] >= 0
    assert latest['relationships_after']
    assert latest['half_label'] == '上半年'
    assert latest['monthly_cycles']
    assert session['current_half'] == 2
    latest_history = session['display_history'][-1]
    assert '状态变化：' in latest_history
    assert "{'" not in latest_history
    assert '学识 ' in latest_history
    assert len(latest['summary']) >= 180
    assert any(item.startswith('【阶段叙事】') for item in session['display_history'])
    stage_history = next(item for item in session['display_history'] if item.startswith('【阶段叙事】'))
    assert '具体场景' in stage_history
    assert '生活片段' in stage_history
    assert '阶段事件' in stage_history
    assert '命盘影响' in stage_history
    assert '选择影响' in stage_history
    assert '命盘与时势' in stage_history
    assert '生活叙事' in latest_history
    assert '判定细节' in latest_history

def test_custom_choice_preserves_raw_text_and_backend_classification(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)

    _choose_focuses(session, ['去上海找工作'])

    latest = session['annual_summaries'][-1]
    assert latest['raw_choice_text'] == '去上海找工作'
    assert latest['raw_focuses'] == ['去上海找工作']
    assert latest['normalized_focuses'] == ['发展事业', '搬迁远行']
    assert latest['choice_intent']['is_custom'] is True
    assert latest['choice_intent']['classification_text'] == '发展事业、搬迁远行'
    assert latest['main_focus'] == '发展事业'
    assert latest['roll_event']['type'] == '事业判定'
    assert '去上海找工作' in latest['summary']
    assert '系统将它归入“发展事业、搬迁远行”' in latest['summary']
    assert '去上海找工作' in session['display_history'][-1]
    assert any('玩家选择' not in item and '去上海找工作' in item for item in session['display_history'])
    assert latest['fate_explanation']['choice_influence'].startswith('你选择“去上海找工作”')

def test_bazi_context_weights_stage_event_style():
    stage = half_year_resolution.age_stage(6)
    gold_water = {
        'useful_elements': ['金', '水'],
        'unfavorable_elements': [],
        'ten_gods': ['正官', '正印'],
        'chart_tags': [],
        'luck_themes': [],
        'annual_events': [],
    }
    wood_earth = {
        'useful_elements': ['木', '土'],
        'unfavorable_elements': ['木'],
        'ten_gods': ['比肩', '食神'],
        'chart_tags': ['土气显'],
        'luck_themes': [],
        'annual_events': [],
    }

    gold_event = event_pool.pick_stage_event('same_player', 6, 1, '专注学业', '成功', stage, gold_water)
    wood_event = event_pool.pick_stage_event('same_player', 6, 1, '专注学业', '成功', stage, wood_earth)

    assert gold_event['title'] == '旧题重做'
    assert wood_event['title'] == '沉默积累'
    assert gold_event['title'] != wood_event['title']
    assert '规则训练和信息整理' in gold_event['bazi_event_influence']
    assert gold_event['bazi_event_score'] != wood_event['bazi_event_score']
    assert {'金', '水'} <= set(gold_event['elements'])
    assert gold_event['life_domains']

def test_life_memory_records_and_echoes_at_later_age(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    monkeypatch.setattr(half_year_resolution.random, 'randint', lambda start, end: 42)
    session = life_session.new_session('memory_echo_player')
    _generate_chart(
        session,
        {
            'birth_info': {
                'birth_date': '2018-04-10',
                'birth_time': '09:00',
                'gender': 'unknown',
                'start_age': 6,
                'calendar': 'solar',
            }
        },
    )
    _generate_prelude(session)
    _accept_prelude(session)

    _choose_focuses(session, ['反复学习旧题'])
    first = session['annual_summaries'][-1]
    assert first['life_memory']['echo_after_age'] == 18
    assert first['life_memory']['choice_text'] == '反复学习旧题'
    assert session['life_memories']

    session['current_age'] = 18
    session['current_half'] = 1
    session['current_half_label'] = '上半年'
    _choose_focuses(session, ['准备升学考试'])
    latest = session['annual_summaries'][-1]

    assert latest['memory_echoes']
    assert '反复学习旧题' in latest['memory_echoes'][0]['text']
    assert '伏笔与回声' in latest['summary']

def test_game_command_router_owns_public_action_dispatch(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    source = Path('backend/app/game_logic.py').read_text(encoding='utf-8')
    assert 'COMMAND_ROUTER.dispatch(session, action)' in source
    assert 'COMMAND_ROUTER.dispatch_async(session, action)' in source
    assert 'def _action_payload' not in source

    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)

    game_logic.apply_player_action(session, '专注学业')

    assert isinstance(game_logic.COMMAND_ROUTER, game_command_router.GameCommandRouter)
    assert session['annual_summaries'][-1]['main_focus'] == '专注学业'

def test_half_year_resolution_delegates_policy_to_deepened_modules():
    source = Path('backend/app/half_year_resolution.py').read_text(encoding='utf-8')

    assert 'life_stage_policy.age_stage(age)' in source
    assert 'life_goal_progress.refresh_goal_progress(session)' in source
    assert 'life_systems.refresh_life_systems(session, record)' in source
    assert half_year_resolution.ACTION_OPTIONS == life_stage_policy.ACTION_OPTIONS
    assert half_year_resolution.LIFE_GOAL_TEMPLATES == life_goal_progress.LIFE_GOAL_TEMPLATES

def test_life_context_projection_owns_action_guides():
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)
    session['action_guides'] = []

    half_year_resolution.refresh_current_context(session, game_logic.ACTION_DETAIL)
    assert session['action_guides'] == []

    life_context_projection.refresh_current_context(session, game_logic.ACTION_DETAIL)
    assert session['action_guides']
    assert session['current_life']['行动预览'] == session['action_guides']
    source = Path('backend/app/half_year_resolution.py').read_text(encoding='utf-8')
    assert 'from . import action_guide' not in source
    assert 'import action_guide' not in source

def test_half_year_resolution_core_returns_authoritative_record(monkeypatch):
    monkeypatch.setattr(half_year_resolution.random, 'randint', lambda start, end: 42)
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)
    life_context_projection.refresh_current_context(session, game_logic.ACTION_DETAIL)

    record = half_year_resolution.resolve_authoritative_record(session, {'focuses': ['发展事业', '投资理财']})

    assert record['half_label'] == '上半年'
    assert record['main_focus'] == '发展事业'
    assert record['focuses'] == ['发展事业', '投资理财']
    assert record['roll_event']['result'] == 42
    assert record['roll_event']['modifiers'] == record['roll_modifiers']
    assert record['stage_event']['event']
    assert record['state_before'] != record['state_after']
    assert record['goal_progress_before']['goal_id'] == session['active_life_goal_id']
    assert session['roll_event'] == record['roll_event']
    assert session['focus_memory']['last_focus'] == '发展事业'

def test_half_year_resolution_owns_system_projection_and_cursor(monkeypatch):
    monkeypatch.setattr(half_year_resolution.random, 'randint', lambda start, end: 42)
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)
    life_context_projection.refresh_current_context(session, game_logic.ACTION_DETAIL)

    assert session['current_life']['行动预览'] == session['action_guides']
    assert session['current_monthly_cycles']

    record = half_year_resolution.resolve_authoritative_record(session, {'focuses': ['发展事业']})
    half_year_resolution.complete_authoritative_record(session, record)

    assert session['life_systems']['career']['stage'].startswith('职业入口')
    assert session['life_systems']['career']['notes']
    assert session['relationships'][1]['name'] == '伴侣/亲密关系'
    assert record['goal_progress_after']['goal_id'] == session['active_life_goal_id']
    assert record['new_achievements']
    assert record['milestone']['title']
    assert session['latest_achievements'] == record['new_achievements']
    assert session['milestones'][-1] == record['milestone']

    half_year_resolution.advance_turn_cursor(session, record)
    assert session['current_half'] == 2
    assert session['current_age'] == 22

    half_year_resolution.advance_turn_cursor(session, {'half': 2, 'age': 22, 'year': session['current_year']})
    assert session['current_half'] == 1
    assert session['current_age'] == 23
    assert session['current_year'] == 2023

def test_stage_event_pool_returns_structured_event():
    stage = half_year_resolution.age_stage(22)
    picked = event_pool.pick_stage_event('event_pool_player', 22, 1, '发展事业', '成功', stage)

    assert len(event_pool.STAGE_EVENT_POOL[stage['id']]['发展事业']) >= 3
    assert picked['stage_id'] == stage['id']
    assert picked['event_id']
    assert picked['title']
    assert picked['event']
    assert picked['tags']
    assert isinstance(picked['state_bias'], dict)
    assert picked['clue']

def test_repeated_focus_adds_streak_feedback_and_effect(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)

    _choose_focuses(session, ['发展事业'])
    first = session['annual_summaries'][-1]
    _choose_focuses(session, ['发展事业'])
    second = session['annual_summaries'][-1]

    assert first['focus_streak']['count'] == 1
    assert first['streak_bonus'] == 0
    assert second['focus_streak']['count'] == 2
    assert second['streak_bonus'] == 3
    assert second['roll_modifiers']['连续投入'] == 3
    assert second['streak_effect']
    assert session['focus_memory']['last_focus'] == '发展事业'
    assert session['focus_memory']['streak'] == 2
    assert '连续选择反馈' in second['summary']
    assert any('连续选择反馈' in item for item in session['display_history'])

def test_action_guides_preview_goal_alignment_and_streak(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)
    _set_life_goal(session, 'recognized_work')
    life_context_projection.refresh_current_context(session, game_logic.ACTION_DETAIL)

    career_guide = next(item for item in session['action_guides'] if item['action'] == '发展事业')
    direct_career_guide = next(
        item for item in action_guide.build_decision_support(session, game_logic.ACTION_DETAIL)
        if item['action'] == '发展事业'
    )
    assert direct_career_guide == career_guide
    assert career_guide['goal_alignment']['level'] == '高度契合'
    assert career_guide['primary'] == '事业'
    assert career_guide['secondary'] == '财富'
    assert career_guide['risk'] == '压力'
    assert career_guide['roll_target_preview'] >= 20
    assert career_guide['streak_preview']['count'] == 1
    assert career_guide['life_choice']['short_label']
    assert '命盘' in career_guide['life_choice']['bazi_hint']

    _choose_focuses(session, ['发展事业'])
    next_career_guide = next(item for item in session['action_guides'] if item['action'] == '发展事业')
    assert next_career_guide['streak_preview']['count'] == 2
    assert next_career_guide['streak_preview']['bonus'] == 3
    assert next_career_guide['roll_target_preview'] >= next_career_guide['roll_target_base']
    assert next_career_guide['clue']

def test_ending_contains_life_archive(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = life_session.new_session('ending_archive_player')
    _generate_chart(
        session,
        {
            'birth_info': {
                'birth_date': '2000-03-15',
                'birth_time': '08:30',
                'gender': 'male',
                'start_age': 59,
                'calendar': 'solar',
            }
        },
    )
    _generate_prelude(session)
    _accept_prelude(session)
    _choose_focuses(session, ['发展事业'])
    _choose_focuses(session, ['陪伴家人'])

    ending = session['ending']
    assert ending['dimensions']
    assert ending['achievements']
    assert ending['regrets']
    assert ending['key_turning_points']
    assert ending['life_systems']
    assert ending['life_goal']
    assert 'life_goal_achieved' in ending
    assert ending['achievements_unlocked']
    assert ending['milestones']
    assert '主要成就' in ending['summary']

def test_player_can_retrospect_life_before_age_60(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = life_session.new_session('retrospect_player')
    _generate_chart(
        session,
        {
            'birth_info': {
                'birth_date': '2000-03-15',
                'birth_time': '08:30',
                'gender': 'male',
                'start_age': 22,
                'calendar': 'solar',
            }
        },
    )
    _generate_prelude(session)
    _accept_prelude(session)

    _retrospect_life(session)

    assert session['phase'] == 'ending'
    assert session['is_finished'] is True
    assert session['ending_reason'] == 'retrospect'
    assert session['ending']['reason'] == 'retrospect'
    assert '主动选择停下脚步' in session['ending']['summary']
    assert any(item.startswith('【回望一生：') for item in session['display_history'])

def test_hidden_ending_unlocks_from_final_state():
    session = life_session.new_session('hidden_ending_player')
    session['phase'] = 'life_simulation'
    session['current_age'] = 60
    session['life_state'] = {
        '健康': 78,
        '心智': 82,
        '情绪': 72,
        '学识': 86,
        '事业': 92,
        '财富': 64,
        '家庭': 45,
        '感情': 42,
        '社交': 68,
        '名望': 86,
        '福德': 40,
        '压力': 52,
    }

    ending_resolution.finish_session(session, 'age_60')

    ending = session['ending']
    assert ending['hidden_ending']['id'] in {'cloud_road_legacy', 'solitary_peak'}
    assert ending['hidden_ending']['title'] == ending['title']
    assert ending['hidden_ending']['rarity'] in {'稀有', '隐藏'}
    assert ending['hidden_endings']
    assert '隐藏结局' in ending['summary']

def test_ending_codex_records_first_unlock():
    session = life_session.new_session('codex_player')
    session['phase'] = 'life_simulation'
    session['current_age'] = 60
    session['current_half_label'] = '下半年'
    session['life_state'] = {
        '健康': 70,
        '心智': 60,
        '情绪': 62,
        '学识': 55,
        '事业': 42,
        '财富': 44,
        '家庭': 48,
        '感情': 45,
        '社交': 40,
        '名望': 30,
        '福德': 20,
        '压力': 38,
    }

    ending_resolution.finish_session(session, 'age_60')

    codex = session['ending_codex']
    assert codex['total_count'] == len(game_logic.ENDING_CODEX_CATALOG)
    assert codex['unlocked_count'] == 1
    assert codex['latest_unlocks'][0]['title'] == '一生多变，晚景自明'
    assert session['ending']['codex_progress']['unlocked_count'] == 1
    assert session['ending']['codex_unlocks'][0]['id'] == 'many_changes'
    assert any(item.startswith('【结局图鉴】首次解锁') for item in session['display_history'])

def test_reaching_age_60_finishes_immediately(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = life_session.new_session('age_60_player')
    _generate_chart(
        session,
        {
            'birth_info': {
                'birth_date': '2000-03-15',
                'birth_time': '08:30',
                'gender': 'male',
                'start_age': 59,
                'calendar': 'solar',
            }
        },
    )
    _generate_prelude(session)
    _accept_prelude(session)

    _choose_focuses(session, ['发展事业'])

    assert session['phase'] == 'life_simulation'
    assert session['current_age'] == 59
    assert session['current_half'] == 2

    _choose_focuses(session, ['发展事业'])

    assert session['phase'] == 'ending'
    assert session['is_finished'] is True
    assert session['current_age'] == 60
    assert half_year_resolution.finish_reason(session) == 'age_60'
    assert len(session['annual_summaries']) == 2
    assert len(session['half_year_summaries']) == 2
    assert session['ending']['title']

def test_ai_prelude_can_override_fallback(monkeypatch):
    async def fake_get_ai_response(*args, **kwargs):
        return '''
        {
          "text": "AI 生成的前传文本。",
          "personality": ["清醒", "韧性"],
          "life_state": {"健康": 66, "心智": 77, "情绪": 55, "学识": 80, "事业": 22, "财富": 18, "家庭": 45, "感情": 33, "社交": 44, "名望": 9, "福德": 3, "压力": 29},
          "early_events": ["一次搬家改变了学习环境"],
          "hidden_strengths": ["复盘能力"],
          "hidden_weaknesses": ["压力内化"]
        }
        '''

    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: True)
    monkeypatch.setattr(game_logic.openai_client, 'get_ai_response', fake_get_ai_response)
    session = _chart_session()

    asyncio.run(_generate_prelude_async(session))

    assert session['prelude']['source'] == 'ai'
    assert session['prelude']['text'].startswith('AI 生成的前传文本。')
    assert '补充底色' in session['prelude']['text']
    assert session['life_state']['心智'] == 77
    assert session['major_events'][0] == '一次搬家改变了学习环境'
    assert len(session['major_events']) >= 4

def test_ai_prelude_structured_events_are_formatted(monkeypatch):
    async def fake_get_ai_response(*args, **kwargs):
        return '''
        {
          "text": "AI 生成的前传文本。",
          "personality": ["敏锐"],
          "life_state": {"健康": 66, "心智": 77, "情绪": 55, "学识": 80, "事业": 22, "财富": 18, "家庭": 45, "感情": 33, "社交": 44, "名望": 9, "福德": 3, "压力": 29},
          "early_events": [
            {"age": 1, "year": 2003, "event": "出生时体质偏弱。", "impact": "健康基础值略低。"}
          ],
          "hidden_strengths": [],
          "hidden_weaknesses": []
        }
        '''

    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: True)
    monkeypatch.setattr(game_logic.openai_client, 'get_ai_response', fake_get_ai_response)
    session = _chart_session()

    asyncio.run(_generate_prelude_async(session))

    assert session['prelude']['early_events'][0] == '1岁（2003年）：出生时体质偏弱。 影响：健康基础值略低。'
    assert len(session['prelude']['early_events']) >= 4
    assert "{'age'" not in session['display_history'][-1]
    assert session['major_events'][0].startswith('1岁（2003年）')

def test_ai_bazi_analysis_can_enrich_chart(monkeypatch):
    async def fake_get_ai_response(prompt, *args, **kwargs):
        assert '命盘分析器' in prompt
        return '''
        {
          "five_element_balance": {"木": 2, "火": 1, "土": 2, "金": 3, "水": 2},
          "day_master_status": "中和偏强",
          "useful_elements": ["金", "水"],
          "unfavorable_elements": ["火"],
          "ten_god_focus": ["正官", "偏印"],
          "luck_cycle_themes": ["辛巳：事业上升"],
          "life_topics": ["AI课题：以专业能力换取稳定"],
          "suitable_directions": ["AI方向：规则清晰的职业路径"],
          "high_risk_fields": ["AI风险：过度追逐名望"],
          "chart_tags": ["AI洞察"]
        }
        '''

    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: True)
    monkeypatch.setattr(game_logic.openai_client, 'get_ai_response', fake_get_ai_response)
    session = life_session.new_session('ai_chart_player')

    asyncio.run(_generate_chart_async(
        session,
        {
            'birth_info': {
                'birth_date': '2000-03-15',
                'birth_time': '08:30',
                'gender': 'male',
                'start_age': 22,
                'calendar': 'solar',
            }
        },
    ))

    assert session['bazi_analysis']['source'] == 'ai'
    assert session['bazi_analysis']['day_master_status'] == '中和偏强'
    assert 'AI洞察' in session['chart_tags']
    assert session['life_topics'] == ['AI课题：以专业能力换取稳定']
    assert any('【命盘分析】' in item for item in session['display_history'])

def test_ai_life_gm_narrative_preserves_authoritative_state(monkeypatch):
    async def fake_get_ai_response(prompt, *args, **kwargs):
        if '人生 GM' in prompt:
            return '''
            {
              "scene_title": "雨夜里的选择",
              "narrative": "AI GM 叙事：你在压力下继续准备考试，结果由后端 D100 判定落定。",
              "state_update": {"财富": 100, "健康": 0},
              "memory_tags": ["年度叙事", "考试压力"]
            }
            '''
        return '''
        {
          "age": 22,
          "year": 2022,
          "summary": "AI 年度总结：学习选择被记录为长期筹码。",
          "state_effect": {"财富": 999},
          "long_term_impact": "更重视专业路线。",
          "memory_tags": ["学习"]
        }
        '''

    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: True)
    monkeypatch.setattr(game_logic.openai_client, 'get_ai_response', fake_get_ai_response)
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)

    asyncio.run(_choose_focuses_async(session, ['准备考研并提升专业技能']))

    latest = session['annual_summaries'][-1]
    assert latest['gm_source'] == 'ai'
    assert latest['gm_scene_title'] == '雨夜里的选择'
    assert latest['gm_state_update_suggestion'] == {'财富': 100, '健康': 0}
    assert session['life_state']['财富'] != 100
    assert session['life_state']['健康'] != 0
    assert any('【阶段叙事】' in item for item in session['display_history'])
    assert latest['state_effect'] != {'财富': 999}

def test_ai_annual_summary_can_override_latest_summary(monkeypatch):
    async def fake_get_ai_response(*args, **kwargs):
        return '''
        {
          "age": 22,
          "year": 2022,
          "summary": "AI 年度总结：这一年把学习压力转化成长期筹码。",
          "state_effect": {"学识": 7},
          "long_term_impact": "后续职业选择更偏向专业路线。",
          "memory_tags": ["学习", "长期积累"]
        }
        '''

    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: True)
    monkeypatch.setattr(game_logic.openai_client, 'get_ai_response', fake_get_ai_response)
    session = _chart_session()
    _generate_prelude(session)
    _accept_prelude(session)

    asyncio.run(_choose_focuses_async(session, ['准备考研并提升专业技能']))

    latest = session['annual_summaries'][-1]
    assert latest['source'] == 'ai'
    assert latest['summary'].startswith('AI 年度总结')
    assert latest['memory_tags'] == ['学习', '长期积累']
    assert any('长期影响' in item for item in session['display_history'])
    assert not any("{'" in item for item in session['display_history'] if '状态变化：' in item)
