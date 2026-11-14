"""Cloud structural preservation, source matching and independent counter regression."""
import hashlib,json,pathlib,re,zipfile,itertools
from lupa.lua51 import LuaRuntime,lua_type
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai'
BASE=pathlib.Path('/workspace/foreverthai-dev/downloads/ForeverThai-0.462.0-Quest-Skills-PRIVATE-TEST.zip')
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='d36621b9357a33e909777f31fdc5745ddf96aa579add740364ac60011f30cb62'
z=zipfile.ZipFile(BASE);names=[n for n in z.namelist() if not n.endswith('/')];assert len(names)==126
lua=LuaRuntime(unpack_returned_tuples=True);load=lua.eval('function(s,a) local f,e=loadstring(s); assert(f,e); if a then f("ForeverThai",a) end end')
base=lua.table();addon=lua.table()
for n in ['Catalog.lua','Match.lua','SpeechData.lua','Atlas.lua']:
 load(z.read('ForeverThai/'+n).decode(),base);load((RUN/n).read_text(),addon)
lua.execute('UnitName=function() return "CloudTester" end; UnitClass=function() return "Druid", "DRUID" end; UnitRace=function() return "Night Elf" end')
batch1=json.loads((ROOT/'evidence/main-objectives-01.json').read_text());batch2=json.loads((ROOT/'evidence/main-phases-02.json').read_text())
batch4=json.loads((ROOT/'evidence/main-query-04.json').read_text())
batch7=json.loads((ROOT/'evidence/books-labels-07.json').read_text());new_book_pages={(v['book_title'],v['page']) for v in batch7['fields']};new_book_titles=set(batch7['new_book_titles']);historical_steps={(v['quest_id'],v['step_index']) for v in batch7['historical_label_aliases']}
batch8=json.loads((ROOT/'evidence/npc-gossip-08.json').read_text());batch9=json.loads((ROOT/'evidence/npc-templates-09.json').read_text());batch10=json.loads((ROOT/'evidence/public-literals-10.json').read_text());batch12=json.loads((ROOT/'evidence/npc-reuse-12.json').read_text());npc_fields=batch8['fields']+batch9['fields']+[v for v in batch10['fields'] if v['kind']=='npc']+batch12['fields'];new_book_titles.update(v['book_title'] for v in batch10['fields'] if v['kind']=='book');new_book_pages.update((v['book_title'],v['page']) for v in batch10['fields'] if v['kind']=='book');new_npc_ids={v['npc_id'] for v in npc_fields if base.npcs[v['npc_id']] is None};new_npc_lines={(v['npc_id'],v['line_index']) for v in npc_fields}
batch6=json.loads((ROOT/'evidence/main-counters-06.json').read_text())
batch5=json.loads((ROOT/'evidence/main-hyjal-05.json').read_text())
batch3=json.loads((ROOT/'evidence/main-counters-03.json').read_text());dynamic_fields={(x['quest_id'],x['field']) for x in batch3['fields']+batch5['fields']+batch6['fields']}
added={(x['quest_id'],x['field']) for x in batch1['fields']};variants={(x['quest_id'],x['field']) for x in batch2['fields']+batch4['fields']};assert len(added)==34 and len(variants)==15
party_report_path=ROOT/'evidence/party-speech-regression12.json' if (ROOT/'evidence/party-speech-regression12.json').exists() else ROOT/'evidence/party-speech-regression11.json'
party_report=json.loads(party_report_path.read_text()) if party_report_path.exists() else None
def approved_speech_change(path):
 assert party_report and party_report['status']=='passed'
 expected_delta=['ForeverThai/Catalog.lua','ForeverThai/Speech.lua'] if party_report_path.name.endswith('12.json') else ['ForeverThai/Speech.lua']
 assert party_report['changed_runtime_files']==expected_delta
 assert hashlib.sha256(path.read_bytes()).hexdigest()==party_report['runtime_speech_sha256']
 return True
checks=0
def equal(a,b,path=()):
 global checks
 if lua_type(a)=='table':
  assert lua_type(b)=='table',path
  for k,v in a.items():equal(v,b[k],path+(k,))
  for k,v in b.items():
   if a[k] is None:
    allowed=path in [('runs',),('glyphs',)]
    allowed=allowed or path==('npcs',) and k in new_npc_ids or len(path)==3 and path[0]=='npcs' and path[2]=='lines' and (path[1],k) in new_npc_lines
    if path==('books',) and k in new_book_titles:allowed=True
    if len(path)==2 and path[0]=='books' and (path[1],k) in new_book_pages:allowed=True
    if len(path)==4 and path[0]=='quests' and path[2]=='steps' and (path[1],path[3]) in historical_steps and k=='variants':allowed=True
    allowed=allowed or (len(path)==2 and path[0]=='quests' and (path[1],k) in added)
    if len(path)==3 and path[0]=='quests' and (path[1],path[2]) in variants and k=='variants':allowed=True
    if len(path)==3 and path[0]=='quests' and (path[1],path[2]) in dynamic_fields and k=='amount':allowed=True
    if len(path)==4 and path[0]=='quests' and (path[1],path[2]) in variants and path[3]=='variants':allowed=True
    assert allowed,(path,k)
 else:assert a==b,(path,a,b)
 checks+=1
for k,v in base.items():
 if lua_type(v)!='function':equal(v,addon[k],(k,))
# No original files other than the two reviewed append-only data edits may change.
for n in names:
 p=ROOT/'src'/n;assert p.is_file(),n
 if n.endswith('/Catalog.lua'):continue
 if n.endswith('/Speech.lua') and p.read_bytes()!=z.read(n):assert approved_speech_change(p);continue
 if n.endswith('/Atlas.lua'):assert p.read_bytes().startswith(z.read(n));continue
 assert p.read_bytes()==z.read(n),n
prior_manifest=json.loads((ROOT/'evidence/private-package-manifest05.json').read_text())['runtime_manifest']
prior_unchanged=0
for name,digest in prior_manifest.items():
 if name.endswith(('/Catalog.lua','/Atlas.lua')):continue
 if name.endswith('/Speech.lua') and hashlib.sha256((ROOT/'src'/name).read_bytes()).hexdigest()!=digest:assert approved_speech_change(ROOT/'src'/name);continue
 assert hashlib.sha256((ROOT/'src'/name).read_bytes()).hexdigest()==digest,name
 prior_unchanged+=1
for p in RUN.rglob('*.lua'):load(p.read_text(),None)
toc=(RUN/'ForeverThai.toc').read_text();paths=[x.strip().replace('\\','/') for x in toc.splitlines() if x.strip() and not x.startswith('#')];assert all((RUN/x).is_file() for x in paths)
assert '## OptionalDeps: Questie' in toc and 'AlphaWoWSkillsDB' in toc
positives=negatives=0;unique_templates=set();rendered_inputs=set()
def positive(q,field,source,expected):
 global positives
 assert addon.Translate(addon.quests[q][field],source)==expected,(q,field,source)
 positives+=1;rendered_inputs.add((q,field,source))
def negative(entry,source):
 global negatives
 assert addon.Translate(entry,source) is None,source
 negatives+=1
for f in batch1['fields']:
 q=f['quest_id'];entry=addon.quests[q][f['field']];assert base.quests[q][f['field']] is None
 unique_templates.add((q,f['field'],f['english']))
 assert hashlib.sha256(f['english'].encode()).hexdigest()==f['english_sha256']
 assert hashlib.sha256(f['thai'].encode()).hexdigest()==f['thai_sha256']
 # Equal-count probes retain broad magnitude/format coverage. Independent unequal
 # count oracles below prove item identity and catch swapped worldN bindings.
 counts=['1','12','1,234','999999'] if '$' in f['english'] else [None]
 for count in counts:
  source=f['english'];target=f['thai']
  for token in re.findall(r'\$(\d+)oa',source):source=source.replace('$'+token+'oa',count);target=target.replace('{world'+token+'}',count)
  positive(q,f['field'],source,target)
  negative(entry,'UNRELATED '+source);negative(entry,source+' incorrect')
  if '1,234' in source:negative(entry,source.replace('1,234','1,23'))
# Batch 03 reuses reviewed prose and adds only explicit source amount slots.
for f in batch3['fields']+batch5['fields']+batch6['fields']:
 q=f['quest_id'];entry=addon.quests[q][f['field']];assert base.quests[q][f['field']] is not None and base.quests[q][f['field']].amount is None
 unique_templates.add((q,f['field'],f['english']))
 for count in ['1','12','1,234','999999']:
  source=f['english'];target=f['thai']
  for token in re.findall(r'\$(\d+)oa',source):source=source.replace('$'+token+'oa',count);target=target.replace('{world'+token+'}',count)
  positive(q,f['field'],source,target);negative(entry,'UNRELATED '+source);negative(entry,source+' incorrect')
  if '1,234' in source:negative(entry,source.replace('1,234','1,23'))
# New literal-race variants must work for multiple identities without substituting race.
for f in batch2['fields']:
 q=f['quest_id'];assert '$' not in f['english'] and '{race}' not in f['thai'];unique_templates.add((q,f['field'],f['english']))
 for race in ['Night Elf','Human','Skyborne']:
  lua.globals().UnitRace=lambda unit,race=race:race
  positive(q,f['field'],f['english'],f['thai'])
 negative(addon.quests[q][f['field']],f['english']+' incorrect')
 negative(addon.quests[q][f['field']],f['english'].replace('skyborne','unverified-word'))
lua.execute('UnitRace=function() return "Night Elf" end')
# Query tokens are explicit, unlike uploader-normalized class/race replacements.
query_variant_executions=0
for f in batch4['fields']:
 unique_templates.add((f['quest_id'],f['field'],f['english']))
 branches=[f['english']]
 while any(re.search(r'\$g([^:;]*):([^;]*);',v,re.I) for v in branches):
  expanded=[]
  for v in branches:
   m=re.search(r'\$g([^:;]*):([^;]*);',v,re.I)
   expanded.extend([v[:m.start()]+choice+v[m.end():] for choice in m.groups()] if m else [v])
  branches=expanded
 for name,cls,cls_id,race,thai_cls,thai_race in [('CloudTester','Druid','DRUID','Night Elf','ดรูอิด','ไนต์เอลฟ์'),('SecondTester','Mage','MAGE','Human','จอมเวท','มนุษย์'),('ThirdTester','Warrior','WARRIOR','Skyborne','นักรบ','สกายบอร์น')]:
  lua.execute('UnitName=function() return '+json.dumps(name)+' end; UnitClass=function() return '+json.dumps(cls)+','+json.dumps(cls_id)+' end; UnitRace=function() return '+json.dumps(race)+' end')
  for branch in branches:
   source=re.sub(r'\$b','\n',branch,flags=re.I)
   for token,value in [('n',name),('c',cls),('r',race)]:source=re.sub(r'\$'+token,value,source,flags=re.I)
   target=f['thai'].replace('{name}',name).replace('{class}',thai_cls).replace('{race}',thai_race)
   positive(f['quest_id'],f['field'],source,target);query_variant_executions+=1
   negative(addon.quests[f['quest_id']][f['field']],source+' incorrect')
   if '$n' in branch.lower():negative(addon.quests[f['quest_id']][f['field']],source.replace(name,'WrongPlayer'))
lua.execute('UnitName=function() return "CloudTester" end; UnitClass=function() return "Druid","DRUID" end; UnitRace=function() return "Night Elf" end')
# Static whole-sentence expectations are separately authored in the fixture file.
# Mutate either source bindings OR Thai slots to ensure the oracle detects a swap.
fixtures=json.loads((ROOT/'tests/objective-counts.json').read_text())['fixtures'];counter_cases=mutation_detections=0
source_fields={f['quest_id']:f for f in batch1['fields']+batch3['fields']+batch5['fields']+batch6['fields']}
for fixture in fixtures:
 q=fixture['quest_id'];entry=addon.quests[q]['objective'];dynamic=entry.amount or entry
 assert 'W1' in dynamic[1] and 'W2' in dynamic[1]
 if q in source_fields:
  record=source_fields[q]['source_record'];by_id={o['objectId']:o for o in record['objectives']}
  if 'source_item_ids' in fixture:assert set(fixture['source_item_ids'])==set(by_id)
  if any(c.get('source_record_amounts') for c in fixture['cases']):
   assert [by_id[i]['amount'] for i in fixture['source_item_ids']]==[2,1]
  unique_templates.add((q,'objective',source_fields[q]['english']))
 else:
  # These two pre-existing objectives extend coverage to reverse token order.
  unique_templates.add((q,'objective',fixture['source_template']))
 token_ids=sorted(set(int(v) for v in re.findall(r'\$(\d+)oa',fixture['source_template'])))
 mutants=[]
 for first,second in itertools.combinations(token_ids,2):
  swapped_signature=re.sub(r'\bW([0-9]+)\b',lambda m:'W'+str(second if int(m[1])==first else first if int(m[1])==second else int(m[1])),dynamic[1])
  swapped_target=dynamic[2].replace('{world'+str(first)+'}','{SWAP}').replace('{world'+str(second)+'}','{world'+str(first)+'}').replace('{SWAP}','{world'+str(second)+'}')
  mutants.extend([lua.table_from([swapped_signature,dynamic[2]]),lua.table_from([dynamic[1],swapped_target])])
 for case in fixture['cases']:
  positive(q,'objective',case['source'],case['expected']);counter_cases+=1
  for mutant in mutants:
   assert addon.Translate(mutant,case['source'])!=case['expected'],('Oracle missed swapped bindings',q)
   mutation_detections+=1
  negative(entry,case['source'].replace('1,234','1,23')) if '1,234' in case['source'] else None
# Low-level source holds: trainer names/classes stay literal across identities.
# The user's partial page observation is not imported as a raw/hash source.
low_query=json.loads((ROOT/'work/eg/data/wowf/1.60.1.70888/quests.enUS.json').read_text())['quests']
low_binding_checks=0
for q,literal in [(92479,'hunter trainer'),(98574,'priest trainer'),(98581,'shaman trainer'),(98601,'a paladin like yourself')]:
 source=low_query[str(q)]['description'];assert literal in source
 entry=addon.quests[q].description
 assert 'C' not in str(entry[1]).split(),q
 for cls,cls_id in [('Druid','DRUID'),('Mage','MAGE'),('Warrior','WARRIOR')]:
  lua.execute('UnitClass=function() return '+json.dumps(cls)+','+json.dumps(cls_id)+' end')
  rendered=re.sub(r'\$n','CloudTester',source,flags=re.I)
  assert addon.Translate(entry,rendered) is not None,q
  assert addon.Translate(entry,rendered.replace(literal,'unverified trainer')) is None,q
  low_binding_checks+=1
lua.execute('UnitClass=function() return "Druid","DRUID" end')
# Every new Thai run has valid glyphs; all existing run values were checked above.
for f in batch1['fields']+batch2['fields']+batch3['fields']+batch4['fields']+batch5['fields']+batch6['fields']:
 for run in re.findall(r'[\u0e00-\u0e7f]+',f['thai']):
  assert addon.runs[run] is not None,(f['quest_id'],run)
  for _,idx in addon.runs[run].items():
   glyph=addon.glyphs[idx];assert glyph and glyph[4]>0 and glyph[6]>0
images={}
for p in (RUN/'Fonts').glob('*.tga'):
 with Image.open(p) as im:im.load();images[p.name]=im.size
for _,g in addon.glyphs.items():
 w,h=images[f'Thai{g[1]}.tga'];assert 0<=g[2] and g[2]+g[4]<=w and 0<=g[3] and g[3]+56<=h
result=dict(baseline_components_retained=126,candidate05_unchanged_component_hashes=prior_unchanged,new_book_page_fields_batch07=len(batch7["fields"]),historical_label_aliases_batch07=len(historical_steps),byte_identical_baseline_files=sum((ROOT/"src"/n).read_bytes()==z.read(n) for n in names),new_objective_fields_batch01=len(added),new_source_variants_batch02=len(batch2["fields"]),new_source_variants_batch04=len(batch4["fields"]),new_or_changed_prose_batch04=4,query_variant_executions=query_variant_executions,low_level_literal_binding_checks=low_binding_checks,new_dynamic_forms_batch03=len(batch3["fields"]),new_dynamic_forms_batch05=len(batch5["fields"]),new_dynamic_forms_batch06=len(batch6["fields"]),unchanged_data_values_checked=checks,unique_source_cases=len(unique_templates),distinct_rendered_positive_inputs=len(rendered_inputs),parameterized_positive_executions=positives,negative_executions=negatives,independent_unequal_counter_cases=counter_cases,swapped_binding_mutations_detected=mutation_detections,lua_files_compiled=len(list(RUN.rglob('*.lua'))),toc_paths=len(paths),font_pages_decoded=len(images),old_glyphs=len(base.glyphs),old_runs=sum(1 for _ in base.runs.items()),new_glyphs=len(addon.glyphs)-len(base.glyphs),new_runs=sum(1 for k,_ in addon.runs.items() if base.runs[k] is None),scope='Current Cloud checks. Unique source cases are quest/field/template tuples; parameterized executions are tests, not added translations. Recovered nine-case Skill UI suite is reported separately; NPC686 runtime replay is reported separately in npc-cloud-replay05.json; fresh pinned API-source proof is reported separately in npc-api-proof.json; not in-game verification.')
(ROOT/'evidence/cloud-regression.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
