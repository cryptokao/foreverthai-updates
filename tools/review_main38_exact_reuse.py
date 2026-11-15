"""Find exact full literal source signatures for reuse, not a broad old-suite rerun."""
import pathlib,json,re,zipfile,hashlib,sys,collections,time
from lupa.lua51 import LuaRuntime,lua_type
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter()
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main36/build-0.473.0/ForeverThai-0.473.0-main36-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','MainQuest35.lua','MainQuest36.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
def sig(s):
 s=re.sub(r'\$[Bb]','\n',s).replace('\u00a0',' ');s=re.sub(r'[ \t\r\n\f\v]+',' ',s).strip();b=s.encode();assert len(b)==len(s) and '$' not in s and '|' not in s;x=y=0
 for c in b:x=(x*257+c)%2147483647;y=(y*131+c)%2147483629
 return f'{len(b)}:{x}:{y}'
index=collections.defaultdict(list)
def visit(entry,q,f,path):
 if lua_type(entry)!='table':return
 ss=[entry[1]] if isinstance(entry[1],str) else [v for _,v in entry[1].items()] if lua_type(entry[1])=='table' else []
 for s in ss:
  if isinstance(s,str) and re.fullmatch(r'\d+:\d+:\d+',s):index[s].append((q,f,path,entry))
 if entry.variants:
  for k,v in entry.variants.items():visit(v,q,f,path+f'.variants[{k}]')
 if entry.amount:visit(entry.amount,q,f,path+'.amount')
for q,quest in a.quests.items():
 for f in ['title','objective','description','progress','completion']:visit(quest[f],q,f,f)
doc=json.loads((R/'main38-reviewed-pairs.json').read_text(encoding='utf8'));out=[];seen=set()
for r in doc['fields']:
 q=r['quest_id'];f=r['field'];s=sig(r['english']);assert s==r['expected_dynamic_signature'];ui=re.sub(r'\$[Bb]','\n',r['english'])
 quest=a.quests[q];assert a.Translate(quest[f] if quest is not None else None,ui) is None,(q,f,'already supported own-ID')
 for oq,of,path,entry in index[s]:
  if of!=f:continue
  th=a.Translate(entry,ui)
  if isinstance(th,str) and th and '{' not in th:
   out.append(dict(quest_id=q,field=f,reuse_quest_id=oq,reuse_field=of,reuse_path=path,english_sha256=hashlib.sha256(r['english'].encode()).hexdigest(),thai=th,exact_full_literal_signature=s));break
report=dict(batch='MAIN38',baseline='0.473.0',status='REUSE_CANDIDATES_NEED_FULL_MEANING_REVIEW',matches=out,new_Thai_or_runtime_changes=0,elapsed_wall_seconds=time.perf_counter()-t)
(R/'main38-exact-reuse-candidates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(matches=len(out),wall=report['elapsed_wall_seconds']),ensure_ascii=False))
for row in out:
 key=(row['english_sha256'],row['thai'])
 if key not in seen:print(json.dumps(row,ensure_ascii=False));seen.add(key)
