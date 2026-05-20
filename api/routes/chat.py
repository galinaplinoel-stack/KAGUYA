"""Chat route — apply personality to LLM interactions."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from api.routes.personality import _profiles
from api.routes.emotion import _get_engine as get_emotion_engine
from api.routes.relationships import _get_manager as get_rel_manager
from kaguya.middleware.response_modifier import ResponseModifier

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat_with_personality(req: ChatRequest):
    """Generate a personality-enhanced prompt for LLM consumption.

    This endpoint doesn't call an LLM directly — it returns the
    modified system prompt and context that should be used with
    any OpenAI-compatible API.
    """
    profile = _profiles.get(req.personality_id)
    if not profile:
        raise HTTPException(404, "Personality not found")

    emotion_engine = get_emotion_engine(req.personality_id)
    rel_manager = get_rel_manager(req.personality_id)

    modifier = ResponseModifier(profile, emotion_engine, rel_manager)
    modified_prompt = modifier.modify_prompt(req.base_prompt, req.user_id)

    # Record this interaction
    rel_manager.record_interaction(req.user_id, sentiment=0.0)

    state = emotion_engine.current_state
    rel = rel_manager.get_relationship(req.user_id)

    return ChatResponse(
        modified_prompt=modified_prompt,
        personality_context=profile.traits.to_dict(),
        emotional_state={
            "emotion": state.primary_emotion.value,
            "intensity": state.intensity,
            "valence": state.valence,
        },
        relationship_context={
            "trust": rel.trust,
            "familiarity": rel.familiarity,
            "affinity": rel.affinity,
        } if rel else None,
    )
