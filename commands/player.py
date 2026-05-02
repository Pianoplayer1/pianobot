"""`/player` slash command group: stats, activity chart, alt-suspiciousness."""

from __future__ import annotations

import io
from datetime import UTC, date, datetime, timedelta
from math import floor
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from discord import Colour, Embed, File, Interaction, app_commands
from discord.utils import format_dt
from matplotlib import dates as mdates
from matplotlib import pyplot as plt

from api import NotFoundError, WynncraftError
from database import (
    completions,
    global_stats,
    guild_membership,
    guilds,
    players,
    snapshots,
    xp_daily,
)
from views import send_table_response

if TYPE_CHECKING:
    from client import Pianobot


def _sus_field(
    embed: Embed, title: str, value: float, max_value: int, text: str | None = None
) -> float:
    sus_score = 100 - min(100 * value / max_value, 100)
    embed.add_field(
        name=title,
        value=f"```hs\n{text or value:<12}\n{round(sus_score, 2)}% sus```",
    )
    return sus_score


class PlayerCommands(app_commands.Group, name="player"):
    """Per-player stats and profile info."""

    def __init__(self, bot: Pianobot) -> None:
        """Bind the group to its owning bot for pool/api access."""
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(player="Wynncraft username or UUID")
    async def stats(self, interaction: Interaction, player: str) -> None:
        """Profile stats (playtime, level, quests, raids, and more from the DB)."""
        await interaction.response.defer(thinking=True)
        try:
            p = await self.bot.api.get_player(player)
        except NotFoundError:
            await interaction.followup.send(f"Player `{player}` not found.")
            return
        except WynncraftError as exc:
            await interaction.followup.send(f"Wynncraft API error: {exc}")
            return

        embed = Embed(
            title=p.username,
            colour=0x00AA88 if p.online else 0x888888,
            timestamp=datetime.now(UTC),
        )
        embed.set_thumbnail(url=f"https://mc-heads.net/avatar/{p.uuid.hex}")
        if p.online and p.server:
            status = f"Online on `{p.server}`"
        elif p.last_online is not None:
            status = f"Last seen {format_dt(p.last_online, 'R')}"
        else:
            status = "Unknown"
        embed.add_field(name="Status", value=status, inline=False)
        first_join = format_dt(p.joined, "R") if p.joined else "Unknown"
        embed.add_field(name="First join", value=first_join, inline=True)
        embed.add_field(
            name="Playtime", value=f"{round(p.playtime)} hours", inline=True
        )
        embed.add_field(name="Rank", value=p.rank or "Player", inline=True)
        embed.add_field(name="Total level", value=str(p.total_level), inline=True)
        embed.add_field(name="Quests", value=str(p.completed_quests), inline=True)
        embed.add_field(
            name="Raids / Dungeons",
            value=f"{p.total_raids} / {p.total_dungeons}",
            inline=True,
        )

        db = await global_stats.get(self.bot.pool, p.uuid)
        if db:

            def _v(val: int | None) -> str:
                return str(val) if val is not None else "?"

            embed.add_field(name="Wars", value=_v(db["wars"]), inline=True)
            embed.add_field(name="Lootruns", value=_v(db["lootruns"]), inline=True)
            embed.add_field(name="Caves", value=_v(db["caves"]), inline=True)
            embed.add_field(
                name="Mobs killed", value=_v(db["mobs_killed"]), inline=True
            )
            embed.add_field(
                name="Chests found", value=_v(db["chests_found"]), inline=True
            )
            embed.add_field(
                name="World events", value=_v(db["world_events"]), inline=True
            )
            embed.add_field(
                name="PvP",
                value=f"{_v(db['pvp_kills'])} kills / {_v(db['pvp_deaths'])} deaths",
                inline=True,
            )
            if (cc := db["content_completion"]) is not None:
                embed.add_field(name="Content completion", value=f"{cc}%", inline=True)

        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.describe(
        player="Wynncraft username or UUID",
        days="Number of days to include (1-30, default: 14)",
    )
    async def activity(
        self, interaction: Interaction, player: str, days: int = 14
    ) -> None:
        """Bar chart of the player's daily online minutes for the last N days."""
        await interaction.response.defer(thinking=True)
        days = max(1, min(30, days))
        try:
            p = await self.bot.api.get_player(player)
        except NotFoundError:
            await interaction.followup.send(f"Player `{player}` not found.")
            return
        except WynncraftError as exc:
            await interaction.followup.send(f"Wynncraft API error: {exc}")
            return
        history = await snapshots.daily_history(self.bot.pool, p.uuid, days)
        if not history:
            await interaction.followup.send(
                f"No activity data recorded for `{p.username}` yet. Data is"
                " collected from the moment the bot first saw them online."
            )
            return
        today = datetime.now(UTC).date()
        days_list: list[date] = [
            today - timedelta(days=i) for i in range(days - 1, -1, -1)
        ]
        minutes = [history.get(d, 0) for d in days_list]
        fig, axes = plt.subplots()
        axes.bar(days_list, minutes, color="steelblue")  # type: ignore[arg-type]
        axes.xaxis.set_major_formatter(
            mdates.DateFormatter("%b %d")  # type: ignore[no-untyped-call]
        )
        axes.xaxis.set_label_position("top")
        fig.autofmt_xdate()
        plt.xlabel(f"Daily online minutes — {p.username} ({days} days)")
        plt.ylabel("Minutes")
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        await interaction.followup.send(file=File(buf, filename="player-activity.png"))

    @app_commands.command()
    @app_commands.describe(player="Wynncraft username or UUID")
    async def sus(self, interaction: Interaction, player: str) -> None:
        """Approximate probability of a player being an alt account."""
        await interaction.response.defer(thinking=True)
        try:
            p = await self.bot.api.get_player(player)
        except NotFoundError:
            await interaction.followup.send(f"Player `{player}` not found.")
            return
        except WynncraftError as exc:
            await interaction.followup.send(f"Wynncraft API error: {exc}")
            return

        embed = Embed(
            description=f"## Suspiciousness of {p.username}: ",
            timestamp=datetime.now(UTC),
        )
        embed.set_footer(text=Pianobot)
        embed.set_thumbnail(url=f"https://visage.surgeplay.com/face/{p.uuid.hex}")

        total = 0.0
        if p.joined is not None:
            total += _sus_field(
                embed,
                "Join Date",
                (datetime.now(UTC) - p.joined).days,
                500,
                p.joined.strftime("%b %d, %Y"),
            )
        else:
            total += _sus_field(embed, "Join Date", 0, 500, "Unknown")
        rank_label = p.support_rank or "player"
        total += _sus_field(
            embed,
            "Rank",
            {"player": 50, "vip": 80}.get(rank_label, 100),
            100,
            f"[{rank_label}]",
        )
        total += _sus_field(
            embed, "Total Playtime", p.playtime, 500, f"{floor(p.playtime)} Hours"
        )
        total += _sus_field(embed, "Total Level", p.total_level, 1000)
        total += _sus_field(embed, "Quests", p.completed_quests, 300)
        total += _sus_field(
            embed, "Dungeons & Raids", p.total_dungeons + p.total_raids, 200
        )
        total /= 6
        if embed.description is not None:
            embed.description += f"{total:.2f}%"
        red = 255 if total >= 25 else round(255 * total / 25)
        green = 255 if total <= 75 else round(255 * (total - 75) / 25)
        embed.colour = Colour((red << 16) + (green << 8))
        await interaction.followup.send(embed=embed)

    @app_commands.command()
    @app_commands.describe(player="Wynncraft username or UUID")
    async def history(self, interaction: Interaction, player: str) -> None:
        """Guild + rank + name history we've observed for a player."""
        await interaction.response.defer(thinking=True)
        uuid = await _resolve_uuid(self.bot, player)
        if uuid is None:
            await interaction.followup.send(f"Player `{player}` not found.")
            return

        events = await guild_membership.events_for_player(self.bot.pool, uuid)
        renames = await players.username_history(self.bot.pool, uuid)
        guild_names = await guilds.name_by_uuid(self.bot.pool)
        current = await players.get_by_uuid(self.bot.pool, uuid)
        membership = await guild_membership.get(self.bot.pool, uuid)

        rows: list[list[str]] = []
        for change in renames:
            rows.append(
                [
                    format_dt(change.changed_at, "f"),
                    "renamed",
                    f"{change.old_username} to {change.new_username}",
                ]
            )
        for event in events:
            guild_name = guild_names.get(event.guild_uuid, str(event.guild_uuid))
            if event.event_type == "rank_change":
                detail = f"{event.old_rank} to {event.new_rank} in {guild_name}"
            elif event.event_type == "join":
                detail = f"joined {guild_name} as {event.new_rank or '?'}"
            else:
                detail = f"left {guild_name}"
            rows.append([format_dt(event.occurred_at, "f"), event.event_type, detail])
        if not rows:
            await interaction.followup.send(
                f"No history recorded for `{current.username if current else player}`."
            )
            return
        rows.sort(key=lambda r: r[0])
        leading = f"History for **{current.username if current else player}**"
        if membership and (gname := guild_names.get(membership.guild_uuid)):
            leading += f" — currently {membership.rank} in {gname}."
        else:
            leading += " — currently guildless."
        columns = {"When": 30, "Event": 14, "Detail": 36}
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=15,
            separator_rows=0,
            enum=False,
            leading_text=leading,
        )

    @app_commands.command()
    @app_commands.describe(
        player="Wynncraft username or UUID",
        metric="Which series to plot (default: xp)",
        days="Number of days to plot (default: 30)",
    )
    async def graph(
        self,
        interaction: Interaction,
        player: str,
        metric: Literal["xp", "raids", "wars"] = "xp",
        days: int = 30,
    ) -> None:
        """Daily XP/raids/wars history for a player as a bar chart."""
        await interaction.response.defer(thinking=True)
        if days < 1:
            await interaction.followup.send("`days` must be at least 1.")
            return
        uuid = await _resolve_uuid(self.bot, player)
        if uuid is None:
            await interaction.followup.send(f"Player `{player}` not found.")
            return

        since_dt = datetime.now(UTC) - timedelta(days=days)
        if metric == "xp":
            history = await xp_daily.daily_for_player(
                self.bot.pool, uuid, since_dt.date()
            )
            ylabel = "XP gained"
            history_int = {d: int(v) for d, v in history.items()}
        elif metric == "raids":
            history_int = await completions.daily_raid_counts_for_player(
                self.bot.pool, uuid, since_dt
            )
            ylabel = "Raid completions"
        else:
            history_int = await completions.daily_war_counts_for_player(
                self.bot.pool, uuid, since_dt
            )
            ylabel = "War completions"

        if not history_int:
            await interaction.followup.send(
                f"No {metric} history recorded for that player."
            )
            return
        username = (
            (await players.get_by_uuid(self.bot.pool, uuid)).username  # type: ignore[union-attr]
            if (await players.get_by_uuid(self.bot.pool, uuid))
            else player
        )
        png = _bar_chart(history_int, days, ylabel, f"{username} — {metric}")
        await interaction.followup.send(file=File(png, filename="player-graph.png"))


async def _resolve_uuid(bot: Pianobot, query: str) -> UUID | None:
    """Resolve a username or UUID string to a UUID using the local DB first."""
    try:
        return UUID(query)
    except ValueError:
        pass
    if uuid := await players.resolve_username(bot.pool, query):
        return uuid
    # Fallback: try the live API
    try:
        info = await bot.api.get_player(query)
    except (NotFoundError, WynncraftError):
        return None
    return info.uuid


def _bar_chart(
    history: dict[date, int], days: int, ylabel: str, label: str
) -> io.BytesIO:
    """Render a per-day bar chart and return the PNG buffer."""
    today = datetime.now(UTC).date()
    days_list: list[date] = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    values = [history.get(d, 0) for d in days_list]
    fig, axes = plt.subplots()
    axes.bar(days_list, values, color="steelblue")  # type: ignore[arg-type]
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))  # type: ignore[no-untyped-call]
    axes.xaxis.set_label_position("top")
    fig.autofmt_xdate()
    plt.xlabel(f"Daily {ylabel.lower()} — {label} ({days} days)")
    plt.ylabel(ylabel)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf
