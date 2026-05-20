"""Tests for personality evolution."""
import pytest
from kaguya.personality.traits import TraitVector
from kaguya.evolution.engine import PersonalityEvolution, EvolutionConfig


class TestPersonalityEvolution:
    def setup_method(self):
        self.traits = TraitVector(kindness=0.5, humor=0.5, empathy=0.5)
        self.config = EvolutionConfig(learning_rate=0.05, max_change_per_interaction=0.1)
        self.evolution = PersonalityEvolution(self.traits, self.config)

    def test_positive_evolution(self):
        initial = self.traits.kindness
        self.evolution.evolve(
            interaction_sentiment=1.0,
            emotional_intensity=0.8,
            reinforced_traits={"kindness": 1.0},
        )
        assert self.traits.kindness > initial

    def test_negative_evolution(self):
        initial = self.traits.kindness
        self.evolution.evolve(
            interaction_sentiment=-1.0,
            emotional_intensity=0.8,
            reinforced_traits={"kindness": 1.0},
        )
        assert self.traits.kindness < initial

    def test_evolution_bounds(self):
        self.traits.kindness = 0.01
        self.evolution.evolve(
            interaction_sentiment=-1.0,
            emotional_intensity=1.0,
            reinforced_traits={"kindness": 1.0},
        )
        assert self.traits.kindness >= 0.0

    def test_history_tracking(self):
        self.evolution.evolve(1.0, 0.5, {"kindness": 1.0})
        self.evolution.evolve(0.5, 0.3, {"humor": 1.0})
        assert len(self.evolution.history) == 2

    def test_evolution_summary(self):
        self.evolution.evolve(1.0, 0.5, {"kindness": 1.0})
        summary = self.evolution.get_evolution_summary()
        assert "total_interactions" in summary
        assert "current_traits" in summary
