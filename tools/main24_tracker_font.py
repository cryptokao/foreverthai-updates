"""Affected89 title/objective native+Questie render routes using actual unchanged Tracker/Atlas."""
import ast,json,pathlib,re,hashlib
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];RUN=R/'src/ForeverThai';cases=[f for n in [1,2,3] for f in json.loads((R/f'evidence/main24-proposal0{n}.json').read_text())['fields'] if f['field'] in ['title','objective']];assert len(cases)==89
parsed=ast.parse((R/'tools/main_trace_regression17.py').read_text());fixture=next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fixture' for t in n.targets));l=LuaRuntime(unpack_returned_tuples=True);l.execute(fixture);a=l.table();l.globals().addon=a
for n in ['Catalog','Match','Atlas','Tracker']:l.execute((RUN/f'{n}.lua').read_text(),'ForeverThai',a)
assert a.SetQuestieTrackerThai(True);positive=negative=bitmap=passthrough=guarded=0
for f in cases:
 g=l.globals();g.q=f['quest_id'];g.currentSource=re.sub(r'\$[Bb]','\n',f['english']);g.currentField=f['field'];isThai=bool(re.search(r'[\u0e00-\u0e7f]',f['thai']))
 l.execute('''header=label();objective=label();block={id=q,parentModule=QuestObjectiveTracker,HeaderText=header,usedLines={[1]={used=true,Text=objective}},SetStringText=function(_,font,text)font:SetText(text)end};QuestObjectiveTracker:AnchorBlock(block);targetLabel=currentField=="title" and header or objective;block:SetStringText(targetLabel,currentSource);original={clickMode="quest",target={Id=q,name=currentSource},text=currentSource};obj={questId=q,Type="log",Description=currentSource};if currentField=="title"then result=lines.AddTitle(original).text;assert(original.text==currentSource)else result=data.GetObjectiveText(obj)end''')
 for value in [g.targetLabel.text,g.result]:
  if f['quest_id']==84213 and f['field']=='objective':
   assert '\n' in f['thai'] and value==g.currentSource and '|T' not in value;guarded+=1
  elif isThai:assert '|T' in value,(f['quest_id'],f['field'],value==g.currentSource,len(value),positive);bitmap+=1
  else:assert value==g.currentSource;passthrough+=1
  positive+=1
 a.SetQuestieTrackerThai(False);l.execute('''block:SetStringText(targetLabel,currentSource);assert(targetLabel.text==currentSource);if currentField=="title"then result=lines.AddTitle(original).text else result=data.GetObjectiveText(obj)end;assert(result==currentSource)''');negative+=2;a.SetQuestieTrackerThai(True)
 l.execute('''block.id=99999999;original.target.Id=99999999;obj.questId=99999999;block:SetStringText(targetLabel,currentSource);assert(targetLabel.text==currentSource);if currentField=="title"then result=lines.AddTitle(original).text else result=data.GetObjectiveText(obj)end;assert(result==currentSource)''');negative+=2
r=dict(status='PASSED_AFFECTED_ROUTES_WITH_ONE_EXISTING_MULTILINE_SAFE_FALLBACK',unique_title_objective_fields=89,client_build_fixture='70938',native_Questie_positive_executions=positive,Thai_bitmap_markup_executions=bitmap,Latin_propername_passthrough_executions=passthrough,multiline_safeguard_English_executions=guarded,multiline_safeguard_fields=[dict(quest_id=84213,field="objective",reason="unchanged bitmapMarkup rejects newline; wholetextpanel bitmap verified separately; no engine change")],settings_off_wrongID_negative_executions=negative,synthetic_glyphs=False,actual_current_Atlas=True,unexpected_missing_glyph_fallbacks=0,known_multiline_English_fallback_fields=1,Catalog_sha256=hashlib.sha256((RUN/'Catalog.lua').read_bytes()).hexdigest(),Tracker_runtime_changed=False,old_matcher_Skill_NPC_party_suites_rerun=False,game_verified=False)
(R/'evidence/main24-tracker-font.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
