"""Only new main16 fields: static full-body oracles, mutations and runtime byte preservation."""
import pathlib,json,hashlib,subprocess
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';BASE='d0fc7a8631016ef4d8687c153656af96e7950f48'
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
prior=git('show',BASE+':src/ForeverThai/Catalog.lua');current=(RUN/'Catalog.lua').read_bytes();assert current.startswith(prior)
lua=LuaRuntime(unpack_returned_tuples=True);a=lua.table();old=lua.table()
for target,cat in [(a,current),(old,prior)]:
 lua.execute(cat.decode(),'ForeverThai',target);lua.execute((RUN/'Match.lua').read_text(),'ForeverThai',target)
unchanged=0
for path in git('ls-tree','-r','--name-only',BASE,'src/ForeverThai').decode().splitlines():
 if path.endswith('/Catalog.lua'):continue
 assert (ROOT/path).read_bytes()==git('show',BASE+':'+path),path;unchanged+=1
cases=json.loads((ROOT/'tests/main16-cases.json').read_text())['cases'];fields=json.loads((ROOT/'evidence/main16-translations.json').read_text())['fields'];assert len(cases)==len(fields)==9
positive=negative=0
for case in cases:
 q,f=case['quest_id'],case['field'];lua.globals().UnitName=lambda *_:case['name'];lua.globals().UnitClass=lambda *_:(case['class_name'],'DRUID');lua.globals().UnitRace=lambda *_:case['race']
 entry=a.quests[q][f];assert old.Translate(old.quests[q][f],case['english']) is None,(q,f,'already supported')
 assert a.Translate(entry,case['english'])==case['expected'],q;positive+=1
 variant=entry.variants[len(entry.variants)] if entry.variants else entry
 for bad in [case['english']+' Extra instruction.', 'Changed instruction. '+case['english']]:
  assert a.Translate(variant,bad) is None,q;negative+=1
 if q in [7632,8160]:
  assert a.Translate(variant,case['english'].replace('Nira','UnrelatedPlayer')) is None;negative+=1
  lua.globals().UnitName=lambda *_:'Nira-Realm'
  assert a.Translate(variant,case['english']) is None;negative+=1
 if q==4602:
  assert a.Translate(variant,case['english'].replace('three silver','four silver')) is None;negative+=1
 if q==97184:
  assert a.Translate(variant,case['english'].replace('Danitha Morr','Eldrun Stormbreaker')) is None;negative+=1
# Exact raw own-ID English and quantities from the pinned review evidence.
for x in fields:
 assert hashlib.sha256(x['english'].encode()).hexdigest()==x['english_sha256']
 assert hashlib.sha256(x['thai'].encode()).hexdigest()==x['thai_sha256']
 if x['quest_id']==97184:assert [(o['objectId'],o['amount']) for o in x['source_record']['objectives']]==[(12800,1),(18335,1)]
 if x['quest_id']==97169:assert 'Eldrun Stormbreaker' in x['source_record']['objectivesText'] and 'Ironforge' in x['source_record']['objectivesText']
report=dict(status='passed',baseline_source=BASE,catalog_sha256=hashlib.sha256(current).hexdigest(),old_catalog_exact_byte_prefix_preserved=True,unchanged_other_runtime_files=unchanged,unique_source_cases=9,independent_static_oracles=9,positive_executions=positive,negative_executions=negative,new_thai_fields=6,reused_thai_fields=3,newly_supported_fields=9,unique_quest_ids=9,fonts_rebuilt=False,version_changed=False,root_wording_review='pending',scope='Affected MAIN data-only Lua5.1 checks. No686/Skills/party/full-font suites or in-game proof.')
(ROOT/'evidence/main16-regression.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
