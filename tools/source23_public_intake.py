"""Bounded11 historical cache rows + target-only metadata/title hashes for27 local envelopes.
No runtime writes, generic source scans, role inference, amount substitution or third-party parser execution.
"""
import pathlib,json,re,hashlib,subprocess,collections
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];W=R/'work/source23';sha=lambda b:hashlib.sha256(b).hexdigest();Q='4dbb82440a27856f8dccf57094a5d792cdc7cc9b';E='e0f8585914c134d9cb5d76756bd065b1e3e92ece';P='8153cf7536636208c91bc88e34082d1dc1bdeac0';l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:l.execute((R/f'src/ForeverThai/{n}.lua').read_text(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
assert sha((R/'src/ForeverThai/Catalog.lua').read_bytes())=='43ec92f88113114aef4918dcbe10c0bb89b7f222d6658dc5183c08c706f94f50'
meta=json.loads((R/'source_inputs/source23-local-cache-envelope-metadata.json').read_text());doc=json.loads((W/'enUS.json').read_text());ids={v['id'] for v in meta['records']};public_ids={int(q) for q in doc['quests']};targets=ids|public_ids;known=collections.defaultdict(list);levels={};pins=[];queries={}
def readrepo(repo,ref,path):
 b=subprocess.check_output(['git','-C',str(R/'work'/repo),'show',ref+':'+path]);pins.append(dict(repository=repo,commit=ref,path=path,sha256=sha(b)));return b
# Literal token splitter for selected generated-row metadata, never evaluate whole Lua source.
def split_top(s):
 out=[];start=0;depth=0;quoted=False;escape=False
 for i,c in enumerate(s):
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='{':depth+=1
  elif c=='}':depth-=1
  elif c==',' and depth==0:out.append(s[start:i]);start=i+1
 out.append(s[start:]);return out
b=readrepo('questiedb',Q,'data/Forever/foreverQuestDB.lua').decode()
for m in re.finditer(r'^\s*\[(\d+)\] = \{(.*)\},?$',b,re.M):
 q=int(m[1])
 if q not in targets:continue
 parts=split_top(m[2]);token=parts[0].strip();assert re.fullmatch(r'"(?:[^"\\]|\\.)*"',token);name=l.eval(token);known[q].append(dict(title=name,repository='Questie/QuestieDB',commit=Q,path='data/Forever/foreverQuestDB.lua'));levels[q]=int(parts[4]) if parts[4].strip().lstrip('-').isdigit() else None
quoted=r'"(?:[^"\\]|\\.)*"'
for path in ['src/corrections/Forever/foreverQuestFixes.lua','src/corrections/Forever/traces/foreverQuestTraces.lua']:
 b=readrepo('questiedb',Q,path).decode()
 for m in re.finditer(r'^        \[(\d+)\] = \{(.*?)(?=^        \[|^    \})',b,re.M|re.S):
  q=int(m[1])
  if q not in targets:continue
  title=re.search(r'\[questKeys.name\] = ('+quoted+')',m[2]);level=re.search(r'\[questKeys.questLevel\] = (-?\d+)',m[2])
  if title:known[q].append(dict(title=l.eval(title[1]),repository='Questie/QuestieDB',commit=Q,path=path))
  if level:levels[q]=int(level[1])
for build in ['70888','70938']:
 path=f'data/wowf/1.60.1.{build}/quests.enUS.json';data=json.loads(readrepo('eg',E,path))['quests']
 for q in targets:
  v=data.get(str(q))
  if not v:continue
  queries[q]=v
  if v.get('title'):known[q].append(dict(title=v['title'],repository='JIVESCORP/eg-link-output-wowf',commit=E,path=path))
  if v.get('level') is not None:levels[q]=v['level']
rows=[];counts=collections.Counter()
for qstr,v in doc['quests'].items():
 q=int(qstr);assert v['build']==70124
 for key,field in [('name','title'),('objectivesText','objective'),('details','description')]:
  s=v.get(key)
  if not s:continue
  if isinstance(s,list):s='\n'.join(s)
  # Source spelling $B is linebreak markup only; identity/counter macros stay raw.
  text=re.sub(r'\$B','\n',s,flags=re.I);entry=a.quests[q][field] if a.quests[q] else None;result=a.Translate(entry,text);tokens=sorted(set(re.findall(r'\$[^\s.,!?]*',text)));current=queries.get(q,{}).get({'title':'title','objective':'objectivesText','description':'description'}[field]);same=bool(current and ' '.join(current.split())==' '.join(text.split()))
  if result is not None:status='already_supported_exact'
  elif tokens:status='held_raw_macro_roles_unconfirmed'
  elif same:status='ready_current_ownID_literal'
  else:status='held_historical_source_without_current_exact_field_corroboration'
  counts[status]+=1;rows.append(dict(quest_id=q,field=field,source_key=key,build=70124,english_sha256=sha(s.encode()),runtime_slot_present=entry is not None,status=status,level=levels.get(q),current_ownID_metadata_present=bool(known[q]),current_ownID_exact_field_corroboration=same,raw_macros=tokens,canonical_support_is_not_current_enabled_proof=True))
  if status=='ready_current_ownID_literal':rows[-1]['english']=text
expected={}
for q in sorted(ids):
 sources=[dict(title_sha256=sha(v['title'].encode()),repository=v['repository'],commit=v['commit'],path=v['path']) for v in known[q]];hashes=sorted({v['title_sha256'] for v in sources});markers=any(re.search(r'\[(?:DNT|UNUSED|PH|NYI)\]|^TEST QUEST$',v['title'],re.I) for v in known[q]);expected[str(q)]=dict(title_sha256=hashes[0] if len(hashes)==1 and not markers else None,status='confirmed_unique_metadata_title' if len(hashes)==1 and not markers else 'held_conflicting_or_missing_or_developer_title',source_title_hashes=sources)
out=dict(schema=1,source23_file_sha256=meta['sha256'],expected_build=70938,expected_magic='TSQW',expected_locale='enUS',max_input_bytes=1048576,expected_records=meta['records'],expected_titles=expected,metadata_pins=pins,scope='Only27ownIDs; hashes are known title binding, not current enabled/whole inventory proof. Exact UTF8 raw title hash; no case/role normalization.')
(R/'source_inputs/source23-expected-title-hashes.json').write_text(json.dumps(out,indent=2)+'\n')
sourcepins=[]
for name,path in [('questcache.py','etl/questcache.py'),('import_questcache.py','etl/import_questcache.py'),('enUS.json','etl/corrections/questcache/forever/enUS.json'),('README.md','README.md'),('LICENSE','LICENSE')]:
 raw=(W/name).read_bytes();sourcepins.append(dict(repository='Stein-N/WoW-Quest-Database',commit=P,path=path,bytes=len(raw),sha256=sha(raw),git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()))
report=dict(scope='Only11public historicalbuild70124 records; actual current own-ID Catalog/Match, current metadata targets only. No full oldsource scan.',source_pins=sourcepins,repository_license='GPL-3.0 per pinned README/LICENSE; not treated as a blanket grant for underlying Blizzard text.',source_field_mapping=dict(name='title',objectivesText='objective from logDescription',details='description from questDescription',endText='completionLog: NOT reward/completion dialogue, held/unmapped'),untrusted_transformations='Upstream importer uses fill_amounts; no counter-role proof inferred. Raw $c not expanded or typed by this audit. Upstream heuristic last-plausible fallback not adopted.',records=11,fields=len(rows),counts=dict(counts),ready_literal_fields=sum(v['status']=='ready_current_ownID_literal' for v in rows),new_thai_fields=0,runtime_changed=False,current_enabled_inventory=False,expected_title_ids=27,expected_title_qualified=sum(v['title_sha256'] is not None for v in expected.values()),expected_title_held_ids=[int(q) for q,v in expected.items() if v['title_sha256'] is None],metadata_pins=pins,rows=sorted(rows,key=lambda v:(v['level'] if v['level'] is not None else 999,v['quest_id'],v['field'])))
(R/'evidence/source23-public11-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['source_pins','metadata_pins','rows']},indent=2));print(json.dumps([v for v in report['rows'] if v['status']!='already_supported_exact'],indent=2))
