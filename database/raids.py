"""Raid name to id lookup. Log-level tables reference raids by id, not name."""

import logging

from asyncpg import Pool

log = logging.getLogger(__name__)


async def get_or_create_id(pool: Pool, name: str) -> int:
    """Return the id for `name`, inserting + logging a warning for new raids."""
    if row := await pool.fetchrow("SELECT id FROM raid_names WHERE name = $1", name):
        return int(row[0])
    inserted = await pool.fetchrow(
        "INSERT INTO raid_names (name) VALUES ($1)"
        " ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name"
        " RETURNING id",
        name,
    )
    if inserted is None:
        raise RuntimeError(f"failed to upsert raid_name {name!r}")
    raid_id = int(inserted[0])
    log.warning("Discovered new raid: %r (id=%d)", name, raid_id)
    return raid_id


async def search(pool: Pool, query: str, limit: int = 25) -> list[tuple[int, str]]:
    """Substring search over raid names for command autocompletion."""
    rows = await pool.fetch(
        "SELECT id, name FROM raid_names"
        " WHERE $1 = '' OR name ILIKE '%' || $1 || '%'"
        " ORDER BY name LIMIT $2",
        query,
        limit,
    )
    return [(row[0], row[1]) for row in rows]
