from discord.ext import commands

from pianobot.bot import Pianobot
from pianobot.utils import check_permissions, paginator, table


class Territories(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        aliases=['claim', 'terrs'],
        brief='Lets you view and edit the territory list.',
        description='guild_only',
        help=(
            'Depending on the option you pass, you can either view a list of territories the bots'
            ' listens to or add / delete territories from the list.'
        ),
        name='territories',
        usage='<"add" | "del" | "list"> [territory], [territory] ...',
    )
    @commands.guild_only()
    async def territories(
        self, ctx: commands.Context, action: str, *, territories: str = ''
    ) -> None:
        db_terrs = self.bot.database.territories.get_all()
        territory_list = territories.split(', ')
        if action.lower() == 'list':
            await paginator(
                self.bot,
                ctx,
                table(
                    {
                        'Territory': len(max([terr.name for terr in db_terrs], key=len)) + 8,
                        'Guild': len(max([terr.name for terr in db_terrs], key=len)) + 8,
                    },
                    sorted([[terr.name, terr.guild] for terr in db_terrs], key=lambda i: i[0]),
                    10,
                    20,
                    True,
                ),
            )
        elif action.lower() == 'add':
            if not check_permissions(ctx.author, ctx.channel, 'manage_server', all_guilds=False):
                await ctx.send('You don\'t have the required permissions to perform this action!')
                return
            if len(territory_list) == 0:
                await ctx.send('You have to specify at least one territory to add!')
                return
            wynn_terrs = await self.bot.corkus.territory.list_all()
            failed = []
            for territory in territory_list:
                found = next(
                    (terr for terr in wynn_terrs if terr.name.lower() == territory.lower()), None
                )
                if found is None:
                    failed.append(territory)
                else:
                    self.bot.database.territories.add(
                        found.name, None if found.guild is None else found.guild.name
                    )
            message = ''
            if len(territory_list) - len(failed) > 0:
                message += (
                    f'Successfully added {len(territory_list) - len(failed)}'
                    f' territor{"ies" if len(territory_list) - len(failed) > 1 else "y"}'
                    ' to the territory list!\n\n'
                )
            if len(failed) > 0:
                failed_string = '-`' + '`\n-`'.join(failed) + '`\n'
                message += f'Invalid territor{"ies" if len(failed) > 1 else "y"}:\n{failed_string}'
            await ctx.send(message)
        elif action.lower() in ['del', 'delete', 'remove']:
            if not check_permissions(ctx.author, ctx.channel, 'manage_server', all_guilds=False):
                await ctx.send('You don\'t have the required permissions to perform this action!')
                return
            if len(territory_list) == 0:
                await ctx.send('You have to specify at least one territory to remove!')
                return
            failed = []
            for territory in territory_list:
                found = next(
                    (terr for terr in db_terrs if terr.name.lower() == territory.lower()), None
                )
                if found is None:
                    failed.append(territory)
                else:
                    self.bot.database.territories.remove(found.name)
            message = ''
            if len(territory_list) - len(failed) > 0:
                message += (
                    f'Successfully removed {len(territory_list) - len(failed)}'
                    f' territor{"ies" if len(territory_list) - len(failed) > 1 else "y"}'
                    ' from the territory list!\n\n'
                )
            if failed:
                failed_string = '-`' + '`\n-`'.join(failed) + '`\n'
                message += f'Invalid territor{"ies" if len(failed) > 1 else "y"}:\n{failed_string}'
            await ctx.send(message)
        else:
            raise commands.BadArgument


def setup(bot: Pianobot) -> None:
    bot.add_cog(Territories(bot))
