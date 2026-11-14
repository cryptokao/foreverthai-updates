"""Restricted read-only Harvest audit; no third-party Lua/library execution."""
import pathlib,json,hashlib,collections,re,csv
from lupa.lua51 import LuaRuntime
from harvest_literals import parse_harvest
from source_classification import classify_title
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'tests/source_inputs/libquestdb-010';OUT=ROOT/'evidence';sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((SOURCE/'manifest.json').read_text())
for item in manifest['files']:
 raw=(SOURCE/item['path']).read_bytes();assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
core=parse_harvest((SOURCE/'QuestDB/Data/Forever/_core/Harvest.lua').read_text(),'core');text=parse_harvest((SOURCE/'QuestDB/Data/Forever/enUS/HarvestText.lua').read_text(),'text');assert set(core)==set(text) and len(text)==775
lua=LuaRuntime(unpack_returned_tuples=True);addon=lua.table();load=lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
# Execute only our reviewed runtime's data/matcher, never the source library.
for n in ['Catalog','Match']:load((ROOT/'src/ForeverThai'/f'{n}.lua').read_text(),addon)
lua.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
runtime={int(q) for q,_ in addon.quests.items()};union={int(v['quest_id']) for v in csv.DictReader((OUT/'source-id-union.csv').open())};queries=json.loads((ROOT/'work/eg/data/wowf/1.60.1.70888/quests.enUS.json').read_text())['quests'];counts=collections.Counter();differences=[];candidates=[]
def match(entry,source):
 if entry is None:return False
 s=re.sub(r'\$b','\n',source,flags=re.I)
 for t,value in [('n','CloudTester'),('c','Druid'),('r','Night Elf')]:s=re.sub(r'\$'+t,value,s,flags=re.I)
 return addon.Translate(entry,s) is not None
for q,encoded in text.items():
 parts=encoded.split('\x1f');parts+=['']*max(0,10-len(parts));assert not any(parts[i] for i in [1,3,4,5]),('Unadvertised accept/reward/progress/end prose',q)
 level_parts=core[q].split('\x1f');level=int(level_parts[1]) if len(level_parts)>1 and level_parts[1].isdigit() else None;native=queries.get(str(q),{});quest=addon.quests[q] if q in runtime else None
 for field,source in [('title',parts[0]),('objective',parts[2])]+[('objective_line'+str(i+1),parts[6+i]) for i in range(4)]:
  if not source:continue
  counts['present_'+field]+=1;placeholder=source.strip().lower() in ['log','description','null'] or source.startswith('[PH]')
  if field in ['title','objective']:
   supported=match(quest[field] if quest else None,source);current=native.get('title' if field=='title' else 'objectivesText');current_match=current is not None and ' '.join(current.split())==' '.join(source.split())
  else:
   supported=False
   if quest:
    for _,entry in (quest.steps or lua.table()).items():
     if match(entry,source):supported=True;break
    for _,labels in (quest.objectiveLabels or lua.table()).items():
     if labels[source] is not None:supported=True
   if quest and not supported:supported=match(quest.objective,source)
   current_match=any(o.get('text')==source for o in native.get('objectives',[]));current=source if current_match else None
  if classify_title(parts[0],q) is not None:status='hold_explicit_disabled_or_development_marker'
  elif placeholder:status='hold_placeholder_not_prose'
  elif supported:status='already_supported'
  elif current_match:status='current_own_id_source_candidate'
  else:status='hold_snapshot_or_current_binding_unconfirmed'
  counts[status]+=1
  if status!='already_supported':
   row=dict(quest_id=q,level=level,title=parts[0],field=field,english=source,source_sha256=sha(source.encode()),status=status,current_own_id_match=current_match,current_name=native.get('title'),runtime_field_present=(quest is not None and quest[field] is not None) if field in ['title','objective'] else None)
   differences.append(row)
   if status=='current_own_id_source_candidate':candidates.append(row)
summary=dict(source='Pimptasty / LibQuestDB 0.1.0',license='MIT',original_release=manifest['original_release_url'],original_zip_sha256=manifest['original_sha256'],supplement_sha256='d28107f58f0e6facdd65de59b5e46217a096002695cc829a52e3a2dd05038a16',harvest_date='2026-09-28',interface=16001,exact_client_build=None,core_ids=len(core),text_ids=len(text),outside_catalog=sorted(set(text)-runtime),outside_prior_union=sorted(set(text)-union),field_counts=dict(counts),current_own_id_candidates=candidates,forbidden_prose_fields_found=0,library_or_third_party_scripts_executed=False,new_translations=0,new_runtime_fields=0,original_zip_rehashed_on_cloud=False,scope='Only literal harvested title/log-summary/objective lines. No Classic dump accept/progress/completion imported; not a whole-game denominator or live verification.')
(OUT/'harvest-source-audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');(OUT/'harvest-source-differences.json').write_text(json.dumps(sorted(differences,key=lambda x:(x['level'] if x['level'] is not None else 999,x['quest_id'],x['field'])),ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2))
