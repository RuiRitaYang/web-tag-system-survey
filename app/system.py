import pandas as pd
import numpy as np

from app.utils import *
from app.database import get_tags_by_rtn_id


def get_rtn_level_stt_table():
  site_root = os.path.realpath(os.path.dirname(__file__))
  filename = os.path.join(site_root, "static/data", "rtn_level_tag_strategy.csv")
  df = pd.read_csv(filename)
  df.replace(np.nan, '', regex=True, inplace=True)
  return df


def get_rtn_level_stt(rtn_sys_tag1, rtn_sys_tag2, rtn_higher_pri):
  df = get_rtn_level_stt_table()
  stt = df[(df['r1_sys'] == rtn_sys_tag1) &
           (df['r2_sys'] == rtn_sys_tag2) &
           (df['cus_pri'] == rtn_higher_pri)]['strategy']
  print('Getting raw strategy list: ' + str(stt.to_list()))
  stt = stt.to_list()[0]
  return stt

def get_strategy(rtn_sys_tag1, cmd1_tag1, cmd2_tag1, cus_pri1,
                 rtn_sys_tag2, cmd1_tag2, cmd2_tag2, cus_pri2):
  # System tags are routine-level
  if ((rtn_sys_tag1 and rtn_sys_tag2) or
      (not rtn_sys_tag1 and not rtn_sys_tag2)):
    stt = get_rtn_level_stt(
      rtn_sys_tag1,
      rtn_sys_tag2,
      'r2' if cus_pri2 >= cus_pri1 else 'r1')
    return stt
  else:
    return 'WORKING'

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
                     *get_tags_by_rtn_id(uuid, rtn_ids[1]))
  return get_outcome_info_by_stt(scn_info, stt)
