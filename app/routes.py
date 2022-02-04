import random
from unicodedata import name
import uuid

from app import app, db
from app.database import commit_eou_record, db_commit, delete_customized_tag, \
  get_all_customized_tag, get_email_and_itv, \
  get_scn_ids_by_uuid, \
  get_rtn_ids_by_uuid, record_finish_time, update_customized_tag, update_email_itv, update_itv, \
  record_multi_scn_stt_scores
from app.models import FinishForm, Users, RoutineTag, UUIDForm, EaseOfUseForm
from app.system import get_user_scn_outcome
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
      scn_ids = random.sample(range(1, 5), 4)
      rtn_ids = get_rtn_ids_by_scn_ids(scn_ids)
      user = Users(uuid=uuid,
                   scn_ids=','.join([str(v) for v in scn_ids]),
                   rtn_ids=','.join([str(v) for v in rtn_ids]))
      db.session.add(user)
      db.session.commit()
    flash("Welcome!")
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
  # Get all long routines for the specific user.
  rtn_ids = get_rtn_ids_by_uuid(session['uuid'])
  rtn_ids, rtn_info = get_long_rtn_info(rtn_ids)
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
  rid = rtn_ids[idx - 1]
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  if rtn_tags is None:
    rtn_tags = RoutineTag(uuid=session['uuid'], rtn_id=rid)
    db.session().add(rtn_tags)
    db.session().commit()

  all_cus_tag_list = get_all_customized_tag(session['uuid'])
  rtn_cus_tags = rtn_tags.rtn_cus_tags.split(',') if rtn_tags.rtn_cus_tags else []
  rtn_sys_tag = tag_display_name(rtn_tags.rtn_sys_tag)
  cmd1_tag = tag_display_name(rtn_tags.cmd1_tag)
  cmd2_tag = tag_display_name(rtn_tags.cmd2_tag)
  return render_template('tagging.html',
                         rtn_info=rtn_info[rid],
                         idx=idx,
                         rid=rid,
                         rtn_sys_tag=rtn_sys_tag,
                         all_cus_tag=all_cus_tag_list,
                         rtn_cus_tags=rtn_cus_tags,
                         cmd1_tag=cmd1_tag,
                         cmd2_tag=cmd2_tag,
                         total_rtn=total_rtn)

@app.route('/create-tag', methods=['GET', 'POST'])
def create_cus_tag():
  data = request.get_json()
  tag_name, priority = data['tag_name'], data['priority']
  status = update_customized_tag(session['uuid'], tag_name, priority)
  if status == 'empty name':
    flash('Tag name cannot be empty.')
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)

@app.route('/edit-tag', methods=['GET', 'POST'])
def edit_cus_tag():
  data = request.get_json()
  tag_name, priority = data['tag_name'], data['priority']
  update_customized_tag(session['uuid'], tag_name, priority)
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)

@app.route('/delete-tag', methods=['GET', 'POST'])
def delete_cus_tag():
  data = request.get_json()
  tag_name = data['tag_name']
  delete_customized_tag(session['uuid'], tag_name)
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)


@app.route('/update-sys-tag', methods=['GET', 'POST'])
def update_sys_tag():
  data = request.get_json()
  item, rid = data['item'], data['rid']
  item = internal_sys_name(item)
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
  item = internal_sys_name(item)
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  if item in ['Uninterruptible', 'Pausable']:
    rtn_tags.cmd1_tag = item
    # Update routine level system tag accordingly.
    if rtn_tags.cmd1_tag == rtn_tags.cmd2_tag:
      rtn_tags.rtn_sys_tag = rtn_tags.cmd1_tag
    else:
      rtn_tags.rtn_sys_tag = ''
  else:
    flash("Self-defined tag can only be put for routine!")
  db_commit(success_msg="Update CMD1 system tag successfully",
            fail_msg="[ERROR] CMD1 sys tag update failed")
  result = {'success': True, 'response': 'Done'}
  return jsonify(result)

@app.route('/update-cmd2-tag', methods=['GET', 'POST'])
def update_cmd2_tag():
  data = request.get_json()
  item, rid = data['item'], data['rid']
  item = internal_sys_name(item)
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  if item in ['Uninterruptible', 'Pausable']:
    rtn_tags.cmd2_tag = item
    if rtn_tags.cmd1_tag == rtn_tags.cmd2_tag:
      rtn_tags.rtn_sys_tag = rtn_tags.cmd2_tag
    else:
      rtn_tags.rtn_sys_tag = ''
  else:
    flash("Customized tag can only be put for routine!")

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

@app.route('/remove-cus-tag/<int:rid>/<int:idx>/<string:tag_name>',
           methods=['GET', 'POST'])
def remove_cus_tag(rid, idx, tag_name):
  rtn_tags = RoutineTag.query.get((session['uuid'], rid))
  rtn_tags.rtn_cus_tags = remove_cus_tag_in_string(
    rtn_tags.rtn_cus_tags, tag_name)
  db_commit(success_msg="RTN {0} cus tag {1} removed".format(rid, tag),
            fail_msg="[ERROR] RTN customized tag remove failed")
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

  # Read user record if they've filled for this scenario
  # no matter whether it has been pushed to database.
  sid = scn_ids[idx - 1]
  scn_info = get_scenario_by_id(sid)
  outcomes, scores, strategies = get_user_scn_outcome(
    session['uuid'], sid, scn_info)

  fst_oc_form = FstOutcomeForm()
  snd_oc_form = SndOutcomeForm() if len(scores) > 1 else None
  if request.method == 'POST' and 'scn-page-action' in request.form:
    # Record user choice
    scores = [fst_oc_form.oc1.data]
    if snd_oc_form:
      scores.append(snd_oc_form.oc2.data)
    record_multi_scn_stt_scores(
      session['uuid'], sid, strategies, scores)

    # Navigate among scenarios
    action = request.form['scn-page-action']
    if action == 'Previous':
      return redirect(url_for('scenario', idx=idx-1))
    elif action == 'Next':
      return redirect(url_for('scenario', idx=idx+1))
    elif action == 'Finish':
      return redirect(url_for('ease_of_use'))

  fst_oc_form, snd_oc_form = get_outcome_forms(scores)
  return render_template('scenario.html',
                         idx=idx,
                         sid=sid,
                         scn_description=scn_info['scn_description'],
                         outcome=outcomes,
                         total_scn=total_scn,
                         fst_oc_form=fst_oc_form,
                         snd_oc_form=snd_oc_form)

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
    responses['open'] = form.open_ended.data
    commit_eou_record(session['uuid'], responses)
    return redirect(url_for('finish', status=1))

  return render_template('easy_of_use.html',
                         form=form,
                         descriptions=descriptions)

@app.route('/finish/<int:status>', methods=['GET', 'POST'])
def finish(status):
  form = FinishForm()
  email, itv = get_email_and_itv(session['uuid']) if status >= 1 else [None, None]
  if status == 3:
    record_finish_time(session['uuid'])

  if form.validate_on_submit():
    e_confirm = form.email_confirm.data if email is not None else 0
    # Deal with last step refresh
    if e_confirm is None:
      e_confirm = 1 if email is not None else 0
    itv_interest = int(form.interview.data)
    if int(e_confirm):
      update_itv(session['uuid'], itv_interest)
      form.interview.data = None
      return redirect(url_for('finish', status=3))
    if not int(e_confirm) and form.email.data:
      email = form.email.data
      update_email_itv(session['uuid'], email, itv_interest)
      form.email.data = None
      form.interview.data = None
      return redirect(url_for('finish', status=3))
    if not int(e_confirm) and not form.email.data:
      return redirect(url_for('finish', status=2))
  return render_template('finish.html', finished=status,
                         email=email, form=form)
