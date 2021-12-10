from ..bot import Pianobot
from discord import Embed
from discord.ext import commands
from datetime import datetime
from math import floor

class Sus(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot

    @commands.command(  name = 'sus',
                        aliases = ['alt'],
                        brief = 'Check the suspiciousness of a player.',
                        help = 'View the approximate probability of a player being an alt account.',
                        usage = '<player>')
    async def sus(self, ctx : commands.Context, player : str):
        get_date_score = lambda date, maxValue : min(int((datetime.utcnow() - date).days / maxValue * 100), 100)

        # Ashcon API
        try:
            async with self.bot.session.get('https://api.ashcon.app/mojang/v2/user/' + player) as response:
                response = await response.json()
                uuid = response['uuid']
                first_name_change = datetime.strptime(response['username_history'][1]['changed_at'], '%Y-%m-%dT%H:%M:%S.%fZ') if len(response['username_history']) > 1 else None
                ashcon_created = datetime.strptime(response['created_at'], '%Y-%m-%d') if response['created_at'] else None
        except KeyError:
            await ctx.send('Not a minecraft username!')
            return


        # Wynncraft API
        try:
            async with self.bot.session.get(f'https://api.wynncraft.com/v2/player/{uuid}/stats') as response:
                response = await response.json()
                player_data = response['data'][0]
        except IndexError:
            await ctx.send('Not a valid Wynncraft player!')
            return

        first_wynncraft_login = datetime.strptime(player_data['meta']['firstJoin'], '%Y-%m-%dT%H:%M:%S.%fZ')
        first_wynncraft_login_score = get_date_score(first_wynncraft_login, 200)
        wynncraft_playtime = floor(player_data['meta']['playtime'] * 4.7 / 60)
        wynncraft_playtime_score = min(wynncraft_playtime, 100)
        wynncraft_rank = player_data['meta']['tag']['value'] if player_data['meta']['tag']['value'] else 'NONE'
        wynncraft_rank_score = min(['NONE', None, 'VIP', 'VIP+', 'HERO', 'CHAMPION'].index(wynncraft_rank) * 25, 100)

        wynncraft_level = 0
        wynncraft_quests = set()
        for player_class in player_data['classes']:
            wynncraft_quests.update(player_class['quests']['list'])
            wynncraft_level += player_class['level']
        wynncraft_level_score = min(wynncraft_level / 10, 100)
        wynncraft_quests_score = min(int(len(wynncraft_quests) / 2), 100)


        # Hypixel API
        async with self.bot.session.get('https://api.hypixel.net/player', params = {'key': 'd9a6b029-99ea-4620-ba52-6df35c61486b', 'uuid': uuid}) as response:
            response = await response.json()
            first_hypixel_login = None
            if response['player'] and response['player']['firstLogin']:
                first_hypixel_login = datetime.utcfromtimestamp(response['player']['firstLogin'] / 1000)


        oldest_date = min([date for date in [first_hypixel_login, first_wynncraft_login, ashcon_created, first_name_change] if date is not None])
        oldest_date_score = get_date_score(oldest_date, 1000)

        embed_fields = ['Wynncraft Join Date', 'Wynncraft Playtime', 'Wynncraft Level', 'Wynncraft Quests', 'Wynncraft Rank', 'Minecraft Join Date']
        categories = [first_wynncraft_login.strftime('%B %d, %Y'), f'{wynncraft_playtime} hours', f'{wynncraft_level} (all classes)', 
            f'{len(wynncraft_quests)} (all classes)', wynncraft_rank.capitalize(), f'~{oldest_date.strftime("%B %d, %Y")}']
        scores = [first_wynncraft_login_score, wynncraft_playtime_score, wynncraft_level_score, wynncraft_quests_score, wynncraft_rank_score, oldest_date_score]
        total_score = round(100 - sum(scores) / len(scores), 2)

        color = 0x00ff00
        if total_score >= 40:
            color = 0xff0000
        elif total_score >= 20:
            color = 0xffff00

        embed = Embed(title = 'Suspiciousness of ' + player + ': ' + str(total_score) + '%', description = 'The rating is based on following components:', color = color)
        for i, field in enumerate(embed_fields):
            embed.add_field(name = field, value = f'{categories[i]}\n{round(100 - scores[i], 2)}% sus', inline = True)
        await ctx.send(embed = embed)


def setup(bot : Pianobot):
    bot.add_cog(Sus(bot))