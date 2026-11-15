"""Compare only the distinct MAIN38 56-form source-acquisition queue. No old corpus tests."""
import pathlib,json,re,zipfile,hashlib,sys,time,collections
from lupa.lua51 import LuaRuntime
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time()
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main38/build-0.474.0/ForeverThai-0.474.0-main38-PRIVATE-TEST.zip') as z:
 toc=z.read('ForeverThai/ForeverThai.toc').decode()
 for n in [s for s in toc.splitlines() if s=='Catalog.lua' or s.startswith('MainQuest')]+['Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
def norm(s):return re.sub(r'[ \t\r\n\f\v]+',' ',re.sub(r'\$[Bb]','\n',s).replace('\u00a0',' ')).strip()
def qualify(raw,rendered):
 parts=re.split(r'(\$[1-9][0-9]*oa)',norm(raw));tokens=[v for v in parts if re.fullmatch(r'\$[1-9][0-9]*oa',v)];pattern='^'+''.join('([0-9]+)' if v in tokens else re.escape(v) for v in parts)+'$';m=re.fullmatch(pattern,norm(rendered))
 if not m:return None
 values={}
 for token,value in zip(tokens,m.groups()):
  if token in values and values[token]!=value:return None
  values[token]=value
 return values
def literal_table_fields(s):
 assert s[0]=='{' and s[-1]=='}';depth=0;quote=False;escape=False;start=1;out=[]
 for i,c in enumerate(s):
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
   continue
  if c=='"':quote=True
  elif c=='{':depth+=1
  elif c=='}':
   depth-=1
   if depth==0:out.append(s[start:i].strip())
  elif c==',' and depth==1:out.append(s[start:i].strip());start=i+1
 assert depth==0 and not quote
 return out
inputdoc=json.loads((R/'main39-trace-queue-input-private.json').read_text(encoding='utf8'));base=json.loads((R/'main39-base-selected-private.json').read_text(encoding='utf8'));baseobj={}
for row in base:
 fs=literal_table_fields(row['literal']);value=fs[7]
 if value.startswith('{'):baseobj[row['quest_id']]=json.loads('['+value[1:-1]+']')
spoken=json.loads((R/'main39-spoken-description-selected-private.json').read_text(encoding='utf8'));out=[];pending=[]
for r in inputdoc['rows']:
 q=r['quest_id'];phase=r['field'];sources=[]
 if phase=='objective' and r['trace_same_phase_available']:sources.append(('QuestieTrace own-ID live API',' '.join(r['trace_objectives_text']),inputdoc['source_blob']))
 if phase=='objective' and q in baseobj:sources.append(('QuestieDB base own-ID objectiveText[8]',' '.join(baseobj[q]),'f4ea75ca02efc2333fd02dd955f42b68f4ffb14a'))
 if phase=='description':
  for row in spoken:
   if row['quest_id']==q:sources.append(('Spoken originalText accept',row['english'],'2408451f381a86b74f6e664c9e515b6757e3fa2e'))
 if not sources:
  out.append(dict(quest_id=q,field=phase,status='no_ownID_samephase_body_in_these_sources',source_English_sha256=r['english_sha256']));continue
 for source,en,blob in sources:
  captures=qualify(r['raw_source'],en);quest=a.quests[q];th=a.Translate(quest[phase] if quest is not None else None,re.sub(r'\$[Bb]','\n',en))
  status='already_supported_independent_full_UI_body' if th is not None else 'independent_body_unmatched_needs_review'
  if '$' in re.sub(r'\$[Bb]','',en):status='source_original_still_macro_or_identity_not_qualified'
  meta=dict(quest_id=q,field=phase,source=source,blob=blob,status=status,source_English_sha256=r['english_sha256'],independent_English_sha256=hashlib.sha256(en.encode()).hexdigest(),same_full_template_except_actual_captured_counts=captures is not None,captured_amounts=captures,current_enabled_inventory_proven=False)
  out.append(meta)
  if status=='independent_body_unmatched_needs_review':pending.append(dict(meta,english=en,raw_template=r['raw_source'],level=r['level'],title=r['title']))
report=dict(batch='MAIN39',scope='Only MAIN38 distinct56form queue;no old3902/39soleobjective/1414pages rerun',baseline='Actual0.474combinedZIP',trace_pin=inputdoc['source_pin'],trace_blob=inputdoc['source_blob'],base_blob='f4ea75ca02efc2333fd02dd955f42b68f4ffb14a',spoken_pin='ecbd06b379a4b30048c5139f10fa379430d840a0',counts=dict(collections.Counter(v['status'] for v in out)),rows=out,newThai=0,newaliases=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu,limits=['Independent numeric live API bodies need no objective-array order inference','No progress/description inferred from objective summaries','Spoken only originalText,never adapted text/voice identity substitutions','Query/trace presence not currentenabled whole-game inventory','Unmatched bodies are review candidates,NOTapproved translations'])
(R/'main39-independent-source-subset-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'main39-independent-source-pending-private.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False));print(json.dumps(pending,ensure_ascii=False))
