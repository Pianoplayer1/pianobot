from logging import getLogger
from os import getenv

import psycopg2

class Connection:
    def __init__(self):
        self.con = psycopg2.connect(host = getenv('PG_HOST'), user = getenv('PG_USER'), password = getenv('PG_PASS'), database = getenv('PG_DB'))
        self.con.autocommit = True
        getLogger('database').debug('Connected to database')

    def disconnect(self):
        self.con.close()
        getLogger('database').debug('Disconnected from database')

    def query(self, sql: str, *args) -> tuple:
        cursor = self.con.cursor()
        cursor.execute(sql, args)
        self.con.commit()
        try:
            rows = cursor.fetchall()
        except psycopg2.ProgrammingError:
            rows = ()
        cursor.close()
        return rows
