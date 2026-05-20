"""Memory data models."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class MemoryEntry:
    """A single memory unit.

    Attributes:
        id: Unique identifier
        content: The actual memory text
        memory_type: Type of memory (fact, event, emotion, interaction)
        importance: How important this memory is (0.0-1.0)
        emotional_valence: Emotional charge (-1.0 to 1.0)
        emotional_intensity: How emotionally charged (0.0-1.0)
        tags: Categorical tags for filtering
        source: Where this memory came from (user_id, system, etc.)
        access_count: How many times this memory was recalled
        last_accessed: When this memory was last retrieved
        created_at: When this memory was created
        metadata: Extra key-value data
    """

    id: str = ""
    content: str = ""
    memory_type: str = "fact"  # fact, event, emotion, interaction
    importance: float = 0.5
    emotional_valence: float = 0.0  # -1 negative, +1 positive
    emotional_intensity: float = 0.0
    tags: list[str] = field(default_factory=list)
    source: str = ""
    access_count: int = 0
    last_accessed: float = 0.0
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "emotional_valence": self.emotional_valence,
            "emotional_intensity": self.emotional_intensity,
            "tags": self.tags,
            "source": self.source,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> MemoryEntry:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ConversationTurn:
    """A single turn in a conversation.

    Attributes:
        id: Unique identifier
        conversation_id: Which conversation this belongs to
        role: Who said this (user, assistant, system)
        content: What was said
        emotion_at_time: Emotional state during this turn
        sentiment: Sentiment score (-1.0 to 1.0)
        timestamp: When this was said
        metadata: Extra data
    """

    id: str = ""
    conversation_id: str = ""
    role: str = "user"
    content: str = ""
    emotion_at_time: str = ""
    sentiment: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "emotion_at_time": self.emotion_at_time,
            "sentiment": self.sentiment,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
