from logging import getLogger
from time import time

from discord.ext.commands import Cog
from discord.ext.tasks import loop

from pianobot import Pianobot
from pianobot.tasks import (
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
        print('Bot booted up')
        self.loop_30s.start()
        self.loop_1m.start()
        self.loop_5m.start()

    @loop(seconds=30)
    async def loop_30s(self):
        start = time()
        await territories(self.bot)
        self.logger.info('Territory finished in %s seconds', time() - start)
        start = time()
        await worlds(self.bot)
        self.logger.info('World finished in %s seconds', time() - start)

    @loop(seconds=60)
    async def loop_1m(self):
        start = time()
        await guild_leaderboard(self.bot)
        self.logger.info('Guild Leaderboard finished in %s seconds', time() - start)
        start = time()
        await member_activity(self.bot)
        self.logger.info('Member Activity finished in %s seconds', time() - start)

    @loop(seconds=300)
    async def loop_5m(self):
        start = time()
        await guild_activity(self.bot)
        self.logger.info('Guild Activity finished in %s seconds', time() - start)
        start = time()
        await guild_xp(self.bot)
        self.logger.info('Guild XP finished in %s seconds', time() - start)

def setup(bot: Pianobot):
    bot.add_cog(OnReady(bot))
