from app import db
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
