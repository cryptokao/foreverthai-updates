"""One new151-record six-part export audit against current approved MAIN21 source; raw stays private."""
import pathlib,json,hashlib,re,zlib,base64,collections,subprocess
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];BASE='f2a469dbff82a2b68d569bbb2b16ad2041a74ba4';sha=lambda b:hashlib.sha256(b).hexdigest();l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:
 b=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']);assert b==(R/'src/ForeverThai'/f'{n}.lua').read_bytes();l.execute(b.decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
pins=[];header=None;records=[];expected=[23,25,34,20,26,23]
for part,no in enumerate(range(3482,3488),1):
 raw=(R/f'work/issue-{no}.json').read_bytes();issue=json.loads(raw);assert issue['comments']==0;assert re.search(r'part '+str(part)+r' of 6',issue['title']);m=re.search(r'FVO1:([A-Za-z0-9+/=]+)',issue['body']);assert m;compressed=base64.b64decode(m[1],validate=True);decoded=zlib.decompress(compressed);doc=json.loads(decoded);(R/f'work/issue-{no}-decoded.json').write_bytes(decoded);assert len(doc['lines'])==expected[part-1]
 current={k:doc.get(k) for k in ['v','addon','build','locale']}
 if header is None:header=current
 assert current==header
 pins.append(dict(issue=no,part=part,total_parts=6,url=issue['html_url'],created_at=issue['created_at'],updated_at=issue['updated_at'],comments=0,body_sha256=sha(issue['body'].encode()),body_chars=len(issue['body']),compressed_sha256=sha(compressed),decoded_sha256=sha(decoded),decoded_bytes=len(decoded),records=len(doc['lines']),document_keys=sorted(doc),attachment_urls=re.findall(r'https://[^\s)]+',issue['body'])))
 records.extend((no,i,v) for i,v in enumerate(doc['lines']))
assert len(records)==151
kinds=collections.Counter();mainphases=collections.Counter();counts=collections.Counter();main_seen={};non_seen=set();rows=[];private=[];non_counts=collections.defaultdict(collections.Counter)
for no,i,v in records:
 kind=v.get('k','unknown');kinds[kind]+=1;text=v.get('x');assert isinstance(text,str)
 if kind!='quest':
  key=(kind,v.get('n'),v.get('t'),v.get('p'),v.get('e'),text)
  if key in non_seen:non_counts[kind]['duplicate_occurrences']+=1;continue
  non_seen.add(key);non_counts[kind]['unique_records']+=1
  keys_ok=(bool(v.get('n')) and str(v['n']).lstrip('-').isdigit() and int(v['n'])!=0) if kind=='gossip' else bool(v.get('t') and isinstance(v.get('p'),int) and v['p']>0) if kind=='book' else False
  if not text.strip():status='blank'
  elif re.search(r'\$|<(?:name|player|race|class|unknown)[^>]*>|\{[^}]*\}',text,re.I):status='held_role_or_privacy_tokens'
  elif not keys_ok:status='held_missing_source_keys'
  else:status='literal_with_source_keys_unreviewed'
  non_counts[kind][status]+=1;continue
 q=v.get('q');phase=v.get('e');mainphases[phase]+=1;f={'accept':'description','complete':'completion','progress':'progress','objective':'objective','objectives':'objective','title':'title'}.get(phase);assert isinstance(q,int) and q>0;key=q,f,text
 if key in main_seen:counts['duplicate_main_occurrences']+=1;main_seen[key]['source_positions'].append(dict(issue=no,line_index=i));continue
 entry=a.quests[q][f] if a.quests[q] and f else None
 if not f:status='held_unknown_phase'
 elif not text.strip():status='blank_no_prose'
 elif a.Translate(entry,text) is not None:status='supported_exact'
 elif '$' in text:
  rendered=text
  for t,z in [('N','CloudTester'),('n','CloudTester'),('C','Druid'),('c','Druid'),('R','Night Elf'),('r','Night Elf')]:rendered=rendered.replace('$'+t,z)
  status='diagnostic_substitution_supported' if a.Translate(entry,rendered) is not None else 'held_unproven_normalized_roles'
 else:status='literal_unmatched_needs_qualification'
 counts[status]+=1;row=dict(quest_id=q,field=f,status=status,source_positions=[dict(issue=no,line_index=i)],english_sha256=sha(text.encode()),runtime_quest_present=a.quests[q] is not None,runtime_field_present=entry is not None,unproven_tokens=sorted(set(re.findall(r'\$[NnCcRr]|\$\d+oa',text))))
 if status.startswith('held'):row['needed_proof']='Exact own-ID phase full raw typed source; no roles inferred from export substitutions or reader context. Keep existing canonical.'
 rows.append(row);main_seen[key]=row
 if status not in ['supported_exact','diagnostic_substitution_supported']:private.append(dict(row,english=text,source_record=v))
(R/'work/main22-unmatched-private.json').write_text(json.dumps(private,ensure_ascii=False,indent=2))
for k in ['supported_exact','diagnostic_substitution_supported','held_unproven_normalized_roles','blank_no_prose','literal_unmatched_needs_qualification','duplicate_main_occurrences']:counts.setdefault(k,0)
report=dict(snapshot='MAIN22 issues3482–3487 one claimed151-record export',baseline_source=BASE,baseline_catalog_sha256=sha((R/'src/ForeverThai/Catalog.lua').read_bytes()),approved94233_MAIN21_preserved=True,source_parts=pins,split_validation=dict(parts=list(range(1,7)),claimed_total_parts=6,part_sizes=expected,total_records=151,consistent_export_header=True,group_claim='Sixpart titles and Root input identify one export; no independent session identity inferred.'),export_header=header,per_row_addon_client_build='not independently proven by export header',kind_occurrences=dict(kinds),main_phase_occurrences=dict(mainphases),unique_main_forms=len(rows),main_counts=dict(counts),unmatched_main=[v for v in rows if v['status'] not in ['supported_exact','diagnostic_substitution_supported']],non_main_source_readiness_totals={k:dict(v) for k,v in non_counts.items()},non_main_scope='Kind/key/literal-token totals only, not translation-matching or NPC/book source audit. Literal-with-keys does NOT mean new translation or independently reviewed content; Root may decide GOAL7next.',new_thai_fields=0,new_main_prose=0,runtime_changed=False,font_version_package_feed_changed=False,scope='Only six newparts decoded/deduplicated once. No Questie/EGpull/re-audit, oldsource20/oldholds, theme/caller re-audit, auxiliarytests/clientgate/glyph work. Raw/player context ignored/private.')
(R/'evidence/main22-sixpart-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['source_parts','unmatched_main']},indent=2));print('UNMATCHED:')
for v in private:print(json.dumps({k:v[k] for k in ['quest_id','field','status','source_positions','english_sha256']},ensure_ascii=False))
