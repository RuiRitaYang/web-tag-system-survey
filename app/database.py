from app import db
from app.models import EaseOfUseRecord, Users, RoutineTag, CustomizedTag
from app.utils import *
import random

def get_name():
  return random.choice(["Ann", "Bob"])

def db_commit(success_msg="Update successfully",
              fail_msg="[ERROR] Failed for updating database record"):
  try:
    db.session.commit()
    print(success_msg)
  except Exception as e:
    print(fail_msg + "\nError: " + str(e))

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
  tags = RoutineTag.query.get_or_404((uuid, rtn_id))
  rtn_sys_tag = tags.rtn_sys_tag
  cmd1_tag = tags.cmd1_tag  # CMD1-specific tag
  cmd2_tag = tags.cmd2_tag  # CMD2-specific tag
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

def commit_eou_record(uuid, responses):
  for qid in responses:
    modified = True
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
