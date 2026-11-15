"""Compare only newly inspected private SavedVariables fields,without publishing identities or raw text."""
import pathlib,json,hashlib,zipfile,re,time,collections
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;start=time.perf_counter();cpu=time.process_time()
docs=json.loads((R/'main32-local-observed-decoded-private.json').read_text(encoding='utf-8'));base=R/'package-main28/build-0.470.0/ForeverThai-0.470.0-main28-COMBINED.zip'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='a9c854976d2efac55b4821492714b7cf93dae627fbb77309d6bc820610cfb5e6'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
class_ids={v:v.upper() for v in ['Warrior','Paladin','Hunter','Rogue','Priest','Shaman','Mage','Warlock','Druid']}
counts=collections.Counter();seen=set();rows=[];private=[];duplicate=0
for doc in docs:
 for q,fields in doc['observed'].get('quests',{}).items():
  for field,variants in fields.items():
   if not isinstance(variants,dict):continue
   for ix,v in variants.items():
    if not isinstance(v,dict) or not isinstance(v.get('text'),str):continue
    text=v['text'];key=(int(q),field,text,v.get('player'),v.get('class'),v.get('race'))
    if key in seen:duplicate+=1;continue
    seen.add(key);g=l.globals();g.sampleName=v.get('player');g.sampleClass=v.get('class');g.sampleClassID=class_ids.get(v.get('class'));g.sampleRace=v.get('race');thai=None
    entry=a.quests[int(q)][field] if a.quests[int(q)] else None
    if v.get('locale')!='enUS':status='held_nonEnglish'
    elif field not in ['title','objective','description','progress','completion']:status='held_unknown_phase'
    elif not all(isinstance(v.get(k),str) and v[k] for k in ['player','class','race']) or g.sampleClassID is None:status='held_missing_typed_identity_context'
    else:
     thai=a.Translate(entry,text);status='supported_exact_captured_profile' if thai is not None else 'unmatched_private_capture_needs_full_review'
    counts[status]+=1;meta=dict(quest_id=int(q),field=field,source_index=doc['pin']['source_index'],variant_index=ix,source_build=v.get('build'),locale=v.get('locale'),text_sha256=hashlib.sha256(text.encode()).hexdigest(),text_bytes=len(text.encode()),status=status,canonical_present=entry is not None,identity_provenance='Observe UnitName/UnitClass/UnitRace stored at capture,values private',current70938_or_enabled_inventory_proven=False)
    rows.append(meta)
    if status=='unmatched_private_capture_needs_full_review':private.append(dict(meta,english=text,source_record=v))
report=dict(status='ONLY_NEWLY_INSPECTED_LOCAL_OBSERVED_FIELDS_COMPARED',baseline_version='0.470.0',unique_main_forms=len(rows),duplicate_backup_occurrences_skipped=duplicate,counts=dict(counts),rows=rows,new_Thai_fields=0,new_aliases=0,runtime_changed=False,source_files_modified=False,game_control_or_installation=False,raw_player_context_published=False,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limits=['Capture build70790,not current70938 live acceptance','Stored identities used for existing matcher test only,not inferred replacement roles','Raw source/names/account paths remain private;no nonMAIN NPC/book/speech tests'])
for n,d in [('main32-local-observed-audit.json',report),('main32-local-observed-unmatched-private.json',private)]:
 (R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=True))
print(json.dumps([dict(q=v['quest_id'],field=v['field'],bytes=v['text_bytes'],build=v['source_build']) for v in private]))
