import json
import os
import random

from app import app, db
from app.models import Users, UUIDForm, RoutineTag
from flask import render_template, request, redirect, jsonify, flash, session
from app.utils import *


@app.before_request
def before_request_func():
  pass


@app.route('/', methods=['GET', 'POST'])
def index():
  uuid = None
  form = UUIDForm()
  if form.validate_on_submit():
    # TODO(@ry): check to database and record to database
    uuid = form.uuid.data
    user = Users.query.filter_by(uuid=uuid).first()
    if user is None:
      user = Users(uuid=uuid)
      db.session.add(user)
      db.session.commit()
    flash("Welcome dear participants! ")
    session['uuid'] = uuid
    form.uuid.data = ''
    return render_template('consent_form.html', uuid=uuid, consented=None)
  return render_template('id_validation.html', uuid=uuid, form=form)

@app.route('/consented', methods=['GET', 'POST'])
def consented():
  consent = request.form.get('consent')
  if consent == 'y':
    return render_template('background.html')
  else:
    return render_template('finish.html', finished=False)

@app.route('/tag', methods=['GET', 'POST'])
def tag():
  scenarios, routines = get_all_scenarios_routines()
  # TODO: fixed ids read from database
  scenario_ids = random.sample(range(0, 2), 2)
  scn_info = scenarios[scenario_ids[0]]
  rtn_ids = scn_info['rtn_ids']
  rtn_info_all = [rtn for rtn in routines if rtn["rtn_id"] in rtn_ids]
  ind = 0

  if request.method == 'POST' and 'tag-page-action' in request.form:
    action = request.form['tag-page-action']
    if action == 'Previous':
      ind -= 1
    elif action == 'Next':
      ind += 1
    elif action == 'Finish':
      return render_template('scenario.html')

  return render_template('tagging.html',
                         rtn_info=rtn_info_all[ind],
                         rid=ind + 1,
                         total_rtn=2)

@app.route('/updateList', methods=['GET', 'POST'])
def update_list():
  item = request.get_json()['item']
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)

@app.route('/tag-submit', methods=['GET', 'POST'])
def tag_submit():
  # TODO: stored in database
  return render_template('scenario.html')

@app.route('/scenario-submit', methods=['GET', 'POST'])
def scenario_submit():
  return render_template('easy_of_use.html')

@app.route('/eou-submit', methods=['GET', 'POST'])
def ease_of_use_submit():

  return render_template('finish.html', finished=1)

@app.route('/finish-submit', methods=['GET', 'POST'])
def finish_submit():
  if request.method == 'POST':
    email = request.form.get('email')
    interview = request.form.get('interview')
    return render_template('finish.html', finished=2)

@app.route('/db', methods=['POST', 'GET'])
def dbtests():
  if request.method == 'POST':
    uid = request.form['uid']
    new_user = Users(uid=uid)
    # Push to database
    try:
      db.session.add(new_user)
      db.session.commit()
      return redirect('/db')
    except Exception as e:
      return "Error for storing new user info:" + str(e)
  else:
    users = Users.query.order_by(Users.date_added)
    return render_template('db_test.html', users=users)
