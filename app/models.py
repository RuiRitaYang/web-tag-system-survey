from app import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.Integer, nullable=True)
  consented = db.Column(db.Boolean, nullable=True)
  date_added = db.Column(db.DateTime, default=datetime.utcnow())

  # Create A String
  def __ref__(self):
    return 'ID %d has consented (%d) on %r'.format(self.uuid, self.consented, self.date_added)

class UUIDForm(FlaskForm):
  uuid = StringField("What's the UUID (sent through email)?", validators=[DataRequired()])
  submit = SubmitField('Submit')

class RoutineTag(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  uid = db.Column(db.Integer, nullable=True)
  rtn_id = db.Column(db.Integer, nullable=True)
  rtn_tags = db.Column(db.String(300), nullable=True)
  cmd1_tag = db.Column(db.String(20), nullable=True)
  cmd2_tag = db.Column(db.String(20), nullable=True)

  def __ref__(self):
    return 'Updated routine %d for uid %d'.format(self.rtn_id, self.uid)
