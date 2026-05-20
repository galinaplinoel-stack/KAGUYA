"""FastAPI application — KAGUYA Personality Engine REST API."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from kaguya.storage.database import Database, get_engine
from kaguya.config import Settings

from api.routes import personality, emotion, relationships, evolution, chat
from api.websocket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize database on startup."""
    db = get_engine(Settings().database_url)
    await db.initialize()
    app.state.db = db
    yield
    await db.close()


app = FastAPI(
    title="KAGUYA — AI Personality Engine",
    description="Production-grade personality infrastructure for AI beings.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(personality.router, prefix="/personality", tags=["Personality"])
app.include_router(emotion.router, prefix="/emotion", tags=["Emotion"])
app.include_router(relationships.router, prefix="/relationships", tags=["Relationships"])
app.include_router(evolution.router, prefix="/evolution", tags=["Evolution"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])

# Serve dashboard static files
try:
    app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
except Exception:
    pass  # Dashboard not built yet


@app.get("/")
async def root():
    return {
        "name": "KAGUYA — AI Personality Engine",
        "version": "0.1.0",
        "docs": "/docs",
        "dashboard": "/dashboard",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
