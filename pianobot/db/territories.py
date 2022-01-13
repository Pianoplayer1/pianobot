from pianobot.db import Connection

class Territory:
    def __init__(self, name, guild):
        self._name = name
        self._guild = guild

    @property
    def name(self) -> str:
        return self._name

    @property
    def guild(self) -> str:
        return self._guild

class TerritoryTable:
    def __init__(self, con: Connection):
        self._con = con

    def get_all(self) -> list[Territory]:
        result = self._con.query('SELECT name, guild FROM territories')
        return [Territory(row[0], row[1]) for row in result]

    def update(self, name: str, guild: str):
        self._con.query('UPDATE territories SET guild = %s WHERE name = %s;', guild, name)
