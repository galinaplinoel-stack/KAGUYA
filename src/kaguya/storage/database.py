"""Async database engine — supports SQLite and PostgreSQL."""
from __future__ import annotations

import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from kaguya.storage.models import Base


class Database:
    """Async database manager supporting SQLite and PostgreSQL.

    Usage:
        db = Database("sqlite+aiosqlite:///kaguya.db")
        await db.initialize()
        async with db.session() as session:
            ...
    """

    def __init__(self, url: Optional[str] = None) -> None:
        self.url = url or os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:///kaguya.db",
        )
        self._engine = None
        self._session_factory = None

    async def initialize(self) -> None:
        """Create engine and initialize all tables."""
        kwargs = {"echo": False}

        # SQLite needs StaticPool for async
        if self.url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
            kwargs["poolclass"] = StaticPool

        self._engine = create_async_engine(self.url, **kwargs)
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close the database engine."""
        if self._engine:
            await self._engine.dispose()


# Module-level convenience
_default_db: Optional[Database] = None


def get_engine(url: Optional[str] = None) -> Database:
    """Get or create the default database instance."""
    global _default_db
    if _default_db is None:
        _default_db = Database(url)
    return _default_db


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Convenience: get a session from the default database."""
    db = get_engine()
    async for s in db.session():
        yield s
