"""`/eden` Eden-only stats and reward views."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from discord import Interaction, app_commands
from discord.utils import format_dt

from database import completions, eden, guild_membership, players
from utils import display_full, get_cycle, get_cycle_window, raid_autocomplete
from views import send_table_response

if TYPE_CHECKING:
    from client import Pianobot


def _format_interval(prefix: str, start: datetime | None, end: datetime | None) -> str:
    if start and not end:
        return f"{prefix} since {format_dt(start, style='D')}"
    if start and end:
        return (
            f"{prefix} between {format_dt(start, style='D')}"
            f" and {format_dt(end, style='D')}"
        )
    return prefix


class EdenCommands(app_commands.Group, name="eden"):
    """Eden member stats, contribution intervals, and pending reward views."""

    def __init__(self, bot: Pianobot) -> None:
        """Bind the group to its owning bot for pool/api access."""
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(sort_by="Which stat to rank by (default: raids)")
    async def awards(
        self,
        interaction: Interaction,
        sort_by: Literal["raids", "wars", "xp"] = "raids",
    ) -> None:
        """Current-cycle leaderboards for raids, wars, and guild XP."""
        await interaction.response.defer(thinking=True)
        now = datetime.now(UTC)
        cycle = get_cycle(now)
        start, end = get_cycle_window(now)
        pool = self.bot.pool
        eden_uuid = self.bot.eden_wynn_uuid
        raid_counts = await completions.raid_counts_by_username(
            pool, start, end, guild_uuid=eden_uuid
        )
        war_counts = await completions.war_counts_by_username(
            pool, start, end, guild_uuid=eden_uuid
        )
        xp_diff = await eden.xp_diff_by_username(pool, start, end)

        usernames = set(raid_counts) | set(war_counts) | set(xp_diff)
        rows_raw = [
            (
                name,
                raid_counts.get(name, 0),
                war_counts.get(name, 0),
                xp_diff.get(name, 0),
            )
            for name in usernames
        ]
        if sort_by == "xp":
            rows_raw.sort(key=lambda r: (r[3], r[1], r[2]), reverse=True)
        elif sort_by == "wars":
            rows_raw.sort(key=lambda r: (r[2], r[1], r[3]), reverse=True)
        else:
            rows_raw.sort(key=lambda r: (r[1], r[2], r[3]), reverse=True)
        rows = [[name, str(r), str(w), display_full(x)] for name, r, w, x in rows_raw]
        columns = {"Username": 22, "Guild Raids": 14, "Wars": 14, "Guild XP": 20}
        leading = (
            f"Current Eden Award leaderboards for cycle `{cycle}`,"
            f" sorted by {sort_by}.\n"
            f"This promotion cycle will end on {format_dt(end)}."
        )
        await send_table_response(
            interaction, columns, rows, page_size=15, leading_text=leading
        )

    @app_commands.command()
    @app_commands.describe(
        days_start="Days ago to start the interval (default: 7)",
        days_end="Days ago to end the interval (default: 0 = now)",
    )
    async def xp(
        self,
        interaction: Interaction,
        days_start: float = 7.0,
        days_end: float = 0.0,
    ) -> None:
        """Guild XP contributed by Eden members in an interval."""
        await interaction.response.defer(thinking=True)
        now = datetime.now(UTC)
        start = now - timedelta(days=days_start) if days_start else None
        end = now - timedelta(days=days_end) if days_end else None

        diffs = await eden.xp_diff_by_username(self.bot.pool, start, end)
        if not diffs:
            await interaction.followup.send("No guild XP gained in this interval.")
            return
        rows = [
            [name, display_full(xp)]
            for name, xp in sorted(diffs.items(), key=lambda x: x[1], reverse=True)
        ]
        columns = {"Username": 18, "Amount": 18}
        leading = _format_interval("Guild XP contributions", start, end) + ":"
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=20,
            separator_rows=0,
            enum=False,
            leading_text=leading,
        )

    @app_commands.command()
    @app_commands.describe(
        raid="Restrict to one specific raid (blank = all)",
        days_start="Days ago to start the interval (default: 7)",
        days_end="Days ago to end the interval (default: 0 = now)",
    )
    @app_commands.autocomplete(raid=raid_autocomplete)
    async def raids(
        self,
        interaction: Interaction,
        raid: str | None = None,
        days_start: float = 7.0,
        days_end: float = 0.0,
    ) -> None:
        """Guild raid completions per Eden member in an interval."""
        await interaction.response.defer(thinking=True)
        now = datetime.now(UTC)
        start = now - timedelta(days=days_start) if days_start else None
        end = now - timedelta(days=days_end) if days_end else None

        raid_id: int | None = None
        label = "Guild raid"
        if raid:
            raid_id = self.bot.raid_id_cache.get(raid)
            if raid_id is None:
                await interaction.followup.send(
                    f"Unknown raid `{raid}`. Pick one from the autocomplete."
                )
                return
            label = raid

        counts = await completions.raid_counts_by_username(
            self.bot.pool,
            start,
            end,
            raid_id=raid_id,
            guild_uuid=self.bot.eden_wynn_uuid,
        )
        if not counts:
            await interaction.followup.send("No guild raids in this interval.")
            return
        rows = [
            [name, str(count)]
            for name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]
        columns = {"Username": 22, "Amount": 8}
        leading = _format_interval(f"{label} completions", start, end) + ":"
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=20,
            separator_rows=0,
            enum=False,
            leading_text=leading,
        )

    @app_commands.command()
    @app_commands.describe(
        days_start="Days ago to start the interval (default: 7)",
        days_end="Days ago to end the interval (default: 0 = now)",
    )
    async def wars(
        self,
        interaction: Interaction,
        days_start: float = 7.0,
        days_end: float = 0.0,
    ) -> None:
        """Guild wars per Eden member in an interval."""
        await interaction.response.defer(thinking=True)
        now = datetime.now(UTC)
        start = now - timedelta(days=days_start) if days_start else None
        end = now - timedelta(days=days_end) if days_end else None

        counts = await completions.war_counts_by_username(
            self.bot.pool, start, end, guild_uuid=self.bot.eden_wynn_uuid
        )
        if not counts:
            await interaction.followup.send("No guild wars in this interval.")
            return
        rows = [
            [name, str(count)]
            for name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]
        columns = {"Username": 22, "Amount": 8}
        leading = _format_interval("Guild war completions", start, end) + ":"
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=20,
            separator_rows=0,
            enum=False,
            leading_text=leading,
        )

    @app_commands.command()
    @app_commands.describe(
        player="Show one player's full week-by-week history (default: weekly table)",
        week="ISO week to show (default: current; ignored if player set)",
        year="ISO year to show (default: current; ignored if player set)",
    )
    async def objective(
        self,
        interaction: Interaction,
        player: str | None = None,
        week: int | None = None,
        year: int | None = None,
    ) -> None:
        """Weekly objective status. No args = current week's table for Eden."""
        await interaction.response.defer(thinking=True)

        if player is not None:
            try:
                target = UUID(player)
            except ValueError:
                target = await players.resolve_username(self.bot.pool, player)  # type: ignore[assignment]
            if target is None:
                await interaction.followup.send(f"Player `{player}` not found.")
                return
            history = await eden.weekly_objective_history(self.bot.pool, target)
            if not history:
                await interaction.followup.send(
                    f"No objective history recorded for `{player}`."
                )
                return
            uname = (await players.get_by_uuid(self.bot.pool, target)) or None
            rows = [
                [
                    f"{y}-W{w:02}",
                    "yes" if completed else "no",
                    str(streak),
                ]
                for y, w, completed, streak in history
            ]
            columns = {"Week": 12, "Completed": 12, "Streak": 8}
            display_name = uname.username if uname else player
            leading = f"Weekly objective history for **{display_name}**"
            await send_table_response(
                interaction,
                columns,
                rows,
                page_size=15,
                separator_rows=0,
                enum=False,
                leading_text=leading,
            )
            return

        now = datetime.now(UTC).isocalendar()
        iso_week = week or now.week
        iso_year = year or now.year
        data = await eden.weekly_objective_for_week(self.bot.pool, iso_year, iso_week)
        if not data:
            await interaction.followup.send(
                f"No objective data for week `{iso_year}-W{iso_week:02}`."
                " (Token may not have Strategist+ access in Eden.)"
            )
            return
        membership = await guild_membership.by_guild(
            self.bot.pool, self.bot.eden_wynn_uuid
        )
        usernames = await players.usernames_by_uuid(
            self.bot.pool, [m.uuid for m in membership]
        )
        rows_raw: list[tuple[int, bool, list[str]]] = []
        for m in membership:
            entry = data.get(m.uuid)
            if entry is None:
                continue
            completed, streak = entry
            rows_raw.append(
                (
                    streak,
                    completed,
                    [
                        usernames.get(m.uuid, "?"),
                        m.rank,
                        "yes" if completed else "no",
                        str(streak),
                    ],
                )
            )
        rows_raw.sort(key=lambda r: (r[1], r[0]), reverse=True)
        rows = [r[2] for r in rows_raw]
        columns = {"Eden Member": 30, "Rank": 22, "Completed": 12, "Streak": 8}
        leading = f"Weekly objective for `{iso_year}-W{iso_week:02}`."
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=15,
            leading_text=leading,
        )

    @app_commands.command()
    @app_commands.describe(weeks="Number of recent weeks to show (default: 12)")
    async def objective_history(
        self, interaction: Interaction, weeks: int = 12
    ) -> None:
        """Aggregate weekly objective completion across Eden over recent weeks."""
        await interaction.response.defer(thinking=True)
        weeks = max(1, min(52, weeks))
        data = await eden.weekly_objective_aggregate(self.bot.pool, limit=weeks)
        if not data:
            await interaction.followup.send("No objective history recorded yet.")
            return
        rows = [
            [
                f"{y}-W{w:02}",
                str(completed),
                str(total),
                f"{100 * completed // total}%" if total else "?",
            ]
            for y, w, completed, total in data
        ]
        columns = {"Week": 12, "Completed": 12, "Total": 8, "%": 6}
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=20,
            separator_rows=0,
            enum=False,
            leading_text="Weekly objective completion history (newest first):",
        )

    @app_commands.command()
    @app_commands.describe(show="Which slice of the balance to show (default: active)")
    async def emeralds(
        self,
        interaction: Interaction,
        show: Literal["active", "left", "blocked"] = "active",
    ) -> None:
        """Pending raid emeralds: active members, ex-members, or blocked list."""
        await interaction.response.defer(thinking=True)
        pool = self.bot.pool
        eden_uuid = self.bot.eden_wynn_uuid
        unit = eden.display_unit("emeralds")
        if show == "left":
            data = await eden.pending_emeralds_left(pool, eden_uuid)
            if not data:
                await interaction.followup.send(
                    "No pending emeralds owed to former members."
                )
                return
            rows = [
                [str(uuid), str(count // unit)]
                for uuid, count in sorted(
                    data.items(), key=lambda x: x[1], reverse=True
                )
            ]
            columns = {"UUID": 40, "Pending LE": 12}
        elif show == "blocked":
            names = await eden.blocked_list(pool, eden_uuid, "emeralds")
            if not names:
                await interaction.followup.send(
                    "No members are currently blocked from receiving emeralds."
                )
                return
            await interaction.followup.send(
                "Blocked from emeralds:\n" + "\n".join(sorted(names))
            )
            return
        else:
            data_active = await eden.pending_emeralds_active(pool, eden_uuid)
            if not data_active:
                await interaction.followup.send("No new raids have been logged.")
                return
            rows = [
                [name, str(count // unit)]
                for name, count in sorted(
                    data_active.items(), key=lambda x: x[1], reverse=True
                )
                if count // unit > 0
            ]
            if not rows:
                await interaction.followup.send(
                    "No emeralds owed (all balances < 1 LE)."
                )
                return
            columns = {"Username": 22, "Pending LE": 12}
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=20,
            separator_rows=0,
            enum=False,
        )

    @app_commands.command()
    @app_commands.describe(show="Which slice of the balance to show (default: active)")
    async def aspects(
        self,
        interaction: Interaction,
        show: Literal["active", "left", "blocked"] = "active",
    ) -> None:
        """Pending aspects: active members, ex-members, or blocked list."""
        await interaction.response.defer(thinking=True)
        pool = self.bot.pool
        eden_uuid = self.bot.eden_wynn_uuid
        unit = eden.display_unit("aspects")
        if show == "left":
            data = await eden.pending_aspects_left(pool, eden_uuid)
            if not data:
                await interaction.followup.send(
                    "No pending aspects owed to former members."
                )
                return
            rows = [
                [str(uuid), str(count // unit)]
                for uuid, count in sorted(
                    data.items(), key=lambda x: x[1], reverse=True
                )
            ]
            columns = {"UUID": 40, "Pending Aspects": 17}
        elif show == "blocked":
            names = await eden.blocked_list(pool, eden_uuid, "aspects")
            if not names:
                await interaction.followup.send(
                    "No members are currently blocked from receiving aspects."
                )
                return
            await interaction.followup.send(
                "Blocked from aspects:\n" + "\n".join(sorted(names))
            )
            return
        else:
            data_active = await eden.pending_aspects_active(pool, eden_uuid)
            if not data_active:
                await interaction.followup.send("No new raids have been logged.")
                return
            now_dt = datetime.now(UTC)
            rows = []
            for name, (count, joined_at) in sorted(
                data_active.items(), key=lambda x: x[1][0], reverse=True
            ):
                if count // unit <= 0:
                    continue
                joined = joined_at if isinstance(joined_at, datetime) else now_dt
                recent = (now_dt - joined) < timedelta(days=7)
                rows.append([f"(* {name} *)" if recent else name, str(count // unit)])
            if not rows:
                await interaction.followup.send(
                    "No aspects owed (all balances < 1 aspect)."
                )
                return
            columns = {"Username": 22, "Pending Aspects": 17}
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=20,
            separator_rows=0,
            enum=False,
        )
