# Web Tag System Survey

This is a web application for tag system survey including front-end and 
back-end design.

This web application is built based on Python Flask.

## Prerequisite
- Python 3
To install necessary messages:
```commandline
pip3 install flask flask_sqlalchemy pymysql pyyaml 
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