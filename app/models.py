from app import db
from datetime import datetime
import email_validator
from flask_wtf import FlaskForm
from wtforms import EmailField, IntegerField, StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, Optional


class Users(db.Model):
  uuid = db.Column(db.Integer, primary_key=True)
  scn_ids = db.Column(db.String(30), nullable=True)
  rtn_ids = db.Column(db.String(90), nullable=True)
  consented = db.Column(db.Boolean, nullable=True)
  email = db.Column(db.String(50), nullable=True)
  interview = db.Column(db.Boolean(), nullable=True)
  date_added = db.Column(db.DateTime, default=datetime.utcnow())
  date_finished = db.Column(db.DateTime, nullable=True)

  def __ref__(self):
    return 'ID %d has consented (%d) on %r'.format(self.uuid, self.consented, self.date_added)


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
  uuid = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30), primary_key=True)
  priority = db.Column(db.Integer, default=5)

  def __ref__(self):
    return 'New customized tag %s for user %d'.format(self.name, self.uuid)


class EaseOfUseRecord(db.Model):
  uuid = db.Column(db.Integer, primary_key=True)
  qid = db.Column(db.Integer, primary_key=True)
  score = db.Column(db.Integer, nullable=True)


class UUIDForm(FlaskForm):
  uuid = StringField("What's the UUID (sent through email)?", validators=[DataRequired()])
  submit = SubmitField('Submit')


class EaseOfUseForm(FlaskForm):
  options = [(1, 'Strongly disagree'),
             (2, 'Somewhat disagree'),
             (3, 'Neither agree nor disagree'),
             (4, 'Somewhat agree'),
             (5, 'Strongly agree')]

  q0 = RadioField('q0', choices=options)
  q1 = RadioField('q1', choices=options)
  q2 = RadioField('q2', choices=options)
  q3 = RadioField('q3', choices=options)
  q4 = RadioField('q4', choices=options)
  q5 = RadioField('q5', choices=options)
  q6 = RadioField('q6', choices=options)
  q7 = RadioField('q7', choices=options)
  q8 = RadioField('q8', choices=options)
  submit = SubmitField('Submit')


class FinishForm(FlaskForm):
  email_confirm = RadioField(
    'conf_email',
    choices=[(1, 'Yes'), (0, 'No')],
    validators=[Optional()]
  )
  email = EmailField(
    'email',
    validators=[Optional(), Email(granular_message=True)])
  interview = RadioField('interview',
                         choices=[(1, 'Yes'), (0, 'No')],
                         validators=[DataRequired()])
  submit = SubmitField('Submit')
