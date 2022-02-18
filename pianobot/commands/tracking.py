from discord import Embed, Role
from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import check_permissions

class Tracking(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(
        aliases=['channel', 'cooldown', 'track'],
        brief='Lets you configure tracking for Eden\'s territories.',
        description='guild_only',
        help=
            'This bot keeps track of Eden  \'s territory claim (configurable with'
            ' `[[prefix]]territories`) and sends messages when a territory gets taken, optionally'
            ' with a ping.\n\nUse `[[prefix]]tracking channel` to enable  tracking messages for'
            ' that channel, do that again to stop tracking.\nSet the cooldown between pings with'
            ' `[[prefix]]tracking ping <minutes>`, use 0 to disable pings completely.\nThe role'
            ' that should get pinged is set with `[[prefix]]tracking role <id | mention>`, mention'
            ' the role or use its id for the second argument.\n To disable pings when a certain (or'
            ' above) rank is online, use `[[prefix]]tracking rank <no. of stars ingame>`.',
        name='tracking',
        usage='<channel | ping | role> [arguments]'
    )
    @commands.guild_only()
    async def tracking(self, ctx: commands.Context, action: str = '', arg: int | Role = None):
        if not check_permissions(ctx.author, ctx.channel, 'manage_channels'):
            await ctx.send('You don\'t have the required permissions to perform this action!')
            return
        current_server = self.bot.database.servers.get(ctx.guild.id)
        ranks = ['Recruit', 'Recruiter', 'Captain', 'Strategist', 'Chief', 'Owner']
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
        elif action.lower() == 'rank':
            current_rank = current_server.rank
            if arg is None:
                if current_rank == -1:
                    await ctx.send('Pings are always on, regardless of online members.')
                else:
                    await ctx.send(
                        f'Pings are disabled when at least one {ranks[current_rank]} is online.'
                    )
                return
            if not isinstance(arg, int) or arg < -1 or arg > 5:
                await ctx.send('You must specify a rank by its number of stars (ingame)!')
                return
            self.bot.database.servers.update_rank(ctx.guild.id, arg)
            if arg == -1:
                await ctx.send('Ping are now always active.')
            else:
                await ctx.send(
                    f'Pings will be deactivated when at least one {ranks[arg]} is online.'
                )
        else:
            channel = ctx.guild.get_channel(current_server.channel)
            role = ctx.guild.get_role(current_server.role)
            role_msg = 'does not ping' if role is None else f'pings {role.mention}'

            embed = Embed(
                description=(
                    f'Not active at the moment. Use `{current_server.prefix}tracking channel`'
                    ' to start territory tracking!'
                ) if current_server.channel is None else (
                    f'Currently running in {channel.mention}, {role_msg} if a territory gets taken.'
                ),
                color=0xffff00 if current_server.channel is None else 0x00ff00
            )
            embed.set_author(
                name='Eden Territory Tracking',
                icon_url=(
                    'https://cdn.discordapp.com/attachments/'
                    '784114583974445077/802578487252090950/eden100.png'
                )
            )
            embed.add_field(
                inline=False,
                name=(
                    f'Ping cooldown: {current_server.ping // 60} minutes'
                    if current_server.ping > 0 else 'Pings disabled'
                ),
                value=f'*Configure with* `{current_server.prefix}tracking ping <minutes>`*.*'
            )
            embed.add_field(
                inline=False,
                name=(
                    'Pings regardless of online members' if current_server.rank == -1
                    else f'Pings unless a {ranks[current_server.rank]} is online'
                ),
                value=(
                    f'*Configure with* `{current_server.prefix}tracking rank <stars>`*, '
                    'use -1 as value to ping regardless of online members.*'
                )
            )
            embed.set_footer(
                text=f'For more information, run `{current_server.prefix}help tracking`.'
            )
            await ctx.send(embed=embed)

def setup(bot: Pianobot):
    bot.add_cog(Tracking(bot))
