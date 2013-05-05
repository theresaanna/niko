from Niko_DB import query_db
from flask.ext.login import g

class Mood():
  def __init__(self, value, userid, username, entry_date, new=False):
    self.value = value
    self.userid = userid
    self.username = username
    self.entry_date = entry_date
    self.new = new
    if self.new:
      self._store_mood()

  def _store_mood(self):
    entry = query_db('insert into entries (mood, userid, username, entry_date) values (?, ?, ?, ?)', [self.value, self.userid, self.username, self.entry_date])
    g.db.commit()


