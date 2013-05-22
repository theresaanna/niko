from Niko_DB import query_db

# returns team id int
def create_team(team_name):
  cur = g.db.cursor()
  g.db.execute('insert into teams (name) values (?)', (team_name,))
  g.db.commit()
  team_id = cur.lastrowid
  cur.close()
  return team_id

def get_team_name(team_id):
  return query_db('select name from teams where id = ?', (team_id,))

def get_team_list():
  return query_db('select id, name from teams')
