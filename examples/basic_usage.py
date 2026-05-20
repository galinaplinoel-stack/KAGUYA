"""Basic KAGUYA usage — create a personality and modify responses."""
from kaguya.personality.traits import TraitVector
from kaguya.personality.profile import CharacterProfile
from kaguya.emotion.engine import EmotionalStateEngine
from kaguya.relationships.manager import RelationshipManager
from kaguya.middleware.response_modifier import ResponseModifier


def main():
    # 1. Create a personality
    traits = TraitVector(
        curiosity=0.8,
        kindness=0.9,
        humor=0.6,
        confidence=0.4,
        empathy=0.85,
        creativity=0.7,
        discipline=0.5,
        introversion=0.3,
        aggression=0.1,
        sensitivity=0.7,
    )
    profile = CharacterProfile(name="Luna", traits=traits)

    # 2. Initialize systems
    emotion = EmotionalStateEngine(profile)
    relationships = RelationshipManager()
    modifier = ResponseModifier(profile, emotion, relationships)

    # 3. Simulate some interactions
    emotion.process_event("received compliment", intensity=0.7)
    relationships.record_interaction("alice", sentiment=0.8, emotion="joy")
    relationships.record_interaction("alice", sentiment=0.5)

    # 4. Generate personality-enhanced prompt
    prompt = modifier.modify_prompt(
        base_prompt="You are a helpful AI assistant.",
        user_id="alice",
    )
    print("=== Enhanced Prompt ===")
    print(prompt)

    # 5. Check emotional state
    print(f"\nCurrent emotion: {emotion.current_state.primary_emotion.value}")
    print(f"Intensity: {emotion.current_state.intensity:.0%}")

    # 6. Check relationship
    rel = relationships.get_relationship("alice")
    print(f"\nRelationship with Alice:")
    print(f"  Trust: {rel.trust:.0%}")
    print(f"  Familiarity: {rel.familiarity:.0%}")
    print(f"  Affinity: {rel.affinity:.0%}")


if __name__ == "__main__":
    main()
