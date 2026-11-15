"""One new schema-qualified cache-NCR subgroup join; not a repeat of old11144 audit."""
import json,pathlib,re,hashlib,zipfile,time,collections
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
doc=json.loads((R/'main27-qualified-cache-private.json').read_text(encoding='utf-8'));rows=doc['rows'];assert len(rows)==1057
base=R/'package-main25-26/build-0.468.0/ForeverThai-0.468.0-main25-26-PRIVATE-TEST.zip';assert sha(base.read_bytes())=='90b85b81dc4f9dc4d94b4349ec7c64a90889deedf8340c8976806115fb5441df'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
def render(s):
 s=re.sub(r'\$[bB]','\n',s)
 return re.sub(r'\$([nNcCrR])',lambda m:{'n':'CloudTester','c':'Druid','r':'Night Elf'}[m[1].lower()],s)
def signature(s):
 s=re.sub(r'\$[bB]','\n',s).replace('\u00a0',' ');s=re.sub(r'[ \t\r\n\f\v]+',' ',s).strip(' ');parts=[]
 for value in re.split(r'(\$[nNcCrR])',s):
  if not value:continue
  if re.fullmatch(r'\$[nNcCrR]',value):parts.append(value[1].upper());continue
  b=value.encode();x=y=0
  for c in b:x=(x*257+c)%2147483647;y=(y*131+c)%2147483629
  parts.append(f'{len(b)}:{x}:{y}')
 return ' '.join(parts)
counts=collections.Counter();safe=[];candidates=[]
for r in rows:
 en=r['english'];assert sha(en.encode())==r['english_sha256'];assert not re.sub(r'\$[bBnNcCrR]','',en).count('$')
 q,f=r['quest_id'],r['field'];assert f in ['description','objective'];quest=a.quests[q];entry=quest[f] if quest else None
 value=a.Translate(entry,render(en));status='supported_under_documented_role_fixture' if value is not None else 'unmatched_needs_full_meaning_reuse_class_scope_review' if entry is not None else 'missing_field_needs_full_meaning_review'
 counts[status]+=1
 meta={k:v for k,v in r.items() if k!='english'};meta.update(schema_qualified_status=status,expected_dynamic_signature=signature(en),current_profile_is_synthetic_NOT_inventory_or_quest_eligibility=True)
 safe.append(meta)
 if value is None:candidates.append(dict(r,expected_dynamic_signature=signature(en),candidate_status=status,existing_canonical_thai=entry[2] if entry else None,existing_canonical_signature=entry[1] if entry else None))
report=dict(batch='MAIN27 schema-qualified query subgroup only',new_input_is='New applicability proof from primary DATASETS.md lines582-594; no new upstream dataset/English claim',source_pin='ea970da071079b32e56f349e09648ff0e314b351',documentation_blob='8fee3e320e15fdd2e782c93dc2fb2c280ec55654',baseline_zip_sha256=sha(base.read_bytes()),qualified_cache_rows=len(rows),qualification_counts=doc['counts'],result_counts=dict(counts),rows=safe,new_thai_fields=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limits=['Explicit primary raw cache slot semantics, not roles inferred from normalized captured phase or story','Only current70938 exact query description/objective fields; gender/counter/adjacent-letter/noData-only discrepancies excluded','Synthetic profile matching is NOT evidence of actual class/race eligibility, enabled inventory or a new translation gap; unmatched candidates require full source/Thai review','No old literals, MAIN25/26 joins,old Skill/NPC/full font/full game tests repeated','Raw captured-phase/name fragments stay private'])
(R/'main27-cache-ncr-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(R/'main27-cache-ncr-candidates-private.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['rows']},ensure_ascii=False))
print('CANDIDATE_METADATA',json.dumps([dict(quest_id=r['quest_id'],field=r['field'],level=r['level'],title=r['title'],bytes=len(r['english'].encode()),status=r['candidate_status']) for r in candidates[:35]],ensure_ascii=False))
