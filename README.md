# Web Tag System Survey

This is a web application for tag system survey including front-end and 
back-end design.

This web application is built based on Python Flask.

## Prerequisite
- Python 3
To install necessary messages:
```commandline
pip3 install flask flask-wtf Flask-Bootstrap4 
pip3 install mysql-connector mysql-connector-python mysql-connector-python-rf
pip3 install flask_sqlalchemy pymysql pyyaml cryptography 
```

## How to run
Under the root folder
```commandline
export FLASK_APP = app
export FLASK_DEBUG = 1  # this is only for debugging
flask run
```
If FLASK_DEBUG is set as 1, backend debugging information will be shown
in the command line.


## How to deploy the database locally
**If using SQLite (built-in by python).** Follow the following steps:
- Stop the running backend.
- Open Python3 shell
  - from app import db
  - db.create_all()
  - exit()
- Then there will a defined .db file stored locally in the app/ folder
- Start the website by `flask run`

**If using mySQL database locally**
- Start database server in the backend
- Update password and uri information in the `__init__.py`
- Follow the same steps for using SQLite.