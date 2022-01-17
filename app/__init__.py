from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Add Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:11111111@localhost/test_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "my secret key"
# Initialize the database
db = SQLAlchemy(app)

from app import routes

# @app.route("/")
# def homepage():
#   return jsonify({"state": "OK"})

