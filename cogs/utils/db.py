from os import getenv
import psycopg2
from psycopg2 import connection

def connect() -> connection:
    con = psycopg2.connect(host = getenv('PG_HOST'), user = getenv('PG_USER'), password = getenv('PG_PASS'), database = getenv('PG_DB'))
    print('Connected to database')
    return con

def disconnect(con : connection):
    con.close()
    print('Disconnected from database')

def query(con : connection, sql : str, vals : tuple) -> tuple:
    sql = sql.replace('`', '"')
    cursor = con.cursor()
    cursor.execute(sql, vals)
    con.commit()
    rows = cursor.fetchall()
    cursor.close()
    return rows