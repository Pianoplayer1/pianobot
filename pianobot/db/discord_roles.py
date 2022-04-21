from pianobot.db import Connection


class DiscordRole:
    def __init__(self, discord_id: int, name: str, color: str, position: int) -> None:
        self._discord_id = discord_id
        self._name = name
        self._color = color
        self._position = position

    @property
    def discord_id(self) -> int:
        return self._discord_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def color(self) -> str:
        return self._color

    @property
    def position(self) -> int:
        return self._position


class DiscordRoleTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    def get_all(self) -> list[DiscordRole]:
        result = self._con.query('SELECT * FROM discord_roles')
        return [DiscordRole(row[0], row[1], row[2], row[3]) for row in result]

    def add_or_update(self, discord_id: int, name: str, color: str, position: int) -> None:
        if any(role for role in self.get_all() if role.discord_id == discord_id):
            self._con.query(
                'UPDATE discord_roles SET name = %s, color = %s, position = %s WHERE id = %s',
                name,
                color,
                position,
                discord_id,
            )
        else:
            self._con.query(
                'INSERT INTO discord_roles (id, name, color, position) VALUES (%s, %s, %s, %s)',
                discord_id,
                name,
                color,
                position,
            )
