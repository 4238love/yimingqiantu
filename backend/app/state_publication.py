from __future__ import annotations

import asyncio
from typing import Any

from . import state_manager
from .live_system import live_manager
from .websocket_manager import manager as websocket_manager


async def publish_game_state(player_id: str, session_data: dict[str, Any]) -> None:
    """Publish the authoritative session snapshot to the active player."""
    await websocket_manager.send_json_to_player(
        player_id,
        {'type': 'full_state', 'data': session_data},
    )


async def publish_live_state(player_id: str, session_data: dict[str, Any]) -> None:
    """Publish the authoritative session snapshot to live observers."""
    await live_manager.broadcast_state_update(player_id, session_data)


async def publish_session_update(player_id: str, session_data: dict[str, Any]) -> None:
    """Publish a committed session through every real-time Adapter."""
    await asyncio.gather(
        publish_game_state(player_id, session_data),
        publish_live_state(player_id, session_data),
    )


async def commit_session(player_id: str, session_data: dict[str, Any]) -> None:
    """Persist, then publish, a session mutation.

    Durable storage remains in state_manager.save_session(); this Module is the
    explicit commit/publish seam used by gameplay code that must notify clients.
    """
    await state_manager.save_session(player_id, session_data)
    await publish_session_update(player_id, session_data)


async def publish_live_snapshot(viewer_id: str, session_data: dict[str, Any]) -> None:
    """Send one watched session snapshot to a live-viewer connection."""
    await websocket_manager.send_json_to_player(
        viewer_id,
        {'type': 'live_update', 'data': session_data},
    )


def add_live_viewer(viewer_id: str, target_id: str) -> None:
    live_manager.add_viewer(viewer_id, target_id)


def remove_live_viewer(viewer_id: str) -> None:
    live_manager.remove_viewer(viewer_id)
