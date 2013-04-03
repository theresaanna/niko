# I am a mess.

import sqlite3
from flask import Flask, request, session, redirect, url_for, g, render_template, abort, flash
from flask.ext.login import (LoginManager, current_user, redirect, login_required, login_user, logout_user, UserMixin, confirm_login)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.db = '/home/ubuntu/niko/db/niko.db'

# this... doesn't feel right
app.secret_key = 'hi'

def connect_db():
  return sqlite3.connect(app.config.db)

@app.before_request
def before_request():
  g.db = connect_db()
  g.user = current_user

@app.teardown_request
def teardown_request(exception):
  g.db.close()

login_manager = LoginManager()
login_manager.setup_app(app)

class User(UserMixin):
  def __init__(self, username, email, password, id, register=False):
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

@login_manager.user_loader
def load_user(id):
  return g.user   

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
  if g.user is not None:
    return redirect(url_for('dashboard'))
  return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
  if request.method == 'POST':
    db_user = query_db('select * from users where username=?', (request.form.get('username'), ), one=True)
    if db_user:
      g.user = User(db_user.get('username'), db_user.get('email'), db_user.get('password'), db_user.get('id'))
      if g.user.check_password(request.form.get('password')):
        login_user(g.user, remember=True)
        return redirect(url_for('dashboard'))
      return 'nope'
  return render_template('login.html') 

@app.route('/register', methods=['GET', 'POST'])
def register_user():
  if request.method == 'POST':
    user = User(request.form['username'], request.form['email'], request.form['password'], '', register=True)
    g.db.execute('insert into users (username, email, password) values (?, ?, ?)', 
                [user.username, user.email, user.hashed_pw])
    g.db.commit()
    flash('registered!')
    return redirect(url_for('login_page'))
  return render_template('create-user.html')    

@app.route('/dashboard')
def dashboard():
  user = g.user
  return 'dashboard'

@app.route('/log', methods=['POST'])
@login_required
def log_mood():
  g.db.execute('insert into entries (user, mood) values (?, ?)',
              [request.form['user'], request.form['mood']])
  g.db.commit()
  flash('Thanks for logging your mood')
  return

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
