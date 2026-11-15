"""Only newly typed8315objective callbacks, with/without optional Questie. No old suite."""
import ast,pathlib,json,re,zipfile,hashlib
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.469.0'
t=ast.parse((R/'trace_fixture_source.py').read_text(encoding='utf-8'));fixture=next(ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='fixture' for x in n.targets))
f=next(v for v in json.loads((R.parent/'main27-reviewed-pairs.json').read_text(encoding='utf-8'))['fields'] if v['quest_id']==8315)
rows=[]
for optional in [True,False]:
 l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');l.execute(fixture)
 if not optional:l.execute('Questie=nil;QuestieLoader=nil;C_AddOns={IsAddOnLoaded=function()return false end}')
 a=l.table();l.globals().addon=a
 with zipfile.ZipFile(O/'ForeverThai-0.469.0-main27-PRIVATE-TEST.zip') as z:
  for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','Match.lua','Atlas.lua','AtlasMain2526.lua','AtlasMain27.lua','Tracker.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
 l.globals().currentSource=re.sub(r'\$[nN]','Nira',re.sub(r'\$[Bb]','\n',f['english']));l.globals().q=8315
 assert a.Translate(a.quests[8315].objective,l.globals().currentSource)==f['thai'].replace('{name}','Nira')
 a.SetQuestieTrackerThai(True)
 l.execute('''header=label();objective=label();block={id=q,parentModule=QuestObjectiveTracker,HeaderText=header,usedLines={[1]={used=true,Text=objective}},SetStringText=function(_,font,text)font:SetText(text)end};QuestObjectiveTracker:AnchorBlock(block);block:SetStringText(objective,currentSource);assert(objective.text==currentSource)''')
 tested=1
 if optional:
  l.execute('obj={questId=q,Type="log",Description=currentSource};assert(data.GetObjectiveText(obj)==currentSource)');tested+=1
 a.SetQuestieTrackerThai(False);l.execute('block:SetStringText(objective,currentSource);assert(objective.text==currentSource)');off=1
 if optional:l.execute('assert(data.GetObjectiveText(obj)==currentSource)');off+=1
 a.SetQuestieTrackerThai(True);l.execute('block.id=99999999;block:SetStringText(objective,currentSource);assert(objective.text==currentSource)');wrong=1
 if optional:l.execute('obj.questId=99999999;assert(data.GetObjectiveText(obj)==currentSource)');wrong+=1
 rows.append(dict(optional_Questie_present=optional,native_Questie_English_multiline_guard_callbacks=tested,settings_off_callbacks=off,wrongID_callbacks=wrong))
report=dict(status='PASSED_8315_NEW_OBJECTIVE_ALIAS_WITH_EXISTING_TRACKER_SAFE_FALLBACK',field=dict(quest_id=8315,field='objective'),full_panel_template_Thai=True,Tracker_Thai=False,reason='Existing bitmapMarkup rejects multiline; native callbacks retain English with and without optionalQuestie. No engine change.',rows=rows,old_suite_rerun=False,real_game_verified=False)
(O/'tracker-8315-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report,indent=2))
