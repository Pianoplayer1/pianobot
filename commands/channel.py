from discord.ext import commands
from functions.db import query

class Channel(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(name = 'channel', brief = 'Sets the current channel for displaying future territory change messages.', help = 'Using this command will set the channel in that the command was typed in as the territory log channel. If any guild captures a territory from Eden on Eden\'s claim, a message will be sent in the such specified channel.', hidden = True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def channel(self, ctx):
        query("UPDATE servers SET channel = %s WHERE id = %s;", (ctx.channel.id, ctx.guild.id))
        await ctx.send(f'Channel changed to #{ctx.channel.name}')

def setup(client):
    client.add_cog(Channel(client))