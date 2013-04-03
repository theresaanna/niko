# I am a mess.

import sqlite3
from flask import Flask, request, session, redirect, url_for, g, render_template, abort, flash
from flask.ext.login import (LoginManager, current_user, redirect, login_required, login_user, logout_user, UserMixin, confirm_login)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.db = '/home/ubuntu/niko/db/niko.db'

# this... doesn't feel right
app.secret_key = '\xbb\xed,\xe3\xf1\xd4\xf5\x84\xd0\x96_\x9d~y\xfb)s\xfa13\xc7\x0b\x08\xe9'

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
  def __init__(self, username, email, password, id, active=True):
    self.username = username
    self.email = email
    self.set_password(password)
    self.id = id
    self.active = active

  def set_password(self, password):
    self.hashed_pw = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.hashed_pw, password)

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
  if g.user is not None and g.user.is_authenticated():
    return redirect(url_for('dashboard'))
  return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
  if request.method == 'POST':
    form_username = request.form.get('username')
    db_user = query_db('select * from users where username=?', (form_username, ), one=True)
    if db_user:
      g.user = User(db_user.get('username'), db_user.get('email'), db_user.get('password'), db_user.get('id'))
      if g.user.check_password(request.form.get('password')):
        login_user(g.user, remember=True)
        return redirect(url_for('dashboard'))
      return redirect(url_for('login_page'))
  return render_template('login.html') 

@app.route('/register', methods=['GET', 'POST'])
def register_user():
  if request.method == 'POST':
    user = User(request.form['username'], request.form['email'], request.form['password'])
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
