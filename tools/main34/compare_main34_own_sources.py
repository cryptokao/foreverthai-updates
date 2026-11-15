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
out=[];held=[];counts=collections.Counter();calls=0
for r in records:
 q=r['quest_id'];f=r['field'];raw=r['english'];title=titles.get(q,'');exclusion=classify_title(title,q) or classify_title(raw,q)
 forms=[gpat.sub(lambda m:m[branch],raw) for branch in [1,2]] if gpat.search(raw) else [raw]
 for branch,en in enumerate(forms,1):
  entry=a.quests[q][f] if a.quests[q] else None;ui=re.sub(r'\$[Bb]','\n',en);token=bool(re.search(r'\$[NnCcRr]',ui));ds=slots(entry);profile=None;status=None
  l.globals().testClass='Druid';l.globals().testClassID='DRUID';l.globals().testRace='Night Elf'
  if exclusion:status='excluded_'+exclusion
  else:
   thai=a.Translate(entry,en);calls+=1
   if thai is None:thai=a.Translate(entry,ui);calls+=1
   if thai is not None:status='supported_exact_or_markup'
   elif '$' in re.sub(r'\$[nNcCrR]','',ui) or '|' in ui:status='held_unproven_syntax'
   else:
    for cl,cid in (classes if 'C' in ds else [classes[0]]):
     for race in (races if 'R' in ds else [races[0]]):
      l.globals().testClass=cl;l.globals().testClassID=cid;l.globals().testRace=race
      for cls in ([cl,cl.lower()] if '$c' in ui or '$C' in ui else [cl]):
       rendered=re.sub(r'\$[nNcCrR](?![A-Za-z0-9_])',lambda m:{'n':'CloudTester','c':cls,'r':race}[m[0][1].lower()],ui)
       thai=a.Translate(entry,rendered);calls+=1
       if thai is not None:profile=dict(class_fixture=cl,race_fixture=race,class_render=cls);break
      if thai is not None:break
     if thai is not None:break
    status=('diagnostic_identity_substitution_supported_NOT_roleproof' if token else 'supported_other_identity_fixture_NOT_eligibility') if thai is not None else 'held_unproven_identity_or_current_source' if token else 'literal_unmatched_needs_primary_original'
  meta={k:v for k,v in r.items() if k!='english'};meta.update(title=title,branch=branch,english_sha256=hashlib.sha256(en.encode()).hexdigest(),english_bytes=len(en.encode()),status=status,profile=profile,not_current_enabled_inventory=True)
  out.append(meta);counts[status]+=1
  if 'held' in status or 'unmatched' in status:held.append(dict(meta,english=en,raw_english=raw))
report=dict(batch='MAIN34',scope='Only20source-owned quest file;paragraph breaks restored by publisher and metadata inferred,not treated as primary current inventory',source_repo='Karrz1/TrinityCore',pin='e6399e4fcbf774f7a8eabf0148058b70f49487af',path='sql/custom/world/2026_10_30_20_world_forever_quests_own_sources.sql',blob='9efa62b49ae8d539914faec2924dd72a879012f7',quests=len(titles),raw_fields=len(records),forms=len(out),counts=dict(counts),rows=out,matcher_calls=calls,new_Thai_fields=0,new_aliases=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu)
(R/'main34-own-source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'main34-own-source-unmatched-private.json').write_text(json.dumps(held,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=True))
print(json.dumps(held,ensure_ascii=True))
