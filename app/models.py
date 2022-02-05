from app import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, SubmitField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional, Length


class Users(db.Model):
  uuid = db.Column(db.Integer, primary_key=True)
  scn_ids = db.Column(db.String(30), nullable=True)
  rtn_ids = db.Column(db.String(90), nullable=True)
  consented = db.Column(db.Boolean, nullable=True)
  email = db.Column(db.String(50), nullable=True)
  interview = db.Column(db.Boolean, nullable=True)
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
  tag_reason = db.Column(db.String(500), nullable=True)

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

class ScenarioOutcomeRecord(db.Model):
  uuid = db.Column(db.Integer, primary_key=True)
  sid = db.Column(db.Integer, primary_key=True)
  strategy = db.Column(db.String(10), primary_key=True)
  score = db.Column(db.Integer, nullable=True)

class TextResponse(db.Model):
  uuid = db.Column(db.Integer, primary_key=True)
  eou_feedback = db.Column(db.String(500), nullable=True)
  s1_reason = db.Column(db.String(500), nullable=True)
  s2_reason = db.Column(db.String(500), nullable=True)
  s3_reason = db.Column(db.String(500), nullable=True)
  s4_reason = db.Column(db.String(500), nullable=True)

class UUIDForm(FlaskForm):
  uuid = StringField("What's the UUID (sent through email)?", validators=[DataRequired()])
  submit = SubmitField('Submit')

class EaseOfUseForm(FlaskForm):
  options = [(1, 'Strongly disagree'),
             (2, 'Somewhat disagree'),
             (3, 'Neither agree nor disagree'),
             (4, 'Somewhat agree'),
             (5, 'Strongly agree')]

  q0 = RadioField('q0', coerce=int, choices=options, validators=[DataRequired()])
  q1 = RadioField('q1', coerce=int, choices=options, validators=[DataRequired()])
  q2 = RadioField('q2', coerce=int, choices=options, validators=[DataRequired()])
  q3 = RadioField('q3', coerce=int, choices=options, validators=[DataRequired()])
  q4 = RadioField('q4', coerce=int, choices=options, validators=[DataRequired()])
  q5 = RadioField('q5', coerce=int, choices=options, validators=[DataRequired()])
  q6 = RadioField('q6', coerce=int, choices=options, validators=[DataRequired()])
  q7 = RadioField('q7', coerce=int, choices=options, validators=[DataRequired()])
  q8 = RadioField('q8', coerce=int, choices=options, validators=[DataRequired()])
  open_ended = TextAreaField('open_ended',
                             validators=[Optional(), Length(max=500)])
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

class FstOutcomeForm(FlaskForm):
  oc1 = RadioField(
    'satisfaction',
    choices=[(1, 'Unsatisfied'), (2, 'Slightly Unsatisfied'),
             (3, 'Neutral'), (4, 'Slightly Satisfied'),
             (5, 'Satisfied')],
    validators=[DataRequired()], coerce=int
  )

class SndOutcomeForm(FlaskForm):
  oc2 = RadioField(
    'satisfaction',
    choices=[(1, 'Unsatisfied'), (2, 'Slightly Unsatisfied'),
             (3, 'Neutral'), (4, 'Slightly Satisfied'),
             (5, 'Satisfied')],
    validators=[DataRequired()], coerce=int
  )

class ReasoningForm(FlaskForm):
  reason = TextAreaField('reason',
                         validators=[Optional(), Length(max=500)])
