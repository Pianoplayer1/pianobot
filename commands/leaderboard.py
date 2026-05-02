"""`/leaderboard` slash group: top guilds and players by raids, wars, or XP."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from asyncpg import Pool
from discord import Interaction, app_commands

from api import GuildLeaderboardEntry, WynncraftError
from database import completions, global_stats, stats_daily, tracked_guilds, xp_daily
from utils import display_full, tracked_guild_autocomplete
from views import send_table_response

if TYPE_CHECKING:
    from client import Pianobot


Period = Literal["today", "week", "month", "all"]
_PERIOD_LABEL = {
    "today": "today",
    "week": "the last 7 days",
    "month": "the last 30 days",
    "all": "all time",
}


def _period_start(period: Period) -> datetime:
    """Inclusive lower bound for the requested period (UTC)."""
    now = datetime.now(UTC)
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "week":
        return now - timedelta(days=7)
    if period == "month":
        return now - timedelta(days=30)
    return datetime.min.replace(tzinfo=UTC)


async def _resolve_guild_uuid(pool: Pool, guild: str | None) -> tuple[UUID, str] | None:
    """Resolve `guild` (name/tag substring) to (uuid, name) or None when unset."""
    if guild is None:
        return None
    found = await tracked_guilds.find(pool, guild)
    if not found:
        return None
    target = found[0]
    return target.uuid, target.name


ApiRow = tuple[UUID | None, str, int]


async def _api_top(bot: Pianobot, lb_type: str, limit: int = 25) -> list[ApiRow] | None:
    """Live Wynncraft leaderboard, dropping opted-out rows. None on API error."""
    try:
        entries: list[GuildLeaderboardEntry] = await bot.api.get_guild_leaderboard(
            lb_type, limit=limit
        )
    except WynncraftError:
        return None
    return [(e.uuid, e.name, e.score) for e in entries if not e.restricted and e.name]


class _GuildLeaderboard(app_commands.Group, name="guild"):
    """Top tracked guilds by activity in a window."""

    def __init__(self, bot: Pianobot) -> None:
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(period="Time window (default: week)")
    async def raids(self, interaction: Interaction, period: Period = "week") -> None:
        """Top guilds by raid completions. All-time uses Wynncraft's leaderboard."""
        await interaction.response.defer(thinking=True)
        if period == "all" and (
            api_rows := await _api_top(self.bot, "guildTotalRaids")
        ):
            await _send_table(
                interaction,
                api_rows,
                "Guild",
                "Raids",
                "Top guilds by total raid completions (live Wynncraft leaderboard).",
            )
            return
        rows = await completions.top_guilds_by_raids(
            self.bot.pool, _period_start(period), limit=25
        )
        await _send_guild_count_table(interaction, period, "raid", rows)

    @app_commands.command()
    @app_commands.describe(period="Time window (default: week)")
    async def wars(self, interaction: Interaction, period: Period = "week") -> None:
        """Top guilds by war completions. All-time uses Wynncraft's leaderboard."""
        await interaction.response.defer(thinking=True)
        if period == "all" and (api_rows := await _api_top(self.bot, "guildWars")):
            await _send_table(
                interaction,
                api_rows,
                "Guild",
                "Wars",
                "Top guilds by total wars (live Wynncraft leaderboard).",
            )
            return
        rows = await completions.top_guilds_by_wars(
            self.bot.pool, _period_start(period), limit=25
        )
        await _send_guild_count_table(interaction, period, "war", rows)

    @app_commands.command()
    @app_commands.describe(period="Time window (default: week)")
    async def xp(self, interaction: Interaction, period: Period = "week") -> None:
        """Top guilds by guild XP. All-time falls back to Wynncraft's level board."""
        await interaction.response.defer(thinking=True)
        if period == "all" and (api_rows := await _api_top(self.bot, "guildLevel")):
            await _send_table(
                interaction,
                api_rows,
                "Guild",
                "Level",
                "Top guilds by level (live Wynncraft leaderboard"
                " — there's no all-time XP leaderboard, level is the proxy).",
            )
            return
        rows = await xp_daily.top_guilds_by_xp(
            self.bot.pool, _period_start(period).date(), limit=25
        )
        await _send_guild_xp_table(interaction, period, rows)


class _PlayerLeaderboard(app_commands.Group, name="player"):
    """Top players by activity in a window, optionally scoped to one guild."""

    def __init__(self, bot: Pianobot) -> None:
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(
        period="Time window (default: week)",
        guild="Restrict to one guild (default: all tracked)",
    )
    @app_commands.autocomplete(guild=tracked_guild_autocomplete)
    async def raids(
        self,
        interaction: Interaction,
        period: Period = "week",
        guild: str | None = None,
    ) -> None:
        """Top players by raid completions, optionally guild-scoped."""
        await interaction.response.defer(thinking=True)
        guild_info = await _resolve_guild_uuid(self.bot.pool, guild)
        if guild is not None and guild_info is None:
            await interaction.followup.send(
                f"`{guild}` is not a tracked guild. Pick one from the autocomplete."
            )
            return
        guild_uuid = guild_info[0] if guild_info else None
        rows = await completions.top_players_by_raids(
            self.bot.pool,
            _period_start(period),
            limit=25,
            guild_uuid=guild_uuid,
        )
        await _send_player_count_table(
            interaction, period, "raid", rows, guild_info[1] if guild_info else None
        )

    @app_commands.command()
    @app_commands.describe(
        period="Time window (default: week)",
        guild="Restrict to one guild (default: all tracked)",
    )
    @app_commands.autocomplete(guild=tracked_guild_autocomplete)
    async def wars(
        self,
        interaction: Interaction,
        period: Period = "week",
        guild: str | None = None,
    ) -> None:
        """Top players by war completions. All-time + no guild = live API."""
        await interaction.response.defer(thinking=True)
        guild_info = await _resolve_guild_uuid(self.bot.pool, guild)
        if guild is not None and guild_info is None:
            await interaction.followup.send(
                f"`{guild}` is not a tracked guild. Pick one from the autocomplete."
            )
            return
        if (
            period == "all"
            and guild_info is None
            and (api_rows := await _api_top(self.bot, "warsCompletion"))
        ):
            await _send_table(
                interaction,
                api_rows,
                "Player",
                "Wars",
                "Top players by total wars (live Wynncraft leaderboard).",
            )
            return
        guild_uuid = guild_info[0] if guild_info else None
        rows = await completions.top_players_by_wars(
            self.bot.pool,
            _period_start(period),
            limit=25,
            guild_uuid=guild_uuid,
        )
        await _send_player_count_table(
            interaction, period, "war", rows, guild_info[1] if guild_info else None
        )

    @app_commands.command()
    @app_commands.describe(
        period="Time window (default: week)",
        guild="Restrict to one guild (default: all tracked)",
    )
    @app_commands.autocomplete(guild=tracked_guild_autocomplete)
    async def xp(
        self,
        interaction: Interaction,
        period: Period = "week",
        guild: str | None = None,
    ) -> None:
        """Top players by guild-XP gained, optionally guild-scoped."""
        await interaction.response.defer(thinking=True)
        guild_info = await _resolve_guild_uuid(self.bot.pool, guild)
        if guild is not None and guild_info is None:
            await interaction.followup.send(
                f"`{guild}` is not a tracked guild. Pick one from the autocomplete."
            )
            return
        guild_uuid = guild_info[0] if guild_info else None
        rows = await xp_daily.top_players_by_xp(
            self.bot.pool,
            _period_start(period).date(),
            limit=25,
            guild_uuid=guild_uuid,
        )
        await _send_player_xp_table(
            interaction, period, rows, guild_info[1] if guild_info else None
        )

    @app_commands.command()
    @app_commands.describe(
        metric="Which stat to rank by",
        period="Time window — 'all' uses lifetime totals (default: all)",
        guild="Restrict to current members of one guild (default: all)",
    )
    @app_commands.autocomplete(guild=tracked_guild_autocomplete)
    async def stats(
        self,
        interaction: Interaction,
        metric: Literal[
            "total_level",
            "completed_quests",
            "total_dungeons",
            "total_raids",
            "playtime_hours",
            "mobs_killed",
            "chests_found",
            "world_events",
            "lootruns",
            "caves",
            "pvp_kills",
            "pvp_deaths",
            "content_completion",
        ],
        period: Period = "all",
        guild: str | None = None,
    ) -> None:
        """Top players by a globalData stat, optionally in a time window."""
        await interaction.response.defer(thinking=True)
        guild_info = await _resolve_guild_uuid(self.bot.pool, guild)
        if guild is not None and guild_info is None:
            await interaction.followup.send(
                f"`{guild}` is not a tracked guild. Pick one from the autocomplete."
            )
            return
        guild_uuid = guild_info[0] if guild_info else None
        target_all_time = (
            f"current members of {guild_info[1]}"
            if guild_info
            else "all observed players"
        )
        target_windowed = (
            f"activity attributed to {guild_info[1]}"
            if guild_info
            else "all observed players"
        )

        if period != "all":
            rows = await stats_daily.top_by_stat(
                self.bot.pool,
                metric,
                _period_start(period).date(),
                limit=25,
                guild_uuid=guild_uuid,
            )
            if not rows:
                await interaction.followup.send(
                    f"No `{metric}` gains recorded for {_PERIOD_LABEL[period]}."
                )
                return
            leading = (
                f"Top by `{metric}` gained"
                f" over {_PERIOD_LABEL[period]} — {target_windowed}."
            )
            columns = {"Player": 22, f"{metric} gained": 16}
            body = [[name, str(value)] for _, name, value in rows]
            await send_table_response(
                interaction, columns, body, page_size=15, leading_text=leading
            )
            return

        # All-time: live Wynncraft leaderboard for metrics it exposes
        api_lb = {
            "total_level": "totalGlobalLevel",
            "content_completion": "globalPlayerContent",
        }.get(metric)
        if (
            api_lb is not None
            and guild_info is None
            and (api_rows := await _api_top(self.bot, api_lb))
        ):
            await _send_table(
                interaction,
                api_rows,
                "Player",
                metric,
                f"Top by `{metric}` (live Wynncraft leaderboard).",
            )
            return
        rows = await global_stats.top_players_by_stat(
            self.bot.pool, metric, limit=25, guild_uuid=guild_uuid
        )
        if not rows:
            await interaction.followup.send(
                f"No `{metric}` data captured yet (the API may hide it for"
                " all observed players)."
            )
            return
        body = [[name, str(value)] for _, name, value in rows]
        leading = f"Top by `{metric}` (lifetime) — {target_all_time}."
        columns = {"Player": 22, metric: 16}
        await send_table_response(
            interaction, columns, body, page_size=15, leading_text=leading
        )


class LeaderboardCommands(app_commands.Group, name="leaderboard"):
    """Cross-guild + per-guild leaderboards for raids, wars, and XP."""

    def __init__(self, bot: Pianobot) -> None:
        """Bind the group + register the guild and player subgroups."""
        super().__init__()
        self.bot = bot
        self.add_command(_GuildLeaderboard(bot))
        self.add_command(_PlayerLeaderboard(bot))


async def _send_table(
    interaction: Interaction,
    rows: list[ApiRow] | list[tuple[UUID, str, int]],
    entity: str,
    value_label: str,
    leading: str,
) -> None:
    """Generic name+value table. Used for both API and DB-sourced leaderboards."""
    body = [[name, str(value)] for _, name, value in rows]
    columns = {entity: 28, value_label: 16}
    await send_table_response(
        interaction, columns, body, page_size=15, leading_text=leading
    )


async def _send_guild_count_table(
    interaction: Interaction,
    period: Period,
    kind: str,
    rows: list[tuple[UUID, str, int]],
) -> None:
    if not rows:
        await interaction.followup.send(
            f"No {kind} completions tracked for {_PERIOD_LABEL[period]}."
        )
        return
    body = [[name, str(count)] for _, name, count in rows]
    columns = {"Guild": 28, f"{kind.capitalize()}s": 10}
    leading = f"Top guilds by {kind} completions over {_PERIOD_LABEL[period]}."
    await send_table_response(
        interaction, columns, body, page_size=15, leading_text=leading
    )


async def _send_guild_xp_table(
    interaction: Interaction, period: Period, rows: list[tuple[UUID, str, int]]
) -> None:
    if not rows:
        await interaction.followup.send(
            f"No guild XP tracked for {_PERIOD_LABEL[period]}."
        )
        return
    body = [[name, display_full(xp)] for _, name, xp in rows]
    columns = {"Guild": 28, "XP gained": 16}
    leading = f"Top guilds by guild-XP gained over {_PERIOD_LABEL[period]}."
    await send_table_response(
        interaction, columns, body, page_size=15, leading_text=leading
    )


async def _send_player_count_table(
    interaction: Interaction,
    period: Period,
    kind: str,
    rows: list[tuple[UUID, str, int]],
    scope: str | None,
) -> None:
    if not rows:
        await interaction.followup.send(
            f"No {kind} completions tracked for {_PERIOD_LABEL[period]}."
        )
        return
    body = [[name, str(count)] for _, name, count in rows]
    columns = {"Player": 22, f"{kind.capitalize()}s": 10}
    target = f"in {scope}" if scope else "across all tracked guilds"
    leading = (
        f"Top players by {kind} completions {target} over {_PERIOD_LABEL[period]}."
    )
    await send_table_response(
        interaction, columns, body, page_size=15, leading_text=leading
    )


async def _send_player_xp_table(
    interaction: Interaction,
    period: Period,
    rows: list[tuple[UUID, str, int]],
    scope: str | None,
) -> None:
    if not rows:
        await interaction.followup.send(
            f"No guild XP tracked for {_PERIOD_LABEL[period]}."
        )
        return
    body = [[name, display_full(xp)] for _, name, xp in rows]
    columns = {"Player": 22, "XP gained": 16}
    target = f"in {scope}" if scope else "across all tracked guilds"
    leading = f"Top players by guild-XP gained {target} over {_PERIOD_LABEL[period]}."
    await send_table_response(
        interaction, columns, body, page_size=15, leading_text=leading
    )
