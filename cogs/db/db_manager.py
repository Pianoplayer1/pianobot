from . import connection, guild_activity, guild_xp, guilds, servers, territories, worlds

class DBManager:
    def __init__(self):
        self.con = connection.Connection()
        self.guild_activity = guild_activity.Manager(self.con)
        self.guild_xp = guild_xp.Manager(self.con)
        self.guilds = guilds.Manager(self.con)
        self.servers = servers.Manager(self.con)
        self.territories = territories.Manager(self.con)
        self.worlds = worlds.Manager(self.con)
