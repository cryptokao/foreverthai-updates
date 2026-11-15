"""Acquire missing phases only for1438new-query IDs, skipping all closed earlier page lookups."""
import pathlib,json,re,zipfile,sys,collections
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main38/build-0.474.0/ForeverThai-0.474.0-main38-PRIVATE-TEST.zip') as z:
 for n in [s for s in z.read('ForeverThai/ForeverThai.toc').decode().splitlines() if s=='Catalog.lua' or s.startswith('MainQuest')]:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
doc=json.loads((R/'main36-eg-query-delta-input-private.json').read_text(encoding='utf8'));new=set(doc['new_quest_ids']);assert len(new)==1438
records={r['quest_id']:r['query_record'] for r in doc['rows'] if r['quest_id'] in new};assert len(records)==1438
closed=set()
for name in ['main35-primary-source-acquisition-final.json','main34-lowlevel-primary-all-section-closure.json','main34-completion-primary-section-closure.json']:
 for r in json.loads((R/name).read_text(encoding='utf8'))['rows']:
  closed.add((r['quest_id'],r.get('field') or ('completion' if 'completion' in name else 'progress')))
out=[];excluded=[]
for q,rec in records.items():
 title=rec.get('title','');level=rec.get('level',0);reason=classify_title(title,q)
 if q in [5101,8274] or re.search(r'(?i)(?:test quest|test kill|collin.*test|zzold)',title):reason='explicit_test_title'
 if rec.get('description','').strip().lower() in ['nyi','nyi.','not yet implemented','placeholder']:reason='explicit_placeholder_description'
 if reason:excluded.append(dict(quest_id=q,reason=reason));continue
 if not isinstance(level,int) or level<=0:continue
 quest=a.quests[q]
 for f in ['progress','completion']:
  if quest is not None and quest[f] is not None:continue
  if (q,f) in closed:continue
  # These just-read new pages contain full mainbody throughRewards/Related and no target headings.
  if q in [86792,92189,95818]:continue
  slug=re.sub(r'[^a-z0-9]+','-',title.lower().replace("'",'')).strip('-')
  out.append(dict(quest_id=q,field=f,title=title,level=level,url=f'https://www.wowhead.com/forever/quest={q}/{slug}',actual0474field_absent=True,source_phase_exists_NOT_yet_proven=True,current_enabled_inventory_proven=False))
out.sort(key=lambda x:(x['level'],x['quest_id'],x['field']))
report=dict(batch='MAIN39',scope='New1438queryIDs only,not old3902/closed1414or lowlevel179pages',input_query_pin='0f202e892f1a15c8192c232351824eccb99efd8a',baseline='Actual0.474combinedZIP',candidate_fields=len(out),candidate_ids=len({r['quest_id'] for r in out}),by_level=dict(collections.Counter(r['level'] for r in out)),rows=out,excluded_source_titles=excluded,game_phase_absence_or_current_enabled_proven=False,limits=['Nilslots are acquisition candidates,NOTmissingprose or completequests','Unknownlevel IDs not counted,remain separate','Do not retry inaccessible403 or repeat closed pages','86792/92189/95818newmainbodies alreadyread noProgress/Completion;not gameabsence proof'])
(R/'main39-new-id-phase-source-queue.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['rows','excluded_source_titles']},ensure_ascii=False));print(json.dumps(out[:12],ensure_ascii=False))
