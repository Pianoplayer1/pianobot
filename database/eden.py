"""Eden-specific tables: rewards, weekly objective, weekly playtime, award cycles."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from asyncpg import Pool

# Display-unit conversions: how many internal units make one displayed unit.
_DISPLAY_UNITS = {"emeralds": 4096, "aspects": 2}


def display_unit(kind: str) -> int:
    """Internal-units-per-display-unit ratio for the given reward kind."""
    return _DISPLAY_UNITS[kind]


@dataclass(slots=True, frozen=True)
class RewardBalance:
    """One row of the `reward_balances` table."""

    uuid: UUID
    pending_emeralds: int
    pending_aspects: int
    emeralds_blocked: bool
    aspects_blocked: bool


async def ensure_reward_balance(pool: Pool, uuid: UUID) -> None:
    """Create the `reward_balances` row for a new member if it doesn't exist."""
    await pool.execute(
        "INSERT INTO reward_balances (uuid) VALUES ($1) ON CONFLICT (uuid) DO NOTHING",
        uuid,
    )


async def record_raid_completion(
    pool: Pool, uuid: UUID, emeralds_rate: int, aspects_rate: int
) -> None:
    """Credit emeralds + aspects for one raid, skipping each if blocked."""
    await pool.execute(
        "UPDATE reward_balances SET"
        " pending_emeralds = pending_emeralds"
        "   + (CASE WHEN emeralds_blocked THEN 0 ELSE $1 END),"
        " pending_aspects = pending_aspects"
        "   + (CASE WHEN aspects_blocked THEN 0 ELSE $2 END)"
        " WHERE uuid = $3",
        emeralds_rate,
        aspects_rate,
        uuid,
    )


async def pending_emeralds_active(pool: Pool, eden_uuid: UUID) -> dict[str, int]:
    """Map current-Eden username to pending raid-emerald balance."""
    rows = await pool.fetch(
        "SELECT p.username, r.pending_emeralds"
        " FROM players p JOIN guild_memberships gm ON gm.uuid = p.uuid"
        " JOIN reward_balances r ON r.uuid = p.uuid"
        " WHERE gm.guild_uuid = $1 AND r.pending_emeralds > 0",
        eden_uuid,
    )
    return {row[0]: row[1] for row in rows}


async def pending_emeralds_left(pool: Pool, eden_uuid: UUID) -> dict[UUID, int]:
    """Map uuid to pending raid-emerald balance for ex-Eden-members."""
    rows = await pool.fetch(
        "SELECT r.uuid, r.pending_emeralds FROM reward_balances r"
        " LEFT JOIN guild_memberships gm ON gm.uuid = r.uuid AND gm.guild_uuid = $1"
        " WHERE gm.uuid IS NULL AND r.pending_emeralds > 0",
        eden_uuid,
    )
    return {row[0]: row[1] for row in rows}


async def pending_aspects_active(
    pool: Pool, eden_uuid: UUID
) -> dict[str, tuple[int, datetime]]:
    """Map current-Eden username to (pending-aspects, joined-at)."""
    rows = await pool.fetch(
        "SELECT p.username, r.pending_aspects, gm.joined_at"
        " FROM players p JOIN guild_memberships gm ON gm.uuid = p.uuid"
        " JOIN reward_balances r ON r.uuid = p.uuid"
        " WHERE gm.guild_uuid = $1 AND r.pending_aspects > 0",
        eden_uuid,
    )
    return {row[0]: (row[1], row[2]) for row in rows}


async def pending_aspects_left(pool: Pool, eden_uuid: UUID) -> dict[UUID, int]:
    """Map uuid to pending aspects for ex-Eden-members."""
    rows = await pool.fetch(
        "SELECT r.uuid, r.pending_aspects FROM reward_balances r"
        " LEFT JOIN guild_memberships gm ON gm.uuid = r.uuid AND gm.guild_uuid = $1"
        " WHERE gm.uuid IS NULL AND r.pending_aspects > 0",
        eden_uuid,
    )
    return {row[0]: row[1] for row in rows}


async def blocked_list(pool: Pool, eden_uuid: UUID, kind: str) -> list[str]:
    """Active Eden members blocked from receiving the given reward kind."""
    column = "emeralds_blocked" if kind == "emeralds" else "aspects_blocked"
    # `column` is bounded to two literal values; safe to interpolate.
    rows = await pool.fetch(
        f"SELECT p.username FROM players p"  # noqa: S608
        f" JOIN guild_memberships gm ON gm.uuid = p.uuid"
        f" JOIN reward_balances r ON r.uuid = p.uuid"
        f" WHERE gm.guild_uuid = $1 AND r.{column}",
        eden_uuid,
    )
    return [row[0] for row in rows]


async def set_blocked(pool: Pool, uuid: UUID, kind: str, blocked: bool) -> None:
    """Set the blocked flag for emeralds or aspects on one member."""
    column = "emeralds_blocked" if kind == "emeralds" else "aspects_blocked"
    await pool.execute(
        f"UPDATE reward_balances SET {column} = $1 WHERE uuid = $2",  # noqa: S608
        blocked,
        uuid,
    )


async def reset_pending(pool: Pool, uuid: UUID, kind: str) -> None:
    """Reset one member's pending balance, keeping the sub-display-unit remainder."""
    column = "pending_emeralds" if kind == "emeralds" else "pending_aspects"
    unit = display_unit(kind)
    await pool.execute(
        f"UPDATE reward_balances SET {column} = MOD({column}, {unit})"  # noqa: S608
        " WHERE uuid = $1",
        uuid,
    )


async def reset_all_pending(
    pool: Pool, kind: str, eden_uuid: UUID | None = None
) -> None:
    """Reset every positive pending balance (for aspects: 7d cd) for the given kind."""
    column = "pending_emeralds" if kind == "emeralds" else "pending_aspects"
    unit = display_unit(kind)
    if kind == "aspects" and eden_uuid is not None:
        await pool.execute(
            f"UPDATE reward_balances r SET {column} = MOD({column}, {unit})"  # noqa: S608
            f" WHERE {column} > 0"
            " AND NOT EXISTS ("
            "   SELECT 1 FROM guild_memberships gm"
            "   WHERE gm.uuid = r.uuid AND gm.guild_uuid = $1"
            "   AND gm.joined_at > NOW() - INTERVAL '7 days'"
            ")",
            eden_uuid,
        )
    else:
        await pool.execute(
            f"UPDATE reward_balances SET {column} = MOD({column}, {unit})"  # noqa: S608
            f" WHERE {column} > 0"
        )


async def get_rate(pool: Pool, key: str, default: int = 0) -> int:
    """Read an entry from `reward_rates`, falling back to `default`."""
    row = await pool.fetchrow("SELECT value FROM reward_rates WHERE key = $1", key)
    return row[0] if row else default


async def set_rate(pool: Pool, key: str, value: int) -> None:
    """Upsert a `reward_rates` entry."""
    await pool.execute(
        "INSERT INTO reward_rates (key, value) VALUES ($1, $2)"
        " ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
        key,
        value,
    )


async def cycle_pending_finalization(pool: Pool, code: str) -> bool:
    """Check whether the cycle exists but has not yet been finalized."""
    row = await pool.fetchrow(
        "SELECT 1 FROM award_cycles WHERE code = $1 AND finalized_at IS NULL", code
    )
    return row is not None


async def ensure_cycle(pool: Pool, code: str, started_at: datetime) -> None:
    """Register the start of a new award cycle (idempotent)."""
    await pool.execute(
        "INSERT INTO award_cycles (code, started_at) VALUES ($1, $2)"
        " ON CONFLICT (code) DO NOTHING",
        code,
        started_at,
    )


async def finalize_cycle(pool: Pool, code: str, ended_at: datetime) -> None:
    """Mark an award cycle finalized after posting its results."""
    await pool.execute(
        "UPDATE award_cycles SET ended_at = $1, finalized_at = NOW()"
        " WHERE code = $2 AND finalized_at IS NULL",
        ended_at,
        code,
    )


async def upsert_weekly_objective(
    pool: Pool,
    uuid: UUID,
    completed: bool,
    streak: int,
) -> None:
    """Record one (uuid, current ISO year/week) weekly-objective row."""
    await pool.execute(
        "INSERT INTO eden_weekly_objective (uuid, completed, streak)"
        " VALUES ($1, $2, $3)"
        " ON CONFLICT (uuid, iso_year, iso_week) DO UPDATE"
        "   SET completed = EXCLUDED.completed, streak = EXCLUDED.streak",
        uuid,
        completed,
        streak,
    )


async def weekly_objective_aggregate(
    pool: Pool, limit: int = 12
) -> list[tuple[int, int, int, int]]:
    """Per-week objective stats: (iso_year, iso_week, completed_count, total_count)."""
    rows = await pool.fetch(
        "SELECT iso_year, iso_week,"
        " COUNT(*) FILTER (WHERE completed) AS completed_count,"
        " COUNT(*) AS total_count"
        " FROM eden_weekly_objective"
        " GROUP BY iso_year, iso_week"
        " ORDER BY iso_year DESC, iso_week DESC"
        " LIMIT $1",
        limit,
    )
    return [(row[0], row[1], row[2], row[3]) for row in rows]


async def weekly_objective_for_week(
    pool: Pool, iso_year: int, iso_week: int
) -> dict[UUID, tuple[bool, int]]:
    """Map uuid to (completed, streak) for the given ISO week."""
    rows = await pool.fetch(
        "SELECT uuid, completed, streak FROM eden_weekly_objective"
        " WHERE iso_year = $1 AND iso_week = $2",
        iso_year,
        iso_week,
    )
    return {row[0]: (row[1], row[2]) for row in rows}


async def weekly_objective_history(
    pool: Pool, uuid: UUID
) -> list[tuple[int, int, bool, int]]:
    """One row per ISO week we have data for: (year, week, completed, streak)."""
    rows = await pool.fetch(
        "SELECT iso_year, iso_week, completed, streak FROM eden_weekly_objective"
        " WHERE uuid = $1 ORDER BY iso_year, iso_week",
        uuid,
    )
    return [(row[0], row[1], row[2], row[3]) for row in rows]


async def record_xp(pool: Pool, rows: dict[UUID, int]) -> None:
    """Batch-insert one XP snapshot for many Eden members at a single instant."""
    if not rows:
        return
    taken_at = datetime.now(UTC)
    uuids = list(rows.keys())
    xps = [rows[uuid] for uuid in uuids]
    await pool.execute(
        "INSERT INTO eden_xp_snapshots (uuid, contributed_xp, taken_at)"
        " SELECT u, x, $3 FROM UNNEST($1::UUID[], $2::BIGINT[]) AS t(u, x)"
        " ON CONFLICT (uuid, taken_at) DO NOTHING",
        uuids,
        xps,
        taken_at,
    )


async def latest_two_xp_times(pool: Pool) -> list[datetime]:
    """Two most recent distinct snapshot times (used for the XP-diff post)."""
    rows = await pool.fetch(
        "SELECT DISTINCT taken_at FROM eden_xp_snapshots ORDER BY taken_at DESC LIMIT 2"
    )
    return [row[0] for row in rows]


async def xp_at(pool: Pool, taken_at: datetime) -> dict[UUID, int]:
    """Every member's contributed_xp at a specific snapshot time."""
    rows = await pool.fetch(
        "SELECT uuid, contributed_xp FROM eden_xp_snapshots WHERE taken_at = $1",
        taken_at,
    )
    return {row[0]: row[1] for row in rows}


async def cleanup_xp(pool: Pool) -> None:
    """Thin: keep hourly after 7 days, daily after 14 days."""
    await pool.execute(
        "DELETE FROM eden_xp_snapshots WHERE taken_at < NOW() - '7 days'::interval"
        " AND date_trunc('hour', taken_at) <> taken_at"
    )
    await pool.execute(
        "DELETE FROM eden_xp_snapshots WHERE taken_at < NOW() - '14 days'::interval"
        " AND date_trunc('day', taken_at) <> taken_at"
    )


async def xp_diff_by_username(
    pool: Pool, start: datetime | None = None, end: datetime | None = None
) -> dict[str, int]:
    """Map current-username to XP gained between earliest+latest snapshot in window."""
    start_row = await pool.fetchrow(
        "SELECT taken_at FROM eden_xp_snapshots"
        " WHERE taken_at >= $1 ORDER BY taken_at LIMIT 1",
        start or datetime.min,
    )
    end_row = await pool.fetchrow(
        "SELECT taken_at FROM eden_xp_snapshots"
        " WHERE taken_at <= $1 ORDER BY taken_at DESC LIMIT 1",
        end or datetime.max,
    )
    if start_row is None or end_row is None or start_row[0] >= end_row[0]:
        return {}
    rows = await pool.fetch(
        "SELECT p.username,"
        " COALESCE(e.contributed_xp, 0) - COALESCE(s.contributed_xp, 0)"
        " FROM players p"
        " LEFT JOIN eden_xp_snapshots s ON s.uuid = p.uuid AND s.taken_at = $1"
        " LEFT JOIN eden_xp_snapshots e ON e.uuid = p.uuid AND e.taken_at = $2"
        " WHERE COALESCE(e.contributed_xp, 0) - COALESCE(s.contributed_xp, 0) > 0",
        start_row[0],
        end_row[0],
    )
    return {row[0]: row[1] for row in rows}
