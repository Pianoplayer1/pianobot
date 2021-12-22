from logging import getLogger
from time import time

from discord.ext.commands import Cog
from discord.ext.tasks import loop

from ..bot import Pianobot
from ..tasks import guild_activity, guild_leaderboard, territory, worlds, guild_xp

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
        await territory.run(self.bot)
        self.logger.info(f'Territory finished in {time() - start} seconds')
        start = time()
        await worlds.run(self.bot)
        self.logger.info(f'World finished in {time() - start} seconds')

    @loop(seconds=60)
    async def loop_1m(self):
        start = time()
        await guild_leaderboard.run(self.bot)
        self.logger.info(f'Guild Leaderboard finished in {time() - start} seconds')
    
    @loop(seconds=300)
    async def loop_5m(self):
        start = time()
        await guild_activity.run(self.bot)
        self.logger.info(f'Guild Activity finished in {time() - start} seconds')
        start = time()
        await guild_xp.run(self.bot)
        self.logger.info(f'Guild XP finished in {time() - start} seconds')

def setup(bot: Pianobot):
    bot.add_cog(OnReady(bot))
