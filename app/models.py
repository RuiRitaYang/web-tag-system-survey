from app import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  uid = db.Column(db.Integer, nullable=True)
  consented = db.Column(db.Boolean, nullable=True)
  date_added = db.Column(db.DateTime, default=datetime.utcnow())

  # Create A String
  def __ref__(self):
    return 'ID %d has consented (%d) on %r'.format(self.uid, self.consented, self.date_added)

class UUIDForm(FlaskForm):
  uuid = StringField("What's the UUID (sent through email)?", validators=[DataRequired()])
  submit = SubmitField('Submit')