"""Qualify only the eight previously reviewed Player-target speech templates."""
import argparse,hashlib,json,pathlib,runpy,urllib.request,zipfile
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();archive=pathlib.Path('/workspace/foreverthai-dev/downloads/ForeverThai-0.462.0-Windows-Mac.zip');assert sha(archive.read_bytes())=='9eb4084c1f6c90d5cc05486b1ecb41951d6e3543cde9fb78b97686df73f81881';name='ForeverThai/Dev/NPCSpeech-0.462.0.json'
with zipfile.ZipFile(archive) as z:raw=z.read(name)
doc=json.loads(raw);assert len(doc['entries'])==len(doc['evidence'])==8;sig=runpy.run_path('/workspace/foreverthai-dev/combined/ForeverThai/Dev/Signature.py')['signature'];lua=LuaRuntime();a=lua.table();lua.execute((ROOT/'src/ForeverThai/SpeechData.lua').read_text(),'ForeverThai',a);rows=[]
for entry,evidence in zip(doc['entries'],doc['evidence']):
 for k in ['npc_id','quest_id','npc_name','event','english']:assert entry[k]==evidence[k]
 assert entry['source_kind']=='published_forever_words_with_exact_historical_player_target_corroboration';assert evidence['caller']['historical_only_not_current_server_code'];assert evidence['caller']['kind'] in ['explicit-Player-pointer','quest-start-dbscript','quest-end-dbscript'];assert evidence['caller']['target'] in ['GetPlayerForEscort()','Player::this'];assert entry['event']=='CHAT_MSG_MONSTER_SAY';assert entry['english'].count('$N')==1 and entry['english'].count('$')==1;assert entry['thai'].count('{name}')==1 and entry['thai'].count('{')==1
 signature=sig(entry['english']);matches=[value for _,value in a.speech[entry['npc_id']][entry['event']].items() if value[1]==signature and value[2]==entry['thai']];assert len(matches)==1;before,after=entry['english'].split('$N');rows.append(dict(**entry,signature=signature,prefix=before,suffix=after,caller=evidence['caller'],reference=evidence['reference'],original_entry_index=len(rows)))
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--download-api',action='store_true');args=parser.parse_args();pins=json.loads((ROOT/'tests/source_inputs/party-unit-api-pins.json').read_text());api=[];required={'UnitExists':('result','bool'),'UnitIsPlayer':('result','bool'),'UnitGUID':('result','WOWGUID'),'UnitName':('unitName','cstring'),'UnitInParty':('result','bool'),'UnitInRaid':('result','luaIndex')}
for pin in pins:
 if pin['path']!='UnitDocumentation.lua':continue
 path=ROOT/'work/party-api'/f"{pin['build']}-{pin['path']}"
 if args.download_api:
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(urllib.request.urlopen(pin['url']).read())
 data=path.read_bytes();assert len(data)==pin['bytes'] and sha(data)==pin['sha256'];text=data.decode();contracts=[]
 for function,(result,typ) in required.items():
  block=text.split('Name = "'+function+'"',1)[1].split('\n\t\t},',1)[0];assert 'Type = "Function"' in block and 'Type = "UnitToken' in block;assert f'Name = "{result}", Type = "{typ}"' in block
  if function in ['UnitGUID','UnitName','UnitInRaid']:assert 'SecretWhenUnit' in block
  contracts.append(dict(function=function,return_field=result,return_type=typ,block_sha256=sha(block.encode())))
 assert 'partyn' in text and 'raidn' in text;api.append(dict(**pin,contracts=contracts))
assert {v['build'] for v in api}=={'70862','70888'}
result=dict(source_zip=archive.name,source_zip_sha256=sha(archive.read_bytes()),source_document=name,source_document_sha256=sha(raw),source_pins=doc['source_pins'],qualified_templates=rows,unit_api_proofs=api,chat_api_proof='npc-api-proof.json: exact text arg1 and speaker guid arg12; arg5 playerName2 NOT used as addressee',historical_primary_cpp_files_transferred=False,qualification_scope='Reuse the already reviewed eight exact Player-name source qualifications from original Dev evidence, including typed historical Player callers. Their hash-pinned original C++ files are not newly downloaded or independently rerun here. This is not proof of current server code. No expansion to other N templates, normalized tokens or fixed Ringo/Torta/race/class references.',in_game_verified=False)
(ROOT/'evidence/party-source-audit11.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Qualified8existingPlayer-targettemplates;12UnitAPIcontracts on2pinnedbuilds; no arg5 recipient inference')
