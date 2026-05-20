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
        interaction_count=rel.interaction_count,
    )


@router.post("/{profile_id}/{user_id}/interact", response_model=RelationshipResponse)
async def log_interaction(profile_id: str, user_id: str, req: InteractRequest):
    """Log an interaction and evolve the relationship."""
    manager = _get_manager(profile_id)
    manager.record_interaction(
        user_id=user_id,
        sentiment=req.sentiment,
        emotion=req.emotion,
        summary=req.summary,
    )
    rel = manager.get_relationship(user_id)
    return RelationshipResponse(
        personality_id=profile_id,
        user_id=user_id,
        trust=rel.trust,
        familiarity=rel.familiarity,
        affinity=rel.affinity,
        respect=rel.respect,
        interaction_count=rel.interaction_count,
    )


@router.get("/{profile_id}", response_model=list[RelationshipResponse])
async def list_relationships(profile_id: str):
    """List all relationships for a personality."""
    manager = _get_manager(profile_id)
    rels = manager.get_all_relationships()
    return [
        RelationshipResponse(
            personality_id=profile_id,
            user_id=uid,
            trust=r.trust,
            familiarity=r.familiarity,
            affinity=r.affinity,
            respect=r.respect,
            interaction_count=r.interaction_count,
        )
        for uid, r in rels.items()
    ]
