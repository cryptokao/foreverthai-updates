"""Only17 new literal conditional variants; preserve every old canonical/alias and do not infer conditions."""
import pathlib,json,zipfile,re,hashlib,time,collections
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((R/'main28-reviewed-pairs.json').read_text(encoding='utf-8'));fields=p['fields'];assert len(fields)==17 and len({f['quest_id'] for f in fields})==13
base=R/'package-main27/build-0.469.0/ForeverThai-0.469.0-main27-PRIVATE-TEST.zip';assert sha(base.read_bytes())=='4fb985134c382d87744214a4ab290e5d3a3caf81a2cc0e47eaa17559dbd90021'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('testName="CloudTester";testClass="Druid";testClassID="DRUID";testRace="Night Elf";issecretvalue=function(v)return v=="SECRET_SENTINEL"end;UnitName=function()return testName end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return testRace end')
serialize=l.eval('function(v) local function s(x) if type(x)~="table" then return type(x)..":"..tostring(x) end local t={} for k,v in pairs(x) do t[#t+1]=s(k).."="..s(v) end table.sort(t) return "{"..table.concat(t,",").."}" end return s(v) end')
before={q:serialize(a.quests[q].description) for q in {f['quest_id'] for f in fields}};old_counts={q:len(a.quests[q].description.variants) if a.quests[q].description.variants is not None else None for q in before};lines=['-- MAIN28 literal conditional description bodies. Game selects conditions; addon matches only exact text.','local _, addon = ...'];newentries=[]
for f in fields:
 q,en,th=f['quest_id'],f['english'],f['thai'];assert sha(en.encode())==f['english_sha256'] and not re.search(r'\$|\{(?:name|class|race|world)',en+th)
 assert re.fullmatch(r'\d+:\d+:\d+',f['expected_dynamic_signature'])
 if f['translation_kind']=='verbatim_reviewed_reuse':
  rs=f['reuse_source'];entry=a.quests[rs['quest_id']][rs['field']];tail=rs['path'][len(rs['field']):]
  while tail:
   m=re.match(r'^\.variants\[(\d+)\]',tail);assert m,rs['path'];entry=entry.variants[int(m[1])];tail=tail[m.end():]
  assert entry[2]==th and sha(th.encode())==rs['thai_sha256']
 entrytxt='{ '+json.dumps(f['expected_dynamic_signature'])+', '+json.dumps(th,ensure_ascii=False)+' }';e=l.eval('function()return '+entrytxt+' end')();newentries.append(e);path=f'addon.quests[{q}].description'
 lines.extend([f'assert(type({path}) == "table", "MAIN28 canonical missing")',f'{path}.variants = {path}.variants or {{}}',f'table.insert({path}.variants, {entrytxt})']);f['thai_sha256']=sha(th.encode())
overlay='\n'.join(lines)+'\n';l.execute(overlay,'ForeverThai',a)
for q in before:
 entry=a.quests[q].description;vs=entry.variants;old=old_counts[q];added=len(vs)-(old or 0);saved=[vs[i] for i in range((old or 0)+1,len(vs)+1)]
 for i in range(len(vs),(old or 0),-1):vs[i]=None
 if old is None:entry.variants=None
 assert serialize(entry)==before[q]
 entry.variants=vs
 for i,v in enumerate(saved,start=(old or 0)+1):vs[i]=v
positive=negative=routes=0
for name,cl,cid,race in [('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('Felflick','Paladin','PALADIN','Human'),('Hailen','Warlock','WARLOCK','Orc')]:
 g=l.globals();g.testName=name;g.testClass=cl;g.testClassID=cid;g.testRace=race
 for f,e in zip(fields,newentries):
  en=f['english'];q=f['quest_id'];assert a.Translate(a.quests[q].description,en)==f['thai'];positive+=1
  for bad in [en+' Changed.',en.rstrip()[:-1],None,'','SECRET_SENTINEL',123]:assert a.Translate(e,bad) is None;negative+=1
  for var in ['testName','testClass','testClassID','testRace']:
   old=g[var];g[var]='SECRET_SENTINEL';assert a.Translate(e,en) is None;g[var]=old;negative+=1
  assert a.Translate(None,en) is None;assert a.Translate(a.quests[q].objective,en) is None;routes+=2
p['status']='REVIEWED_SOURCE_AND_AFFECTED_LITERAL_VARIANT_CHECKS_PASSED_NOT_PACKAGED'
(R/'main28-reviewed-pairs.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');(R/'main28-reviewed-overlay.lua').write_text(overlay,encoding='utf-8',newline='\n')
receipt=dict(status='PASSED17_NEW_LITERAL_CONDITIONAL_VARIANTS',source_variants=17,quest_ids=13,new_Thai_variants=8,verbatim_reuse_variants=9,complete_quests_claimed=0,positive_exact_matches=positive,negative_template_checks=negative,wrongID_wrongphase_negatives=routes,old_canonical_alias_trees_preserved=13,playerConditionId_interpreted=False,creatureId_binding_guessed=False,fixed_class_race_NPC_names_not_player_slots=True,matcher_or_old_runtime_changed=False,overlay_sha256=sha(overlay.encode()),pairs_sha256=sha((R/'main28-reviewed-pairs.json').read_bytes()),elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limitations=['Only source/template guards,not actual condition eligibility/current enabled inventory','98391uppercaseGheld;91754basepipe5grammarstillheld independently of this literal variant','Font/package/real Windows/MacM2 game acceptance pending','Old UI/Skill/NPC/fullfont suites not rerun'])
(R/'main28-variant-checks.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(receipt,indent=2))
