"""Tests for personality trait system."""
import pytest
from kaguya.personality.traits import TraitVector


class TestTraitVector:
    def test_default_traits(self):
        t = TraitVector()
        assert 0.0 <= t.curiosity <= 1.0
        assert 0.0 <= t.kindness <= 1.0

    def test_custom_traits(self):
        t = TraitVector(curiosity=0.9, kindness=0.1)
        assert t.curiosity == 0.9
        assert t.kindness == 0.1

    def test_to_dict(self):
        t = TraitVector()
        d = t.to_dict()
        assert isinstance(d, dict)
        assert "curiosity" in d
        assert "empathy" in d

    def test_clamp_values(self):
        t = TraitVector(curiosity=1.5, kindness=-0.5)
        # Values should be clamped or validated
        assert t.curiosity <= 1.0
        assert t.kindness >= 0.0

    def test_influence_weight(self):
        t = TraitVector(humor=0.9, empathy=0.1)
        assert t.influence_weight("humor") > t.influence_weight("empathy")
