from pianobot.db import Connection

class World:
    def __init__(self, world, time):
        self._world = world
        self._time = time

    @property
    def world(self) -> str:
        return self._world

    @property
    def time(self) -> int:
        return self._time

class WorldTable:
    def __init__(self, con: Connection):
        self._con = con

    def get_all(self) -> list[World]:
        result = self._con.query('SELECT * FROM worlds;')
        return [World(row[0], row[1]) for row in result]

    def add(self, world: str, time: int):
        self._con.query('INSERT INTO worlds VALUES (%s, %s);', world, time)

    def remove(self, world: str):
        self._con.query('DELETE FROM worlds WHERE world = %s;', world)
