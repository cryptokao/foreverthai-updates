"""Audit the scoped runtime-ID inventory against pinned public source files.

This is not an authoritative list of currently playable Forever quests.
No player capture text or identity is copied into the public inventory.
"""
import csv,collections,hashlib,json,pathlib,re
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];EG=ROOT/'work/eg';VO=ROOT/'work/forever-vo';OUT=ROOT/'evidence'
lua=LuaRuntime(unpack_returned_tuples=True);addon=lua.table();load=lua.eval('function(s,a) assert(loadstring(s))("ForeverThai",a) end')
for n in ['Catalog','Match']:load((ROOT/'src/ForeverThai'/f'{n}.lua').read_text(),addon)
lua.execute('UnitName=function() return "CloudTester" end; UnitClass=function() return "Druid","DRUID" end; UnitRace=function() return "Night Elf" end')
qp=EG/'data/wowf/1.60.1.70888/quests.enUS.json';queries=json.loads(qp.read_text())['quests'];sources=collections.defaultdict(list)
def add(q,f,text,origin,kind):
 if int(q) not in ids:return
 item=(text,origin,kind)
 if not any(x[0]==text for x in sources[int(q),f]):sources[int(q),f].append(item)
def forms(text):
 texts=[text]
 while any(re.search(r'\$g([^:;]*):([^;]*);',s,re.I) for s in texts):
  out=[]
  for s in texts:
   m=re.search(r'\$g([^:;]*):([^;]*);',s,re.I)
   out.extend([s[:m.start()]+v+s[m.end():] for v in m.groups()] if m else [s])
  texts=out
 for s in texts:
  s=re.sub(r'\$b','\n',s,flags=re.I);s=re.sub(r'\$\d+oa','123',s)
  for k,v in [('n','CloudTester'),('c','Druid'),('r','Night Elf')]:s=re.sub(r'\$'+k,v,s,flags=re.I)
  yield s
ids={int(q) for q,_ in addon.quests.items()}
for q,v in queries.items():
 for f,k in [('title','title'),('objective','objectivesText'),('description','description')]:
  if v.get(k):add(q,f,v[k],str(qp.relative_to(EG)),'query')
for p in sorted((EG/'data/wowf').glob('*/texts.enUS.json'),reverse=True):
 for q,phases in json.loads(p.read_text()).get('quests',{}).items():
  for phase,entries in phases.items():
   f={'accept':'description','complete':'completion','progress':'progress','objectives':'objective'}.get(phase)
   if f:
    for e in entries:add(q,f,e['text'],str(p.relative_to(EG)),'captured_text')
for key,v in json.loads((VO/'tools/data/capture.json').read_text())['quests'].items():
 f={'accept':'description','complete':'completion','progress':'progress'}.get(v['event'])
 if f:add(v['questID'],f,v['text'],f"Forever-VO/{v.get('origin','capture')}:{key}",'normalized_capture')
for p in sorted((ROOT/'work').glob('issue-*-decoded.json')):
 for i,v in enumerate(json.loads(p.read_text())['lines']):
  f={'accept':'description','complete':'completion','progress':'progress'}.get(v.get('e'))
  if v.get('k')=='quest' and f:add(v['q'],f,v['x'],f'Forever-VO/{p.stem}:{i}','normalized_capture')
rows=[];queue=[];counts=collections.Counter();missing=collections.Counter();unsupported=collections.Counter()
for q in sorted(ids,key=lambda q:(queries.get(str(q),{}).get('level',999),q)):
 v=queries.get(str(q),{});title=v.get('title','');usage='query_record_present_usage_unverified' if v else 'current_usage_unconfirmed'
 test=bool(re.search(r'(?i)unused|never used|<nyi|<txt|test|chow|reuse|\[dnt\]|temp disabled',title))
 for field in ['title','objective','description','progress','completion']:
  entry=addon.quests[q][field];records=sources[q,field];supported=unmatched=placeholders=0;refs=[];unmatched_refs=[]
  for text,origin,kind in records:
   digest=hashlib.sha256(text.encode()).hexdigest();refs.append(origin+'#sha256='+digest)
   if not text.strip() or text.strip() in ['Description','Log'] or text.startswith('[PH]'):
    placeholders+=1;continue
   if entry and all(addon.Translate(entry,s) is not None for s in forms(text)):supported+=1
   else:unmatched+=1;unmatched_refs.append(dict(origin=origin,sha256=digest,kind=kind,has_tokens=bool(re.search(r'\$[ncrg]|\$\d+oa',text,re.I))))
  if test:status='current_usage_unconfirmed_test_or_disabled'
  elif supported and not unmatched:status='source_and_translation_match'
  elif unmatched:
   if entry:status='source_variant_or_token_requires_review'
   elif any(x['has_tokens'] or x['kind']=='normalized_capture' for x in unmatched_refs):status='missing_source_or_token_evidence'
   else:status='source_available_untranslated'
  elif placeholders:status='missing_source_placeholder_or_empty'
  else:status='missing_source_or_token_evidence'
  counts[status]+=1
  if entry is None:missing[field]+=1
  if unmatched:unsupported[field]+=unmatched
  row=dict(quest_id=q,level=v.get('level',''),zone_area_id=v.get('zoneAreaId',''),field=field,status=status,runtime_translation_present=entry is not None,current_usage=usage,unique_source_versions=len(records),supported_versions=supported,unmatched_versions=unmatched,placeholder_versions=placeholders,source_refs=' | '.join(refs));rows.append(row)
  if unmatched or entry is None:queue.append({k:row[k] for k in row if k!='source_refs'}|dict(unmatched_sources=unmatched_refs))
with (OUT/'quest-field-inventory.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
summary=dict(scope='All IDs in the editable runtime Catalog, five main fields per ID. Query/capture provenance does not prove current playability. Counts are this inventory only; not whole-game completion.',runtime_quest_ids=len(ids),field_rows=len(rows),statuses=dict(counts),missing_runtime_fields=dict(missing),unmatched_source_versions_by_field=dict(unsupported),current_query_sha256=hashlib.sha256(qp.read_bytes()).hexdigest(),eg_commit='164bd1e2d89579ada4ee5e2de7e5fd4db684a9f1',vo_commit='d562be626b9970fa8575170950ff61076dc47df0')
(OUT/'quest-field-inventory-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(OUT/'main-source-queue.json').write_text(json.dumps(queue,indent=2)+'\n');print(json.dumps(summary,indent=2))
