"""Chatbot Integration — connect KAGUYA to an OpenAI-compatible API.

This example shows how to use KAGUYA as middleware between
your application and any LLM API.
"""
import json
from kaguya.personality.traits import TraitVector
from kaguya.personality.profile import CharacterProfile
from kaguya.emotion.engine import EmotionalStateEngine
from kaguya.relationships.manager import RelationshipManager
from kaguya.middleware.response_modifier import ResponseModifier


class PersonalityChatbot:
    """A chatbot wrapper that applies KAGUYA personality to LLM calls."""

    def __init__(
        self,
        name: str = "Kaguya",
        base_prompt: str = "You are a helpful AI assistant.",
        api_key: str = "",
        api_base: str = "https://api.openai.com/v1",
        model: str = "gpt-4",
    ) -> None:
        self.base_prompt = base_prompt
        self.api_key = api_key
        self.api_base = api_base
        self.model = model

        # Initialize KAGUYA
        self.profile = CharacterProfile(
            name=name,
            traits=TraitVector(
                kindness=0.8,
                humor=0.5,
                empathy=0.7,
                curiosity=0.6,
            ),
        )
        self.emotion = EmotionalStateEngine(self.profile)
        self.relationships = RelationshipManager()
        self.modifier = ResponseModifier(
            self.profile, self.emotion, self.relationships
        )

    def chat(self, user_id: str, message: str) -> str:
        """Send a message with personality-enhanced context.

        In production, this would call the actual LLM API.
        Here we return the modified prompt as a demonstration.
        """
        # Enhance the system prompt with personality
        enhanced_prompt = self.modifier.modify_prompt(
            self.base_prompt, user_id=user_id,
        )

        # Record the interaction
        sentiment = self._analyze_sentiment(message)
        self.relationships.record_interaction(user_id, sentiment=sentiment)

        # In production, you would call the LLM here:
        # response = call_openai_api(
        #     system=enhanced_prompt,
        #     messages=[{"role": "user", "content": message}],
        #     model=self.model,
        #     api_key=self.api_key,
        #     api_base=self.api_base,
        # )

        return f"[Enhanced System Prompt]\n{enhanced_prompt}\n\n[User Message]\n{message}"

    def _analyze_sentiment(self, text: str) -> float:
        """Simple keyword-based sentiment analysis."""
        positive = ["thanks", "love", "great", "awesome", "good", "please"]
        negative = ["hate", "bad", "terrible", "awful", "stupid", "angry"]

        text_lower = text.lower()
        score = 0.0
        for word in positive:
            if word in text_lower:
                score += 0.2
        for word in negative:
            if word in text_lower:
                score -= 0.2
        return max(-1.0, min(1.0, score))


def main():
    bot = PersonalityChatbot(
        name="Kaguya",
        base_prompt="You are Kaguya, a friendly AI companion.",
    )

    # Simulate conversation
    result = bot.chat("user_1", "Hello! How are you today?")
    print(result)
    print("---")

    result = bot.chat("user_1", "Thanks for being so helpful!")
    print(result)


if __name__ == "__main__":
    main()
