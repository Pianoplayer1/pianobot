from datetime import datetime, timezone

from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

from pianobot import Pianobot


class Names(Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @command(
        brief='View a list of name changes of a Minecraft player or uuid',
        help=(
            'This command returns a list of the last 25 name changes to a Minecraft account,'
            ' including the respective change dates and durations. Search for a player by their'
            ' current username or UUID.'
        ),
        name='names',
        usage='<player>',
    )
    async def names(self, ctx: Context[Bot], player: str) -> None:
        if len(player) > 20:
            uuid = player
        else:
            profile_response = await self.bot.session.get(
                f'https://api.mojang.com/users/profiles/minecraft/{player}'
            )
            if profile_response.status != 200:
                await ctx.send(f'No Minecraft player with username `{player}` found!')
                return
            profile = await profile_response.json()
            uuid = profile['id']

        name_history_response = await self.bot.session.get(
            f'https://api.mojang.com/user/profiles/{uuid}/names'
        )
        if name_history_response.status != 200:
            await ctx.send('Invalid username or UUID!')
            return
        name_history = await name_history_response.json()

        embed = Embed(
            title=name_history[-1]['name'].replace('_', '\\_'),
            description=(
                f'{len(name_history) - 1} name change{"s" if len(name_history) > 1 else ""} in'
                ' total:'
                if len(name_history) > 1
                else 'No name changes yet'
            )
            + '⠀' * 20,
            color=0x77FF77,
        )
        embed.set_thumbnail(url=f'https://mc-heads.net/avatar/{uuid}')

        for i, entry in enumerate(reversed(name_history)):
            time = (
                datetime.fromtimestamp(entry['changedToAt'] / 1000, timezone.utc)
                if 'changedToAt' in entry
                else None
            )
            name_history[-i]['datetime'] = time
            time_diff = (
                (name_history[1 - i]['datetime'] if i > 0 else datetime.now(timezone.utc)) - time
                if time is not None
                else None
            )
            value = (
                f'{time.strftime("%d.%m.%Y, %H:%M:%S")} • '
                + (
                    f'{time_diff.days / 365.2425:.2f} years'
                    if time_diff.days > 365.2425
                    else f'{time_diff.days} day{"s" if time_diff.days != 1 else ""}'
                )
                if time is not None
                else 'Original account name'
            )
            embed.add_field(inline=False, name=entry['name'].replace('_', '\\_'), value=value)
        await ctx.send(embed=embed)


async def setup(bot: Pianobot) -> None:
    await bot.add_cog(Names(bot))
