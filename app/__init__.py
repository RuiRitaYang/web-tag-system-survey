from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Add Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# Posgres DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ruiyang:123654@localhost/survey_test'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vjehzfgxguljlq:1cbae71db7a73531e2f9bbfe0193d4461ab6a3d7ac08d43fd645393f6379436f@ec2-44-199-111-161.compute-1.amazonaws.com:5432/d3b1k5jus1if16'
# MySQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:11111111@localhost/test_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "my secret key"
# Initialize the database
db = SQLAlchemy(app)

from app import routes

# @app.route("/")
# def homepage():
#   return jsonify({"state": "OK"})

