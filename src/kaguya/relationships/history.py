"""Interaction history tracking for relationships."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InteractionRecord:
    """A single interaction with a user.

    Attributes:
        timestamp: Unix timestamp.
        summary: Short description of the interaction.
        sentiment: -1.0 (negative) to +1.0 (positive).
        event_type: Tag such as "chat", "compliment", "question".
        metadata: Extra key-value data.
    """

    timestamp: float = field(default_factory=time.time)
    summary: str = ""
    sentiment: float = 0.0
    event_type: str = "chat"
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "summary": self.summary,
            "sentiment": round(self.sentiment, 4),
            "event_type": self.event_type,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "InteractionRecord":
        return cls(
            timestamp=data.get("timestamp", time.time()),
            summary=data.get("summary", ""),
            sentiment=data.get("sentiment", 0.0),
            event_type=data.get("event_type", "chat"),
            metadata=data.get("metadata", {}),
        )


class InteractionHistory:
    """Ordered log of interactions with a single user.

    Maintains a rolling window to prevent unbounded memory growth.
    """

    def __init__(self, max_records: int = 1000) -> None:
        self._records: List[InteractionRecord] = []
        self._max = max_records

    def add(self, record: InteractionRecord) -> None:
        """Append an interaction record."""
        self._records.append(record)
        if len(self._records) > self._max:
            self._records = self._records[-self._max:]

    def add_interaction(
        self,
        summary: str = "",
        sentiment: float = 0.0,
        event_type: str = "chat",
        metadata: Optional[Dict[str, str]] = None,
    ) -> InteractionRecord:
        """Convenience method to create and add a record."""
        record = InteractionRecord(
            summary=summary,
            sentiment=sentiment,
            event_type=event_type,
            metadata=metadata or {},
        )
        self.add(record)
        return record

    @property
    def records(self) -> List[InteractionRecord]:
        """All records (oldest first)."""
        return list(self._records)

    def recent(self, n: int = 10) -> List[InteractionRecord]:
        """Return the *n* most recent records."""
        return self._records[-n:]

    def average_sentiment(self, window: int = 20) -> float:
        """Compute average sentiment over the last *window* interactions."""
        recent = self._records[-window:] if self._records else []
        if not recent:
            return 0.0
        return sum(r.sentiment for r in recent) / len(recent)

    def count_by_type(self) -> Dict[str, int]:
        """Count interactions by event type."""
        counts: Dict[str, int] = {}
        for r in self._records:
            counts[r.event_type] = counts.get(r.event_type, 0) + 1
        return counts

    def to_dicts(self) -> List[Dict]:
        """Serialize all records."""
        return [r.to_dict() for r in self._records]

    @classmethod
    def from_dicts(cls, data: List[Dict], max_records: int = 1000) -> "InteractionHistory":
        history = cls(max_records=max_records)
        for d in data:
            history.add(InteractionRecord.from_dict(d))
        return history

    def __len__(self) -> int:
        return len(self._records)
