"""Context Builder — constructs personality-aware context for LLM calls."""
from __future__ import annotations

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class PersonalityContext:
    """Complete personality context for an LLM interaction."""
    system_prompt_addition: str
    trait_summary: dict[str, float]
    emotional_state: dict
    relationship_context: Optional[dict] = None
    behavior_instructions: list[str] = field(default_factory=list)


class ContextBuilder:
    """Builds comprehensive personality context for AI interactions.

    Aggregates data from personality, emotion, and relationship systems
    into a structured context that can be injected into LLM calls.
    """

    def __init__(
        self,
        profile=None,
        emotion_engine=None,
        relationship_manager=None,
    ) -> None:
        self.profile = profile
        self.emotion = emotion_engine
        self.relationships = relationship_manager

    def build_context(
        self,
        user_id: Optional[str] = None,
        include_history: bool = False,
    ) -> PersonalityContext:
        """Build complete personality context.

        Args:
            user_id: Optional user for relationship context
            include_history: Whether to include interaction history

        Returns:
            PersonalityContext with all personality data
        """
        trait_summary = {}
        behavior_instructions = []

        if self.profile:
            trait_summary = self.profile.traits.to_dict()
            behavior_instructions = self._get_behavior_instructions()

        emotional_state = {}
        if self.emotion:
            state = self.emotion.current_state
            emotional_state = {
                "emotion": state.primary_emotion.value,
                "intensity": state.intensity,
                "valence": state.valence,
                "arousal": state.arousal,
                "tone": self.emotion.get_tone(),
            }

        relationship_context = None
        if user_id and self.relationships:
            rel = self.relationships.get_relationship(user_id)
            if rel:
                relationship_context = {
                    "trust": rel.trust,
                    "familiarity": rel.familiarity,
                    "affinity": rel.affinity,
                    "respect": rel.respect,
                    "interaction_count": rel.interaction_count,
                }

        return PersonalityContext(
            system_prompt_addition=self._generate_prompt_addition(),
            trait_summary=trait_summary,
            emotional_state=emotional_state,
            relationship_context=relationship_context,
            behavior_instructions=behavior_instructions,
        )

    def _get_behavior_instructions(self) -> list[str]:
        """Get behavioral instructions based on personality."""
        if not self.profile:
            return []

        instructions = []
        traits = self.profile.traits.to_dict()

        if traits.get("humor", 0) > 0.7:
            instructions.append("Use humor and wit in responses")
        if traits.get("empathy", 0) > 0.7:
            instructions.append("Show strong emotional understanding")
        if traits.get("curiosity", 0) > 0.7:
            instructions.append("Ask follow-up questions, show interest")
        if traits.get("confidence", 0) > 0.7:
            instructions.append("Be assertive and decisive")
        if traits.get("introversion", 0) > 0.7:
            instructions.append("Keep responses measured, avoid over-sharing")

        return instructions

    def _generate_prompt_addition(self) -> str:
        """Generate the full prompt addition string."""
        parts = []

        if self.profile:
            parts.append(f"You are {self.profile.name}.")
            top_traits = sorted(
                self.profile.traits.to_dict().items(),
                key=lambda x: x[1],
                reverse=True,
            )[:3]
            trait_desc = ", ".join(f"{k} ({v:.0%})" for k, v in top_traits)
            parts.append(f"Your strongest traits: {trait_desc}.")

        if self.emotion:
            state = self.emotion.current_state
            parts.append(
                f"Currently feeling {state.primary_emotion.value} "
                f"at {state.intensity:.0%} intensity."
            )

        return " ".join(parts)
