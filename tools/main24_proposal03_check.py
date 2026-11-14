"""Final42 proposal-only checks; no integration or old/addon/font/game suites."""
import pathlib,json,hashlib,re,subprocess
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/main24-proposal03.json').read_text());checks=json.loads((R/'evidence/main24-proposal03-checks.json').read_text());sha=lambda v:hashlib.sha256(v).hexdigest();assert sha((R/'src/ForeverThai/Catalog.lua').read_bytes())==b['integrated_prior_Catalog_sha256'];assert len(b['fields'])==42;l=LuaRuntime(unpack_returned_tuples=True);a=l.table();cache={}
for n in ['Catalog','Match']:l.execute((R/f'src/ForeverThai/{n}.lua').read_text(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
for f in b['fields']:
 assert f['quest_id']!=2752 and '$' not in f['english'];assert sha(f['english'].encode())==f['english_sha256'] and sha(f['thai'].encode())==f['thai_sha256']
 for ref in f['source_refs']:
  path=ref['path']
  if path not in cache:cache[path]=json.loads(subprocess.check_output(['git','-C',str(R/'work/eg'),'show',f['source_pin']+':'+path]))
  v=cache[path]
  for k in ref['pointer'].split('/')[1:]:v=v[int(k)] if isinstance(v,list) else v[k]
  assert v==f['english']
 for old in f['exact_Thai_reuse_matches']:assert old['thai']==f['thai'] and a.Translate(a.quests[old['quest_id']][old['field']],f['english'])==f['thai']
by={(f['quest_id'],f['field']):f for f in b['fields']}
for o in checks['explicit_condition_oracles']:
 f=by[o['quest_id'],o['field']]
 for s in o['english_required']:assert s in f['english']
 for s in o['thai_required']:assert s in f['thai']
assert by[94302,'completion']['source_kind']=='captured_phase'
print(json.dumps(dict(status='proposal03_static_source_conditions_passed_pendingRoot',fields=42,new_Thai=15,exact_reuse=27,integration_from_proposal=False)))
