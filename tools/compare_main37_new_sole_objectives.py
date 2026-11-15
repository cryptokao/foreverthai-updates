"""Only new Nov15 delta sole-objective macros, not the closed old115 corpus."""
import pathlib,json,re,zipfile,hashlib,sys,time
from lupa.lua51 import LuaRuntime
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time()
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main36/build-0.473.0/ForeverThai-0.473.0-main36-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','MainQuest35.lua','MainQuest36.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
rows=json.loads((R/'main36-new-query-unmatched-private.json').read_text(encoding='utf8'));out=[];pending=[]
for r in rows:
 en=r['english'];obj=r['query_record'].get('objectives',[]);tokens=re.findall(r'\$[1-9][0-9]*oa',en)
 if r['status']!='held_unproven_macro_or_markup' or len(obj)!=1 or not tokens or set(tokens)!={'$1oa'}:continue
 amount=obj[0].get('amount');assert isinstance(amount,int) and 0<amount<1000
 ui=re.sub(r'\$[Bb]','\n',en).replace('$1oa',str(amount))
 if '$' in ui or '|' in ui:continue
 quest=a.quests[r['quest_id']];entry=quest[r['field']] if quest is not None else None;th=a.Translate(entry,ui)
 status='already_supported_ownID_numeric_UI' if th is not None else 'literal_resolved_pending_meaning_review'
 meta=dict(quest_id=r['quest_id'],field=r['field'],level=r['level'],title=r['title'],source_pointer=r['source_pointer'],raw_english_sha256=r['raw_source_sha256'],sole_amount=amount,objective_count=1,english_sha256=hashlib.sha256(ui.encode()).hexdigest(),status=status,current_enabled_inventory_proven=False)
 out.append(meta)
 if th is None:pending.append(dict(meta,english=ui,raw_english=en,query_record=r['query_record']))
report=dict(batch='MAIN37_SOURCE_ONLY',scope='Only new Nov15 delta sole-objective macros;NOT old115corpus rerun',primary_grammar_proof=dict(repository='Stein-N/WoW-Quest-Database',pin='bd4f36aba4894a68bb5e002fac78f010b29bd790',path='etl/questcache.py',blob='ab70d8f1aee3bc44538e6cbba9012855d9555bbc'),source_pin='0f202e892f1a15c8192c232351824eccb99efd8a',baseline='0.473.0',rows=out,qualified_fields=len(out),already_supported=sum(r['status'].startswith('already') for r in out),pending=len(pending),newThai=0,newaliases=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu,limits=['Only exactly ONE objective and $1oa with ownamount;no storageIndex or multipleobjective order inferred','Query is not enabled inventory;numericUIproof reused from MAIN31/32','No raw macro runtime bridge or frozen wildcard added'])
(R/'main37-new-sole-objective-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'main37-new-sole-objective-pending-private.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False));print(json.dumps([dict(q=x['quest_id'],f=x['field'],L=x['level'],english=x['english']) for x in pending],ensure_ascii=False))
