"""Memory Retrieval — personality-influenced memory search and context building."""
from __future__ import annotations

from typing import Dict, List, Optional

from kaguya.memory.models import MemoryEntry
from kaguya.memory.memory import MemoryManager


class MemoryRetrieval:
    """Advanced memory retrieval with personality bias and context building.

    This class provides higher-level memory operations:
    - Context-aware retrieval for conversations
    - Emotional memory filtering
    - Personality-biased memory ranking
    - Memory summary generation

    Usage:
        retrieval = MemoryRetrieval(memory_manager)
        context = retrieval.build_context("Tell me about cats", traits)
    """

    def __init__(self, memory_manager: MemoryManager) -> None:
        self.memory = memory_manager

    def build_context(
        self,
        query: str,
        personality_traits: Optional[Dict[str, float]] = None,
        current_emotion: Optional[str] = None,
        max_tokens: int = 500,
    ) -> str:
        """Build a memory context string for LLM injection.

        Retrieves relevant memories and formats them as context
        that can be added to an LLM prompt.

        Args:
            query: Current conversation topic/query
            personality_traits: For bias calculation
            current_emotion: Current emotional state (affects retrieval)
            max_tokens: Approximate token limit for context

        Returns:
            Formatted memory context string
        """
        # Retrieve relevant memories
        memories = self.memory.retrieve(
            query=query,
            top_k=5,
            personality_traits=personality_traits,
        )

        if not memories:
            return ""

        # Format as context
        lines = ["[Relevant Memories]"]
        total_chars = 0
        char_limit = max_tokens * 4  # rough token-to-char ratio

        for mem in memories:
            line = f"- [{mem.memory_type}] {mem.content}"
            if total_chars + len(line) > char_limit:
                break
            lines.append(line)
            total_chars += len(line)

        return "\n".join(lines)

    def get_emotional_context(
        self,
        personality_traits: Dict[str, float],
        top_k: int = 3,
    ) -> str:
        """Get emotionally relevant memories for the current state.

        Emotional personalities retrieve more emotional memories.
        """
        emotional_memories = self.memory.get_emotional_memories(top_k=top_k)

        if not emotional_memories:
            return ""

        lines = ["[Emotional Memories]"]
        for mem in emotional_memories:
            valence = "positive" if mem.emotional_valence > 0 else "negative"
            lines.append(f"- [{valence}] {mem.content}")

        return "\n".join(lines)

    def get_social_context(
        self,
        user_id: str,
        top_k: int = 3,
    ) -> str:
        """Get memories about a specific user."""
        memories = self.memory.retrieve(
            query=user_id,
            top_k=top_k,
            memory_type="interaction",
        )

        if not memories:
            return ""

        lines = [f"[Memories about {user_id}]"]
        for mem in memories:
            lines.append(f"- {mem.content}")

        return "\n".join(lines)

    def summarize_memories(
        self,
        personality_traits: Optional[Dict[str, float]] = None,
    ) -> str:
        """Generate a summary of important memories."""
        important = self.memory.get_important_memories(top_k=10)
        emotional = self.memory.get_emotional_memories(top_k=5)

        if not important and not emotional:
            return "No significant memories yet."

        lines = ["[Memory Summary]"]

        if important:
            lines.append("Important memories:")
            for mem in important[:5]:
                lines.append(f"- {mem.content}")

        if emotional:
            lines.append("Emotionally significant:")
            for mem in emotional[:3]:
                valence = "positive" if mem.emotional_valence > 0 else "negative"
                lines.append(f"- [{valence}] {mem.content}")

        return "\n".join(lines)
