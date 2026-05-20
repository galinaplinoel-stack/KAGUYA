"""Behavioral reinforcement — positive/negative feedback shapes traits."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReinforcementSignal:
    """A signal that reinforces or weakens a behavior pattern."""
    behavior: str
    valence: float  # -1.0 (punishment) to 1.0 (reward)
    intensity: float  # 0.0 to 1.0
    associated_traits: list[str]


# Default behavior-to-trait mappings
BEHAVIOR_TRAIT_MAP: dict[str, list[str]] = {
    "helpful_response": ["kindness", "empathy"],
    "joke_told": ["humor", "confidence"],
    "question_asked": ["curiosity"],
    "creative_solution": ["creativity"],
    "structured_plan": ["discipline"],
    "social_engagement": ["introversion"],  # negative = more extroverted
    "emotional_support": ["empathy", "sensitivity"],
    "bold_decision": ["confidence", "aggression"],
    "careful_analysis": ["discipline", "curiosity"],
}


class BehavioralReinforcement:
    """Processes behavioral feedback to generate trait reinforcement signals."""

    def __init__(
        self,
        custom_mappings: dict[str, list[str]] | None = None,
    ) -> None:
        self.mappings = {**BEHAVIOR_TRAIT_MAP}
        if custom_mappings:
            self.mappings.update(custom_mappings)

    def process_feedback(
        self,
        behavior: str,
        feedback_valence: float,
        intensity: float = 0.5,
    ) -> ReinforcementSignal:
        """Create a reinforcement signal from behavior feedback.

        Args:
            behavior: The behavior identifier
            feedback_valence: -1.0 (negative) to 1.0 (positive)
            intensity: Strength of the feedback

        Returns:
            ReinforcementSignal ready for evolution engine
        """
        traits = self.mappings.get(behavior, [])
        return ReinforcementSignal(
            behavior=behavior,
            valence=feedback_valence,
            intensity=min(1.0, max(0.0, intensity)),
            associated_traits=traits,
        )

    def extract_reinforcement(
        self,
        signal: ReinforcementSignal,
    ) -> dict[str, float]:
        """Convert a signal to trait reinforcement strengths.

        Returns:
            Dict of trait_name -> reinforcement_strength
        """
        return {
            trait: signal.valence * signal.intensity
            for trait in signal.associated_traits
        }
