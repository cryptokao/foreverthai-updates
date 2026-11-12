"""Only the Root-edited2881 case; unchanged five cases use their prior scoped report."""
import pathlib,json,hashlib,subprocess
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';prior='42fc950';tree='f85a68ca9c2ade231310620e693765cd99eebfc1';sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','-C',str(ROOT),'show',prior+':'+p])
d=json.loads((ROOT/'evidence/main-semantic-15.json').read_text());previous=json.loads(old('evidence/main-semantic-15.json'));oldfixtures=json.loads(old('tests/main-semantic-cases15.json'));fixtures=json.loads((ROOT/'tests/main-semantic-cases15.json').read_text());final=json.loads((ROOT/'evidence/root-main15-review.json').read_text())['wording_change']['final_thai'];r=next(r for r in d['fields'] if r['quest_id']==2881);before=next(r for r in previous['fields'] if r['quest_id']==2881)
assert r['thai']==final;assert [r for r in d['fields'] if r['quest_id']!=2881]==[r for r in previous['fields'] if r['quest_id']!=2881]
assert [r for r in fixtures['cases'] if r['quest_id']!=2881]==[r for r in oldfixtures['cases'] if r['quest_id']!=2881]
raw=(RUN/'Catalog.lua').read_bytes();assert raw==old('src/ForeverThai/Catalog.lua').replace(json.dumps(before['thai'],ensure_ascii=False).encode(),json.dumps(final,ensure_ascii=False).encode())
base=subprocess.check_output(['git','-C',str(ROOT),'show',tree+':Catalog.lua']);assert raw.startswith(base)
l=LuaRuntime(unpack_returned_tuples=True);a=l.table();load=l.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for n in ['Catalog','Match']:load((RUN/f'{n}.lua').read_text(),a)
c=next(c for c in fixtures['cases'] if c['quest_id']==2881);l.globals().UnitName=lambda *_:c['name'];l.globals().UnitClass=lambda *_:(c['class_name'],c['class_id']);l.globals().UnitRace=lambda *_:c['race'];e=a.quests[2881].completion.variants[1]
assert a.Translate(e,c['english'])==c['expected']==final.replace('{name}',c['name'])
for bad in [c['english']+' Extra source words.',c['english'].replace('Another set','One fewer set'),c['english'].replace('CloudTester','UnrelatedPlayer')]:assert a.Translate(e,bad) is None
report=dict(status='passed',root_review='b7b5124eb29bf144b5515344012cf0a1cc5d0553',quest_id=2881,field='completion',final_thai=final,final_thai_sha256=sha(final.encode()),final_catalog_sha256=sha(raw),affected_unique_source_cases=1,positive_executions=1,negative_executions=3,unchanged_five_pairs_and_oracles=True,prior_six_case_report='main-semantic-regression15.json',old_catalog_byte_prefix_preserved=True,scope='Only edited2881 executed; five unchanged fields/oracles retained by exact data comparison. Prior six-case report is not relabeled as a final-hash rerun. No unchanged NPC/Skills/party/full suite.')
(ROOT/'evidence/main-final-wording15.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['final_thai','scope']},indent=2))
