from math import floor, log10

from ..bot import Pianobot

async def run(bot: Pianobot) -> None:
    guild = await bot.corkus.guild.get('Eden')
    current_xp = {member.username: member.contributed_xp for member in guild.members}

    bot.db.guild_xp.update_columns(current_xp.keys())
    bot.db.guild_xp.add(current_xp)

    data = bot.db.guild_xp.get_last(2)
    new = data[0]
    old = data[1]
    xp_diff = [[name, xp - old.data.get(name, 0)] for name, xp in new.data.items() if xp - old.data.get(name, 0) > 0]
    if len(xp_diff) == 0: return

    msg = '--------------------------------------------------------------------------------'
    for pos, (name, xp) in enumerate(sorted(xp_diff, key = lambda item: item[1], reverse = True)):
        msg += f'\n**#{pos + 1} {name}** — `{format(xp)} XP | {format(xp / 5)} XP/min`'
    msg += f'\n**Total: ** `{format(sum([item[1] for item in xp_diff]))} XP`'
    channel = bot.get_channel(920757651380506644)
    if channel is not None:
        await channel.send(msg)

def format(n: float) -> str:
    names = ['',' Thousand',' Million',' Billion',' Trillion']
    if (n < 10000): return n
    pos = max(0, min(len(names) - 1, int(floor(0 if n == 0 else log10(abs(n)) / 3))))
    return f'{round(n / 10 ** (3 * pos), 2):g}{names[pos]}'
