from discord.ext import commands
import discord

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(name = 'help', aliases = ['info'], brief = 'Shows this page; use help [command] for detailed description about a command.', help = 'This command gives you an overview of this bot and its commands. If you want more information on a specific command, enter that command name as an argument of the help command.', usage = '[command]')
    async def help(self, ctx, command = None):
        help_text = 'List of commands:\n```'
        if ctx.guild:
            prefix = self.client.query('SELECT * FROM servers WHERE id = %s', ctx.guild.id)
            prefix = prefix[0][1]
            help_text = help_text = f'Utility bot for various different Wynncraft related things.\n\n' + help_text
        else:
            prefix = '-'
        if command:
            allCommands = {}
            for i in self.client.cogs:
                cog = self.client.get_cog(i)
                try:
                    commands = cog.get_commands()
                    for cmd in commands:
                        if ctx.guild or not cmd.hidden:
                            allCommands[cmd] = [cog, cmd.name]
                            for alias in cmd.aliases:
                                allCommands[cmd].append(alias) 
                except:
                    pass
            commands = [key  for (key, value) in allCommands.items() if command in value]
            if len(commands) == 0:
                command = None
            else:
                cmd = commands[0]
                aliases = ''
                for alias in cmd.aliases:
                    aliases += '`' + prefix + alias + '`\n'
                embed = discord.Embed(title = f'{cmd.name.capitalize()} command', description = cmd.help)
                embed.add_field(name = 'Usage', value = f'`{prefix}{cmd.name}{(" " + cmd.usage) if cmd.usage else ""}`', inline = False)
                if len(aliases) > 0:
                    embed.add_field(name = 'Aliases', value = aliases, inline = False)
                embed.set_footer(text = '<Required Argument>   [Optional Argument]\nYou can use aliases instead of the command name.')
                await ctx.send(embed = embed)
        if not command:
            for i in self.client.cogs:
                cog = self.client.get_cog(i)
                try:
                    commands = cog.get_commands()
                    for command in commands:
                        if ctx.guild or not command.hidden:
                            help_text += f'{prefix}{command.name.ljust(22)}{command.brief}\n'
                except:
                    pass
            await ctx.send(help_text+'```')

def setup(client):
    client.add_cog(Help(client))