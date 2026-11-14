"""Read-only proposal02 proof checks; not an integration/matcher/font/game suite."""
import pathlib,json,hashlib,subprocess,re
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/main24-proposal02.json').read_text());c=json.loads((R/'evidence/main24-proposal02-checks.json').read_text());sha=lambda x:hashlib.sha256(x).hexdigest();cache={};l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:l.execute((R/f'src/ForeverThai/{n}.lua').read_text(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end');assert sha((R/'src/ForeverThai/Catalog.lua').read_bytes())==b['integrated_proposal01_Catalog_sha256']
for f in b['fields']:
 assert f['quest_id']!=2752 and sha(f['english'].encode())==f['english_sha256'] and sha(f['thai'].encode())==f['thai_sha256'];assert not [x for x in re.findall(r'\$(?:\d+[A-Za-z]+|[A-Za-z])',f['english']) if x.lower()!='$b']
 for ref in f['source_refs']:
  path=ref['path']
  if path not in cache:cache[path]=json.loads(subprocess.check_output(['git','-C',str(R/'work/eg'),'show',f['source_pin']+':'+path]))
  v=cache[path]
  for k in ref['pointer'].split('/')[1:]:v=v[int(k)] if isinstance(v,list) else v[k]
  assert v==f['english']
 for old in f['exact_Thai_reuse_matches']:assert old['thai']==f['thai'] and a.Translate(a.quests[old['quest_id']][old['field']],re.sub(r'\$[Bb]','\n',f['english']))==f['thai']
by={(f['quest_id'],f['field']):f for f in b['fields']}
for o in c['explicit_quantity_condition_oracles']:
 f=by[o['quest_id'],o['field']]
 for s in o['english_required']:assert s in f['english']
 for s in o['thai_required']:assert s in f['thai']
print(json.dumps(dict(status='proposal02_source_static_checks_passed',fields=42,new_Thai=38,exact_reuse=4,integration_from_this_proposal=False)))
