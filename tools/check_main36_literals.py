"""MAIN36: exact own-ID literal additions, preserving all canonical/alias data."""
import pathlib,json,re,zipfile,hashlib,sys,copy,time
from lupa.lua51 import LuaRuntime,lua_type
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent
start=time.perf_counter();cpu=time.process_time();sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main35/build-0.472.0/ForeverThai-0.472.0-main35-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','MainQuest35.lua','Match.lua','Atlas.lua','AtlasMain2526.lua','AtlasMain27.lua','AtlasMain28.lua','AtlasMain35.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
def plain(v):
 return {str(k):plain(x) for k,x in v.items()} if lua_type(v)=='table' else v
def sig(s):
 s=re.sub(r'\$[Bb]','\n',s).replace('\u00a0',' ');s=re.sub(r'[ \t\r\n\f\v]+',' ',s).strip();b=s.encode();x=y=0
 assert len(b)==len(s),'This batch is literal ASCII English only'
 assert not re.search(r'\$(?![Bb])|\|',s),'No identity/numeric/grammar macros or markup'
 for c in b:x=(x*257+c)%2147483647;y=(y*131+c)%2147483629
 return f'{len(b)}:{x}:{y}'
doc=json.loads((R/'main36-reviewed-pairs.json').read_text(encoding='utf8'));rows=doc['fields'];assert len(rows)==13
prior={q:plain(a.quests[q]) for q in {r['quest_id'] for r in rows}};held={q:plain(a.quests[q]) for q in [91754,95318,95772,97928,8315,84213]}
lines=['-- MAIN36: full literal own-ID fields only. Game chooses conditions; no inferred dispatch.','local _, addon = ...'];actions={};newids=set()
for r in rows:
 q=r['quest_id'];f=r['field'];en=r['english'];assert sha(en)==r['english_sha256'];s=sig(en);assert s==r['expected_dynamic_signature'];old=a.quests[q];entry=old[f] if old is not None else None
 assert a.Translate(entry,en) is None,(q,f,'already supported')
 if r['translation_kind']=='verbatim_reviewed_reuse':
  assert entry is not None and isinstance(entry[2],str);r['thai']=entry[2];r['reused_from']=dict(quest_id=q,field=f,baseline='0.472.0 canonical')
 assert isinstance(r['thai'],str) and r['thai'];r['thai_sha256']=sha(r['thai'])
 pair='{ '+json.dumps(s)+', '+json.dumps(r['thai'],ensure_ascii=False)+' }'
 if old is None and q not in newids:
  lines.extend([f'assert(addon.quests[{q}] == nil, "MAIN36 new quest baseline changed")',f'addon.quests[{q}] = {{}}']);newids.add(q)
 if entry is None:
  lines.extend([f'assert(addon.quests[{q}].{f} == nil, "MAIN36 field baseline changed")',f'addon.quests[{q}].{f} = '+pair]);actions[q,f]='new field'
 else:
  lines.extend([f'assert(type(addon.quests[{q}].{f}) == "table", "MAIN36 canonical missing")',f'addon.quests[{q}].{f}.variants = addon.quests[{q}].{f}.variants or {{}}',f'table.insert(addon.quests[{q}].{f}.variants, '+pair+')']);actions[q,f]='append literal variant'
overlay='\n'.join(lines)+'\n';l.execute(overlay,'ForeverThai',a)
for q,before in prior.items():
 after=plain(a.quests[q]);changes=[r for r in rows if r['quest_id']==q]
 if before is None:assert set(after)=={r['field'] for r in changes};continue
 for r in changes:
  f=r['field']
  if actions[q,f]=='new field':after.pop(f)
  else:
   v=after[f]['variants'];v.pop(str(len(v)))
   if 'variants' not in before[f]:assert not v;after[f].pop('variants')
 assert before==after,(q,'canonical or old aliases changed')
assert held=={q:plain(a.quests[q]) for q in held}
positives=negatives=wrongroutes=0;g=l.globals()
for name,cl,cid,race in [('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('MageReader','Mage','MAGE','Human'),('PriestReader','Priest','PRIEST','Windshaper Skyborne')]:
 g.sampleName=name;g.sampleClass=cl;g.sampleClassID=cid;g.sampleRace=race
 for r in rows:
  q=r['quest_id'];f=r['field'];en=r['english'];entry=a.quests[q][f]
  ui=re.sub(r'\$[Bb]','\n',en)
  forms=[ui,'  '+re.sub(r'\s+','  ',ui)+' \n']
  if ui==en:forms.append(en)
  else:assert a.Translate(entry,en) is None;negatives+=1
  for v in forms:
   assert a.Translate(entry,v)==r['thai'],(q,f,'positive');positives+=1
  # Unchanged/canonical aliases still accepted as appropriate; only reject deliberate full-body mutations.
  for v in [None,'',ui+' [different source]',ui+'?',ui+' x',ui[1:],'x'+ui]:
   assert a.Translate(entry,v) is None,(q,f,'negative',v);negatives+=1
  for other in ['progress','completion']:
   assert a.Translate(a.quests[q][other],ui) is None,(q,other);wrongroutes+=1
  for old,new in [('3 Arcanite','4 Arcanite'),('15 Silithus','16 Silithus'),('20 gold','21 gold'),('Mokvar','Deliana'),('Gatekeeper Rageroar','Gatekeeper WRONG'),('when your side is victorious','when your side is defeated')]:
   if old in ui:assert a.Translate(entry,ui.replace(old,new)) is None;negatives+=1
needs=[]
for r in rows:
 for span in re.findall(r'[\u0e00-\u0e7f]+',r['thai']):
  if not any(n['run']==span for n in needs):needs.append(dict(run=span,existing_full_run=a.runs[span] is not None))
report=dict(batch='MAIN36',status='PASSED_SOURCE_CHECKS_NOT_PACKAGED',supported_new_fields_or_variants=13,new_Thai_fields=10,verbatim_reviewed_reuse=3,quest_ids=8,new_runtime_ids=len(newids),new_field_slots=sum(v=='new field' for v in actions.values()),appended_variants=sum(v!='new field' for v in actions.values()),positive_checks=positives,negative_checks=negatives,wrong_phase_checks=wrongroutes,all_old_canonical_and_alias_trees_preserved=True,held_quests_preserved=list(held),glyph_baseline=len(a.glyphs),new_Thai_runs_needed=sum(not v['existing_full_run'] for v in needs),complete_quests_claimed=0,real_Windows_MacM2_acceptance=False,current_enabled_inventory_proven=False,overlay_sha256=sha(overlay),elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu)
for n,v in [('main36-reviewed-pairs.json',doc),('main36-source-checks.json',report),('main36-font-run-needs.json',needs)]:
 (R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'main36-reviewed-overlay.lua').write_text(overlay,encoding='utf8',newline='\n')
print(json.dumps(report,ensure_ascii=False));print(json.dumps([n['run'] for n in needs if not n['existing_full_run']],ensure_ascii=False))
