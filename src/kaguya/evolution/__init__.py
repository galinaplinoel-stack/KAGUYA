"""Personality evolution system — traits change over time."""
from kaguya.evolution.engine import PersonalityEvolution
from kaguya.evolution.reinforcement import BehavioralReinforcement
from kaguya.evolution.conditioning import EmotionalConditioning

__all__ = ["PersonalityEvolution", "BehavioralReinforcement", "EmotionalConditioning"]
