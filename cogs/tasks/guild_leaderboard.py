from ..bot import Pianobot

async def run(bot: Pianobot) -> None:
    bot.query('TRUNCATE TABLE guilds;')
    leaderboard = await bot.corkus.leaderboard.guild()
    placeholders = ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s)' for _ in leaderboard])
    args = []
    for guild in leaderboard:
        args.extend((guild.name, guild.tag, guild.level, guild.total_xp, guild.territories.count, guild.war_count, guild.members_count, guild.created))
    bot.query(f'INSERT INTO guilds VALUES {placeholders};', tuple(args))