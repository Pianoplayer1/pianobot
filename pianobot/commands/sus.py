from datetime import datetime
from math import floor

from aiohttp import ClientSession
from corkus.errors import BadRequest
from discord import Embed, Interaction, app_commands
from discord.ext import commands

from pianobot import Pianobot


class LegacySus(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        aliases=['alt'],
        brief='Check the suspiciousness of a player.',
        help='View the approximate probability of a player being an alt account.',
        name='sus',
        usage='<player>',
    )
    async def sus(self, ctx: commands.Context, player: str) -> None:
        await ctx.trigger_typing()

        # Ashcon API
        try:
            async with ClientSession() as session, session.get(
                'https://api.ashcon.app/mojang/v2/user/' + player
            ) as res:
                response = await res.json()
                uuid = response['uuid']
                first_name_change = (
                    datetime.strptime(
                        response['username_history'][1]['changed_at'], '%Y-%m-%dT%H:%M:%S.%fZ'
                    )
                    if len(response['username_history']) > 1
                    else None
                )
                ashcon_created = (
                    datetime.strptime(response['created_at'], '%Y-%m-%d')
                    if response['created_at']
                    else None
                )
        except KeyError:
            await ctx.send('Not a minecraft username!')
            return

        # Wynncraft API
        try:
            player_data = await self.bot.corkus.player.get(player)
        except BadRequest:
            await ctx.send('Not a valid Wynncraft player!')
            return

        first_wynncraft_login = player_data.join_date.replace(tzinfo=None)
        wynncraft_playtime = floor(player_data.playtime.raw * 4.7 / 60)
        wynncraft_rank = player_data.tag.value

        wynncraft_level = 0
        wynncraft_quests = 0
        for player_class in player_data.classes:
            wynncraft_quests += len(player_class.quests)
            wynncraft_level += player_class.combined_level

        # Hypixel API
        async with ClientSession() as session, session.get(
            'https://api.hypixel.net/player',
            params={'key': 'd9a6b029-99ea-4620-ba52-6df35c61486b', 'uuid': uuid},
        ) as res:
            response = await res.json()
            first_hypixel_login = None
            if response['player'] and response['player']['firstLogin']:
                first_hypixel_login = datetime.utcfromtimestamp(
                    response['player']['firstLogin'] / 1000
                )

        oldest_date = min(
            date
            for date in [
                first_hypixel_login,
                first_wynncraft_login,
                ashcon_created,
                first_name_change,
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
        categories = [
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
            min(
                ['PLAYER', None, 'VIP', 'VIP+', 'HERO', 'CHAMPION'].index(wynncraft_rank) * 25, 100
            ),
            min(int((datetime.utcnow() - oldest_date).days / 10), 100),
        ]
        total_score = round(100 - sum(scores) / len(scores), 2)

        embed = Embed(
            color=0x00FF00 if total_score < 40 else (0xFF0000 if total_score < 20 else 0xFFFF00),
            description='The rating is based on following components:',
            title=f'Suspiciousness of {player}: {total_score}%',
        )
        for field, category, score in zip(embed_fields, categories, scores):
            embed.add_field(
                inline=True, name=field, value=f'{category}\n{round(100 - score, 2)}% sus'
            )
        await ctx.send(embed=embed)


async def ashcon(session: ClientSession, player: str) -> tuple[str, datetime | None]:
    response = await (await session.get('https://api.ashcon.app/mojang/v2/user/' + player)).json()
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


class Sus(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @app_commands.command(description='The rough probability of a player being an alt account')
    @app_commands.describe(player='The player to check for')
    async def sus(self, interaction: Interaction, player: str) -> None:
        await interaction.response.defer()
        try:
            uuid, ashcon_date = await ashcon(self.bot.session, player)
        except KeyError:
            await interaction.followup.send('Not a minecraft username!')
            return
        hypixel_date = await hypixel(self.bot.session, uuid)

        try:
            player_data = await self.bot.corkus.player.get(player)
        except BadRequest:
            await interaction.followup.send('Not a valid Wynncraft player!')
            return

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
            color=0x00FF00 if total_score <= 40 else (0xFF0000 if total_score <= 20 else 0xFFFF00),
            description='The rating is based on following components:',
            title=f'Suspiciousness of {player_data.username}: {total_score}%',
        )
        for field, category, score in zip(embed_fields, embed_values, scores):
            embed.add_field(
                inline=True, name=field, value=f'{category}\n{round(100 - score, 2)}% sus'
            )
        await interaction.followup.send(embed=embed)


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(LegacySus(bot))
    await bot.add_cog(Sus(bot))
