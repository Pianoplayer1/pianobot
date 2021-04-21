from discord.ext import commands
from functions.db import query

class Cooldown(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(name = 'cooldown', aliases = ['cd', 'ping'], brief = 'Sets the interval in which the bot pings when Eden gets raided.', help = 'With this command, you can adjust the interval of war pings in minutes. To turn them off completely, you can use this command without setting a time.', usage = '[minutes]', hidden = True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def cooldown(self, ctx, new=0):
        query("UPDATE servers SET ping = %s WHERE id = %s;", (new*60, ctx.guild.id))
        if new == 0:
            await ctx.send(f'Territory ping toggled off')
        else:
            await ctx.send(f'Territory ping cooldown changed to {new} minutes')

def setup(client):
    client.add_cog(Cooldown(client))