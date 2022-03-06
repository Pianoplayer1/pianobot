from asyncio import gather

from corkus.objects import Member

from discord import Message
from discord.ext import commands
from discord.utils import get

from pianobot import Pianobot
from pianobot.utils import check_permissions, format_last_seen

class Vote(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(
        hidden=True,
        name='vote'
    )
    async def vote(self, ctx: commands.Context):
        if not check_permissions(ctx.author, ctx.channel, 'manage_channels'):
            return

        first_msg: Message = await ctx.send(
            'Please wait until I have posted every vote before you start voting,'
            ' I will notify you once you can vote.'
        )

        ranks = ['Owner', 'Chief', 'Strategist', 'Captain', 'Recruiter', 'Recruit']
        eden = await self.bot.corkus.guild.get('Eden')
        results = await gather(*[fetch(member) for member in eden.members])
        results = sorted(results, key=lambda x: (ranks.index(x['rank']), x['raw_time'], x['name']))
        await gather(*[send(ctx, member) for member in results])

        message = f'''
@everyone as decided somewhere above here, we will now vote on **every single member**'s rank, regardless of their current one! This was an idea to kind of clean up the rank distribution we have right now. In the above votes, you will find a member's ingame name, rank and inactivity time. Please take the time to look at each member and decide on their rank, even though it will take some time.
For more information about the general idea of this mega-vote, look at https://discord.com/channels/682671629213368351/727608200895135784/922212425263120465.

The reactions symbolize the following:
:baby:  - Citizen (Recruit)
{get(ctx.guild.emojis, name='sanglasis')}  - Legionnaire (Recruiter: able to access public bank)
:military_helmet:  - Legate (Captain: able to start wars)
:warning:  - Tribune (Strategist: able to do economy & access private bank)
:exclamation:  - Senate (Strategist)
:bangbang:  - Dux (Chief: able to manage the guild ingame, e.g. when it comes to rewards, allies, hq, banner...)

The exclamation marks aren't there without a reason, remember that everyone with three stars and above is able to manage the guild in some ways and to impact our relations to other guilds, especially those who get into the Senate.
For the votes on <@235781853179543553>, <@290191000813568001>, <@718558765988970616>, <@284500595920863233>, <@232178035841957899> and <@437305878257860608>, consider their Senate applications in #elections too.
Please refrain from memeing around on those votes, it's simply faster if you stay on topic and just vote.
                     
Start voting at the top by clicking here: {first_msg.jump_url}'''

        await ctx.send(message)
        await first_msg.edit(
            content = 'Please take some time to vote on **everything** below'
            ' (although you can probably ignore the first vote...)'
        )

async def fetch(member: Member) -> dict:
    player = await member.fetch_player()
    raw_days, display_time = format_last_seen(player)

    return {'name': member.username.replace('_', '\\_'), 'rank': member.rank.value.title(),
            'last_seen': display_time, 'raw_time': raw_days}

async def send(ctx: commands.Context, member: dict):
    msg: Message = await ctx.send(f'{member["name"]} ({member["rank"]}) - {member["last_seen"]}')
    await msg.add_reaction('👶')
    await msg.add_reaction(get(ctx.guild.emojis, name='sanglasis'))
    await msg.add_reaction('🪖')
    await msg.add_reaction('⚠️')
    await msg.add_reaction('❗')
    await msg.add_reaction('‼️')

def setup(bot: Pianobot):
    bot.add_cog(Vote(bot))
