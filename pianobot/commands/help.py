from discord import Embed
from discord.ext import commands

from pianobot import Pianobot
from pianobot.utils import get_prefix


class Help(commands.Cog):
    def __init__(self, bot: Pianobot) -> None:
        self.bot = bot

    @commands.command(
        aliases=['info'],
        brief='Shows this page; use help [command] for detailed description about a command.',
        help=(
            'This command gives you an overview of this bot and its commands. If you want more'
            ' information on a specific command, enter that command name as an argument of the'
            ' help command.'
        ),
        name='help',
        usage='[command]',
    )
    async def help(self, ctx: commands.Context, command: str | None = None) -> None:
        help_text = (
            'I am a utility bot for various different Wynncraft related things.\n\nList of'
            ' commands:\n```'
        )
        prefix = get_prefix(self.bot.database.servers, ctx.guild)

        visible_commands = {
            cmd: [cmd.name.lower()]
            for cog in self.bot.cogs.values()
            for cmd in cog.get_commands()
            if not cmd.hidden and (ctx.guild or cmd.description != 'guild_only')
        }
        for cmd in visible_commands:
            visible_commands[cmd].extend(map(str.lower, cmd.aliases))

        if command:
            try:
                cmd = next(
                    cmd for cmd, aliases in visible_commands.items() if command.lower() in aliases
                )
                usage = ' ' + cmd.usage if cmd.usage else ''
                aliases = '\n'.join([f'`{prefix}{alias}`' for alias in cmd.aliases])

                help_text = cmd.help or ''
                embed = Embed(
                    title=f'{cmd.name.capitalize()} command',
                    description=help_text.replace('[[prefix]]', prefix),
                )
                embed.add_field(inline=False, name='Usage', value=f'`{prefix}{cmd.name}{usage}`')
                if len(aliases) > 0:
                    embed.add_field(inline=False, name='Aliases', value=aliases)
                embed.set_footer(
                    text=(
                        '<Required Argument>   [Optional Argument]\n'
                        'You can use aliases instead of the command name.'
                    )
                )
                await ctx.send(embed=embed)
                return
            except StopIteration:
                help_text = (
                    'Please specify a valid command for detailed information about it!\n\nRefer to'
                    ' this list of available commands:\n```'
                )

        await ctx.send(
            help_text
            + '\n'.join([f'{prefix}{cmd.name.ljust(22)}{cmd.brief}' for cmd in visible_commands])
            + '```'
        )


def setup(bot: Pianobot) -> None:
    bot.add_cog(Help(bot))
