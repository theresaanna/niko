# I am a mess.

import sqlite3, datetime, time
from flask import Flask, request, session, redirect, url_for, g, render_template, abort, flash
from flask.ext.login import (LoginManager, current_user, redirect, login_required, login_user, logout_user, UserMixin, confirm_login)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.db = '/home/ubuntu/niko/db/niko.db'

# this... doesn't feel right
app.secret_key = 'hi'

# db communication setup
def connect_db():
  return sqlite3.connect(app.config.db)

@app.before_request
def before_request():
  g.db = connect_db()
  if current_user is not None:
    g.user = current_user

@app.teardown_request
def teardown_request(exception):
  g.db.close()

# flask-login init
login_manager = LoginManager()
login_manager.setup_app(app)

class User(UserMixin):
  def __init__(self, username, email, password, id, register=False, active=True):
    self.username = username
    self.email = email
    self.password = password
    self.id = id
    self.register = register
    if register:
      self.hash_password(password)
      self.set_id()

  def hash_password(self, password):
    self.hashed_pw = generate_password_hash(str(password))

  def check_password(self, form_password):
    return check_password_hash(self.password, str(form_password))

  def set_id():
    self.id = query_db('select id from users where username=?', (self.username,))

class Mood():
  def __init__(self, value, user, entry_date, new=False):
    self.value = value
    self.user = user
    self.entry_date = entry_date
    self.new = new
    if self.new:
      self.store_mood()

  def store_mood(self):
    entry = query_db('insert into entries (mood, user, entry_date) values (?, ?, ?)', [self.value, self.user, self.entry_date])

# dependency of flask-login
@login_manager.user_loader
def load_user(hook):
  param_type = "id" if int(hook) else "username"
  db_user = query_db('select username, email, password, id from users where (' + param_type + ' = ?)', (hook,), one=True)
  return User(db_user.get('username'), db_user.get('email'), db_user.get('password'), db_user.get('id'))

# helpers
# gives nice return value from db query
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

# ROUTES
# index
@app.route('/')
def index():
  if g.user is not None:
    return redirect(url_for('dashboard'))
  return redirect(url_for('login_page'))

# login form
@app.route('/login', methods=['GET', 'POST'])
def login_page():
  if request.method == 'POST':
    g.user = load_user(request.form.get('username'))
    if g.user.check_password(request.form.get('password')):
      login_user(g.user, remember=True)
      return redirect(url_for('dashboard'))
    return 'nope'
  return render_template('login.html') 

# registration form
@app.route('/register', methods=['GET', 'POST'])
def register_user():
  if request.method == 'POST':
    if query_db('select id from users where username=?', (request.form['username'],)):
      return 'This username is already taken'
    user = User(request.form['username'], request.form['email'], request.form['password'], '', register=True)
    g.db.execute('insert into users (username, email, password) values (?, ?, ?)', 
                [user.username, user.email, user.hashed_pw])
    g.db.commit()
    return redirect(url_for('login_page'))
  return render_template('create-user.html')    

# user dashboard
@app.route('/dashboard')
@login_required
def dashboard():
  # if user has a mood for today
  # change form in template
  return render_template('dashboard.html', user = g.user)

# record mood entry
@app.route('/log', methods=['POST'])
@login_required
def log_mood():
  if request.method == 'POST':
    entry_date = time.mktime(datetime.datetime.now().timetuple()) if request.form['entry_for'] == 'today' else ''
    Mood(request.form['mood'], request.form['uid'], entry_date, new=True) 
    return redirect(url_for('dashboard'))
  return 'try again'

# potential future bot endpoint
@app.route('/nikobot', methods=['POST'])
def nikobot_log():
  return

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
