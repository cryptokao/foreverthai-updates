"""Only5 previously unresolved MAIN34 forms;no rerun of38 supported forms."""
import pathlib,json,re,zipfile,hashlib,time,collections
from lupa.lua51 import LuaRuntime,lua_type
R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time()
pending=json.loads((R/'main34-live-sql-unmatched-private.json').read_text(encoding='utf8'));assert len(pending)==5
grammar=json.loads((R/'main30-primary-grammar-proof.json').read_text(encoding='utf8'))
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('testClass="Druid";testClassID="DRUID";UnitName=function()return "CloudTester"end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return "Night Elf"end')
def py(v):
 if lua_type(v)!='table':return v
 return {str(k):py(x) for k,x in v.items()}
gpat=re.compile(r'\$[Gg]\s*([^:;$]+?)\s*:\s*([^;$]+?)\s*;')
out=[];held=[]
classes=[('Druid','DRUID'),('Hunter','HUNTER'),('Warrior','WARRIOR'),('Paladin','PALADIN'),('Rogue','ROGUE'),('Priest','PRIEST'),('Shaman','SHAMAN'),('Mage','MAGE'),('Warlock','WARLOCK')]

out=[]
for v in pending:
 if v['quest_id']==94373 and v['field']=='progress':
  l.execute('UnitRace=function()return \"Dwarf\"end')
  for branch in [1,2]:
   en=re.sub(r'\$[Bb]','\n',gpat.sub(lambda m:m[branch],v['english']));out.append(dict(quest_id=94373,field='progress',branch=branch,profile_fixture='Dwarf',supported=a.Translate(a.quests[94373].progress,en) is not None,not_eligibility_proof=True))
 elif v['quest_id']==96628:
  for cl,cid in classes:
   l.globals().testClass=cl;l.globals().testClassID=cid
   en=re.sub(r'\$[Bb]','\n',v['english']).replace('$c',cl.lower());out.append(dict(quest_id=96628,field='completion',lowercase_class_diagnostic=cl,supported=a.Translate(a.quests[96628].completion,en) is not None,not_source_case_or_roleproof=True))
r=dict(batch='MAIN34',only_remaining3form_followup=True,rows=out,no_runtime_change=True,new_Thai_fields=0)
(R/'main34-profile-followup.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(r))
