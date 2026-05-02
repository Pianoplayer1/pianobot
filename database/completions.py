"""Raid and war completion logs and aggregate queries for leaderboards/graphs."""

from datetime import date, datetime
from uuid import UUID

from asyncpg import Pool


async def add_raid(pool: Pool, uuid: UUID, guild_uuid: UUID, raid_id: int) -> None:
    """Log one raid completion attributed to `guild_uuid`."""
    await pool.execute(
        "INSERT INTO raid_completions (uuid, guild_uuid, raid_id) VALUES ($1, $2, $3)",
        uuid,
        guild_uuid,
        raid_id,
    )


async def add_wars(pool: Pool, uuid: UUID, guild_uuid: UUID, count: int) -> None:
    """Log `count` war completions attributed to `guild_uuid`."""
    if count <= 0:
        return
    await pool.execute(
        "INSERT INTO war_completions (uuid, guild_uuid)"
        " SELECT $1, $2 FROM generate_series(1, $3)",
        uuid,
        guild_uuid,
        count,
    )


async def raid_counts_by_username(
    pool: Pool,
    start: datetime | None = None,
    end: datetime | None = None,
    raid_id: int | None = None,
    guild_uuid: UUID | None = None,
) -> dict[str, int]:
    """Map current-username to raid completions in the interval."""
    rows = await pool.fetch(
        "SELECT p.username, COUNT(*)"
        " FROM raid_completions l"
        " JOIN players p ON p.uuid = l.uuid"
        " WHERE ($1::TIMESTAMPTZ IS NULL OR l.completed_at >= $1)"
        "   AND ($2::TIMESTAMPTZ IS NULL OR l.completed_at < $2)"
        "   AND ($3::SMALLINT IS NULL OR l.raid_id = $3)"
        "   AND ($4::UUID IS NULL OR l.guild_uuid = $4)"
        " GROUP BY p.username",
        start,
        end,
        raid_id,
        guild_uuid,
    )
    return {row[0]: row[1] for row in rows}


async def war_counts_by_username(
    pool: Pool,
    start: datetime | None = None,
    end: datetime | None = None,
    guild_uuid: UUID | None = None,
) -> dict[str, int]:
    """Map current-username to war completions in the interval, optionally scoped."""
    rows = await pool.fetch(
        "SELECT p.username, COUNT(*)"
        " FROM war_completions l"
        " JOIN players p ON p.uuid = l.uuid"
        " WHERE ($1::TIMESTAMPTZ IS NULL OR l.completed_at >= $1)"
        "   AND ($2::TIMESTAMPTZ IS NULL OR l.completed_at < $2)"
        "   AND ($3::UUID IS NULL OR l.guild_uuid = $3)"
        " GROUP BY p.username",
        start,
        end,
        guild_uuid,
    )
    return {row[0]: row[1] for row in rows}


async def top_guilds_by_raids(
    pool: Pool, since: datetime, limit: int
) -> list[tuple[UUID, str, int]]:
    """Top guilds by raid completions since `since`. Returns (uuid, name, count)."""
    rows = await pool.fetch(
        "SELECT g.uuid, g.name, COUNT(*) AS c"
        " FROM raid_completions r JOIN guild_names g ON g.uuid = r.guild_uuid"
        " WHERE r.completed_at >= $1"
        " GROUP BY g.uuid, g.name ORDER BY c DESC LIMIT $2",
        since,
        limit,
    )
    return [(row[0], row[1], row[2]) for row in rows]


async def top_guilds_by_wars(
    pool: Pool, since: datetime, limit: int
) -> list[tuple[UUID, str, int]]:
    """Top guilds by war completions since `since`."""
    rows = await pool.fetch(
        "SELECT g.uuid, g.name, COUNT(*) AS c"
        " FROM war_completions w JOIN guild_names g ON g.uuid = w.guild_uuid"
        " WHERE w.completed_at >= $1"
        " GROUP BY g.uuid, g.name ORDER BY c DESC LIMIT $2",
        since,
        limit,
    )
    return [(row[0], row[1], row[2]) for row in rows]


async def top_players_by_raids(
    pool: Pool,
    since: datetime,
    limit: int,
    guild_uuid: UUID | None,
) -> list[tuple[UUID, str, int]]:
    """Top players by raid completions since `since`, optionally scoped to a guild."""
    rows = await pool.fetch(
        "SELECT p.uuid, p.username, COUNT(*) AS c"
        " FROM raid_completions r JOIN players p ON p.uuid = r.uuid"
        " WHERE r.completed_at >= $1"
        " AND ($2::UUID IS NULL OR r.guild_uuid = $2)"
        " GROUP BY p.uuid, p.username ORDER BY c DESC LIMIT $3",
        since,
        guild_uuid,
        limit,
    )
    return [(row[0], row[1], row[2]) for row in rows]


async def top_players_by_wars(
    pool: Pool,
    since: datetime,
    limit: int = 10,
    guild_uuid: UUID | None = None,
) -> list[tuple[UUID, str, int]]:
    """Top players by war completions since `since`, optionally scoped to a guild."""
    rows = await pool.fetch(
        "SELECT p.uuid, p.username, COUNT(*) AS c"
        " FROM war_completions w JOIN players p ON p.uuid = w.uuid"
        " WHERE w.completed_at >= $1"
        " AND ($2::UUID IS NULL OR w.guild_uuid = $2)"
        " GROUP BY p.uuid, p.username ORDER BY c DESC LIMIT $3",
        since,
        guild_uuid,
        limit,
    )
    return [(row[0], row[1], row[2]) for row in rows]


async def daily_raid_counts_for_guild(
    pool: Pool, guild_uuid: UUID, since: datetime
) -> dict[date, int]:
    """Per-day raid count for one guild since `since`."""
    rows = await pool.fetch(
        "SELECT completed_at::date AS d, COUNT(*)::INTEGER FROM raid_completions"
        " WHERE guild_uuid = $1 AND completed_at >= $2"
        " GROUP BY d ORDER BY d",
        guild_uuid,
        since,
    )
    return {row[0]: row[1] for row in rows}


async def daily_raid_counts_for_player(
    pool: Pool, uuid: UUID, since: datetime
) -> dict[date, int]:
    """Per-day raid count for one player since `since`."""
    rows = await pool.fetch(
        "SELECT completed_at::date AS d, COUNT(*)::INTEGER FROM raid_completions"
        " WHERE uuid = $1 AND completed_at >= $2"
        " GROUP BY d ORDER BY d",
        uuid,
        since,
    )
    return {row[0]: row[1] for row in rows}


async def daily_war_counts_for_guild(
    pool: Pool, guild_uuid: UUID, since: datetime
) -> dict[date, int]:
    """Per-day war count for one guild since `since`."""
    rows = await pool.fetch(
        "SELECT completed_at::date AS d, COUNT(*)::INTEGER FROM war_completions"
        " WHERE guild_uuid = $1 AND completed_at >= $2"
        " GROUP BY d ORDER BY d",
        guild_uuid,
        since,
    )
    return {row[0]: row[1] for row in rows}


async def daily_war_counts_for_player(
    pool: Pool, uuid: UUID, since: datetime
) -> dict[date, int]:
    """Per-day war count for one player since `since`."""
    rows = await pool.fetch(
        "SELECT completed_at::date AS d, COUNT(*)::INTEGER FROM war_completions"
        " WHERE uuid = $1 AND completed_at >= $2"
        " GROUP BY d ORDER BY d",
        uuid,
        since,
    )
    return {row[0]: row[1] for row in rows}
