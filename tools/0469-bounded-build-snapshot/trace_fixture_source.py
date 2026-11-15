"""New literal own-ID entries and affected native/Questie routing only; font review pending."""
import pathlib,json,re,hashlib,subprocess
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';BASE='1e04b81e0374c8c282c70b54508cf6c8dcc98a37';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
prior=git('show',BASE+':src/ForeverThai/Catalog.lua');current=(RUN/'Catalog.lua').read_bytes();assert current.startswith(prior);unchanged=0
for name in git('ls-tree','-r','--name-only',BASE,'src/ForeverThai').decode().splitlines():
 if name.endswith('/Catalog.lua'):continue
 assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name;unchanged+=1
cases=json.loads((ROOT/'tests/main17-cases.json').read_text())['cases'];fields=json.loads((ROOT/'evidence/main17-translations.json').read_text())['fields'];assert len(cases)==len(fields)==12
lua=LuaRuntime(unpack_returned_tuples=True);a=lua.table();old=lua.table()
fixture='''
SECRET={};ForeverThaiQuestieTracker=true;calls={}
function GetLocale()return "enUS"end
function GetBuildInfo()return "1.60.1","70938","",16001 end
function UnitName()return "Nira"end
function UnitClass()return "Druid","DRUID"end
function UnitRace()return "Night Elf"end
function issecretvalue(v)return v==SECRET end
function InCombatLockdown()return false end
function CreateFrame()return {RegisterEvent=function()end,SetScript=function()end}end
function hooksecurefunc(object,key,callback)local original=object[key];object[key]=function(self,...)local value=original(self,...);callback(self,...);return value end end
C_QuestLog={GetTitleForQuestID=function()return currentSource end,GetLogIndexForQuestID=function()return 1 end}
function GetQuestLogLeaderBoard()return currentSource,"log"end
QuestObjectiveTracker={AnchorBlock=function()end,MarkDirty=function()end}
function label()return {GetFont=function()return "Default",16 end,GetTextColor=function()return 1,1,1 end,GetHeight=function()return 18 end,IsTruncated=function()return false end,SetText=function(self,v)self.text=v end}end
Questie={db={profile={trackerFontSizeQuest=16,trackerFontSizeObjective=16}}}
lines={AddTitle=function(o)return o end,AddObjective=function(o)return o end}
data={GetObjectiveText=function(o)return o.Description end};qtracker={Update=function()end}
QuestieLoader={ImportModule=function(_,n)if n=="QuestieTracker"then return qtracker elseif n=="TrackerData"then return data else return lines end end}
C_AddOns={IsAddOnLoaded=function(n)return n=="Questie"end}
''';lua.execute(fixture)
for obj,cat in [(a,current),(old,prior)]:
 lua.execute(cat.decode(),'ForeverThai',obj);lua.execute((RUN/'Match.lua').read_text(),'ForeverThai',obj)
pos=neg=0
for c in cases:
 q,f=c['quest_id'],c['field'];oldEntry=old.quests[q][f] if old.quests[q] else None;assert oldEntry is None,(q,f,'overwrite')
 entry=a.quests[q][f];assert a.Translate(entry,c['english'])==c['expected'];pos+=1
 bad=[c['english']+' Extra requirement.','Changed source. '+c['english']]
 if q in [84147,84148] and f=='objective':
  bad.extend([c['english'].replace('15 Winterspring','20 Winterspring'),c['english'].replace('20 gold','15 gold'),c['english'].replace('Wildheart Bracers',"Beaststalker's Bindings") if q==84147 else c['english'].replace("Beaststalker's Bindings",'Wildheart Bracers')])
 if q==80411 and f=='objective':bad.append(c['english'].replace(' You must complete the job alone.',''))
 if q==98462:bad.extend([c['english'].replace('5 Chillwind','4 Chillwind'),c['english'].replace('5 Winterspring','6 Winterspring')])
 for text in bad:assert a.Translate(entry,text) is None,(q,f,text);neg+=1
assert set(int(q) for q,_ in a.quests.items())-set(int(q) for q,_ in old.quests.items())=={80411,80526,84147,84148,89015,91907}
for q in [80411,80526,84147,84148,89015,91907]:
 for f in ['description','progress','completion']:assert a.quests[q][f] is None
assert a.quests[91907].objective is None
# Actual unchanged Tracker module with the real current Atlas. Translation routing
# is asserted even where a new Thai run correctly leaves the label English pre-font.
lua.globals().addon=a;lua.execute((RUN/'Atlas.lua').read_text(),'ForeverThai',a);lua.execute('originalTranslate=addon.Translate;addon.Translate=function(entry,source)local thai=originalTranslate(entry,source);calls[#calls+1]={entry=entry,source=source,thai=thai};return thai end');lua.execute((RUN/'Tracker.lua').read_text(),'ForeverThai',a);assert a.SetQuestieTrackerThai(True)
routepos=routeneg=0;rendered=0;pending=[]
for c in cases:
 q,f=c['quest_id'],c['field'];g=lua.globals();g.q=q;g.currentSource=c['english'];g.currentField=f;g.expected=c['expected'];ready=all(a.runs[s] is not None for s in re.findall(r'[\u0e00-\u0e7f]+',c['expected']))
 lua.execute('''
 calls={};header=label();objective=label();block={id=q,parentModule=QuestObjectiveTracker,HeaderText=header,usedLines={[1]={used=true,Text=objective}},SetStringText=function(_,font,text)font:SetText(text)end}
 QuestObjectiveTracker:AnchorBlock(block);targetLabel=currentField=="title" and header or objective
 block:SetStringText(targetLabel,currentSource);assert(#calls==1 and calls[1].thai==expected and calls[1].entry==addon.quests[q][currentField])
 ''');out=g.targetLabel.text;assert ('|T' in out) if ready else out==c['english'];routepos+=1;rendered+=int(ready)
 lua.execute('''calls={};original={clickMode="quest",target={Id=q,name=currentSource},text=currentSource};obj={questId=q,Type="log",Description=currentSource};if currentField=="title"then result=lines.AddTitle(original).text;assert(original.text==currentSource)else result=data.GetObjectiveText(obj)end;assert(#calls==1 and calls[1].thai==expected and calls[1].entry==addon.quests[q][currentField])''');assert ('|T' in g.result) if ready else g.result==c['english'];routepos+=1;rendered+=int(ready)
 if not ready:pending.append(dict(quest_id=q,field=f))
 # Settings-off must preserve native and Questie text without translating.
 a.SetQuestieTrackerThai(False);lua.execute('''calls={};block:SetStringText(targetLabel,currentSource);assert(targetLabel.text==currentSource);if currentField=="title"then result=lines.AddTitle(original).text else result=data.GetObjectiveText(obj)end;assert(result==currentSource and #calls==0)''');routeneg+=2;a.SetQuestieTrackerThai(True)
 # Wrong own-ID must not fall through to a similarly worded other quest.
 lua.execute('''calls={};block.id=999999;block:SetStringText(targetLabel,currentSource);assert(targetLabel.text==currentSource and #calls==0);original.target.Id=999999;obj.questId=999999;if currentField=="title"then result=lines.AddTitle(original).text else result=data.GetObjectiveText(obj)end;assert(result==currentSource and #calls==0)''');routeneg+=2
for f in fields:assert sha(f['english'].encode())==f['english_sha256'] and sha(f['thai'].encode())==f['thai_sha256']
report=dict(status='passed',baseline_runtime_source=BASE,catalog_sha256=sha(current),old_catalog_prefix_preserved=True,unchanged_other_runtime_files=unchanged,new_ownID_entries=6,unique_source_cases=12,unique_quest_ids=7,new_thai_fields=6,reused_thai_fields=6,independent_static_oracles=12,positive_executions=pos,negative_executions=neg,tracker_actual_native_and_questie_routing_executions=routepos,tracker_settings_and_wrongID_negative_executions=routeneg,tracker_existing_atlas_bitmap_rendered_executions=rendered,tracker_missing_new_run_fallback_fields=pending,no_unproven_phases_created=True,font_build_pending_root_review=True,version_package_unchanged=True,scope='New MAIN17 literal fields and routing only. Real existing Atlas used, no synthetic glyphs or forced rendering; missing runs retain English until reviewed append. No NPC/Skills/party/full suite/game execution.')
(ROOT/'evidence/main17-regression.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
