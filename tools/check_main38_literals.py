"""82 reviewed exact own-ID/phase literals; no matcher or engine edits."""
import pathlib,json,re,zipfile,hashlib,sys,time
from lupa.lua51 import LuaRuntime,lua_type
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time();sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
base=R/'package-main36/build-0.473.0/ForeverThai-0.473.0-main36-PRIVATE-TEST.zip';assert hashlib.sha256(base.read_bytes()).hexdigest()=='a606548c0b8877ca29fcee2bbca8919dba085ab166d87484e885982b27cb7add'
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','MainQuest35.lua','MainQuest36.lua','Match.lua','Atlas.lua','AtlasMain2526.lua','AtlasMain27.lua','AtlasMain28.lua','AtlasMain35.lua','AtlasMain36.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
def plain(v):return {str(k):plain(x) for k,x in v.items()} if lua_type(v)=='table' else v
def sig(s):
 s=re.sub(r'\$[Bb]','\n',s).replace('\u00a0',' ');s=re.sub(r'[ \t\r\n\f\v]+',' ',s).strip();b=s.encode();assert len(b)==len(s) and '$' not in s and '|' not in s;x=y=0
 for c in b:x=(x*257+c)%2147483647;y=(y*131+c)%2147483629
 return f'{len(b)}:{x}:{y}'
doc=json.loads((R/'main38-reviewed-pairs.json').read_text(encoding='utf8'));rows=doc['fields'];assert len(rows)==82 and len({(r['quest_id'],r['field']) for r in rows})==82
prior={q:plain(a.quests[q]) for q in {r['quest_id'] for r in rows}};held={q:plain(a.quests[q]) for q in [91754,95318,95772,97928,8315,84213,86792,9556]};reuseprior={r['reused_from']['quest_id']:plain(a.quests[r['reused_from']['quest_id']]) for r in rows if r.get('reused_from')}
lines=['-- MAIN38: reviewed literal fields;match exact own-ID full UI source only.','-- No enabled-quest inventory,player condition or identity/quantity macro dispatch inferred.','local _, addon = ...'];created=set();newslots=variants=0
for r in rows:
 q=r['quest_id'];f=r['field'];en=r['english'];assert sha(en)==r['english_sha256'];s=sig(en);assert s==r['expected_dynamic_signature'];ui=re.sub(r'\$[Bb]','\n',en);quest=a.quests[q];entry=quest[f] if quest is not None else None
 assert a.Translate(entry,ui) is None,(q,f,'already supported')
 assert r['meaning_review_passed'] and isinstance(r['thai'],str) and r['thai'];r['thai_sha256']=sha(r['thai'])
 if r.get('reused_from'):
  ref=r['reused_from'];source=a.quests[ref['quest_id']][ref['field']];assert a.Translate(source,ui)==r['thai'],(q,f,'reuse not exact')
 if quest is None and q not in created:
  lines.extend([f'assert(addon.quests[{q}] == nil, "MAIN38 quest baseline changed")',f'addon.quests[{q}] = {{}}']);created.add(q)
 pair='{ '+json.dumps(s)+', '+json.dumps(r['thai'],ensure_ascii=False)+' }'
 if entry is None:
  lines.extend([f'assert(addon.quests[{q}].{f} == nil, "MAIN38 field baseline changed")',f'addon.quests[{q}].{f} = '+pair]);newslots+=1;r['runtime_action']='new field'
 else:
  lines.extend([f'assert(type(addon.quests[{q}].{f}) == "table", "MAIN38 canonical missing")',f'addon.quests[{q}].{f}.variants = addon.quests[{q}].{f}.variants or {{}}',f'table.insert(addon.quests[{q}].{f}.variants, '+pair+')']);variants+=1;r['runtime_action']='append variant'
overlay='\n'.join(lines)+'\n';l.execute(overlay,'ForeverThai',a)
for q,before in prior.items():
 after=plain(a.quests[q]);changes=[r for r in rows if r['quest_id']==q]
 if before is None:assert set(after)=={r['field'] for r in changes};continue
 for r in changes:
  f=r['field']
  if r['runtime_action']=='new field':after.pop(f)
  else:
   vs=after[f]['variants'];vs.pop(str(len(vs)))
   if 'variants' not in before[f]:assert not vs;after[f].pop('variants')
 assert before==after,(q,'old data changed')
assert held=={q:plain(a.quests[q]) for q in held};assert reuseprior=={q:plain(a.quests[q]) for q in reuseprior}
pos=neg=wrong=0;g=l.globals()
for name,cl,cid,race in [('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('MageReader','Mage','MAGE','Human'),('PriestReader','Priest','PRIEST','Windshaper Skyborne')]:
 g.sampleName=name;g.sampleClass=cl;g.sampleClassID=cid;g.sampleRace=race
 for r in rows:
  q=r['quest_id'];f=r['field'];en=r['english'];ui=re.sub(r'\$[Bb]','\n',en);entry=a.quests[q][f];forms=[ui,'  '+re.sub(r'\s+','  ',ui)+' \n']
  if en==ui:forms.append(en)
  else:assert a.Translate(entry,en) is None;neg+=1
  for v in forms:assert a.Translate(entry,v)==r['thai'],(q,f,'positive');pos+=1
  for v in [None,'',ui+' [different source]',ui+'?',ui+' x',ui[1:],'x'+ui]:assert a.Translate(entry,v) is None,(q,f,'mutation');neg+=1
  for match in re.finditer(r'\d+',ui):
   mutated=ui[:match.start()]+str(int(match[0])+1)+ui[match.end():];assert a.Translate(entry,mutated) is None,(q,f,'number mutation');neg+=1
  for other in ['title','objective','description','progress','completion']:
   if other!=f:assert a.Translate(a.quests[q][other],ui) is None,(q,other,'wrong phase');wrong+=1
cuts=json.loads((R/'main38-reviewed-word-cuts.json').read_text(encoding='utf8'));needs=[]
for r in rows:
 for span in re.findall(r'[\u0e00-\u0e7f]+',r['thai']):
  if any(n['run']==span for n in needs):continue
  row=dict(run=span,existing_full_run=a.runs[span] is not None)
  if not row['existing_full_run']:
   assert span in cuts and ''.join(cuts[span])==span,('missing manual cuts',span);row['words']=cuts[span]
  needs.append(row)
report=dict(batch='MAIN38',status='PASSED_SOURCE_CHECKS_NOT_PACKAGED',supported_new_fields_or_variants=82,new_Thai_fields=67,verbatim_reviewed_reuse=15,quest_ids=len(prior),new_runtime_ids=len(created),new_field_slots=newslots,appended_variants=variants,positive_checks=pos,negative_checks=neg,wrong_phase_checks=wrong,all_old_target_canonical_alias_trees_preserved=True,reuse_source_trees_preserved=len(reuseprior),held_quests_preserved=list(held),glyph_baseline=len(a.glyphs),new_Thai_runs_needed=sum(not n['existing_full_run'] for n in needs),complete_quests_claimed=0,real_Windows_MacM2_acceptance=False,current_enabled_inventory_proven=False,overlay_sha256=sha(overlay),elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu)
for n,v in [('main38-reviewed-pairs.json',doc),('main38-source-checks.json',report),('main38-font-run-needs.json',needs)]:
 (R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'main38-reviewed-overlay.lua').write_text(overlay,encoding='utf8',newline='\n')
print(json.dumps(report,ensure_ascii=False));print(json.dumps([n['run'] for n in needs if not n['existing_full_run']],ensure_ascii=False))
