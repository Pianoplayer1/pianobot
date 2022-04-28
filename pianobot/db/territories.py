from pianobot.db import Connection


class Territory:
    def __init__(self, name: str, guild: str) -> None:
        self._name = name
        self._guild = guild

    @property
    def name(self) -> str:
        return self._name

    @property
    def guild(self) -> str:
        return self._guild


class TerritoryTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    async def add(self, name: str, guild: str | None) -> None:
        await self._con.execute(
            'INSERT INTO territories VALUES ($1, $2) ON CONFLICT (name) DO NOTHING', name, guild
        )

    async def get_all(self) -> list[Territory]:
        result = await self._con.query('SELECT name, guild FROM territories')
        return [Territory(row[0], row[1]) for row in result]

    async def remove(self, name: str) -> None:
        await self._con.execute('DELETE FROM territories WHERE name = $1', name)

    async def update(self, name: str, guild: str | None) -> None:
        await self._con.execute('UPDATE territories SET guild = $1 WHERE name = $2', guild, name)
