from ..bot import Pianobot

async def run(bot: Pianobot) -> None:
    bot.db.guilds.delete_all()
    leaderboard = await bot.corkus.leaderboard.guild()
    bot.db.guilds.add(leaderboard)
