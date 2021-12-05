from discord.ext import commands
from ..utils.db import query
from ..utils.table import table
from ..utils.pages import paginator
from ..utils.permissions import check_permissions
import aiohttp

class Territories(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(  name = 'territories',
                        aliases = ['terrs'],
                        brief = 'Lets you view and edit the territory list.',
                        help = 'Depending on the option you pass, you can either view a list of territories the bots listens to or add / delete territories from the list.',
                        usage = '<add|del|list> [territory], [territory] ...',
                        hidden = True  )
    @commands.guild_only()
    async def territories(self, ctx, action, *, territories = None):
        tlist = query("SELECT * FROM territories")
        tlist = dict(tlist)
        territories = territories.split(', ') if territories else []
        if action.lower() == 'list':
            await paginator(self.client, ctx, table({f'Territory' : len(max(list(tlist.keys()), key=len)) + 8, 'Guild' : len(max(list(tlist.keys()), key=len)) + 3}, list(tlist.items()), 10, 20, True))
        elif action.lower() == 'add':
            if not check_permissions(ctx.author, ctx.channel, ['manage_roles']):
                await ctx.send('You don\'t have the required permissions to perform this action!')
                return
            tlist = list(tlist.keys())
            async with aiohttp.ClientSession() as session, session.get('https://api.wynncraft.com/public_api.php?action=territoryList') as response:
                all_terrs = await response.json()
                all_terrs = list(all_terrs['territories'].keys())
                lower_terrs = list(map(str.lower, all_terrs))
                success = []
                failed = []
                for territory in territories:
                    if territory.lower() in lower_terrs:
                        territory = all_terrs[lower_terrs.index(territory.lower())]
                        if territory not in tlist:
                            query("INSERT INTO territories VALUES (%s,'None')", territory)
                            success.append(territory)
                        else:
                            failed.append(territory)
                    else:
                        failed.append(territory)
                message = ''
                if success:
                    message += f'Successfully added {len(success)} {"territories" if len(success) > 1 else "territory"} to the list!\n\n'
                if failed: 
                    message += f'Following {"territories" if len(failed) > 1 else "territory"} could not be added:\n'
                    for fail in failed:
                        message += f'-`{fail}`\n'
                if len(territories) == 0:
                    message = 'You have to specifiy at least one territory to add!'
                await ctx.send(message)
        elif action.lower() in ['del', 'delete']:
            if not check_permissions(ctx.author, ctx.channel, ['manage_roles']):
                await ctx.send('You don\'t have the required permissions to perform this action!')
                return
            tlist = list(tlist.keys())
            lower_tlist = list(map(str.lower, tlist))
            success = []
            failed = []
            for territory in territories:
                if territory.lower() in lower_tlist:
                    territory = tlist[lower_tlist.index(territory.lower())]
                    query("DELETE FROM territories WHERE name = %s", territory)
                    success.append(territory)
                else:
                    failed.append(territory)
            message = ''
            if success:
                message += f'Successfully removed {len(success)} {"territories" if len(success) > 1 else "territory"} from the list!\n\n'
            if failed:
                message += f'Following {"territories" if len(failed) > 1 else "territory"} could not be removed:\n'
                for fail in failed:
                    message += f'-`{fail}`\n'
            if len(territories) == 0:
                message = 'You have to specifiy at least one territory to remove!'
            await ctx.send(message)
        else:
            await ctx.send(f'Please enter a valid action! Refer to `{ctx.message.content[0]}help territories` for more information.')

def setup(client):
    client.add_cog(Territories(client))