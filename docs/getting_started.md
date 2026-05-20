# Getting Started with KAGUYA

## Installation

### From PyPI (coming soon)
```bash
pip install kaguya
```

### From Source
```bash
git clone https://github.com/galinaplinoel-stack/KAGUYA.git
cd KAGUYA
pip install -e .
```

### Docker
```bash
docker-compose up -d
```

## Quick Start

### 1. Create a Personality
```python
from kaguya.personality.traits import TraitVector
from kaguya.personality.profile import CharacterProfile

profile = CharacterProfile(
    name="Sakura",
    traits=TraitVector(
        kindness=0.9,
        humor=0.6,
        empathy=0.85,
    ),
)
```

### 2. Add Emotional State
```python
from kaguya.emotion.engine import EmotionalStateEngine

emotion = EmotionalStateEngine(profile)
emotion.process_event("received gift", intensity=0.8)
print(emotion.current_state.primary_emotion)  # joy
```

### 3. Track Relationships
```python
from kaguya.relationships.manager import RelationshipManager

relationships = RelationshipManager()
relationships.record_interaction("user_1", sentiment=0.7)
rel = relationships.get_relationship("user_1")
print(f"Trust: {rel.trust:.0%}")
```

### 4. Modify LLM Responses
```python
from kaguya.middleware.response_modifier import ResponseModifier

modifier = ResponseModifier(profile, emotion, relationships)
enhanced = modifier.modify_prompt(
    base_prompt="You are a helpful assistant.",
    user_id="user_1",
)
print(enhanced)
```

### 5. Use Character Presets
```python
from kaguya.personality.presets import tsundere, kuudere, chaotic_gremlin

profile = tsundere(name="Kaguya")
profile = kuudere(name="Ice Queen")
profile = chaotic_gremlin(name="Gremlin")
```

### 6. Start the API Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:
- API docs: http://localhost:8000/docs
- Dashboard: http://localhost:8000/dashboard

## Environment Variables

```env
DATABASE_URL=sqlite+aiosqlite:///kaguya.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/kaguya
```

## Next Steps

- Read the [Architecture Guide](architecture.md)
- Check the [API Reference](api_reference.md)
- Look at the [examples/](../examples/) directory
- Run the test suite: `pytest tests/`
