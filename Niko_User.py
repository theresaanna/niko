from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

class User(UserMixin):
  def __init__(self, username, email, password, team, id, register=False, active=True):
    self.username = username
    self.email = email
    self.password = password
    self.team = team
    self.id = id
    self.register = register
    if register:
      self._hash_password(password)
      self._set_id()

  def _hash_password(self, password):
    self.hashed_pw = generate_password_hash(str(password))

  def check_password(self, form_password):
    return check_password_hash(self.password, str(form_password))

  def _set_id(self):
    self.id = query_db('select id from users where username=?', (self.username,))

  def set_team(self, team_id):
    g.db.execute('update users set team = ? where id = ?', (team_id, self.id))
    g.db.commit()
    self.team = team_id


