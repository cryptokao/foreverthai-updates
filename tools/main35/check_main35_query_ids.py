import pathlib,json,zipfile
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent
rows=json.loads((R/'main35-current-query-id-metadata.json').read_text(encoding='utf8'))
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main35/build-0.472.0/ForeverThai-0.472.0-main35-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','MainQuest35.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)



missing=[]
for r in rows:
 q=r['quest_id']
 if a.quests[q] is None:missing.append(dict(r,classification=classify_title(r['title'],q)))
report=dict(batch='MAIN35',scope='Current pinned query IDs compared to actual0.472quest-table membership only,no old field matcher rerun',source_query_ids=len(rows),missing_runtime_ids=missing,not_enabled_inventory=True,new_Thai_fields=0)
(R/'main35-current-query-id-coverage.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
