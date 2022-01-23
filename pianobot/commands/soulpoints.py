from math import floor
from time import time

from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import table

class Soulpoints(commands.Cog):
    def __init__(self, bot: Pianobot):
        self.bot = bot

    @commands.command(
        aliases = ['sp'],
        brief = 'Returns a list of the next Wynncraft servers that will give you soul points.',
        help =
            'If you are low on soul points, you can join one of the servers the bot returns to'
            ' get one or two soul points soon. The timers of the bot are not 100% accurate, so'
            ' if you do not get a soul point in the displayed time after joining the server,'
            ' you may join another one from the top of the list.',
        name = 'soulpoints'
    )
    async def soulpoints(self, ctx: commands.Context):
        worlds = [[world.world, world.time] for world in self.bot.database.worlds.get_all()]
        now = time()
        worlds = sorted(worlds, key = lambda item: (now - item[1]) % 1200, reverse = True)
        data = [
            [
                server,
                f'{floor(20 - ((now - uptime) / 60) % 20):02}:'
                    f'{floor((1200 - (now - uptime) % 1200) % 60):02} minutes',
                f'{floor((now - uptime) / 3600):02}'
                    f':{floor((now - uptime) % 3600 / 60):02} hours'
            ]
            for server, uptime in worlds
        ]

        columns = {'Server': 10, 'Next Soul Point': 18, 'Uptime': 18}
        await ctx.send(table(columns, data[:20])[0])

def setup(bot: Pianobot):
    bot.add_cog(Soulpoints(bot))
