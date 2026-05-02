"""Per-day deltas for player globalData counters (``player_stats_daily``)."""

from datetime import date
from uuid import UUID

from asyncpg import Pool

# Columns present in both player_stats_daily and player_global_stats.
DELTA_COLS: tuple[str, ...] = (
    "total_level",
    "completed_quests",
    "total_dungeons",
    "total_raids",
    "playtime_hours",
    "content_completion",
    "mobs_killed",
    "chests_found",
    "world_events",
    "lootruns",
    "wars",
    "caves",
    "pvp_kills",
    "pvp_deaths",
)


async def add_delta(
    pool: Pool, uuid: UUID, guild_uuid: UUID, delta: dict[str, int]
) -> None:
    """Accumulate ``delta`` into today's row for ``(uuid, guild_uuid)``."""
    if not delta:
        return
    vals = [delta.get(col, 0) for col in DELTA_COLS]
    await pool.execute(
        "INSERT INTO player_stats_daily"
        "  (uuid, guild_uuid, total_level, completed_quests, total_dungeons,"
        "   total_raids, playtime_hours, content_completion, mobs_killed,"
        "   chests_found, world_events, lootruns, wars, caves, pvp_kills, pvp_deaths)"
        " VALUES"
        "   ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)"
        " ON CONFLICT (uuid, day, guild_uuid) DO UPDATE SET"
        "   total_level = player_stats_daily.total_level + EXCLUDED.total_level,"
        "   completed_quests ="
        "     player_stats_daily.completed_quests + EXCLUDED.completed_quests,"
        "   total_dungeons ="
        "     player_stats_daily.total_dungeons + EXCLUDED.total_dungeons,"
        "   total_raids = player_stats_daily.total_raids + EXCLUDED.total_raids,"
        "   playtime_hours ="
        "     player_stats_daily.playtime_hours + EXCLUDED.playtime_hours,"
        "   content_completion ="
        "     player_stats_daily.content_completion + EXCLUDED.content_completion,"
        "   mobs_killed = player_stats_daily.mobs_killed + EXCLUDED.mobs_killed,"
        "   chests_found = player_stats_daily.chests_found + EXCLUDED.chests_found,"
        "   world_events = player_stats_daily.world_events + EXCLUDED.world_events,"
        "   lootruns = player_stats_daily.lootruns + EXCLUDED.lootruns,"
        "   wars = player_stats_daily.wars + EXCLUDED.wars,"
        "   caves = player_stats_daily.caves + EXCLUDED.caves,"
        "   pvp_kills = player_stats_daily.pvp_kills + EXCLUDED.pvp_kills,"
        "   pvp_deaths = player_stats_daily.pvp_deaths + EXCLUDED.pvp_deaths",
        uuid,
        guild_uuid,
        *vals,
    )


async def top_by_stat(
    pool: Pool, stat: str, since: date, limit: int = 25, guild_uuid: UUID | None = None
) -> list[tuple[UUID, str, int]]:
    """Top players by total ``stat`` gained since ``since``."""
    if stat not in DELTA_COLS:
        raise ValueError(f"Unknown daily stat: {stat!r}")
    sql = (
        f"SELECT p.uuid, p.username, SUM(s.{stat})::BIGINT AS total"  # noqa: S608
        f" FROM player_stats_daily s JOIN players p ON p.uuid = s.uuid"
        f" WHERE s.day >= $1"
        f" AND ($2::UUID IS NULL OR s.guild_uuid = $2)"
        f" GROUP BY p.uuid, p.username"
        f" HAVING SUM(s.{stat}) > 0"
        f" ORDER BY total DESC LIMIT $3"
    )
    rows = await pool.fetch(sql, since, guild_uuid, limit)
    return [(row[0], row[1], row[2]) for row in rows]
