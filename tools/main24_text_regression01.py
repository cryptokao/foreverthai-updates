"""Only38 approved additive fields: exact Thai, negative attribution, prior byte preservation."""
import pathlib,json,subprocess,hashlib,re
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];RUN=R/'src/ForeverThai';BASE='86c449ac6f01568edd3c79a7c48ddf80a4e7ca80';b=json.loads((R/'evidence/main24-proposal01.json').read_text());approved=json.loads((R/'evidence/root-main24-proposal01-review.json').read_text());sha=lambda v:hashlib.sha256(v).hexdigest();before=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/Catalog.lua']);now=(RUN/'Catalog.lua').read_bytes();assert now.startswith(before) and sha(before)==b['baseline_Catalog_sha256'];assert approved['fields_approved']==38
l=LuaRuntime(unpack_returned_tuples=True);a=l.table();old=l.table()
for n in ['Catalog','Match']:
 l.execute((RUN/f'{n}.lua').read_text(),'ForeverThai',a);l.execute(subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']).decode(),'ForeverThai',old)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end;SECRET={};issecretvalue=function(v)return v==SECRET end');g=l.globals();pos=neg=0;oracles=[]
for f in b['fields']:
 q,key,en,th=f['quest_id'],f['field'],f['english'],f['thai'];assert q!=2752 and (old.quests[q] is None or old.quests[q][key] is None);entry=a.quests[q][key];assert sha(en.encode())==f['english_sha256'] and sha(th.encode())==f['thai_sha256'];assert a.Translate(entry,en)==th;pos+=1
 for bad in [en+' changed',None,g.SECRET]:assert a.Translate(entry,bad) is None;neg+=1
 other=next(c for c in b['fields'] if c['field']==key and c['quest_id']!=q and ' '.join(c['english'].split())!=' '.join(en.split()));assert a.Translate(a.quests[other['quest_id']][key],en) is None;neg+=1
 wrongkey='objective' if key=='description' else 'description';assert a.Translate(a.quests[q][wrongkey],en) is None;neg+=1
 oracles.append(dict(quest_id=q,field=key,wrong_quest_id=other['quest_id'],wrong_field=wrongkey,english_sha256=f['english_sha256'],thai_sha256=f['thai_sha256']))
assert pos==38 and neg==190
# One direct preserved-value comparison, not oldmatching/gate/game suite reruns.
assert a.quests[2752].progress[1]==old.quests[2752].progress[1] and a.quests[2752].progress[2]==old.quests[2752].progress[2]
prior=old.quests[94233].progress.variants;current=a.quests[94233].progress.variants
for i,v in prior.items():assert current[i][1]==v[1] and current[i][2]==v[2]
paths=subprocess.check_output(['git','-C',str(R),'ls-tree','-r','--name-only',BASE+':src/ForeverThai'],text=True).splitlines();assert len(paths)==141;assert sorted(paths)==sorted(p.relative_to(RUN).as_posix() for p in RUN.rglob('*') if p.is_file());unchanged=0
for path in paths:
 if path=='Catalog.lua':continue
 assert (RUN/path).read_bytes()==subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+path]);unchanged+=1
report=dict(status='PASSED_SOURCE_INTEGRATED_TEXT_ONLY_PENDING_BITMAP_FONTS',baseline_source=BASE,unique_approved_source_cases=38,positive_executions=pos,negative_executions=neg,negative_types=['changedbody','nil','secret','wrong known questID','wrong field'],negative_oracles=oracles,old_Catalog_prefix_preserved=True,unchanged_runtime_files=unchanged,runtime_files=141,protected28_CoreSpeech70938_Questie_settings_fonts='all140nonCatalog runtime files byte-preserved',quest2752_canonical_preserved=True,MAIN21_variants_preserved=True,final_Catalog_sha256=sha(now),actual_bitmap_fonts_build_ZIP_game_checks=False,old_suites_rerun=False,source81781_location_discrepancy_retained=True)
(R/'evidence/main24-text-regression01.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='negative_oracles'},indent=2))
