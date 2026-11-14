"""One new issue3481 payload audit only; raw exports stay ignored/private under work."""
import pathlib,json,re,zlib,base64,hashlib,collections,subprocess
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];BASE='7f082e6a57fe72305bd4366c1588c04d5bc1ad95';sha=lambda b:hashlib.sha256(b).hexdigest();p=R/'work/issue-3481.json';raw=p.read_bytes();issue=json.loads(raw);assert issue['number']==3481 and issue['comments']==0;m=re.search(r'FVO1:([A-Za-z0-9+/=]+)',issue['body']);assert m;compressed=base64.b64decode(m[1],validate=True);decoded=zlib.decompress(compressed);doc=json.loads(decoded);(R/'work/issue-3481-decoded.json').write_bytes(decoded);assert len(doc['lines'])==293
l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:
 b=subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']);assert b==(R/'src/ForeverThai'/f'{n}.lua').read_bytes();l.execute(b.decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
phases=collections.Counter();counts=collections.Counter();seen={};rows=[];private=[];kinds=collections.Counter();shapes=collections.Counter()
for i,v in enumerate(doc['lines']):
 kinds[v.get('k','missing')]+=1
 if v.get('k')!='quest':counts['non_main_ignored']+=1;continue
 phases[v.get('e','unknown')]+=1;shapes[','.join(sorted(v))]+=1;q=v.get('q');f={'accept':'description','complete':'completion','progress':'progress','objective':'objective','objectives':'objective','title':'title'}.get(v.get('e'));text=v.get('x');assert isinstance(q,int) and q>0 and isinstance(text,str)
 key=q,f,text
 if key in seen:counts['duplicate_main_occurrences']+=1;seen[key]['source_indices'].append(i);continue
 entry=a.quests[q][f] if a.quests[q] and f else None
 if f is None:status='held_unknown_main_phase'
 elif not text.strip():status='blank_no_prose'
 elif a.Translate(entry,text) is not None:status='already_supported_exact'
 elif '$' in text:
  rendered=text
  for t,s in [('N','CloudTester'),('n','CloudTester'),('C','Druid'),('c','Druid'),('R','Night Elf'),('r','Night Elf')]:rendered=rendered.replace('$'+t,s)
  status='diagnostic_substitution_supported' if a.Translate(entry,rendered) is not None else 'held_unproven_normalized_roles'
 else:status='literal_unmatched_needs_qualification'
 counts[status]+=1;row=dict(quest_id=q,field=f,source_indices=[i],english_sha256=sha(text.encode()),status=status,runtime_quest_present=a.quests[q] is not None,runtime_field_present=entry is not None,normalized_tokens=sorted(set(re.findall(r'\$[NnCcRr]|\$\d+oa',text))))
 if status.startswith('held'):row['required_proof']='Exact own-ID phase full raw typed source/caller proof for each identity occurrence; export normalization and reader metadata are not proof. Keep existing canonical.'
 elif status=='blank_no_prose':row['required_proof']='Actual nonempty own-ID phase body if that phase exists; blank is not translated content.'
 rows.append(row);seen[key]=row
 if status not in ['already_supported_exact','diagnostic_substitution_supported']:private.append(dict(row,english=text,source_record=v))
(R/'work/main21-unmatched-private.json').write_text(json.dumps(private,ensure_ascii=False,indent=2))
report=dict(snapshot='MAIN21 only new issue3481',baseline_runtime_source=BASE,baseline_catalog_sha256=sha((R/'src/ForeverThai/Catalog.lua').read_bytes()),provenance=dict(url=issue['html_url'],issue=3481,created_at=issue['created_at'],updated_at=issue['updated_at'],comments=0,body_chars=len(issue['body']),body_sha256=sha(issue['body'].encode()),saved_issue_json_sha256=sha(raw),fvo1_base64_sha256=sha(m[1].encode()),compressed_payload_sha256=sha(compressed),decoded_json_sha256=sha(decoded),decoded_json_bytes=len(decoded)),schema=dict(document_keys=sorted(doc),export_header_build=doc.get('build'),export_header_locale=doc.get('locale'),total_records=293,record_kinds=dict(kinds),main_record_key_shapes=dict(shapes),row_build_proven=False),main_phase_occurrences=dict(phases),counts=dict(counts),unique_main_source_forms=len(rows),unmatched_records=[v for v in rows if v['status'] not in ['already_supported_exact','diagnostic_substitution_supported']],ready_literal_candidates=sum(v['status']=='literal_unmatched_needs_qualification' for v in rows),new_translation_count=0,scope='Only3481; no otherissue/Questie/EGpull or source20/old audit/clientgate/fullsuite/font work. Diagnostic substitutions are not independently typed proof or new coverage. Raw/player-context capture values remain ignored/private.',runtime_changed=False,fonts_version_feed_changed=False)
(R/'evidence/main21-issue3481-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['unmatched_records','provenance']},indent=2));print('UNMATCHED:')
for v in private:print(json.dumps({k:v[k] for k in ['quest_id','field','source_indices','english_sha256','status']},ensure_ascii=False))
