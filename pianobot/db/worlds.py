from pianobot.db import Connection


class World:
    def __init__(self, world: str, time: int) -> None:
        self._world = world
        self._time = time

    @property
    def world(self) -> str:
        return self._world

    @property
    def time(self) -> int:
        return self._time


class WorldTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    async def get_all(self) -> list[World]:
        result = await self._con.query('SELECT * FROM worlds')
        return [World(row[0], row[1]) for row in result]

    async def add(self, world: str, time: float) -> None:
        await self._con.execute('INSERT INTO worlds VALUES ($1, $2)', world, time)

    async def remove(self, world: str) -> None:
        await self._con.execute('DELETE FROM worlds WHERE world = $1', world)
