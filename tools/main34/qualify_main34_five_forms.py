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
for v in pending:
 q=v['quest_id'];f=v['field'];entry=a.quests[q][f];raw=v['english']
 if '$G' in raw:
  assert len(list(gpat.finditer(raw)))==1 and '$' not in re.sub(r'\$[Bb]','',gpat.sub(lambda m:m[1],raw))
  for branch in [1,2]:
   en=re.sub(r'\$[Bb]','\n',gpat.sub(lambda m:m[branch],raw));thai=a.Translate(entry,en)
   row=dict(quest_id=q,field=f,branch='first_source_alternative' if branch==1 else 'second_source_alternative',english_sha256=hashlib.sha256(en.encode()).hexdigest(),supported=thai is not None,no_gender_dispatch_or_eligibility_inferred=True)
   out.append(row)
   if thai is None:held.append(dict(row,english=en,existing_entry=py(entry)))
 else:
  checks=[]
  for cl,cid in classes:
   l.globals().testClass=cl;l.globals().testClassID=cid
   en=re.sub(r'\$[nNcCrR](?![A-Za-z0-9_])',lambda m:{'n':'CloudTester','c':cl,'r':'Night Elf'}[m[0][1].lower()],re.sub(r'\$[Bb]','\n',raw))
   thai=a.Translate(entry,en);checks.append(dict(class_fixture=cl,matched=thai is not None))
   if thai is not None:break
  row=dict(quest_id=q,field=f,diagnostic_profile_checks=checks,matched=thai is not None,not_identity_role_or_eligibility_proof=True)
  out.append(row)
  if thai is None:held.append(dict(row,english=raw,existing_entry=py(entry)))
report=dict(batch='MAIN34',scope='Only5unresolved forms,known primary G/g structure;no UnitSex/eligibility/identity role inferred',new_Thai_fields=0,new_aliases=0,rows=out,remaining=len(held),grammar_reference='evidence/main30-primary-grammar-proof.json',elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu)
(R/'main34-five-form-followup.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
(R/'main34-followup-unmatched-private.json').write_text(json.dumps(held,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
print(json.dumps(held,ensure_ascii=True))
