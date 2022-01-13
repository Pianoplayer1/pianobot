from pianobot import Pianobot

async def guild_leaderboard(bot: Pianobot):
    bot.database.guilds.delete_all()
    leaderboard = await bot.corkus.leaderboard.guild()
    bot.database.guilds.add(leaderboard)
