"""MAIN24: only added/changed text values in4 EG quest datasets; no unchanged corpus audit."""
import pathlib,json,subprocess,hashlib,re,collections
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
R=pathlib.Path(__file__).resolve().parents[1];OLD='e0f8585914c134d9cb5d76756bd065b1e3e92ece';NEW='ea970da071079b32e56f349e09648ff0e314b351';BASE='d7f69916c7a5ebba38b7aeed3326f9caed2a169d';sha=lambda b:hashlib.sha256(b).hexdigest();pins=[];index={};counts=collections.Counter();ignored_metadata_rows=0;removed=[];queries={}
l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:l.execute((R/f'src/ForeverThai/{n}.lua').read_text(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end');CAT=sha((R/'src/ForeverThai/Catalog.lua').read_bytes());assert CAT=='43ec92f88113114aef4918dcbe10c0bb89b7f222d6658dc5183c08c706f94f50'
def read(ref,p):return subprocess.check_output(['git','-C',str(R/'work/eg'),'show',ref+':'+p])
def add(q,f,text,ref,kind):
 if not isinstance(text,str):return
 key=q,f,text
 if key not in index:index[key]=dict(quest_id=q,field=f,english=text,english_sha256=sha(text.encode()),source_kind=kind,source_refs=[])
 index[key]['source_refs'].append(ref)
for build in ['70888','70938']:
 for name in ['quests.enUS.json','texts.enUS.json']:
  path=f'data/wowf/1.60.1.{build}/{name}';ob=read(OLD,path);nb=read(NEW,path);before=json.loads(ob);after=json.loads(nb);pins.append(dict(path=path,old_sha256=sha(ob),new_sha256=sha(nb),old_bytes=len(ob),new_bytes=len(nb),meta=after.get('meta')))
  if name.startswith('quests'):
   for qstr,v in after['quests'].items():
    q=int(qstr);queries[q]=v;b=before['quests'].get(qstr,{});changed=False
    for k,f in [('title','title'),('objectivesText','objective'),('description','description'),('progress','progress'),('completion','completion')]:
     if k in v and v[k]!=b.get(k):
      counts[f'query{build}_changed_field_values']+=1;changed=True;add(q,f,v[k],dict(path=path,pointer=f'/quests/{q}/{k}',build=build,phase=k,source_old_value_sha256=sha(b[k].encode()) if isinstance(b.get(k),str) else None),'query')
     elif k in b and k not in v:removed.append(dict(quest_id=q,field=f,path=path,old_sha256=sha(b[k].encode()) if isinstance(b[k],str) else None))
    if not changed and v!=b:ignored_metadata_rows+=1
  else:
   for qstr,phases in after.get('quests',{}).items():
    q=int(qstr)
    for phase,entries in phases.items():
     f={'title':'title','objectives':'objective','accept':'description','progress':'progress','complete':'completion'}.get(phase)
     if f is None:continue
     oldtexts={v['text'] for v in before.get('quests',{}).get(qstr,{}).get(phase,[])}
     for i,v in enumerate(entries):
      if v.get('text') not in oldtexts:counts[f'texts{build}_new_field_forms']+=1;add(q,f,v.get('text'),dict(path=path,pointer=f'/quests/{q}/{phase}/{i}/text',build=build,phase=phase),'captured_phase')
rows=[];ready=[];statuses=collections.Counter()
for r in index.values():
 q,f,text=r['quest_id'],r['field'],r['english'];v=queries.get(q,{});entry=a.quests[q][f] if a.quests[q] else None;tokens=sorted(set(re.findall(r'\$(?:\d+[A-Za-z]+|[A-Za-z])|<(?:name|player|race|class|unknown)[^>]*>|\{[^}]*\}',text,re.I)));nonbreak=[t for t in tokens if t.lower()!='$b'];ui=re.sub(r'\$[Bb]','\n',text)
 if not text.strip():status='blank'
 elif classify_title(v.get('title',''),q) or classify_title(text,q):status='held_developer_disabled'
 elif text.strip().lower() in ['description','log','placeholder','nyi','not yet implemented']:status='held_placeholder'
 elif a.Translate(entry,text) is not None:status='already_supported_exact'
 elif nonbreak or '$' in re.sub(r'\$[Bb]','',text):status='held_raw_tokens_no_role_substitution'
 elif a.Translate(entry,ui) is not None:status='already_supported_linebreak_markup'
 else:status='ready_literal'
 r.update(status=status,canonical_present=entry is not None,level=v.get('level'),zone_area_id=v.get('zoneAreaId'),required_class_mask=v.get('classMask'),race_mask=v.get('raceMask'),query_title_sha256=sha(v['title'].encode()) if v.get('title') else None,raw_tokens=tokens,current_enabled_usage='unproven; query/capture presence not enabledinventory')
 statuses[status]+=1;rows.append(r)
 if status=='ready_literal':ready.append(r)
order=lambda r:(r['level'] if isinstance(r['level'],(int,float)) and r['level']>=0 else 999, r['zone_area_id'] if r['zone_area_id'] is not None else 999999,0 if r['required_class_mask'] in [4,1024] else 1,r['quest_id'],r['field'])
rows.sort(key=order);ready.sort(key=order)
# New schema inspection is metadata-only. Scan query IDs/test records do not establish enabled inventory.
scan=json.loads(read(NEW,'data/wowf/1.60.1.70938/quest_scan.json'));prereq=json.loads(read(NEW,'data/wowf/1.60.1.70938/quest_prerequisites.json'))
probe=dict(quest_scan_sections={k:len(v) for k,v in scan.items() if k!='meta'},quest_scan_described_includes_known_test1='1' in scan.get('described',{}),prerequisite_records=len(prereq.get('quests',{})),prerequisite_field_names=sorted({k for v in prereq.get('quests',{}).values() for k in v}),privacy='characters/member values not copied',enabled_denominator=False,limitation='Queried/described/noData/prerequisite observations are partial source evidence, not enabled/playable inventory.')
# Privacy: prose stays private until manual selected-pair review; public audit carries IDs/hashes/refs only.
safe=[{k:v for k,v in r.items() if k!='english'} for r in rows];report=dict(scope='Only4datasets added/changed ownID main text values, not all3902records or otherdatasets.',old_pin=OLD,new_pin=NEW,baseline_source=BASE,catalog_sha256=CAT,dataset_pins=pins,changed_occurrences=dict(counts),ignored_metadata_only_query_rows=ignored_metadata_rows,unique_changed_source_forms=len(rows),statuses=dict(statuses),removed_source_fields_retained_in_runtime=removed,scan_prerequisite_schema=probe,ready_literal_forms=len(ready),ready_literal_unique_quest_ids=len({r['quest_id'] for r in ready}),raw_roles='No synthetic name/class/race/counter/gender substitution or slot inference; raw markers held unless already exactliteral supported. Query vs normalized capture provenance preserved per source ref.',rows=safe)
(R/'work/main24-ready-private.json').write_text(json.dumps(ready,ensure_ascii=False,indent=2)+'\n');(R/'work/main24-all-private.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(R/'evidence/main24-eg-delta.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['rows','dataset_pins','removed_source_fields_retained_in_runtime']},indent=2));print('Ready prose stays private pending manual privacy/meaning review.')

# Final source qualification and ordered proposal queue. Only preliminary unmatched literals.
explicit_developer_titles={8230:"Collin's Test Quest",7681:'Hunter test quest',7682:'Hunter test quest2'}
no_data=set(scan['noData'])
for r in rows:
    if r['status']!='ready_literal':continue
    qid=r['quest_id'];title=queries.get(qid,{}).get('title','')
    if qid==2752 and r['field']=='progress':r['status']='held_resolved_or_unproven_identity_context'
    elif qid in explicit_developer_titles and title==explicit_developer_titles[qid]:r['status']='held_explicit_developer_test_title'
    elif title.startswith('zzOLD '):r['status']='held_explicit_old_title'
    elif qid==95056:r['status']='held_placeholder_objective' if r['field']=='objective' else 'held_usage_incomplete_NAME_objective_record'
    elif qid in no_data and str(qid) not in scan['described'] and all(x['phase'] in ['title','objectivesText','description'] for x in r['source_refs']):r['status']='held_query_vs_scan_noData_uncertainty'
    else:r['status']='ready_literal_qualified_source'
    r['scan_observation']='described' if str(qid) in scan['described'] else 'noData' if qid in no_data else 'not_in_this_scan'
    r['ownID_prerequisite_observation']=str(qid) in prereq['quests']
ready=[r for r in rows if r['status']=='ready_literal_qualified_source']
report['initial_statuses']=report.pop('statuses');report['statuses']=dict(collections.Counter(r['status'] for r in rows));report['ready_literal_forms']=len(ready);report['ready_literal_unique_quest_ids']=len({r['quest_id'] for r in ready});report['selected_proposal_fields']=38;report['remaining_ready_after_proposal']=len(ready)-38
report['qualification']='Current own-ID query/captured phase literal body with exactsignature-only translation; no enabledinventory claim. Explicit test/zzOLD/incompleteNAME, noData query-only discrepancy and2752resolved/unproven identity context held. No expansion/role inferred from story.'
report['scan_prerequisite_schema']['dataset_document_sha256']=sha(read(NEW,'DATASETS.md'));report['rows']=[{k:v for k,v in r.items() if k!='english'} for r in rows]
(R/'evidence/main24-eg-delta.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(R/'work/main24-finalqueue-private.json').write_text(json.dumps(ready,ensure_ascii=False,indent=2)+'\n')
(R/'evidence/main24-remaining-ready.json').write_text(json.dumps(dict(source_pin=NEW,ready_before_proposal=len(ready),selected_proposal_fields=38,remaining_ready_forms=len(ready)-38,records=[{k:v for k,v in r.items() if k!='english'} for r in ready[38:]]),ensure_ascii=False,indent=2)+'\n')
print('Final qualified readyforms',len(ready),'remaining_after_proposal',len(ready)-38)
