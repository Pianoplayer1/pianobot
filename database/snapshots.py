"""Generic time-series tables: per-player daily playtime + world online counts."""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from asyncpg import Pool


async def increment_daily(pool: Pool, uuids: list[UUID], minutes: int = 1) -> None:
    """Tick `minutes` of daily online time for each uuid (default: today)."""
    if not uuids:
        return
    await pool.execute(
        "INSERT INTO player_daily_activity (uuid, minutes)"
        " SELECT u, $2 FROM UNNEST($1::UUID[]) AS t(u)"
        " ON CONFLICT (uuid, day) DO UPDATE"
        " SET minutes = player_daily_activity.minutes + EXCLUDED.minutes",
        uuids,
        minutes,
    )


async def daily_history(pool: Pool, uuid: UUID, days: int) -> dict[date, int]:
    """Daily minutes online for one player over the last N days."""
    since = datetime.now(UTC).date() - timedelta(days=days)
    rows = await pool.fetch(
        "SELECT day, minutes FROM player_daily_activity"
        " WHERE uuid = $1 AND day >= $2"
        " ORDER BY day",
        uuid,
        since,
    )
    return {row[0]: row[1] for row in rows}


async def cleanup_daily(pool: Pool, retain_days: int = 60) -> None:
    """Drop daily-activity rows older than `retain_days` days."""
    cutoff = datetime.now(UTC).date() - timedelta(days=retain_days)
    await pool.execute(
        "DELETE FROM player_daily_activity WHERE day < $1",
        cutoff,
    )


async def record_online_counts(pool: Pool, counts: dict[str, int]) -> None:
    """Batch-insert per-world online-player counts at current snapshot time."""
    if not counts:
        return
    await pool.executemany(
        "INSERT INTO online_player_snapshots (world, count)"
        " VALUES ($1, $2) ON CONFLICT (taken_at, world) DO NOTHING",
        list(counts.items()),
    )


async def online_history(
    pool: Pool, days: int, region: str | None = None
) -> dict[datetime, int]:
    """Online-player time-series for the last N days, summed across all worlds."""
    if region is None:
        rows = await pool.fetch(
            "SELECT taken_at, SUM(count)::INTEGER FROM online_player_snapshots"
            " WHERE taken_at > NOW() - MAKE_INTERVAL(days => $1)"
            " GROUP BY taken_at ORDER BY taken_at",
            days,
        )
    else:
        rows = await pool.fetch(
            "SELECT taken_at, SUM(count)::INTEGER FROM online_player_snapshots"
            " WHERE substring(world from '^[A-Za-z]+') = $1"
            " AND taken_at > NOW() - MAKE_INTERVAL(days => $2)"
            " GROUP BY taken_at ORDER BY taken_at",
            region,
            days,
        )
    return {row[0]: row[1] for row in rows}


async def regions(pool: Pool) -> list[str]:
    """Distinct world-region prefixes present in online snapshots."""
    rows = await pool.fetch(
        "SELECT DISTINCT substring(world from '^[A-Za-z]+') AS region"
        " FROM online_player_snapshots"
        " WHERE world IS NOT NULL"
        " ORDER BY region"
    )
    return [row[0] for row in rows if row[0]]


async def cleanup_online_counts(pool: Pool) -> None:
    """Hourly-mean after 7 days, daily-mean after 14 days."""
    await pool.execute(
        "INSERT INTO online_player_snapshots (taken_at, world, count)"
        " SELECT date_trunc('hour', taken_at), world, ROUND(AVG(count))::SMALLINT"
        "   FROM online_player_snapshots"
        "  WHERE taken_at < NOW() - '7 days'::interval"
        "    AND taken_at >= NOW() - '14 days'::interval"
        "  GROUP BY date_trunc('hour', taken_at), world"
        " ON CONFLICT (taken_at, world) DO UPDATE SET count = EXCLUDED.count"
    )
    await pool.execute(
        "DELETE FROM online_player_snapshots"
        " WHERE taken_at < NOW() - '7 days'::interval"
        "   AND taken_at >= NOW() - '14 days'::interval"
        "   AND date_trunc('hour', taken_at) <> taken_at"
    )
    await pool.execute(
        "INSERT INTO online_player_snapshots (taken_at, world, count)"
        " SELECT date_trunc('day', taken_at), world, ROUND(AVG(count))::SMALLINT"
        "   FROM online_player_snapshots"
        "  WHERE taken_at < NOW() - '14 days'::interval"
        "  GROUP BY date_trunc('day', taken_at), world"
        " ON CONFLICT (taken_at, world) DO UPDATE SET count = EXCLUDED.count"
    )
    await pool.execute(
        "DELETE FROM online_player_snapshots"
        " WHERE taken_at < NOW() - '14 days'::interval"
        "   AND date_trunc('day', taken_at) <> taken_at"
    )
