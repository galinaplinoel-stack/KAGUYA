"""Response Modifier — shapes LLM output based on personality, emotion, and relationships."""
from __future__ import annotations

from typing import Optional

from kaguya.personality.profile import CharacterProfile
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

        # Communication style
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
        """Generate communication style directives."""
        style = self.profile.communication_style
        directives = ["[Communication Style]"]

        if style.formality > 0.7:
            directives.append("Use formal, professional language.")
        elif style.formality < 0.3:
            directives.append("Use casual, relaxed language.")

        if style.verbosity > 0.7:
            directives.append("Be detailed and thorough in responses.")
        elif style.verbosity < 0.3:
            directives.append("Be concise and to the point.")

        if style.humor_frequency > 0.7:
            directives.append("Include humor and wit frequently.")
        elif style.humor_frequency > 0.4:
            directives.append("Occasionally include light humor.")

        if style.emotional_expression > 0.7:
            directives.append("Express emotions openly and vividly.")
        elif style.emotional_expression < 0.3:
            directives.append("Maintain emotional composure.")

        return "\n".join(directives)

    def _build_emotion_directives(self) -> str:
        """Generate directives based on current emotional state."""
        state = self.emotion.current_state
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

        if rel.trust < 0.3:
            directives.append("Be cautious and guarded with this user.")
        elif rel.trust > 0.8:
            directives.append("This is a trusted user. Be open and warm.")

        if rel.familiarity < 0.2:
            directives.append("This user is new. Be welcoming but formal.")
        elif rel.familiarity > 0.7:
            directives.append("This is a well-known user. Be comfortable and familiar.")

        return "\n".join(directives)
