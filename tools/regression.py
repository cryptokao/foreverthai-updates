"""Cloud structural preservation, source matching and independent counter regression."""
import hashlib,json,pathlib,re,zipfile
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
added={(x['quest_id'],x['field']) for x in batch1['fields']};variants={(x['quest_id'],x['field']) for x in batch2['fields']};assert len(added)==34 and len(variants)==2
checks=0
def equal(a,b,path=()):
 global checks
 if lua_type(a)=='table':
  assert lua_type(b)=='table',path
  for k,v in a.items():equal(v,b[k],path+(k,))
  for k,v in b.items():
   if a[k] is None:
    allowed=path in [('runs',),('glyphs',)] or (len(path)==2 and path[0]=='quests' and (path[1],k) in added)
    if len(path)==3 and path[0]=='quests' and (path[1],path[2]) in variants and k=='variants':allowed=True
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
 if n.endswith('/Atlas.lua'):assert p.read_bytes().startswith(z.read(n));continue
 assert p.read_bytes()==z.read(n),n
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
# New literal-race variants must work for multiple identities without substituting race.
for f in batch2['fields']:
 q=f['quest_id'];assert '$' not in f['english'] and '{race}' not in f['thai'];unique_templates.add((q,f['field'],f['english']))
 for race in ['Night Elf','Human','Skyborne']:
  lua.globals().UnitRace=lambda race=race:race
  positive(q,f['field'],f['english'],f['thai'])
 negative(addon.quests[q][f['field']],f['english']+' incorrect')
 negative(addon.quests[q][f['field']],f['english'].replace('skyborne','unverified-word'))
lua.execute('UnitRace=function() return "Night Elf" end')
# Static whole-sentence expectations are separately authored in the fixture file.
# Mutate either source bindings OR Thai slots to ensure the oracle detects a swap.
fixtures=json.loads((ROOT/'tests/objective-counts.json').read_text())['fixtures'];counter_cases=mutation_detections=0
source_fields={f['quest_id']:f for f in batch1['fields']}
for fixture in fixtures:
 q=fixture['quest_id'];entry=addon.quests[q]['objective'];dynamic=entry.amount or entry
 assert 'W1' in dynamic[1] and 'W2' in dynamic[1]
 if q in source_fields:
  record=source_fields[q]['source_record'];by_id={o['objectId']:o for o in record['objectives']}
  assert set(fixture['source_item_ids'])==set(by_id)
  if any(c.get('source_record_amounts') for c in fixture['cases']):
   assert [by_id[i]['amount'] for i in fixture['source_item_ids']]==[2,1]
  unique_templates.add((q,'objective',source_fields[q]['english']))
 else:
  # These two pre-existing objectives extend coverage to reverse token order.
  unique_templates.add((q,'objective',fixture['source_template']))
 swapped_signature=re.sub(r'\bW([12])\b',lambda m:'W'+str(3-int(m[1])),dynamic[1])
 swapped_target=dynamic[2].replace('{world1}','{SWAP}').replace('{world2}','{world1}').replace('{SWAP}','{world2}')
 mutants=[lua.table_from([swapped_signature,dynamic[2]]),lua.table_from([dynamic[1],swapped_target])]
 for case in fixture['cases']:
  positive(q,'objective',case['source'],case['expected']);counter_cases+=1
  for mutant in mutants:
   assert addon.Translate(mutant,case['source'])!=case['expected'],('Oracle missed swapped bindings',q)
   mutation_detections+=1
  negative(entry,case['source'].replace('1,234','1,23')) if '1,234' in case['source'] else None
# Every new Thai run has valid glyphs; all existing run values were checked above.
for f in batch1['fields']+batch2['fields']:
 for run in re.findall(r'[\u0e00-\u0e7f]+',f['thai']):
  assert addon.runs[run] is not None,(f['quest_id'],run)
  for _,idx in addon.runs[run].items():
   glyph=addon.glyphs[idx];assert glyph and glyph[4]>0 and glyph[6]>0
images={}
for p in (RUN/'Fonts').glob('*.tga'):
 with Image.open(p) as im:im.load();images[p.name]=im.size
for _,g in addon.glyphs.items():
 w,h=images[f'Thai{g[1]}.tga'];assert 0<=g[2] and g[2]+g[4]<=w and 0<=g[3] and g[3]+56<=h
result=dict(baseline_components_retained=126,byte_identical_baseline_files=124,new_objective_fields_batch01=len(added),new_source_variants_batch02=len(variants),unchanged_data_values_checked=checks,unique_source_cases=len(unique_templates),distinct_rendered_positive_inputs=len(rendered_inputs),parameterized_positive_executions=positives,negative_executions=negatives,independent_unequal_counter_cases=counter_cases,swapped_binding_mutations_detected=mutation_detections,lua_files_compiled=len(list(RUN.rglob('*.lua'))),toc_paths=len(paths),font_pages_decoded=len(images),old_glyphs=len(base.glyphs),old_runs=sum(1 for _ in base.runs.items()),new_glyphs=len(addon.glyphs)-len(base.glyphs),new_runs=sum(1 for k,_ in addon.runs.items() if base.runs[k] is None),scope='Current Cloud checks. Unique source cases are quest/field/template tuples; parameterized executions are tests, not added translations. Not the missing historical 686 speech/9 Skills harness or in-game verification.')
(ROOT/'evidence/cloud-regression.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
