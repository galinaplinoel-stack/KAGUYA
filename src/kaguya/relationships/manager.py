"""Relationship manager — per-user relationship tracking and evolution.

Maintains a dictionary of ``RelationshipValues`` keyed by user ID, along
with per-user ``InteractionHistory`` instances.
"""

from __future__ import annotations

from typing import Dict, Optional

from kaguya.relationships.models import (
    RelationshipValues,
    BehaviorModifier,
    compute_behavior_modifier,
)
from kaguya.relationships.history import InteractionHistory, InteractionRecord


class RelationshipManager:
    """Manage relationships with multiple users.

    Usage::

        rm = RelationshipManager()
        rm.evolve("user_42", sentiment=0.7, event_type="compliment")
        modifier = rm.get_behavior_modifier("user_42")
    """

    def __init__(self, max_history: int = 1000) -> None:
        self._relationships: Dict[str, RelationshipValues] = {}
        self._histories: Dict[str, InteractionHistory] = {}
        self._max_history = max_history

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get_relationship(self, user_id: str) -> RelationshipValues:
        """Get the relationship values for a user. Creates defaults if new."""
        if user_id not in self._relationships:
            self._relationships[user_id] = RelationshipValues()
        return self._relationships[user_id]

    def set_relationship(self, user_id: str, values: RelationshipValues) -> None:
        """Directly set relationship values for a user."""
        self._relationships[user_id] = values

    def get_history(self, user_id: str) -> InteractionHistory:
        """Get the interaction history for a user."""
        if user_id not in self._histories:
            self._histories[user_id] = InteractionHistory(self._max_history)
        return self._histories[user_id]

    def get_behavior_modifier(self, user_id: str) -> BehaviorModifier:
        """Compute how the character should behave toward this user."""
        rel = self.get_relationship(user_id)
        return compute_behavior_modifier(rel)

    @property
    def user_ids(self) -> list[str]:
        """All tracked user IDs."""
        return list(self._relationships.keys())

    # ------------------------------------------------------------------
    # Evolution
    # ------------------------------------------------------------------

    def evolve(
        self,
        user_id: str,
        sentiment: float = 0.0,
        event_type: str = "chat",
        summary: str = "",
        metadata: Optional[Dict[str, str]] = None,
    ) -> RelationshipValues:
        """Update relationship based on an interaction.

        Args:
            user_id: The user involved.
            sentiment: How positive the interaction was (-1 to +1).
            event_type: Type of interaction.
            summary: Short text summary.
            metadata: Extra data.

        Returns:
            Updated ``RelationshipValues``.
        """
        rel = self.get_relationship(user_id)
        history = self.get_history(user_id)

        # Record the interaction
        history.add_interaction(
            summary=summary,
            sentiment=max(-1.0, min(1.0, sentiment)),
            event_type=event_type,
            metadata=metadata,
        )

        # Compute deltas
        positive = max(0.0, sentiment)
        negative = max(0.0, -sentiment)

        # Trust: grows slowly, drops fast
        if sentiment >= 0:
            rel.trust += positive * 0.02
        else:
            rel.trust -= negative * 0.05

        # Familiarity: always grows with interaction
        rel.familiarity += 0.01

        # Affinity: mirrors sentiment
        rel.affinity += sentiment * 0.03

        # Respect: grows with positive interactions, drops with negative
        rel.respect += sentiment * 0.02

        # Clamp
        rel.trust = max(0.0, min(1.0, rel.trust))
        rel.familiarity = max(0.0, min(1.0, rel.familiarity))
        rel.affinity = max(0.0, min(1.0, rel.affinity))
        rel.respect = max(0.0, min(1.0, rel.respect))

        self._relationships[user_id] = rel
        return rel

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict:
        """Serialize all relationships and histories."""
        data: Dict = {}
        for uid in self._relationships:
            data[uid] = {
                "values": self._relationships[uid].to_dict(),
                "history": self.get_history(uid).to_dicts(),
            }
        return data

    @classmethod
    def from_dict(cls, data: Dict, max_history: int = 1000) -> "RelationshipManager":
        """Restore from serialized dict."""
        rm = cls(max_history=max_history)
        for uid, entry in data.items():
            rm._relationships[uid] = RelationshipValues.from_dict(entry.get("values", {}))
            rm._histories[uid] = InteractionHistory.from_dicts(
                entry.get("history", []), max_records=max_history
            )
        return rm
