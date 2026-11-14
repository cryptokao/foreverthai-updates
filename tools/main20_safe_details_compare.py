"""One comparison of the18privacy-screened phase bodies; no host fetch/aliases/runtime writes."""
import json,pathlib,hashlib,subprocess,collections
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];P=R/'source_inputs/warcraftforever-beta-details20-safe.json';raw=P.read_bytes();assert raw==subprocess.check_output(['git','-C',str(R),'show','faa496275ee1009c26261be02df9b4a2d4626d42:'+str(P.relative_to(R))]);doc=json.loads(raw);details=doc['details'];assert len(details)==8 and sum(len(v['phases']) for v in details)==18;assert all(v['progress_rendered'] is False for v in details)
BASE='7f082e6a57fe72305bd4366c1588c04d5bc1ad95';l=LuaRuntime();a=l.table()
for n in ['Catalog','Match']:
 data=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']);assert data==(R/'src/ForeverThai'/f'{n}.lua').read_bytes();l.execute(data.decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
rows=[];counts=collections.Counter()
for v in details:
 for f in v['phases']:
  field={'Objectives':'objective','Description':'description','Completion':'completion'}[f['source_heading']];text=f['english'];assert hashlib.sha256(text.encode()).hexdigest()==f['source_sha256'];q=v['quest_id'];entry=a.quests[q][field] if a.quests[q] else None;thai=a.Translate(entry,text);status='supported_actualTranslate' if thai is not None else 'unmatched_needs_independent_phase_literal_typed_proof';counts[status]+=1
  row=dict(quest_id=q,field=field,source_heading=f['source_heading'],url=v['url'],html_sha256=v['html_sha256'],english_sha256=f['source_sha256'],runtime_canonical_present=entry is not None,status=status,reader_context='SyntheticDruid/NightElf; no reader context inferred from beta page')
  if thai is not None:row['thai_sha256']=hashlib.sha256(thai.encode()).hexdigest()
  else:row['english']=text
  rows.append(row)
report=dict(scope='ONEcomparison of18sanitized field bodies against frozen actualCatalog/Match466; no HTTP/JS/crawl, oldsource audit, alias, translation or version.',source_commit='faa496275ee1009c26261be02df9b4a2d4626d42',source_path=str(P.relative_to(R)),source_sha256=hashlib.sha256(raw).hexdigest(),runtime_source=BASE,representative_ids=[v['quest_id'] for v in details],provided_literal_fields=18,counts=dict(counts),rows=rows,progress_headings_seen=0,progress_policy='Eight pages show no Progressheading; this does not prove no game progress. No empty slots populated and no more page crawl.',held_description_ids=[96656,94006,6081,6126],held_policy='Four fullDescriptionfields with resolvedreader names are not in comparison, not reconstructed/published/aliased.',roles_policy='Resolved class/race/name words never authorize new role aliases. Any unmatched field needs independent own-ID literal/typed source proof; logged=true is not currentactive/build evidence.',per_row_build='unknown',metadata_ready_translations=0,runtime_changed=False,fonts_version_feed_changed=False)
(R/'evidence/main20-safe-details-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report['counts'])
for v in rows:
 if v['status']!='supported_actualTranslate':print(json.dumps(v,ensure_ascii=False))
