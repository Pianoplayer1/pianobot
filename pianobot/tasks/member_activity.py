from pianobot import Pianobot

async def member_activity(bot: Pianobot):
    guild = await bot.corkus.guild.get('Eden')
    player_list = await bot.corkus.network.online_players()
    online_members = [m.username for m in guild.members if player_list.is_player_online(m)]
    bot.database.member_activity.add(online_members)
