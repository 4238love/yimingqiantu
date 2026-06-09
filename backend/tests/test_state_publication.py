import asyncio
from pathlib import Path

from backend.app import life_session, state_manager, state_publication

def _redirect_storage(tmp_path: Path) -> None:
    state_manager.configure_storage_runtime(root=tmp_path)

def test_save_session_persists_without_publication(monkeypatch, tmp_path):
    _redirect_storage(tmp_path)
    calls = []

    async def fake_send_json(player_id, message):
        calls.append(('game', player_id, message.get('type'), message.get('data')))

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
    game_call = next(call for call in calls if call[:3] == ('game', 'tester', 'full_state'))
    assert 'internal_history' not in game_call[3]
    assert ('live', 'tester', 'life_simulation') in calls

def test_save_session_serializes_concurrent_history_writes(tmp_path):
    _redirect_storage(tmp_path)
    base = life_session.new_session('race_player')
    base['phase'] = 'life_simulation'
    asyncio.run(state_manager.save_session('race_player', base))

    first = {**base, 'display_history': base['display_history'] + ['first'], 'internal_history': [{'role': 'user', 'content': 'first'}]}
    second = {**base, 'display_history': base['display_history'] + ['second'], 'internal_history': [{'role': 'user', 'content': 'second'}]}

    async def save_both():
        await asyncio.gather(
            state_manager.save_session('race_player', first),
            state_manager.save_session('race_player', second),
        )

    asyncio.run(save_both())

    saved = asyncio.run(state_manager.get_session('race_player'))
    assert saved['display_history'][-2:] == ['first', 'second']
    assert [item['content'] for item in saved['internal_history']] == ['first', 'second']

def test_save_session_uses_atomic_json_replace(tmp_path):
    _redirect_storage(tmp_path)
    path = tmp_path / 'game_data' / 'atomic.json'

    asyncio.run(state_manager._write_json_file(path, {'value': 1}))
    asyncio.run(state_manager._write_json_file(path, {'value': 2}))

    assert state_manager.current_runtime().data_dir == tmp_path / 'game_data'
    assert path.read_text(encoding='utf-8').strip().endswith('"value": 2\n}')
    assert list(path.parent.glob('.*.tmp')) == []
