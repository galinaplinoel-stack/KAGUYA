"""Personality Evolution Engine — gradual trait changes based on interactions."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from kaguya.personality.traits import TraitVector


@dataclass
class EvolutionEvent:
    """Record of a single trait change."""
    trait: str
    old_value: float
    new_value: float
    cause: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class EvolutionConfig:
    """Configuration for personality evolution."""
    learning_rate: float = 0.01
    max_change_per_interaction: float = 0.05
    decay_rate: float = 0.001
    min_trait_value: float = 0.0
    max_trait_value: float = 1.0


class PersonalityEvolution:
    """Manages gradual personality evolution over time.

    Traits shift based on interaction patterns, emotional experiences,
    and behavioral reinforcement. Changes are small and cumulative.
    """

    def __init__(
        self,
        traits: TraitVector,
        config: Optional[EvolutionConfig] = None,
    ) -> None:
        self.traits = traits
        self.config = config or EvolutionConfig()
        self.history: list[EvolutionEvent] = []
        self._interaction_count: int = 0

    def evolve(
        self,
        interaction_sentiment: float,
        emotional_intensity: float,
        reinforced_traits: dict[str, float],
    ) -> list[EvolutionEvent]:
        """Apply evolution based on a completed interaction.

        Args:
            interaction_sentiment: -1.0 (negative) to 1.0 (positive)
            emotional_intensity: 0.0 (calm) to 1.0 (intense)
            reinforced_traits: dict of trait_name -> reinforcement_strength

        Returns:
            List of evolution events that occurred.
        """
        self._interaction_count += 1
        events: list[EvolutionEvent] = []
        lr = self.config.learning_rate
        max_delta = self.config.max_change_per_interaction

        for trait_name, strength in reinforced_traits.items():
            if not hasattr(self.traits, trait_name):
                continue

            old_val = getattr(self.traits, trait_name)
            delta = lr * strength * interaction_sentiment * emotional_intensity
            delta = max(-max_delta, min(max_delta, delta))

            new_val = max(
                self.config.min_trait_value,
                min(self.config.max_trait_value, old_val + delta),
            )

            if abs(new_val - old_val) > 1e-6:
                setattr(self.traits, trait_name, new_val)
                event = EvolutionEvent(
                    trait=trait_name,
                    old_value=old_val,
                    new_value=new_val,
                    cause=f"reinforcement (sentiment={interaction_sentiment:.2f})",
                )
                self.history.append(event)
                events.append(event)

        return events

    def get_evolution_summary(self) -> dict:
        """Get summary of personality evolution."""
        trait_changes: dict[str, list[float]] = {}
        for event in self.history:
            trait_changes.setdefault(event.trait, []).append(
                event.new_value - event.old_value
            )

        return {
            "total_interactions": self._interaction_count,
            "total_events": len(self.history),
            "trait_drifts": {
                trait: sum(changes)
                for trait, changes in trait_changes.items()
            },
            "current_traits": self.traits.to_dict(),
        }

    def get_trait_history(self, trait_name: str) -> list[EvolutionEvent]:
        """Get evolution history for a specific trait."""
        return [e for e in self.history if e.trait == trait_name]
