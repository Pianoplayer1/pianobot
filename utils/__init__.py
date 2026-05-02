"""Stateless helpers: time, formatters, table rendering, Discord shims."""

from utils.discord import (
    guild_autocomplete,
    raid_autocomplete,
    region_autocomplete,
    tracked_guild_autocomplete,
)
from utils.formatters import (
    display_full,
    display_short,
    format_last_seen,
    format_time_since,
    smooth_series,
)
from utils.tables import paginate, render_page
from utils.time import get_cycle, get_cycle_window, get_prev_cycle, get_rounded_time

__all__ = [
    "display_full",
    "display_short",
    "format_last_seen",
    "format_time_since",
    "get_cycle",
    "get_cycle_window",
    "get_prev_cycle",
    "get_rounded_time",
    "guild_autocomplete",
    "paginate",
    "raid_autocomplete",
    "render_page",
    "region_autocomplete",
    "smooth_series",
    "tracked_guild_autocomplete",
]
