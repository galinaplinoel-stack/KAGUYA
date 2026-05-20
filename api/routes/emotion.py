"""Emotion routes — get and trigger emotional states."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from api.schemas import EmotionResponse, TriggerEmotionRequest
from api.routes.personality import _profiles
from kaguya.emotion.engine import EmotionalStateEngine

router = APIRouter()

_engines: dict[str, EmotionalStateEngine] = {}


def _get_engine(profile_id: str) -> EmotionalStateEngine:
    profile = _profiles.get(profile_id)
    if not profile:
        raise HTTPException(404, "Personality not found")
    if profile_id not in _engines:
        _engines[profile_id] = EmotionalStateEngine()
    return _engines[profile_id]


@router.get("/{profile_id}", response_model=EmotionResponse)
async def get_emotion(profile_id: str):
    """Get current emotional state."""
    engine = _get_engine(profile_id)
    state = engine.state
    return EmotionResponse(
        personality_id=profile_id,
        primary_emotion=state.primary_emotion.value,
        intensity=state.intensity,
        valence=state.valence,
        arousal=state.arousal,
    )


@router.post("/{profile_id}/trigger", response_model=EmotionResponse)
async def trigger_emotion(profile_id: str, req: TriggerEmotionRequest):
    """Trigger an emotional event."""
    engine = _get_engine(profile_id)
    engine.trigger(req.event)
    state = engine.state
    return EmotionResponse(
        personality_id=profile_id,
        primary_emotion=state.primary_emotion.value,
        intensity=state.intensity,
        valence=state.valence,
        arousal=state.arousal,
    )


@router.post("/{profile_id}/decay")
async def apply_decay(profile_id: str):
    """Apply emotional decay (simulate time passing)."""
    engine = _get_engine(profile_id)
    engine.update()
    state = engine.state
    return EmotionResponse(
        personality_id=profile_id,
        primary_emotion=state.primary_emotion.value,
        intensity=state.intensity,
        valence=state.valence,
        arousal=state.arousal,
    )
