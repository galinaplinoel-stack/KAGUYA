"""Conversation Memory — persistent conversation tracking with memory formation."""
from __future__ import annotations

import uuid
import time
from typing import Dict, List, Optional

from kaguya.memory.models import ConversationTurn, MemoryEntry
from kaguya.memory.memory import MemoryManager


class ConversationMemory:
    """Tracks conversations and automatically forms memories from them.

    This system:
    1. Records every conversation turn
    2. Periodically summarizes conversations into long-term memories
    3. Links memories to conversations for traceability
    4. Provides conversation history retrieval

    Usage:
        cm = ConversationMemory(memory_manager)
        cm.add_turn("conv_1", "user", "I love cats!")
        cm.add_turn("conv_1", "assistant", "Cats are wonderful!")
        cm.summarize_conversation("conv_1")  # Forms long-term memory
    """

    def __init__(
        self,
        memory_manager: MemoryManager,
        auto_summarize_threshold: int = 10,
    ) -> None:
        self._conversations: Dict[str, List[ConversationTurn]] = {}
        self._memory = memory_manager
        self._auto_summarize_threshold = auto_summarize_threshold

    def add_turn(
        self,
        conversation_id: str,
        role: str,
        content: str,
        emotion: str = "",
        sentiment: float = 0.0,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ConversationTurn:
        """Add a turn to a conversation.

        Args:
            conversation_id: Which conversation
            role: user, assistant, or system
            content: What was said
            emotion: Emotional state at this turn
            sentiment: Sentiment score (-1 to 1)
            metadata: Extra data

        Returns:
            The created ConversationTurn
        """
        turn_id = str(uuid.uuid4())[:8]
        turn = ConversationTurn(
            id=turn_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            emotion_at_time=emotion,
            sentiment=sentiment,
            metadata=metadata or {},
        )

        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].append(turn)

        # Auto-summarize if threshold reached
        if len(self._conversations[conversation_id]) >= self._auto_summarize_threshold:
            self.summarize_conversation(conversation_id)

        return turn

    def get_conversation(
        self, conversation_id: str, last_n: int = 20
    ) -> List[ConversationTurn]:
        """Get recent turns from a conversation."""
        turns = self._conversations.get(conversation_id, [])
        return turns[-last_n:]

    def get_all_conversations(self) -> Dict[str, int]:
        """Get all conversation IDs and their turn counts."""
        return {cid: len(turns) for cid, turns in self._conversations.items()}

    def summarize_conversation(
        self, conversation_id: str, keep_turns: bool = True
    ) -> Optional[MemoryEntry]:
        """Summarize a conversation into a long-term memory.

        Args:
            conversation_id: Which conversation to summarize
            keep_turns: Whether to keep the raw turns after summarizing

        Returns:
            The created MemoryEntry, or None if no turns
        """
        turns = self._conversations.get(conversation_id, [])
        if not turns:
            return None

        # Build summary
        user_msgs = [t.content for t in turns if t.role == "user"]
        assistant_msgs = [t.content for t in turns if t.role == "assistant"]

        # Calculate average sentiment
        sentiments = [t.sentiment for t in turns if t.sentiment != 0]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        # Determine emotional tone
        emotions = [t.emotion_at_time for t in turns if t.emotion_at_time]
        dominant_emotion = max(set(emotions), key=emotions.count) if emotions else "neutral"

        # Create summary content
        summary_parts = [f"Conversation {conversation_id}:"]
        if user_msgs:
            summary_parts.append(f"User discussed: {'. '.join(user_msgs[:5])}")
        if assistant_msgs:
            summary_parts.append(f"Topics covered: {'. '.join(assistant_msgs[:3])}")

        summary = " ".join(summary_parts)

        # Determine importance based on length and sentiment
        importance = min(1.0, len(turns) * 0.05 + abs(avg_sentiment) * 0.3)

        # Store as memory
        memory = self._memory.store(
            content=summary,
            memory_type="interaction",
            importance=importance,
            emotional_valence=avg_sentiment,
            emotional_intensity=abs(avg_sentiment),
            tags=["conversation", conversation_id],
            source=conversation_id,
        )

        # Optionally clear raw turns
        if not keep_turns:
            self._conversations[conversation_id] = []

        return memory

    def summarize_all(self) -> List[MemoryEntry]:
        """Summarize all active conversations."""
        summaries = []
        for cid in list(self._conversations.keys()):
            summary = self.summarize_conversation(cid)
            if summary:
                summaries.append(summary)
        return summaries

    def to_dict(self) -> Dict:
        """Serialize all conversations."""
        return {
            cid: [t.to_dict() for t in turns]
            for cid, turns in self._conversations.items()
        }

    @classmethod
    def from_dict(
        cls, data: Dict, memory_manager: MemoryManager
    ) -> ConversationMemory:
        """Restore from serialized dict."""
        cm = cls(memory_manager)
        for cid, turns_data in data.items():
            cm._conversations[cid] = [
                ConversationTurn(**t) for t in turns_data
            ]
        return cm
