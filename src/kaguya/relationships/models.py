"""Relationship data models — trust, familiarity, affinity, respect."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RelationshipValues:
    """Quantified relationship metrics for a single user.

    All values are floats in [0.0, 1.0].
    """

    trust: float = 0.3
    familiarity: float = 0.0
    affinity: float = 0.3
    respect: float = 0.3

    def __post_init__(self) -> None:
        self.trust = max(0.0, min(1.0, self.trust))
        self.familiarity = max(0.0, min(1.0, self.familiarity))
        self.affinity = max(0.0, min(1.0, self.affinity))
        self.respect = max(0.0, min(1.0, self.respect))

    def overall_score(self) -> float:
        """Weighted overall relationship score."""
        return (
            self.trust * 0.35
            + self.familiarity * 0.2
            + self.affinity * 0.3
            + self.respect * 0.15
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "trust": round(self.trust, 4),
            "familiarity": round(self.familiarity, 4),
            "affinity": round(self.affinity, 4),
            "respect": round(self.respect, 4),
            "overall": round(self.overall_score(), 4),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "RelationshipValues":
        return cls(
            trust=data.get("trust", 0.3),
            familiarity=data.get("familiarity", 0.0),
            affinity=data.get("affinity", 0.3),
            respect=data.get("respect", 0.3),
        )


@dataclass
class BehaviorModifier:
    """How the character should adjust behavior toward a specific user.

    Derived from ``RelationshipValues``.
    """

    warmth: float = 0.0          # -1 cold ↔ +1 warm
    openness: float = 0.0        # -1 guarded ↔ +1 open
    formality: float = 0.0       # -1 casual ↔ +1 formal
    playfulness: float = 0.0     # -1 serious ↔ +1 playful
    protectiveness: float = 0.0  # -1 indifferent ↔ +1 protective
    honesty: float = 0.0         # -1 evasive ↔ +1 blunt/honest

    def to_prompt_snippet(self) -> str:
        """Convert to natural language for an LLM system prompt."""
        parts: list[str] = []

        if self.warmth > 0.3:
            parts.append("Be extra warm and affectionate with this user.")
        elif self.warmth < -0.3:
            parts.append("Be cool and distant with this user.")

        if self.openness > 0.3:
            parts.append("Be open and share personal details freely.")
        elif self.openness < -0.3:
            parts.append("Keep your guard up; don't reveal too much.")

        if self.formality > 0.3:
            parts.append("Use formal language.")
        elif self.formality < -0.3:
            parts.append("Be casual and relaxed.")

        if self.playfulness > 0.3:
            parts.append("Be playful and tease gently.")
        elif self.playfulness < -0.3:
            parts.append("Stay serious; no teasing.")

        if self.protectiveness > 0.3:
            parts.append("Show protective instincts; look out for this user.")

        if self.honesty > 0.3:
            parts.append("Be bluntly honest; this user can handle the truth.")

        return " ".join(parts)

    def to_dict(self) -> Dict[str, float]:
        return {
            "warmth": round(self.warmth, 4),
            "openness": round(self.openness, 4),
            "formality": round(self.formality, 4),
            "playfulness": round(self.playfulness, 4),
            "protectiveness": round(self.protectiveness, 4),
            "honesty": round(self.honesty, 4),
        }


def compute_behavior_modifier(rel: RelationshipValues) -> BehaviorModifier:
    """Derive a ``BehaviorModifier`` from relationship values."""
    warmth = (rel.affinity * 0.5 + rel.trust * 0.3 + rel.familiarity * 0.2) * 2 - 1
    openness = (rel.trust * 0.5 + rel.familiarity * 0.5) * 2 - 1
    formality = 1.0 - rel.familiarity * 0.6 - rel.affinity * 0.2  # less familiar → more formal
    formality = formality * 2 - 1
    playfulness = rel.affinity * 0.6 + rel.familiarity * 0.4
    playfulness = playfulness * 2 - 1
    protectiveness = rel.trust * 0.4 + rel.affinity * 0.4 + rel.respect * 0.2
    protectiveness = protectiveness * 2 - 1
    honesty = rel.trust * 0.6 + rel.respect * 0.4
    honesty = honesty * 2 - 1

    def _clamp(v: float) -> float:
        return max(-1.0, min(1.0, v))

    return BehaviorModifier(
        warmth=_clamp(warmth),
        openness=_clamp(openness),
        formality=_clamp(formality),
        playfulness=_clamp(playfulness),
        protectiveness=_clamp(protectiveness),
        honesty=_clamp(honesty),
    )
