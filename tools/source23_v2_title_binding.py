"""Bind all217 v2 envelopes and target-only title hashes from existing cached pins.
No public11 intake, runtime lookup, source pull or local/raw cache access.
"""
import pathlib,json,re,hashlib,subprocess,collections
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];Q='4dbb82440a27856f8dccf57094a5d792cdc7cc9b';E='e0f8585914c134d9cb5d76756bd065b1e3e92ece';sha=lambda b:hashlib.sha256(b).hexdigest();l=LuaRuntime(unpack_returned_tuples=True)
meta=json.loads((R/'source_inputs/source23-local-cache-v2-envelope-metadata.json').read_text());ids={v['id'] for v in meta['records']};assert len(ids)==len(meta['records'])==217;assert meta['bytes']==228447 and meta['sha256']=='26612489c7f5015c7958b84703b295760b7096c058a00c3c170ff3ae6a6baf00';assert 24+sum(v['payload_bytes']+8 for v in meta['records'])+8==meta['bytes'];known=collections.defaultdict(list);pins=[]
def readrepo(repo,ref,path):
 b=subprocess.check_output(['git','-C',str(R/'work'/repo),'show',ref+':'+path]);pins.append(dict(repository=repo,commit=ref,path=path,sha256=sha(b)));return b.decode()
def split_top(s):
 out=[];start=0;depth=0;quoted=False;escape=False
 for i,c in enumerate(s):
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='{':depth+=1
  elif c=='}':depth-=1
  elif c==',' and depth==0:out.append(s[start:i]);start=i+1
 out.append(s[start:]);return out
b=readrepo('questiedb',Q,'data/Forever/foreverQuestDB.lua')
for m in re.finditer(r'^\s*\[(\d+)\] = \{(.*)\},?$',b,re.M):
 q=int(m[1])
 if q not in ids:continue
 token=split_top(m[2])[0].strip();assert re.fullmatch(r'"(?:[^"\\]|\\.)*"',token);known[q].append(dict(title=l.eval(token),repository='Questie/QuestieDB',commit=Q,path='data/Forever/foreverQuestDB.lua'))
quoted=r'"(?:[^"\\]|\\.)*"'
for path in ['src/corrections/Forever/foreverQuestFixes.lua','src/corrections/Forever/traces/foreverQuestTraces.lua']:
 b=readrepo('questiedb',Q,path)
 for m in re.finditer(r'^        \[(\d+)\] = \{(.*?)(?=^        \[|^    \})',b,re.M|re.S):
  q=int(m[1])
  if q not in ids:continue
  title=re.search(r'\[questKeys.name\] = ('+quoted+')',m[2])
  if title:known[q].append(dict(title=l.eval(title[1]),repository='Questie/QuestieDB',commit=Q,path=path))
for build in ['70888','70938']:
 path=f'data/wowf/1.60.1.{build}/quests.enUS.json';data=json.loads(readrepo('eg',E,path))['quests']
 for q in ids:
  v=data.get(str(q))
  if v and v.get('title'):known[q].append(dict(title=v['title'],repository='JIVESCORP/eg-link-output-wowf',commit=E,path=path))
expected={}
for q in sorted(ids):
 sources=[dict(title_sha256=sha(v['title'].encode()),repository=v['repository'],commit=v['commit'],path=v['path']) for v in known[q]];hashes=sorted({v['title_sha256'] for v in sources});markers=any(re.search(r'\[(?:DNT|UNUSED|PH|NYI)\]|^TEST QUEST$',v['title'],re.I) for v in known[q]);expected[str(q)]=dict(title_sha256=hashes[0] if len(hashes)==1 and not markers else None,status='confirmed_unique_metadata_title' if len(hashes)==1 and not markers else 'held_conflicting_or_missing_or_developer_title',source_title_hashes=sources)
out=dict(schema=1,snapshot_version=2,status='ACTIVE_FROZEN_V2_PENDING_FIRST_EXTRACTION',source23_file_sha256=meta['sha256'],expected_source_bytes=meta['bytes'],expected_build=70938,expected_magic='TSQW',expected_locale='enUS',max_input_bytes=1048576,expected_records=meta['records'],expected_titles=expected,metadata_pins=pins,scope='Only217v2ownIDs; exact payload hashes and exact title hashes, not current enabled/inventory proof. Unused27cfg is supersededv1; no actual decoder executions yet.')
raw=(json.dumps(out,separators=(',',':'))+'\n').encode();assert len(raw)<=256*1024
(R/'source_inputs/source23-v2-expected-title-hashes.json').write_bytes(raw)
report=dict(status='V2_BINDING_READY_PENDING_FIRST_ACTUAL_DECODE',snapshot_version=2,snapshot_bytes=228447,snapshot_sha256=meta['sha256'],records=217,manifest='source_inputs/source23-v2-expected-title-hashes.json',manifest_bytes=len(raw),manifest_sha256=sha(raw),MAX_EXPECTED=256*1024,record_limit=217,manifest_exact_ID_payload_set_verified=True,title_qualified=sum(v['title_sha256'] is not None for v in expected.values()),title_held_ids=[int(q) for q,v in expected.items() if v['title_sha256'] is None],v1_status='SUPERSEDED_UNUSED_BEFORE_ANY_EXTRACTION; old27config and metadata preserved unchanged',source_pins_unchanged=True,public11_intake_rerun=False,source_pull=False,actual_WDB_decoder_runs=0,runtime_changed=False)
(R/'evidence/source23-v2-binding.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
