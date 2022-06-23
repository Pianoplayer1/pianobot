from datetime import datetime
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

            uuid, ashcon_date = await ashcon(self.bot.session, player_data.username)
            hypixel_date = await hypixel(self.bot.session, uuid)

            first_wynncraft_login = player_data.join_date.replace(tzinfo=None)
            wynncraft_playtime = floor(player_data.playtime.raw * 4.7 / 60)
            wynncraft_rank = player_data.tag.value
            wynncraft_level = 0
            wynncraft_quests = 0
            for player_class in player_data.classes:
                wynncraft_quests += len(player_class.quests)
                wynncraft_level += player_class.combined_level

            oldest_date = min(
                date
                for date in [
                    hypixel_date,
                    first_wynncraft_login,
                    ashcon_date,
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
                min(int((datetime.utcnow() - first_wynncraft_login).days / 2), 100),
                min(wynncraft_playtime, 100),
                min(wynncraft_level / 10, 100),
                min(wynncraft_quests / 2, 100),
                50 if wynncraft_rank == 'PLAYER' else (80 if wynncraft_rank == 'VIP' else 100),
                min(int((datetime.utcnow() - oldest_date).days / 10), 100),
            ]
            total_score = round(100 - sum(scores) / len(scores), 2)

            embed = Embed(
                color=0x00FF00
                if total_score <= 40
                else (0xFF0000 if total_score <= 20 else 0xFFFF00),
                description='The rating is based on following components:',
                title=f'Suspiciousness of {player_data.username}: {total_score}%',
            )
            embed.set_thumbnail(
                url=f'https://mc-heads.net/avatar/{player_data.uuid.string(dashed=False)}',
            )
            for field, category, score in zip(embed_fields, embed_values, scores):
                embed.add_field(
                    inline=True, name=field, value=f'{category}\n{round(100 - score, 2)}% sus'
                )
            await ctx.send(embed=embed)


async def ashcon(session: ClientSession, player: str) -> tuple[str, datetime | None]:
    response = await (await session.get(f'https://api.ashcon.app/mojang/v2/user/{player}')).json()
    uuid = response['uuid']
    first_name_change = (
        datetime.strptime(response['username_history'][1]['changed_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if len(response['username_history']) > 1
        else None
    )
    created_at = (
        datetime.strptime(response['created_at'], '%Y-%m-%d') if response['created_at'] else None
    )
    return uuid, min(
        (date for date in (first_name_change, created_at) if date is not None), default=None
    )


async def hypixel(session: ClientSession, uuid: str) -> datetime | None:
    response = await (
        await session.get(
            'https://api.hypixel.net/player',
            params={'key': 'd9a6b029-99ea-4620-ba52-6df35c61486b', 'uuid': uuid},
        )
    ).json()
    return (
        datetime.utcfromtimestamp(response['player']['firstLogin'] / 1000)
        if response['player'] and response['player']['firstLogin']
        else None
    )


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(Sus(bot))
