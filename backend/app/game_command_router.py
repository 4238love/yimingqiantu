from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any


SyncHandler = Callable[[dict[str, Any], dict[str, Any]], None]
AsyncHandler = Callable[[dict[str, Any], dict[str, Any]], Awaitable[None]]


def action_payload(action: Any) -> dict[str, Any]:
    if isinstance(action, dict):
        return action
    value = str(action or '')
    return {'type': value, 'value': value}


def action_type(payload: dict[str, Any]) -> str:
    return str(payload.get('type') or payload.get('action') or payload.get('value') or '')


class GameCommandRouter:
    """Dispatch player commands through a small command Interface."""

    def __init__(self) -> None:
        self._sync_handlers: dict[str, SyncHandler] = {}
        self._async_handlers: dict[str, AsyncHandler] = {}
        self._default_sync: SyncHandler | None = None
        self._default_async: AsyncHandler | None = None

    def register(self, command_type: str, sync_handler: SyncHandler, async_handler: AsyncHandler | None = None) -> None:
        self._sync_handlers[command_type] = sync_handler
        if async_handler:
            self._async_handlers[command_type] = async_handler

    def set_default(self, sync_handler: SyncHandler, async_handler: AsyncHandler | None = None) -> None:
        self._default_sync = sync_handler
        self._default_async = async_handler

    def dispatch(self, session: dict[str, Any], action: Any) -> dict[str, Any]:
        payload = action_payload(action)
        command_type = action_type(payload)
        handler = self._sync_handlers.get(command_type) or self._default_sync
        if handler:
            handler(session, payload)
        return session

    async def dispatch_async(self, session: dict[str, Any], action: Any) -> dict[str, Any]:
        payload = action_payload(action)
        command_type = action_type(payload)
        handler = self._async_handlers.get(command_type)
        if handler:
            await handler(session, payload)
            return session
        sync_handler = self._sync_handlers.get(command_type) or self._default_sync
        if sync_handler:
            sync_handler(session, payload)
            return session
        if self._default_async:
            await self._default_async(session, payload)
        return session
