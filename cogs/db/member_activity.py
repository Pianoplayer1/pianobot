from datetime import datetime
from typing import Union

from .connection import Connection

class MemberActvity:
    def __init__(self, username, data):
        self._username = username
        self._data = data

    @property
    def username(self) -> str:
        return self._username

    @property
    def data(self) -> dict[str: int]:
        return self._data

class Manager:
    def __init__(self, db: Connection):
        self._db = db

    def get_weeks(self) -> list[str]:
        result = self._db.query('SELECT column_name FROM information_schema.columns WHERE table_name = \'member_activity\';')
        if len(result) <= 1:
            return []
        return [column[0] for column in result[1:]]

    def get(self, username: str) -> Union[MemberActvity, None]:
        result = self._db.query('SELECT * FROM member_activity WHERE username = %s;', username)
        weeks = self.get_weeks()
        if result:
            row = result[0]
            data = {weeks[i]: row[i + 1] for i in range(len(weeks))}
            return MemberActvity(row[0], data)
        else:
            return None
    
    def get_all(self) -> list[MemberActvity]:
        results = self._db.query('SELECT * FROM member_activity;')
        weeks = self.get_weeks()
        return [MemberActvity(row[0], {weeks[i]: row[i + 1] for i in range(len(weeks))}) for row in results]

    def add(self, names: list[str]):
        iso_date = datetime.utcnow().isocalendar()
        date = f'{iso_date.year}-{iso_date.week}'
        if date not in self.get_weeks():
            self._db.query(f'ALTER TABLE member_activity ADD COLUMN "{date}" INTEGER DEFAULT 0;')
        new_names = set(names)
        new_names.difference_update(row[0] for row in self._db.query('SELECT username FROM member_activity;'))
        for name in new_names:
            self._db.query('INSERT INTO member_activity(username) VALUES (%s)', name)

        placeholders = ', '.join(['%s'] * len(names))
        sql = f'UPDATE member_activity SET "{date}" = "{date}" + 1 WHERE username IN ({placeholders});'
        self._db.query(sql, *names)
