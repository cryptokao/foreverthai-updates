"""Only4new literal objective fields;preserve entire old quest objects and test exact routing."""
import pathlib,json,re,zipfile,hashlib,time,sys
from lupa.lua51 import LuaRuntime,lua_type
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((R/'main35-reviewed-four-input.json').read_text(encoding='utf8'));prior=json.loads((R/'main35-four-literal-reuse-review.json').read_text(encoding='utf8'));prior={v['quest_id']:v for v in prior}
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
base=R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip';assert sha(base.read_bytes())=='54eef1b1fb33379332d8bfe5621d166e9bc77f9fe5931cdf510efbfd782b5077'
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','Match.lua','Atlas.lua','AtlasMain2526.lua','AtlasMain27.lua','AtlasMain28.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
serial=l.eval('function(v)local function s(x)if type(x)~="table" then return type(x)..":"..tostring(x)end local t={}for k,v in pairs(x)do t[#t+1]=s(k).."="..s(v)end table.sort(t)return "{"..table.concat(t,",").."}"end return s(v)end')
old={v['quest_id']:serial(a.quests[v['quest_id']]) for v in p['fields']};protected={q:serial(a.quests[q]) for q in [97928,95772,91754]}
overlay=['-- MAIN35: four exact own-ID literal objective fields;retain all old quest data.','local _, addon = ...']
runs=set()
for v in p['fields']:
 q=v['quest_id'];assert v['field']=='objective' and a.quests[q].objective is None and not re.search(r'[$|{}<>]',v['english']);pr=prior[q];assert pr['english']==v['english'] and not pr['reuse_candidates']
 v.update(expected_dynamic_signature=pr['expected_dynamic_signature'],english_sha256=pr['english_sha256'],thai_sha256=sha(v['thai'].encode()),meaning_review_passed=True)
 assert int(v['expected_dynamic_signature'].split(':')[0])==len(v['english'].encode())
 overlay+=['assert(type(addon.quests['+str(q)+']) == "table" and addon.quests['+str(q)+'].objective == nil, "MAIN35 baseline changed")','addon.quests['+str(q)+'].objective = { '+json.dumps(v['expected_dynamic_signature'])+', '+json.dumps(v['thai'],ensure_ascii=False)+' }']
 runs.update(re.findall(r'[\u0e00-\u0e7f]+',v['thai']))
over='\n'.join(overlay)+'\n';l.execute(over,'ForeverThai',a)
for q,before in old.items():
 entry=a.quests[q].objective;a.quests[q].objective=None;assert serial(a.quests[q])==before;a.quests[q].objective=entry
for q,before in protected.items():assert serial(a.quests[q])==before
profiles=[('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('MageReader','Mage','MAGE','Human'),('PriestReader','Priest','PRIEST','Windshaper Skyborne')]
pos=negative=routes=0
for name,cl,cid,race in profiles:
 g=l.globals();g.sampleName=name;g.sampleClass=cl;g.sampleClassID=cid;g.sampleRace=race
 for v in p['fields']:
  q=v['quest_id'];en=v['english'];entry=a.quests[q].objective
  assert a.Translate(entry,en)==v['thai'];pos+=1
  assert a.Translate(entry,en.replace(' ',' \n '))==v['thai'];pos+=1
  mutation=en.replace('Pix Xizzix','Wrong Recipient') if 'Pix Xizzix' in en else en.replace('kodos','horses')
  for bad in [en+' Changed.',en[:-1],en[1:],mutation,'',None]:assert a.Translate(entry,bad) is None;negative+=1
  for wrong in ['description','progress']:assert a.Translate(a.quests[q][wrong],en) is None;routes+=1
words={'รวบรวม':['รวบรวม'],'จาก':['จาก'],'ใน':['ใน'],'และ':['และ'],'ที่':['ที่'],'แล้วนำทั้งหมดไปให้':['แล้ว','นำ','ทั้งหมด','ไป','ให้'],'ตรวจดูโคโดหุ้มเกราะเพื่อเลือกพาหนะระดับมหากาพย์ของเจ้า':['ตรวจดู','โคโด','หุ้มเกราะ','เพื่อ','เลือก','พาหนะ','ระดับ','มหากาพย์','ของ','เจ้า']}
assert set(words)==runs and all(''.join(words[s])==s for s in runs)
font=[]
for run in sorted(runs):
 font.append(dict(run=run,existing_full_run=a.runs[run] is not None,words=words[run],word_runs_present={s:a.runs[s] is not None for s in words[run]}))
p.update(status='FOUR_LITERAL_OBJECTIVE_FIELDS_SOURCE_CHECKS_PASSED_NOT_PACKAGED',baseline='0.471.0',source_checks=dict(positive=pos,negative=negative,wrong_routes=routes),old_entire_quests_except_added_slot_preserved=True,protected_97928_95772_91754_preserved=True)
report=dict(batch='MAIN35',status='PASSED_FOUR_NEW_LITERAL_OBJECTIVE_FIELDS',positive=pos,negative=negative,wrong_routes=routes,new_Thai_fields=4,new_supported_fields=4,quest_ids=4,complete_quests_claimed=0,overlay_sha256=sha(over.encode()),old_entire_quests_except_new_slots_preserved=True,protected_quests_preserved=True,real_game_verified=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu,initial_helper_note='Initial escaped-whitespace signature helper was rejected before any overlay;fixed and ASCII byte-length invariant added;this check validates full original English against actual matcher')
for n,d in [('main35-reviewed-pairs.json',p),('main35-source-checks.json',report),('main35-font-run-needs.json',font)]: (R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'main35-reviewed-overlay.lua').write_text(over,encoding='utf8',newline='\n')
print(json.dumps(report,indent=2));print(json.dumps(font,ensure_ascii=False,indent=2))
