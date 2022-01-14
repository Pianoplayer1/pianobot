from typing import Union

from discord import Role
from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import check_permissions

class Tracking(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(
        aliases = ['channel', 'cooldown', 'track'],
        brief = 'Lets you configure tracking for Eden\'s territories.',
        description = 'guild_only',
        help = (
            'This bot keeps track of Eden  \'s territory claim (configurable with'
            ' `[[prefix]]territories`) and sends messages when a territory gets taken, optionally'
            ' with a ping.\n\nUse `[[prefix]]tracking channel` to enable  tracking messages for'
            ' that channel, do that again to stop tracking.\n Set the cooldown between pings with'
            ' `[[prefix]]tracking ping <minutes>`, use 0 to disable pings completely.\n The role'
            ' that should get pinged is set with `[[prefix]]tracking role <id | mention>`, mention'
            ' the role or use its id for the second argument.'
        ),
        name = 'tracking',
        usage = '<channel | ping | role> [arguments]'
    )
    @commands.guild_only()
    async def tracking(self, ctx: commands.Context, action: str, arg: Union[int, Role] = None):
        if not check_permissions(ctx.author, ctx.channel, 'manage_channels'):
            await ctx.send('You don\'t have the required permissions to perform this action!')
            return
        current_server = self.bot.database.servers.get(ctx.guild.id)
        if action.lower() == 'channel':
            if current_server.channel == ctx.channel.id:
                self.bot.database.servers.update_channel(ctx.guild.id, 0)
                await ctx.send('Territory tracking toggled off.')
            else:
                self.bot.database.servers.update_channel(ctx.guild.id, ctx.channel.id)
                await ctx.send(f'Territory tracking will be sent in {ctx.channel.mention}.')
        elif action.lower() in ('cooldown', 'ping'):
            if arg is None:
                text = ('is currently disabled.' if current_server.ping == 0
                    else f'cooldown: `{int(current_server.ping / 60)} minutes`')
                await ctx.send(f'Territory ping {text}')
                return
            if not isinstance(arg, int):
                await ctx.send('You must specify the ping cooldown time in minutes!')
                return
            self.bot.database.servers.update_ping(ctx.guild.id, arg * 60)
            if arg == 0:
                await ctx.send('Territory ping toggled off.')
            else:
                await ctx.send(f'Territory ping cooldown changed to {arg} minutes.')
        elif action.lower() == 'role':
            if arg is None:
                current_role = ctx.guild.get_role(current_server.role)
                if current_role is None:
                    current_role = 'None'
                else:
                    current_role = f'`{current_role.name}`'
                await ctx.send(f'Territory ping role: {current_role}')
                return
            if isinstance(arg, int):
                arg = ctx.guild.get_role(arg)
            if not isinstance(arg, Role):
                await ctx.send('You must specify a valid role by its mention or its id!')
                return
            self.bot.database.servers.update_role(ctx.guild.id, arg.id)
            await ctx.send(f'Territory ping role changed to {arg.name}.')
        else:
            raise commands.BadArgument()

def setup(bot: Pianobot):
    bot.add_cog(Tracking(bot))
