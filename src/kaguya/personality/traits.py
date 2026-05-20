"""Personality trait definitions and the TraitVector container.

Every trait is a float in [0.0, 1.0].  The ``TraitVector`` exposes helpers
to compute influence weights, blend two vectors, and serialize to dicts.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field, fields, asdict
from enum import Enum
from typing import Dict, Optional


class PersonalityTrait(str, Enum):
    """Enumeration of all recognised personality traits."""

    curiosity = "curiosity"
    kindness = "kindness"
    humor = "humor"
    confidence = "confidence"
    empathy = "empathy"
    creativity = "creativity"
    discipline = "discipline"
    introversion = "introversion"
    aggression = "aggression"
    sensitivity = "sensitivity"


# Default midpoint values for a balanced personality
_DEFAULTS: Dict[str, float] = {t.value: 0.5 for t in PersonalityTrait}


@dataclass
class TraitVector:
    """A point in personality-trait space.

    Each field is a float clamped to [0.0, 1.0].
    """

    curiosity: float = 0.5
    kindness: float = 0.5
    humor: float = 0.5
    confidence: float = 0.5
    empathy: float = 0.5
    creativity: float = 0.5
    discipline: float = 0.5
    introversion: float = 0.5
    aggression: float = 0.5
    sensitivity: float = 0.5

    def __post_init__(self) -> None:
        """Clamp every trait to [0, 1]."""
        for f in fields(self):
            val = getattr(self, f.name)
            setattr(self, f.name, max(0.0, min(1.0, float(val))))

    # ------------------------------------------------------------------
    # Access helpers
    # ------------------------------------------------------------------

    def get(self, trait: str | PersonalityTrait) -> float:
        """Return the value of a single trait by name or enum."""
        key = trait.value if isinstance(trait, PersonalityTrait) else trait
        if not hasattr(self, key):
            raise KeyError(f"Unknown trait: {key}")
        return getattr(self, key)

    def set(self, trait: str | PersonalityTrait, value: float) -> None:
        """Set a single trait, clamped."""
        key = trait.value if isinstance(trait, PersonalityTrait) else trait
        if not hasattr(self, key):
            raise KeyError(f"Unknown trait: {key}")
        setattr(self, key, max(0.0, min(1.0, float(value))))

    def as_dict(self) -> Dict[str, float]:
        """Return a plain dict mapping trait name → value."""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    # ------------------------------------------------------------------
    # Influence helpers
    # ------------------------------------------------------------------

    def influence_weight(self, trait: str | PersonalityTrait, *, baseline: float = 0.5) -> float:
        """Return a signed weight showing how far *trait* deviates from *baseline*.

        Positive means the trait is above baseline; negative means below.
        Useful for deciding how strongly a trait should push a response modifier.
        """
        value = self.get(trait)
        return value - baseline

    def dominant_traits(self, top_n: int = 3) -> list[tuple[str, float]]:
        """Return the *top_n* strongest traits sorted descending."""
        d = self.as_dict()
        return sorted(d.items(), key=lambda kv: kv[1], reverse=True)[:top_n]

    def weakest_traits(self, top_n: int = 3) -> list[tuple[str, float]]:
        """Return the *top_n* weakest traits sorted ascending."""
        d = self.as_dict()
        return sorted(d.items(), key=lambda kv: kv[1])[:top_n]

    # ------------------------------------------------------------------
    # Math / blending
    # ------------------------------------------------------------------

    def blend(self, other: "TraitVector", weight: float = 0.5) -> "TraitVector":
        """Return a new TraitVector that is *weight* of *other* and (1-weight) of self."""
        weight = max(0.0, min(1.0, weight))
        blended: Dict[str, float] = {}
        for f in fields(self):
            a = getattr(self, f.name)
            b = getattr(other, f.name)
            blended[f.name] = a * (1 - weight) + b * weight
        return TraitVector(**blended)

    def distance(self, other: "TraitVector") -> float:
        """Euclidean distance between two trait vectors."""
        total = 0.0
        for f in fields(self):
            diff = getattr(self, f.name) - getattr(other, f.name)
            total += diff * diff
        return math.sqrt(total)

    def nudge(self, trait: str | PersonalityTrait, delta: float) -> "TraitVector":
        """Return a copy with *trait* moved by *delta* (clamped)."""
        clone = copy.deepcopy(self)
        clone.set(trait, clone.get(trait) + delta)
        return clone

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, float]:
        return self.as_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "TraitVector":
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)
