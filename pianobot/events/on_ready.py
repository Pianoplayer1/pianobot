from logging import getLogger
from time import perf_counter

from discord.ext.commands import Cog
from discord.ext.tasks import loop

from pianobot import Pianobot
from pianobot.tasks import (
    add_discord_member_roles,
    add_discord_members,
    add_discord_roles,
    guild_activity,
    guild_leaderboard,
    member_activity,
    territories,
    worlds,
    guild_xp
)

class OnReady(Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot
        self.logger = getLogger('tasks')

    @Cog.listener()
    async def on_ready(self):
        self.bot.logger.info('Booted up')
        self.loop_once.start()
        self.loop_30s.start()
        self.loop_1m.start()
        self.loop_5m.start()

    @loop(count=1)
    async def loop_once(self):
        start = perf_counter()
        await add_discord_members(self.bot)
        self.logger.debug('Discord members finished in %s seconds', perf_counter() - start)
        start = perf_counter()
        await add_discord_roles(self.bot)
        self.logger.debug('Discord roles finished in %s seconds', perf_counter() - start)
        start = perf_counter()
        await add_discord_member_roles(self.bot)
        self.logger.debug('Discord member roles finished in %s seconds', perf_counter() - start)

    @loop(seconds=30)
    async def loop_30s(self):
        start = perf_counter()
        await territories(self.bot)
        self.logger.debug('Territory finished in %s seconds', perf_counter() - start)
        start = perf_counter()
        await worlds(self.bot)
        self.logger.debug('World finished in %s seconds', perf_counter() - start)

    @loop(seconds=60)
    async def loop_1m(self):
        start = perf_counter()
        await guild_leaderboard(self.bot)
        self.logger.debug('Guild Leaderboard finished in %s seconds', perf_counter() - start)
        start = perf_counter()
        await member_activity(self.bot)
        self.logger.debug('Member Activity finished in %s seconds', perf_counter() - start)

    @loop(seconds=300)
    async def loop_5m(self):
        start = perf_counter()
        await guild_activity(self.bot)
        self.logger.debug('Guild Activity finished in %s seconds', perf_counter() - start)
        start = perf_counter()
        await guild_xp(self.bot)
        self.logger.debug('Guild XP finished in %s seconds', perf_counter() - start)

def setup(bot: Pianobot):
    bot.add_cog(OnReady(bot))
