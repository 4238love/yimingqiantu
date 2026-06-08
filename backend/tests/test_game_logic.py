import asyncio

from backend.app import bazi_engine, game_logic


def _chart_session() -> dict:
    session = game_logic._new_session('test_player')
    game_logic._handle_generate_chart(
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
    return session


def test_custom_focus_text_maps_to_action_profile():
    assert game_logic._normalize_focuses({'focuses': ['准备考研并考一个专业证书']}) == ['专注学业']
    assert game_logic._normalize_focuses({'focuses': ['辞职创业，尝试做自己的产品']}) == ['创业冒险']
    assert game_logic._normalize_focuses({'focuses': ['今年多陪父母和孩子']}) == ['陪伴家人']


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
    session = game_logic._new_session('age_6_player')
    game_logic._handle_generate_chart(
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
    session = game_logic._new_session('stage_player')
    game_logic._handle_generate_chart(
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
    game_logic._handle_generate_prelude(session)
    game_logic._handle_accept_prelude(session)

    assert session['current_stage']['label'] == '童年启蒙'
    assert '创业冒险' not in session['action_options']
    assert '投资理财' not in session['action_options']
    assert '专注学业' in session['action_options']
    assert session['life_systems']['career']['stage'].startswith('启蒙学习')
    assert session['relationships']
    assert session['life_goals']
    assert session['goal_progress']['title']

    game_logic._handle_annual_action(session, {'focuses': ['想创业赚钱']})
    assert session['annual_summaries'][-1]['main_focus'] == '专注学业'
    assert session['annual_summaries'][-1]['goal_progress_after']['goal_id'] == session['active_life_goal_id']
    assert session['achievements']
    assert session['milestones']
    assert session['annual_summaries'][-1]['new_achievements']
    assert session['annual_summaries'][-1]['milestone']['title']


def test_player_can_select_life_goal_before_starting_life():
    session = game_logic._new_session('goal_player')
    game_logic._handle_generate_chart(
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
    game_logic._handle_generate_prelude(session)
    game_logic._handle_set_life_goal(session, 'warm_bonds')

    assert session['active_life_goal_id'] == 'warm_bonds'
    assert session['goal_progress']['title'] == '亲密圆满'
    assert any('【人生愿望】' in item for item in session['display_history'])


def test_current_luck_cycle_uses_real_luck_start_not_simulation_start_age():
    session = game_logic._new_session('luck_cycle_player')
    game_logic._handle_generate_chart(
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
    game_logic._handle_generate_prelude(session)
    game_logic._handle_accept_prelude(session)

    assert session['current_age'] == 30
    assert session['current_luck_cycle']['age_start_label'] == '29岁11个月'
    assert session['current_luck_cycle']['age_start'] != session['start_age']


def test_chart_async_falls_back_when_ai_disabled(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = game_logic._new_session('chart_player')

    asyncio.run(game_logic._handle_generate_chart_async(
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

    asyncio.run(game_logic._handle_generate_prelude_async(session))

    assert session['phase'] == 'prelude_ready'
    assert session['prelude']['text']
    assert len(session['prelude']['text']) >= 220
    assert len(session['prelude']['early_events']) >= 4
    assert session['life_state']['健康'] >= 0


def test_annual_action_accepts_custom_text(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = _chart_session()
    game_logic._handle_generate_prelude(session)
    game_logic._handle_accept_prelude(session)

    game_logic._handle_annual_action(session, {'focuses': ['准备考研并提升专业技能']})

    latest = session['annual_summaries'][-1]
    assert latest['focuses'] == ['专注学业']
    assert latest['roll_event']['type'] == '学业判定'
    assert latest['stage_event']['event']
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
    assert '阶段事件' in stage_history
    assert '命盘与时势' in stage_history
    assert '判定细节' in latest_history


def test_ending_contains_life_archive(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = game_logic._new_session('ending_archive_player')
    game_logic._handle_generate_chart(
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
    game_logic._handle_generate_prelude(session)
    game_logic._handle_accept_prelude(session)
    game_logic._handle_annual_action(session, {'focuses': ['发展事业']})
    game_logic._handle_annual_action(session, {'focuses': ['陪伴家人']})

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
    session = game_logic._new_session('retrospect_player')
    game_logic._handle_generate_chart(
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
    game_logic._handle_generate_prelude(session)
    game_logic._handle_accept_prelude(session)

    game_logic._handle_retrospect_life(session)

    assert session['phase'] == 'ending'
    assert session['is_finished'] is True
    assert session['ending_reason'] == 'retrospect'
    assert session['ending']['reason'] == 'retrospect'
    assert '主动选择停下脚步' in session['ending']['summary']
    assert any(item.startswith('【回望一生：') for item in session['display_history'])


def test_hidden_ending_unlocks_from_final_state():
    session = game_logic._new_session('hidden_ending_player')
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

    game_logic._finish_session(session, 'age_60')

    ending = session['ending']
    assert ending['hidden_ending']['id'] in {'cloud_road_legacy', 'solitary_peak'}
    assert ending['hidden_ending']['title'] == ending['title']
    assert ending['hidden_ending']['rarity'] in {'稀有', '隐藏'}
    assert ending['hidden_endings']
    assert '隐藏结局' in ending['summary']


def test_ending_codex_records_first_unlock():
    session = game_logic._new_session('codex_player')
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

    game_logic._finish_session(session, 'age_60')

    codex = session['ending_codex']
    assert codex['total_count'] == len(game_logic.ENDING_CODEX_CATALOG)
    assert codex['unlocked_count'] == 1
    assert codex['latest_unlocks'][0]['title'] == '一生多变，晚景自明'
    assert session['ending']['codex_progress']['unlocked_count'] == 1
    assert session['ending']['codex_unlocks'][0]['id'] == 'many_changes'
    assert any(item.startswith('【结局图鉴】首次解锁') for item in session['display_history'])


def test_reaching_age_60_finishes_immediately(monkeypatch):
    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)
    session = game_logic._new_session('age_60_player')
    game_logic._handle_generate_chart(
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
    game_logic._handle_generate_prelude(session)
    game_logic._handle_accept_prelude(session)

    game_logic._handle_annual_action(session, {'focuses': ['发展事业']})

    assert session['phase'] == 'life_simulation'
    assert session['current_age'] == 59
    assert session['current_half'] == 2

    game_logic._handle_annual_action(session, {'focuses': ['发展事业']})

    assert session['phase'] == 'ending'
    assert session['is_finished'] is True
    assert session['current_age'] == 60
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

    asyncio.run(game_logic._handle_generate_prelude_async(session))

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

    asyncio.run(game_logic._handle_generate_prelude_async(session))

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
    session = game_logic._new_session('ai_chart_player')

    asyncio.run(game_logic._handle_generate_chart_async(
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
    game_logic._handle_generate_prelude(session)
    game_logic._handle_accept_prelude(session)

    asyncio.run(game_logic._handle_annual_action_async(session, {'focuses': ['准备考研并提升专业技能']}))

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
    game_logic._handle_generate_prelude(session)
    game_logic._handle_accept_prelude(session)

    asyncio.run(game_logic._handle_annual_action_async(session, {'focuses': ['准备考研并提升专业技能']}))

    latest = session['annual_summaries'][-1]
    assert latest['source'] == 'ai'
    assert latest['summary'].startswith('AI 年度总结')
    assert latest['memory_tags'] == ['学习', '长期积累']
    assert any('长期影响' in item for item in session['display_history'])
    assert not any("{'" in item for item in session['display_history'] if '状态变化：' in item)
