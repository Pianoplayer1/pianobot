from asyncio import gather
from logging import getLogger

from corkus import Corkus
from corkus.errors import CorkusTimeoutError
from corkus.objects.online_players import OnlinePlayers

from pianobot import Pianobot

async def guild_activity(bot: Pianobot):
    guilds = {guild: None for guild in bot.tracked_guilds}

    players = await bot.corkus.network.online_players()
    results = await gather(*[fetch(bot.corkus, guild, players) for guild in guilds])

    for res in results:
        if res is not None:
            guilds.update(res)
    if len(guilds) != len(bot.tracked_guilds):
        return

    bot.database.guild_activity.add(guilds)

    bot.database.guild_activity.cleanup()

async def fetch(corkus: Corkus, guild_name: str, players: OnlinePlayers) -> dict[str, int]:
    try:
        guild = await corkus.guild.get(guild_name)
        return {guild.name: sum(players.is_player_online(m.username) for m in guild.members)}
    except (CorkusTimeoutError, KeyError, TypeError):
        getLogger('tasks').warning('Error when fetching %s\'s activity!', guild_name)
        return {}
