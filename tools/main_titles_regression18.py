"""Only three new exact own-ID title fields and affected tracker routing; no font build."""
import ast,pathlib,json,subprocess,re,hashlib
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];run=R/'src/ForeverThai';BASE='f32eb64fec3047a288d1963c3476f97e2c4858af';prior=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/Catalog.lua']);current=(run/'Catalog.lua').read_bytes();assert current.startswith(prior);unchanged=0
for path in subprocess.check_output(['git','-C',str(R),'ls-tree','-r','--name-only',BASE,'src/ForeverThai']).decode().splitlines():
 if path.endswith('/Catalog.lua'):continue
 assert (R/path).read_bytes()==subprocess.check_output(['git','-C',str(R),'show',BASE+':'+path]);unchanged+=1
cases=json.loads((R/'tests/main18-cases.json').read_text())['cases'];assert [(c['quest_id'],c['english'],c['expected']) for c in cases]==[(91902,'A Sealed Crate','ลังปิดผนึก'),(86747,'Legashi Horns','เขาของ Legashi'),(93162,'Head of the Obliterator','ศีรษะของ Obliterator')]
parsed=ast.parse((R/'tools/main_trace_regression17.py').read_text());fixture=next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fixture' for t in n.targets));l=LuaRuntime(unpack_returned_tuples=True);l.execute(fixture);a=l.table();old=l.table()
for obj,cat in [(a,current),(old,prior)]:
 l.execute(cat.decode(),'ForeverThai',obj);l.execute((run/'Match.lua').read_text(),'ForeverThai',obj)
pos=neg=0
for c in cases:
 q=c['quest_id'];assert old.quests[q] is None;assert a.Translate(a.quests[q].title,c['english'])==c['expected'];pos+=1
 for f in ['objective','description','progress','completion']:assert a.quests[q][f] is None
 for text in [c['english']+' Extra title','Changed '+c['english']]:assert a.Translate(a.quests[q].title,text) is None;neg+=1
l.globals().addon=a
for n in ['Atlas','Tracker']:l.execute((run/f'{n}.lua').read_text(),'ForeverThai',a)
assert a.SetQuestieTrackerThai(True);routes=negroute=rendered=0;pending=[]
for c in cases:
 g=l.globals();g.q=c['quest_id'];g.currentSource=c['english'];ready=all(a.runs[s] is not None for s in re.findall(r'[\u0e00-\u0e7f]+',c['expected']))
 l.execute('''header=label();block={id=q,parentModule=QuestObjectiveTracker,HeaderText=header,usedLines={},SetStringText=function(_,font,text)font:SetText(text)end};QuestObjectiveTracker:AnchorBlock(block);block:SetStringText(header,currentSource);original={clickMode="quest",target={Id=q,name=currentSource},text=currentSource};result=lines.AddTitle(original).text;assert(original.text==currentSource)''')
 if ready:assert '|T' in g.header.text and '|T' in g.result;rendered+=2
 else:assert g.header.text==g.result==c['english'];pending.append(c['quest_id'])
 routes+=2;a.SetQuestieTrackerThai(False);l.execute('block:SetStringText(header,currentSource);assert(header.text==currentSource and lines.AddTitle(original).text==currentSource)');negroute+=2;a.SetQuestieTrackerThai(True)
 l.execute('block.id=999999;original.target.Id=999999;block:SetStringText(header,currentSource);assert(header.text==currentSource and lines.AddTitle(original).text==currentSource)');negroute+=2
report=dict(status='passed',baseline_source=BASE,catalog_sha256=hashlib.sha256(current).hexdigest(),old_catalog_exact_prefix_preserved=True,unchanged_other_runtime_files=unchanged,unique_source_cases=3,new_thai_fields=2,reused_thai_fields=1,independent_static_oracles=3,positive_executions=pos,negative_executions=neg,tracker_native_questie_routing_executions=routes,tracker_settings_wrongID_negative_executions=negroute,real_existing_atlas_bitmap_executions=rendered,pending_font_ids=pending,no_other_phases_or_levels_created=True,fonts_version_package_unchanged=True,scope='Only3new literal title cases after single bounded trace join. No repeated full join/source scan, old suites or game execution.')
(R/'evidence/main18-regression.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
