from .connection import Connection

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

class Manager:
    def __init__(self, db: Connection):
        self._db = db
    
    def get_all(self) -> list[Territory]:
        result = self._db.query('SELECT name, guild FROM territories')
        return [Territory(row[0], row[1]) for row in result]

    def update(self, name: str, guild: str):
        self._db.query('UPDATE territories SET guild = %s WHERE name = %s;', guild, name)
