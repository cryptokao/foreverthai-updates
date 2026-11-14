"""Focused70938 Speech/Quest/Tracker plus required narrow old-build Perception receipt replay.
No NPC686, source audit, old nine-case suite or font generation.
"""
import ast,hashlib,json,pathlib,sys,zipfile
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';archive=pathlib.Path(sys.argv[1]);z=zipfile.ZipFile(archive);sha=lambda b:hashlib.sha256(b).hexdigest()
for name in z.namelist():assert z.read(name)==(ROOT/'src'/name).read_bytes()
def load(l,a,name):l.execute(z.read('ForeverThai/'+name).decode(),'ForeverThai',a)
# Small original NPC fixture is recovered as a literal; no686 corpus import/replay.
tree=ast.parse((ROOT/'tools/npc_replay.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='replay');fixture=ast.literal_eval(next(n.value for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fixture' for t in n.targets)))
l=LuaRuntime(unpack_returned_tuples=True);l.execute(fixture);l.globals().build='70938';a=l.table()
for n in ['Catalog.lua','Match.lua','Atlas.lua','Bitmap.lua','SpeechData.lua']:load(l,a,n)
l.execute('local a=...;local original=a.BitmapLayer;a.BitmapLayer=function(...)local layer,draw=original(...);return layer,function(text,...)draws[#draws+1]=text;return draw(text,...)end end',a);load(l,a,'Speech.lua')
l.execute('''
roster={}
function UnitExists(u)return roster[u]~=nil end
function UnitIsPlayer(u)return roster[u]~=nil and roster[u].player~=false end
function UnitInParty(u)return roster[u]~=nil end
function UnitInRaid(u)return nil end
function UnitGUID(u)if u=="player" then return "Player-1-1" end;return roster[u] and roster[u].guid end
function UnitName(u)if u=="player" then return playerName end;return roster[u] and roster[u].name,"" end
''');g=l.globals();cases=json.loads((ROOT/'tests/speech-party-cases11.json').read_text())+json.loads((ROOT/'tests/speech-party-extra-cases12.json').read_text());assert len(cases)==16;pos=neg=0
for c in cases:
 g.roster=l.table_from({'party1':l.table_from(dict(name='Maelin',guid='Player-1-2'))});a.SpeechCommand('speech hide');g.event(c['event'],c['english'],c['npc_id']);assert g.frames.ForeverThaiSpeechReader.IsShown(g.frames.ForeverThaiSpeechReader);assert g.draws[len(g.draws)].endswith(c['thai']);pos+=1
 for bad in [c['english'].replace('Maelin','Unrelated'),c['english']+' changed']:
  a.SpeechCommand('speech hide');before=len(g.draws);g.event(c['event'],bad,c['npc_id']);assert len(g.draws)==before;neg+=1
c=cases[0];g.roster=l.table();g.playerName='Maelin';a.SpeechCommand('speech hide');g.event(c['event'],c['english'],c['npc_id']);assert g.frames.ForeverThaiSpeechReader.IsShown(g.frames.ForeverThaiSpeechReader);pos+=1;g.tick(16);assert not g.frames.ForeverThaiSpeechReader.IsShown(g.frames.ForeverThaiSpeechReader)
for kind in ['text_secret','guid_secret','off','unsupported_build','unsupported_locale','nonplayer_guid']:
 a.SpeechCommand('speech hide');before=len(g.draws);text=c['english'];guid=None;g.build='70938';g.locale='enUS';g.ForeverThaiSpeech=l.table()
 if kind=='text_secret':text=g.SECRET
 if kind=='guid_secret':guid=g.SECRET
 if kind=='off':g.ForeverThaiSpeech=l.table_from({'enabled':False})
 if kind=='unsupported_build':g.build='70939'
 if kind=='unsupported_locale':g.locale='frFR'
 if kind=='nonplayer_guid':guid='Player-1-2'
 g.event(c['event'],text,c['npc_id'],guid);assert len(g.draws)==before;neg+=1
# Existing Speech build/locale gates directly; no old speech UI/corpus rerun.
s=(RUN/'Speech.lua').read_text();gate=s[s.index('local function supported()'):s.index('\nlocal function show')];f=l.execute(gate+'\nreturn supported');oldgates=[]
for b,loc,w in [('70862','enUS',True),('70888','enUS',True),('70938','enGB',True),('70939','enUS',False),('70938','frFR',False)]:g.build=b;g.locale=loc;assert f()==w;oldgates.append(dict(build=b,locale=loc,supported=w))
# Actual Tracker connect/wrappers with Questie absent then present; unchanged module.
t=LuaRuntime(unpack_returned_tuples=True);t.execute(fixture);t.globals().build='70938';ns=t.table()
for n in ['Catalog.lua','Match.lua','Atlas.lua']:load(t,ns,n)
t.execute('''
ForeverThaiQuestieTracker=true
function InCombatLockdown()return false end
C_AddOns={IsAddOnLoaded=function()return false end}
C_QuestLog={GetTitleForQuestID=function()return "The Balance of Nature"end,GetLogIndexForQuestID=function()return 1 end}
function GetQuestLogLeaderBoard()return "", "" end
''');load(t,ns,'Tracker.lua');assert ns.SetQuestieTrackerThai(True)==False
assert ns.Translate(ns.quests[456].title,'The Balance of Nature')=='สมดุลแห่งธรรมชาติ'
t.execute('''
updates=0;Questie={db={profile={trackerFontSizeQuest=16,trackerFontSizeObjective=16}}}
lines={AddTitle=function(o)return o end,AddObjective=function(o)return o end}
data={GetObjectiveText=function(o)return o.Description end};qtracker={Update=function()updates=updates+1 end}
QuestieLoader={ImportModule=function(_,n)if n=="QuestieTracker"then return qtracker elseif n=="TrackerData"then return data else return lines end end}
C_AddOns.IsAddOnLoaded=function(n)return n=="Questie"end
''');assert ns.SetQuestieTrackerThai(True)==True
t.execute('''
original={clickMode="quest",target={Id=456,name="The Balance of Nature"},text="The Balance of Nature"}
translated=lines.AddTitle(original)
assert(original.text=="The Balance of Nature" and translated.text~=original.text and translated.text:find("|T",1,true))
''');ns.SetQuestieTrackerThai(False);t.execute('assert(lines.AddTitle(original).text==original.text)');ns.SetQuestieTrackerThai(True);t.globals().secretInput=t.globals().SECRET;t.execute('local o={clickMode="quest",target={Id=456,name=secretInput},text="The Balance of Nature"};assert(lines.AddTitle(o).text==o.text)')
# Native tracker present with Questie absent: exact actual AnchorBlock/SetStringText hook.
t.execute("""
QuestieLoader=nil;nativeUpdates=0
function hooksecurefunc(object,key,callback)
 local original=object[key];object[key]=function(self,...)local value=original(self,...);callback(self,...);return value end
end
QuestObjectiveTracker={AnchorBlock=function()end,MarkDirty=function()nativeUpdates=nativeUpdates+1 end}
label={text="The Balance of Nature"}
function label:GetFont()return "Default",16 end
function label:GetTextColor()return 1,1,1 end
function label:GetHeight()return 18 end
function label:SetText(text)self.text=text end
function label:IsTruncated()return false end
block={id=456,parentModule=QuestObjectiveTracker,usedLines={},HeaderText=label,SetStringText=function(_,font,text)font:SetText(text)end}
""");assert ns.SetQuestieTrackerThai(True)==True
t.execute('QuestObjectiveTracker:AnchorBlock(block);block:SetStringText(label,"The Balance of Nature");assert(label.text:find("|T",1,true))')
ns.SetQuestieTrackerThai(False);t.execute('block:SetStringText(label,"The Balance of Nature");assert(label.text=="The Balance of Nature")')
ns.SetQuestieTrackerThai(True);t.execute('C_QuestLog.GetTitleForQuestID=function()return SECRET end;block:SetStringText(label,"The Balance of Nature");assert(label.text=="The Balance of Nature")')
# Only the two old Perception screenshots required by the Launcher receipt, not old9suite.
import legacy_skill_runner as legacy
sys.path.insert(0,str(legacy.RECOVERED/'tests'));import test_recipe_panel
import tempfile
tmp=tempfile.TemporaryDirectory();z.extractall(pathlib.Path(tmp.name)/'addon');test_recipe_panel.ROOT=pathlib.Path(tmp.name)
fixture_case=test_recipe_panel.RecipePanelTests();fixture_case.setUp();p=fixture_case.lua
legacy_ast=ast.parse((ROOT/'tools/legacy_skill_runner.py').read_text());check=next(n for n in legacy_ast.body if isinstance(n,ast.FunctionDef) and n.name=='check');constants=[n.value for n in ast.walk(check) if isinstance(n,ast.Constant) and isinstance(n.value,str)];init=next(s for s in constants if 'addon={};frames={};SlashCmdList' in s).replace('"70888"','"70938"');p.execute(init);ad=p.globals().addon
for name in legacy.modules(z.read('ForeverThai/ForeverThai.toc').decode()):p.execute(z.read('ForeverThai/'+name).decode(),'ForeverThai',ad)
p.execute('event("ADDON_LOADED","ForeverThai");S=addon.skills;assert(S.supported and S.settings.fontSize==19)')
p.execute("Enum={TooltipDataType={Item=0,Spell=1},TooltipDataLineType={SpellDescription=34}}")
perception=next(s for s in constants if 'local build, locale = "70862"' in s);p.execute(perception)
report=dict(status='passed',candidate_sha256=sha(archive.read_bytes()),build='70938',speech_unique_templates=16,speech_positive_executions=pos,speech_negative_executions=neg,speech_timer_passed=True,speech_old_build_gate_checks=oldgates,quest_title70938=True,tracker_questie_absent_safe=True,tracker_questie_present_actual_bitmap_markup=True,native_tracker_actual_bitmap_markup_without_questie=True,tracker_settings_and_secret_failclosed=True,perception_screenshot_builds=['70862','70888'],perception_old_replay_scope='Two narrow exact original action-tooltip screenshot cases on this ZIP, required receipt fields; not old nine-case/full suite.',scope='Focused changed70938Speech path plus Quest/optionalQuestie and required receipt compatibility. No686/full fonts/source audits or game proof.')
(ROOT/'evidence/compat70938-paths.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
