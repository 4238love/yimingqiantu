import tempfile
from pathlib import Path

import jsonpatch
from fastapi.testclient import TestClient

from backend.app import ai_settings, openai_client, state_manager

def _redirect_storage(tmp: str) -> None:
    state_manager.configure_storage_runtime(root=Path(tmp))

def _apply_ws_message(current_state: dict | None, message: dict) -> dict:
    if message['type'] == 'full_state':
        return message['data']
    if message['type'] == 'patch':
        assert current_state is not None
        return jsonpatch.apply_patch(current_state, message['patch'], in_place=False)
    raise AssertionError('unexpected websocket message type: ' + str(message.get('type')))

def test_guest_websocket_can_play_to_ending(monkeypatch):
    from backend.app import game_logic

    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)

    with tempfile.TemporaryDirectory() as tmp:
        _redirect_storage(tmp)
        from backend.app.main import app

        with TestClient(app) as client:
            guest_response = client.post('/api/guest')
            assert guest_response.status_code == 200

            init_response = client.post('/api/game/init')
            assert init_response.status_code == 200
            assert init_response.json()['phase'] == 'birth_input'

            with client.websocket_connect('/api/ws') as websocket:
                first_message = websocket.receive_json()
                state = _apply_ws_message(None, first_message)
                assert state['phase'] == 'birth_input'

                websocket.send_json({
                    'action': {
                        'type': 'generate_chart',
                        'birth_info': {
                            'birth_date': '2000-03-15',
                            'birth_time': '08:30',
                            'gender': 'male',
                            'start_age': 59,
                            'calendar': 'solar',
                        },
                    }
                })

                state = _apply_ws_message(state, websocket.receive_json())
                assert state['phase'] == 'chart_ready'
                assert state['bazi_chart']['day_master']
                assert state['bazi_analysis']['source'] == 'deterministic'

                websocket.send_json({'action': {'type': 'generate_prelude'}})
                state = _apply_ws_message(state, websocket.receive_json())
                assert state['phase'] == 'prelude_ready'
                assert state['prelude']['text']
                assert state['life_state']['健康'] >= 0

                websocket.send_json({'action': {'type': 'accept_prelude'}})
                state = _apply_ws_message(state, websocket.receive_json())
                assert state['phase'] == 'life_simulation'
                assert state['current_age'] == 59
                assert state['current_half'] == 1
                assert state['current_half_label'] == '上半年'
                assert state['current_annual_cycle']['age'] == 59
                assert len(state['current_monthly_cycles']) == 6

                websocket.send_json({'action': {'type': 'annual_action', 'focuses': ['准备考研并提升专业技能']}})
                state = _apply_ws_message(state, websocket.receive_json())
                assert state['phase'] == 'life_simulation'
                assert state['current_age'] == 59
                assert state['current_half'] == 2
                assert state['annual_summaries'][-1]['main_focus'] == '专注学业'
                assert state['annual_summaries'][-1]['half_label'] == '上半年'
                assert state['annual_summaries'][-1]['monthly_cycles']

                websocket.send_json({'action': {'type': 'annual_action', 'focuses': ['准备考研并提升专业技能']}})
                state = _apply_ws_message(state, websocket.receive_json())
                assert state['phase'] == 'ending'
                assert state['is_finished'] is True
                assert state['current_age'] == 60
                assert state['annual_summaries'][-1]['main_focus'] == '专注学业'
                assert state['annual_summaries'][-1]['half_label'] == '下半年'
                assert state['annual_summaries'][-1]['roll_event']['type'] == '学业判定'
                assert state['ending']['title']
                assert len(state['annual_summaries']) == 2

def test_guest_websocket_can_retrospect_life(monkeypatch):
    from backend.app import game_logic

    monkeypatch.setattr(game_logic.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)

    with tempfile.TemporaryDirectory() as tmp:
        _redirect_storage(tmp)
        from backend.app.main import app

        with TestClient(app) as client:
            assert client.post('/api/guest').status_code == 200
            assert client.post('/api/game/init').status_code == 200

            with client.websocket_connect('/api/ws') as websocket:
                state = _apply_ws_message(None, websocket.receive_json())
                websocket.send_json({
                    'action': {
                        'type': 'generate_chart',
                        'birth_info': {
                            'birth_date': '2000-03-15',
                            'birth_time': '08:30',
                            'gender': 'male',
                            'start_age': 22,
                            'calendar': 'solar',
                        },
                    }
                })
                state = _apply_ws_message(state, websocket.receive_json())
                websocket.send_json({'action': {'type': 'generate_prelude'}})
                state = _apply_ws_message(state, websocket.receive_json())
                websocket.send_json({'action': {'type': 'accept_prelude'}})
                state = _apply_ws_message(state, websocket.receive_json())
                assert state['phase'] == 'life_simulation'

                websocket.send_json({'action': {'type': 'retrospect_life'}})
                state = _apply_ws_message(state, websocket.receive_json())

                assert state['phase'] == 'ending'
                assert state['is_finished'] is True
                assert state['ending_reason'] == 'retrospect'
                assert state['ending']['reason'] == 'retrospect'
                assert any(item.startswith('【回望一生：') for item in state['display_history'])
                assert state['ending_codex']['unlocked_count'] == 1

                websocket.send_json({'action': {'type': 'reset_game'}})
                state = _apply_ws_message(state, websocket.receive_json())
                assert state['phase'] == 'birth_input'
                assert state['ending_codex']['unlocked_count'] == 1

def test_guest_can_manage_custom_ai_settings(monkeypatch):
    async def fake_test_text_ai_connection(user_id, payload):
        assert user_id.startswith('guest_')
        if payload.get('profile_id'):
            return {'ok': True, 'message': '连接成功：已保存配置', 'base_url': 'saved', 'model': 'saved'}
        assert payload['api_key'] == 'sk-test-custom-key'
        assert payload['base_url'] == 'https://api.example.test/v1'
        assert payload['model'] == 'custom-model'
        return {'ok': True, 'message': '连接成功：连接成功', 'base_url': payload['base_url'], 'model': payload['model']}

    monkeypatch.setattr(openai_client, 'test_text_ai_connection', fake_test_text_ai_connection)

    with tempfile.TemporaryDirectory() as tmp:
        _redirect_storage(tmp)
        from backend.app.main import app

        with TestClient(app) as client:
            assert client.get('/api/settings/ai').status_code == 401
            assert client.post('/api/settings/ai/test', json={}).status_code == 401

            guest_response = client.post('/api/guest')
            assert guest_response.status_code == 200
            username = guest_response.json()['username']

            initial = client.get('/api/settings/ai')
            assert initial.status_code == 200
            assert initial.json()['custom_enabled'] is False

            saved = client.post('/api/settings/ai', json={
                'api_key': 'sk-test-custom-key',
                'base_url': 'https://api.example.test/v1',
                'model': 'custom-model',
            })
            assert saved.status_code == 200
            saved_payload = saved.json()
            assert saved_payload['custom_enabled'] is True
            assert saved_payload['api_key_set'] is True
            assert saved_payload['api_key_mask'].startswith('sk-t')
            assert saved_payload['base_url'] == 'https://api.example.test/v1'
            assert saved_payload['model'] == 'custom-model'
            assert saved_payload['version'] == 3
            assert len(saved_payload['profiles']) == 1
            default_profile_id = saved_payload['active_profile_id']

            stored = ai_settings.get_custom_ai_config(username)
            assert stored
            assert stored['api_key'] == 'sk-test-custom-key'
            raw_settings = (state_manager.ai_settings_dir() / (username + '.json')).read_text(encoding='utf-8')
            assert 'sk-test-custom-key' not in raw_settings
            assert 'api_key_secret' in raw_settings
            assert '"api_key"' not in raw_settings
            assert openai_client.is_text_ai_enabled(username) is True
            assert openai_client._test_config(username, {'profile_id': default_profile_id})['api_key'] == 'sk-test-custom-key'
            assert openai_client._test_config(username, {'profile_id': 'missing-profile'})['api_key'] == ''

            tested = client.post('/api/settings/ai/test', json={
                'api_key': 'sk-test-custom-key',
                'base_url': 'https://api.example.test/v1',
                'model': 'custom-model',
            })
            assert tested.status_code == 200
            assert tested.json()['ok'] is True

            second = client.post('/api/settings/ai/profiles', json={
                'name': 'Second API',
                'api_key': 'sk-second-custom-key',
                'base_url': 'https://api.second.example/v1',
                'model': 'second-model',
                'enabled': True,
            })
            assert second.status_code == 200
            second_payload = second.json()
            assert len(second_payload['profiles']) == 2
            second_profile = next(item for item in second_payload['profiles'] if item['name'] == 'Second API')
            assert second_profile['api_key_set'] is True
            assert second_profile['api_key_mask'].startswith('sk-s')
            assert second_payload['active_profile_id'] == default_profile_id

            activated = client.post('/api/settings/ai/profiles/' + second_profile['id'] + '/activate')
            assert activated.status_code == 200
            assert activated.json()['active_profile_id'] == second_profile['id']
            assert ai_settings.get_custom_ai_config(username)['model'] == 'second-model'

            saved_profile_test = client.post('/api/settings/ai/profiles/' + second_profile['id'] + '/test')
            assert saved_profile_test.status_code == 200
            assert saved_profile_test.json()['ok'] is True

            deleted = client.delete('/api/settings/ai/profiles/' + second_profile['id'])
            assert deleted.status_code == 200
            assert len(deleted.json()['profiles']) == 1
            assert deleted.json()['active_profile_id'] == default_profile_id

            cleared = client.delete('/api/settings/ai')
            assert cleared.status_code == 200
            assert cleared.json()['custom_enabled'] is False
            assert ai_settings.get_custom_ai_config(username) is None

def test_legacy_single_ai_settings_are_migrated_in_memory():
    with tempfile.TemporaryDirectory() as tmp:
        _redirect_storage(tmp)
        player_id = 'legacy_player'
        settings_dir = state_manager.ai_settings_dir()
        settings_dir.mkdir(parents=True, exist_ok=True)
        (settings_dir / (player_id + '.json')).write_text(
            '{"api_key":"sk-legacy-key","base_url":"https://legacy.example/v1","model":"legacy-model"}',
            encoding='utf-8',
        )

        public = ai_settings.public_ai_config(player_id)
        config = ai_settings.get_custom_ai_config(player_id)

        assert public['version'] == 3
        assert public['custom_enabled'] is True
        assert public['profiles'][0]['id'] == 'profile_default'
        assert public['profiles'][0]['api_key_set'] is True
        raw_settings = (settings_dir / (player_id + '.json')).read_text(encoding='utf-8')
        assert 'sk-legacy-key' not in raw_settings
        assert 'api_key_secret' in raw_settings
        assert '"api_key"' not in raw_settings
        assert config == {
            'api_key': 'sk-legacy-key',
            'base_url': 'https://legacy.example/v1',
            'model': 'legacy-model',
        }
