from discord import Message
from discord.ext import commands

from ..bot import Pianobot
from ..utils.permissions import check_permissions

class Vote(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(name='vote',
                      hidden=True)
    async def vote(self, ctx: commands.Context, new: str):
        if not check_permissions(ctx.author, ctx.channel, 'administrator'):
            return

        eden = await self.bot.corkus.guild.get('Eden')
        for member in eden.members[:4]:
            msg: Message = await ctx.send(f'{member.name} ({member.rank})')
            await msg.add_reaction(':white_check_mark:')
            await msg.add_reaction(':no_entry:')
            await msg.add_reaction('man_shrugging')

def setup(bot: Pianobot):
    bot.add_cog(Vote(bot))
