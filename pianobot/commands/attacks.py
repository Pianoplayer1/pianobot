from asyncio import gather
from time import time

from corkus.objects import Territory
from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

from pianobot import Pianobot


class Attacks(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @command(
        brief='Returns all territories of a guild that are getting attacked by Avomod users',
        help=(
            'When attacking a territory using Avomod, its defence is getting sent to a certain'
            ' endpoint so that defences can get synchronized within a guild. By checking this'
            ' endpoint for every territory of a guild, it is possible to see which territories'
            ' of that guild are currently getting attacked, which only works if the territory was'
            ' hit by somebody using Avomod who has not disabled this feature.'
        ),
        name='attacks',
    )
    async def attacks(self, ctx: Context[Bot], *, guild: str) -> None:
        async with ctx.typing():
            territories = await self.bot.corkus.territory.list_all()
            results: list[tuple[int, Embed | None]] = await gather(
                *[fetch(self.bot, t) for t in territories if t.guild.name == guild]
            )
            embeds = []
            for result in sorted(results, key=lambda x: x[0]):
                if result[1] is not None:
                    embeds.append(result[1])
            if embeds:
                for i in range(0, len(embeds), 10):
                    await ctx.send(embeds=embeds[i : i + 10])
            else:
                await ctx.send(f'No attacks on territories of `{guild}` have been found.')


async def fetch(bot: Pianobot, territory: Territory, tries: int = 0) -> tuple[int, Embed | None]:
    response = await bot.session.get(
        'https://script.google.com/macros/s/AKfycbw7lRN6tojW1RjsPeC7bhVNsGETBl_LZEc6bZKXAHG95HB_UC'
        f'4NKQMm9LGmuvT8KU-R-A/exec?territory={territory.name.replace(" ", "%20")}'
        f'&timestamp={int(time() * 1000)}'
    )
    text = await response.text()
    if text == 'null' or tries > 5:
        return -1, None
    if text.startswith('<'):
        return await fetch(bot, territory, tries + 1)

    defence, timestamp = text.split('|')
    color = 0x55FF55 if 'Low' in defence else (0xFFFF55 if defence == 'Medium' else 0xFF5555)
    formatted_time = f'<t:{int(timestamp) // 1000}:R>'
    return int(timestamp), Embed(
        color=color,
        title=f'{territory.name} ({defence})',
        description=f'Start of the war: {formatted_time}',
    )


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(Attacks(bot))
