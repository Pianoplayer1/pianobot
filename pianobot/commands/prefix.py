from discord import GroupChannel, User
from discord.ext.commands import Bot, Cog, Context, command, guild_only

from pianobot import Pianobot


class Prefix(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @command(
        aliases=['pre'],
        brief='Updates the bot prefix for this server.',
        description='guild_only',
        help=(
            'Use this command to set a new bot prefix, which will be used to access this bot on'
            ' this server. The prefix can consist of any letters, numbers and special characters,'
            ' but make sure it does not conflict with another bot.'
        ),
        name='prefix',
        usage='<new>',
    )
    @guild_only()
    async def prefix(self, ctx: Context[Bot], new: str) -> None:
        if (
            ctx.guild is None
            or isinstance(ctx.author, User)
            or isinstance(ctx.channel, GroupChannel)
        ):
            return
        if len(new) > 3:
            await ctx.send('A prefix cannot be longer than 3 characters!')
            return
        if not ctx.channel.permissions_for(ctx.author).manage_guild:
            await ctx.send('You don\'t have the required permissions to perform this action!')
            return
        await self.bot.database.servers.update_prefix(ctx.guild.id, new)
        await ctx.send(f'Prefix changed to \'{new}\'')


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(Prefix(bot))
