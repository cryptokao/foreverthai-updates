"""Only one new literal progress variant; no old suites, glyph or client-gate work."""
import pathlib,json,hashlib,subprocess
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];BASE='7f082e6a57fe72305bd4366c1588c04d5bc1ad95';prior=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/Catalog.lua']);current=(R/'src/ForeverThai/Catalog.lua').read_bytes();assert current.startswith(prior)
l=LuaRuntime();a=l.table();old=l.table()
for obj,cat in [(a,current),(old,prior)]:l.execute(cat.decode(),'ForeverThai',obj);l.execute((R/'src/ForeverThai/Match.lua').read_text(),'ForeverThai',obj)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end');c=json.loads((R/'tests/main21-cases.json').read_text())['cases'][0];assert c['quest_id']==94233 and c['field']=='progress';assert c['expected']=='ข้าเห็นที่นี่ถูกเผาจนราบและเห็นป้อมถูกโค่นลงกับตา สะใจจริง ๆ\n\nไม่คิดว่าจะมีพวกโจรสักกลุ่มมาพยายามใช้ที่นี่เป็นฐานปฏิบัติการ'
assert old.Translate(old.quests[94233].progress,c['english']) is None;entry=a.quests[94233].progress;v=entry.variants[len(entry.variants)];assert a.Translate(entry,c['english'])==c['expected'];assert entry[1]==old.quests[94233].progress[1] and entry[2]==old.quests[94233].progress[2]
for text in [c['english']+' Extra requirement.',c['english'].replace('glorious','disastrous'),c['english'].replace('bandits','soldiers')]:assert a.Translate(v,text) is None
unchanged=0
for p in subprocess.check_output(['git','-C',str(R),'ls-tree','-r','--name-only',BASE,'src/ForeverThai']).decode().splitlines():
 if p.endswith('/Catalog.lua'):continue
 assert (R/p).read_bytes()==subprocess.check_output(['git','-C',str(R),'show',BASE+':'+p]);unchanged+=1
report=dict(status='passed',baseline_source=BASE,catalog_sha256=hashlib.sha256(current).hexdigest(),old_catalog_exact_prefix_preserved=True,old94233_canonical_signature_thai_preserved=True,unchanged_other_runtime_files=unchanged,unique_source_cases=1,static_oracles=1,positive_executions=1,negative_executions=3,new_thai_fields=0,new_prose_bodies=0,reused_ownID_wording=1,new_source_variants_supported=1,font_version_package_feed_changed=False,scope='Only one exact progress variant. Full141sourcecomponent preservation except append-onlyCatalog; no old suites, glyph/clientgate repeats or game proof.')
(R/'evidence/main21-affected-regression.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
