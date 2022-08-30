from datetime import datetime

from pianobot.db import Connection


class World:
    def __init__(self, name: str, started_at: datetime) -> None:
        self._name = name
        self._started_at = started_at

    @property
    def name(self) -> str:
        return self._name

    @property
    def started_at(self) -> datetime:
        return self._started_at


class WorldTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    async def get_all(self) -> list[World]:
        result = await self._con.query('SELECT * FROM worlds')
        return [World(row[0], row[1]) for row in result]

    async def add(self, name: str) -> None:
        await self._con.execute('INSERT INTO worlds (name) VALUES ($1)', name)

    async def remove(self, name: str) -> None:
        await self._con.execute('DELETE FROM worlds WHERE name = $1', name)
