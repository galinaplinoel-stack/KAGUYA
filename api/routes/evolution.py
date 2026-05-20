"""Evolution routes — track personality changes over time."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from api.schemas import EvolutionResponse
from api.routes.personality import _profiles
from kaguya.evolution.engine import PersonalityEvolution

router = APIRouter()

_engines: dict[str, PersonalityEvolution] = {}


def _get_engine(profile_id: str) -> PersonalityEvolution:
    profile = _profiles.get(profile_id)
    if not profile:
        raise HTTPException(404, "Personality not found")
    if profile_id not in _engines:
        _engines[profile_id] = PersonalityEvolution(profile.traits)
    return _engines[profile_id]


@router.get("/{profile_id}", response_model=EvolutionResponse)
async def get_evolution(profile_id: str):
    """Get evolution history and current trait drifts."""
    engine = _get_engine(profile_id)
    summary = engine.get_evolution_summary()
    return EvolutionResponse(**summary)


@router.post("/{profile_id}/evolve")
async def trigger_evolution(
    profile_id: str,
    sentiment: float = 0.0,
    intensity: float = 0.5,
    traits: str = "kindness,empathy",
):
    """Manually trigger an evolution event."""
    engine = _get_engine(profile_id)
    reinforced = {t.strip(): 1.0 for t in traits.split(",")}
    events = engine.evolve(sentiment, intensity, reinforced)
    return {
        "events": [
            {"trait": e.trait, "old": e.old_value, "new": e.new_value, "cause": e.cause}
            for e in events
        ],
        "summary": engine.get_evolution_summary(),
    }
