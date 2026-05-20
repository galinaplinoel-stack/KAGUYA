"""Relationship routes — manage per-user relationship tracking."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from api.schemas import RelationshipResponse, InteractRequest
from api.routes.personality import _profiles
from kaguya.relationships.manager import RelationshipManager

router = APIRouter()

_managers: dict[str, RelationshipManager] = {}


def _get_manager(profile_id: str) -> RelationshipManager:
    if profile_id not in _profiles:
        raise HTTPException(404, "Personality not found")
    if profile_id not in _managers:
        _managers[profile_id] = RelationshipManager()
    return _managers[profile_id]


@router.get("/{profile_id}/{user_id}", response_model=RelationshipResponse)
async def get_relationship(profile_id: str, user_id: str):
    """Get relationship data for a specific user."""
    manager = _get_manager(profile_id)
    rel = manager.get_relationship(user_id)
    return RelationshipResponse(
        personality_id=profile_id,
        user_id=user_id,
        trust=rel.trust,
        familiarity=rel.familiarity,
        affinity=rel.affinity,
        respect=rel.respect,
        interaction_count=0,
    )


@router.post("/{profile_id}/{user_id}/interact", response_model=RelationshipResponse)
async def log_interaction(profile_id: str, user_id: str, req: InteractRequest):
    """Log an interaction and evolve the relationship."""
    manager = _get_manager(profile_id)
    manager.evolve(
        user_id=user_id,
        sentiment=req.sentiment,
        event_type=req.emotion or "chat",
        summary=req.summary or "",
    )
    rel = manager.get_relationship(user_id)
    return RelationshipResponse(
        personality_id=profile_id,
        user_id=user_id,
        trust=rel.trust,
        familiarity=rel.familiarity,
        affinity=rel.affinity,
        respect=rel.respect,
        interaction_count=0,
    )


@router.get("/{profile_id}", response_model=list[RelationshipResponse])
async def list_relationships(profile_id: str):
    """List all relationships for a personality."""
    manager = _get_manager(profile_id)
    result = []
    for uid in manager.user_ids:
        rel = manager.get_relationship(uid)
        result.append(RelationshipResponse(
            personality_id=profile_id,
            user_id=uid,
            trust=rel.trust,
            familiarity=rel.familiarity,
            affinity=rel.affinity,
            respect=rel.respect,
            interaction_count=0,
        ))
    return result
