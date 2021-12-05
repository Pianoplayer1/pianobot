from os import getenv
import pymysql
from pymysql.connections import Connection

def connect() -> Connection:
    con = pymysql.connect(host = getenv('HOST'), user = getenv('USER'), password = getenv('PASSWORD'), database = getenv('DATABASE'))
    print('Connected to database')
    return con

def disconnect(con : Connection):
    con.close()
    print('Disconnected from database')

def query(con : Connection, sql : str, vals : tuple) -> tuple:
    cursor = con.cursor()
    cursor.execute(sql, vals)
    con.commit()
    rows = cursor.fetchall()
    cursor.close()
    return rows