from ..bot import Pianobot
from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot : Pianobot):
        self.bot = bot
    
    @commands.command(  name = 'help',
                        aliases = ['info'],
                        brief = 'Shows this page; use help [command] for detailed description about a command.',
                        help = 'This command gives you an overview of this bot and its commands. If you want more information on a specific command, enter that command name as an argument of the help command.',
                        usage = '[command]')
    async def help(self, ctx : commands.Context, command : str = None):
        help_text = 'I am a utility bot for various different Wynncraft related things.\n\nList of commands:\n```'
        prefix = '-'
        if ctx.guild:
            prefix = self.bot.query('SELECT prefix FROM servers WHERE id = %s;', ctx.guild.id)[0][0]

        visible_commands = {cmd: [cmd.name] for cog in self.bot.cogs.values() for cmd in cog.get_commands() if ctx.guild or not cmd.hidden}
        for cmd in visible_commands:
            visible_commands[cmd].extend(cmd.aliases)

        if command:
            matching_commands = [cmd  for cmd, aliases in visible_commands.items() if command in aliases]

            if len(matching_commands) == 0:
                help_text = 'Please specify a valid command for detailed information about it!\n\nRefer to this list of available commands:\n```'
            else:
                cmd = matching_commands[0]
                usage = ' ' + cmd.usage if cmd.usage else ''
                aliases = '\n'.join([f'`{prefix}{alias}`' for alias in cmd.aliases])

                embed = discord.Embed(title = f'{cmd.name.capitalize()} command', description = cmd.help)
                embed.add_field(name = 'Usage', value = f'`{prefix}{cmd.name}{usage}`', inline = False)
                if len(aliases) > 0:
                    embed.add_field(name = 'Aliases', value = aliases, inline = False)
                embed.set_footer(text = '<Required Argument>   [Optional Argument]\nYou can use aliases instead of the command name.')
                await ctx.send(embed = embed)
                return

        await ctx.send(help_text + '\n'.join([f'{prefix}{cmd.name.ljust(22)}{cmd.brief}' for cmd in visible_commands]) + '```')

def setup(bot : Pianobot):
    bot.add_cog(Help(bot))