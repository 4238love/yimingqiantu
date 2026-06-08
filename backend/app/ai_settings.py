from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from . import state_manager
from .config import settings


STORE_VERSION = 2
DEFAULT_PROFILE_ID = 'profile_default'


def _safe_player_id(player_id: str) -> str:
    return str(player_id or 'guest').replace('/', '_').replace('\\', '_')


def _settings_dir() -> Path:
    return state_manager.DATA_DIR / 'ai_settings'


def _settings_path(player_id: str) -> Path:
    return _settings_dir() / (_safe_player_id(player_id) + '.json')


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _mask_key(api_key: str) -> str:
    key = str(api_key or '')
    if len(key) <= 8:
        return '*' * len(key)
    return key[:4] + '...' + key[-4:]


def _empty_store() -> dict[str, Any]:
    return {'version': STORE_VERSION, 'active_profile_id': '', 'profiles': []}


def _profile_id() -> str:
    return 'profile_' + uuid4().hex[:12]


def _normalize_store(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return _empty_store()
    if data.get('version') == STORE_VERSION and isinstance(data.get('profiles'), list):
        profiles = []
        for item in data.get('profiles') or []:
            if isinstance(item, dict):
                profiles.append(_normalize_profile(item, item.get('id') or _profile_id()))
        active_id = str(data.get('active_profile_id') or '')
        if active_id and not any(profile['id'] == active_id for profile in profiles):
            active_id = profiles[0]['id'] if profiles else ''
        if not active_id and profiles:
            active_id = profiles[0]['id']
        return {'version': STORE_VERSION, 'active_profile_id': active_id, 'profiles': profiles}

    # Backward compatibility: old single-key payload.
    api_key = str(data.get('api_key') or '').strip()
    if not api_key:
        return _empty_store()
    profile = _normalize_profile(
        {
            'id': DEFAULT_PROFILE_ID,
            'name': '默认配置',
            'api_key': api_key,
            'base_url': data.get('base_url') or settings.OPENAI_BASE_URL,
            'model': data.get('model') or settings.OPENAI_MODEL,
            'enabled': True,
        },
        DEFAULT_PROFILE_ID,
    )
    return {'version': STORE_VERSION, 'active_profile_id': DEFAULT_PROFILE_ID, 'profiles': [profile]}


def _normalize_profile(data: dict[str, Any], profile_id: str) -> dict[str, Any]:
    now = _now_iso()
    name = str(data.get('name') or data.get('label') or '自定义 API').strip()[:80] or '自定义 API'
    return {
        'id': str(profile_id or _profile_id()),
        'name': name,
        'api_key': str(data.get('api_key') or '').strip(),
        'base_url': str(data.get('base_url') or settings.OPENAI_BASE_URL).strip(),
        'model': str(data.get('model') or settings.OPENAI_MODEL).strip(),
        'enabled': bool(data.get('enabled', True)),
        'created_at': str(data.get('created_at') or now),
        'updated_at': str(data.get('updated_at') or now),
    }


def _read_store(player_id: str | None) -> dict[str, Any]:
    if not player_id:
        return _empty_store()
    path = _settings_path(player_id)
    try:
        if not path.exists():
            return _empty_store()
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return _empty_store()
    return _normalize_store(data)


def _write_store(player_id: str, store: dict[str, Any]) -> None:
    directory = _settings_dir()
    directory.mkdir(parents=True, exist_ok=True)
    _settings_path(player_id).write_text(json.dumps(_normalize_store(store), ensure_ascii=False, indent=2), encoding='utf-8')


def _active_profile(store: dict[str, Any]) -> dict[str, Any] | None:
    active_id = str(store.get('active_profile_id') or '')
    profiles = store.get('profiles') or []
    for profile in profiles:
        if profile.get('id') == active_id:
            return profile
    return profiles[0] if profiles else None


def _public_profile(profile: dict[str, Any], active_id: str) -> dict[str, Any]:
    api_key = str(profile.get('api_key') or '')
    return {
        'id': profile.get('id'),
        'name': profile.get('name') or '自定义 API',
        'api_key_set': bool(api_key),
        'api_key_mask': _mask_key(api_key) if api_key else '',
        'base_url': profile.get('base_url') or settings.OPENAI_BASE_URL,
        'model': profile.get('model') or settings.OPENAI_MODEL,
        'enabled': bool(profile.get('enabled', True)),
        'active': profile.get('id') == active_id,
        'created_at': profile.get('created_at') or '',
        'updated_at': profile.get('updated_at') or '',
    }


def get_profile_ai_config(player_id: str | None, profile_id: str | None, include_disabled: bool = False) -> dict[str, str] | None:
    if not player_id or not profile_id:
        return None
    store = _read_store(player_id)
    for profile in store.get('profiles') or []:
        if profile.get('id') == profile_id:
            api_key = str(profile.get('api_key') or '').strip()
            if not api_key or (not include_disabled and not bool(profile.get('enabled', True))):
                return None
            return {
                'api_key': api_key,
                'base_url': str(profile.get('base_url') or settings.OPENAI_BASE_URL).strip(),
                'model': str(profile.get('model') or settings.OPENAI_MODEL).strip(),
            }
    return None


def get_custom_ai_config(player_id: str | None) -> dict[str, str] | None:
    if not player_id:
        return None
    store = _read_store(player_id)
    profile = _active_profile(store)
    if not profile:
        return None
    return get_profile_ai_config(player_id, str(profile.get('id') or ''))


def save_profile(player_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    store = _read_store(player_id)
    profiles = store.get('profiles') or []
    incoming_id = str(payload.get('id') or payload.get('profile_id') or '').strip()
    existing = next((profile for profile in profiles if profile.get('id') == incoming_id), None)
    profile_id = incoming_id or _profile_id()
    now = _now_iso()
    data = {
        'id': profile_id,
        'name': payload.get('name') or (existing or {}).get('name') or '自定义 API',
        'api_key': (existing or {}).get('api_key', ''),
        'base_url': payload.get('base_url') or (existing or {}).get('base_url') or settings.OPENAI_BASE_URL,
        'model': payload.get('model') or (existing or {}).get('model') or settings.OPENAI_MODEL,
        'enabled': payload.get('enabled', (existing or {}).get('enabled', True)),
        'created_at': (existing or {}).get('created_at') or now,
        'updated_at': now,
    }
    if 'api_key' in payload and payload.get('api_key') is not None:
        data['api_key'] = str(payload.get('api_key') or '').strip()
    profile = _normalize_profile(data, profile_id)

    if existing:
        profiles = [profile if item.get('id') == profile_id else item for item in profiles]
    else:
        profiles.append(profile)
    store['profiles'] = profiles
    if not store.get('active_profile_id'):
        store['active_profile_id'] = profile_id
    _write_store(player_id, store)
    return public_ai_config(player_id)


def delete_profile(player_id: str, profile_id: str) -> dict[str, Any]:
    store = _read_store(player_id)
    profiles = [profile for profile in store.get('profiles') or [] if profile.get('id') != profile_id]
    if len(profiles) == len(store.get('profiles') or []):
        raise ValueError('profile not found')
    store['profiles'] = profiles
    if store.get('active_profile_id') == profile_id:
        store['active_profile_id'] = profiles[0]['id'] if profiles else ''
    if profiles:
        _write_store(player_id, store)
    else:
        clear_custom_ai_config(player_id)
    return public_ai_config(player_id)


def activate_profile(player_id: str, profile_id: str) -> dict[str, Any]:
    store = _read_store(player_id)
    if not any(profile.get('id') == profile_id for profile in store.get('profiles') or []):
        raise ValueError('profile not found')
    store['active_profile_id'] = profile_id
    _write_store(player_id, store)
    return public_ai_config(player_id)


def save_custom_ai_config(player_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    # Legacy single-profile endpoint: update the active profile or create default.
    store = _read_store(player_id)
    active = _active_profile(store)
    payload = dict(payload)
    payload['id'] = payload.get('id') or (active or {}).get('id') or DEFAULT_PROFILE_ID
    payload['name'] = payload.get('name') or (active or {}).get('name') or '默认配置'
    if not str(payload.get('api_key') or (active or {}).get('api_key') or '').strip():
        raise ValueError('api_key is required')
    return save_profile(player_id, payload)


def clear_custom_ai_config(player_id: str) -> dict[str, Any]:
    path = _settings_path(player_id)
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass
    return public_ai_config(player_id)


def public_ai_config(player_id: str | None) -> dict[str, Any]:
    store = _read_store(player_id)
    active = _active_profile(store)
    active_config = get_custom_ai_config(player_id)
    active_id = str(store.get('active_profile_id') or '')
    public_profiles = [_public_profile(profile, active_id) for profile in store.get('profiles') or []]
    if not active_config:
        return {
            'version': STORE_VERSION,
            'custom_enabled': False,
            'active_profile_id': active_id,
            'profiles': public_profiles,
            'api_key_set': False,
            'api_key_mask': '',
            'base_url': (active or {}).get('base_url') or settings.OPENAI_BASE_URL,
            'model': (active or {}).get('model') or settings.OPENAI_MODEL,
        }
    return {
        'version': STORE_VERSION,
        'custom_enabled': True,
        'active_profile_id': active_id,
        'profiles': public_profiles,
        'api_key_set': True,
        'api_key_mask': _mask_key(active_config['api_key']),
        'base_url': active_config['base_url'],
        'model': active_config['model'],
    }
