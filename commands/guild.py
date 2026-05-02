"""`/guild` slash group: stats, graph, inactivity, history (any Wynncraft guild)."""

from __future__ import annotations

import io
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Literal

from discord import Embed, File, Interaction, app_commands
from discord.utils import format_dt
from matplotlib import dates as mdates
from matplotlib import pyplot as plt

from api import NotFoundError, WynncraftError
from database import (
    completions,
    guild_membership,
    guild_metrics,
    guilds,
    players,
    tracked_guilds,
    world_state,
    xp_daily,
)
from utils import (
    format_last_seen,
    guild_autocomplete,
    smooth_series,
    tracked_guild_autocomplete,
)
from views import send_table_response

if TYPE_CHECKING:
    from client import Pianobot


class GuildCommands(app_commands.Group, name="guild"):
    """Wynncraft guild lookups and tracked-guild activity."""

    def __init__(self, bot: Pianobot) -> None:
        """Bind the group to its owning bot for pool/api access."""
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(guild="Guild name or prefix")
    @app_commands.autocomplete(guild=guild_autocomplete)
    async def stats(self, interaction: Interaction, guild: str) -> None:
        """Guild profile (level, member count, territories, wars, total raids)."""
        await interaction.response.defer(thinking=True)
        try:
            g = await self.bot.api.get_guild(guild)
        except NotFoundError:
            await interaction.followup.send(f"Guild `{guild}` not found.")
            return
        except WynncraftError as exc:
            await interaction.followup.send(f"Wynncraft API error: {exc}")
            return

        is_tracked = bool(await tracked_guilds.find(self.bot.pool, g.name))
        online = g.online_total
        embed = Embed(
            title=f"{g.name} [{g.prefix}]",
            timestamp=datetime.now(UTC),
        )
        embed.add_field(name="Level", value=f"{g.level} ({g.xp_percent}%)", inline=True)
        embed.add_field(
            name="Members", value=f"{online} / {g.member_total} online", inline=True
        )
        embed.add_field(name="Created", value=format_dt(g.created_at, "R"), inline=True)
        embed.add_field(name="Territories", value=str(g.territories), inline=True)
        embed.add_field(name="Wars", value=str(g.wars or "?"), inline=True)
        embed.add_field(name="Total raids", value=str(g.total_raids), inline=True)
        if is_tracked:
            embed.set_footer(text=f"Tracked guild  •  {g.uuid}")
        else:
            embed.set_footer(text=str(g.uuid))
        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.describe(guild="Guild name or prefix")
    @app_commands.autocomplete(guild=guild_autocomplete)
    async def history(self, interaction: Interaction, guild: str) -> None:
        """Recent joins, leaves, rank changes, and renames for a guild."""
        await interaction.response.defer(thinking=True)

        known = await guilds.all_known(self.bot.pool)
        guild_row = next(
            (
                g
                for g in known
                if g.name.lower() == guild.lower()
                or (g.prefix is not None and g.prefix.lower() == guild.lower())
            ),
            None,
        )
        if guild_row is None:
            await interaction.followup.send(
                f"Guild `{guild}` not found in the database."
            )
            return

        guild_uuid = guild_row.uuid
        guild_name = guild_row.name

        member_events = await guild_membership.events_for_guild(
            self.bot.pool, guild_uuid, limit=80
        )
        lifecycle_events = await guilds.events_for_guild(
            self.bot.pool, guild_uuid, limit=20
        )

        if not member_events and not lifecycle_events:
            await interaction.followup.send(f"No history recorded for `{guild_name}`.")
            return

        uuids = list({e.uuid for e in member_events})
        username_map = await players.usernames_by_uuid(self.bot.pool, uuids)

        raw: list[tuple[datetime, str, str]] = []
        for ev in member_events:
            name = username_map.get(ev.uuid, str(ev.uuid)[:8])
            if ev.event_type == "rank_change":
                detail = f"{ev.old_rank} to {ev.new_rank}: {name}"
            elif ev.event_type == "join":
                detail = f"joined as {ev.new_rank or '?'}: {name}"
            else:
                detail = f"left ({ev.old_rank}): {name}"
            raw.append((ev.occurred_at, ev.event_type, detail))

        for lev in lifecycle_events:
            if lev.event_type == "renamed":
                detail = f"{lev.old_name} to {lev.new_name}"
            elif lev.event_type == "retagged":
                detail = f"[{lev.old_prefix}] to [{lev.new_prefix}]"
            elif lev.event_type == "created":
                detail = lev.new_name or guild_name
            else:
                detail = lev.old_name or guild_name
            raw.append((lev.occurred_at, lev.event_type, detail))

        raw.sort(key=lambda t: t[0], reverse=True)
        rows = [[format_dt(ts, "f"), etype, detail] for ts, etype, detail in raw]

        columns = {"When": 30, "Event": 14, "Detail": 36}
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=15,
            separator_rows=0,
            enum=False,
            leading_text=f"History for **{guild_name}**",
        )

    @app_commands.command()
    @app_commands.describe(
        guild="Tracked guild name",
        metric="Which series to plot (default: online)",
        days="Number of days to plot (default: 7)",
    )
    @app_commands.autocomplete(guild=tracked_guild_autocomplete)
    async def graph(
        self,
        interaction: Interaction,
        guild: str,
        metric: Literal["online", "raids", "wars", "xp"] = "online",
        days: int = 7,
    ) -> None:
        """Time series of a tracked guild's online count, raids, wars, or XP."""
        await interaction.response.defer(thinking=True)
        if days < 1:
            await interaction.followup.send("`days` must be at least 1.")
            return
        found = await tracked_guilds.find(self.bot.pool, guild)
        if not found:
            await interaction.followup.send(
                f"`{guild}` is not a tracked guild. Pick one from the autocomplete."
            )
            return
        target = found[0]
        tag_part = f" [{target.prefix}]" if target.prefix else ""

        if metric == "online":
            timeseries = await guild_metrics.online_history(
                self.bot.pool, target.uuid, days
            )
            if not timeseries:
                await interaction.followup.send(
                    f"No activity data for `{target.name}` in the last {days} day(s)."
                )
                return
            buf = _render_line(
                timeseries,
                f"Online Player Activity of {target.name}{tag_part}"
                f" — {days} Day{'' if days == 1 else 's'}",
                "Player Count",
            )
        else:
            since_dt = datetime.now(UTC) - timedelta(days=days)
            if metric == "raids":
                daily = await completions.daily_raid_counts_for_guild(
                    self.bot.pool, target.uuid, since_dt
                )
                ylabel = "Raid completions"
            elif metric == "wars":
                daily = await completions.daily_war_counts_for_guild(
                    self.bot.pool, target.uuid, since_dt
                )
                ylabel = "War completions"
            else:
                daily_int = await xp_daily.daily_for_guild(
                    self.bot.pool, target.uuid, since_dt.date()
                )
                daily = {d: int(v) for d, v in daily_int.items()}
                ylabel = "XP gained"
            if not daily:
                await interaction.followup.send(
                    f"No {metric} data for `{target.name}` in the last {days} day(s)."
                )
                return
            buf = _render_bars(
                daily,
                days,
                ylabel,
                f"{target.name}{tag_part} — {days} Day{'' if days == 1 else 's'}",
            )
        await interaction.followup.send(file=File(buf, filename="graph.png"))

    @app_commands.command()
    @app_commands.describe(guild="Guild name (tracked guilds auto-complete)")
    @app_commands.autocomplete(guild=guild_autocomplete)
    async def inactivity(self, interaction: Interaction, guild: str) -> None:
        """Time since each member of a guild has been last seen online."""
        await interaction.response.defer(thinking=True)
        try:
            guild_data = await self.bot.api.get_guild(guild)
        except NotFoundError:
            await interaction.followup.send(f"Guild `{guild}` not found.")
            return
        except WynncraftError as exc:
            await interaction.followup.send(f"Wynncraft API error: {exc}")
            return
        uuids = [m.uuid for m in guild_data.members]
        stored = await world_state.last_seen_map(self.bot.pool, uuids)
        rows_raw: list[tuple[float, list[str]]] = []
        for member in guild_data.members:
            last_seen = stored.get(member.uuid) or member.last_join_at
            raw_days, text = format_last_seen(member.online, last_seen)
            rows_raw.append((raw_days, [member.username, member.rank, text]))
        rows_raw.sort(key=lambda r: r[0], reverse=True)
        rows = [r[1] for r in rows_raw]
        columns = {f"{guild_data.name} Members": 36, "Rank": 26, "Time Inactive": 26}
        await send_table_response(interaction, columns, rows, page_size=15)


def _render_line(
    timeseries: dict[datetime, int], xlabel: str, ylabel: str
) -> io.BytesIO:
    """Render a smoothed line chart and return the PNG buffer."""
    fig, axes = plt.subplots()
    axes.plot(list(timeseries.keys()), smooth_series(timeseries.values()))  # type: ignore[arg-type]
    axes.xaxis.set_major_formatter(
        mdates.DateFormatter("%b %d, %H:%M")  # type: ignore[no-untyped-call]
    )
    axes.xaxis.set_label_position("top")
    fig.autofmt_xdate()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def _render_bars(
    daily: dict[date, int], days: int, ylabel: str, label: str
) -> io.BytesIO:
    """Render a per-day bar chart and return the PNG buffer."""
    today = datetime.now(UTC).date()
    days_list: list[date] = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    values = [daily.get(d, 0) for d in days_list]
    fig, axes = plt.subplots()
    axes.bar(days_list, values, color="steelblue")  # type: ignore[arg-type]
    axes.xaxis.set_major_formatter(
        mdates.DateFormatter("%b %d")  # type: ignore[no-untyped-call]
    )
    axes.xaxis.set_label_position("top")
    fig.autofmt_xdate()
    plt.xlabel(f"Daily {ylabel.lower()} — {label}")
    plt.ylabel(ylabel)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf
