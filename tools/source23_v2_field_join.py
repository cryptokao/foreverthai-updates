"""One targeted own-ID join for actual161-record/483field safe metadata only.
No WDB decoder/source refresh, role/counter expansion, book data or runtime writes.
"""
import pathlib,json,re,hashlib,subprocess,collections,gzip
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();META=R/'source_inputs/source23-v2-field-metadata-safe.json';m=json.loads(META.read_text());assert m['actual_invocations']==1 and m['envelopes_validated']==217
qualified=[v for v in m['records'] if v['status']=='unique_structure_raw_only_pending_review'];assert len(qualified)==161;ids={v['qid'] for v in qualified};Q='4dbb82440a27856f8dccf57094a5d792cdc7cc9b';E='e0f8585914c134d9cb5d76756bd065b1e3e92ece';V='d562be626b9970fa8575170950ff61076dc47df0';index=collections.defaultdict(dict);pins=[];levels={};zones={};classes={};l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:l.execute((R/f'src/ForeverThai/{n}.lua').read_text(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
CAT=sha((R/'src/ForeverThai/Catalog.lua').read_bytes());assert CAT=='43ec92f88113114aef4918dcbe10c0bb89b7f222d6658dc5183c08c706f94f50'
def git(repo,ref,path):
 b=subprocess.check_output(['git','-C',str(R/'work'/repo),'show',ref+':'+path]);pins.append(dict(repository=repo,commit=ref,path=path,sha256=sha(b)));return b

def add(q,field,text,ref):
 if q not in ids or field not in ['title','objective','description'] or not isinstance(text,str) or not text.strip():return
 h=sha(text.encode());entry=index[q,field].setdefault(h,dict(text=text,english_sha256=h,references=[]));entry['references'].append(ref)

def macro_roles(text):return [x for x in re.findall(r'\$(?:\d+[A-Za-z]+|[A-Za-z])',text) if x.lower()!='$b']
def diagnostic(text,fold='lower'):
 text=re.sub(r'\$[Bb]','\n',text)
 text=re.sub(r'\$[NnCcRr]',lambda x:getattr(x[0],fold)(),text)
 return ' '.join(text.split())
for build in ['70888','70938']:
 path=f'data/wowf/1.60.1.{build}/quests.enUS.json';d=json.loads(git('eg',E,path))['quests']
 for q in ids:
  v=d.get(str(q),{})
  if v.get('level') is not None:levels[q]=v['level']
  if v.get('zoneAreaId') is not None:zones[q]=v['zoneAreaId']
  if v.get('classMask') is not None:classes[q]=v['classMask']
  for key,f in [('title','title'),('objectivesText','objective'),('description','description')]:add(q,f,v.get(key),dict(repository='JIVESCORP/eg-link-output-wowf',commit=E,path=path,pointer=f'/quests/{q}/{key}',phase=f,kind='ownID_query'))
paths=subprocess.check_output(['git','-C',str(R/'work/eg'),'ls-tree','-r','--name-only',E],text=True).splitlines()
for path in paths:
 if not re.fullmatch(r'data/wowf/[^/]+/texts.enUS.json',path):continue
 d=json.loads(git('eg',E,path)).get('quests',{})
 for q in ids:
  for phase,entries in d.get(str(q),{}).items():
   f={'accept':'description','objectives':'objective','title':'title'}.get(phase)
   if not f:continue
   for i,v in enumerate(entries):add(q,f,v.get('text'),dict(repository='JIVESCORP/eg-link-output-wowf',commit=E,path=path,pointer=f'/quests/{q}/{phase}/{i}/text',phase=phase,kind='ownID_captured_phase'))
# Existing VO corpus: only selected own-ID accept fields; no gossip/books/raw reader context copied.
path='tools/data/capture.json';d=json.loads(git('forever-vo',V,path))['quests']
for key,v in d.items():
 q=v.get('questID');phase=v.get('event')
 if q in ids and phase=='accept':add(q,'description',v.get('text'),dict(repository='quinn-dougherty/forever-vo',commit=V,path=path,pointer='/quests/'+key+'/text',phase=phase,kind='normalized_capture_reference_not_roleproof'))
# Questie literal data: evaluate only validated selected row/table literals, never upstream scripts.
path='data/Forever/foreverQuestDB.lua';text=git('questiedb',Q,path).decode()
for row in re.finditer(r'^\s*\[(\d+)\] = (\{.*\}),?$',text,re.M):
 q=int(row[1])
 if q not in ids:continue
 # Restricted selected-row literal whitelist (tables/numeric/bool/nil/quoted strings only).
 stripped=re.sub(r'"(?:[^"\\]|\\.)*"','""',row[2]);assert not re.search(r'[^0-9\s{},.=\-\[\]"A-Za-z]',stripped);words=re.findall(r'[A-Za-z_]+',stripped);assert all(w in ['nil','true','false'] for w in words)
 v=l.eval(row[2]);add(q,'title',v[1],dict(repository='Questie/QuestieDB',commit=Q,path=path,pointer=f'/{q}/1',phase='title',kind='ownID_metadata_literal'))
 if v[8]:add(q,'objective','\n'.join(x for _,x in sorted(v[8].items())),dict(repository='Questie/QuestieDB',commit=Q,path=path,pointer=f'/{q}/8',phase='objectivesText',kind='ownID_metadata_literal'))
 if q not in levels and v[5] is not None:levels[q]=v[5]
 if q not in classes and v[7] is not None:classes[q]=v[7]
quoted=r'"(?:[^"\\]|\\.)*"'
for path in ['src/corrections/Forever/foreverQuestFixes.lua','src/corrections/Forever/traces/foreverQuestTraces.lua']:
 text=git('questiedb',Q,path).decode()
 for row in re.finditer(r'^        \[(\d+)\] = \{(.*?)(?=^        \[|^    \})',text,re.M|re.S):
  q=int(row[1])
  if q not in ids:continue
  for key,f in [('name','title'),('objectivesText','objective')]:
   v=re.search(r'\[questKeys\.'+key+r'\] = (.*?)(?=\n\s*\[questKeys\.|\n        \},|$)',row[2],re.S)
   if not v:continue
   strings=re.findall(quoted,v[1]);lines=[l.eval(x) for x in strings]
   if lines:add(q,f,'\n'.join(lines),dict(repository='Questie/QuestieDB',commit=Q,path=path,pointer=f'/{q}/questKeys.{key}',phase=key,kind='ownID_questlog_trace' if '/traces/' in path else 'ownID_authored_metadata'))
# Reuse existing pinned source corpus only at selected IDs/3fields; no old365/592 matching pass.
oldpins=json.loads((R/'evidence/main-new-source-discovery13.json').read_text())['sources']
for local,path in [('stein-cache-enUS.json','etl/corrections/questcache/forever/enUS.json'),('stein-wowhead-enUS.json','etl/corrections/wowhead/forever/enUS.json')]:
 pin=next(x for x in oldpins if x['repository']=='Stein-N/WoW-Quest-Database');filepin=next(x for x in pin['files'] if x['path']==path);raw=(R/'work/new-main-sources'/local).read_bytes();assert sha(raw)==filepin['sha256'];pins.append(dict(repository=pin['repository'],commit=pin['commit'],**filepin));data=json.loads(raw)['quests']
 for q in ids:
  v=data.get(str(q),{})
  for key,f in [('name','title'),('objectivesText','objective'),('details','description')]:
   s=v.get(key)
   if isinstance(s,list):s='\n'.join(s)
   add(q,f,s,dict(repository=pin['repository'],commit=pin['commit'],path=path,pointer=f'/quests/{q}/{key}',phase=f,kind='historical_or_normalized_reference_not_roleproof',record_build=v.get('build'),record_fetched=v.get('fetched')))
pin=next(x for x in oldpins if x['repository']=='rusty-key/spoken-wow');filepin=next(x for x in pin['files'] if x['path']=='pipelines/quests/corpus/corpus.json.gz');raw=(R/'work/new-main-sources/spoken-corpus.json.gz').read_bytes();assert sha(raw)==filepin['sha256'];pins.append(dict(repository=pin['repository'],commit=pin['commit'],**filepin))
for i,v in enumerate(json.loads(gzip.decompress(raw))['lines']):
 if v.get('questId') not in ids or v.get('source')!='accept':continue
 add(v['questId'],'description',v.get('originalText'),dict(repository=pin['repository'],commit=pin['commit'],path=filepin['path'],pointer=f'/lines/{i}/originalText',line_id=v.get('lineId'),contribution_id=v.get('contributionId'),phase='accept',kind='mixed_corpus_reference_not_current_or_roleproof'))
# Exactly483 own-ID/phase comparisons. No expansion/substitution of ANY role/counter marker.
rows=[];counts=collections.Counter();pending=[]
for record in qualified:
 q=record['qid']
 for field in record['fields']:
  rawfield=field['field'];f={'title':'title','logDescription':'objective','questDescription':'description'}[rawfield];candidates=list(index[q,f].values());exact=[v for v in candidates if v['english_sha256']==field['sha256']];dh=field.get('diagnostic_sha256',field['sha256']);matches=exact or [v for v in candidates if any(sha(diagnostic(v['text'],fold).encode())==dh for fold in ['lower','upper'])];kind='exact_raw_SHA' if exact else 'diagnostic_ONLY_not_binding_approval' if matches else 'none';rolemarkers=[v for _,v in field.get('raw_macro_positions',[]) if v.lower()!='$b'];entry=a.quests[q][f] if a.quests[q] else None
  refs=[];supported=[]
  for v in matches:
   refs.append(dict(english_sha256=v['english_sha256'],raw_or_diagnostic_match=kind,references=v['references']))
   if not rolemarkers and not macro_roles(v['text']):
    ui=re.sub(r'\$[Bb]','\n',v['text']);supported.append(a.Translate(entry,ui) is not None)
  if rolemarkers:status='role_hold_known_english' if matches else 'role_hold_unknown_english'
  elif matches and any(supported):status='supported_independent_English_exact_raw' if exact else 'supported_independent_English_diagnostic_cache_binding_only'
  elif exact:status='known_English_new_literal_variant_exact_raw'
  elif matches:status='known_English_unmatched_diagnostic_only'
  else:status='unknown_English'
  counts[status]+=1;r=dict(qid=q,raw_field=rawfield,field=f,raw_sha256=field['sha256'],raw_bytes=field['bytes'],diagnostic_sha256=field.get('diagnostic_sha256'),raw_macro_positions=field.get('raw_macro_positions',[]),status=status,match_kind=kind,existing_English_references=refs,canonical_present=entry is not None,level=levels.get(q),zone_area_id=zones.get(q),required_class_mask=classes.get(q),current_enabled_usage='unproven',phase_qualification='Raw protocol field joins ONLY independent same-ownID title/objective/description reference; diagnostic join alone is not phase/role approval.')
  rows.append(r)
  if status.startswith('known_English_new'):pending.append(dict(qid=q,field=f,english=exact[0]['text'],refs=refs))
assert len(rows)==483
rows.sort(key=lambda r:(r['level'] if r['level'] is not None and r['level']>=0 else 999,r['zone_area_id'] if r['zone_area_id'] is not None else 999999,0 if r['required_class_mask'] in [4,1024] else 1,r['qid'],r['field']))
unresolved=[r for r in rows if not r['status'].startswith('supported_')];request=[r for r in rows if r['status'] in ['unknown_English','role_hold_unknown_english','known_English_unmatched_diagnostic_only']];literal=[r for r in request if not [v for _,v in r['raw_macro_positions'] if v.lower()!='$b']];selected=literal[:24] if literal else request[:24]
report=dict(scope='ONE targeted join161structurallyqualified records/483title-objective-description candidates ONLY; no rawWDB onCloud, no decoder/public11/old6150/686/party/source20/22held rerun.',metadata_source_commit='384a8aba5f098eab4b744ecc6651620b336b323c',metadata_bytes=META.stat().st_size,metadata_sha256=sha(META.read_bytes()),actual_extraction_invocations=m['actual_invocations'],actual_input_sha256=m['input_sha256'],qualified_records=161,fields=483,original217_record_statuses=m['counts'],catalog_sha256=CAT,counts=dict(counts),ready_exact_literal_candidates=len(pending),new_thai_fields=0,source_pins=pins,diagnostic_scope='Only $B/$b newline, macroN/C/Rcasefold and whitespace. Both casefold directions indexed for metadata compatibility; neither infers roles or proves phase. No token/body/checklist/quantity stripping.',rows=rows)
(R/'evidence/source23-v2-field-join.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(R/'evidence/source23-v2-unresolved-fields.json').write_text(json.dumps(dict(counts=dict(collections.Counter(r['status'] for r in unresolved)),fields=unresolved),ensure_ascii=False,separators=(',',':'))+'\n');(R/'evidence/source23-v2-next-text-request.json').write_text(json.dumps(dict(status='NO_UNKNOWN_ENGLISH_TEXT_TRANSFER_NEEDED' if not request else 'SELECTED_FIELDS_ONLY_PRIVACY_SCREEN_BEFORE_TRANSFER',selected_fields=len(selected),remaining_unresolved_after_selected=len(request)-len(selected),selection='Lowest knownlevel/zone with literal-only fields first; class metadata breaks ties, unknownlevel retained unknown. No guessed story associations.',fields=[dict(qid=r['qid'],field=r['field'],raw_field=r['raw_field'],raw_sha256=r['raw_sha256'],raw_bytes=r['raw_bytes'],level=r['level'],zone_area_id=r['zone_area_id'],required_class_mask=r['required_class_mask'],status=r['status'],existing_English_references=r['existing_English_references'],needed='Only this exact private raw fullfield, verify rawSHA and screen names/privacy before transfer; do not substitute counters/roles or send entire161records.') for r in selected]),indent=2)+'\n');(R/'work/source23/ready-exact-literal-private.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['rows','source_pins']},indent=2));print('SELECTED',json.dumps([(r['qid'],r['field'],r['level']) for r in selected]));print('READY',json.dumps([(r['qid'],r['field']) for r in pending]))

# Final compact roleproof-only queue and checkpoint; no extra source comparisons.
p=R/'evidence/source23-v2-field-join.json';d=json.loads(p.read_text());rows=d['rows'];unresolved=[r for r in rows if not r['status'].startswith('supported_')];assert len(unresolved)==50 and all(r['status']=='role_hold_known_english' for r in unresolved)
def primary(r):
 refs=[]
 for v in r['existing_English_references']:
  assert v['english_sha256']==r['raw_sha256'] and v['raw_or_diagnostic_match']=='exact_raw_SHA'
  refs.extend(v['references'])
 return sorted(refs,key=lambda ref:(ref['kind']!='ownID_query','70938' not in ref['path'],'70888' not in ref['path'],ref['repository'],ref['path']))[0]
compact=[]
for r in unresolved:
 compact.append(dict(qid=r['qid'],field=r['field'],raw_field=r['raw_field'],raw_sha256=r['raw_sha256'],raw_bytes=r['raw_bytes'],canonical_present=True,status=r['status'],level=r['level'],zone_area_id=r['zone_area_id'],required_class_mask=r['required_class_mask'],raw_non_linebreak_markers=sorted({v for _,v in r['raw_macro_positions'] if v.lower()!='$b'}),exact_matching_existing_English_reference=primary(r),needed_proof='Independent own-ID UI/caller/protocol binding for raw marker semantics/positions. English already known by exact rawSHA; no raw-text reread or role/counter/gender substitution requested. Existing canonical remains.'))
(R/'evidence/source23-v2-unresolved-fields.json').write_text(json.dumps(dict(scope='All50 role holds,40description+10objective; all have existing own-ID canonical. Not50untranslated fields/quests.',counts=dict(collections.Counter(r['status'] for r in unresolved)),fields=compact),ensure_ascii=False,separators=(',',':'))+'\n')
(R/'evidence/source23-v2-next-text-request.json').write_text(json.dumps(dict(status='NO_UNKNOWN_ENGLISH_TEXT_TRANSFER_NEEDED',unknown_English_fields=0,selected_private_raw_fields=[],ready_new_literal_variants=0,reason='All483raw hashes exactly match existing independent own-ID English/phase references.433literal existingEnglish supported;50raw-marker fields remain roleproof-only holds, allcanonicalpresent.',typed_role_proof_queue='evidence/source23-v2-unresolved-fields.json',first_lowlevel_proof_targets=[{k:r[k] for k in ['qid','field','raw_field','raw_sha256','level','zone_area_id','required_class_mask','raw_non_linebreak_markers','exact_matching_existing_English_reference']} for r in compact[:12]],needed='Only independent typed UI/caller/protocol proof if resolving these marker holds; do not send entire161records, repeat decoder, or infer roles from a hash/matcher/canonical.',phase_limits='Only title/logDescription/objective and questDescription/description were joined. No completionLog/endText/area/portrait/progress/reward binding.',new_translation_or_current_inventory_claim=False),indent=2)+'\n')
d.update(exact_raw_English_matches=483,diagnostic_only_matches=0,unknown_English_fields=0,known_English_new_literal_variants=0,role_hold_fields_with_existing_canonical=50,private_raw_text_fields_requested=0,unresolved_compact_reference='evidence/source23-v2-unresolved-fields.json',next_input_request='evidence/source23-v2-next-text-request.json',interpretation='433existing literal Englishs supported, not433newtranslations.50raw marker fields retain existingcanonicals; English is known by exactSHA but raw slot semantics not newly approved.161/483notnewcoverage/currentinventory.')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
checkpoint=dict(status='ACTUAL_SOURCE23_TARGETED483FIELD_COMPARISON_FINISHED',safe_input_commit='384a8aba5f098eab4b744ecc6651620b336b323c',safe_input_sha256=d['metadata_sha256'],Root_actual_decoder_invocations=1,Cloud_decoder_invocations=0,structurally_qualified_records=161,fields_compared_once=483,rawSHA_ownID_English_phase_matches=483,supported_literal_fields=433,role_hold_knownEnglish_fields=50,role_hold_phase_counts=dict(collections.Counter(r['field'] for r in unresolved)),all_role_hold_fields_have_existing_canonical=True,unknown_English_fields=0,knownEnglish_new_literal_variants=0,new_Thai_fields=0,private_raw_text_fields_requested=0,next_precise_input='Independent own-ID typed UI/caller/protocol roleproof for50indexed raw-marker fields if resolving those holds; exactEnglish references supplied, so no English reread/transfer required.',compact_hold_queue='evidence/source23-v2-unresolved-fields.json',next_request='evidence/source23-v2-next-text-request.json',original56_other_structural_holds_not_retried=True,Catalog_sha256=d['catalog_sha256'],runtime_unchanged_vs_delivered=not bool(subprocess.check_output(['git','diff','383cb00416b0b1069e3801c5532cadc685f3dd84','--','src/ForeverThai'])),books22_still_held=True,public11_decoder_oldcorpus_tests_fonts_version_ZIP_feed_rerun_or_changed=False,full_GOAL_complete=False,current_enabled_inventory_proven=False,actual_Windows_MacM2_game_acceptance=False)
(R/'evidence/source23-v2-comparison-checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')

