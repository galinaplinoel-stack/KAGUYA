<div align="center">

```
██╗  ██╗ █████╗  ██████╗ ██╗   ██╗██╗   ██╗ █████╗
██║ ██╔╝██╔══██╗██╔════╝ ██║   ██║╚██╗ ██╔╝██╔══██╗
█████╔╝ ███████║██║  ███╗██║   ██║ ╚████╔╝ ███████║
██╔═██╗ ██╔══██║██║   ██║██║   ██║  ╚██╔╝  ██╔══██║
██║  ██╗██║  ██║╚██████╔╝╚██████╔╝   ██║   ██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝
```

**A Production-Grade AI Personality Engine**

*Give your AI a soul.*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)

</div>

---

## What is KAGUYA?

KAGUYA is a modular **Personality Operating Layer** for AI systems. It gives AI agents, chatbots, VTubers, NPCs, and digital companions:

- **Persistent Identity** — consistent personality across conversations
- **Emotional Intelligence** — real-time mood simulation with decay
- **Relationship Memory** — per-user trust, familiarity, and affinity tracking
- **Response Modification** — LLM output shaped by personality + emotion + relationships
- **Personality Evolution** — traits gradually change based on interactions

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    KAGUYA Engine                     │
├─────────────┬─────────────┬─────────────┬───────────┤
│ Personality │  Emotion    │ Relationship│ Evolution │
│   Core      │  Engine     │  System     │  Engine   │
├─────────────┴─────────────┴─────────────┴───────────┤
│              Response Modifier Middleware             │
├─────────────────────────────────────────────────────┤
│         Storage Layer (SQLite / PostgreSQL)          │
├─────────────────────────────────────────────────────┤
│           REST API  │  WebSocket  │  Dashboard      │
└─────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install
pip install kaguya

# Or with Docker
docker-compose up -d
```

### Basic Usage

```python
from kaguya.personality.traits import TraitVector
from kaguya.personality.profile import CharacterProfile
from kaguya.emotion.engine import EmotionalStateEngine
from kaguya.relationships.manager import RelationshipManager
from kaguya.middleware.response_modifier import ResponseModifier

# Create a personality
profile = CharacterProfile(
    name="Sakura",
    traits=TraitVector(
        kindness=0.9,
        humor=0.6,
        empathy=0.85,
        confidence=0.4,
        curiosity=0.7,
    ),
)

# Initialize systems
emotion = EmotionalStateEngine(profile)
relationships = RelationshipManager()
modifier = ResponseModifier(profile, emotion, relationships)

# Modify an LLM prompt based on personality
enhanced_prompt = modifier.modify_prompt(
    base_prompt="You are a helpful assistant.",
    user_id="user_123"
)
```

### Character Presets

```python
from kaguya.personality.presets import tsundere, kuudere, chaotic_gremlin

# Use a preset personality
profile = tsundere(name="Kaguya")
profile = kuudere(name="Ice Queen")
profile = chaotic_gremlin(name="Gremlin")
```

### REST API

```bash
# Start the server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Create personality
curl -X POST http://localhost:8000/personality \
  -H "Content-Type: application/json" \
  -d '{"name": "Kaguya", "traits": {"kindness": 0.8, "humor": 0.6}}'

# Get emotional state
curl http://localhost:8000/emotion/{personality_id}

# Chat with personality
curl -X POST http://localhost:8000/chat \
  -d '{"personality_id": "xxx", "user_id": "user_1", "message": "Hello!"}'
```

## Features

| Feature | Description |
|---------|-------------|
| 🎭 **Personality Traits** | 10+ traits with float precision (0.0-1.0) |
| 💜 **Emotion Engine** | Valence-Arousal model with decay and transitions |
| 💕 **Relationships** | Per-user trust, familiarity, affinity, respect |
| 🧠 **Memory Bias** | Personality-influenced memory retrieval |
| 📈 **Evolution** | Gradual trait changes from interactions |
| 🔧 **Response Modifier** | LLM prompt enhancement based on state |
| 🎨 **Character Presets** | tsundere, kuudere, chaotic_gremlin, and more |
| 🖥️ **Dashboard** | Futuristic dark-mode visualization |
| 🐳 **Docker** | One-command deployment |
| 🔌 **REST API** | Full CRUD + WebSocket streaming |

## Dashboard

Access at `http://localhost:8000/dashboard` after starting the server.

Features:
- Personality radar chart
- Real-time emotion gauge
- Relationship map
- Mood timeline
- Trait evolution graph

## Project Structure

```
kaguya/
├── src/kaguya/
│   ├── personality/    # Trait system, profiles, presets
│   ├── emotion/        # Emotional state engine
│   ├── relationships/  # Per-user relationship tracking
│   ├── evolution/      # Personality evolution over time
│   ├── middleware/      # Response modification
│   └── storage/        # Database layer
├── api/                # FastAPI REST API + WebSocket
├── dashboard/          # Web dashboard
├── examples/           # Usage examples
├── tests/              # Test suite
└── docs/               # Documentation
```

## Tech Stack

- **Python 3.10+**
- **FastAPI** — REST API + WebSocket
- **SQLAlchemy** — async ORM
- **SQLite / PostgreSQL** — storage
- **Docker** — deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for the AI character community**

*KAGUYA — Because AI deserves a personality.*

</div>
