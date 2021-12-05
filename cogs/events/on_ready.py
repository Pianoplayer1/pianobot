from ..bot import Pianobot
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from ..tasks import guild_activity, members, player_activity, territory, worlds

class OnReady(Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot
    
    @Cog.listener()
    async def on_ready(self):
        print('Booted up')
        self.loop_10s.start()
        self.loop_1m.start()
        self.loop_5m.start()

    @loop(seconds=10)
    async def loop_10s(self):
        await territory.run(self.bot)
        await worlds.run(self.bot)

    @loop(seconds=60)
    async def loop_1m(self):
        #await members.run(self.bot)
        await player_activity.run(self.bot)
    
    @loop(seconds=300)
    async def loop_5m(self):
        await guild_activity.run(self.bot)

def setup(bot : Pianobot):
    bot.add_cog(OnReady(bot))