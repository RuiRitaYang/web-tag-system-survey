import numpy as np
import pandas as pd
from random import randint

from app.utils import *
from app.database import get_tags_by_rtn_id, get_scn_stt_score_from_db

debug = True
def get_rtn_level_stt_table():
  site_root = os.path.realpath(os.path.dirname(__file__))
  filename = os.path.join(site_root, "static/data", "rtn_level_tag_strategy.csv")
  df = pd.read_csv(filename)
  df.replace(np.nan, '', regex=True, inplace=True)
  return df

def get_cmd_level_stt_table():
  site_root = os.path.realpath(os.path.dirname(__file__))
  filename = os.path.join(site_root, "static/data", "cmd_level_tag_strategy.csv")
  df = pd.read_csv(filename)
  df.replace(np.nan, '', regex=True, inplace=True)
  return df


def get_default_stt_table():
  site_root = os.path.realpath(os.path.dirname(__file__))
  filename = os.path.join(site_root, "static/data", "scenario_default_stt.csv")
  df = pd.read_csv(filename)
  return df


def get_rtn_level_stt(rtn_sys_tag1, rtn_sys_tag2, rtn_higher_pri):
  df = get_rtn_level_stt_table()
  stt = df[(df['r1_sys'] == rtn_sys_tag1) &
           (df['r2_sys'] == rtn_sys_tag2) &
           (df['cus_pri'] == rtn_higher_pri)]['strategy']
  print('Getting RTN level raw strategy list: ' + str(stt.to_list()))
  stt = stt.to_list()[0]
  return stt


def get_cmd_level_stt(rtn_sys_tag1, cmd1_tag1, cmd2_tag1,
                      rtn_sys_tag2, cmd1_tag2, cmd2_tag2,
                      rtn_higher_pri, scn_id):
  df = get_cmd_level_stt_table()
  stt = df[(df['sid'] == scn_id) &
           (df['r1_sys'] == rtn_sys_tag1) &
           (df['r2_sys'] == rtn_sys_tag2) &
           (df['c11_sys'] == cmd1_tag1) &
           (df['c12_sys'] == cmd2_tag1) &
           (df['c21_sys'] == cmd1_tag2) &
           (df['c22_sys'] == cmd2_tag2) &
           (df['cus_pri'] == rtn_higher_pri)]['strategy']
  print('Getting CMD raw strategy list: ' + str(stt.to_list()))
  if stt.empty:
    df_default = get_default_stt_table()
    stt = df_default[df_default['sid'] == scn_id]['strategy']
    print("  Empty strategy, so using the default one.")
    print("  Scn ", scn_id, " flags: ",
          " rtn1: sys-", rtn_sys_tag1, ' cmd1-', cmd1_tag1, ' cmd2-', cmd2_tag1,
          " rtn2: sys-", rtn_sys_tag2, ' cmd1-', cmd1_tag2, ' cmd2-', cmd2_tag2,
          ' cur-priority-', rtn_higher_pri)
  stt = stt.to_list()[0]
  return stt

def get_strategy(rtn_sys_tag1, cmd1_tag1, cmd2_tag1, cus_pri1,
                 rtn_sys_tag2, cmd1_tag2, cmd2_tag2, cus_pri2,
                 scn_id):
  # System tags are routine-level
  if debug:
    print('Scn id: {} rtn1 sys tags: {}, {}, {}\n      rtn2 sys tags '
          '{}, {}, {}, higher cus: {}'
          .format(scn_id, rtn_sys_tag1, cmd1_tag1, cmd2_tag1,
                  rtn_sys_tag2, cmd1_tag2, cmd2_tag2,
                  'r2' if cus_pri2 >= cus_pri1 else 'r1'))
  any_tag = (rtn_sys_tag1 or cmd1_tag1 or cmd2_tag1 or
             rtn_sys_tag2 or cmd1_tag2 or cmd2_tag2)
  if ((rtn_sys_tag1 and rtn_sys_tag2) or
      (rtn_sys_tag1 and not cmd1_tag2 and not cmd2_tag2) or
      (rtn_sys_tag2 and not cmd1_tag1 and not cmd2_tag1) or
      (not any_tag)):
    stt = get_rtn_level_stt(
      rtn_sys_tag1,
      rtn_sys_tag2,
      'r2' if cus_pri2 >= cus_pri1 else 'r1')
    return stt
  else:
    return get_cmd_level_stt(
      rtn_sys_tag1, cmd1_tag1, cmd2_tag1,
      rtn_sys_tag2, cmd1_tag2, cmd2_tag2,
      'r2' if cus_pri2 >= cus_pri1 else 'r1',
      scn_id)

def get_outcome_info_by_stt(scn_info, stt):
  for oc in scn_info['system_outcomes']:
    if stt in oc['strategy']:
      # Set complete address of image
      # oc['photo'] = get_image_full_path(oc['photo'])
      return oc
  return {'outcome_id': 100,
          'strategy': ['TESTING'],
          'description': 'testing',
          'photo': 'testing photo'}


def get_tag_outcome_by_scn_info(scn_info, uuid):
  rtn_ids = scn_info["rtn_ids"]
  stt = get_strategy(*get_tags_by_rtn_id(uuid, rtn_ids[0]),
                     *get_tags_by_rtn_id(uuid, rtn_ids[1]),
                     scn_info['scn_id'])
  return get_outcome_info_by_stt(scn_info, stt), stt

def get_user_scn_outcome(uuid, scn_id: int, scn_info):
  # TODO: add randomization for outcome
  outcome, stt = get_tag_outcome_by_scn_info(scn_info, uuid)
  outcomes = [outcome]
  scores = [get_scn_stt_score_from_db(uuid, scn_id, stt)]
  strategies = [stt]
  ex_outcome = get_outcome_info_by_stt(scn_info, 'EX')

  if outcomes[0]['outcome_id'] != ex_outcome['outcome_id']:
    index = randint(0, 1)
    outcomes.insert(index, ex_outcome)
    scores.insert(index, get_scn_stt_score_from_db(uuid, scn_id, 'EX'))
    strategies.insert(index, 'EX')
  return outcomes, scores, strategies
