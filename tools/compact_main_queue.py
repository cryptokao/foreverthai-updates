"""Compact actionable/blocked main-source variants; exclude no-source inventory rows."""
import pathlib,json,hashlib,re,collections
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
ROOT=pathlib.Path(__file__).resolve().parents[1];sha=lambda s:hashlib.sha256(s.encode()).hexdigest();index=collections.defaultdict(list)
def add(q,field,text,kind,build,origin):
 index[int(q),field,sha(text)].append(dict(english=text,source_kind=kind,build=build,origin=origin))
p=ROOT/'work/eg/data/wowf/1.60.1.70888/quests.enUS.json';query=json.loads(p.read_text())['quests'];EGPIN='164bd1e2d89579ada4ee5e2de7e5fd4db684a9f1';VOPIN='d562be626b9970fa8575170950ff61076dc47df0'
for q,v in query.items():
 for f,k in [('title','title'),('objective','objectivesText'),('description','description')]:
  if v.get(k):add(q,f,v[k],'current_query_explicit','1.60.1.70888',str(p.relative_to(ROOT/'work/eg')))
for p in (ROOT/'work/eg/data/wowf').glob('*/texts.enUS.json'):
 for q,phases in json.loads(p.read_text()).get('quests',{}).items():
  for phase,entries in phases.items():
   field={'accept':'description','complete':'completion','progress':'progress','objectives':'objective'}.get(phase)
   if field:
    for e in entries:add(q,field,e['text'],'EG_captured_text',p.parent.name,str(p.relative_to(ROOT/'work/eg')))
for key,v in json.loads((ROOT/'work/forever-vo/tools/data/capture.json').read_text())['quests'].items():
 field={'accept':'description','complete':'completion','progress':'progress'}.get(v['event'])
 if field:add(v['questID'],field,v['text'],'VO_normalized_capture',v.get('build'),f"{v.get('origin')}:{key}")
for p in sorted((ROOT/'work').glob('issue-*-decoded.json')):
 d=json.loads(p.read_text())
 for i,v in enumerate(d['lines']):
  field={'accept':'description','complete':'completion','progress':'progress'}.get(v.get('e'))
  if v.get('k')=='quest' and field:add(v['q'],field,v['x'],'VO_normalized_capture',d.get('build'),f'{p.stem}:{i}')
l=LuaRuntime(unpack_returned_tuples=True);a=l.table();load=l.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for name in ['Catalog','Match']:load((ROOT/'src/ForeverThai'/f'{name}.lua').read_text(),a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
def supported(entry,text):
 variants=[text]
 while any(re.search(r'\$g([^:;]*):([^;]*);',v,re.I) for v in variants):
  out=[]
  for v in variants:
   m=re.search(r'\$g([^:;]*):([^;]*);',v,re.I);out.extend([v[:m.start()]+c+v[m.end():] for c in m.groups()] if m else [v])
  variants=out
 for v in variants:
  v=re.sub(r'\$b','\n',v,flags=re.I);v=re.sub(r'\$\d+oa','123',v)
  for token,value in [('n','CloudTester'),('c','Druid'),('r','Night Elf')]:v=re.sub(r'\$'+token,value,v,flags=re.I)
  if not a.Translate(entry,v):return False
 return True
rows=[];seen=set()
for row in json.loads((ROOT/'evidence/main-source-queue.json').read_text()):
 q=row['quest_id'];f=row['field'];entry=a.quests[q] and a.quests[q][f];sources=[]
 for ref in row.get('unmatched_sources',[]):
  candidates=index[q,f,ref['sha256']];assert candidates,(q,f,ref)
  s=next((v for v in candidates if v['source_kind']=='current_query_explicit'),candidates[0])
  if supported(entry,s['english']):continue
  source=dict(s,sha256=ref['sha256'],commit=EGPIN if not s['source_kind'].startswith('VO') else VOPIN)
  if q in [257,258]:source.pop('english');source['reason_text_withheld']='Capture has unredacted player literal; full source hash retained, no typed-name assumption.'
  sources.append(source)
 if row.get('placeholder_versions'):
  for (iq,field,digest),versions in index.items():
   if iq==q and field==f:
    for s in versions:
     if not s['english'].strip() or s['english'].strip().lower() in ['description','log','null'] or s['english'].startswith('[PH]'):
      sources.append(dict(s,sha256=digest,commit=EGPIN if not s['source_kind'].startswith('VO') else VOPIN));break
 if not sources:continue
 key=q,f
 if key in seen:continue
 seen.add(key);current=next((s for s in sources if s['source_kind']=='current_query_explicit'),None)
 if any(not s.get('english','').strip() or s.get('english','').strip().lower() in ['description','log','null'] or s.get('english','').startswith('[PH]') for s in sources if 'english' in s):category='blocked_placeholder';reason='Available record is empty/developer placeholder, not usable quest prose';action='Need a complete own-ID real main field; do not copy a sibling quest.'
 elif current and re.search(r'\$\d+oa',current['english']) and not re.search(r'\$[ncrg]|\|5',current['english'],re.I) and entry is not None:
  category='actionable_explicit_query_amount';reason='Explicit objective-amount tokens in current query; prior reviewed wording exists';action='Review named objects and independently bind each worldN; preserve fixed wording/aliases. Count as source form, not new prose.'
 elif any(s['source_kind']!='current_query_explicit' and re.search(r'\$[ncr]',s.get('english',''),re.I) for s in sources):category='blocked_typed_identity';reason='Uploader/capture token may replace a fixed trainer/general race/third-party noun';action='Need exact own-ID primary typed template or unredacted current rendered text and independent binding proof; preserve fixed references.'
 elif current and '|5' in current['english']:category='blocked_rendering_binding';reason='Query has a declension/rendering marker; exact final client text is unproven';action='Need current rendered full body or pinned caller/formatter proof, not guessed grammar stripping.'
 elif any('Les entendez-vous' in s.get('english','') for s in sources):category='blocked_non_enUS';reason='Available capture is French, not corroborated English';action='Need full enUS own-ID phase; retain existing English fallback.'
 else:category='blocked_old_or_normalized_source';reason='Existing supported canonical differs from an old/normalized/unredacted source variant';action='Need full current own-ID text with exact punctuation/slots; do not repair source by similarity.'
 rows.append(dict(quest_id=q,level=row['level'] if row['level']!='' else None,field=f,category=category,reason=reason,next_action=action,sources=sources))
# Explicit historical fields really present in a new snapshot remain visible,
# but current repurposed records do not establish that these old phases exist.
for row in json.loads((ROOT/'evidence/additional-source-audit.json').read_text())['missing_runtime_fields']:
 if row['quest_id'] not in [5641,5679]:continue
 rows.append(dict(quest_id=row['quest_id'],level=row['level'],field=row['field'],category='blocked_old_snapshot_repurposed_id',reason='Historical priest travel objective has no matching current query field; current title/quest type changed',next_action='Need current own-ID objective body or confirmation the old phase still exists; do not import Classic travel text.',sources=[dict(source_kind='curated_historical_snapshot',build=None,commit='9f4c5aac2d077854d7f4a2bdc2f8eceb8d7b23af',sha256=row['source_text_sha256'],current_title=row['current_name'])]))
rows.sort(key=lambda x:(x['level'] if x['level'] is not None else 999,x['quest_id'],x['field']));counts=collections.Counter(x['category'] for x in rows);actionable=[x for x in rows if x['category'].startswith('actionable_')]
report=dict(scope='Only unresolved main field variants with actual source records plus explicit placeholders/two historical repurposed-ID fields. No-source inventory rows and unproven hypothetical phases are excluded.',categories=dict(counts),actionable_fields=len(actionable),blocked_fields=len(rows)-len(actionable),new_prose_ready=0,quantity_forms_are_not_new_translations=True,excluded_no_source_inventory_rows=json.loads((ROOT/"evidence/quest-field-inventory-summary.json").read_text())["evidence_breakdown"]["fields_with_no_available_source_record"],source_only_outside_catalog_queue='source-ids-outside-catalog.json; 192 usage/test/metadata holds, not expanded into hypothetical fields',records=rows)
(ROOT/'evidence/compact-main-queue.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
print([(x['quest_id'],x['level'],x['field']) for x in actionable])
