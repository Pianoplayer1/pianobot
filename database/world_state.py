"""External-world reference tables: worlds, territories, generic player last-seen."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Pool


async def touch_players(pool: Pool, uuids: Iterable[UUID]) -> None:
    """Upsert `last_seen_at = NOW()` for every given player uuid."""
    uuid_list = list(uuids)
    if not uuid_list:
        return
    await pool.execute(
        "INSERT INTO player_last_seen (uuid)"
        " SELECT DISTINCT u FROM UNNEST($1::UUID[]) AS t(u)"
        " ON CONFLICT (uuid) DO UPDATE SET last_seen_at = NOW()",
        uuid_list,
    )


async def last_seen_map(pool: Pool, uuids: Iterable[UUID]) -> dict[UUID, datetime]:
    """Map uuid to last_seen_at for the subset of `uuids` we have data for."""
    uuid_list = list(uuids)
    if not uuid_list:
        return {}
    rows = await pool.fetch(
        "SELECT uuid, last_seen_at FROM player_last_seen WHERE uuid = ANY($1::UUID[])",
        uuid_list,
    )
    return {row[0]: row[1] for row in rows}


@dataclass(slots=True, frozen=True)
class World:
    """One Wynncraft world and the first time we saw it online."""

    name: str
    started_at: datetime


async def all_worlds(pool: Pool) -> list[World]:
    """Every world currently tracked as online."""
    rows = await pool.fetch("SELECT name, started_at FROM worlds ORDER BY name")
    return [World(*row) for row in rows]


async def sync_worlds(pool: Pool, online_now: set[str]) -> None:
    """Upsert new worlds, delete disappeared ones."""
    names = sorted(online_now)
    # Set-based reconciliation in SQL: insert missing, delete disappeared.
    await pool.execute(
        "WITH incoming AS ("
        "  SELECT DISTINCT w FROM UNNEST($1::TEXT[]) AS t(w)"
        "), ins AS ("
        "  INSERT INTO worlds (name)"
        "  SELECT i.w FROM incoming i"
        "  ON CONFLICT (name) DO NOTHING"
        ")"
        " DELETE FROM worlds"
        " WHERE NOT EXISTS (SELECT 1 FROM incoming i WHERE i.w = worlds.name)",
        names,
    )


@dataclass(slots=True, frozen=True)
class Territory:
    """One map territory with its current owning guild uuid (if any)."""

    name: str
    guild_uuid: UUID | None
    acquired: datetime


async def all_territories(pool: Pool) -> dict[str, Territory]:
    """Snapshot of the territories table keyed by territory name."""
    rows = await pool.fetch(
        "SELECT name, guild_uuid, acquired FROM territories ORDER BY name"
    )
    return {row[0]: Territory(row[0], row[1], row[2]) for row in rows}


async def add_territory(
    pool: Pool, name: str, guild_uuid: UUID | None, acquired: datetime
) -> None:
    """Insert a territory row; no-op if it already exists."""
    await pool.execute(
        "INSERT INTO territories (name, guild_uuid, acquired) VALUES ($1, $2, $3)"
        " ON CONFLICT (name) DO NOTHING",
        name,
        guild_uuid,
        acquired,
    )


async def update_territory(
    pool: Pool, name: str, guild_uuid: UUID | None, acquired: datetime
) -> None:
    """Update a territory's owning guild and acquired timestamp."""
    await pool.execute(
        "UPDATE territories SET guild_uuid = $1, acquired = $2 WHERE name = $3",
        guild_uuid,
        acquired,
        name,
    )


async def record_territory_ownership_change(
    pool: Pool,
    territory_name: str,
    old_guild_uuid: UUID | None,
    new_guild_uuid: UUID | None,
    acquired_at: datetime,
) -> None:
    """Append one ownership transition (initial capture uses old_guild_uuid NULL)."""
    await pool.execute(
        "INSERT INTO territory_ownership_events"
        " (territory_name, old_guild_uuid, new_guild_uuid, acquired_at)"
        " VALUES ($1, $2, $3, $4)",
        territory_name,
        old_guild_uuid,
        new_guild_uuid,
        acquired_at,
    )
