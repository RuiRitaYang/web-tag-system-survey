import json
import os

def get_all_scenarios_routines():
  site_root = os.path.realpath(os.path.dirname(__file__))
  scn_url = os.path.join(site_root, "static/data", "scenarios.json")
  rtn_url = os.path.join(site_root, "static/data", "routines.json")
  scenarios = json.load(open(scn_url))
  routines = json.load(open(rtn_url))
  return scenarios, routines
