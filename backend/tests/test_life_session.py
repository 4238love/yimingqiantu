from backend.app import life_session


def test_life_session_model_constructs_birth_input_session():
    session = life_session.new_session('model_player')

    assert session['player_id'] == 'model_player'
    assert session['phase'] == 'birth_input'
    assert session['display_history'] == [life_session.INTRO_TEXT]
    assert session['focus_memory']['last_focus'] == ''
    assert session['ending_codex']['total_count'] == len(life_session.ENDING_CODEX_CATALOG)


def test_life_session_model_normalizes_legacy_simulation_session():
    session = {
        'player_id': 'legacy_player',
        'phase': 'life_simulation',
        'current_age': 22,
        'life_state': {'健康': 50, '心智': 50, '情绪': 50, '学识': 50, '事业': 50, '财富': 50, '家庭': 50, '感情': 50, '社交': 50, '名望': 50, '福德': 50, '压力': 20},
        'focus_memory': {'last_focus': '发展事业', 'streak': '2'},
        'ending_codex': {'entries': [{'id': 'many_changes', 'unlocked': True, 'unlock_count': 1}]},
    }

    normalized = life_session.ensure_defaults(session)

    assert normalized is session
    assert session['focus_memory']['streak'] == 2
    assert session['action_options']
    assert session['action_guides']
    assert session['goal_progress']['goal_id']
    assert 'many_changes' in session['ending_codex']['unlocked_ids']
