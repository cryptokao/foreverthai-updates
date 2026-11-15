"""Only39 newly qualified conditional descriptions. No guessed condition gates or old corpus rerun."""
import pathlib,json,re,hashlib,zipfile,collections,time
from lupa.lua51 import LuaRuntime,lua_type
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent;start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
doc=json.loads((R/'main28-conditional-input-private.json').read_text(encoding='utf-8'));rows=doc['rows'];assert len(rows)==39
zpath=R/'package-main27/build-0.469.0/ForeverThai-0.469.0-main27-PRIVATE-TEST.zip';assert sha(zpath.read_bytes())=='4fb985134c382d87744214a4ab290e5d3a3caf81a2cc0e47eaa17559dbd90021'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(zpath) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('testClass="Druid";testClassID="DRUID";testRace="Night Elf";UnitName=function()return "CloudTester"end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return testRace end')
classes=[('Druid','DRUID'),('Hunter','HUNTER'),('Warrior','WARRIOR'),('Paladin','PALADIN'),('Rogue','ROGUE'),('Priest','PRIEST'),('Shaman','SHAMAN'),('Mage','MAGE'),('Warlock','WARLOCK')]
races=['Night Elf','Dwarf','Gnome','Human','Orc','Tauren','Troll','Undead','Skyborne','High Order Skyborne','Windshaper Skyborne']
def dynamic(e):
 if lua_type(e)!='table':return set()
 ss=[e[1]] if isinstance(e[1],str) else [v for _,v in e[1].items()] if lua_type(e[1])=='table' else []
 found={x for s in ss for x in s.split() if x in ['C','R']}
 if e.variants:
  for _,v in e.variants.items():found|=dynamic(v)
 if e.amount:found|=dynamic(e.amount)
 return found
def render(en,c,r):return re.sub(r'\$([nNcCrR])',lambda m:{'n':'CloudTester','c':c,'r':r}[m[1].lower()],re.sub(r'\$[Bb]','\n',en))
def sig(en):
 norm=re.sub(r'[ \t\r\n\f\v]+',' ',re.sub(r'\$[Bb]','\n',en).replace('\u00a0',' ')).strip(' ');parts=[]
 for s in re.split(r'(\$[nNcCrR])',norm):
  if not s:continue
  if re.fullmatch(r'\$[nNcCrR]',s):parts.append(s[1].upper());continue
  b=s.encode();x=y=0
  for c in b:x=(x*257+c)%2147483647;y=(y*131+c)%2147483629
  parts.append(f'{len(b)}:{x}:{y}')
 return ' '.join(parts)
counts=collections.Counter();safe=[];pending=[];executions=0
for r in rows:
 q,en=r['quest_id'],r['english'];entry=a.quests[q].description if a.quests[q] else None;g=l.globals();g.testClass='Druid';g.testClassID='DRUID';g.testRace='Night Elf';profile=None;thai=None
 if classify_title(r['title'],q) or classify_title(en,q):status='held_developer_or_disabled_source'
 elif not en.strip() or en.strip().lower() in ['placeholder','description','log','nyi','not yet implemented']:status='held_blank_or_placeholder'
 else:
  thai=a.Translate(entry,render(en,'Druid','Night Elf'));executions+=1
  if thai is not None:status='already_supported_default_fixture';profile=dict(className='Druid',race='Night Elf')
  else:
   slots=dynamic(entry);tests=classes if 'C' in slots else [classes[0]];rs=races if 'R' in slots else [races[0]]
   for c,cid in tests:
    for race in rs:
     if c=='Druid' and race=='Night Elf':continue
     g.testClass=c;g.testClassID=cid;g.testRace=race;thai=a.Translate(entry,render(en,c,race));executions+=1
     if thai is not None:profile=dict(className=c,race=race);break
    if thai is not None:break
   status='already_supported_other_identity_fixture_NOT_eligibility_proof' if thai is not None else 'unmatched_conditional_description_needs_full_review'
 counts[status]+=1;meta={k:v for k,v in r.items() if k!='english'};meta.update(status=status,english_sha256=sha(en.encode()),english_bytes=len(en.encode()),canonical_present=entry is not None,expected_dynamic_signature=sig(en),supported_profile_fixture=profile)
 safe.append(meta)
 if status=='unmatched_conditional_description_needs_full_review':pending.append(dict(meta,english=en,existing_canonical_thai_template=entry[2] if entry else None))
report=dict(batch='MAIN28',scope='Only previously unprocessed current70938 conditionalDescriptions,40raw/39eligible,1uppercaseGhold',baseline_zip_sha256=sha(zpath.read_bytes()),source_pin='ea970da071079b32e56f349e09648ff0e314b351',schema_blob='8fee3e320e15fdd2e782c93dc2fb2c280ec55654',rows=safe,counts=dict(counts),matcher_executions=executions,holds=doc['holds'],new_Thai_fields=0,version_or_runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limits=['Source description variants are matched by full incoming own-ID body; playerConditionId/creatureId semantics never inferred or enforced','Fixture profile support is not actual condition eligibility/current enabled inventory','UppercaseGorientation/otherunknownmacros held; no gender guess','No old base-cache/MAIN27/old UI/Skill/NPC/font corpus rerun'])
for n,d in [('main28-conditional-audit.json',report),('main28-unmatched-private.json',pending)]:
 (R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False))
print(json.dumps([dict(q=r['quest_id'],index=r['source_ref']['pointer'],level=r['level'],title=r['title'],bytes=r['english_bytes']) for r in pending],ensure_ascii=False))
