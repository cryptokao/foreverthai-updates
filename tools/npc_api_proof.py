"""API-source-only proof. Does not rerun speech/Skill runtime simulations."""
import hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];pins=json.loads((ROOT/'tests/recovered_npc/api-source-pins.json').read_text());rows=[]
for pin in pins['pins']:
 path=pathlib.Path('/workspace/foreverthai-dev/recovered-npc-api')/('ChatInfoDocumentation-'+pin['build']+'.lua');raw=path.read_bytes()
 assert len(raw)==pin['document_bytes'] and hashlib.sha256(raw).hexdigest()==pin['document_sha256']
 text=raw.decode();events=[]
 for event in pins['expected_event_payload']['events']:
  block=text.split('LiteralName = "'+event+'"',1)[1].split('\n\t\t},',1)[0]
  fields=re.findall(r'Name = "([^"]+)"',block)
  assert fields[0]=='text' and fields[11]=='guid',(pin['build'],event,fields)
  assert fields[4]=='playerName2',(pin['build'],event,fields)
  events.append(dict(event=event,argument_1=fields[0],argument_5=fields[4],argument_12=fields[11],all_argument_names=fields))
 rows.append(dict(build=pin['build'],commit=pin['commit'],raw_url=pin['raw_url'],bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),events=events))
report=dict(status='passed',proof_kind='Fresh Cloud pinned raw-source download/hash and historical event-order assertions only',builds=rows,event_layouts_checked=sum(len(v['events']) for v in rows),runtime_tests_rerun=False,group_recipient_inference=False,identity_scope='playerName2 at arg5 does not prove a party addressee. Current-player typed restrictions and fixed NPC-name handling remain unchanged.',in_game_verified=False)
(ROOT/'evidence/npc-api-proof.json').write_text(json.dumps(report,indent=2)+'\n');print('API proof: 8 event layouts across 70862/70888 passed; no runtime rerun')
