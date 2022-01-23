from app import db
from app.models import Users
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
