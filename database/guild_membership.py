"""Current guild membership state and the append-only event log."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from asyncpg import Pool

EventType = Literal["join", "leave", "rank_change"]


@dataclass(slots=True, frozen=True)
class Membership:
    """One row of the `guild_memberships` table."""

    uuid: UUID
    guild_uuid: UUID
    rank: str
    joined_at: datetime
    contributed_xp: int


async def get(pool: Pool, uuid: UUID) -> Membership | None:
    """Current guild membership for one player (None if guildless / unknown)."""
    row = await pool.fetchrow(
        "SELECT uuid, guild_uuid, rank, joined_at, contributed_xp"
        " FROM guild_memberships WHERE uuid = $1",
        uuid,
    )
    return Membership(*row) if row else None


async def by_guild(pool: Pool, guild_uuid: UUID) -> list[Membership]:
    """Every player currently in `guild_uuid`."""
    rows = await pool.fetch(
        "SELECT uuid, guild_uuid, rank, joined_at, contributed_xp"
        " FROM guild_memberships WHERE guild_uuid = $1",
        guild_uuid,
    )
    return [Membership(*row) for row in rows]


async def by_guilds(
    pool: Pool, guild_uuids: list[UUID]
) -> dict[UUID, dict[UUID, Membership]]:
    """Group current memberships by guild. {guild_uuid: {player_uuid: Membership}}."""
    if not guild_uuids:
        return {}
    rows = await pool.fetch(
        "SELECT uuid, guild_uuid, rank, joined_at, contributed_xp"
        " FROM guild_memberships WHERE guild_uuid = ANY($1)",
        guild_uuids,
    )
    grouped: dict[UUID, dict[UUID, Membership]] = {gu: {} for gu in guild_uuids}
    for row in rows:
        m = Membership(*row)
        grouped.setdefault(m.guild_uuid, {})[m.uuid] = m
    return grouped


async def upsert(
    pool: Pool,
    uuid: UUID,
    guild_uuid: UUID,
    rank: str,
    joined_at: datetime,
    contributed_xp: int,
) -> None:
    """Set the player's current membership row, creating it if absent."""
    await pool.execute(
        "INSERT INTO guild_memberships"
        " (uuid, guild_uuid, rank, joined_at, contributed_xp)"
        " VALUES ($1, $2, $3, $4, $5)"
        " ON CONFLICT (uuid) DO UPDATE SET"
        "   guild_uuid = EXCLUDED.guild_uuid,"
        "   rank = EXCLUDED.rank,"
        "   joined_at = EXCLUDED.joined_at,"
        "   contributed_xp = EXCLUDED.contributed_xp",
        uuid,
        guild_uuid,
        rank,
        joined_at,
        contributed_xp,
    )


async def update_rank(pool: Pool, uuid: UUID, rank: str) -> None:
    """Rewrite just the rank cell."""
    await pool.execute(
        "UPDATE guild_memberships SET rank = $1 WHERE uuid = $2", rank, uuid
    )


async def update_xp(pool: Pool, uuid: UUID, xp: int) -> None:
    """Rewrite just the contributed_xp cell."""
    await pool.execute(
        "UPDATE guild_memberships SET contributed_xp = $1 WHERE uuid = $2", xp, uuid
    )


async def remove(pool: Pool, uuid: UUID) -> None:
    """Drop the player's membership row (they left the guild)."""
    await pool.execute("DELETE FROM guild_memberships WHERE uuid = $1", uuid)


async def record_event(
    pool: Pool,
    uuid: UUID,
    guild_uuid: UUID,
    event_type: EventType,
    *,
    old_rank: str | None = None,
    new_rank: str | None = None,
) -> None:
    """Append one row to guild_membership_events."""
    await pool.execute(
        "INSERT INTO guild_membership_events"
        " (uuid, guild_uuid, event_type, old_rank, new_rank)"
        " VALUES ($1, $2, $3, $4, $5)",
        uuid,
        guild_uuid,
        event_type,
        old_rank,
        new_rank,
    )


@dataclass(slots=True, frozen=True)
class MembershipEvent:
    """One row of the `guild_membership_events` table."""

    id: int
    uuid: UUID
    guild_uuid: UUID
    event_type: EventType
    old_rank: str | None
    new_rank: str | None
    occurred_at: datetime


async def events_for_player(pool: Pool, uuid: UUID) -> list[MembershipEvent]:
    """Chronological event log for one player (oldest to newest)."""
    rows = await pool.fetch(
        "SELECT id, uuid, guild_uuid, event_type, old_rank, new_rank, occurred_at"
        " FROM guild_membership_events WHERE uuid = $1 ORDER BY occurred_at",
        uuid,
    )
    return [MembershipEvent(*row) for row in rows]


async def events_for_guild(
    pool: Pool, guild_uuid: UUID, limit: int = 100
) -> list[MembershipEvent]:
    """Recent membership events for one guild (newest to oldest, capped at `limit`)."""
    rows = await pool.fetch(
        "SELECT id, uuid, guild_uuid, event_type, old_rank, new_rank, occurred_at"
        " FROM guild_membership_events WHERE guild_uuid = $1"
        " ORDER BY occurred_at DESC LIMIT $2",
        guild_uuid,
        limit,
    )
    return [MembershipEvent(*row) for row in rows]
