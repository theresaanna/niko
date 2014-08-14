# Niko

Supporting the idea that team member happiness is a valuable indicator of team success. More on the Niko Niko method of tracking team happiness: [http://agiletrail.com/2011/09/12/how-to-track-the-teams-mood-with-a-niko-niko-calendar/]

Niko is very much under development.

## Tech
Niko is an app written in Python using the Flask [http://flask.pocoo.org/] web framework. It uses Flask-Login [http://pythonhosted.org/Flask-Login/] for user registration and authentication. It stores data using a Sqlite3 database.

## What is Niko?
It has a simple interface to let team members log their mood based on five different mood faces for the current day or yesterday. You can see a chart of team members' moods displayed in various time increments. The soonest you can see mood ratings from teammembers is seven days later. This is a social decision translated into code. People tend to be influenced by self-reports from others around them.

## Why?
There are other much prettier apps that will collect mood tracking information. I needed to be able to install a tool that would capture data on internal servers, hence Niko.

## How?
### Dependencies:
- [pip](https://pypi.python.org/pypi/pip)
- [sqlite3](http://www.sqlite.org/)

##### For Python package dependencies:
```
cd niko
pip install -r requirements.txt
```

### Create new database:
```
sqlite3 db/dev.db < db/schema.sql
```

### To configure Niko:
```
cd niko
cp example_config.cfg config.cfg
```
Be sure to change the value of ```SECRET_KEY```

### To run Niko:
```
python niko.py
```
