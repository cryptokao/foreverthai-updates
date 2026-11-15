import pathlib,json,zipfile
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent
rows=json.loads((R/'main35-higher-level-acquisition-candidates.json').read_text(encoding='utf8'))
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)

out=[]
for r in rows:
 q=r['quest_id'];quest=a.quests[q]
 if quest is None or classify_title(r['title'],q):continue
 fs=[f for f in r['fields'] if quest[f] is None]
 if fs:out.append(dict(r,fields=fs,actual0471field_absent=True,source_phase_exists_NOT_yet_proven=True))
r=dict(scope='Next uninspected source acquisition level21-60 only,not missing prose or enabled count',baseline='0.471.0',candidates=out)
(R/'main35-higher-level-actual-queue.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(candidate_ids=len(out),candidate_fields=sum(len(x['fields']) for x in out))))
