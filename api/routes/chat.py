"""Chat route — apply personality to LLM interactions with memory context."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from api.routes.personality import _profiles
from api.routes.emotion import _get_engine as get_emotion_engine
from api.routes.relationships import _get_manager as get_rel_manager
from api.routes.memory import _get_memory, _get_conversation, _get_retrieval
from kaguya.middleware.response_modifier import ResponseModifier

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat_with_personality(req: ChatRequest):
    """Generate a personality-enhanced prompt for LLM consumption.

    Now includes memory context from past interactions.
    """
    profile = _profiles.get(req.personality_id)
    if not profile:
        raise HTTPException(404, "Personality not found")

    emotion_engine = get_emotion_engine(req.personality_id)
    rel_manager = get_rel_manager(req.personality_id)
    memory_manager = _get_memory(req.personality_id)
    conversation = _get_conversation(req.personality_id)
    retrieval = _get_retrieval(req.personality_id)

    modifier = ResponseModifier(profile, emotion_engine, rel_manager)
    modified_prompt = modifier.modify_prompt(req.base_prompt, req.user_id)

    # Add memory context
    memory_context = retrieval.build_context(
        query=req.message,
        personality_traits=profile.traits.to_dict(),
    )
    if memory_context:
        modified_prompt += "\n\n" + memory_context

    # Record this interaction
    rel_manager.evolve(req.user_id, sentiment=0.0)

    # Add to conversation memory
    conversation.add_turn(
        conversation_id=f"{req.personality_id}_{req.user_id}",
        role="user",
        content=req.message,
        emotion=emotion_engine.state.primary_emotion.value,
        sentiment=0.0,
    )

    state = emotion_engine.state
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
        },
    )
