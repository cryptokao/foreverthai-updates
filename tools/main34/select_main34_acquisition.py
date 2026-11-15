import pathlib,json,zipfile
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent
rows=json.loads((R/'main34-source-acquisition-candidates.json').read_text(encoding='utf8'))
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
out=[]
for r in rows:
 q=r['quest_id'];quest=a.quests[q];reason=classify_title(r['title'],q)
 if quest is None or reason or not 1<=r['level']<=10:continue
 if quest.progress is None:out.append(dict(r,field='progress',actual0471field_absent=True,source_phase_exists_NOT_yet_proven=True))
(R/'main34-actual-lowlevel-source-acquisition-queue.json').write_text(json.dumps(dict(scope='Source acquisition only,not missing prose or current enabled inventory',baseline='0.471.0',candidates=out),indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(count=len(out),first16=out[:16])))
