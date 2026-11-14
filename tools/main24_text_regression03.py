"""Only42new approved02 cases; old38 proof reused, prior bytes/canonical values preserved."""
import pathlib,json,re,subprocess,hashlib
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];RUN=R/'src/ForeverThai';BASE='e2d39553edd3c73b7adc6453927233fecde80221';b=json.loads((R/'evidence/main24-proposal03.json').read_text());l=LuaRuntime(unpack_returned_tuples=True);a=l.table();old=l.table();sha=lambda v:hashlib.sha256(v).hexdigest();before=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/Catalog.lua']);now=(RUN/'Catalog.lua').read_bytes();assert now.startswith(before) and sha(before)==b['integrated_prior_Catalog_sha256']
for n in ['Catalog','Match']:
 l.execute((RUN/f'{n}.lua').read_text(),'ForeverThai',a);l.execute(subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']).decode(),'ForeverThai',old)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end;SECRET={};issecretvalue=function(v)return v==SECRET end');g=l.globals();pos=neg=0;oracles=[];canonical=0
for f in b['fields']:
 q,key,th=f['quest_id'],f['field'],f['thai'];ui=re.sub(r'\$[Bb]','\n',f['english']);assert sha(f['english'].encode())==f['english_sha256'] and sha(th.encode())==f['thai_sha256'];assert a.Translate(a.quests[q][key],ui)==th;pos+=1
 if old.quests[q] and old.quests[q][key]:
  beforeentry=old.quests[q][key];entry=a.quests[q][key]
  # Old signatures/Thai remain; added signatures are variants, not canonical overwrites.
  assert entry[2]==beforeentry[2]
  if isinstance(beforeentry[1],str):assert entry[1]==beforeentry[1]
  else:
   for i,s in beforeentry[1].items():assert entry[1][i]==s
  if beforeentry.variants:
   for i,v in beforeentry.variants.items():assert entry.variants[i][1]==v[1] and entry.variants[i][2]==v[2]
  canonical+=1
 for bad in [ui+' changed',None,g.SECRET]:assert a.Translate(a.quests[q][key],bad) is None;neg+=1
 other={'quest_id':94233} if key=='completion' else next(c for c in b['fields'] if c['field']==key and c['quest_id']!=q and ' '.join(re.sub(r'\$[Bb]','\n',c['english']).split())!=' '.join(ui.split()));assert a.Translate(a.quests[other['quest_id']][key],ui) is None;neg+=1
 wrong='objective' if key=='description' else 'description';assert a.Translate(a.quests[q][wrong],ui) is None;neg+=1
 oracles.append(dict(quest_id=q,field=key,wrong_known_quest_id=other['quest_id'],wrong_field=wrong,english_sha256=f['english_sha256'],thai_sha256=f['thai_sha256']))
assert pos==42 and neg==210
paths=subprocess.check_output(['git','-C',str(R),'ls-tree','-r','--name-only',BASE+':src/ForeverThai'],text=True).splitlines();actual=set(p.relative_to(RUN).as_posix() for p in RUN.rglob('*') if p.is_file());assert len(paths)==141 and set(paths)<=actual;added=sorted(actual-set(paths));assert all(re.fullmatch(r'Fonts/Thai[0-9]+.tga',p) for p in added);unchanged=0
for path in paths:
 if path=='Catalog.lua':continue
 if path=='Atlas.lua':
  assert (RUN/path).read_bytes().startswith(subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+path]));continue
 assert (RUN/path).read_bytes()==subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+path]);unchanged+=1
priorcases=[f for n in [1,2] for f in json.loads((R/f'evidence/main24-proposal0{n}.json').read_text())['fields']];assert {(f['quest_id'],f['field']) for f in priorcases}.isdisjoint({(f['quest_id'],f['field']) for f in b['fields']})
assert a.quests[2752].progress[1]==old.quests[2752].progress[1] and a.quests[2752].progress[2]==old.quests[2752].progress[2]
for i,v in old.quests[94233].progress.variants.items():assert a.quests[94233].progress.variants[i][1]==v[1] and a.quests[94233].progress.variants[i][2]==v[2]
report=dict(status='PASSED_SOURCE_INTEGRATED122_TEXT_ONLY_PENDING_BITMAP_FONTS',baseline_source=BASE,unique_affected03_cases=42,positive_executions=pos,negative_executions=neg,independent_negative_attribution_oracles=oracles,wrongphase_selection='Fixed description→objective; title/objective→description. Not selected by matcher outcome.',existing_canonical_slots_preserved=canonical,old_Catalog_prefix_preserved=True,prior80_matching_rerun=False,prior80_field_keys_disjoint_from42=True,MAIN21_and2752_preserved=True,unchanged_other_runtime_files=unchanged,runtime_files=len(actual),baseline_runtime_files=141,old_Atlas_prefix_preserved=True,authorized_added_font_pages=added,protected28_CoreSpeech70938_Questie_settings_fonts='139nonCatalog/nonAtlas files byte-identical, oldAtlas prefix retained; append-only fonts separately checked',final_Catalog_sha256=sha(now),font_append_preceded_final_fixture_completion=True,initial_fixture_issue='Only one completion source case; fixed independent wrongknownQuestID94233, no engine/runtime text change',fonts_bitmap_build_ZIP_game_checks=False,old_suites_rerun=False)
(R/'evidence/main24-text-regression03.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='independent_negative_attribution_oracles'},indent=2))
