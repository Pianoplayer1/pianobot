from discord.ext import commands
from ..utils.db import query
from ..utils.table import table
from math import floor
import time

class Soulpoints(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(name = 'soulpoints', aliases = ['sp'], brief = 'Returns a list of the next Wynncraft servers that will give you soul points.', help = 'If you are low on soul points, you can join one of the servers the bot returns to get one or two soul points soon. The timers of the bot are not 100% accurate, so if you do not get a soul point in the displayed time after joining the server, you may join another one from the top of the list.')
    async def soulpoints(self, ctx):
        data = [[server, f'{floor(20 - ((time.time() - uptime) / 60) % 20):02}:{floor((1200 - (time.time() - uptime) % 1200) % 60):02} minutes',
                 f'{floor((time.time() - uptime) / 3600):02}:{floor((time.time() - uptime) % 3600 / 60):02} hours']
                for server, uptime in sorted(query("SELECT * FROM worlds"), key = lambda item: (time.time() - item[1]) % 1200, reverse = True)]

        columns = {"Server" : 10, "Next Soul Point" : 18, "Uptime" : 18}
        await ctx.send(table(columns, data[:20])[0])

def setup(client):
    client.add_cog(Soulpoints(client))