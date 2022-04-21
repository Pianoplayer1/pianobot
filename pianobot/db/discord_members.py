from discord import Member

from pianobot.db import Connection


class DiscordMember:
    def __init__(
        self,
        discord_id: int,
        nickname: str,
        username: str,
        tag: int,
        avatar_url: str,
        is_member: bool,
    ) -> None:
        self._discord_id = discord_id
        self._nickname = nickname
        self._username = username
        self._tag = tag
        self._avatar_url = avatar_url
        self._is_member = is_member

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

    @property
    def is_member(self) -> bool:
        return self._is_member


class DiscordMemberTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    def get_all(self) -> list[DiscordMember]:
        result = self._con.query('SELECT * FROM discord_members')
        return [DiscordMember(row[0], row[1], row[2], row[3], row[4], row[5]) for row in result]

    def add_or_update(self, member: Member) -> None:
        if any(m for m in self.get_all() if m.discord_id == member.id):
            self.update(member, True)
        else:
            self._con.query(
                'INSERT INTO discord_members VALUES (%s, %s, %s, %s, %s, %s)',
                member.id,
                member.nick or member.name,
                member.name,
                int(member.discriminator),
                str(member.avatar_url),
                True,
            )

    def update_and_remove(self, member: Member) -> None:
        self.update(member, False)

    def update(self, member: Member, is_member: bool) -> None:
        self._con.query(
            'UPDATE discord_members SET nickname = %s, username = %s, tag = %s, avatar = %s,'
            ' is_member = %s WHERE id = %s',
            member.nick or member.name,
            member.name,
            member.discriminator,
            str(member.avatar_url),
            is_member,
            member.id,
        )
