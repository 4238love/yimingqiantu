import asyncio
from pathlib import Path

from backend.app import state_manager, state_publication


def _redirect_storage(tmp_path: Path) -> None:
    state_manager.DATA_DIR = tmp_path / 'game_data'
    state_manager.SESSIONS_DIR = state_manager.DATA_DIR / 'sessions'
    state_manager.INDEX_FILE = state_manager.DATA_DIR / 'index.json'
    state_manager.OLD_DATA_FILE = tmp_path / 'game_data.json'
    state_manager._meta_cache.clear()
    state_manager._sessions_index.clear()
    state_manager._index_modified = False


def test_save_session_persists_without_publication(monkeypatch, tmp_path):
    _redirect_storage(tmp_path)
    calls = []

    async def fake_send_json(player_id, message):
        calls.append(('game', player_id, message.get('type')))

    async def fake_live_publish(player_id, session_data):
        calls.append(('live', player_id, session_data.get('phase')))

    monkeypatch.setattr(state_publication.websocket_manager, 'send_json_to_player', fake_send_json)
    monkeypatch.setattr(state_publication.live_manager, 'broadcast_state_update', fake_live_publish)

    session = {
        'player_id': 'tester',
        'phase': 'birth_input',
        'internal_history': [{'role': 'user', 'content': 'hello'}],
        'display_history': ['hello'],
    }

    asyncio.run(state_manager.save_session('tester', session))
    assert calls == []
    assert asyncio.run(state_manager.get_session('tester'))['display_history'] == ['hello']

    session['phase'] = 'life_simulation'
    asyncio.run(state_publication.commit_session('tester', session))
    assert ('game', 'tester', 'full_state') in calls
    assert ('live', 'tester', 'life_simulation') in calls
