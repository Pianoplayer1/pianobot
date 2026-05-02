"""Slash command groups registered on the discord.py CommandTree."""

from commands.eden import EdenCommands
from commands.guild import GuildCommands
from commands.leaderboard import LeaderboardCommands
from commands.manage import ManageCommands
from commands.player import PlayerCommands
from commands.wynn import WynnCommands

__all__ = [
    "EdenCommands",
    "GuildCommands",
    "LeaderboardCommands",
    "ManageCommands",
    "PlayerCommands",
    "WynnCommands",
]
