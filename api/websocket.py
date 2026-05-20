"""WebSocket endpoint for real-time personality state streaming."""
from __future__ import annotations

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.routes.personality import _profiles
from api.routes.emotion import _get_engine

router = APIRouter()


@router.websocket("/{profile_id}")
async def stream_personality_state(websocket: WebSocket, profile_id: str):
    """Stream real-time personality state updates via WebSocket.

    Sends JSON updates every 2 seconds with current emotional state,
    personality traits, and any recent changes.
    """
    if profile_id not in _profiles:
        await websocket.close(code=4004, reason="Personality not found")
        return

    await websocket.accept()
    engine = _get_engine(profile_id)
    profile = _profiles[profile_id]

    try:
        while True:
            state = engine.current_state
            data = {
                "type": "state_update",
                "personality_id": profile_id,
                "name": profile.name,
                "emotion": {
                    "primary": state.primary_emotion.value,
                    "intensity": state.intensity,
                    "valence": state.valence,
                    "arousal": state.arousal,
                },
                "tone": engine.get_tone(),
                "traits": profile.traits.to_dict(),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close(code=1011)
