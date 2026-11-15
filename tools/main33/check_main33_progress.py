"""One new literal progress slot,verified reuse;preserve its entire old quest and unrelated data."""
import pathlib,json,zipfile,hashlib,time,re
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
review=json.loads((R/'main33-literal-review-private.json').read_text(encoding='utf-8'));reuse=next(v for v in review['reuse_candidates'] if v['quest_id']==97927 and v['path']=='progress')
assert reuse['thai']=='ใช่ ข้าสอนเจ้าได้' and reuse['thai_sha256']=='cb147a9c035833f131ac3124ed33e9559035f278c567bea1a2407bfe9e2ceee5'
pair={k:v for k,v in review.items() if k not in ['reuse_candidates','source_NPC_name']};pair.update(thai=reuse['thai'],thai_sha256=reuse['thai_sha256'],translation_kind='verbatim_reviewed_reuse',reuse_source=dict(quest_id=97927,field='progress',path='progress',thai_sha256=reuse['thai_sha256']),meaning_review_passed=True,source_npc_key='10278')
base=R/'package-main28/build-0.470.0/ForeverThai-0.470.0-main28-COMBINED.zip';assert sha(base.read_bytes())=='a9c854976d2efac55b4821492714b7cf93dae627fbb77309d6bc820610cfb5e6'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('sampleName="CloudTester";sampleClass="Druid";sampleClassID="DRUID";sampleRace="Night Elf";issecretvalue=function(v)return v=="SECRET_SENTINEL"end;UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
serialize=l.eval('function(v) local function s(x) if type(x)~="table" then return type(x)..":"..tostring(x) end local t={} for k,v in pairs(x) do t[#t+1]=s(k).."="..s(v) end table.sort(t) return "{"..table.concat(t,",").."}" end return s(v) end')
q=97928;before=serialize(a.quests[q]);reuse_before=serialize(a.quests[97927]);held_before=serialize(a.quests[95772]);assert a.quests[q].progress is None
assert a.quests[97927].progress[1]==pair['expected_dynamic_signature'] and a.quests[97927].progress[2]==pair['thai']
overlay='-- MAIN33 own-ID literal progress;reviewed exact-source reuse,no condition or identity inference.\nlocal _, addon = ...\nassert(type(addon.quests[97928]) == "table" and addon.quests[97928].progress == nil, "MAIN33 baseline changed")\naddon.quests[97928].progress = { '+json.dumps(pair['expected_dynamic_signature'])+', '+json.dumps(pair['thai'],ensure_ascii=False)+' }\n'
l.execute(overlay,'ForeverThai',a);e=a.quests[q].progress;a.quests[q].progress=None;assert serialize(a.quests[q])==before;a.quests[q].progress=e
assert serialize(a.quests[97927])==reuse_before and serialize(a.quests[95772])==held_before
positives=negatives=routes=0
for name,cl,cid,race in [('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('MageReader','Mage','MAGE','Human'),('PriestReader','Priest','PRIEST','Windshaper Skyborne')]:
 g=l.globals();g.sampleName=name;g.sampleClass=cl;g.sampleClassID=cid;g.sampleRace=race
 assert a.Translate(e,pair['english'])==pair['thai'];positives+=1
 for wrong in [pair['english']+' Changed.',pair['english'][:-1],None,'','SECRET_SENTINEL',123]:assert a.Translate(e,wrong) is None;negatives+=1
 for var in ['sampleName','sampleClass','sampleClassID','sampleRace']:
  old=g[var];g[var]='SECRET_SENTINEL';assert a.Translate(e,pair['english']) is None;g[var]=old;negatives+=1
 assert a.Translate(None,pair['english']) is None;assert a.Translate(a.quests[q].description,pair['english']) is None;routes+=2
assert not re.search(r'\{(?:name|class|race|world)|[$|]',pair['english']+pair['thai'])
proposal=dict(batch='MAIN33',status='REVIEWED_ONE_PROGRESS_FIELD_SOURCE_CHECKS_PASSED_NOT_PACKAGED',counts=dict(new_supported_fields=1,quest_ids=1,new_Thai_fields=0,verbatim_reviewed_reuse_fields=1,complete_quests_claimed=0),baseline='0.470.0',fields=[pair],held_variant=dict(quest_id=95772,field='completion',english_sha256='4282163ceede3b1594c32e319047f6452890176a1c5b2f860d3a60e8cf164a23',reason='Same prior unproven third-party race role,not reader UnitRace;canonical unchanged'))
(R/'main33-reviewed-pairs.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');(R/'main33-reviewed-overlay.lua').write_text(overlay,encoding='utf-8',newline='\n')
report=dict(status='PASSED_ONE_NEW_LITERAL_PROGRESS_SLOT',quest_id=q,field='progress',positive_checks=positives,negative_checks=negatives,wrong_route_checks=routes,old_quest_except_new_slot_preserved=True,reuse97927_entire_quest_preserved=True,held95772_entire_quest_preserved=True,new_Thai_fields=0,new_supported_fields=1,verbatim_reviewed_reuse_fields=1,overlay_sha256=sha(overlay.encode()),proposal_sha256=sha((R/'main33-reviewed-pairs.json').read_bytes()),real_game_verified=False,bitmap_package_pending=True,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu)
(R/'main33-source-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report,indent=2))
