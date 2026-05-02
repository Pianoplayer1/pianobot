"""`/wynn` slash group: general Wynncraft-network info."""

from __future__ import annotations

import io
from datetime import UTC, datetime
from math import floor
from typing import TYPE_CHECKING

from discord import File, Interaction, app_commands
from matplotlib import dates as mdates
from matplotlib import pyplot as plt

from database import snapshots, world_state
from utils import region_autocomplete, smooth_series
from views import send_table_response

if TYPE_CHECKING:
    from client import Pianobot


_REGIONS = {"NA": "North America", "EU": "Europe", "AS": "Asia"}


class WynnCommands(app_commands.Group, name="wynn"):
    """General Wynncraft network info."""

    def __init__(self, bot: Pianobot) -> None:
        """Bind the group to its owning bot for pool/api access."""
        super().__init__()
        self.bot = bot

    @app_commands.command()
    async def worlds(self, interaction: Interaction) -> None:
        """List currently online Wynncraft worlds, sorted by uptime."""
        await interaction.response.defer(thinking=True)
        now = datetime.now(UTC)
        stored = await world_state.all_worlds(self.bot.pool)
        entries = [(w.name, int((now - w.started_at).total_seconds())) for w in stored]
        entries.sort(key=lambda x: x[1], reverse=True)
        rows = [
            [
                name,
                _REGIONS.get(name[:2], "Unknown"),
                f"{floor(uptime / 3600):02}:{floor((uptime % 3600) / 60):02} hours",
            ]
            for name, uptime in entries
        ]
        columns = {"Server": 10, "Region": 18, "Uptime": 18}
        await send_table_response(
            interaction,
            columns,
            rows,
            page_size=20,
            separator_rows=0,
            enum=False,
        )

    @app_commands.command()
    @app_commands.describe(
        region="Restrict to one region, e.g. 'EU'",
        days="Number of days to plot (default: 1)",
    )
    @app_commands.autocomplete(region=region_autocomplete)
    async def history(
        self,
        interaction: Interaction,
        region: str | None = None,
        days: int = 1,
    ) -> None:
        """Line graph of online player counts over time, optionally per region."""
        await interaction.response.defer(thinking=True)
        if days < 1:
            await interaction.followup.send("`days` must be at least 1.")
            return
        history = await snapshots.online_history(self.bot.pool, days, region)
        if not history:
            target = f"region `{region}`" if region else "any world"
            await interaction.followup.send(
                f"No data for {target} in the last {days} day(s)."
            )
            return
        fig, axes = plt.subplots()
        axes.plot(list(history.keys()), smooth_series(history.values()))  # type: ignore[arg-type]
        axes.xaxis.set_major_formatter(mdates.DateFormatter("%b %d, %H:%M"))  # type: ignore[no-untyped-call]
        axes.xaxis.set_label_position("top")
        fig.autofmt_xdate()
        label = f"Online Players on {region}*" if region else "Total Online Players"
        plt.xlabel(f"{label} — {days} Day{'' if days == 1 else 's'}")
        plt.ylabel("Player Count")
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        await interaction.followup.send(file=File(buf, filename="history.png"))
