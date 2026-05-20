"""Persistence helpers for saving/loading personality state to the database."""

from __future__ import annotations

import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kaguya.storage.models import PersonalityProfileRow
from kaguya.personality.profile import CharacterProfile
from kaguya.personality.traits import TraitVector


async def save_profile(session: AsyncSession, profile: CharacterProfile) -> None:
    """Insert or update a character profile in the database."""
    stmt = select(PersonalityProfileRow).where(
        PersonalityProfileRow.profile_id == profile.profile_id
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()

    data = profile.to_dict()
    traits_json = json.dumps(data["traits"])
    catchphrases_json = json.dumps(data["catchphrases"])
    quirks_json = json.dumps(data["quirks"])
    metadata_json = json.dumps(data["metadata"])

    if row is None:
        row = PersonalityProfileRow(
            profile_id=profile.profile_id,
            name=profile.name,
            traits=traits_json,
            backstory=profile.backstory,
            catchphrases=catchphrases_json,
            quirks=quirks_json,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            extra_metadata=metadata_json,
        )
        session.add(row)
    else:
        row.name = profile.name
        row.traits = traits_json
        row.backstory = profile.backstory
        row.catchphrases = catchphrases_json
        row.quirks = quirks_json
        row.updated_at = profile.updated_at
        row.extra_metadata = metadata_json

    await session.commit()


async def load_profile(session: AsyncSession, profile_id: str) -> Optional[CharacterProfile]:
    """Load a character profile by ID. Returns ``None`` if not found."""
    stmt = select(PersonalityProfileRow).where(
        PersonalityProfileRow.profile_id == profile_id
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        return None

    return CharacterProfile(
        name=row.name,
        traits=TraitVector.from_dict(json.loads(row.traits)),
        backstory=row.backstory or "",
        catchphrases=json.loads(row.catchphrases) if row.catchphrases else [],
        quirks=json.loads(row.quirks) if row.quirks else [],
        profile_id=row.profile_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        metadata=json.loads(row.extra_metadata) if row.extra_metadata else {},
    )


async def list_profiles(session: AsyncSession) -> list[CharacterProfile]:
    """Return all stored profiles."""
    stmt = select(PersonalityProfileRow)
    result = await session.execute(stmt)
    rows = result.scalars().all()
    profiles: list[CharacterProfile] = []
    for row in rows:
        profiles.append(
            CharacterProfile(
                name=row.name,
                traits=TraitVector.from_dict(json.loads(row.traits)),
                backstory=row.backstory or "",
                catchphrases=json.loads(row.catchphrases) if row.catchphrases else [],
                quirks=json.loads(row.quirks) if row.quirks else [],
                profile_id=row.profile_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
                metadata=json.loads(row.extra_metadata) if row.extra_metadata else {},
            )
        )
    return profiles


async def delete_profile(session: AsyncSession, profile_id: str) -> bool:
    """Delete a profile. Returns True if something was deleted."""
    stmt = select(PersonalityProfileRow).where(
        PersonalityProfileRow.profile_id == profile_id
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        return False
    await session.delete(row)
    await session.commit()
    return True
