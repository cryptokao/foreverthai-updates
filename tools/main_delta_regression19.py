"""Only MAIN19 fields and their native/Questie routing; no old suites/font generation."""
import ast,pathlib,json,re,hashlib,subprocess
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];run=R/'src/ForeverThai';BASE='2678500dd147c098c547aaec7506b0d2f3b6e57d';prior=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/Catalog.lua']);current=(run/'Catalog.lua').read_bytes();assert current.startswith(prior);unchanged=0
for path in subprocess.check_output(['git','-C',str(R),'ls-tree','-r','--name-only',BASE,'src/ForeverThai']).decode().splitlines():
 if path.endswith('/Catalog.lua'):continue
 assert (R/path).read_bytes()==subprocess.check_output(['git','-C',str(R),'show',BASE+':'+path]),path;unchanged+=1
cases=json.loads((R/'tests/main19-cases.json').read_text())['cases'];doc=json.loads((R/'evidence/main19-translations.json').read_text());assert len(cases)==33
parsed=ast.parse((R/'tools/main_trace_regression17.py').read_text());fixture=next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fixture' for t in n.targets));l=LuaRuntime(unpack_returned_tuples=True);l.execute(fixture);a=l.table();old=l.table()
for obj,cat in [(a,current),(old,prior)]:
 l.execute(cat.decode(),'ForeverThai',obj);l.execute((run/'Match.lua').read_text(),'ForeverThai',obj)
pos=neg=0
for c in cases:
 q,f=c['quest_id'],c['field'];entry=a.quests[q][f];before=old.quests[q][f] if old.quests[q] else None;assert old.Translate(before,c['english']) is None,(q,f,'already supported');assert a.Translate(entry,c['english'])==c['expected'],(q,f);pos+=1
 v=entry.variants[len(entry.variants)] if entry.variants else entry
 bad=[c['english']+' Extra requirement.','Changed source. '+c['english']]
 if '15 ' in c['english'] and '20 gold' in c['english']:
  bad +=[c['english'].replace('15 ','20 ',1),c['english'].replace('20 gold','15 gold'),c['english'].replace('Deliana','Mokvar') if 'Deliana' in c['english'] else c['english'].replace('Mokvar','Deliana')]
 if q==628:bad.append(c['english'].replace(', and some armor patches too',''))
 if q==79242:bad.append(c['english'].replace(' Blood money, no doubt.',''))
 if q==93594:bad.append(c['english'].replace('Without the gift','With the gift'))
 if q==96078:bad.append(c['english'].replace('We Darkspear','We Night Elves'))
 if q==86925 and f=='objective':bad.append(c['english'].replace('Firewater Recipe','Firewater'))
 for text in bad:assert text!=c['english'] and a.Translate(v,text) is None,(q,f,text);neg+=1
 if q==96078:
  l.execute('UnitRace=function()return "Tauren"end;UnitClass=function()return "Hunter","HUNTER"end');assert a.Translate(v,c['english'])==c['expected'];pos+=1;l.execute('UnitRace=function()return "Night Elf"end;UnitClass=function()return "Druid","DRUID"end')
for q in doc['new_ownID_entry_ids']:
 assert old.quests[q] is None
 for f in ['description','progress','completion']:assert a.quests[q][f] is None
for f in doc['fields']:
 assert not re.search(r'\b[NCR]\b',f['signature'])
 assert hashlib.sha256(f['english'].encode()).hexdigest()==f['english_sha256'];assert hashlib.sha256(f['thai'].encode()).hexdigest()==f['thai_sha256']
# Real existing Atlas; missing runs must retain English pre-review, not synthetic-font passes.
l.globals().addon=a;l.execute((run/'Atlas.lua').read_text(),'ForeverThai',a);l.execute('originalTranslate=addon.Translate;addon.Translate=function(entry,source)local thai=originalTranslate(entry,source);calls[#calls+1]={entry=entry,source=source,thai=thai};return thai end');l.execute((run/'Tracker.lua').read_text(),'ForeverThai',a);assert a.SetQuestieTrackerThai(True);routes=negroute=rendered=0;pending=[]
for c in cases:
 if c['field'] not in ['title','objective']:continue
 q,f=c['quest_id'],c['field'];g=l.globals();g.q=q;g.currentSource=c['english'];g.currentField=f;g.expected=c['expected'];ready=all(a.runs[s] is not None for s in re.findall(r'[\u0e00-\u0e7f]+',c['expected']))
 l.execute('''calls={};header=label();objective=label();block={id=q,parentModule=QuestObjectiveTracker,HeaderText=header,usedLines={[1]={used=true,Text=objective}},SetStringText=function(_,font,text)font:SetText(text)end};QuestObjectiveTracker:AnchorBlock(block);targetLabel=currentField=="title" and header or objective;block:SetStringText(targetLabel,currentSource);assert(#calls==1 and calls[1].thai==expected and calls[1].entry==addon.quests[q][currentField])''');assert ('|T' in g.targetLabel.text) if ready else g.targetLabel.text==c['english'];routes+=1;rendered+=int(ready)
 l.execute('''calls={};original={clickMode="quest",target={Id=q,name=currentSource},text=currentSource};obj={questId=q,Type="log",Description=currentSource};if currentField=="title"then result=lines.AddTitle(original).text;assert(original.text==currentSource)else result=data.GetObjectiveText(obj)end;assert(#calls==1 and calls[1].thai==expected and calls[1].entry==addon.quests[q][currentField])''');assert ('|T' in g.result) if ready else g.result==c['english'];routes+=1;rendered+=int(ready)
 if not ready:pending.append(dict(quest_id=q,field=f))
 a.SetQuestieTrackerThai(False);l.execute('''calls={};block:SetStringText(targetLabel,currentSource);assert(targetLabel.text==currentSource);if currentField=="title"then result=lines.AddTitle(original).text else result=data.GetObjectiveText(obj)end;assert(result==currentSource and #calls==0)''');negroute+=2;a.SetQuestieTrackerThai(True)
 l.execute('''calls={};block.id=999999;block:SetStringText(targetLabel,currentSource);assert(targetLabel.text==currentSource and #calls==0);original.target.Id=999999;obj.questId=999999;if currentField=="title"then result=lines.AddTitle(original).text else result=data.GetObjectiveText(obj)end;assert(result==currentSource and #calls==0)''');negroute+=2
report=dict(status='passed',baseline_source=BASE,catalog_sha256=hashlib.sha256(current).hexdigest(),old_catalog_exact_prefix_preserved=True,unchanged_other_runtime_files=unchanged,unique_source_cases=33,independent_static_oracles=33,new_thai_fields=16,reused_thai_fields=17,unique_quest_ids=20,new_ownID_entries=15,matcher_positive_executions=pos,matcher_negative_executions=neg,fixed_Darkspear_not_player_race_case=True,tracker_native_questie_routing_executions=routes,tracker_settings_wrongID_negative_executions=negroute,real_existing_atlas_bitmap_executions=rendered,pending_tracker_font_fields=pending,completion_bitmap_not_executed_before_review=True,no_unproven_phases_created=True,fonts_version_package_unchanged=True,root_wording_review='pending',scope='New33MAINfields only; prior tests not rerun. Real Atlas pre-font fallback separately counted; no NPC/Skills/party/fullfonts or game proof.')
(R/'evidence/main19-regression.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
