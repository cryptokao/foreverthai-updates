"""Apply Root's single628variant change and test only that affected case."""
import pathlib,json,hashlib,subprocess
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];p=R/'evidence/main19-translations.json';doc=json.loads(p.read_text());review=json.loads((R/'evidence/root-main19-wording-review.json').read_text());cases=json.loads((R/'tests/main19-cases.json').read_text());old=json.loads(subprocess.check_output(['git','-C',str(R),'show','ef31e01:evidence/main19-translations.json']))['fields'];approved={(v['quest_id'],v['field']):v for v in review['approved_unchanged']};cat=R/'src/ForeverThai/Catalog.lua';raw=cat.read_bytes()
for f in doc['fields']:
 if f['quest_id']==628:
  before=next(v for v in old if v['quest_id']==628)['thai'];after=review['requested_new_wording']['628'];needle=json.dumps(before,ensure_ascii=False).encode();assert raw.count(needle)==1;raw=raw.replace(needle,json.dumps(after,ensure_ascii=False).encode());f['thai']=after;f['thai_sha256']=hashlib.sha256(after.encode()).hexdigest();next(c for c in cases['cases'] if c['quest_id']==628)['expected']=after
 else:
  assert f==next(v for v in old if (v['quest_id'],v['field'])==(f['quest_id'],f['field']));a=approved[f['quest_id'],f['field']];assert f['english_sha256']==a['english_sha256'] and f['thai_sha256']==a['thai_sha256']
cat.write_bytes(raw);doc['root_wording_review']='approved main ef2d6a22; only628requested wording applied';p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');(R/'tests/main19-cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
l=LuaRuntime();a=l.table();base=l.table()
for obj,s in [(a,raw),(base,subprocess.check_output(['git','-C',str(R),'show','2678500:src/ForeverThai/Catalog.lua']))]:l.execute(s.decode(),'ForeverThai',obj)
l.execute((R/'src/ForeverThai/Match.lua').read_text(),'ForeverThai',a);l.execute('UnitName=function()return "Nira"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end');case=next(c for c in cases['cases'] if c['quest_id']==628);entry=a.quests[628].completion;variant=entry.variants[len(entry.variants)];assert a.Translate(entry,case['english'])==case['expected'];assert entry[2]==base.quests[628].completion[2]
for bad in [case['english']+' Extra requirement.',case['english'].replace(', and some armor patches too',''),case['english'].replace('take a pair','take three pairs')]:assert a.Translate(variant,bad) is None
report=dict(status='passed',root_review='main ef2d6a22',affected_unique_case=1,positive_executions=1,negative_executions=3,old628_canonical_preserved=True,other32pairs_byte_hash_preserved=True,all33English_hashes_preserved=True,catalog_sha256=hashlib.sha256(raw).hexdigest(),fields=[dict(quest_id=f['quest_id'],field=f['field'],english_sha256=f['english_sha256'],thai_sha256=f['thai_sha256']) for f in doc['fields']],scope='628variant only after review; previous33suite remains separate, not rerun.')
(R/'evidence/main19-final-text-hashes.json').write_text(json.dumps(report,indent=2)+'\n');print('628affected1positive/3negative passed;32pairs andold628canonical preserved;CatalogSHA',report['catalog_sha256'])
