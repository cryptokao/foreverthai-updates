"""All objective quantities equal => no objective-order inference needed; only this new queue."""
import pathlib,json,re,zipfile,hashlib,sys,time
from lupa.lua51 import LuaRuntime
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main38/build-0.474.0/ForeverThai-0.474.0-main38-PRIVATE-TEST.zip') as z:
 for n in [s for s in z.read('ForeverThai/ForeverThai.toc').decode().splitlines() if s=='Catalog.lua' or s.startswith('MainQuest')]+['Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
queue=json.loads((R/'main38-next-multiobjective-source-queue.json').read_text(encoding='utf8'))['forms'];source=json.loads((R/'main36-new-query-unmatched-private.json').read_text(encoding='utf8'));out=[];pending=[]
for row in queue:
 if row['field']!='description':continue
 src=next(x for x in source if x['quest_id']==row['quest_id'] and x['field']==row['field']);objs=src['query_record'].get('objectives',[]);amounts=[o.get('amount') for o in objs];indices=[int(i) for i in re.findall(r'\$([1-9][0-9]*)oa',row['raw_source'])]
 if not amounts or len(set(amounts))!=1 or not all(isinstance(a,int) and 0<a<1000 for a in amounts) or not indices or not all(1<=i<=len(objs) for i in indices):continue
 en=re.sub(r'\$[1-9][0-9]*oa',str(amounts[0]),row['raw_source']);assert '$' not in en;quest=a.quests[row['quest_id']];th=a.Translate(quest.description if quest is not None else None,en)
 meta=dict(quest_id=row['quest_id'],field='description',source_sha256=row['english_sha256'],objective_amounts=amounts,tokens=indices,any_permutation_has_same_quantity=True,rendered_English_sha256=hashlib.sha256(en.encode()).hexdigest(),status='already_supported_uniform_quantity_UI' if th is not None else 'qualified_pending_meaning_review',current_enabled_inventory_proven=False)
 out.append(meta)
 if th is None:pending.append(dict(meta,english=en,title=row['title'],level=row['level']))
report=dict(batch='MAIN39',scope='Only new34uniform-count description fields,NOT old115/39sole rerun',primary_format_pin='bd4f36aba4894a68bb5e002fac78f010b29bd790',primary_format_blob='ab70d8f1aee3bc44538e6cbba9012855d9555bbc',primary_lines=[141,142,143,144,145,146],primary_independent_sample='https://www.wowhead.com/forever/quest=94004/craftsmans-writ-elixir-of-ogres-strength description/mainbody29 confirms literal1',rows=out,qualified=len(out),already_supported=sum(x['status'].startswith('already') for x in out),pending=len(pending),newThai=0,newaliases=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-t,limits=['Every actual objective amount same positiveinteger;all ordinal tokens within objectivecount;ANYarraypermutation yields sameamount','No sorting/storageIndex/identity/condition inferred','Not a raw macro runtime bridge or arbitrary quantity wildcard','No currentenabledwholegameinventory or actualgameacceptance'])
(R/'main39-uniform-amount-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(R/'main39-uniform-pending-private.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False));print(json.dumps(pending,ensure_ascii=False))
