from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "my secret key"
# Initialize the database
db = SQLAlchemy(app)


class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  consented = db.Column(db.Boolean, nullable=True)
  date_added = db.Column(db.DateTime, default=datetime.utcnow())

  # Create A String
  def __ref__(self):
    return 'ID %d has consented (%d) on %r'.format(self.id, self.consented, self.date_added)


from app import routes

# @app.route("/")
# def homepage():
#   return jsonify({"state": "OK"})
