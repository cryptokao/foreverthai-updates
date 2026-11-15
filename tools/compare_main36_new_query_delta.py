"""Only new-query IDs/English fields/conditionals in the Nov15 source delta;no old3902corpus rerun."""
import pathlib,json,re,zipfile,hashlib,collections,time,sys
from lupa.lua51 import LuaRuntime,lua_type
from source_classification import classify_title
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time();sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
doc=json.loads((R/'main36-eg-query-delta-input-private.json').read_text(encoding='utf8'));assert doc['new_pin']=='0f202e892f1a15c8192c232351824eccb99efd8a' and len(doc['rows'])==3592
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
base=R/'package-main35/build-0.472.0/ForeverThai-0.472.0-main35-PRIVATE-TEST.zip';assert hashlib.sha256(base.read_bytes()).hexdigest()=='3b6f10f8519c625f4897840e17aabdd908ef6ab1ae753f3ab01daddd52f0cebc'
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','MainQuest35.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('testClass="Druid";testClassID="DRUID";testRace="Night Elf";UnitName=function()return "CloudTester"end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return testRace end')
classes=[('Druid','DRUID'),('Hunter','HUNTER'),('Warrior','WARRIOR'),('Paladin','PALADIN'),('Rogue','ROGUE'),('Priest','PRIEST'),('Shaman','SHAMAN'),('Mage','MAGE'),('Warlock','WARLOCK')]
races=['Night Elf','Dwarf','Gnome','Human','Orc','Tauren','Troll','Undead','Skyborne','High Order Skyborne','Windshaper Skyborne']
gender=re.compile(r'\$[Gg]\s*([^:;$]+?)\s*:\s*([^;$]+?)\s*;')
def slots(e):
 if lua_type(e)!='table':return set()
 ss=[e[1]] if isinstance(e[1],str) else [x for _,x in e[1].items()] if lua_type(e[1])=='table' else []
 out={x for s in ss for x in s.split() if x in ['C','R']}
 if e.variants:
  for _,v in e.variants.items():out|=slots(v)
 if e.amount:out|=slots(e.amount)
 return out
def source_sig(en):
 en=re.sub(r'\$[Bb]','\n',en).replace('\u00a0',' ');en=re.sub(r'[ \t\r\n\f\v]+',' ',en).strip(' ');parts=[]
 for v in re.split(r'(\$[nNcCrR])',en):
  if not v:continue
  if re.fullmatch(r'\$[nNcCrR]',v):parts.append(v[1].upper());continue
  b=v.encode();x=y=0
  for c in b:x=(x*257+c)%2147483647;y=(y*131+c)%2147483629
  parts.append(f'{len(b)}:{x}:{y}')
 return ' '.join(parts)
out=[];pending=[];counts=collections.Counter();calls=0;g=l.globals()
for r in sorted(doc['rows'],key=lambda x:(x.get('level') if isinstance(x.get('level'),int) and x['level']>0 else 100000,x['quest_id'],x['field'])):
 q=r['quest_id'];f=r['field'];raw=r['english'];record=r['query_record'];title=r.get('title') or ''
 reason=classify_title(title,q) or classify_title(raw,q)
 if not reason and re.search(r'(?i)(?:^hunter test quest\d*$|^collin.s test quest$|^zzOLD\b)',title):reason='explicit_test_or_old_title'
 if not reason and record.get('description','').strip().lower() in ['nyi','nyi.','not yet implemented','placeholder']:reason='quest_description_developer_placeholder'
 branches=[(1,gender.sub(lambda m:m[1],raw)),(2,gender.sub(lambda m:m[2],raw))] if gender.search(raw) else [(None,raw)]
 for branch,en in branches:
  quest=a.quests[q];entry=quest[f] if quest is not None else None;ui=re.sub(r'\$[Bb]','\n',en);identity=bool(re.search(r'\$[nNcCrR]',ui));profile=None;thai=None;status=None;sole_amount=None
  g.testClass='Druid';g.testClassID='DRUID';g.testRace='Night Elf'
  remaining=re.sub(r'\$[nNcCrR]','',ui)
  if reason:status='excluded_'+reason
  else:
   thai=a.Translate(entry,en);calls+=1
   if thai is None:thai=a.Translate(entry,ui);calls+=1
   if thai is not None:status='already_supported_exact_or_markup'
   elif '$' in remaining or '|' in en or re.search(r'<(?:name|player|race|class|unknown)[^>]*>|\{[^}]*\}',en,re.I):
    status='held_unproven_macro_or_markup'
   elif re.search(r'\$[nNcCrR][A-Za-z]',ui):status='held_identity_token_attached_letter'
   else:
    ds=slots(entry);clist=classes if 'C' in ds else [classes[0]];rlist=races if 'R' in ds else [races[0]]
    for cl,cid in clist:
     for race in rlist:
      g.testClass=cl;g.testClassID=cid;g.testRace=race
      for cls in ([cl,cl.lower()] if re.search(r'\$[cC]',ui) else [cl]):
       rendered=re.sub(r'\$[nNcCrR](?![A-Za-z0-9_])',lambda m:{'n':'CloudTester','c':cls,'r':race}[m[0][1].lower()],ui)
       thai=a.Translate(entry,rendered);calls+=1
       if thai is not None:profile=dict(class_fixture=cl,race_fixture=race,class_render=cls);break
      if thai is not None:break
     if thai is not None:break
    if thai is not None:status='diagnostic_identity_supported_NOT_role_or_eligibility_proof' if identity else 'already_supported_other_fixture_NOT_eligibility'
    else:status='held_identity_needs_exact_role_source' if identity else 'literal_unmatched_needs_full_meaning_review'
  pointer=f"/quests/{q}/{r['source_field']}"+(f"/{r['source_index']}/text" if r['source_field']=='conditionalDescriptions' else '')
  meta=dict(quest_id=q,field=f,title=title,level=r.get('level'),source_pointer=pointer,branch=branch,english_sha256=sha(en),raw_source_sha256=sha(raw),english_bytes=len(en.encode()),status=status,runtime_quest_present=quest is not None,runtime_field_present=entry is not None,profile=profile,expected_dynamic_signature=source_sig(en) if '$' not in remaining and '|' not in en else None,current_enabled_usage='unproven')
  out.append(meta);counts[status]+=1
  if status.startswith('literal_unmatched') or status.startswith('held_'):pending.append(dict(meta,english=en,raw_english=raw,query_record=record,old_english=r.get('old_english')))
report=dict(batch='MAIN36',scope='Only3592raw new-source fields/conditionals in1438new query IDs plus7new conditional records;old3902English unchanged and NOT re-matched',baseline='Actual immutable combined0.472 withall additive data',source_old_pin=doc['old_pin'],source_new_pin=doc['new_pin'],source_old_blob=doc['old_blob'],source_new_blob=doc['new_blob'],raw_new_fields=3592,qualified_forms=len(out),new_query_ids=len(doc['new_quest_ids']),current_query_ids=5340,source_header=doc['meta'],counts=dict(counts),rows=out,matcher_calls=calls,new_Thai_fields=0,new_aliases=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu,limits=['Newtoquery is not untranslated or enabled/playable quest count','Primary G/g structure only,both alternatives,no sex/condition dispatch','Identity substitutions diagnostic only,not source-role proof','Unknown macros/markup held;no arbitrary amount wildcard','No old3902/11144matcher or UI/Skill/font suite rerun'])
(R/'main36-new-query-delta-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'main36-new-query-unmatched-private.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False));print(json.dumps([dict(q=v['quest_id'],field=v['field'],level=v['level'],status=v['status'],bytes=v['english_bytes']) for v in pending],ensure_ascii=False))
