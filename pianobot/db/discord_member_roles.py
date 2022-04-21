from pianobot.db import Connection


class DiscordMemberRole:
    def __init__(self, member_id: int, role_id: int) -> None:
        self._member_id = member_id
        self._role_id = role_id

    @property
    def member_id(self) -> int:
        return self._member_id

    @property
    def role_id(self) -> int:
        return self._role_id


class DiscordMemberRoleTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    def get_all(self, member_id: int) -> list[DiscordMemberRole]:
        result = self._con.query(
            'SELECT * FROM discord_member_roles WHERE member_id = %s;', member_id
        )
        return [DiscordMemberRole(row[0], row[1]) for row in result]

    def add(self, member_id: int, role_id: int) -> None:
        if not any(1 for member_role in self.get_all(member_id) if member_role.role_id == role_id):
            self._con.query(
                'INSERT INTO discord_member_roles (member_id, role_id) VALUES (%s, %s);',
                member_id,
                role_id,
            )

    def remove(self, member_id: int, role_id: int) -> None:
        self._con.query(
            'DELETE FROM discord_member_roles WHERE member_id = %s AND role_id = %s',
            member_id,
            role_id,
        )

    def remove_all(self, member_id: int) -> None:
        self._con.query('DELETE FROM discord_member_roles WHERE member_id = %s', member_id)
