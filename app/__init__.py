from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "my secret key"
# Initialize the database
db = SQLAlchemy(app)

from app import routes
