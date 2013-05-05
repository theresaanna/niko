from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, LoginManager
from Niko_DB import query_db

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

# dependency of flask-login
# does flask-login tear this down somewhere?
# get a nonetype, not callable error if I call it
LoginManager().user_loader
def load_user_by_id(id):
  return create_user_instance(id, 'id')

def load_user_by_name(username):
  return create_user_instance(username, 'username')

# for creating User objects for existing accounts
def create_user_instance(identifier, param_type):
  db_user = query_db('select username, email, password, team, id from users where (' + param_type + ' = ?)', (identifier,), one=True)
  if db_user:
    return User(db_user.get('username'), db_user.get('email'), db_user.get('password'), db_user.get('team'), db_user.get('id'))
  return None
