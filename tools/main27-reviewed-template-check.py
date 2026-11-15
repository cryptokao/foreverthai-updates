"""Affected25 data-only template checks under explicit primary schema. No matcher edit/old suite."""
import pathlib,json,re,zipfile,hashlib,collections,time
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
proposal=json.loads((R/'main27-reviewed-pairs.json').read_text(encoding='utf-8'));fields=proposal['fields'];assert len(fields)==25
base=R/'package-main25-26/build-0.468.0/ForeverThai-0.468.0-main25-26-PRIVATE-TEST.zip';assert sha(base.read_bytes())=='90b85b81dc4f9dc4d94b4349ec7c64a90889deedf8340c8976806115fb5441df'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('testName="CloudTester";testClass="Druid";testClassID="DRUID";testRace="Night Elf";issecretvalue=function(v)return v=="SECRET_SENTINEL"end;UnitName=function()return testName end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return testRace end')
serialize=l.eval('function(v) local function s(x) if type(x)~="table" then return type(x)..":"..tostring(x) end local t={} for k,v in pairs(x) do t[#t+1]=s(k).."="..s(v) end table.sort(t) return "{"..table.concat(t,",").."}" end return s(v) end')
old8315=serialize(a.quests[8315].objective);lines=['-- MAIN27 reviewed current-cache templates; explicit primary DATASETS.md role schema.','local _, addon = ...'];entries={}
for f in fields:
 q,k,en,th=f['quest_id'],f['field'],f['english'],f['thai'];assert sha(en.encode())==f['english_sha256'] and not re.search(r'\|[0-9]',en)
 source=collections.Counter({'n':'name','c':'class','r':'race'}[x.lower()] for x in re.findall(r'\$([nNcCrR])',en));target=collections.Counter(re.findall(r'\{(name|class|race)\}',th));assert source==target,(q,source,target)
 entry='{ '+json.dumps(f['expected_dynamic_signature'])+', '+json.dumps(th,ensure_ascii=False)+' }';entries[q]=l.eval('function()return '+entry+' end')();path=f'addon.quests[{q}].{k}'
 if q==8315:
  assert a.quests[q][k] is not None
  lines += [f'assert(type({path}) == "table", "MAIN27 canonical missing")',f'{path}.variants = {path}.variants or {{}}',f'table.insert({path}.variants, {entry})']
 else:
  assert a.quests[q] is not None and a.quests[q][k] is None
  lines += [f'assert({path} == nil, "MAIN27 field baseline changed")',path+' = '+entry]
 if f['translation_kind']=='verbatim_reviewed_reuse':
  rs=f['reuse_source'];assert sha(th.encode())==rs['thai_sha256'] and a.quests[rs['quest_id']][rs['field']][2]==th
 f['thai_sha256']=sha(th.encode())
overlay='\n'.join(lines)+'\n';l.execute(overlay,'ForeverThai',a)
vs=a.quests[8315].objective.variants;last=len(vs);saved=vs[last];vs[last]=None
if last==1:a.quests[8315].objective.variants=None
assert serialize(a.quests[8315].objective)==old8315
a.quests[8315].objective.variants=vs;vs[last]=saved
profiles=[('CloudTester','Druid','DRUID','Night Elf','ดรูอิด','ไนต์เอลฟ์'),('NewHunter','Hunter','HUNTER','Night Elf','พราน','ไนต์เอลฟ์'),('Arielle','Mage','MAGE','Human','จอมเวท','มนุษย์'),('Skywarden','Shaman','SHAMAN','High Order Skyborne','ชาแมน','สกายบอร์นฝ่ายไฮออร์เดอร์')]
positive=negative=wrongroute=0;short_race_positive=0
for name,cl,cid,race,thai_cl,thai_race in profiles:
 g=l.globals();g.testName=name;g.testClass=cl;g.testClassID=cid;g.testRace=race
 for f in fields:
  q,k,en,th=f['quest_id'],f['field'],f['english'],f['thai'];entry=entries[q]
  def rendered(n=name,c=cl,r=race):return re.sub(r'\$([nNcCrR])',lambda m:{'n':n,'c':c,'r':r}[m[1].lower()],re.sub(r'\$[Bb]','\n',en))
  ui=rendered();expected=th.replace('{name}',name).replace('{class}',thai_cl).replace('{race}',thai_race)
  assert a.Translate(a.quests[q][k],ui)==expected;positive+=1
  for ix,bad in enumerate([ui+' Changed.',ui.rstrip()[:-1],None,'','SECRET_SENTINEL',re.sub(r'\$[Bb]','\n',en),123]):
   assert a.Translate(entry,bad) is None,(q,k,name,'negative',ix)
   negative+=1
  for role,kwargs in [('n',dict(n='OtherPlayer')),('c',dict(c='Mage' if cl!='Mage' else 'Druid')),('r',dict(r='Orc'))]:
   if re.search(r'\$'+role,en,re.I):assert a.Translate(entry,rendered(**kwargs)) is None;negative+=1
  assert a.Translate(None,ui) is None;wrongroute+=1
  # Actual unchanged wrong phase route: preserve its baseline behavior; this overlay adds only the reviewed field.
  wrongphase='progress' if k in ['description','objective'] else 'description'
  assert a.Translate(a.quests[q][wrongphase],ui) is None;wrongroute+=1
  if len(re.findall(r'\$[nN]',en))>1:
   mixed=re.sub(r'\$[nN]','OtherPlayer',re.sub(r'\$[Bb]','\n',en),count=1);mixed=re.sub(r'\$[nN]',name,mixed);assert a.Translate(entry,mixed) is None;negative+=1
  for var in ['testName','testClass','testClassID','testRace']:
   old=g[var];g[var]='SECRET_SENTINEL';assert a.Translate(entry,ui) is None;g[var]=old;negative+=1
  if race=='High Order Skyborne' and re.search(r'\$[rR]',en):
   expected_short=th.replace('{name}',name).replace('{class}',thai_cl).replace('{race}','สกายบอร์น');assert a.Translate(a.quests[q][k],rendered(r='Skyborne'))==expected_short;short_race_positive+=1
proposal['status']='SOURCE_REVIEW_AND_AFFECTED_TEMPLATE_CHECKS_PASSED_NOT_PACKAGED';proposal['tracker_note']='8315objective retains existing multi-line Thai; Tracker existing newline guard expected English fallback. No Tracker/engine change.'
(R/'main27-reviewed-pairs.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(R/'main27-reviewed-overlay.lua').write_text(overlay,encoding='utf-8')
receipt=dict(status='PASSED_AFFECTED25_TYPED_DATA_TEMPLATES',new_supported_fields=25,quest_ids=25,new_Thai_fields=7,verbatim_reviewed_reuse_fields=18,profiles=len(profiles),positive_exact_matches=positive,short_Skyborne_alias_positive=short_race_positive,negative_template_checks=negative,wrongID_wrongphase_route_negatives=wrongroute,old8315canonical_and_aliases_preserved=True,matcher_changed=False,old_suites_rerun=False,bitmap_or_game_claim=False,overlay_sha256=sha(overlay.encode()),pairs_sha256=sha((R/'main27-reviewed-pairs.json').read_bytes()),elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limits=['Synthetic contexts prove affected data/template guards, not actual quest eligibility or whole-game inventory','No source role inference from story/normalized export; schema only for exact raw current query fields','91754/95318unproven |5 grammar held','8315multi-line objective Tracker English safe fallback preserved','Font readiness,combined package and real Windows/Mac M2 acceptance pending'])
(R/'main27-template-checks.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False,indent=2))
