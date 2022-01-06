import random

from app import app
from flask import render_template, request


@app.before_request
def before_request_func():
  pass


@app.route("/")
def index():
  return render_template('consent_form.html', consented=None)


@app.route("/consented", methods=['GET', 'POST'])
def consented():
  consent = request.form.get('consent')
  if consent == 'y':
    return render_template('background.html')
  else:
    return render_template('finish.html', finished=False)


@app.route("/tag", methods=['GET', 'POST'])
def tag():
  scenario_ids = random.sample(range(1, 20), 2)
  # TODO: stored in database
  # TODO: grab related routine information
  return render_template('tagging.html')
