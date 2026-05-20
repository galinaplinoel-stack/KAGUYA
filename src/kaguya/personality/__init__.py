"""Personality subsystem — traits, profiles, communication style, presets."""

from kaguya.personality.traits import TraitVector, PersonalityTrait
from kaguya.personality.profile import CharacterProfile
from kaguya.personality.style import CommunicationStyle

__all__ = [
    "TraitVector",
    "PersonalityTrait",
    "CharacterProfile",
    "CommunicationStyle",
]
