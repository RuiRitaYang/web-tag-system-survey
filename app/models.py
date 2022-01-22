from app import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Users(db.Model):
  uuid = db.Column(db.Integer, primary_key=True)
  scn_ids = db.Column(db.String(30), nullable=True)
  consented = db.Column(db.Boolean, nullable=True)
  date_added = db.Column(db.DateTime, default=datetime.utcnow())
  date_finished = db.Column(db.DateTime, nullable=True)

  def __ref__(self):
    return 'ID %d has consented (%d) on %r'.format(self.uuid, self.consented, self.date_added)

class UUIDForm(FlaskForm):
  uuid = StringField("What's the UUID (sent through email)?", validators=[DataRequired()])
  submit = SubmitField('Submit')

class RoutineTag(db.Model):
  uuid = db.Column(db.Integer, primary_key=True)
  rtn_id = db.Column(db.Integer, primary_key=True)
  rtn_sys_tag = db.Column(db.String(20), nullable=True)
  rtn_cus_tags = db.Column(db.String(300), nullable=True)
  cmd1_tag = db.Column(db.String(20), nullable=True)
  cmd2_tag = db.Column(db.String(20), nullable=True)

  def __ref__(self):
    return "Tagging record for user {0} routine {1} with cus_tags {2}".format(
      self.uuid, self.rtn_id, self.rtn_cus_tags
    )

  def __str__(self):
    return self.__ref__()

class CustomizedTag(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.Integer)
  name = db.Column(db.String(30))
  priority = db.Column(db.Integer, default=5)

  def __ref__(self):
    return 'New customized tag %s for user %d'.format(self.name, self.uuid)
