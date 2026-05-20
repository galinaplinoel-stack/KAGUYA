"""VTuber Character example — set up a personality-driven VTuber character."""
from kaguya.personality.presets import get_preset, list_presets
from kaguya.emotion.engine import EmotionalStateEngine
from kaguya.relationships.manager import RelationshipManager
from kaguya.middleware.response_modifier import ResponseModifier


def main():
    print("Available presets:", list_presets())

    # Create a tsundere VTuber character
    profile = get_preset("tsundere", name="Kaguya")

    emotion = EmotionalStateEngine(profile)
    relationships = RelationshipManager()
    modifier = ResponseModifier(profile, emotion, relationships)

    # Simulate VTuber stream interactions
    viewers = ["viewer_001", "viewer_002", "viewer_003"]

    # Viewer 001: regular, nice
    for _ in range(5):
        relationships.record_interaction("viewer_001", sentiment=0.7, emotion="joy")

    # Viewer 002: new viewer
    relationships.record_interaction("viewer_002", sentiment=0.3)

    # Viewer 003: troll
    for _ in range(3):
        relationships.record_interaction("viewer_003", sentiment=-0.5, emotion="anger")

    # Trigger emotion from stream event
    emotion.process_event("donation received", intensity=0.8)

    # Generate different prompts for different viewers
    for viewer in viewers:
        prompt = modifier.modify_prompt(
            base_prompt="You are a VTuber streaming on Twitch.",
            user_id=viewer,
        )
        rel = relationships.get_relationship(viewer)
        print(f"\n=== Prompt for {viewer} ===")
        print(f"Trust: {rel.trust:.0%} | Familiarity: {rel.familiarity:.0%}")
        print(f"Prompt preview: {prompt[:200]}...")


if __name__ == "__main__":
    main()
