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

    def add_or_update(
        self,
        discord_id: int,
        nickname: str,
        username: str,
        tag: int,
        avatar_url: str
    ):
        if any(member for member in self.get_all() if member.discord_id == discord_id):
            self.update(discord_id, nickname, username, tag, avatar_url, True)
        else:
            self._con.query(
                'INSERT INTO discord_members VALUES (%s, %s, %s, %s, %s, 1);',
                discord_id,
                nickname,
                username,
                tag,
                avatar_url
            )

    def update_and_remove(
        self,
        discord_id: int,
        nickname: str,
        username: str,
        tag: int,
        avatar_url: str
    ):
        self.update(discord_id, nickname, username, tag, avatar_url, False)

    def update(
        self,
        discord_id: int,
        nickname: str,
        username: str,
        tag: int,
        avatar_url: str,
        is_member: bool
    ):
        self._con.query(
            (
                'UPDATE discord_members '
                'SET nickname = %s, username = %s, tag = %s, avatar = %s, is_member = %s '
                'WHERE id = %s;'
            ),
            nickname,
            username,
            tag,
            avatar_url,
            1 if is_member else 0,
            discord_id
        )
