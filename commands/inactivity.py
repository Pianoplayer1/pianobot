from discord.ext import commands
from functions.inactivity import check_activity
from functions.pages import paginator
from functions.permissions import check_permissions
from functions.table import table
import aiohttp

class Inactivity(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name = 'inactivity', aliases = ['act', 'activity', 'inact'], brief = 'Outputs the member inactivity times of a specified guild.', help = 'This command returns a table with the times since each member of a specified guild has been last seen on the Wynncraft server. Use \'asc\' to display the results in ascending order, by default it will show the highest inactivity times first.', usage = '<guild> [asc|desc]')
    async def inactivity(self, ctx, *, guild):
        reverse = True
        if guild[-4:] == ' asc':
            guild = guild[:-4]
            reverse = False
        elif guild[-5:] == ' desc':
            guild = guild[:-5]

        async with aiohttp.ClientSession() as session, session.get(f'https://api.wynncraft.com/public_api.php?action=guildList') as response:
            guilds = await response.json()
            guilds = guilds['guilds']
            try:
                matches = [guilds[list(map(str.lower, guilds)).index(guild.lower())]]
            except ValueError:
                matches = [g for g in guilds if guild.lower() in g.lower()]
            if len(matches) == 0:
                await ctx.send(f'No guild names include \'{guild}\'. Please try again with another guild name.')
                return
            elif len(matches) == 1:
                guild = matches[0]
                message = None
            elif len(matches) <= 5:
                message = f'Several guild names include \'{guild}\'. Enter the number of one of the following guilds to view their inactivity.\nTo leave this prompt, type \'exit\'.\n'
                for match in range(len(matches)):
                    message += f'\n{match + 1}. {matches[match]}'
                message = await ctx.send(message)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                msg = await self.client.wait_for('message', check=check)
                if ctx.guild and check_permissions(self.client.user, ctx.channel, ['manage_messages']):
                    await msg.delete()
                
                try:
                    guild = matches[int(msg.content) - 1]
                except (IndexError, ValueError):
                    if msg.content == 'exit':
                        await message.edit(content = 'Prompt exited.')
                    else:
                        await message.edit(content = 'Invalid input, exited prompt.')
                    return
            else:
                await ctx.send(f'Several guild names include \'{guild}\'. Please try again with a more precise name.')
                return
            await paginator(self.client, ctx, table({f'{guild} Members' : 36, 'Rank' : 26, 'Time Inactive' : 26}, await check_activity(guild, reverse), 5, 15, True), message)

def setup(client):
    client.add_cog(Inactivity(client))