from discord import Member

from pianobot.db import Connection

class DiscordMember:
    def __init__(self, discord_id, nickname, username, tag, avatar_url):
        self._discord_id = discord_id
        self._nickname = nickname
        self._username = username
        self._tag = tag
        self._avatar_url = avatar_url

    @property
    def discord_id(self) -> int:
        return self._discord_id

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def username(self) -> str:
        return self._username

    @property
    def tag(self) -> int:
        return self._tag

    @property
    def avatar_url(self) -> str:
        return self._avatar_url

class DiscordMemberTable:
    def __init__(self, con: Connection):
        self._con = con

    def get_all(self) -> list[DiscordMember]:
        result = self._con.query('SELECT * FROM discord_members;')
        return [DiscordMember(row[0], row[1], row[2], row[3], row[4]) for row in result]

    def add_or_update(self, member: Member):
        if any(m for m in self.get_all() if m.discord_id == member.id):
            self.update(member, True)
        else:
            self._con.query(
                'INSERT INTO discord_members VALUES (%s, %s, %s, %s, %s, 1);',
                member.id,
                member.nick or member.name,
                member.name,
                member.discriminator,
                str(member.avatar_url)
            )

    def update_and_remove(self, member: Member):
        self.update(member, False)

    def update(self, member: Member, is_member: bool):
        self._con.query(
            'UPDATE discord_members '
            'SET nickname = %s, username = %s, tag = %s, avatar = %s, is_member = %s '
            'WHERE id = %s;',
            member.nick or member.name,
            member.name,
            member.discriminator,
            str(member.avatar_url),
            1 if is_member else 0,
            member.id
        )
