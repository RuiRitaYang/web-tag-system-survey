import json
import os
import random

from app.models import EaseOfUseForm, FstOutcomeForm, SndOutcomeForm


def get_random_scn_rtn_ids():
  scn_ids = random.sample(range(1, 5), 4)
  rtn_ids = get_rtn_ids_by_scn_ids(scn_ids)
  return scn_ids, rtn_ids

def get_all_scenarios_routines():
  site_root = os.path.realpath(os.path.dirname(__file__))
  scn_url = os.path.join(site_root, "static/data", "scenarios.json")
  rtn_url = os.path.join(site_root, "static/data", "routines.json")
  scenarios = json.load(open(scn_url))
  routines = json.load(open(rtn_url))
  return scenarios, routines

def get_all_routines():
  site_root = os.path.realpath(os.path.dirname(__file__))
  rtn_url = os.path.join(site_root, "static/data", "routines.json")
  routines = json.load(open(rtn_url))
  return routines

def get_routine_metadata():
  site_root = os.path.realpath(os.path.dirname(__file__))
  rtn_url = os.path.join(site_root, "static/data", "routine_metadata.json")
  return json.load(open(rtn_url))

# Return the routine information for all long routines in rtn_ids
def get_long_rtn_info(rtn_ids):
  routines = get_all_routines()
  long_rtn_ids = get_routine_metadata()['long_rtn_ids']
  long_ids = [rid for rid in rtn_ids if rid in long_rtn_ids]
  long_rtns = {}
  for rtn in routines:
    if rtn['rtn_id'] in long_ids:
      long_rtns[rtn['rtn_id']] = rtn
  return long_ids, long_rtns

def get_all_rtn_info(rtn_ids):
  routines = get_all_routines()
  rtn_info = {}
  for rtn in routines:
    if rtn['rtn_id'] in rtn_ids:
      rtn_info[rtn['rtn_id']] = rtn
  return rtn_ids, rtn_info

def get_scenario_by_id(sid):
  site_root = os.path.realpath(os.path.dirname(__file__))
  scn_url = os.path.join(site_root, "static/data", "scenarios.json")
  scenarios = json.load(open(scn_url))
  for scn in scenarios:
    if scn['scn_id'] == sid:
      return scn
  return {}

def get_scenarios_by_id(scn_ids):
  site_root = os.path.realpath(os.path.dirname(__file__))
  scn_url = os.path.join(site_root, "static/data", "scenarios.json")
  scenarios = json.load(open(scn_url))
  scn_info = []
  for scn in scenarios:
    if scn['scn_id'] in scn_ids:
      scn_info.append(scn)
  return scn_info

def get_rtn_ids_by_scn_ids(scn_ids):
  scn_info_all = get_scenarios_by_id(scn_ids)
  rtn_ids = set()
  for scn_info in scn_info_all:
    rtn_ids.update(scn_info['rtn_ids'])
  id_list = list(rtn_ids)
  random.shuffle(id_list)
  return id_list

def remove_cus_tag_in_string(all_tags: str, d_tag):
  all_tags = all_tags.split(',')
  all_tags.remove(d_tag)
  return ','.join(all_tags)

def get_image_full_path(filename, folder='img'):
  site_root = os.path.realpath(os.path.dirname(__file__))
  return os.path.join(site_root, "static", folder, filename)

def get_outcome_forms(scores):
  fst_oc_form = FstOutcomeForm()
  if scores[0]:
    fst_oc_form.oc1.data = scores[0]

  snd_oc_form = None
  if len(scores) > 1:
    snd_oc_form = SndOutcomeForm()
    if scores[1]:
      snd_oc_form.oc2.data = scores[1]
  return fst_oc_form, snd_oc_form

def internal_sys_name(name):
  matches = {'No Interruption': 'Uninterruptible', 'OK to Pause': 'Pausable'}
  if name not in matches:
    return name
  return matches[name]

def tag_display_name(name):
  matches = {'Uninterruptible': 'No Interruption',
             'Pausable': 'OK to Pause'}
  if name not in matches:
    return name
  return matches[name]

def get_eou_form(scores):
  form = EaseOfUseForm()
  for qid in range(9):
    if qid in scores:
      exec('form.q{0}.data = scores[{0}]'.format(qid))
  return form
