from . import connection, guild_activity, guild_xp, guilds, member_activity, servers, territories, worlds

class DBManager:
    def __init__(self):
        self._con = connection.Connection()
        self.guild_activity = guild_activity.Manager(self._con)
        self.guild_xp = guild_xp.Manager(self._con)
        self.guilds = guilds.Manager(self._con)
        self.member_activity = member_activity.Manager(self._con)
        self.servers = servers.Manager(self._con)
        self.territories = territories.Manager(self._con)
        self.worlds = worlds.Manager(self._con)
    
    def disconnect(self):
        self._con.disconnect()
