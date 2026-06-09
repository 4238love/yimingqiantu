from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


_SCHEMA_PATH = Path(__file__).with_name('state.schema.json')
_STATE_SCHEMA = json.loads(_SCHEMA_PATH.read_text(encoding='utf-8'))
SCHEMA_STATE_KEYS = frozenset(_STATE_SCHEMA.get('properties', {}).keys())
INTERNAL_STATE_KEYS = frozenset({'internal_history'})
PUBLIC_EXTRA_STATE_KEYS = frozenset({'prelude'})
PLAYER_STATE_KEYS = (SCHEMA_STATE_KEYS | PUBLIC_EXTRA_STATE_KEYS) - INTERNAL_STATE_KEYS
LIVE_STATE_KEYS = frozenset({
    'player_id',
    'phase',
    'current_age',
    'current_year',
    'current_half',
    'current_half_label',
    'current_life',
    'display_history',
    'is_finished',
    'ending',
})


def _copy_allowed(session: dict[str, Any], allowed_keys: frozenset[str]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in session.items()
        if key in allowed_keys
    }


def build_player_state(session: dict[str, Any]) -> dict[str, Any]:
    """Project authoritative session state for the active player client.

    The player sees the public state schema minus internal-only audit history.
    This Module is the single runtime seam for frontend-facing state shape.
    """
    return _copy_allowed(session, PLAYER_STATE_KEYS)


def build_live_state(session: dict[str, Any]) -> dict[str, Any]:
    """Project authoritative session state for live observers."""
    live_state = _copy_allowed(session, LIVE_STATE_KEYS)
    history = live_state.get('display_history')
    if isinstance(history, list):
        live_state['display_history'] = [
            copy.deepcopy(item)
            for item in history
            if not str(item or '').strip().startswith('> ')
        ]
    return live_state


def validate_player_state(state: dict[str, Any]) -> dict[str, Any]:
    """Return a lightweight validation summary for the player projection."""
    keys = set(state)
    return {
        'unexpected_keys': sorted(keys - PLAYER_STATE_KEYS),
        'internal_keys': sorted(keys & INTERNAL_STATE_KEYS),
        'missing_required_keys': sorted((set(_STATE_SCHEMA.get('required', [])) - INTERNAL_STATE_KEYS) - keys),
    }
