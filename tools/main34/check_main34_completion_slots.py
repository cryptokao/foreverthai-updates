import pathlib,json,zipfile
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent
rows=json.loads((R/'main34-completion-acquisition-candidates.json').read_text(encoding='utf8'))
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)

report=[dict(quest_id=r['quest_id'],field='completion',actual0471field_absent=a.quests[r['quest_id']] is not None and a.quests[r['quest_id']].completion is None) for r in rows]
(R/'main34-completion-slot-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
