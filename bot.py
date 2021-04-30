import discord
from discord.ext import commands
from functions import db
from os import listdir, getenv

async def get_prefixes(client, message):
    prefixes = [f'<@!{client.user.id}> ', f'<@{client.user.id}> ']
    if message.guild is None:
        prefixes.append('-')
    else:
        prefixes.append(db.query("SELECT * FROM servers WHERE id = %s", message.guild.id)[0][1])
    return prefixes

client = commands.Bot(command_prefix = get_prefixes, help_command = None, intents = discord.Intents(guilds=True,members=True,messages=True,reactions=True))

for filename in listdir('./commands'):
    if filename.endswith('.py'):
        client.load_extension(f'commands.{filename[:-3]}')
for filename in listdir('./events'):
    if filename.endswith('.py'):
        client.load_extension(f'events.{filename[:-3]}')

db.connect()
client.run(getenv('TOKEN'))

db.disconnect()
print('Exited bot')