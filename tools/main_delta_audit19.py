"""Changed MAIN text fields in exactly two Questie files; no old whole-table matching scan."""
import pathlib,subprocess,re,json,hashlib,collections
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parents[1];OLD='f0ad90875a6531368883904b0f157e7423c14f0b';NEW='4dbb82440a27856f8dccf57094a5d792cdc7cc9b';BASE='2678500dd147c098c547aaec7506b0d2f3b6e57d';EG='e0f8585914c134d9cb5d76756bd065b1e3e92ece';l=LuaRuntime(unpack_returned_tuples=True);a=l.table();quoted=r'"(?:[^"\\]|\\.)*"'
def git(repo,ref,p):return subprocess.check_output(['git','-C',str(R/'work'/repo),'show',ref+':'+p])
for n in ['Catalog','Match']:l.execute(subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
def parse(ref,path):
 b=git('questiedb',ref,path);out={}
 for m in re.finditer(r'^        \[(\d+)\] = \{(.*?)(?=^        \[|^    \})',b.decode(),re.M|re.S):
  q=int(m[1]);body=m[2];lv=re.search(r'\[questKeys.questLevel\] = (\d+)',body)
  for key,f in [('name','title'),('objectivesText','objective')]:
   v=re.search(r'\[questKeys\.'+key+r'\] = (.*?)(?=\n\s*\[questKeys\.|\n        \},|$)',body,re.S)
   if not v:continue
   value=v[1];strings=re.findall(quoted,value);assert strings or f=='objective',(q,key)
   lines=[l.eval(x) for x in strings];text='\n'.join(lines) if f=='objective' else lines[0];out[q,f]=dict(quest_id=q,field=f,english=text,source_lines=lines,level=int(lv[1]) if lv else None,source_row=body,path=path,source_sha256=hashlib.sha256(b).hexdigest())
 return out
records=[];counts=collections.Counter();pins=[];removed=[]
for p in ['src/corrections/Forever/foreverQuestFixes.lua','src/corrections/Forever/traces/foreverQuestTraces.lua']:
 before=parse(OLD,p);after=parse(NEW,p);pins.append(dict(path=p,old_sha256=hashlib.sha256(git('questiedb',OLD,p)).hexdigest(),new_sha256=hashlib.sha256(git('questiedb',NEW,p)).hexdigest()))
 removed.extend(dict(quest_id=k[0],field=k[1],path=p,old_english_sha256=hashlib.sha256(v['english'].encode()).hexdigest(),action='Source metadata removed; retain reviewed runtime text, not new prose') for k,v in before.items() if k not in after)
 for k,v in after.items():
  if k in before and before[k]['english']==v['english']:continue
  q,f=k;text=v['english'];entry=a.quests[q][f] if a.quests[q] else None
  status='already_supported' if a.Translate(entry,text)!=None else 'unmatched_literal'
  if status!='already_supported':
   if classify_title(after.get((q,'title'),{}).get('english',''),q) or classify_title(text,q):status='held_developer_disabled'
   elif re.search(r'\$|\{[^}]*\}|<(?:name|player|race|class|unknown)[^>]*>',text,re.I):status='held_tokens_or_privacy'
   elif not text.strip():status='blank'
  v.update(status=status,canonical_present=entry is not None,old_english_sha256=hashlib.sha256(before[k]['english'].encode()).hexdigest() if k in before else None,english_sha256=hashlib.sha256(text.encode()).hexdigest());records.append(v);counts[status]+=1
# Read cached EG own-ID fields only for unmatched targets, with no fetch/re-audit.
ids={v['quest_id'] for v in records if v['status']=='unmatched_literal'};query={};qpins=[]
for build in ['70888','70938']:
 p='data/wowf/1.60.1.'+build+'/quests.enUS.json';b=git('eg',EG,p);doc=json.loads(b);qpins.append(dict(path=p,sha256=hashlib.sha256(b).hexdigest()));query.update({int(q):v for q,v in doc['quests'].items() if int(q) in ids})
for v in records:
 if v['status']!='unmatched_literal':continue
 q,f=v['quest_id'],v['field'];en=query.get(q,{}).get('title' if f=='title' else 'objectivesText');v['eg_corroboration']=dict(english=en,exact=' '.join(en.split())==' '.join(v['english'].split())) if en else None
 if en and ' '.join(en.split())!=' '.join(v['english'].split()):v['status']='held_text_conflict'
 elif '/traces/' in v['path'] or en:v['status']='ready_literal'
 else:v['status']='held_authored_without_direct_trace_or_query'
 if v['level'] is None:v['level']=query.get(q,{}).get('level')
 if v['status']=='ready_literal':
  found=[]
  for nq,e in a.quests.items():
   for nf in ['title','objective','description','progress','completion']:
    thai=a.Translate(e[nf],v['english'])
    if thai is not None:found.append(dict(quest_id=int(nq),field=nf,thai=thai))
  v['reuse_matches']=found
result=dict(scope='Only added/modified name/objectivesText field values in two-file delta, joining objective paragraphs; no old2886matching scan.',baseline_source=BASE,old_commit=OLD,new_commit=NEW,file_pins=pins,removed_source_field_slots=removed,delta_field_versions=len(records),initial_counts=dict(counts),final_counts=dict(collections.Counter(v['status'] for v in records)),eg_cached_commit=EG,eg_cached_pins=qpins,records=sorted(records,key=lambda v:(v['level'] if v['level'] is not None else 999,v['quest_id'],v['field'])))
(R/'evidence/main19-questie-delta.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in result.items() if k not in ['records','file_pins','eg_cached_pins']})
for v in result['records']:
 if v['status']=='ready_literal':print(json.dumps(dict(quest_id=v['quest_id'],field=v['field'],level=v['level'],english=v['english'],reuse=v['reuse_matches'][:1]),ensure_ascii=False))
