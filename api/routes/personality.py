"""Personality CRUD routes."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException, Request
from api.schemas import (
    CreatePersonalityRequest,
    UpdatePersonalityRequest,
    PersonalityResponse,
)
from kaguya.personality.traits import TraitVector
from kaguya.personality.profile import CharacterProfile
from kaguya.personality.presets import get_preset

router = APIRouter()

# In-memory store (swap for DB in production)
_profiles: dict[str, CharacterProfile] = {}


@router.post("", response_model=PersonalityResponse)
async def create_personality(req: CreatePersonalityRequest):
    """Create a new personality profile."""
    profile_id = str(uuid.uuid4())[:8]

    if req.preset:
        profile = get_preset(req.preset, name=req.name)
        if not profile:
            raise HTTPException(404, f"Preset '{req.preset}' not found")
    else:
        traits = TraitVector(**(req.traits.model_dump() if req.traits else {}))
        profile = CharacterProfile(name=req.name, id=profile_id, traits=traits)

    _profiles[profile_id] = profile
    return PersonalityResponse(
        id=profile.id,
        name=profile.name,
        traits=profile.traits.to_dict(),
        preset=req.preset,
        created_at=profile.created_at,
    )


@router.get("/{profile_id}", response_model=PersonalityResponse)
async def get_personality(profile_id: str):
    """Get a personality profile by ID."""
    profile = _profiles.get(profile_id)
    if not profile:
        raise HTTPException(404, "Personality not found")
    return PersonalityResponse(
        id=profile.id,
        name=profile.name,
        traits=profile.traits.to_dict(),
        preset=getattr(profile, "preset", None),
        created_at=profile.created_at,
    )


@router.put("/{profile_id}", response_model=PersonalityResponse)
async def update_personality(profile_id: str, req: UpdatePersonalityRequest):
    """Update a personality profile."""
    profile = _profiles.get(profile_id)
    if not profile:
        raise HTTPException(404, "Personality not found")

    if req.name:
        profile.name = req.name
    if req.traits:
        for key, value in req.traits.model_dump().items():
            if hasattr(profile.traits, key):
                setattr(profile.traits, key, value)

    return PersonalityResponse(
        id=profile.id,
        name=profile.name,
        traits=profile.traits.to_dict(),
        created_at=profile.created_at,
    )


@router.get("", response_model=list[PersonalityResponse])
async def list_personalities():
    """List all personality profiles."""
    return [
        PersonalityResponse(
            id=p.id, name=p.name, traits=p.traits.to_dict(),
            created_at=p.created_at,
        )
        for p in _profiles.values()
    ]
