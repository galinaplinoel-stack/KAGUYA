"""Memory Manager — stores, retrieves, and manages memories with personality bias."""
from __future__ import annotations

import uuid
import time
import math
from typing import Dict, List, Optional

from kaguya.memory.models import MemoryEntry


class MemoryManager:
    """Persistent memory system with personality-influenced retrieval.

    Memories are stored with emotional context and importance scores.
    Retrieval is influenced by personality traits:
    - Emotional personalities remember emotional events more strongly
    - Social personalities prioritize interpersonal memories
    - Anxious personalities prioritize threats/problems
    - Creative personalities remember novel experiences

    Usage:
        mm = MemoryManager()
        mm.store("User likes cats", memory_type="fact", importance=0.8)
        memories = mm.retrieve("pets", personality_traits=traits)
    """

    def __init__(self, max_memories: int = 10000) -> None:
        self._memories: Dict[str, MemoryEntry] = {}
        self._max_memories = max_memories
        self._access_log: List[str] = []

    def store(
        self,
        content: str,
        memory_type: str = "fact",
        importance: float = 0.5,
        emotional_valence: float = 0.0,
        emotional_intensity: float = 0.0,
        tags: Optional[List[str]] = None,
        source: str = "",
        metadata: Optional[Dict[str, str]] = None,
    ) -> MemoryEntry:
        """Store a new memory.

        Args:
            content: The memory text
            memory_type: Type (fact, event, emotion, interaction)
            importance: How important (0.0-1.0)
            emotional_valence: Emotional charge (-1 to 1)
            emotional_intensity: How emotional (0-1)
            tags: Categorical tags
            source: Where this came from
            metadata: Extra data

        Returns:
            The created MemoryEntry
        """
        memory_id = str(uuid.uuid4())[:8]
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            emotional_valence=emotional_valence,
            emotional_intensity=emotional_intensity,
            tags=tags or [],
            source=source,
            metadata=metadata or {},
        )
        self._memories[memory_id] = entry
        self._enforce_limit()
        return entry

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        personality_traits: Optional[Dict[str, float]] = None,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0,
    ) -> List[MemoryEntry]:
        """Retrieve memories relevant to a query, influenced by personality.

        Args:
            query: Search query (keywords)
            top_k: Number of memories to return
            personality_traits: Trait dict for bias calculation
            memory_type: Filter by type
            min_importance: Minimum importance threshold

        Returns:
            List of relevant MemoryEntry, sorted by relevance
        """
        candidates = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for entry in self._memories.values():
            # Filter by type and importance
            if memory_type and entry.memory_type != memory_type:
                continue
            if entry.importance < min_importance:
                continue

            # Calculate base relevance (keyword overlap)
            content_lower = entry.content.lower()
            content_words = set(content_lower.split())
            overlap = len(query_words & content_words)
            tag_overlap = len(query_words & set(t.lower() for t in entry.tags))

            if overlap == 0 and tag_overlap == 0:
                continue

            # Base score
            relevance = (overlap * 0.3 + tag_overlap * 0.2 + entry.importance * 0.3)

            # Apply personality bias
            if personality_traits:
                relevance *= self._personality_bias(entry, personality_traits)

            # Recency bonus (newer memories get slight boost)
            age_hours = (time.time() - entry.created_at) / 3600
            recency_bonus = max(0.0, 1.0 - (age_hours / 720))  # Decay over 30 days
            relevance += recency_bonus * 0.1

            # Frequency bonus (often-accessed memories get slight boost)
            frequency_bonus = min(0.1, entry.access_count * 0.01)
            relevance += frequency_bonus

            candidates.append((relevance, entry))

        # Sort by relevance, return top_k
        candidates.sort(key=lambda x: x[0], reverse=True)
        results = [entry for _, entry in candidates[:top_k]]

        # Update access counts
        for entry in results:
            entry.access_count += 1
            entry.last_accessed = time.time()
            self._access_log.append(entry.id)

        return results

    def _personality_bias(
        self, entry: MemoryEntry, traits: Dict[str, float]
    ) -> float:
        """Calculate personality-influenced bias for a memory.

        Different personality types weight memories differently:
        - High empathy/sensitivity → emotional memories weighted higher
        - High social (low introversion) → interpersonal memories weighted higher
        - High aggression → threat/negative memories weighted higher
        - High curiosity → novel/exploration memories weighted higher
        - High creativity → creative/novel memories weighted higher
        """
        bias = 1.0

        # Emotional bias: empathetic personalities remember emotions more
        empathy = traits.get("empathy", 0.5)
        sensitivity = traits.get("sensitivity", 0.5)
        if entry.emotional_intensity > 0.5:
            bias *= 1.0 + (empathy + sensitivity) * 0.3

        # Social bias: extroverted personalities remember social events
        introversion = traits.get("introversion", 0.5)
        if entry.memory_type == "interaction":
            bias *= 1.0 + (1 - introversion) * 0.4

        # Threat bias: aggressive/anxious personalities remember threats
        aggression = traits.get("aggression", 0.5)
        if entry.emotional_valence < -0.3:
            bias *= 1.0 + aggression * 0.3

        # Novelty bias: curious personalities remember new things
        curiosity = traits.get("curiosity", 0.5)
        if entry.memory_type == "event":
            bias *= 1.0 + curiosity * 0.3

        # Creative bias: creative personalities remember creative things
        creativity = traits.get("creativity", 0.5)
        if "creative" in entry.tags or "novel" in entry.tags:
            bias *= 1.0 + creativity * 0.3

        return bias

    def get_important_memories(
        self, top_k: int = 10
    ) -> List[MemoryEntry]:
        """Get the most important memories."""
        sorted_memories = sorted(
            self._memories.values(),
            key=lambda m: m.importance,
            reverse=True,
        )
        return sorted_memories[:top_k]

    def get_emotional_memories(
        self, top_k: int = 10
    ) -> List[MemoryEntry]:
        """Get the most emotionally charged memories."""
        sorted_memories = sorted(
            self._memories.values(),
            key=lambda m: m.emotional_intensity,
            reverse=True,
        )
        return sorted_memories[:top_k]

    def get_recent_memories(
        self, hours: float = 24, top_k: int = 10
    ) -> List[MemoryEntry]:
        """Get memories from the last N hours."""
        cutoff = time.time() - (hours * 3600)
        recent = [
            m for m in self._memories.values()
            if m.created_at > cutoff
        ]
        recent.sort(key=lambda m: m.created_at, reverse=True)
        return recent[:top_k]

    def forget(self, memory_id: str) -> bool:
        """Remove a memory."""
        if memory_id in self._memories:
            del self._memories[memory_id]
            return True
        return False

    def update_importance(self, memory_id: str, new_importance: float) -> bool:
        """Update a memory's importance."""
        if memory_id in self._memories:
            self._memories[memory_id].importance = max(0.0, min(1.0, new_importance))
            return True
        return False

    def get_stats(self) -> Dict:
        """Get memory statistics."""
        memories = list(self._memories.values())
        if not memories:
            return {"total": 0}

        return {
            "total": len(memories),
            "by_type": self._count_by_type(memories),
            "avg_importance": sum(m.importance for m in memories) / len(memories),
            "avg_emotional_intensity": sum(m.emotional_intensity for m in memories) / len(memories),
            "most_accessed": max(memories, key=lambda m: m.access_count).id if memories else None,
        }

    def _count_by_type(self, memories: List[MemoryEntry]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for m in memories:
            counts[m.memory_type] = counts.get(m.memory_type, 0) + 1
        return counts

    def _enforce_limit(self) -> None:
        """Remove least important memories if over limit."""
        if len(self._memories) <= self._max_memories:
            return

        # Sort by importance (ascending) and remove lowest
        sorted_memories = sorted(
            self._memories.items(),
            key=lambda x: x[1].importance,
        )
        to_remove = len(self._memories) - self._max_memories
        for i in range(to_remove):
            del self._memories[sorted_memories[i][0]]

    def to_dict(self) -> Dict:
        """Serialize all memories."""
        return {mid: m.to_dict() for mid, m in self._memories.items()}

    @classmethod
    def from_dict(cls, data: Dict, max_memories: int = 10000) -> MemoryManager:
        """Restore from serialized dict."""
        mm = cls(max_memories=max_memories)
        for mid, mdata in data.items():
            mm._memories[mid] = MemoryEntry.from_dict(mdata)
        return mm
