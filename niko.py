import sqlite3, datetime, time, calendar, json
from datetime import timedelta
from calendar import timegm
from flask import Flask, request, session, redirect, url_for, g, render_template, abort, flash
from flask.ext.login import (LoginManager, current_user, redirect, login_required, login_user, logout_user, UserMixin, confirm_login)
from werkzeug.security import generate_password_hash, check_password_hash

# init things
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

# constructors
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

  def set_id(self):
    self.id = query_db('select id from users where username=?', (self.username,))

class Mood():
  def __init__(self, value, userid, username, entry_date, new=False):
    self.value = value
    self.userid = userid
    self.username = username
    self.entry_date = entry_date
    self.new = new
    if self.new:
      self.store_mood()

  def store_mood(self):
    entry = query_db('insert into entries (mood, userid, username, entry_date) values (?, ?, ?, ?)', [self.value, self.userid, self.username, self.entry_date])
    g.db.commit()

# helpers

# dependency of flask-login
# does flask-login tear this down somewhere?
# get a nonetype, not callable error if I call it
@login_manager.user_loader
def load_user_by_id(id):
  return create_user_instance(id, 'id')

def load_user_by_name(username):
  return create_user_instance(username, 'username')

def create_user_instance(identifier, param_type):
  db_user = query_db('select username, email, password, id from users where (' + param_type + ' = ?)', (identifier,), one=True)
  if db_user:
    return User(db_user.get('username'), db_user.get('email'), db_user.get('password'), db_user.get('id'))
  return None

# gives nice return value from db query
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

# timespan = tuple(recent date, oldest date)
def get_moods(timespan):
  assert not isinstance(timespan, basestring)
  return query_db('select * from entries where entry_date > ? and entry_date < ? order by entry_date asc', (timespan[0], timespan[1]))

def get_team_members():
  return query_db('select username, id from users')

# returns monday of last week
def get_one_week_ago():
  today = datetime.datetime.now()
  return today - timedelta(days=today.weekday()) + timedelta(days=0, weeks=-1)

# returns friday of last week
def get_last_available_day():
  today = datetime.datetime.now()
  return today - timedelta(days=today.weekday()) + timedelta(days=4, weeks=-1)

# takes datetime obj
# returns unix timestamp
def get_unix_timestamp(date):
  return int(calendar.timegm(date.timetuple()))

# takes unix timestamp
# returns date object
def get_date(timestamp):
  return datetime.datetime.fromtimestamp(timestamp)

# returns unix timestamp 
def get_date_yesterday():
  return get_unix_timestamp(datetime.datetime.now() - timedelta(days=1))

# two datetime objs and a bool
def get_date_range(start_date, end_date, weekday=False):
  date_range = []
  for one_date in (start_date + datetime.timedelta(n) for n in range((end_date - start_date).days + 1)):
    date_range.append(get_pretty_date(one_date, weekday))
  return date_range

def get_pretty_date(date, day_of_week=False):
  string_format = '%A %m/%d/%Y' if day_of_week == True else '%m/%d/%Y'
  return date.strftime(string_format)

def get_entries_by_week():
  monday = get_one_week_ago()
  friday = get_last_available_day()
  return [get_moods((get_unix_timestamp(monday), get_unix_timestamp(friday))), get_date_range(monday, friday)] 

def get_entries_by_month(ref_date=get_last_available_day()):
  last_day = datetime.datetime.combine(datetime.date(ref_date.year, ref_date.month+1, 1) - datetime.timedelta(1,0,0), datetime.time(23, 59, 59))
  if last_day.month == datetime.datetime.now().month:
    last_day = ref_date

  first_day = datetime.datetime.combine(datetime.date(ref_date.year, ref_date.month, 1) + datetime.timedelta(0), datetime.time(0))
  return [get_moods((get_unix_timestamp(first_day), get_unix_timestamp(last_day))), get_date_range(first_day, last_day, True)]

chart_request_params = {
  1: get_entries_by_week,
  2: get_entries_by_month
}

chart_time_map = {
  1: 'week',
  2: 'month'
}

# yuck
def assemble_chart(period):
  moods = chart_request_params[int(period)]()  
  template_data = {}
  template_data['date_range'] = moods.pop()
  template_data['user_records'] = {}
  for record in moods[0]:
    mood = {get_pretty_date(get_date(record['entry_date']), day_of_week = True if int(period) > 1 else False): record['mood']}
    if template_data['user_records'].get(record['username']):
      template_data['user_records'][record['username']].append(mood)  
    else:
      template_data['user_records'][record['username']] = [mood]
  return template_data

# ROUTES
# index
@app.route('/')
def index():
  if g.user.is_authenticated():
    return redirect(url_for('dashboard'))
  return redirect(url_for('login_page'))

# login form
@app.route('/login', methods=['GET', 'POST'])
def login_page():
  if request.method == 'POST':
    g.user = load_user_by_name(request.form.get('username'))
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

days_of_week = ['M', 'Tu', 'W', 'Th', 'F']

# chart request
@app.route('/chart', methods=['POST'])
@login_required
def show_chart():
  if request.method == 'POST':
    return redirect(url_for('show_chart_' + chart_time_map[int(request.form['time_period'])]))
  return render_template('dashboard.html', user = g.user)

@app.route('/chart/week')
@login_required
def show_chart_week():
  return render_template('chart_week.html', chart = assemble_chart(1), weekdays = days_of_week)

@app.route('/chart/month')
@login_required
def show_chart_month():
  return render_template('chart_month.html', chart = assemble_chart(2), weekdays = days_of_week)

@app.route('/export')
@login_required
def export_data():
  # throw out a csv or something
  return

# record mood entry
@app.route('/log', methods=['POST'])
@login_required
def log_mood():
  if request.method == 'POST':
    entry_date = get_unix_timestamp(datetime.datetime.now()) if request.form['entry_for'] == 'today' else get_date_yesterday()
    Mood(request.form['mood'], request.form['userid'], request.form['username'], entry_date, new=True) 
    return redirect(url_for('dashboard'))
  return 'try again'

# potential future bot endpoint
@app.route('/nikobot', methods=['POST'])
def nikobot_log():
  return

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
