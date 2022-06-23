# Pianobot

Utility bot for the Discord server of the
Wynncraft Eden guild making use of
the [Wynncraft API](https://docs.wynncraft.com) and developed
with [discord.py](https://github.com/Rapptz/discord.py).

[Invite](https://discord.com/api/oauth2/authorize?client_id=808038119332904990&permissions=274878164032&scope=bot)
this bot to your own Discord server
or [join Eden's server](https://discord.gg/P4bss3w) to use it.

## List of commands

For more information about a command, run `<prefix>help <command>`
in [Eden's Discord server](https://discord.gg/P4bss3w).

Every command has to be prefixed with a server-wide prefix you can view by
mentioning the bot followed by `help`. The listed aliases can be used instead
of a command name. [square brackets] stand for optional, <angle brackets\>
for required arguments.

| Command                                 | Description                                                                  | Aliases                    |
|-----------------------------------------|------------------------------------------------------------------------------|----------------------------|
| `graph <guild> -[days]`                 | Outputs the member activity of a guild as a line graph.                      |
| `gxp ['final' / custom interval]`       | Outputs Eden's guild experience contributions in a set interval.             | `guildXP`, `xp`            |
| `help [command]`                        | Gives you an overview or a detailed description on commands.                 | `info`                     |
| `inactivity <guild>`                    | Outputs the member inactivity times of a specified guild.                    | `act`, `activity`, `inact` |
| `memberActivity [calendar week] [year]` | Outputs the member activity times of Eden for a calendar week.               | `mAct`                     |
| `playerActivity <player> [days]`        | Outputs the activity of a given player in a given interval.                  | `pAct`                     |
| `prefix <new>`                          | Updates the bot prefix for this server.                                      | `pre`                      |
| `soulpoints`                            | Returns a list of the next Wynncraft servers that will give you soul points. | `sp`                       |
| `sus <player>`                          | Check the suspiciousness of a player.                                        | `alt`                      |