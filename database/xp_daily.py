"""Per-day, per-(player, guild) guild-XP gains. Aggregated at insert time."""

from datetime import date
from uuid import UUID

from asyncpg import Pool


async def add_xp(pool: Pool, uuid: UUID, guild_uuid: UUID, gained: int) -> None:
    """Bump `(uuid, today, guild_uuid).xp_gained` by `gained`. No-op when ≤ 0."""
    if gained <= 0:
        return
    await pool.execute(
        "INSERT INTO player_xp_daily (uuid, guild_uuid, xp_gained)"
        " VALUES ($1, $2, $3)"
        " ON CONFLICT (uuid, day, guild_uuid) DO UPDATE"
        "   SET xp_gained = player_xp_daily.xp_gained + EXCLUDED.xp_gained",
        uuid,
        guild_uuid,
        gained,
    )


async def daily_for_player(pool: Pool, uuid: UUID, since: date) -> dict[date, int]:
    """Per-day total XP gain for one player (across every guild) since `since`."""
    rows = await pool.fetch(
        "SELECT day, SUM(xp_gained)::BIGINT FROM player_xp_daily"
        " WHERE uuid = $1 AND day >= $2 GROUP BY day ORDER BY day",
        uuid,
        since,
    )
    return {row[0]: row[1] for row in rows}


async def daily_for_guild(pool: Pool, guild_uuid: UUID, since: date) -> dict[date, int]:
    """Per-day total XP contributed to `guild_uuid` since `since`."""
    rows = await pool.fetch(
        "SELECT day, SUM(xp_gained)::BIGINT FROM player_xp_daily"
        " WHERE guild_uuid = $1 AND day >= $2 GROUP BY day ORDER BY day",
        guild_uuid,
        since,
    )
    return {row[0]: row[1] for row in rows}


async def top_players_by_xp(
    pool: Pool,
    since: date,
    limit: int = 10,
    guild_uuid: UUID | None = None,
) -> list[tuple[UUID, str, int]]:
    """Top players by XP gained in [since, today] window, optionally guild-scoped."""
    rows = await pool.fetch(
        "SELECT p.uuid, p.username, SUM(x.xp_gained)::BIGINT AS total"
        " FROM player_xp_daily x JOIN players p ON p.uuid = x.uuid"
        " WHERE x.day >= $1"
        " AND ($2::UUID IS NULL OR x.guild_uuid = $2)"
        " GROUP BY p.uuid, p.username ORDER BY total DESC LIMIT $3",
        since,
        guild_uuid,
        limit,
    )
    return [(row[0], row[1], row[2]) for row in rows]


async def top_guilds_by_xp(
    pool: Pool, since: date, limit: int = 10
) -> list[tuple[UUID, str, int]]:
    """Top guilds by XP gained in [since, today]. Attribution is at-the-time."""
    rows = await pool.fetch(
        "SELECT g.uuid, g.name, SUM(x.xp_gained)::BIGINT AS total"
        " FROM player_xp_daily x"
        " JOIN guild_names g ON g.uuid = x.guild_uuid"
        " WHERE x.day >= $1"
        " GROUP BY g.uuid, g.name ORDER BY total DESC LIMIT $2",
        since,
        limit,
    )
    return [(row[0], row[1], row[2]) for row in rows]
