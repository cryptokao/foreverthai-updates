"""Inspect43 source SQL texts as literal data;never execute SQL or source code."""
import pathlib,json,re,hashlib,time,zipfile,collections
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;t=time.perf_counter();cpu=time.process_time()
raw=(R/'main34-live-quest-texts.sql').read_bytes()
assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='74909b267c259dd38931f9aef2cc2fae9e3a0abd'
rows=[]
pat=re.compile(r"^INSERT INTO \x60(?P<table>quest_offer_reward|quest_request_items)\x60 \(\x60ID\x60, \x60(?:RewardText|CompletionText)\x60, \x60VerifiedBuild\x60\) VALUES \((?P<id>\d+), '(?P<text>(?:[^']|'')*)', (?P<build>\d+)\) .*?; -- (?P<title>.*)$")
for ix,line in enumerate(raw.decode().splitlines(),1):
 if not line.startswith('INSERT INTO '):continue
 m=pat.fullmatch(line);assert m,ix
 rows.append(dict(quest_id=int(m['id']),field='completion' if m['table']=='quest_offer_reward' else 'progress',english=m['text'].replace("''","'"),title=m['title'],source_line=ix,source_VerifiedBuild=int(m['build'])))
assert len(rows)==43 and collections.Counter(v['field'] for v in rows)=={'completion':24,'progress':19}
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil')
a=l.table()
base=R/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='54eef1b1fb33379332d8bfe5621d166e9bc77f9fe5931cdf510efbfd782b5077'
with zipfile.ZipFile(base) as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
prior={}
for f in ['main25-source-audit.json','main26-source-audit.json','main29-fvo-source-audit.json','main33-fvo-source-audit.json']:
 d=json.loads((R/f).read_text(encoding='utf8'))
 for v in d.get('rows',[]):
  if v.get('status') in ['supported_exact','supported_linebreak_markup','diagnostic_identity_substitution_supported_NOT_roleproof']:
   prior[(v.get('quest_id'),v.get('field'),v.get('english_sha256'))]=v
new=[];audit=[];counts=collections.Counter();reused=0
for v in rows:
 en=v['english'];q=v['quest_id'];f=v['field'];enhash=hashlib.sha256(en.encode()).hexdigest();old=prior.get((q,f,enhash))
 quest=a.quests[q];entry=quest[f] if quest is not None else None
 ui=re.sub(r'\$[Bb]','\n',en);tokens=sorted(set(re.findall(r'\$(?:[0-9]+[A-Za-z]+|[A-Za-z])',en))-{'$B','$b'})
 if old:status=old['status'];reused+=1
 elif a.Translate(entry,en) is not None:status='supported_exact'
 elif a.Translate(entry,ui) is not None:status='supported_linebreak_markup'
 elif tokens or '$' in ui:
  rendered=re.sub(r'\$[NnCcRr](?![A-Za-z0-9_])',lambda m:{'n':'CloudTester','c':'Druid','r':'Night Elf'}[m[0][1].lower()],ui)
  status='diagnostic_identity_substitution_supported_NOT_roleproof' if a.Translate(entry,rendered) is not None else 'held_unproven_roles_or_tokens'
 else:status='literal_unmatched_needs_source_review'
 counts[status]+=1
 r={k:v[k] for k in v if k!='english'};r.update(english_sha256=enhash,english_bytes=len(en.encode()),status=status,raw_tokens=tokens,prior_identical_source_proof_reused=bool(old),runtime_quest_present=quest is not None,runtime_field_present=entry is not None)
 audit.append(r)
 if status in ['literal_unmatched_needs_source_review','held_unproven_roles_or_tokens']:new.append(dict(r,english=en))
doc=dict(batch='MAIN34',source_repo='Karrz1/TrinityCore',pin='e6399e4fcbf774f7a8eabf0148058b70f49487af',path='sql/custom/world/2026_11_13_54_world_forever_live_quest_texts_1113.sql',git_blob='74909b267c259dd38931f9aef2cc2fae9e3a0abd',source_change_commit='4316370b600ae49fffc9286fda4b57ac6e26da31',source_provenance='Publisher states English live captures11-11/11-12,build70888;not current70938 enabled inventory or independent proof of macro role',baseline='Actual immutable0.471combined all additive quest modules',counts=dict(counts),forms=len(rows),prior_identical_forms_not_rerun=reused,rows=audit,new_Thai_fields=0,runtime_changed=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu)
for f,d in [('main34-live-sql-audit.json',doc),('main34-live-sql-unmatched-private.json',new)]: (R/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in doc.items() if k!='rows'},ensure_ascii=False))
print(json.dumps(new,ensure_ascii=False))
