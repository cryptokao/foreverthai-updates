"""Only new3524-3526 quest lines; reuse identical previous positive proofs, raw captures stay private."""
import pathlib,json,re,zipfile,hashlib,sys,time,collections
from lupa.lua51 import LuaRuntime
sys.stdout.reconfigure(encoding='utf8');R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time();sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main38/build-0.474.0/ForeverThai-0.474.0-main38-PRIVATE-TEST.zip') as z:
 for n in [s for s in z.read('ForeverThai/ForeverThai.toc').decode().splitlines() if s=='Catalog.lua' or s.startswith('MainQuest')]+['Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return testRace end');g=l.globals()
valid=['supported_exact','supported_linebreak_markup','diagnostic_identity_substitution_supported_NOT_roleproof','blank_no_prose'];prior={}
for file in ['main29-fvo-source-audit.json','main33-fvo-source-audit.json']:
 for row in json.loads((R/file).read_text(encoding='utf8'))['rows']:
  if row['status'] in valid:prior[row['quest_id'],row['field'],row['english_sha256']]=row
out=[];pending=[];reused=0;calls=0;gender=re.compile(r'\$[Gg]\s*([^:;$]+?)\s*:\s*([^;$]+?)\s*;')
for item in json.loads((R/'main39-fvo-main-selected-private.json').read_text(encoding='utf8')):
 v=item['row'];q=v['q'];f={'accept':'description','progress':'progress','complete':'completion'}.get(v['e']);en=v['x'];assert item['build']=='70938' and isinstance(en,str)
 old=prior.get((q,f,sha(en)));quest=a.quests[q];entry=quest[f] if quest is not None and f else None;fixture=None
 g.testClass=v.get('c') or 'Druid';g.testClassID=g.testClass.upper();g.testRace=v.get('r') or 'Night Elf'
 if old:status=old['status'];reused+=1
 elif f is None:status='held_unknown_phase'
 elif not en.strip():status='blank_no_prose'
 else:
  th=a.Translate(entry,en);calls+=1
  if th is not None:status='supported_exact'
  else:
   ui=re.sub(r'\$[Bb]','\n',en);th=a.Translate(entry,ui);calls+=1
   if th is not None:status='supported_linebreak_markup'
   elif re.search(r'\$[nNcCrR]|\$[Gg]|<(?i:name|player|race|class|unknown)[^>]*>|\{[^}]*\}',ui):
    candidates=[(1,gender.sub(lambda m:m[1],ui)),(2,gender.sub(lambda m:m[2],ui))] if gender.search(ui) else [(None,ui)]
    status='held_unproven_roles_or_tokens'
    for branch,text in candidates:
     rendered=re.sub(r'\$[NnCcRr](?![A-Za-z0-9_])',lambda m:{'n':'CloudTester','c':g.testClass,'r':g.testRace}[m[0][1].lower()],text)
     th=a.Translate(entry,rendered);calls+=1
     if th is not None:status='diagnostic_identity_substitution_supported_NOT_roleproof';fixture=dict(class_fixture=g.testClass,race_fixture=g.testRace,gender_branch_diagnostic_only=branch);break
   elif '$' in ui or '|' in ui:status='held_unproven_macro_or_markup'
   else:status='literal_unmatched_needs_full_source_privacy_review'
 meta=dict(quest_id=q,field=f,source_issue=item['issue'],source_line_index=item['index'],english_sha256=sha(en),english_bytes=len(en.encode()),status=status,prior_identical_proof_reused=old is not None,fixture=fixture,headerbuild='70938',individual_row_build_or_current_enabled_proven=False)
 out.append(meta)
 if status.startswith('literal_unmatched') or status.startswith('held_'):pending.append(dict(meta,english=en,source_record=v))
report=dict(batch='MAIN39',scope='Only new3524-3526 exports;no oldissue reparse/matcher rerun',source_counts=dict(exports=3,rawrecords=392,quest_records=56,gossip_records=294,book_records=42),unique_main_forms=len(out),counts=dict(collections.Counter(x['status'] for x in out)),prior_identical_positive_forms_not_rerun=reused,actual_matcher_calls=calls,rows=out,newThai=0,newaliases=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu,limits=['Headerbuild not per-rowbuild or enabledinventory','Diagnostic identity/Gg is not new role or sex-condition proof','Gossip/books secondary not fulltext translated','Raw player contexts/private captures not published','Sample has actualCRLF,no literalbackslashlinebreaks;no parser/runtime fix needed'])
(R/'main39-new-fvo-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(R/'main39-new-fvo-pending-private.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False));print(json.dumps([dict(q=x['quest_id'],field=x['field'],status=x['status'],bytes=x['english_bytes'],english=x['english'] if x['status'].startswith('literal_') else None) for x in pending],ensure_ascii=False))
