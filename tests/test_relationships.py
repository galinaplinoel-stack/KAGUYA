"""Tests for relationship system."""
import pytest
from kaguya.relationships.manager import RelationshipManager


class TestRelationshipManager:
    def setup_method(self):
        self.manager = RelationshipManager()

    def test_new_relationship(self):
        rel = self.manager.get_relationship("user_1")
        assert rel.trust == 0.5  # Default
        assert rel.familiarity == 0.0
        assert rel.interaction_count == 0

    def test_positive_interaction(self):
        self.manager.record_interaction("user_1", sentiment=0.8)
        rel = self.manager.get_relationship("user_1")
        assert rel.trust > 0.5
        assert rel.familiarity > 0.0
        assert rel.interaction_count == 1

    def test_negative_interaction(self):
        self.manager.record_interaction("user_1", sentiment=-0.8)
        rel = self.manager.get_relationship("user_1")
        assert rel.trust < 0.5

    def test_multiple_interactions(self):
        for _ in range(10):
            self.manager.record_interaction("user_1", sentiment=0.6)
        rel = self.manager.get_relationship("user_1")
        assert rel.interaction_count == 10
        assert rel.trust > 0.7

    def test_separate_users(self):
        self.manager.record_interaction("alice", sentiment=0.8)
        self.manager.record_interaction("bob", sentiment=-0.8)
        alice = self.manager.get_relationship("alice")
        bob = self.manager.get_relationship("bob")
        assert alice.trust > bob.trust

    def test_get_all_relationships(self):
        self.manager.record_interaction("alice", sentiment=0.5)
        self.manager.record_interaction("bob", sentiment=0.3)
        all_rels = self.manager.get_all_relationships()
        assert len(all_rels) == 2
