"""Compare only19selected primary page fields;reuse identical new-source proofs."""
import pathlib,json,re,zipfile,hashlib,collections,time
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time()
rows=json.loads((R/'main34-primary-selected-fields.json').read_text(encoding='utf8'));assert len(rows)==19
prior={}
for f in ['main34-live-sql-audit.json','main34-own-source-audit.json']:
 for v in json.loads((R/f).read_text(encoding='utf8'))['rows']:
  if v['status'] in ['supported_exact','supported_linebreak_markup','supported_exact_or_markup','diagnostic_identity_substitution_supported_NOT_roleproof']:
   prior[v['quest_id'],v['field'],v['english_sha256']]=v['status']
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 for f in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','Match.lua']:l.execute(z.read('ForeverThai/'+f).decode(),'ForeverThai',a)
l.execute('testClass="Druid";testClassID="DRUID";UnitName=function()return "CloudTester"end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return "Night Elf"end')
classes=[('Druid','DRUID'),('Hunter','HUNTER'),('Warrior','WARRIOR'),('Paladin','PALADIN'),('Rogue','ROGUE'),('Priest','PRIEST'),('Shaman','SHAMAN'),('Mage','MAGE'),('Warlock','WARLOCK')]
out=[];held=[];counts=collections.Counter();reuse=0;calls=0
for v in rows:
 en=v['english'];q=v['quest_id'];f=v['field'];sh=hashlib.sha256(en.encode()).hexdigest();old=prior.get((q,f,sh));entry=a.quests[q][f] if a.quests[q] else None
 l.globals().testClass='Druid';l.globals().testClassID='DRUID'
 if old:status=old;reuse+=1
 else:
  thai=a.Translate(entry,en);calls+=1
  if thai is not None:status='supported_primary_full_text'
  elif any(x in en for x in ['<class>','<name>','<race>']):
   match=False
   for cl,cid in classes:
    l.globals().testClass=cl;l.globals().testClassID=cid
    for cls in [cl,cl.lower()]:
     txt=en.replace('<class>',cls).replace('<name>','CloudTester').replace('<race>','Night Elf');thai=a.Translate(entry,txt);calls+=1
     if thai is not None:match=True;break
    if match:break
   status='diagnostic_primary_placeholder_supported_NOT_roleproof' if match else 'held_primary_placeholder_roles'
  else:status='literal_primary_unmatched_needs_meaning_review'
 meta={k:x for k,x in v.items() if k!='english'};meta.update(english_sha256=sh,english_bytes=len(en.encode()),status=status,prior_identical_form_proof_reused=bool(old));out.append(meta);counts[status]+=1
 if 'held' in status or 'unmatched' in status:held.append(dict(meta,english=en))
r=dict(batch='MAIN34',scope='Only19selected own-ID objectives/progress/completion from9primary pages,not old full corpus',counts=dict(counts),forms=19,quests=len(set(x['quest_id'] for x in rows)),rows=out,prior_identical_forms_not_rerun=reuse,matcher_calls=calls,new_Thai_fields=0,new_aliases=0,runtime_changed=False,current_enabled_inventory_proven=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu)
(R/'main34-primary-page-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(R/'main34-primary-unmatched-private.json').write_text(json.dumps(held,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in r.items() if k!='rows'},ensure_ascii=True));print(json.dumps(held,ensure_ascii=True))
