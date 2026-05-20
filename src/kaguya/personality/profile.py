"""CharacterProfile — a named personality with traits, backstory, and metadata."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from kaguya.personality.traits import TraitVector


@dataclass
class CharacterProfile:
    """Complete character definition combining traits with narrative metadata.

    Attributes:
        profile_id: Unique identifier (UUID string).
        name: Display name of the character.
        traits: The personality trait vector.
        backstory: Short narrative description.
        catchphrases: List of signature phrases.
        quirks: Behavioural quirks / mannerisms.
        created_at: ISO timestamp of creation.
        updated_at: ISO timestamp of last update.
        metadata: Arbitrary extra key-value pairs.
    """

    name: str
    traits: TraitVector = field(default_factory=TraitVector)
    backstory: str = ""
    catchphrases: list[str] = field(default_factory=list)
    quirks: list[str] = field(default_factory=list)
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, str] = field(default_factory=dict)

    def touch(self) -> None:
        """Bump ``updated_at`` to now."""
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        """Full serialisation."""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "traits": self.traits.to_dict(),
            "backstory": self.backstory,
            "catchphrases": self.catchphrases,
            "quirks": self.quirks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CharacterProfile":
        """Reconstruct from a dict (e.g. from DB or JSON)."""
        traits = TraitVector.from_dict(data.get("traits", {}))
        return cls(
            name=data["name"],
            traits=traits,
            backstory=data.get("backstory", ""),
            catchphrases=data.get("catchphrases", []),
            quirks=data.get("quirks", []),
            profile_id=data.get("profile_id", str(uuid.uuid4())),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            metadata=data.get("metadata", {}),
        )
