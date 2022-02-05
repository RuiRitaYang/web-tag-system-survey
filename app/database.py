from app import db
from app.models import EaseOfUseRecord, TextResponse, Users, RoutineTag, CustomizedTag, \
  ScenarioOutcomeRecord
from app.utils import *

from datetime import datetime

def db_commit(success_msg="Update successfully",
              fail_msg="[ERROR] Failed for updating database record"):
  try:
    db.session.commit()
    print(success_msg)
  except Exception as e:
    print(fail_msg + "\nError: " + str(e))

#########################
## Starting page utils ##
#########################
def record_consented(uuid, consented: bool):
  user = Users.query.get_or_404(uuid)
  modified = True
  if user.consented == consented:
    modified = False
  else:
    user.consented = consented
  if modified:
    db_commit(success_msg='User {0} consented'.format(uuid),
              fail_msg='User {0} does not consented'.format(uuid))

########################
## Tagging page utils ##
########################
def get_scn_ids_by_uuid(uuid):
  scn_ids = Users.query.get_or_404(uuid).scn_ids
  scn_ids = [int(sid) for sid in scn_ids.split(',')]
  return scn_ids

# Input: user (Users type object)
def update_rtn_ids_record(user: Users):
  scn_ids = user.scn_ids
  rtn_ids = get_rtn_ids_by_scn_ids(scn_ids)
  # write to database
  user.rtn_ids = ','.join(rtn_ids)
  print("Writing RTN_IDS " + str(rtn_ids) + " for user " + user['uuid'])
  db.session.commit()
  return rtn_ids

def get_rtn_ids_by_uuid(uuid):
  user = Users.query.get_or_404(uuid)
  db_rtn_ids = user.rtn_ids
  if db_rtn_ids:
    return [int(rid) for rid in db_rtn_ids.split(',')]
  else:  # Generate rtn list based on scn ids
    return update_rtn_ids_record(user)

def get_tags_by_rtn_id(uuid, rtn_id):
  tags = RoutineTag.query.get((uuid, rtn_id))
  if not tags:
    return ['', '', '', 5]
  rtn_sys_tag = tags.rtn_sys_tag or ''
  cmd1_tag = tags.cmd1_tag or ''  # CMD1-specific tag
  cmd2_tag = tags.cmd2_tag or ''  # CMD2-specific tag
  rtn_cus_tags = tags.rtn_cus_tags
  if rtn_cus_tags:
    rtn_cus_tags = rtn_cus_tags.split(',')
  final_priority = 0
  # Get the highest priority of customized tags.
  if rtn_cus_tags:
    for tag_name in rtn_cus_tags:
      cus_tag = CustomizedTag.query.get_or_404((uuid, tag_name))
      priority = cus_tag.priority
      if priority > final_priority:
        final_priority = priority
  return [rtn_sys_tag, cmd1_tag, cmd2_tag, final_priority]

def update_customized_tag(uuid, tag_name, priority=5):
  cus_tag = CustomizedTag.query.get((uuid, tag_name))
  print('try to udpate ============')
  if not tag_name:
    return 'empty name'
  if not priority:
    priority = 5
  modified = True
  if not cus_tag:
    cus_tag = CustomizedTag(uuid=uuid, name=tag_name, priority=priority)
    db.session().add(cus_tag)
  elif cus_tag.priority == priority:
    modified = False
  else:
    cus_tag.priority = priority

  if modified:
    db_commit(
      success_msg='Update user {} customized tag {} with ' +
                  'priority {}'.format(uuid, tag_name, priority),
      fail_msg='[ERROR] failed to update customized tag info!'
    )
  return 'success'

def delete_customized_tag(uuid, tag_name):
  cus_tag = CustomizedTag.query.get_or_404((uuid, tag_name))
  db.session.delete(cus_tag)
  db_commit(
    success_msg='Deleted user {} customized tag {}'.format(
      uuid, tag_name),
    fail_msg='[ERROR] failed to delete customized tag'
  )

def get_all_customized_tag(uuid):
  all_tags = CustomizedTag.query.filter_by(uuid=uuid).all()
  return all_tags

def record_tag_reason(uuid, rid, reason):
  rtn_tag = RoutineTag.query.get((uuid, rid))
  modified = True
  if not rtn_tag:
    rtn_tag = RoutineTag(uuid=uuid, rtn_id=rid, tag_reason=reason)
    db.session.add(rtn_tag)
  elif reason and rtn_tag.tag_reason != reason:
    rtn_tag.tag_reason = reason
  else:
    modified = False
  if modified:
    db_commit(success_msg="Update user {} rtn {} reason".format(uuid, rid),
              fail_msg="[ERROR] Failed to update tag reasoning.")

############################
## Scenario Outcome Utils ##
############################
def get_scn_stt_score_from_db(uuid, scn_id, stt):
  sat_score = ScenarioOutcomeRecord.query.get((
    uuid, scn_id, stt))
  return sat_score.score if sat_score else None

def record_multi_scn_stt_scores_w_reason(
    uuid, scn_id, all_stt: list, scores: list, reason):
  for i, stt in enumerate(all_stt):
    record_scn_stt_satisfaction(uuid, scn_id, stt, scores[i])
  if reason:
    text_resp = TextResponse.query.get(uuid)
    if not text_resp:
      text_resp = TextResponse(uuid=uuid)
      db.session.add(text_resp)
    exec('text_resp.s{}_reason = reason'.format(scn_id))
    db_commit(
      success_msg='Update text response for scn {} for '
                  'user {}'.format(scn_id, uuid),
      fail_msg='[ERROR] #SCNTR Text response failed to record')

def record_scn_stt_satisfaction(uuid, scn_id, stt, score):
  modified = True
  sat_score = ScenarioOutcomeRecord.query.get((
    uuid, scn_id, stt))
  if not sat_score:
    sat_score = ScenarioOutcomeRecord(
      uuid=uuid, sid=scn_id, strategy=stt, score=score)
    db.session.add(sat_score)
  elif sat_score.score == score:
    modified = False
  else:
    sat_score.score = score

  if modified:
    db_commit(success_msg='Update USER {0} scn {1} stt {2} score ' +
                          'to {3}'.format(uuid, scn_id, stt, score),
              fail_msg='[ERROR] Fail when updating scenario outcome score.')

#######################
## Ease of Use utils ##
#######################
def get_eou_record(uuid):
  eou_scores = {}
  for qid in range(9):
    q_score = EaseOfUseRecord.query.get((uuid, qid))
    if q_score:
      eou_scores[qid] = q_score.score
  return eou_scores

def commit_eou_record(uuid, responses):
  for qid in responses:
    modified = True
    if qid == 'open':  # Record open-ended question
      feedback = TextResponse.query.get(uuid)
      if not feedback:
        feedback = TextResponse(uuid=uuid, eou_feedback=responses[qid])
        db.session.add(feedback)
      elif feedback.eou_feedback == responses[qid]:
        modified = False
      else:
        feedback.eou_feedback = responses[qid]
    else:  # Record ease of use multiple choice results
      resp = EaseOfUseRecord.query.get((uuid, qid))
      if not resp:
        resp = EaseOfUseRecord(uuid=uuid, qid=qid, score=responses[qid])
        db.session.add(resp)
      else:
        if resp.score == int(responses[qid]):
          modified = False
        else:
          resp.score = responses[qid]
    if modified:
      db_commit(success_msg='Update q{0} record successfully'.format(qid),
                fail_msg='[ERROR] ease_of_use record udpate failed.')

#######################
## Finish page utils ##
#######################
def get_email(uuid):
  user = Users.query.get(uuid)
  if not user:
    print('[ERROR] Invalid uuid that is acquiring email.')
    return ''
  return user.email

def get_email_and_itv(uuid):
  user = Users.query.get(uuid)
  if not user:
    print('[ERROR] Invalid uuid that is acquiring email.')
    return ''
  return user.email, user.interview

def update_email(uuid, email):
  user = Users.query.get(uuid)
  if not user:
    print('[ERROR] Invalid uuid that is acquiring email.')
  user.email = email
  db_commit(success_msg='Update uuid {} email {} correctly'.format(uuid, email),
            fail_msg='[ERROR] failed to update email')

def update_itv(uuid, itv):
  user = Users.query.get(uuid)
  if not user:
    print('[ERROR] Invalid uuid that is acquiring email.')
    return
  user.interview = int(itv)
  db_commit(
    success_msg='Update {} interview interest {}.'.format(
      uuid, user.interview),
    fail_msg='[ERROR] failed to update interview interest.'
  )

def update_email_itv(uuid, email, itv):
  user = Users.query.get(uuid)
  if not user:
    print('[ERROR] Invalid uuid that is acquiring email.')
    return
  user.email = email
  user.interview = int(itv)
  db_commit(
    success_msg='Update {} email {} and interview state {}.'.format(
      uuid, email, int(itv)),
    fail_msg='[ERROR] failed to update email and interview interest.'
  )

def record_finish_time(uuid):
  user = Users.query.get(uuid)
  if not user:
    user = Users(uuid=uuid)
    db.session.add(user)
  user.date_finished = datetime.utcnow()
  db_commit(success_msg="Update survey finish time for user " + str(uuid),
            fail_msg="[ERROR] Failed to record finish time")
