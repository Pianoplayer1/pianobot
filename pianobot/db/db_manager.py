from os import getenv

from pianobot.db import (
    Connection,
    DiscordMemberRoleTable,
    DiscordMemberTable,
    DiscordRoleTable,
    GuildActivityTable,
    GuildXPTable,
    MemberActivityTable,
    MinecraftMemberTable,
    ServerTable,
    TerritoryTable,
    WorldTable,
)


class DBManager:
    def __init__(self) -> None:
        self._con_bot = Connection(
            getenv('PG_DB', 'pianobot'),
            getenv('PG_HOST', 'localhost'),
            getenv('PG_PASS', ''),
            getenv('PG_USER', 'root'),
        )
        self.guild_activity = GuildActivityTable(self._con_bot)
        self.guild_xp = GuildXPTable(self._con_bot)
        self.member_activity = MemberActivityTable(self._con_bot)
        self.servers = ServerTable(self._con_bot)
        self.territories = TerritoryTable(self._con_bot)
        self.worlds = WorldTable(self._con_bot)

        self._con_website = Connection(
            getenv('PG_SITE_DB', 'pianosite'),
            getenv('PG_SITE_HOST', 'localhost'),
            getenv('PG_SITE_PASS', ''),
            getenv('PG_SITE_USER', 'root'),
        )
        self.discord_member_roles = DiscordMemberRoleTable(self._con_website)
        self.discord_members = DiscordMemberTable(self._con_website)
        self.discord_roles = DiscordRoleTable(self._con_website)
        self.minecraft_members = MinecraftMemberTable(self._con_website)

    def disconnect(self) -> None:
        self._con_bot.disconnect()
        self._con_website.disconnect()
