import random

from app import app, db
from app.database import commit_eou_record, db_commit, get_email_and_itv, get_scn_ids_by_uuid, \
  get_rtn_ids_by_uuid, update_email
from app.models import FinishForm, Users, RoutineTag, UUIDForm, EaseOfUseForm, EaseOfUseRecord
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
  descriptions = [
    'I think that I would like to use this system frequently.',
    'I found the system unnecessarily complex.',
    'I thought the system was easy to use.',
    'I think that I would need the support of a technical person to be able to use this system.',
    'I found the various functions in this system were well integrated.',
    'I thought there was too much inconsistency in this system.',
    'I would imagine that most people would learn to use this system very quickly.',
    'I found the system very cumbersome to use.',
    'I felt very confident using the system.'
  ]
  num_q = len(descriptions)
  form = EaseOfUseForm()

  if form.validate_on_submit():
    # Fetch ease-of-use responses
    responses = {}
    for i in range(num_q):
      exec('responses[{0}] = form.q{0}.data'.format(i))
    # commit to database
    commit_eou_record(session['uuid'], responses)
    return redirect(url_for('finish', status=1))

  return render_template('easy_of_use.html',
                         form=form,
                         descriptions=descriptions)

@app.route('/finish/<int:status>', methods=['GET', 'POST'])
def finish(status):
  form = FinishForm()
  email, itv = get_email_and_itv(session['uuid']) if status >= 1 else [None, None]

  if form.validate_on_submit():
    e_confirm = form.email_confirm.data if email is not None else 0
    if int(e_confirm):
      print('confirmed!')
      return render_template('finish.html', finished=3, email=email)
    if not int(e_confirm) and form.email.data:
      print('not confirmed! but with new email: ', form.email.data)
      email = form.email.data
      form.email.data = ''
      update_email(session['uuid'], email)
      return render_template('finish.html', finished=3, email=email)
    if not int(e_confirm) and not form.email.data:
      return render_template('finish.html', finished=2)
  print('Not valid yet')
  return render_template('finish.html', finished=status,
                         email=email, form=form)
