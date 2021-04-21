from discord.ext import commands
from functions.db import query

class On_guild_join(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f'Joined {guild.name}')
        query("INSERT INTO servers values (%s, '-', 0, 0, 0, 1800);", guild.id)

def setup(client):
    client.add_cog(On_guild_join(client))