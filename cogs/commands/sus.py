import discord
from discord.ext import commands
from datetime import datetime
import math, asyncio

class Sus(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(name = 'sus', aliases = ['alt'], brief = 'Check the suspiciousness of a player.', help = 'View the approximate probability of a player being an alt account.', usage = '<player>')
    async def sus(self, ctx, player):
        self.get_date_score = lambda date, maxValue : min(int((datetime.utcnow() - date).days / maxValue * 100), 100)

        # Ashcon API
        try:
            async with self.client.session.get('https://api.ashcon.app/mojang/v2/user/' + player) as response:
                ashcon_response = await response.json()
                self.uuid = ashcon_response['uuid']
        except KeyError:
            await ctx.send('Not a minecraft username!')
            return

        await asyncio.gather(*[self.wynncraft_api(ctx), self.hypixel_api()])
        if self.first_wynncraft_login is None:
            return
        
        name_history = ashcon_response['username_history']
        first_name_change = datetime.strptime(name_history[1]['changed_at'], '%Y-%m-%dT%H:%M:%S.%fZ') if len(name_history) > 1 else None
        ashcon_created = ashcon_response['created_at']
        if ashcon_created is not None:
            ashcon_created = datetime.strptime(ashcon_response['created_at'], '%Y-%m-%d')


        # Final date calculations
        raw_dates = [self.first_hypixel_login, self.first_wynncraft_login, ashcon_created, first_name_change]
        dates = [date for date in raw_dates if date is not None]
        oldest_date = min(dates)
        oldest_date_score = self.get_date_score(oldest_date, 1000)


        # Embed building
        embed_fields = ['Wynncraft Join Date', 'Wynncraft Playtime', 'Wynncraft Level', 'Wynncraft Quests', 'Wynncraft Rank', 'Minecraft Join Date']
        categories = [self.first_wynncraft_login.strftime('%B %d, %Y'), str(self.wynncraft_playtime) + ' hours', str(self.wynncraft_total_level) + ' (total level)', 
            str(self.wynncraft_quests) + ' (all classes)', self.wynncraft_rank, oldest_date.strftime('%B %d, %Y')]
        scores = [self.first_wynncraft_login_score, self.wynncraft_playtime_score, self.wynncraft_total_level_score, self.wynncraft_quests_score, self.wynncraft_rank_score, oldest_date_score]
        scores = [100 - score for score in scores]
        total_score = round(sum(scores) / len(scores), 2)

        if total_score >= 40:
            color = 0xff0000
        elif total_score >= 20:
            color = 0xffff00
        else:
            color = 0x00ff00

        embed = discord.Embed(title = 'Suspiciousness of ' + player + ': ' + str(total_score) + '%', description = 'The rating is based on following components:', color = color)

        for i in range(len(embed_fields)):
            embed.add_field(name = embed_fields[i], value = str(categories[i]) + '\n' + str(scores[i]) + '% sus', inline = True)

        embed.set_footer(text = 'The minecraft join date is only an approximate date some time after the actual one.')
        await ctx.send(embed = embed)

    async def wynncraft_api(self, ctx):
        self.first_wynncraft_login = None
        try:
            async with self.client.session.get('https://api.wynncraft.com/v2/player/' + self.uuid + '/stats') as response:
                wynncraft_response = await response.json()
                player_data = wynncraft_response['data'][0]
        except IndexError:
            await ctx.send('Not a valid Wynncraft player!')
            return

        self.first_wynncraft_login = datetime.strptime(player_data['meta']['firstJoin'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.first_wynncraft_login_score = self.get_date_score(self.first_wynncraft_login, 200)

        self.wynncraft_playtime = math.floor(player_data['meta']['playtime'] * 4.7 / 60)
        self.wynncraft_playtime_score = min(self.wynncraft_playtime, 100)

        self.wynncraft_total_level = 0
        quests = []
        for player_class in player_data['classes']:
            quests.extend(player_class['quests']['list'])
            self.wynncraft_total_level += player_class['level']
        self.wynncraft_total_level_score = min(self.wynncraft_total_level / 10, 100)

        self.wynncraft_quests = len(set(quests))
        self.wynncraft_quests_score = min(int(self.wynncraft_quests / 2), 100)
        
        self.wynncraft_rank = player_data['meta']['tag']['value']
        self.wynncraft_rank_score = [None, 'VIP', 'VIP+', 'HERO', 'CHAMPION'].index(self.wynncraft_rank) * 25


    async def hypixel_api(self):
        params = {'key': 'd9a6b029-99ea-4620-ba52-6df35c61486b', 'uuid': self.uuid}
        async with self.client.session.get('https://api.hypixel.net/player', params = params) as response:
            hypixel_response = await response.json()
            if hypixel_response['player'] is None:
                self.first_hypixel_login = None
            else:
                self.first_hypixel_login = datetime.utcfromtimestamp(hypixel_response['player']['firstLogin'] / 1000)
                

def setup(client):
    client.add_cog(Sus(client))