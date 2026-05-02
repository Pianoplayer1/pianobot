"""Player registry: every UUID we've ever observed in any tracked guild."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Pool


@dataclass(slots=True, frozen=True)
class Player:
    """One row of the `players` table."""

    uuid: UUID
    username: str
    first_seen_at: datetime
    last_seen_at: datetime


async def upsert(pool: Pool, uuid: UUID, username: str) -> None:
    """Register or refresh a player. Logs a rename if the username changed."""
    await pool.execute(
        "WITH prev AS ("
        "  SELECT username FROM players WHERE uuid = $1"
        "), upserted AS ("
        "  INSERT INTO players (uuid, username) VALUES ($1, $2)"
        "  ON CONFLICT (uuid) DO UPDATE"
        "    SET username = EXCLUDED.username, last_seen_at = NOW()"
        ")"
        " INSERT INTO player_username_history (uuid, old_username, new_username)"
        " SELECT $1, prev.username, $2 FROM prev WHERE prev.username <> $2",
        uuid,
        username,
    )


async def get_by_uuid(pool: Pool, uuid: UUID) -> Player | None:
    """Look up one player by uuid."""
    row = await pool.fetchrow(
        "SELECT uuid, username, first_seen_at, last_seen_at"
        " FROM players WHERE uuid = $1",
        uuid,
    )
    return Player(*row) if row else None


async def usernames_by_uuid(pool: Pool, uuids: list[UUID]) -> dict[UUID, str]:
    """Bulk uuid to current_username lookup. Missing uuids are absent from the map."""
    if not uuids:
        return {}
    rows = await pool.fetch(
        "SELECT uuid, username FROM players WHERE uuid = ANY($1)", uuids
    )
    return {row[0]: row[1] for row in rows}


async def resolve_username(pool: Pool, query: str) -> UUID | None:
    """Resolve username to uuid (case-insensitive). Current name beats history."""
    row = await pool.fetchrow(
        "SELECT uuid FROM players WHERE username ILIKE $1 LIMIT 1", query
    )
    if row:
        return UUID(str(row[0]))
    row = await pool.fetchrow(
        "SELECT uuid FROM player_username_history WHERE old_username ILIKE $1"
        " ORDER BY changed_at DESC LIMIT 1",
        query,
    )
    return UUID(str(row[0])) if row else None


@dataclass(slots=True, frozen=True)
class UsernameChange:
    """One entry in a player's rename log."""

    old_username: str
    new_username: str
    changed_at: datetime


async def username_history(pool: Pool, uuid: UUID) -> list[UsernameChange]:
    """Chronological list of username changes for one player (oldest to newest)."""
    rows = await pool.fetch(
        "SELECT old_username, new_username, changed_at"
        " FROM player_username_history WHERE uuid = $1 ORDER BY changed_at",
        uuid,
    )
    return [UsernameChange(*row) for row in rows]
