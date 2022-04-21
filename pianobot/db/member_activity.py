from datetime import datetime

from pianobot.db import Connection


class MemberActivityTable:
    def __init__(self, con: Connection) -> None:
        self._con = con

    def get_weeks(self) -> list[str]:
        result = self._con.query(
            'SELECT column_name FROM information_schema.columns WHERE table_name ='
            ' \'member_activity\''
        )
        return [] if len(result) <= 1 else [column[0] for column in result[1:]]

    def get_one(self, username: str, week: str) -> int | None:
        result = self._con.query('SELECT * FROM member_activity WHERE username = %s', username)
        weeks = self.get_weeks()
        return int(result[0][weeks.index(week) + 1]) if result else None

    def get(self, week: str) -> dict[str, int]:
        results = self._con.query('SELECT * FROM member_activity')
        pos = self.get_weeks().index(week) + 1
        return {row[0]: row[pos] for row in results}

    def get_usernames(self) -> list[str]:
        return [row[0] for row in self._con.query('SELECT username FROM member_activity')]

    def add(self, names: list[str]) -> None:
        iso_date = datetime.utcnow().isocalendar()
        date = f'"{iso_date.year}-{iso_date.week}"'
        if date[1:-1] not in self.get_weeks():
            self._con.query(f'ALTER TABLE member_activity ADD COLUMN {date} INTEGER DEFAULT 0')
        for name in set(names).difference(self.get_usernames()):
            self._con.query('INSERT INTO member_activity(username) VALUES (%s)', name)

        placeholders = ', '.join('%s' for _ in names)

        self._con.query(
            f'UPDATE member_activity SET {date} = {date} + 1 WHERE username IN ({placeholders});',
            *names,
        )
