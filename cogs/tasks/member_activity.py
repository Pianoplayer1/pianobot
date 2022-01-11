from ..bot import Pianobot

async def run(bot: Pianobot) -> None:
    guild = await bot.corkus.guild.get('Eden')
    player_list = await bot.corkus.network.online_players()
    online_members = [m.username for m in guild.members if player_list.is_player_online(m)]
    bot.db.member_activity.add(online_members)
