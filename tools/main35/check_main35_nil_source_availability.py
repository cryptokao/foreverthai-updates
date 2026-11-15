import pathlib,json,zipfile
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent
rows=json.loads((R/'main35-nil-objective-description-source-input-private.json').read_text(encoding='utf8'))
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)


out=[]
for r in rows:
 q=r['quest_id'];f=r['field'];quest=a.quests[q]
 if quest is not None and quest[f] is not None:status='filled_in_actual0471_not_missing'
 else:status=classify_title(r['title'],q) or classify_title(r['english'],q) or 'source_needs_exact_field_review'
 out.append(dict(quest_id=q,field=f,title=r['title'],level=r['level'],status=status,english_bytes=len(r['english'].encode())))
r=dict(batch='MAIN35',scope='Onlysource-available objective/description candidates marked nil in older inventory;actual0471table presence and source classifier only,no old matcher rerun',rows=out,runtime_changed=False,new_Thai_fields=0)
(R/'main35-nil-objective-description-source-audit.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(r))
