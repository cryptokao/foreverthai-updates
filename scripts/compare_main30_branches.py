"""One comparison of newly qualified lowercase-g branches only; no unchanged corpus rerun."""
import pathlib,json,re,hashlib,zipfile,collections,time
from lupa.lua51 import LuaRuntime,lua_type
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parent;start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
doc=json.loads((R/'main30-uppercase-g-input-private.json').read_text(encoding='utf-8'));assert len(doc['rows'])==15
base=R/'package-main28/build-0.470.0/ForeverThai-0.470.0-main28-COMBINED.zip';assert sha(base.read_bytes())=='a9c854976d2efac55b4821492714b7cf93dae627fbb77309d6bc820610cfb5e6'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('testClass="Druid";testClassID="DRUID";testRace="Night Elf";UnitName=function()return "CloudTester"end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return testRace end')
classes=[('Druid','DRUID'),('Hunter','HUNTER'),('Warrior','WARRIOR'),('Paladin','PALADIN'),('Rogue','ROGUE'),('Priest','PRIEST'),('Shaman','SHAMAN'),('Mage','MAGE'),('Warlock','WARLOCK')]
races=['Night Elf','Dwarf','Gnome','Human','Orc','Tauren','Troll','Undead','Skyborne','High Order Skyborne','Windshaper Skyborne']
gender=re.compile(r'\$[Gg]\s*([^:;$]+?)\s*:\s*([^;$]+?)\s*;')
def slots(e):
 if lua_type(e)!='table':return set()
 ss=[e[1]] if isinstance(e[1],str) else [v for _,v in e[1].items()] if lua_type(e[1])=='table' else []
 found={x for s in ss for x in s.split() if x in ['C','R']}
 if e.variants:
  for _,v in e.variants.items():found|=slots(v)
 if e.amount:found|=slots(e.amount)
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
counts=collections.Counter();safe=[];pending=[];holds=[];executions=0
for raw in sorted(doc['rows'],key=lambda r:(r['level'],r['quest_id'],r['field'])):
 q=raw['quest_id'];source=raw['english'];forms=list(gender.finditer(source))
 hold=classify_title(raw['title'],q) or classify_title(source,q)
 if not hold and raw['noData_in_current_scan'] and not raw['described_in_current_scan']:hold='noData_query_only_current_discrepancy'
 if not hold and not forms:hold='unparsed_lowercase_gender'
 for sex in [1,2]:
  en=gender.sub(lambda m:m[sex],source)
  remaining=re.sub(r'\$[nNcCrRbB]','',en)
  if not hold and ('$' in remaining or '|' in en):hold='unproven_additional_macro_or_markup'
  if not hold and re.search(r'\$[nNcCrR][A-Za-z]',en):hold='identity_macro_attached_letter'
 if hold:
  holds.append(dict(quest_id=q,field=raw['runtime_field'],title=raw['title'],reason=hold));continue
 for sex in [1,2]:
  en=gender.sub(lambda m:m[sex],source);r=dict(raw,raw_english=source,english=en,gender_branch='first_source_alternative' if sex==1 else 'second_source_alternative');r['field']='objective' if r['runtime_field']=='objectives' else r['runtime_field'];entry=a.quests[q][r['field']] if a.quests[q] else None
  g=l.globals();g.testClass='Druid';g.testClassID='DRUID';g.testRace='Night Elf';profile=None
  thai=a.Translate(entry,render(en,'Druid','Night Elf'));executions+=1
  if thai is not None:status='already_supported_default_fixture';profile=dict(className='Druid',race='Night Elf')
  else:
   ds=slots(entry);cs=classes if 'C' in ds else [classes[0]];rs=races if 'R' in ds else [races[0]]
   for c,cid in cs:
    for race in rs:
     if c=='Druid' and race=='Night Elf':continue
     g.testClass=c;g.testClassID=cid;g.testRace=race;thai=a.Translate(entry,render(en,c,race));executions+=1
     if thai is not None:profile=dict(className=c,race=race);break
    if thai is not None:break
   status='already_supported_other_identity_fixture_NOT_eligibility' if thai is not None else 'unmatched_gender_branch_needs_meaning_review'
  counts[status]+=1;meta={k:v for k,v in r.items() if k not in ['english','raw_english']};meta.update(status=status,english_sha256=sha(en.encode()),raw_english_sha256=sha(source.encode()),english_bytes=len(en.encode()),canonical_present=entry is not None,expected_dynamic_signature=sig(en),supported_profile_fixture=profile)
  safe.append(meta)
  if status=='unmatched_gender_branch_needs_meaning_review':pending.append(dict(meta,english=en,raw_english=source,existing_canonical_thai_template=entry[2] if entry else None))
report=dict(batch='MAIN30',scope='New primary G/g branch grammar proof,complete incoming source alternatives only;no reader-sex/condition dispatch or new upstream English',baseline_zip_sha256=sha(base.read_bytes()),source_pin='ea970da071079b32e56f349e09648ff0e314b351',schema_blob=doc['schema_blob'],raw_source_fields=15,qualified_branches=len(safe),counts=dict(counts),rows=safe,holds=holds,matcher_executions=executions,new_Thai_fields=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limits=['Both complete source alternatives supported from explicit primary G/g grammar; reader side/condition never selected by addon','Full incoming branches only; no UnitSex or condition eligibility guessed','Fixtures are not enabled/playable whole-game inventory','No old literal/NCR/MAIN28/Skill/NPC/UI/font suite rerun'])
for n,d in [('main30-branch-audit.json',report),('main30-unmatched-private.json',pending)]:
 (R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=True))
print(json.dumps([dict(q=r['quest_id'],field=r['field'],sex=r['gender_branch'],level=r['level'],title=r['title'],bytes=r['english_bytes']) for r in pending],ensure_ascii=True))
