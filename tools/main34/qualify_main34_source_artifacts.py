"""Parse only text columns of20 source-owned quests;no SQL execution."""
import pathlib,json,re,hashlib,zipfile,time,collections
from lupa.lua51 import LuaRuntime,lua_type
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time()
b=(R/'main34-own-source-quests.sql').read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='9efa62b49ae8d539914faec2924dd72a879012f7'
pat=re.compile(r'^INSERT INTO \x60(quest_template|quest_offer_reward|quest_request_items)\x60 \(([^)]*)\) VALUES \((.*)\);$')
value=re.compile(r"\s*('(?:[^']|'')*'|-?\d+(?:\.\d+)?|NULL)\s*(,|$)")
records=[];titles={}
for ix,line in enumerate(b.decode().splitlines(),1):
 m=pat.fullmatch(line)
 if not m:continue
 vals=[];pos=0;s=m[3]
 while pos<len(s):
  v=value.match(s,pos);assert v,(ix,pos);z=v[1];vals.append(z[1:-1].replace("''","'") if z.startswith("'") else None if z=='NULL' else float(z) if '.' in z else int(z));pos=v.end()
 columns=[x.strip().strip(chr(96)) for x in m[2].split(',')];assert len(columns)==len(vals)
 row=dict(zip(columns,vals));q=row['ID']
 if 'LogTitle' in row:titles[q]=row['LogTitle']
 if row.get('VerifiedBuild')==-1:continue
 fmap={'quest_template':{'LogTitle':'title','LogDescription':'objective','QuestDescription':'description'},'quest_offer_reward':{'RewardText':'completion'},'quest_request_items':{'CompletionText':'progress'}}[m[1]]
 for col,f in fmap.items():
  if isinstance(row.get(col),str) and row[col].strip():records.append(dict(quest_id=q,field=f,english=row[col],source_line=ix,source_column=col,source_VerifiedBuild=row.get('VerifiedBuild')))
assert len(titles)==20
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 for f in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','Match.lua']:l.execute(z.read('ForeverThai/'+f).decode(),'ForeverThai',a)
l.execute('testClass="Druid";testClassID="DRUID";testRace="Night Elf";UnitName=function()return "CloudTester"end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return testRace end')
def slots(e):
 if lua_type(e)!='table':return set()
 found={x for s in ([e[1]] if isinstance(e[1],str) else []) for x in s.split() if x in ['C','R']}
 if e.variants:
  for _,v in e.variants.items():found|=slots(v)
 return found
classes=[('Druid','DRUID'),('Hunter','HUNTER'),('Warrior','WARRIOR'),('Paladin','PALADIN'),('Rogue','ROGUE'),('Priest','PRIEST'),('Shaman','SHAMAN'),('Mage','MAGE'),('Warlock','WARLOCK')]
races=['Night Elf','Dwarf','Gnome','Human','Orc','Tauren','Troll','Undead','Skyborne','High Order Skyborne','Windshaper Skyborne']
gpat=re.compile(r'\$[Gg]\s*([^:;$]+?)\s*:\s*([^;$]+?)\s*;')
pending=json.loads((R/'main34-own-source-unmatched-private.json').read_text(encoding='utf8'));out=[];left=[]
for v in pending:
 en=v['english'];q=v['quest_id'];f=v['field']
 if f=='objective':reason='publisher_objective_truncated_or_wrong_phase_NOT_new_game_source';out.append(dict(quest_id=q,field=f,status=reason,english_sha256=v['english_sha256']));continue
 if '<lad/lass>' in en:out.append(dict(quest_id=q,field=f,status='ambiguous_publisher_placeholder_requires_primary_original',english_sha256=v['english_sha256']));left.append(v);continue
 assert re.search(r'>[A-Za-z]',en)
 ui=re.sub(r'>(?=[A-Za-z])','> ',re.sub(r'\$[Bb]','\n',en));entry=a.quests[q][f] if a.quests[q] else None;match=False;chosen=None
 for cl,cid in classes:
  l.globals().testClass=cl;l.globals().testClassID=cid
  for cls in [cl,cl.lower()]:
   rendered=re.sub(r'\$[nNcCrR](?![A-Za-z0-9_])',lambda m:{'n':'CloudTester','c':cls,'r':'Night Elf'}[m[0][1].lower()],ui)
   if a.Translate(entry,rendered) is not None:match=True;chosen=cl;break
  if match:break
 out.append(dict(quest_id=q,field=f,status='publisher_emote_boundary_diagnostic_supported_NOT_UIproof' if match else 'requires_primary_original',english_sha256=v['english_sha256'],class_fixture=chosen,new_alias=False))
 if not match:left.append(v)
r=dict(batch='MAIN34',scope='Only14new-source mismatches;do not convert visibly truncated objectives or publisher HTML artifacts into new runtime aliases',rows=out,new_Thai_fields=0,new_aliases=0,runtime_changed=False,unresolved_primary_original_fields=len(left))
(R/'main34-own-source-artifact-closure.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r))
(R/'main34-primary-original-needed-private.json').write_text(json.dumps(left,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
