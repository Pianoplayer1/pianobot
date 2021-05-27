from discord.ext import commands, tasks
from functions.update_database import territory, guilds, worlds

class On_ready(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Booted up')
        self.loop_10s.start()
        self.loop_1m.start()

    @tasks.loop(seconds=10)
    async def loop_10s(self):
        await territory(self.client)
        await worlds()

    @tasks.loop(seconds=60)
    async def loop_1m(self):
        await guilds()

def setup(client):
    client.add_cog(On_ready(client))