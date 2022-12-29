from datetime import datetime, timezone
from math import floor

from aiohttp import ClientSession
from corkus.errors import BadRequest
from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

from pianobot import Pianobot


class Sus(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @command(
        aliases=['alt'],
        brief='Check the suspiciousness of a player.',
        help='View the approximate probability of a player being an alt account.',
        name='sus',
        usage='<player>',
    )
    async def sus(self, ctx: Context[Bot], player: str) -> None:
        async with ctx.typing():
            try:
                player_data = await self.bot.corkus.player.get(player)
            except BadRequest:
                await ctx.send('Not a valid Wynncraft player!')
                return

            first_hypixel_login = await hypixel_api(self.bot.session, player_data.uuid.string())

            first_wynncraft_login = player_data.join_date
            wynncraft_playtime = floor(player_data.playtime.raw * 4.7 / 60)
            wynncraft_rank = player_data.tag.value
            wynncraft_level = 0
            wynncraft_quests = 0
            for character in player_data.characters:
                wynncraft_quests += len(character.quests)
                wynncraft_level += character.combined_level

            oldest_date = min(
                date
                for date in [
                    first_hypixel_login,
                    first_wynncraft_login,
                ]
                if date is not None
            )

            embed_fields = [
                'Wynncraft Join Date',
                'Wynncraft Playtime',
                'Wynncraft Level',
                'Wynncraft Quests',
                'Wynncraft Rank',
                'Minecraft Join Date',
            ]
            embed_values = [
                first_wynncraft_login.strftime('%B %d, %Y'),
                f'{wynncraft_playtime} hours',
                f'{wynncraft_level} (all classes)',
                f'{wynncraft_quests} (all classes)',
                wynncraft_rank.capitalize(),
                f'~{oldest_date.strftime("%B %d, %Y")}',
            ]
            scores = [
                min(int((datetime.now(timezone.utc) - first_wynncraft_login).days / 2), 100),
                min(wynncraft_playtime, 100),
                min(wynncraft_level / 10, 100),
                min(wynncraft_quests / 2, 100),
                50 if wynncraft_rank == 'PLAYER' else (80 if wynncraft_rank == 'VIP' else 100),
                min(int((datetime.now(timezone.utc) - oldest_date).days / 10), 100),
            ]
            total_score = round(100 - sum(scores) / len(scores), 2)

            embed = Embed(
                title=f'Suspiciousness of {player_data.username}: {total_score}%',
                description='The rating is based on following components:',
                color=0x00FF00
                if total_score <= 40
                else (0xFF0000 if total_score <= 20 else 0xFFFF00),
            )
            embed.set_thumbnail(
                url=f'https://mc-heads.net/avatar/{player_data.uuid.string(dashed=False)}'
            )
            for field, category, score in zip(embed_fields, embed_values, scores):
                embed.add_field(name=field, value=f'{category}\n{round(100 - score, 2)}% sus')
            await ctx.send(embed=embed)


async def hypixel_api(session: ClientSession, uuid: str) -> datetime | None:
    response = await (
        await session.get(
            'https://api.hypixel.net/player',
            params={'key': 'd9a6b029-99ea-4620-ba52-6df35c61486b', 'uuid': uuid},
        )
    ).json()
    return (
        datetime.fromtimestamp(response['player']['firstLogin'] / 1000, timezone.utc)
        if response['player'] and response['player']['firstLogin']
        else None
    )


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(Sus(bot))
