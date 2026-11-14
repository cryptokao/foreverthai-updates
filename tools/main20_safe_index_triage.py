"""One safe metadata-only title/gap comparison; no host fetch, body import or runtime mutation."""
import json,pathlib,hashlib,subprocess,collections
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parents[1];P=R/'source_inputs/warcraftforever-beta-index20-safe.json';raw=P.read_bytes();doc=json.loads(raw);rows=doc['quests'];assert len(rows)==1609;assert len({q['id'] for q in rows})==1609
assert all(set(q)=={'id','title','level','logged'} for q in rows);assert collections.Counter(q['logged'] for q in rows)=={True:496,False:1113}
BASE='7f082e6a57fe72305bd4366c1588c04d5bc1ad95';l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:
 data=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']);assert data==(R/'src/ForeverThai'/f'{n}.lua').read_bytes();l.execute(data.decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
counts=collections.Counter({"logged_true_title_supported":0,"logged_true_title_unmatched":0,"logged_false_title_supported":0,"logged_false_title_unmatched":0});unmatched=[];gaps=[];excluded=[];phasecounts=collections.Counter()
for q in rows:
 id=q['id'];quest=a.quests[id];entry=quest.title if quest else None;matched=a.Translate(entry,q['title']) is not None;counts[('logged_true' if q['logged'] else 'logged_false')+('_title_supported' if matched else '_title_unmatched')]+=1
 marker=classify_title(q['title'],id)
 if q['title'].lower().startswith('jktestquest'):marker='explicit_developer_test_label'
 record=dict(q,runtime_quest_present=quest is not None,runtime_title_present=entry is not None,title_actualTranslate_supported=matched,missing_main_fields=[f for f in ['objective','description','progress','completion'] if quest is None or quest[f] is None],eligibility='beta observed-metadata only, current enabled status unproven',priority_proof='No class/race inferred from title/reader identity')
 if marker:record['excluded_reason']=marker;excluded.append(record)
 if not matched:unmatched.append(record)
 if q['logged'] and record['missing_main_fields']:
  phasecounts.update(record['missing_main_fields']);gaps.append(record)
report=dict(scope='Exactly1609sanitized metadata rows; one actualTranslate title comparison only. Missing runtime slots do not prove phases exist. No HTTP/HTML/JS/body/private capture accessed.',source_commit='5310edf09efd819f3d7a0f3ca96ee6b0d9ef6914',source_path=str(P.relative_to(R)),source_sha256=hashlib.sha256(raw).hexdigest(),runtime_source=BASE,source_metadata_rows=1609,logged_true=496,logged_false=1113,title_counts=dict(counts),unmatched_title_rows=sorted(unmatched,key=lambda v:(v['level'] if isinstance(v['level'],(int,float)) else 999,v['id'])),logged_true_missing_phase_ids=len(gaps),missing_slot_counts=dict(phasecounts),logged_true_phase_gaps=sorted(gaps,key=lambda v:(v['level'] if isinstance(v['level'],(int,float)) else 999,v['id'])),excluded_metadata_rows=excluded,metadata_ready_translations=0,notes=['logged=falsequery-only titles remain unproven and are not auto-imported.','logged=trueunmatched title needs primary own-ID observed page/title proof, not automatic acceptance from boolean.','No body/phase bulk in supplied safeindex; no missing phase text translated or assumed.','Selection of at most8IDs is a detail-source request queue, not translation count/currentenabled denominator.'])
(R/'evidence/main20-safe-index-triage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('COUNTS',report['title_counts'],'gapIDs',len(gaps),'slots',dict(phasecounts),'excluded',len(excluded));print('UNMATCHED LOGGED:')
for v in report['unmatched_title_rows']:
 if v['logged']:print(v['id'],v['level'],v['title'],v['missing_main_fields'])
print('GAPS L1-30:')
for v in report['logged_true_phase_gaps']:
 if isinstance(v['level'],(int,float)) and 1<=v['level']<=30 and not v.get('excluded_reason'):print(v['id'],v['level'],v['title'],v['missing_main_fields'])
