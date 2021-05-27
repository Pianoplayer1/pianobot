from discord.ext import commands, tasks
from functions.update_database import territory, guilds, worlds

class On_ready(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Booted up')
        self.loop.start()

    @tasks.loop(seconds=10)
    async def loop(self):
        await territory(self.client)
        await guilds()
        await worlds()

def setup(client):
    client.add_cog(On_ready(client))