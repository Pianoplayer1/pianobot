from discord.ext import commands
from functions.db import query

class On_guild_remove(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f'Left {guild.name}')
        query("DELETE FROM servers WHERE id = %s;", guild.id)

def setup(client):
    client.add_cog(On_guild_remove(client))