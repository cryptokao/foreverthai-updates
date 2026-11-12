"""Separate ID union audit. Never restrict source IDs to the existing Catalog.
Metadata and query-cache presence do not establish current Forever playability.
"""
import collections,csv,hashlib,json,pathlib,re,subprocess
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];EG=ROOT/'work/eg';VO=ROOT/'work/forever-vo';QD=ROOT/'work/questiedb';OUT=ROOT/'evidence';sha=lambda b:hashlib.sha256(b).hexdigest()
commit=lambda p,ref='HEAD':subprocess.check_output(['git','-C',str(p),'rev-parse',ref],text=True).strip()
pins={'EG':commit(EG),'VO':commit(VO),'QuestieDB':commit(QD,'origin/master')};sources=collections.defaultdict(list);manifests={};sets=collections.defaultdict(set);titles=collections.defaultdict(set);levels={};prose=collections.defaultdict(list);current_captured=set();flags=collections.defaultdict(set);file_hashes={}
lua=LuaRuntime();addon=lua.table();lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')((ROOT/'src/ForeverThai/Catalog.lua').read_text(),addon);runtime={int(q) for q,_ in addon.quests.items()}
def add(q,family,path,build,fields,raw,content=None):
 q=int(q);sets[family].add(q);base_path=re.sub(r':\d+$','',path.split('#',1)[0]);hash_key=(family,base_path)
 if hash_key not in file_hashes:file_hashes[hash_key]=sha(raw)
 ref=dict(family=family,repository={'EG_query':'JIVESCORP/eg-link-output-wowf','EG_texts':'JIVESCORP/eg-link-output-wowf','Forever_VO':'quinn-dougherty/forever-vo','QuestieDB':'Questie/QuestieDB'}[family],commit=pins['EG' if family.startswith('EG') else 'VO' if family=='Forever_VO' else 'QuestieDB'],path=path,build=build,actual_fields=sorted(set(fields)),file_sha256=file_hashes[hash_key]);sources[q].append(ref);manifests[family+'/'+base_path]=ref['file_sha256']
 for f,text in (content or {}).items():
  texts=text if isinstance(text,list) else [text]
  for t in texts:
   if not isinstance(t,str) or not t.strip():continue
   if f=='title':titles[q].add(t)
   elif f in ['description','objective','progress','completion']:prose[q].append(dict(field=f,english=t,source=ref))
qp=EG/'data/wowf/1.60.1.70888/quests.enUS.json';raw=qp.read_bytes();queries=json.loads(raw)['quests']
for q,v in queries.items():
 fields={f:v[k] for f,k in [('title','title'),('objective','objectivesText'),('description','description')] if v.get(k)};add(q,'EG_query',str(qp.relative_to(EG)),'1.60.1.70888',list(fields),raw,fields);levels[int(q)]=v.get('level');
 if v.get('flags',0)&512:flags[int(q)].add('query_flag512_review_required')
for p in sorted((EG/'data/wowf').glob('*/texts.enUS.json')):
 raw=p.read_bytes();d=json.loads(raw)
 for q,phases in d.get('quests',{}).items():
  fields={};has_live=False
  for phase,entries in phases.items():
   f={'accept':'description','complete':'completion','progress':'progress','objectives':'objective'}.get(phase)
   if not f:continue
   fields[f]=[v['text'] for v in entries]
   if phase in ['accept','complete','progress'] and any(not v.get('template') for v in entries):has_live=True
  add(q,'EG_texts',str(p.relative_to(EG)),p.parent.name,list(fields),raw,fields)
  if has_live and p.parent.name in ['1.60.1.70862','1.60.1.70888']:current_captured.add(int(q))
p=VO/'tools/data/capture.json';raw=p.read_bytes()
for k,v in json.loads(raw)['quests'].items():
 f={'accept':'description','complete':'completion','progress':'progress'}.get(v['event']);fields={'title':v.get('title','')}
 if f:fields[f]=v['text']
 add(v['questID'],'Forever_VO','tools/data/capture.json#'+k,str(v.get('build','')),list(fields),raw,fields)
 if str(v.get('build')) in ['70862','70888']:current_captured.add(int(v['questID']))
for p in sorted((ROOT/'work').glob('issue-*-decoded.json')):
 raw=p.read_bytes();d=json.loads(raw)
 for i,v in enumerate(d['lines']):
  if v.get('k')!='quest' or not v.get('q'):continue
  f={'accept':'description','complete':'completion','progress':'progress'}.get(v.get('e'));fields={'title':v.get('t','')}
  if f:fields[f]=v['x']
  add(v['q'],'Forever_VO',p.stem+':'+str(i),str(d.get('build','')),list(fields),raw,fields)
  if f and str(d.get('build')) in ['70862','70888']:current_captured.add(int(v['q']))
def gitbytes(path):return subprocess.check_output(['git','-C',str(QD),'show',pins['QuestieDB']+':'+path])
p='data/Forever/foreverQuestDB.lua';raw=gitbytes(p);l=LuaRuntime();l.execute('QuestieDB={};QuestieLoader={ImportModule=function()return QuestieDB end}');l.execute(raw.decode());data=l.execute(l.globals().QuestieDB.questData)
for q,v in data.items():
 fields={'title':v[1]}
 if v[8]:fields['objective']=[s for _,s in v[8].items() if isinstance(s,str)]
 add(q,'QuestieDB',p,None,list(fields),raw,fields);levels.setdefault(int(q),v[5])
# Authored/generated/trace corrections all contain top-level quest table entries.
# Scan only eight-space [ID] blocks; nested item/NPC/coordinate keys are excluded.
def block(text,start):
 depth=0;i=start;quote=None
 while i<len(text):
  c=text[i]
  if quote:
   if c=='\\':i+=2;continue
   if c==quote:quote=None
  elif text.startswith('--',i):
   n=text.find('\n',i);i=len(text) if n<0 else n;continue
  elif c in ['"',"'"]:quote=c
  elif c=='{':depth+=1
  elif c=='}':
   depth-=1
   if depth==0:return text[start:i+1]
  i+=1
 raise AssertionError('Unbalanced metadata block')
paths=subprocess.check_output(['git','-C',str(QD),'ls-tree','-r','--name-only',pins['QuestieDB']],text=True).splitlines()
metadata=[p for p in paths if p.startswith('src/corrections/Forever/') and re.search(r'[Qq]uest.*\.lua$',p)]
for p in metadata:
 raw=gitbytes(p);text=raw.decode();manifests['QuestieDB/'+p]=sha(raw)
 for m in re.finditer(r'^        \[(\d+)\] = \{',text,re.M):
  q=int(m[1]);b=block(text,m.end()-1);fields={};names=re.findall(r'\[questKeys\.(\w+)\]\s*=',b)
  for key,f in [('name','title'),('objectivesText','objective')]:
   v=re.search(r'\[questKeys\.'+key+r'\]\s*=\s*([^\r\n]+)',b)
   if v:
    values=[]
    for quoted in re.findall(r'"(?:\\.|[^"\\])*"',v[1]):values.append(l.eval(quoted))
    if values:fields[f]=values
  add(q,'QuestieDB',p+':'+str(text.count('\n',0,m.start())+1),None,list(fields)+['metadata:'+n for n in names],raw,fields)
  level=re.search(r'\[questKeys.questLevel\]\s*=\s*(\d+)',b)
  if level:levels.setdefault(q,int(level[1]))
  if re.search(r'--[^\n]*unverified',b,re.I):flags[q].add('Questie_metadata_explicitly_unverified')
# Cross-flavor presence is diagnostic only. It does not automatically reject a
# quest that Forever may reuse. Foreign flavor IDs do not enter the union.
foreign=collections.defaultdict(set)
for p in paths:
 if not re.fullmatch(r'data/(Classic|TBC|Wotlk|Cata|MoP)/\w*[Qq]uestDB\.lua',p):continue
 for q in re.findall(rb'^\[(\d+)\] =',gitbytes(p),re.M):foreign[int(q)].add(p.split('/')[1])
union=set().union(*sets.values());outside=union-runtime;title_ids=collections.defaultdict(set)
for q,ts in titles.items():
 for t in ts:title_ids[' '.join(t.lower().split())].add(q)
rows=[];outside_rows=[]
for q in sorted(union):
 ts=sorted(titles[q]);joined=' '.join(ts);test=bool(re.search(r'(?i)unused|never used|<nyi|<txt|\[dnt\]|\[ph\]|test|chow|reuse|deprecated',joined));disabled=bool(re.search(r'(?i)disabled|do not use|obsolete',joined));actual=[v for v in prose[q] if v['english'].strip() not in ['Log','Description'] and not v['english'].startswith('[PH]')];families=sorted({v['family'] for v in sources[q]});collisions=sorted({i for t in ts for i in title_ids[' '.join(t.lower().split())] if i!=q});other=sorted(foreign[q]);seen_trace=any('/traces/' in v['path'] for v in sources[q] if v['family']=='QuestieDB')
 if test:triage='hold_test_or_development_label'
 elif disabled:triage='hold_disabled_or_obsolete'
 elif q in current_captured and actual:triage='current_captured_prose_candidate' if q in outside else 'in_runtime'
 elif q in outside and not actual:triage='hold_metadata_or_title_only'
 elif q in outside and other and 'Classic' not in other and not seen_trace:triage='hold_other_expansion_or_legacy_cache_uncertain'
 elif q in outside:triage='hold_current_usage_unconfirmed'
 else:triage='in_runtime'
 row=dict(quest_id=q,in_runtime=q in runtime,level=levels.get(q),titles=ts,source_families=families,actual_fields=sorted({f for v in sources[q] for f in v['actual_fields']}),source_ref_count=len(sources[q]),has_real_prose=bool(actual),observed_current_70862_70888_capture=q in current_captured,questie_trace_metadata_present=seen_trace,other_flavor_metadata=other,title_collision_ids=collisions,flags=sorted(flags[q]),triage=triage,current_playability_proven=False)
 rows.append(row)
 if q in outside:outside_rows.append({**row,'source_refs':sources[q],'available_prose':actual})
summary=dict(scope='Source-ID union discovery, separate from runtime five-field inventory. Not an authoritative current playable-game denominator.',source_pins=pins,source_set_id_counts={k:len(v) for k,v in sets.items()},runtime_ids=len(runtime),union_source_ids=len(union),source_ids_outside_runtime=len(outside),runtime_ids_not_in_source_union=len(runtime-union),outside_triage=dict(collections.Counter(v['triage'] for v in outside_rows)),outside_ids_by_family={k:len(v-runtime) for k,v in sets.items()},outside_current_capture_ids=sorted(outside&current_captured),source_manifest=manifests,questie_metadata_files=metadata,discovery_invariants=dict(no_runtime_filter_in_add=True,union_equals_all_four_source_sets=True,outside_equals_union_minus_runtime=True,foreign_flavors_used_only_for_diagnostics=True),uncertainty='Queries may contain legacy/test/SoD caches. Repeated titles are collisions, not duplicate proof. Questie metadata/trace corrections alone do not establish current prose/phase availability.')
assert union==set(sources) and outside==set(v['quest_id'] for v in outside_rows)
(OUT/'source-id-union-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(OUT/'source-ids-outside-catalog.json').write_text(json.dumps(outside_rows,ensure_ascii=False,indent=2)+'\n')
with (OUT/'source-id-union.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader()
 for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in row.items()})
print(json.dumps({k:v for k,v in summary.items() if k not in ['source_manifest','questie_metadata_files']},indent=2))
