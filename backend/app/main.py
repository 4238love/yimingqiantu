import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated
from pathlib import Path

from fastapi import (
    FastAPI, APIRouter, Depends, HTTPException, status,
    WebSocket, WebSocketDisconnect, Request
)
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import ai_settings, auth, game_logic, openai_client, state_manager, security
from .websocket_manager import manager as websocket_manager
from .live_system import live_manager
from .config import settings

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Application startup...")
    await state_manager.init_storage()
    state_manager.start_auto_save_task()
    yield
    logging.info("Application shutdown...")
    await state_manager.shutdown_storage()

# --- FastAPI App Instance ---
app = FastAPI(lifespan=lifespan, title="一命千途")

app.title = '一命千途'

# --- Routers ---
# Router for /api prefixed routes
api_router = APIRouter(prefix="/api")


# --- Authentication Routes ---
class AiSettingsPayload(BaseModel):
    id: str | None = None
    profile_id: str | None = None
    name: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    enabled: bool | None = None


@api_router.post("/logout")
async def logout():
    """
    Logs the user out by clearing the authentication cookie.
    """
    response = RedirectResponse(url="/")
    response.delete_cookie("token")
    return response

@api_router.post('/guest')
async def guest_login():
    guest_id = 'guest_' + str(int(asyncio.get_running_loop().time() * 1000))
    token = auth.create_access_token(
        data={'sub': guest_id, 'id': 0, 'name': '访客玩家', 'trust_level': 0},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    response = JSONResponse({'username': guest_id})
    response.set_cookie('token', value=token, httponly=True, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, samesite='lax')
    return response


@api_router.get('/settings/ai')
async def get_ai_settings(
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    return ai_settings.public_ai_config(str(current_user.get('username') or 'guest'))


@api_router.post('/settings/ai')
async def save_ai_settings(
    payload: AiSettingsPayload,
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    try:
        return ai_settings.save_custom_ai_config(
            str(current_user.get('username') or 'guest'),
            payload.model_dump(exclude_none=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.post('/settings/ai/test')
async def test_ai_settings(
    payload: AiSettingsPayload,
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    try:
        return await openai_client.test_text_ai_connection(
            str(current_user.get('username') or 'guest'),
            payload.model_dump(exclude_none=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.post('/settings/ai/profiles')
async def save_ai_profile(
    payload: AiSettingsPayload,
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    try:
        return ai_settings.save_profile(
            str(current_user.get('username') or 'guest'),
            payload.model_dump(exclude_none=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.delete('/settings/ai/profiles/{profile_id}')
async def delete_ai_profile(
    profile_id: str,
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    try:
        return ai_settings.delete_profile(str(current_user.get('username') or 'guest'), profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@api_router.post('/settings/ai/profiles/{profile_id}/activate')
async def activate_ai_profile(
    profile_id: str,
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    try:
        return ai_settings.activate_profile(str(current_user.get('username') or 'guest'), profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@api_router.post('/settings/ai/profiles/{profile_id}/test')
async def test_saved_ai_profile(
    profile_id: str,
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    try:
        return await openai_client.test_text_ai_connection(
            str(current_user.get('username') or 'guest'),
            {'profile_id': profile_id},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.delete('/settings/ai')
async def clear_ai_settings(
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    return ai_settings.clear_custom_ai_config(str(current_user.get('username') or 'guest'))

# --- Game Routes ---
@api_router.get("/live/players")
async def get_live_players():
    """Returns a list of the most recently active players for the live view."""
    return state_manager.get_most_recent_sessions(limit=10)

@api_router.post("/game/init")
async def init_game(
    current_user: Annotated[dict, Depends(auth.get_current_active_user)],
):
    """
    Initializes or retrieves the life simulation session for the player.
    This prepares the birth-input phase without advancing the game.
    """
    game_state = await game_logic.get_or_create_session(current_user)
    return game_state

# --- WebSocket Endpoint ---
@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for real-time game state updates."""
    token = websocket.cookies.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return
    try:
        payload = auth.decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token payload")
            return
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token validation failed")
        return

    await websocket_manager.connect(websocket, username)

    try:
        user_info = await auth.get_current_user(token)
        session = await state_manager.get_session(user_info["username"])
        if session:
            await websocket_manager.send_json_to_player(
                user_info["username"], {"type": "full_state", "data": session}
            )

        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action:
                await game_logic.process_player_action(user_info, action)

    except WebSocketDisconnect:
        websocket_manager.disconnect(username)

@api_router.websocket("/live/ws")
async def live_websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for the live viewing system."""
    token = websocket.cookies.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return
    try:
        user_info = await auth.get_current_user(token)
        viewer_id = user_info["username"]
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token validation failed")
        return

    await websocket_manager.connect(websocket, viewer_id)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "watch":
                encrypted_id = data.get("player_id")
                if encrypted_id:
                    target_id = security.decrypt_player_id(encrypted_id)
                    if not target_id:
                        logger.warning(f"Received invalid encrypted ID from {viewer_id}")
                        continue
                    
                    live_manager.add_viewer(viewer_id, target_id)
                    # Send the current state of the watched player immediately
                    target_state = await state_manager.get_session(target_id)
                    if target_state:
                        await websocket_manager.send_json_to_player(
                            viewer_id, {"type": "live_update", "data": target_state}
                        )

    except WebSocketDisconnect:
        websocket_manager.disconnect(viewer_id)
        live_manager.remove_viewer(viewer_id)


# --- Include API Router and Mount Static Files ---
app.include_router(api_router)
static_files_dir = Path(__file__).parent.parent.parent / "frontend"

# --- 404 Exception Handler ---
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Redirect all 404 errors to the root page."""
    return RedirectResponse(url="/")

app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")

# --- Uvicorn Runner ---
if __name__ == "__main__":
    import uvicorn
    # The first argument should be "main:app" and we should specify the app_dir
    # This makes running the script directly more robust.
    # For command line, the equivalent is:
    # uvicorn backend.app.main:app --host <host> --port <port> --reload
    uvicorn.run(
        "main:app",
        app_dir="backend/app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.UVICORN_RELOAD
    )
