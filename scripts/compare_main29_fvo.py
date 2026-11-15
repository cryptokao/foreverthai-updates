"""One new-input-only MAIN29 join against pinned baseline plus reviewed MAIN25 overlay."""
import json,pathlib,re,hashlib,collections,time
from lupa.lua51 import LuaRuntime,lua_type
R=pathlib.Path(__file__).resolve().parent;start=time.perf_counter();cpu=time.process_time()
read=lambda n:json.loads((R/n).read_text(encoding='utf-8'))
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil')
a=l.table()
import zipfile
base=R/'package-main28/build-0.470.0/ForeverThai-0.470.0-main28-COMBINED.zip';assert hashlib.sha256(base.read_bytes()).hexdigest()=='a9c854976d2efac55b4821492714b7cf93dae627fbb77309d6bc820610cfb5e6'
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
docs=read('main29-fvo-decoded-private.json');counts=collections.Counter();kinds=collections.Counter();phases=collections.Counter();seen={};private=[];pins=[]
for d in docs:
 h=d['doc'];assert h['locale']=='enUS' and h['build']=='70938'
 pins.append(dict(issue=d['issue'],url=d['url'],source_kind=d['source_kind'],comment_id=d.get('comment_id'),decoded_sha256=d['raw_sha256'],payload_container_sha256=d['body_sha256'],records=len(h['lines']),header={k:h.get(k) for k in ['v','addon','build','locale']}))
 for ix,v in enumerate(h['lines']):
  kinds[v.get('k')]+=1
  if v.get('k')!='quest':continue
  q,en,phase=v.get('q'),v.get('x'),v.get('e');assert isinstance(q,int) and q>0 and isinstance(en,str)
  phases[phase]+=1;f={'accept':'description','progress':'progress','complete':'completion'}.get(phase)
  pos=dict(issue=d['issue'],line_index=ix,source_kind=d['source_kind'],comment_id=d.get('comment_id'));key=q,f,en
  if key in seen:counts['duplicate_main_occurrences']+=1;seen[key]['source_positions'].append(pos);continue
  quest=a.quests[q];entry=quest[f] if quest is not None and f else None
  ui=re.sub(r'\$[Bb]','\n',en);tokens=sorted(set(re.findall(r'\$(?:[0-9]+[A-Za-z]+|[A-Za-z])',en))-{'$B','$b'})
  if f is None:status='held_unknown_phase'
  elif not en.strip():status='blank_no_prose'
  elif a.Translate(entry,en) is not None:status='supported_exact'
  elif a.Translate(entry,ui) is not None:status='supported_linebreak_markup'
  elif tokens or '$' in ui or re.search(r'<(?:name|player|race|class|unknown)[^>]*>|\{[^}]*\}',en,re.I):
   rendered=re.sub(r'\$[NnCcRr](?![A-Za-z0-9_])',lambda m:{'n':'CloudTester','c':'Druid','r':'Night Elf'}[m[0][1].lower()],ui)
   status='diagnostic_identity_substitution_supported_NOT_roleproof' if a.Translate(entry,rendered) is not None else 'held_unproven_roles_or_tokens'
  else:status='literal_unmatched_needs_full_source_privacy_review'
  counts[status]+=1
  row=dict(quest_id=q,field=f,source_phase=phase,status=status,source_positions=[pos],english_sha256=sha(en),english_bytes=len(en.encode()),runtime_quest_present=quest is not None,runtime_field_present=entry is not None,raw_tokens=tokens,current_enabled_usage='unproven',row_version='export header does not prove individual row version')
  seen[key]=row
  if status not in ['supported_exact','supported_linebreak_markup','diagnostic_identity_substitution_supported_NOT_roleproof','blank_no_prose']:private.append(dict(row,english=en,source_record=v))
audit=dict(batch='MAIN29',inputs='Only new issue3521;3520/3519/3518/3517 body SHA unchanged from prior MAIN26,not rejoined',source_exports=pins,actual_exports=len(docs),actual_records=sum(len(d['doc']['lines']) for d in docs),kind_occurrences=dict(kinds),phase_occurrences=dict(phases),counts=dict(counts),unique_main_forms=len(seen),rows=list(seen.values()),baseline='Actual immutable combined0.470.0 baseline,all additive modules loaded',new_thai_fields=0,runtime_changed=False,actual_invocations=1,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limits=['No whole-game denominator/current enabled inventory','Diagnostic substitutions are not source role proof','NonMAIN gossip/books not translated or fulltext audited','Raw exports and character context remain private','No local AI/game/font/build/test-suite operation'])
for name,data in [('main29-fvo-source-audit.json',audit),('main29-fvo-unmatched-private.json',private)]:
 (R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k not in ['source_exports','rows']},ensure_ascii=False))
print(json.dumps([dict(quest_id=v['quest_id'],field=v['field'],status=v['status'],bytes=v['english_bytes'],tokens=v['raw_tokens'],positions=v['source_positions']) for v in private],ensure_ascii=False))
