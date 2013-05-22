import sqlite3
from flask import g

def connect_db(db):
  return sqlite3.connect(db)

# gives nice return value from db query
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def update_db(query, args=()):
  g.db.execute(query, args)
  g.db.commit()
  return
