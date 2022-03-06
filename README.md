# Pianobot
Utility bot for the [Discord server](https://discord.gg/P4bss3w) of the Wynncraft Eden guild making use of the [Wynncraft API](https://docs.wynncraft.com).

[Invite](https://discord.com/api/oauth2/authorize?client_id=808038119332904990&permissions=274878164032&scope=bot) this bot to your own Discord server or [join Eden's server](https://discord.gg/P4bss3w).

## List of commands
For more information about a command, run `<prefix>help <command>` in [Eden's Discord server](https://discord.gg/P4bss3w).

Every command has to be prefixed with a server-wide prefix you can view by mentioning the bot followed by `help`. The listed aliases can be used instead of a command name. \[Square brackets\] stand for optional, <Angle brackets> for required arguments.

Command | Description | Aliases
------- | ----------- | -------
`graph <guild> -[days]`|Outputs the member activity of a guild as a line graph.|
`gxp ["final" \| custom interval]`|Outputs Eden's guild experience contributions in a set interval.|`guildXP`, `xp`
`help [command]`|Gives you an overview or a detailed description on commands.|`info`
`inactivity <guild>`|Outputs the member inactivity times of a specified guild.|`act`, `activity`, `inact`
`memberActivity [calendar week] [year]`|Outputs the member activity times of Eden for a calendar week.|`mAct`
`playerActivity <player> [days]`|Outputs the activity of a given player in a given interval.|`pAct`
`prefix <new>`|Updates the bot prefix for this server.|`pre`
`soulpoints`|Returns a list of the next Wynncraft servers that will give you soul points.|`sp`
`sus <player>`|Check the suspiciousness of a player.|`alt`
`territories <"add" \| "del" \| "list"> [territory], [territory] ...`|Lets you view and edit the territory list.|`claim`, `terrs`
`tracking <"channel" \| "ping" \| "role"> [arguments]`|Lets you configure tracking for Eden's territories.|`channel`, `cooldown`, `track`

## Use the bot
If you want to experience the bot yourself, you can either [join](https://discord.gg/P4bss3w) Eden's Discord server, [invite](https://discord.com/api/oauth2/authorize?client_id=808038119332904990&permissions=274878164032&scope=bot) the bot to your own server or host it yourself.

Should you decide to host it yourself (discouraged), you will have to follow some steps:
- Clone this repository into local / cloud storage with a python 3 environment
- Install python dependencies with `pip install -r requirements.txt` in a command line
- Create your own [Discord Application](https://discord.com/developers/applications)
- Setup a PostgreSQL database locally or acquire credentials for a hosted one
- In this database, run the `tables.sql` file to create the neccessary tables
- Set following environment variables:
  - `TOKEN` - Your bot's secret token, find it at Discord's developer portal
  - `PG_DB` - PostgreSQL database name
  - `PG_HOST` - URL of your database (localhost if hosted on your own device)
  - `PG_USER` - PostgreSQL username
  - `PG_PASS` - PostgreSQL password for that user

Now, you only need to run the `launcher.py` file with `py launcher.py` in a command line every time you want to start the bot!
> Note: The `py` and `pip` commands may not work or vary depending on your python configuration, consult the [official python documentation](https://docs.python.org/3/using/) in this case.