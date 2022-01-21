import random

from app import app, db
from app.models import Users, UUIDForm, RoutineTag
from app.utils import *

from flask import render_template, request, redirect, jsonify, flash, session, url_for


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
    user = Users.query.get(uuid)
    if user is None:
      scenario_ids = random.sample(range(0, 2), 2)
      str_ids = [str(v) for v in scenario_ids]
      user = Users(uuid=uuid, scn_ids=','.join(str_ids))
      db.session.add(user)
      db.session.commit()
    flash("Welcome dear participants!")
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

@app.route('/tag/<int:rid>', methods=['GET', 'POST'])
def tag(rid):
  scenarios, routines = get_all_scenarios_routines()
  # Get assigned scenario from database
  scn_ids = Users.query.get_or_404(session['uuid']).scn_ids
  scn_ids = [int(sid) for sid in scn_ids.split(',')]
  rtn_ids = set()
  for scn_id in scn_ids:
    scn_info = scenarios[scn_id]
    rtn_ids.update(scn_info['rtn_ids'])
  rtn_info_all = [rtn for rtn in routines if rtn["rtn_id"] in rtn_ids]

  total_rtn = len(rtn_info_all)
  if rid < 1 or rid > total_rtn:
    rid = 1
  if request.method == 'POST' and 'tag-page-action' in request.form:
    action = request.form['tag-page-action']
    if action == 'Previous':
      rid -= 1
    elif action == 'Next':
      rid += 1
    elif action == 'Finish':
      return redirect(url_for('scenario'))
  # rtn_tags = RoutineTag.query.get(uuid=session['uuid'], rtn_id=rid)
  # rtn_cus_tags = rtn_tags.rtn_cus_tags.split(',')
  return render_template('tagging.html',
                         rtn_info=rtn_info_all[rid - 1],
                         rid=rid,
                         # rtn_sys_tag=rtn_tags.rtn_sys_tag,
                         # rtn_cus_tags=rtn_cus_tags,
                         # cmd1_tag=rtn_tags.cmd1_tag,
                         # cmd2_tag=rtn_tags.cmd2_tag,
                         total_rtn=total_rtn)

@app.route('/updateList', methods=['GET', 'POST'])
def update_list():
  item = request.get_json()['item']
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)

@app.route('/scenario', methods=['GET', 'POST'])
def scenario():
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
