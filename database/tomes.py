"""Guild tome queue."""

from datetime import datetime

from asyncpg import Pool


async def add_request(pool: Pool, discord_id: int) -> None:
    """Enqueue a new tome request for a Discord user."""
    await pool.execute("INSERT INTO tome_requests (discord_id) VALUES ($1)", discord_id)


async def stats_for(pool: Pool, discord_id: int) -> tuple[int, int, datetime | None]:
    """Return (pending, granted, latest_request_ts) for one user."""
    row = await pool.fetchrow(
        "SELECT"
        " COUNT(*) FILTER (WHERE resolved_at IS NULL) AS pending,"
        " COUNT(*) FILTER (WHERE resolution = 'granted') AS granted,"
        " MAX(requested_at) AS latest_request"
        " FROM tome_requests WHERE discord_id = $1",
        discord_id,
    )
    if row is None:
        return 0, 0, None
    return row[0], row[1], row[2]


async def pending(pool: Pool) -> dict[int, tuple[int, int, datetime]]:
    """Map discord_id to (pending, granted, latest_request) for open queues."""
    rows = await pool.fetch(
        "SELECT"
        " discord_id,"
        " COUNT(*) FILTER (WHERE resolved_at IS NULL) AS pending,"
        " COUNT(*) FILTER (WHERE resolution = 'granted') AS granted,"
        " MAX(requested_at) AS latest_request"
        " FROM tome_requests GROUP BY discord_id"
        " HAVING COUNT(*) FILTER (WHERE resolved_at IS NULL) > 0"
        " ORDER BY latest_request DESC"
    )
    return {row[0]: (row[1], row[2], row[3]) for row in rows}


async def resolve_oldest(pool: Pool, discord_id: int, resolution: str) -> bool:
    """Resolve the user's oldest open request; True if a row was updated."""
    if resolution not in ("granted", "denied"):
        raise ValueError(f"invalid resolution {resolution!r}")
    status = await pool.execute(
        "UPDATE tome_requests SET resolved_at = NOW(), resolution = $1"
        " WHERE id = ("
        "   SELECT id FROM tome_requests"
        "   WHERE discord_id = $2 AND resolved_at IS NULL"
        "   ORDER BY requested_at LIMIT 1"
        " )",
        resolution,
        discord_id,
    )
    return status.endswith("1")
