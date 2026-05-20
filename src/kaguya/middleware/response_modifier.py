"""Response Modifier — shapes LLM output based on personality, emotion, and relationships."""
from __future__ import annotations

from typing import Optional

from kaguya.personality.profile import CharacterProfile
from kaguya.personality.style import CommunicationStyle
from kaguya.emotion.engine import EmotionalStateEngine
from kaguya.relationships.manager import RelationshipManager


class ResponseModifier:
    """Modifies LLM system prompts based on the full personality context.

    This is the core integration point — it takes personality traits,
    current emotional state, and relationship data to generate
    system prompt enhancements that make the AI respond in character.
    """

    def __init__(
        self,
        profile: CharacterProfile,
        emotion_engine: EmotionalStateEngine,
        relationship_manager: RelationshipManager,
    ) -> None:
        self.profile = profile
        self.emotion = emotion_engine
        self.relationships = relationship_manager

    def modify_prompt(
        self,
        base_prompt: str,
        user_id: Optional[str] = None,
    ) -> str:
        """Enhance a base system prompt with personality context.

        Args:
            base_prompt: The original system prompt
            user_id: Optional user ID for relationship-aware responses

        Returns:
            Enhanced prompt with personality, emotion, and relationship directives
        """
        sections = [base_prompt, "", "=== PERSONALITY CONTEXT ==="]

        # Personality traits
        sections.append(self._build_trait_directives())

        # Communication style (derived from traits)
        sections.append(self._build_style_directives())

        # Emotional state
        sections.append(self._build_emotion_directives())

        # Relationship context
        if user_id:
            rel_directives = self._build_relationship_directives(user_id)
            if rel_directives:
                sections.append(rel_directives)

        return "\n".join(sections)

    def _build_trait_directives(self) -> str:
        """Generate behavioral directives from personality traits."""
        traits = self.profile.traits.to_dict()
        directives = ["[Personality Traits]"]

        high = {k: v for k, v in traits.items() if v >= 0.7}
        mid = {k: v for k, v in traits.items() if 0.3 < v < 0.7}
        low = {k: v for k, v in traits.items() if v <= 0.3}

        if high:
            directives.append(f"Strong traits: {', '.join(high.keys())}. "
                            "Express these prominently in responses.")
        if mid:
            directives.append(f"Moderate traits: {', '.join(mid.keys())}. "
                            "Show these naturally when relevant.")
        if low:
            directives.append(f"Low traits: {', '.join(low.keys())}. "
                            "Minimize these behaviors.")

        return "\n".join(directives)

    def _build_style_directives(self) -> str:
        """Generate communication style directives from traits."""
        style = CommunicationStyle.from_traits(self.profile.traits)
        directives = ["[Communication Style]"]
        directives.append(style.to_prompt_snippet())
        return "\n".join(directives)

    def _build_emotion_directives(self) -> str:
        """Generate directives based on current emotional state."""
        state = self.emotion.state
        directives = [f"[Emotional State: {state.primary_emotion.value} "
                     f"(intensity: {state.intensity:.1%})]"]

        tone = self.emotion.get_tone()
        for aspect, value in tone.items():
            directives.append(f"- {aspect}: {value}")

        return "\n".join(directives)

    def _build_relationship_directives(self, user_id: str) -> str:
        """Generate relationship-aware directives."""
        rel = self.relationships.get_relationship(user_id)
        if not rel:
            return ""

        directives = ["[Relationship Context]"]
        directives.append(f"- Trust level: {rel.trust:.0%}")
        directives.append(f"- Familiarity: {rel.familiarity:.0%}")
        directives.append(f"- Affinity: {rel.affinity:.0%}")

        # Get behavior modifier from relationship
        behavior = self.relationships.get_behavior_modifier(user_id)
        behavior_prompt = behavior.to_prompt_snippet()
        if behavior_prompt:
            directives.append(behavior_prompt)

        return "\n".join(directives)
