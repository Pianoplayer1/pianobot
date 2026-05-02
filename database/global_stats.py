"""Per-player snapshot of globalData fields from the guild endpoint."""

from uuid import UUID

from asyncpg import Pool

# All globalData numeric fields we capture
STAT_COLUMNS: tuple[str, ...] = (
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


async def upsert(pool: Pool, uuid: UUID, stats: dict[str, int | None]) -> None:
    """Upsert one player's globalData. Only non-None fields are written."""
    present = {k: v for k, v in stats.items() if v is not None and k in STAT_COLUMNS}
    if not present:
        await pool.execute(
            "INSERT INTO player_global_stats (uuid) VALUES ($1)"
            " ON CONFLICT (uuid) DO UPDATE SET updated_at = NOW()",
            uuid,
        )
        return

    columns = list(present.keys())
    insert_cols = ", ".join(columns)
    insert_placeholders = ", ".join(f"${i + 2}" for i in range(len(columns)))
    update_assignments = ", ".join(f"{c} = EXCLUDED.{c}" for c in columns)
    sql = (
        f"INSERT INTO player_global_stats (uuid, {insert_cols})"  # noqa: S608
        f" VALUES ($1, {insert_placeholders})"
        f" ON CONFLICT (uuid) DO UPDATE SET {update_assignments}, updated_at = NOW()"
    )
    await pool.execute(sql, uuid, *(present[c] for c in columns))


async def get(pool: Pool, uuid: UUID) -> dict[str, int | None] | None:
    """Return one player's stats as a {column: value} dict, or None if not found."""
    row = await pool.fetchrow(
        "SELECT "  # noqa: S608
        + ", ".join(STAT_COLUMNS)
        + " FROM player_global_stats WHERE uuid = $1",
        uuid,
    )
    if row is None:
        return None
    return dict(zip(STAT_COLUMNS, row, strict=True))


async def top_players_by_stat(
    pool: Pool, stat: str, limit: int = 25, guild_uuid: UUID | None = None
) -> list[tuple[UUID, str, int]]:
    """Top players by one globalData stat, optionally scoped to a guild."""
    if stat not in STAT_COLUMNS:
        raise ValueError(f"Unknown stat: {stat}")
    sql = (
        f"SELECT p.uuid, p.username, gs.{stat}"  # noqa: S608
        " FROM player_global_stats gs JOIN players p ON p.uuid = gs.uuid"
        " LEFT JOIN guild_memberships gm ON gm.uuid = gs.uuid"
        f" WHERE gs.{stat} IS NOT NULL"
        " AND ($1::UUID IS NULL OR gm.guild_uuid = $1)"
        f" ORDER BY gs.{stat} DESC LIMIT $2"
    )
    rows = await pool.fetch(sql, guild_uuid, limit)
    return [(row[0], row[1], row[2]) for row in rows]
