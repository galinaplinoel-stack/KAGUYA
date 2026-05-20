"""Communication style derived from personality traits.

``CommunicationStyle`` converts raw trait values into concrete modifiers
that the response-modifier middleware can plug into prompt templates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from kaguya.personality.traits import TraitVector


@dataclass
class ResponseModifier:
    """Concrete style knobs consumed by the prompt builder.

    All values are floats in [0.0, 1.0] unless noted.
    """

    verbosity: float = 0.5       # 0 = terse, 1 = verbose
    formality: float = 0.5       # 0 = casual, 1 = formal
    humor_level: float = 0.5     # 0 = serious, 1 = comedic
    emotional_expression: float = 0.5  # 0 = stoic, 1 = expressive
    assertiveness: float = 0.5   # 0 = passive, 1 = assertive
    warmth: float = 0.5          # 0 = cold, 1 = warm
    creativity_in_output: float = 0.5  # 0 = literal, 1 = creative/metaphorical
    pace: float = 0.5            # 0 = slow/measured, 1 = rapid/energetic

    def to_prompt_snippet(self) -> str:
        """Generate a natural-language instruction snippet for an LLM system prompt."""
        parts: list[str] = []

        if self.verbosity < 0.3:
            parts.append("Keep responses very concise and to the point.")
        elif self.verbosity > 0.7:
            parts.append("Provide detailed, thorough responses.")

        if self.formality < 0.3:
            parts.append("Use a casual, relaxed tone.")
        elif self.formality > 0.7:
            parts.append("Maintain a formal, professional tone.")

        if self.humor_level > 0.6:
            parts.append("Include humor, wit, and playful language when appropriate.")
        elif self.humor_level < 0.2:
            parts.append("Avoid jokes; stay serious and focused.")

        if self.emotional_expression > 0.6:
            parts.append("Express emotions openly and use expressive language.")
        elif self.emotional_expression < 0.3:
            parts.append("Remain composed and emotionally restrained.")

        if self.warmth > 0.6:
            parts.append("Be warm, caring, and supportive.")
        elif self.warmth < 0.3:
            parts.append("Maintain emotional distance; be businesslike.")

        if self.assertiveness > 0.7:
            parts.append("Be direct and confident in your statements.")
        elif self.assertiveness < 0.3:
            parts.append("Be tentative; use hedging language.")

        if self.creativity_in_output > 0.6:
            parts.append("Use metaphors, analogies, and creative language.")

        if self.pace > 0.7:
            parts.append("Keep the energy high and dynamic.")
        elif self.pace < 0.3:
            parts.append("Use a slow, deliberate pace.")

        return " ".join(parts)

    def to_dict(self) -> Dict[str, float]:
        return {
            "verbosity": self.verbosity,
            "formality": self.formality,
            "humor_level": self.humor_level,
            "emotional_expression": self.emotional_expression,
            "assertiveness": self.assertiveness,
            "warmth": self.warmth,
            "creativity_in_output": self.creativity_in_output,
            "pace": self.pace,
        }


class CommunicationStyle:
    """Derives a ``ResponseModifier`` from a ``TraitVector``.

    Mapping rules (examples):
    - verbosity ← creativity + (1 - introversion)
    - formality ← discipline + (1 - humor)
    - humor_level ← humor directly
    - warmth ← kindness + empathy
    - assertiveness ← confidence + aggression
    """

    @staticmethod
    def from_traits(traits: TraitVector) -> ResponseModifier:
        """Compute style modifiers from a trait vector."""
        verbosity = _clamp(
            traits.creativity * 0.5 + (1 - traits.introversion) * 0.5
        )
        formality = _clamp(
            traits.discipline * 0.6 + (1 - traits.humor) * 0.4
        )
        humor_level = traits.humor
        emotional_expression = _clamp(
            traits.sensitivity * 0.5 + traits.empathy * 0.3 + traits.humor * 0.2
        )
        assertiveness = _clamp(
            traits.confidence * 0.6 + traits.aggression * 0.4
        )
        warmth = _clamp(
            traits.kindness * 0.5 + traits.empathy * 0.5
        )
        creativity = traits.creativity
        pace = _clamp(
            (1 - traits.introversion) * 0.4 + traits.curiosity * 0.3 + traits.humor * 0.3
        )

        return ResponseModifier(
            verbosity=verbosity,
            formality=formality,
            humor_level=humor_level,
            emotional_expression=emotional_expression,
            assertiveness=assertiveness,
            warmth=warmth,
            creativity_in_output=creativity,
            pace=pace,
        )


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))
