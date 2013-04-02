import sqlite3
from flask import Flask, request, session, redirect, url_for, g, render_template, abort
from flask.ext.login import (LoginManager, current_user, redirect, login_required, login_user, logout_user, UserMixin, confirm_login)

app = Flask(__name__)

app.config.db = '/home/ubuntu/niko/db/niko.db'

# this... doesn't feel right
app.secret_key = '\xbb\xed,\xe3\xf1\xd4\xf5\x84\xd0\x96_\x9d~y\xfb)s\xfa13\xc7\x0b\x08\xe9'

def connect_db():
  return sqlite3.connect(app.config.db)

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  g.db.close()

login_manager = LoginManager()
login_manager.setup_app(app)

@login_manager.user_loader
def load_user(userid):
  return User.get(userid)

@app.route('/')
def main_page():
  if 'username' in session:
    return redirect(url_for('dashboard'))
  return redirect(url_for('login_user'))

@app.route('/login', methods=['GET', 'POST'])
def login_user():
  if request.method == 'POST':
    form = LoginForm()
    if form.validate_on_submit():
      login_user(user)
      flash('Welcome back')
      return redirect(url_for('dashboard'))
  return 'login form' 

@app.route('/dashboard')
def dashboard():
  if 'username' in session:
    return 'dashboard'
  return redirect(url_for('login_user'))

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
