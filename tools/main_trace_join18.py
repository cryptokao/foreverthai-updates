"""ONE bounded literal name/objectivesText join of qualified pinned Forever traces."""
import pathlib,subprocess,re,json,hashlib,collections
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parents[1];PIN='f0ad90875a6531368883904b0f157e7423c14f0b';PATH='src/corrections/Forever/traces/foreverQuestTraces.lua';EG='e0f8585914c134d9cb5d76756bd065b1e3e92ece';BASE='f32eb64fec3047a288d1963c3476f97e2c4858af'
def read(repo,ref,path):return subprocess.check_output(['git','-C',str(R/'work'/repo),'show',ref+':'+path])
raw=read('questiedb',PIN,PATH);assert hashlib.sha256(raw).hexdigest()=='c5537baa2968bd69ab06e19bf0754f217dd4105192c43bb0ddea21116da60d33';s=raw.decode();l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:
 payload=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']);l.execute(payload.decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
quoted=r'"(?:[^"\\]|\\.)*"';records=[];counts=collections.Counter();totals=collections.Counter();seen=set()
for m in re.finditer(r'^        \[(\d+)\] = \{(.*?)(?=^        \[|^    \})',s,re.M|re.S):
 q=int(m[1]);body=m[2];level=re.search(r'\[questKeys.questLevel\] = (\d+)',body);titlematch=re.search(r'\[questKeys.name\] = ('+quoted+')',body);title=l.eval(titlematch[1]) if titlematch else ''
 for key,f in [('name','title'),('objectivesText','objective')]:
  v=re.search(r'\[questKeys\.'+key+r'\] = ([^\n]+)',body)
  if not v:continue
  totals[key]+=1;value=v[1].strip().rstrip(',');strings=re.findall(quoted,value)
  # Only strings, commas, whitespace and list braces permitted. Evaluate individual quoted literals only.
  rest=re.sub(quoted,'',value);assert re.fullmatch(r'[\s{},]*',rest),(q,key,rest)
  lines=[l.eval(x) for x in strings];text='\n'.join(lines) if f=='objective' else lines[0];assert (q,f) not in seen;seen.add((q,f))
  entry=a.quests[q][f] if a.quests[q] else None
  if a.Translate(entry,text) is not None:status='already_supported_actualTranslate'
  elif classify_title(title,q) or classify_title(text,q):status='held_developer_or_disabled_marker'
  elif re.search(r'\$|\{[^}]*\}|<(?:name|player|race|class|unknown)[^>]*>',text,re.I):status='held_placeholder_or_privacy_marker'
  elif not text.strip():status='blank'
  else:status='unmatched_literal_for_targeted_EG'
  counts[status]+=1
  if status!='already_supported_actualTranslate':records.append(dict(quest_id=q,field=f,level=int(level[1]) if level else None,title=title,english=text,objective_lines=lines if f=='objective' else None,source_row=body,english_sha256=hashlib.sha256(text.encode()).hexdigest(),status=status,canonical_present=entry is not None))
assert totals=={'name':1492,'objectivesText':1394},totals
ids={v['quest_id'] for v in records if v['status']=='unmatched_literal_for_targeted_EG'};queries=collections.defaultdict(list);texts=collections.defaultdict(list);pins=[]
paths=subprocess.check_output(['git','-C',str(R/'work/eg'),'ls-tree','-r','--name-only',EG]).decode().splitlines()
for p in paths:
 if not re.match(r'data/wowf/[^/]+/(quests|texts)\.enUS.json$',p):continue
 b=read('eg',EG,p);doc=json.loads(b);found={int(q):v for q,v in doc.get('quests',{}).items() if int(q) in ids}
 if not found:continue
 build=doc['meta']['clientBuild'];pins.append(dict(path=p,build=build,sha256=hashlib.sha256(b).hexdigest()))
 for q,v in found.items():
  if '/quests.' in p:queries[q].append((tuple(map(int,build.split('.'))),p,v))
  elif v.get('objectives'):
   texts[q].append((tuple(map(int,build.split('.'))),p,v['objectives']))
def norm(x):return ' '.join(re.sub(r'\$b','\n',x,flags=re.I).split())
for v in records:
 if v['status']!='unmatched_literal_for_targeted_EG':continue
 q=v['quest_id'];f=v['field'];checks=[]
 if queries[q]:
  _,p,query=max(queries[q],key=lambda x:x[0]);source=query.get('title' if f=='title' else 'objectivesText');v['eg_query_level']=query.get('level')
  if source:checks.append(dict(path=p,kind='query',english=source,exact_normalized=norm(source)==norm(v['english'])))
 if f=='objective' and texts[q]:
  _,p,entries=max(texts[q],key=lambda x:x[0])
  for e in entries:
   if e.get('text') and not '$' in e['text']:checks.append(dict(path=p,kind='quest-window objectives',english=e['text'],exact_normalized=norm(e['text'])==norm(v['english'])))
 v['eg_comparison']=checks
 if any(not x['exact_normalized'] for x in checks):v['status']='held_text_conflict'
 else:v['status']='source_ready_literal'
 if v['level'] is None and v.get('eg_query_level') is not None:v['level']=v['eg_query_level'];v['level_source']='targeted EG own-ID query'
 if v['status']=='source_ready_literal':
  matches=[]
  for nq,quest in a.quests.items():
   for nf in ['title','objective','description','progress','completion']:
    thai=a.Translate(quest[nf],v['english'])
    if thai is not None:matches.append(dict(quest_id=int(nq),field=nf,thai=thai))
  v['reuse_matches']=matches
report=dict(scope='ONE qualified pinned Forevertrace name/objectivesText join only, against actual runtime after17. No Classic/old365/592/686, source polling or auxiliary audits.',source_commit=PIN,source_path=PATH,source_sha256=hashlib.sha256(raw).hexdigest(),baseline_source=BASE,fields_scanned=dict(totals),initial_counts=dict(counts),unmatched_literal_ids=sorted(ids),targeted_EG_commit=EG,targeted_EG_file_pins=pins,final_unmatched_counts=dict(collections.Counter(v['status'] for v in records)),records=sorted(records,key=lambda v:(v['level'] if v['level'] is not None else 999,v['quest_id'],v['field'])),limitations=['Unknown per-row trace build; producer provenance as17 does not prove current-enabled whole-game inventory.','Joined objective lines retain internal blank paragraphs. Only literals without roles/markers accepted; no new identity inference.'])
(R/'evidence/main18-trace-join.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['records','targeted_EG_file_pins']},indent=2));print('READY:')
for v in report['records']:
 if v['status']=='source_ready_literal':print(json.dumps(dict(quest_id=v['quest_id'],level=v['level'],field=v['field'],english=v['english'],reuse=v['reuse_matches'][:1]),ensure_ascii=False))
