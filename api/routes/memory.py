"""Memory routes — store, retrieve, and manage memories."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from api.routes.personality import _profiles
from kaguya.memory.memory import MemoryManager
from kaguya.memory.retrieval import MemoryRetrieval
from kaguya.memory.conversation import ConversationMemory

router = APIRouter()

_managers: dict[str, MemoryManager] = {}
_retrievals: dict[str, MemoryRetrieval] = {}
_conversations: dict[str, ConversationMemory] = {}


def _get_memory(profile_id: str) -> MemoryManager:
    if profile_id not in _profiles:
        raise HTTPException(404, "Personality not found")
    if profile_id not in _managers:
        _managers[profile_id] = MemoryManager()
    return _managers[profile_id]


def _get_retrieval(profile_id: str) -> MemoryRetrieval:
    if profile_id not in _retrievals:
        _retrievals[profile_id] = MemoryRetrieval(_get_memory(profile_id))
    return _retrievals[profile_id]


def _get_conversation(profile_id: str) -> ConversationMemory:
    if profile_id not in _conversations:
        _conversations[profile_id] = ConversationMemory(_get_memory(profile_id))
    return _conversations[profile_id]


# --- Schemas ---

class StoreMemoryRequest(BaseModel):
    content: str = Field(..., min_length=1)
    memory_type: str = Field("fact")
    importance: float = Field(0.5, ge=0.0, le=1.0)
    emotional_valence: float = Field(0.0, ge=-1.0, le=1.0)
    emotional_intensity: float = Field(0.0, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    source: str = Field("")


class RetrieveMemoryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)
    memory_type: Optional[str] = None
    min_importance: float = Field(0.0, ge=0.0, le=1.0)


class AddTurnRequest(BaseModel):
    conversation_id: str = Field("default")
    role: str = Field("user")
    content: str = Field(..., min_length=1)
    emotion: str = Field("")
    sentiment: float = Field(0.0, ge=-1.0, le=1.0)


class MemoryResponse(BaseModel):
    id: str
    content: str
    memory_type: str
    importance: float
    emotional_valence: float
    tags: list[str]
    created_at: float


class MemoryStatsResponse(BaseModel):
    total: int
    by_type: dict[str, int]
    avg_importance: float
    avg_emotional_intensity: float


# --- Routes ---

@router.post("/{profile_id}/store", response_model=MemoryResponse)
async def store_memory(profile_id: str, req: StoreMemoryRequest):
    """Store a new memory."""
    mm = _get_memory(profile_id)
    entry = mm.store(
        content=req.content,
        memory_type=req.memory_type,
        importance=req.importance,
        emotional_valence=req.emotional_valence,
        emotional_intensity=req.emotional_intensity,
        tags=req.tags,
        source=req.source,
    )
    return MemoryResponse(
        id=entry.id,
        content=entry.content,
        memory_type=entry.memory_type,
        importance=entry.importance,
        emotional_valence=entry.emotional_valence,
        tags=entry.tags,
        created_at=entry.created_at,
    )


@router.post("/{profile_id}/retrieve", response_model=list[MemoryResponse])
async def retrieve_memories(profile_id: str, req: RetrieveMemoryRequest):
    """Retrieve memories by query with personality bias."""
    mm = _get_memory(profile_id)
    profile = _profiles.get(profile_id)
    traits = profile.traits.to_dict() if profile else None

    memories = mm.retrieve(
        query=req.query,
        top_k=req.top_k,
        personality_traits=traits,
        memory_type=req.memory_type,
        min_importance=req.min_importance,
    )
    return [
        MemoryResponse(
            id=m.id,
            content=m.content,
            memory_type=m.memory_type,
            importance=m.importance,
            emotional_valence=m.emotional_valence,
            tags=m.tags,
            created_at=m.created_at,
        )
        for m in memories
    ]


@router.get("/{profile_id}/stats", response_model=MemoryStatsResponse)
async def memory_stats(profile_id: str):
    """Get memory statistics."""
    mm = _get_memory(profile_id)
    stats = mm.get_stats()
    return MemoryStatsResponse(
        total=stats.get("total", 0),
        by_type=stats.get("by_type", {}),
        avg_importance=stats.get("avg_importance", 0.0),
        avg_emotional_intensity=stats.get("avg_emotional_intensity", 0.0),
    )


@router.get("/{profile_id}/important", response_model=list[MemoryResponse])
async def important_memories(profile_id: str, top_k: int = 10):
    """Get most important memories."""
    mm = _get_memory(profile_id)
    memories = mm.get_important_memories(top_k=top_k)
    return [
        MemoryResponse(
            id=m.id, content=m.content, memory_type=m.memory_type,
            importance=m.importance, emotional_valence=m.emotional_valence,
            tags=m.tags, created_at=m.created_at,
        )
        for m in memories
    ]


@router.get("/{profile_id}/emotional", response_model=list[MemoryResponse])
async def emotional_memories(profile_id: str, top_k: int = 10):
    """Get most emotionally charged memories."""
    mm = _get_memory(profile_id)
    memories = mm.get_emotional_memories(top_k=top_k)
    return [
        MemoryResponse(
            id=m.id, content=m.content, memory_type=m.memory_type,
            importance=m.importance, emotional_valence=m.emotional_valence,
            tags=m.tags, created_at=m.created_at,
        )
        for m in memories
    ]


@router.post("/{profile_id}/turn")
async def add_conversation_turn(profile_id: str, req: AddTurnRequest):
    """Add a conversation turn."""
    cm = _get_conversation(profile_id)
    turn = cm.add_turn(
        conversation_id=req.conversation_id,
        role=req.role,
        content=req.content,
        emotion=req.emotion,
        sentiment=req.sentiment,
    )
    return {"turn_id": turn.id, "conversation_id": turn.conversation_id}


@router.post("/{profile_id}/summarize")
async def summarize_conversations(profile_id: str):
    """Summarize all conversations into long-term memories."""
    cm = _get_conversation(profile_id)
    summaries = cm.summarize_all()
    return {
        "summarized": len(summaries),
        "memories": [m.to_dict() for m in summaries],
    }


@router.get("/{profile_id}/context")
async def get_memory_context(profile_id: str, query: str, max_tokens: int = 500):
    """Get memory context for LLM injection."""
    retrieval = _get_retrieval(profile_id)
    profile = _profiles.get(profile_id)
    traits = profile.traits.to_dict() if profile else None

    context = retrieval.build_context(
        query=query,
        personality_traits=traits,
        max_tokens=max_tokens,
    )
    return {"context": context, "query": query}


@router.delete("/{profile_id}/{memory_id}")
async def forget_memory(profile_id: str, memory_id: str):
    """Delete a memory."""
    mm = _get_memory(profile_id)
    if mm.forget(memory_id):
        return {"status": "forgotten", "memory_id": memory_id}
    raise HTTPException(404, "Memory not found")
