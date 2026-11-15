"""Only4new missing literal objective slots;exact full-source reuse lookup,no old matcher tests."""
import pathlib,json,hashlib,zipfile,re,sys
from lupa.lua51 import LuaRuntime,lua_type
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent
rows=json.loads((R/'main35-four-literal-source-input.json').read_text(encoding='utf8'))
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
proposed=[]
for row in rows:
 en=row['english'];assert en.isascii() and not re.search(r'[$|{}<>]',en);assert a.quests[row['quest_id']].objective is None
 norm=' '.join(en.split());assert norm==en
 b=norm.encode();x=y=0
 for c in b:x=(x*257+c)%2147483647;y=(y*131+c)%2147483629
 sig=f'{len(b)}:{x}:{y}';assert int(sig.split(':')[0])==len(en.encode())
 reuse=[]
 def walk(e,q,f,path):
  if lua_type(e)!='table':return
  ss=[e[1]] if isinstance(e[1],str) else [v for _,v in e[1].items()] if lua_type(e[1])=='table' else []
  if sig in ss and isinstance(e[2],str):reuse.append(dict(quest_id=q,field=f,path=path,thai=e[2],thai_sha256=hashlib.sha256(e[2].encode()).hexdigest()))
  if e.variants:
   for i,v in e.variants.items():walk(v,q,f,path+f'.variants[{i}]')
  if e.amount:walk(e.amount,q,f,path+'.amount')
 for q,e in a.quests.items():
  for f in ['title','objective','description','progress','completion']:walk(e[f],int(q),f,f)
 proposed.append(dict(row,expected_dynamic_signature=sig,english_sha256=hashlib.sha256(en.encode()).hexdigest(),reuse_candidates=reuse,no_identity_or_quantity_macro=True,entire_source_read=True))
(R/'main35-four-literal-reuse-review.json').write_text(json.dumps(proposed,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(proposed,ensure_ascii=False,indent=2))
