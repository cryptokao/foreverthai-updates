import pathlib,json,zipfile,collections,sys,hashlib
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent;sys.stdout.reconfigure(encoding='utf8');doc=json.loads((R/'main36-eg-query-delta-input-private.json').read_text());newids=set(doc['new_quest_ids']);records={}
for r in doc['rows']:
 if r['quest_id'] in newids:records[r['quest_id']]=r
assert len(records)==len(newids)==1438
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();base=R/'package-main44/build-0.480.0-compact/ForeverThai-0.480.0-main44-COMBINED.zip';assert hashlib.sha256(base.read_bytes()).hexdigest()=='7bdbf55bf8f38974a8a55cc80cc0e83dbed1df951b69bf21f1d8f3291ca48208'
with zipfile.ZipFile(base) as z:
 for n in z.read('ForeverThai/ForeverThai.toc').decode().splitlines():
  if n=='Catalog.lua' or n.startswith('MainQuest'):l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
prior=set()
for fn in ['main40-alternate-primary-private.json','main40-alternate-final-private.json','main41-alternate-final-private.json','main42-all-alternate-final-private.json','main43-all-final-primary-private.json']:
 v=json.loads((R/fn).read_text(encoding='utf8'));assert isinstance(v,list),(fn,type(v))
 for r in v:prior.add((r['quest_id'],r['field']))
queue=[];excluded=[];already=[]
for q,r in records.items():
 quest=a.quests[q];title=r['title'];level=r.get('level');reason=classify_title(title,q)
 if reason or r['query_record'].get('description','').strip().lower() in ['nyi','nyi.','not yet implemented','placeholder']:excluded.append(dict(quest_id=q,reason=reason or 'developer_placeholder'));continue
 if quest is None:excluded.append(dict(quest_id=q,reason='no_runtimequest_needs_title_scope'));continue
 for f in ['progress','completion']:
  if quest[f] is not None:continue
  if (q,f) in prior:already.append(dict(quest_id=q,field=f));continue
  queue.append(dict(quest_id=q,field=f,title=title,level=level,alternate_url=f'https://db.icy-veins.com/wow-forever/quests/{q}',runtime_field_nil_verified_in='0.480.0',source_scope='MAIN36 newlyacquired1438 currentqueryIDs,notold3902queue',source_phase_exists_NOT_yet_proven=True,current_enabled_inventory_proven=False))
queue.sort(key=lambda r:(r['level'] if isinstance(r['level'],int) and r['level']>0 else 100000,r['quest_id'],r['field']))
report=dict(batch='MAIN45',status='NEW_UNINSPECTED_PRIMARY_ACQUISITION_QUEUE_NOT_MISSING_PROSE_COUNT',baseline='0.480.0',current_query_pin=doc['new_pin'],current_query_blob=doc['new_blob'],new_query_ids_checked=1438,excluded=excluded,already_alternate_queried=already,candidates=queue,complete_quests_claimed=0,enabled_wholegame_inventory=False)
(R/'main45-new1438-actual-acquisition-queue.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(candidates=len(queue),ids=len({r['quest_id'] for r in queue}),previously_queried=len(already),excluded=len(excluded),level_brackets=dict(collections.Counter((str(((r['level']-1)//10)*10+1)+'-'+str(((r['level']-1)//10+1)*10)) if isinstance(r['level'],int) and r['level']>0 else 'unknown' for r in queue)),first12=queue[:12]),indent=2))
