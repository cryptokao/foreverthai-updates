"""Only17 new conditional candidates: find exact full-source reuse, never arbitrary partial prose."""
import pathlib,json,zipfile,hashlib,re
from lupa.lua51 import LuaRuntime,lua_type
R=pathlib.Path(__file__).resolve().parent;vs=json.loads((R/'main28-unmatched-private.json').read_text(encoding='utf-8'));assert len(vs)==17
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main27/build-0.469.0/ForeverThai-0.469.0-main27-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
by={}
for v in vs:v['reuse_candidates']=[];by.setdefault(v['expected_dynamic_signature'],[]).append(v)
def walk(e,q,f,path):
 if lua_type(e)!='table':return
 ss=[e[1]] if isinstance(e[1],str) else [s for _,s in e[1].items()] if lua_type(e[1])=='table' else []
 for sig in ss:
  if sig in by:
   for v in by[sig]:
    if isinstance(e[2],str):v['reuse_candidates'].append(dict(quest_id=q,field=f,path=path,thai_template=e[2],thai_sha256=hashlib.sha256(e[2].encode()).hexdigest(),contains_role_placeholders=bool(re.search(r'\{(?:name|class|race|world\d+)\}',e[2]))))
 if e.variants:
  for ix,x in e.variants.items():walk(x,q,f,path+f'.variants[{ix}]')
 if e.amount:walk(e.amount,q,f,path+'.amount')
for q,e in a.quests.items():
 for f in ['title','objective','description','progress','completion']:walk(e[f],int(q),f,f)
(R/'main28-reuse-review-private.json').write_text(json.dumps(vs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
groups={}
for v in vs:groups.setdefault(v['expected_dynamic_signature'],[]).append(v)
out=[]
for sig,rs in groups.items():
 choices=[];seen=set()
 for c in rs[0]['reuse_candidates']:
  if c['thai_sha256'] not in seen:seen.add(c['thai_sha256']);choices.append(c)
 out.append(dict(ids=[r['quest_id'] for r in rs],level=rs[0]['level'],title=rs[0]['title'],english=rs[0]['english'],signature=sig,reuse_candidates=choices,existing_canonical_thai=rs[0].get('existing_canonical_thai_template')))
print(json.dumps(out,ensure_ascii=False,indent=2))
