import random

from app import app, db
from app.database import db_commit, get_scn_ids_by_uuid, get_rtn_ids_by_uuid
from app.models import Users, RoutineTag, UUIDForm, EaseOfUseForm
from app.system import get_outcome_info_by_stt, get_tag_outcome_by_scn_info
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
      scn_ids = random.sample(range(1, 5), 2)
      rtn_ids = get_rtn_ids_by_scn_ids(scn_ids)
      user = Users(uuid=uuid,
                   scn_ids=','.join([str(v) for v in scn_ids]),
                   rtn_ids=','.join([str(v) for v in rtn_ids]))
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

@app.route('/tag/<int:idx>', methods=['GET', 'POST'])
def tag(idx):
  rtn_ids = get_rtn_ids_by_uuid(session['uuid'])
  total_rtn = len(rtn_ids)
  print("Current idx: " + str(idx) + " Total rtn: ", total_rtn)
  if idx < 1 or idx > total_rtn:
    return redirect(url_for('tag', idx=1))
  if request.method == 'POST' and 'tag-page-action' in request.form:
    action = request.form['tag-page-action']
    if action == 'Previous':
      return redirect(url_for('tag', idx=idx-1))
    elif action == 'Next':
      return redirect(url_for('tag', idx=idx+1))
    elif action == 'Finish':
      return redirect(url_for('scenario', idx=0))

  # Start to show the page.
  scenarios, routines = get_all_scenarios_routines()
  rtn_info_all = [rtn for rtn in routines if rtn["rtn_id"] in rtn_ids]
  rid = rtn_ids[idx - 1]
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  if rtn_tags is None:
    rtn_tags = RoutineTag(uuid=session['uuid'], rtn_id=rid)
    db.session().add(rtn_tags)
    db.session().commit()
  rtn_cus_tags = rtn_tags.rtn_cus_tags.split(',') if rtn_tags.rtn_cus_tags else []
  return render_template('tagging.html',
                         rtn_info=rtn_info_all[idx - 1],
                         idx=idx,
                         rid=rid,
                         rtn_sys_tag=rtn_tags.rtn_sys_tag,
                         rtn_cus_tags=rtn_cus_tags,
                         cmd1_tag=rtn_tags.cmd1_tag,
                         cmd2_tag=rtn_tags.cmd2_tag,
                         total_rtn=total_rtn)

@app.route('/update-sys-tag', methods=['GET', 'POST'])
def update_sys_tag():
  data = request.get_json()
  item, rid = data['item'], data['rid']
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  if item in ['Uninterruptible', 'Pausable']:
    rtn_tags.rtn_sys_tag = item
    rtn_tags.cmd1_tag = item
    rtn_tags.cmd2_tag = item
  else:
    if rtn_tags.rtn_cus_tags:
      if item not in rtn_tags.rtn_cus_tags.split(','):
        rtn_tags.rtn_cus_tags += ',' + item
    else:
      rtn_tags.rtn_cus_tags = item

  db_commit()
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)

@app.route('/update-cmd1-tag', methods=['GET', 'POST'])
def update_cmd1_tag():
  data = request.get_json()
  item, rid = data['item'], data['rid']
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  if item in ['Uninterruptible', 'Pausable']:
    rtn_tags.cmd1_tag = item
    # Update routine level system tag accordingly.
    if rtn_tags.cmd1_tag == rtn_tags.cmd2_tag:
      rtn_tags.rtn_sys_tag = rtn_tags.cmd1_tag
    else:
      rtn_tags.rtn_sys_tag = ''
  db_commit(success_msg="Update CMD1 system tag successfully",
            fail_msg="[ERROR] CMD1 sys tag update failed")
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)

@app.route('/update-cmd2-tag', methods=['GET', 'POST'])
def update_cmd2_tag():
  data = request.get_json()
  item, rid = data['item'], data['rid']
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  if item in ['Uninterruptible', 'Pausable']:
    rtn_tags.cmd2_tag = item
    if rtn_tags.cmd1_tag == rtn_tags.cmd2_tag:
      rtn_tags.rtn_sys_tag = rtn_tags.cmd2_tag
    else:
      rtn_tags.rtn_sys_tag = ''
  db_commit(success_msg="Update CMD2 system tag successfully",
            fail_msg="[ERROR] CMD2 sys tag update failed")
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)

@app.route('/remove-rtn-sys-tag/<int:rid>/<int:idx>', methods=['GET', 'POST'])
def remove_rtn_sys_tag(rid, idx):
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  rtn_tags.rtn_sys_tag = ''
  db_commit(success_msg="RTN {0} system tag removed".format(rid),
            fail_msg="[ERROR] RTN sys tag remove failed")
  return redirect(url_for('tag', idx=idx))

@app.route('/remove-cmd1-tag/<int:rid>/<int:idx>', methods=['GET', 'POST'])
def remove_cmd1_tag(rid, idx):
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  rtn_tags.cmd1_tag = ''
  db_commit(success_msg="RTN {0} (rid {1}) CMD1 tag removed".format(idx, rid),
            fail_msg="[ERROR] RTN {0} CMD1 tag remove failed".format(rid))
  return redirect(url_for('tag', idx=idx))

@app.route('/remove-cmd2-tag/<int:rid>/<int:idx>', methods=['GET', 'POST'])
def remove_cmd2_tag(rid, idx):
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  rtn_tags.cmd2_tag = ''
  db_commit(success_msg="RTN {0} (rid {1}) CMD2 tag removed".format(idx, rid),
            fail_msg="[ERROR] RTN {0} CMD2 tag remove failed".format(rid))
  return redirect(url_for('tag', idx=idx))

@app.route('/scenario/<int:idx>', methods=['GET', 'POST'])
def scenario(idx):
  scn_ids = get_scn_ids_by_uuid(session['uuid'])
  total_scn = len(scn_ids)
  if idx < 1 or idx > total_scn:
    return redirect(url_for('scenario', idx=1))
  if request.method == 'POST' and 'scn-page-action' in request.form:
    action = request.form['scn-page-action']
    if action == 'Previous':
      return redirect(url_for('scenario', idx=idx-1))
    elif action == 'Next':
      return redirect(url_for('scenario', idx=idx+1))
    elif action == 'Finish':
      return redirect(url_for('ease_of_use'))

  sid = scn_ids[idx - 1]
  scn_info = get_scenario_by_id(sid)
  sys_outcome = [get_tag_outcome_by_scn_info(scn_info, session['uuid'])]
  ex_outcome = get_outcome_info_by_stt(scn_info, 'EX')
  if sys_outcome[0]['outcome_id'] != ex_outcome['outcome_id']:
    sys_outcome.append(ex_outcome)

  return render_template('scenario.html',
                         idx=idx,
                         sid=sid,
                         scn_description=scn_info['scn_description'],
                         outcome=sys_outcome,
                         total_scn=total_scn)

@app.route('/ease-of-use', methods=['GET', 'POST'])
def ease_of_use():
  form = EaseOfUseForm()
  if form.validate_on_submit():
    return render_template('finish.html', finished=1)
  return render_template('easy_of_use.html', form=form)

@app.route('/eou-submit', methods=['GET', 'POST'])
def ease_of_use_submit():
  return render_template('finish.html', finished=1)

@app.route('/finish-submit', methods=['GET', 'POST'])
def finish_submit():
  if request.method == 'POST':
    email = request.form.get('email')
    interview = request.form.get('interview')
    return render_template('finish.html', finished=2)
