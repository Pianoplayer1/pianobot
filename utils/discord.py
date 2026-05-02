"""Discord interaction helpers shared across slash commands."""

from typing import TYPE_CHECKING, cast

from discord import Interaction, app_commands

from database import guilds, raids, snapshots, tracked_guilds

if TYPE_CHECKING:
    from client import Pianobot


async def guild_autocomplete(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Autocomplete from all known guilds (name or prefix match, case-insensitive)."""
    bot = cast("Pianobot", interaction.client)
    all_guilds = await guilds.all_known(bot.pool)
    current_l = current.lower()
    matches = [
        g
        for g in all_guilds
        if current_l in g.name.lower()
        or (g.prefix is not None and current_l in g.prefix.lower())
    ]
    choices: list[app_commands.Choice[str]] = []
    for g in matches[:25]:
        label = f"{g.name} [{g.prefix}]" if g.prefix else g.name
        choices.append(app_commands.Choice(name=label, value=g.name))
    return choices


async def tracked_guild_autocomplete(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Autocomplete only tracked guilds (name or prefix match, case-insensitive)."""
    bot = cast("Pianobot", interaction.client)
    all_t = await tracked_guilds.all_tracked(bot.pool)
    current_l = current.lower()
    matches = [
        g
        for g in all_t
        if current_l in g.name.lower()
        or (g.prefix is not None and current_l in g.prefix.lower())
    ]
    choices: list[app_commands.Choice[str]] = []
    for g in matches[:25]:
        label = f"{g.name} [{g.prefix}]" if g.prefix else g.name
        choices.append(app_commands.Choice(name=label, value=g.name))
    return choices


async def raid_autocomplete(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Autocomplete raid names containing `current` (case-insensitive)."""
    bot = cast("Pianobot", interaction.client)
    results = await raids.search(bot.pool, current, limit=25)
    return [app_commands.Choice(name=name, value=name) for _, name in results]


async def region_autocomplete(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Autocomplete distinct world-region prefixes from snapshots (e.g. 'EU')."""
    bot = cast("Pianobot", interaction.client)
    current_l = current.lower()
    regions = await snapshots.regions(bot.pool)
    filtered = [r for r in regions if current_l in r.lower()]
    return [app_commands.Choice(name=n, value=n) for n in filtered[:25]]
