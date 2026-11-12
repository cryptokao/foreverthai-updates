"""Independently verify eight additional existing Player-target qualifications.
PC draft is a lead only: use original Dev456, pinned raw callers and corpus/runtime.
"""
import argparse,hashlib,json,pathlib,re,runpy,urllib.request,zipfile
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--download',action='store_true');args=parser.parse_args();assessment=json.loads((ROOT/'evidence/root-local-draft-assessment.json').read_text());base_path=ROOT/'evidence/party-source-audit11.json';base=json.loads(base_path.read_text());pins=json.loads((ROOT/'tests/source_inputs/party-extra-primary-pins12.json').read_text());sources={}
for p in pins:
 path=ROOT/'work/party16'/pathlib.Path(p['path']).name
 if args.download:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(urllib.request.urlopen(p['raw_url']).read())
 raw=path.read_bytes();assert len(raw)==p['bytes'] and sha(raw)==p['sha256'];sources[path.name]=raw.decode()
archive=pathlib.Path('/workspace/foreverthai-dev/downloads/ForeverThai-0.462.0-Windows-Mac.zip');assert sha(archive.read_bytes())==base['source_zip_sha256'];docpath='ForeverThai/Dev/NPCSpeech-0.456.0.json'
with zipfile.ZipFile(archive) as z:raw=z.read(docpath)
assert len(raw)==42987 and sha(raw)=='0b161ac06475061eb3948351c952c4992e7cc266256f615b760b9bbd69707ca0';doc=json.loads(raw);corpus=json.loads((ROOT/'tests/npc_corpus/reviewed-0462.json').read_text());sig=runpy.run_path('/workspace/foreverthai-dev/combined/ForeverThai/Dev/Signature.py')['signature'];lua=LuaRuntime();a=lua.table();lua.execute((ROOT/'src/ForeverThai/SpeechData.lua').read_text(),'ForeverThai',a);rows=[]
for index,entry in enumerate(doc['entries']):
 if entry['npc_id'] not in [12717,2768] or '$N' not in entry['english']:continue
 evidence=next(v for v in doc['evidence'] if (v['npc_id'],v['event'],v['english'])==(entry['npc_id'],entry['event'],entry['english']));caller=evidence['caller'];assert caller['target']=='explicit_Player_pointer' and caller['historical_only_not_current_server_code'];cpp=sources[pathlib.Path(caller['file']).name];pin=next(p for p in pins if p['path'].endswith(pathlib.Path(caller['file']).name));assert caller['sha256']==pin['sha256'];constant=caller['constant'];value=int(re.search(r'\b'+constant+r'\s*=\s*(-?\d+)',cpp)[1]);assert value==evidence['reference']['id'];assert caller['call']+';' in cpp
 offset=cpp.index(caller['call']+';');context=cpp[max(0,offset-700):offset]
 if entry['npc_id']==12717:assert 'Player* player = GetPlayerForEscort()' in context;pointer='GetPlayerForEscort() -> Player* player'
 elif constant=='SAY_PROGRESS_1':assert 'QuestAccept_npc_professor_phizzlethorpe(Player* pPlayer,' in context;pointer='QuestAccept typed Player* pPlayer'
 else:
  method=cpp[cpp.index('void WaypointReached('):cpp.index('void Aggro(')];assert caller['call']+';' in method and 'Player* pPlayer = GetPlayerForEscort();' in method and 'if (!pPlayer)' in method;pointer='WaypointReached: checked GetPlayerForEscort() -> Player* pPlayer'
 assert entry['event']=='CHAT_MSG_MONSTER_SAY' and entry['english'].count('$N')==1 and entry['english'].count('$')==1;assert entry['thai'].count('{name}')==entry['thai'].count('{')==1;signature=sig(entry['english']);assert sum(v[1]==signature and v[2]==entry['thai'] for _,v in a.speech[entry['npc_id']][entry['event']].items())==1
 independent=[v for v in corpus['entries'] if (v['npc_id'],v['event'],v['english'],v['thai'])==(entry['npc_id'],entry['event'],entry['english'],entry['thai'])];assert len(independent)==1;assert independent[0]['evidence_file']==docpath and independent[0]['evidence_entry_index']==index
 prefix,suffix=entry['english'].split('$N');rows.append(dict(**entry,signature=signature,prefix=prefix,suffix=suffix,caller=caller,reference=evidence['reference'],original_entry_index=index,caller_line=cpp[:offset].count('\n')+1,constant_value=value,independent_pointer_proof=pointer,primary_source=pin,corpus_evidence_file=independent[0]['evidence_file'],corpus_evidence_entry_index=index))
assert len(rows)==8 and sum(v['npc_id']==12717 for v in rows)==5 and sum(v['npc_id']==2768 for v in rows)==3
for lead in assessment['additional_records']:assert any(all(v[k]==lead[k] for k in ['npc_id','quest_id','npc_name','level','event','english','thai']) for v in rows)
combined=base['qualified_templates']+rows;assert len(combined)==16 and len({(v['npc_id'],v['event'],v['signature']) for v in combined})==16
result=dict(source_zip=archive.name,source_zip_sha256=base['source_zip_sha256'],source_document=docpath,source_document_bytes=len(raw),source_document_sha256=sha(raw),base_qualification_file='party-source-audit11.json',base_qualification_sha256=sha(base_path.read_bytes()),additional_qualified_templates=rows,qualified_templates=combined,total_templates=16,total_npcs=len({v['npc_id'] for v in combined}),new_prose=0,new_thai=0,new_primary_cpp_pins=pins,historical_only_not_current_forever_server=True,pc_draft_code_used=False,role_words_separation='Forever English/Thai and signatures come only from original transferred Dev and independent686 corpus. Fresh historical C++ constants/typed pointers corroborate Player roles only; no Classic words replace Forever. Existing11algorithm and sharedMatch remain unchanged.',in_game_verified=False)
(ROOT/'evidence/party-source-audit12.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Additional8: Muglash5/Professor3; verified Dev456/hash/corpus/Thai/signatures/constants/Player*callers. Total16templates/7NPCs;0newprose.')
