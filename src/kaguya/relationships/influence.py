"""How relationships affect character behavior.

Provides utility functions to generate LLM prompt modifications based on
relationship depth and history.
"""

from __future__ import annotations

from typing import Dict

from kaguya.relationships.models import RelationshipValues, BehaviorModifier, compute_behavior_modifier
from kaguya.relationships.history import InteractionHistory


def generate_relationship_context(
    user_id: str,
    rel: RelationshipValues,
    history: InteractionHistory,
) -> str:
    """Build a natural-language context paragraph about the relationship.

    This is injected into the LLM system prompt so the character can
    behave consistently with its relationship to the user.
    """
    modifier = compute_behavior_modifier(rel)
    overall = rel.overall_score()

    parts: list[str] = []

    # Relationship level description
    if overall < 0.2:
        parts.append(f"You barely know this person (user: {user_id}). They are a stranger.")
    elif overall < 0.4:
        parts.append(f"This person (user: {user_id}) is an acquaintance. You're still getting to know them.")
    elif overall < 0.6:
        parts.append(f"This person (user: {user_id}) is a familiar friend. You're comfortable with them.")
    elif overall < 0.8:
        parts.append(f"This person (user: {user_id}) is a close friend. You trust them deeply.")
    else:
        parts.append(f"This person (user: {user_id}) is extremely close to you. You'd do almost anything for them.")

    # Trust details
    if rel.trust > 0.7:
        parts.append("You trust them with personal information.")
    elif rel.trust < 0.2:
        parts.append("You don't trust them yet; be cautious.")

    # Familiarity details
    if rel.familiarity > 0.7:
        parts.append("You know their quirks and preferences well.")
    elif rel.familiarity < 0.2:
        parts.append("You're still learning about them.")

    # Recent interaction summary
    recent = history.recent(5)
    if recent:
        avg_sentiment = history.average_sentiment(10)
        if avg_sentiment > 0.3:
            parts.append("Your recent interactions have been positive and enjoyable.")
        elif avg_sentiment < -0.3:
            parts.append("Your recent interactions have been tense or unpleasant.")
        else:
            parts.append("Your recent interactions have been neutral.")

        last = recent[-1]
        if last.summary:
            parts.append(f"Last interaction: {last.summary}")

    # Behavioral guidance from modifier
    behavior = modifier.to_prompt_snippet()
    if behavior:
        parts.append(behavior)

    return " ".join(parts)


def relationship_stage(rel: RelationshipValues) -> str:
    """Return a human-readable relationship stage label."""
    overall = rel.overall_score()
    if overall < 0.15:
        return "stranger"
    elif overall < 0.3:
        return "acquaintance"
    elif overall < 0.45:
        return "casual_friend"
    elif overall < 0.6:
        return "friend"
    elif overall < 0.75:
        return "close_friend"
    elif overall < 0.9:
        return "best_friend"
    else:
        return "soulmate"
