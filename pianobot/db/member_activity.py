from datetime import datetime
from typing import Union

from pianobot.db import Connection

class MemberActivityTable:
    def __init__(self, con: Connection):
        self._con = con

    def get_weeks(self) -> list[str]:
        result = self._con.query(
            'SELECT column_name FROM information_schema.columns '
            'WHERE table_name = \'member_activity\';'
        )
        if len(result) <= 1:
            return []
        return [column[0] for column in result[1:]]

    def get_one(self, username: str, week: str) -> Union[int, None]:
        result = self._con.query('SELECT * FROM member_activity WHERE username = %s;', username)
        weeks = self.get_weeks()
        if result:
            row = result[0]
            return row[weeks.index(week) + 1]
        return None

    def get(self, week: str) -> dict[str, int]:
        results = self._con.query('SELECT * FROM member_activity;')
        pos = self.get_weeks().index(week) + 1
        return {row[0]: row[pos] for row in results}

    def add(self, names: list[str]):
        iso_date = datetime.utcnow().isocalendar()
        date = f'{iso_date.year}-{iso_date.week}'
        if date not in self.get_weeks():
            self._con.query(f'ALTER TABLE member_activity ADD COLUMN "{date}" INTEGER DEFAULT 0;')
        new_names = set(names)
        new_names.difference_update(
            row[0] for row in self._con.query('SELECT username FROM member_activity;')
        )
        for name in new_names:
            self._con.query('INSERT INTO member_activity(username) VALUES (%s)', name)

        placeholders = ', '.join(['%s'] * len(names))
        self._con.query(
            f'UPDATE member_activity SET "{date}" = "{date}" + 1 '
            f'WHERE username IN ({placeholders});', *names
        )
