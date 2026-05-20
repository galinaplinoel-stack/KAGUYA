"""How emotions affect response generation.

Provides concrete modifiers that the response-middleware layer can
blend into the LLM prompt to reflect the character's current mood.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from kaguya.emotion.states import EmotionType, MoodState


@dataclass
class EmotionInfluence:
    """Modifiers derived from the current emotional state.

    All values are in [0.0, 1.0] except ``sentiment_bias`` which ranges
    from -1.0 (negative) to +1.0 (positive).
    """

    sentiment_bias: float = 0.0   # -1 negative ↔ +1 positive
    verbosity_modifier: float = 0.0  # -1 much shorter ↔ +1 much longer
    energy_modifier: float = 0.0     # -1 low energy ↔ +1 high energy
    warmth_modifier: float = 0.0     # -1 cold ↔ +1 warm
    humor_modifier: float = 0.0      # -1 serious ↔ +1 playful
    formality_modifier: float = 0.0  # -1 very casual ↔ +1 very formal
    expressiveness: float = 0.5      # 0 stoic ↔ 1 very expressive

    def blend_with(self, other: "EmotionInfluence", weight: float = 0.5) -> "EmotionInfluence":
        """Blend two influences together (weight = how much of *other*)."""
        w = max(0.0, min(1.0, weight))
        return EmotionInfluence(
            sentiment_bias=self.sentiment_bias * (1 - w) + other.sentiment_bias * w,
            verbosity_modifier=self.verbosity_modifier * (1 - w) + other.verbosity_modifier * w,
            energy_modifier=self.energy_modifier * (1 - w) + other.energy_modifier * w,
            warmth_modifier=self.warmth_modifier * (1 - w) + other.warmth_modifier * w,
            humor_modifier=self.humor_modifier * (1 - w) + other.humor_modifier * w,
            formality_modifier=self.formality_modifier * (1 - w) + other.formality_modifier * w,
            expressiveness=self.expressiveness * (1 - w) + other.expressiveness * w,
        )

    def to_prompt_snippet(self) -> str:
        """Convert modifiers into an LLM instruction."""
        parts: list[str] = []

        if self.sentiment_bias > 0.2:
            parts.append("Your mood is positive; lean into optimism.")
        elif self.sentiment_bias < -0.2:
            parts.append("Your mood is low; allow some melancholy or edge in your tone.")

        if self.energy_modifier > 0.2:
            parts.append("You feel energized; be dynamic and lively.")
        elif self.energy_modifier < -0.2:
            parts.append("You feel drained; be measured and slow-paced.")

        if self.warmth_modifier > 0.2:
            parts.append("You feel affectionate; be extra warm and caring.")
        elif self.warmth_modifier < -0.2:
            parts.append("You feel distant; be more reserved.")

        if self.humor_modifier > 0.2:
            parts.append("You're in a playful mood; include humor.")
        elif self.humor_modifier < -0.2:
            parts.append("You're not in the mood for jokes.")

        if self.expressiveness > 0.7:
            parts.append("Express your emotions vividly.")
        elif self.expressiveness < 0.3:
            parts.append("Keep your emotional expression subdued.")

        return " ".join(parts)

    def to_dict(self) -> Dict[str, float]:
        return {
            "sentiment_bias": round(self.sentiment_bias, 4),
            "verbosity_modifier": round(self.verbosity_modifier, 4),
            "energy_modifier": round(self.energy_modifier, 4),
            "warmth_modifier": round(self.warmth_modifier, 4),
            "humor_modifier": round(self.humor_modifier, 4),
            "formality_modifier": round(self.formality_modifier, 4),
            "expressiveness": round(self.expressiveness, 4),
        }


def compute_influence(mood: MoodState) -> EmotionInfluence:
    """Compute ``EmotionInfluence`` from a ``MoodState``.

    The primary emotion sets the base direction; intensity scales the
    magnitude; valence/arousal fine-tune the modifiers.
    """
    intensity = mood.intensity
    valence = mood.valence  # -1 to +1
    arousal = mood.arousal  # 0 to 1

    # Sentiment bias directly from valence
    sentiment_bias = valence * intensity

    # Energy from arousal
    energy_modifier = (arousal - 0.5) * 2 * intensity  # -1 to +1

    # Warmth: positive valence + moderate arousal = warm
    warmth_modifier = valence * 0.7 + (0.5 - arousal) * 0.3
    warmth_modifier *= intensity

    # Emotion-specific tweaks
    humor_modifier = 0.0
    formality_modifier = 0.0

    if mood.primary_emotion == EmotionType.joy:
        humor_modifier = 0.3 * intensity
        warmth_modifier += 0.2 * intensity
    elif mood.primary_emotion == EmotionType.sadness:
        humor_modifier = -0.3 * intensity
        formality_modifier = 0.1 * intensity
    elif mood.primary_emotion == EmotionType.anger:
        formality_modifier = -0.2 * intensity
        warmth_modifier -= 0.3 * intensity
    elif mood.primary_emotion == EmotionType.fear:
        formality_modifier = 0.1 * intensity
        humor_modifier = -0.4 * intensity
    elif mood.primary_emotion == EmotionType.surprise:
        energy_modifier += 0.2 * intensity
    elif mood.primary_emotion == EmotionType.disgust:
        warmth_modifier -= 0.4 * intensity
        humor_modifier = -0.3 * intensity
    elif mood.primary_emotion == EmotionType.trust:
        warmth_modifier += 0.3 * intensity
        formality_modifier = 0.1 * intensity
    elif mood.primary_emotion == EmotionType.anticipation:
        energy_modifier += 0.2 * intensity
        humor_modifier = 0.1 * intensity

    expressiveness = 0.3 + intensity * 0.7  # higher intensity → more expressive

    return EmotionInfluence(
        sentiment_bias=_clamp(sentiment_bias, -1.0, 1.0),
        verbosity_modifier=_clamp(energy_modifier * 0.5, -1.0, 1.0),
        energy_modifier=_clamp(energy_modifier, -1.0, 1.0),
        warmth_modifier=_clamp(warmth_modifier, -1.0, 1.0),
        humor_modifier=_clamp(humor_modifier, -1.0, 1.0),
        formality_modifier=_clamp(formality_modifier, -1.0, 1.0),
        expressiveness=_clamp(expressiveness, 0.0, 1.0),
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))
