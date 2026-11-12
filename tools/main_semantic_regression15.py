"""Affected main15 data checks only. No font build or unrelated suite rerun."""
import hashlib,json,pathlib,subprocess
from lupa.lua51 import LuaRuntime,lua_type
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';TREE='f85a68ca9c2ade231310620e693765cd99eebfc1'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(b):return hashlib.sha256(b).hexdigest()
prior=git('show',TREE+':Catalog.lua');current=(RUN/'Catalog.lua').read_bytes();assert current.startswith(prior)
lua=LuaRuntime(unpack_returned_tuples=True);load=lua.eval('function(s,a) assert(loadstring(s))("ForeverThai",a) end');base=lua.table();addon=lua.table()
for obj,cat in [(base,prior),(addon,current)]:
 load(cat.decode(),obj)
fields=json.loads((ROOT/'evidence/main-semantic-15.json').read_text())['fields'];allowed={(r['quest_id'],r['field']) for r in fields};values=0
# All old leaf values and all old keys survive; only one appended variant at each four exact fields.
def equal(a,b,path=()):
 global values
 if lua_type(a)=='table':
  for k,v in a.items():equal(v,b[k],path+(k,))
  for k,v in b.items():
   if a[k] is None:assert len(path)==3 and path[0]=='quests' and (path[1],path[2]) in allowed and k=='variants',path+(k,)
 else:assert a==b,path;values+=1
equal(base,addon)
for obj in [base,addon]:load((RUN/'Match.lua').read_text(),obj)
for q,f in allowed:assert len(addon.quests[q][f].variants)==1
unchanged=0
for line in git('ls-tree','-r',TREE).decode().splitlines():
 metadata,path=line.split('\t');blob=metadata.split()[2]
 if path=='Catalog.lua':continue
 assert (RUN/path).read_bytes()==git('cat-file','blob',blob),path;unchanged+=1
positive=negative=0
for r in json.loads((ROOT/'tests/main-semantic-cases15.json').read_text())['cases']:
 lua.globals().UnitName=lambda *_:r['name'];lua.globals().UnitClass=lambda *_:(r['class_name'],r['class_id']);lua.globals().UnitRace=lambda *_:r['race']
 entry=addon.quests[r['quest_id']][r['field']];variant=entry.variants[1]
 assert base.Translate(base.quests[r['quest_id']][r['field']],r['english']) is None
 assert addon.Translate(entry,r['english'])==r['expected'],(r['quest_id'],addon.Translate(entry,r['english']),r['expected']);positive+=1
 mutations=[r['english']+' Extra source words.',r['english'].replace('Excellent work','Poor work').replace('Another set','One fewer set').replace('heroes like you','villains like you').replace('many gnomes','many trolls')]
 if '{name}' in next(f['thai'] for f in fields if f['quest_id']==r['quest_id']):mutations.append(r['english'].replace(r['name'],'UnrelatedPlayer'))
 if r['quest_id']==98574:mutations.append(r['english'].replace('another '+r['race'],'another Orc'))
 elif r['quest_id'] in [8384,8391]:mutations.append(r['english'].replace(r['class_name'],'Warrior'))
 for bad in mutations:
  assert bad!=r['english'];assert addon.Translate(variant,bad) is None,(r['quest_id'],bad);negative+=1
report=dict(status='passed',baseline_runtime_tree=TREE,catalog_sha256=sha(current),old_catalog_byte_prefix_preserved=True,old_data_values_preserved=values,unchanged_runtime_files=unchanged,unique_source_cases=6,independent_rendered_oracles=positive,negative_executions=negative,new_or_expanded_thai_fields=2,unique_new_or_expanded_thai_bodies=2,reused_existing_thai_fields=4,font='not rebuilt; root Thai review pending; candidate13 remains delivered package',scope='Data-only targeted Lua5.1 matcher checks against static independent oracles and all old Catalog values/runtime bytes; not NPC686/party/Skills/full suite or in-game test.')
(ROOT/'evidence/main-semantic-regression15.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
