from os import getenv
import pymysql

def connect():
  global con
  con = pymysql.connect(host = getenv('HOST'), user = getenv('USER'), password = getenv('PASSWORD'), database = getenv('DATABASE'))
  print('Connected to database')

def disconnect():
  con.close()
  print('Disconnected from database')

def query(sql, vals = None):
    cursor = con.cursor()
    cursor.execute(sql, vals)
    con.commit()
    rows = cursor.fetchall()
    cursor.close()
    return rows