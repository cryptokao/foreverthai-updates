"""Recover independent speech expectations from reviewed Dev JSON in the original ZIP.
Never import or inspect runtime SpeechData while constructing this corpus.
"""
import hashlib,json,pathlib,re,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=pathlib.Path('/workspace/foreverthai-dev/downloads/ForeverThai-0.462.0-Windows-Mac.zip')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert SOURCE.stat().st_size==25948703 and sha(SOURCE.read_bytes())=='9eb4084c1f6c90d5cc05486b1ecb41951d6e3543cde9fb78b97686df73f81881'
rows=[];manifest=[];keys=set()
with zipfile.ZipFile(SOURCE) as z:
 names=sorted([n for n in z.namelist() if re.fullmatch(r'ForeverThai/Dev/NPCSpeech-\d+\.\d+\.\d+\.json',n)],key=lambda n:tuple(map(int,n.rsplit('-',1)[1][:-5].split('.'))))
 for name in names:
  raw=z.read(name);document=json.loads(raw);entries=document.get('entries',[]);manifest.append(dict(path=name,bytes=len(raw),sha256=sha(raw),reviewed_entries=len(entries)))
  for i,entry in enumerate(entries):
   for key in ['npc_id','event','english','thai','review','review_sha256']:assert key in entry,(name,i,key)
   key=(entry['npc_id'],entry['event'],entry['english']);assert key not in keys,('Duplicate or competing expectation',name,i,key);keys.add(key)
   rows.append({**entry,'evidence_file':name,'evidence_entry_index':i,'evidence_file_sha256':sha(raw)})
report=dict(source_zip=SOURCE.name,source_zip_sha256=sha(SOURCE.read_bytes()),construction='Only reviewed entries arrays from Dev/NPCSpeech-*.json; no runtime SpeechData or inferred expected text; no deduplication/filtering against runtime.',source_files=manifest,independent_unique_forms=len(rows),entries=rows)
(ROOT/'tests/npc_corpus/reviewed-0462.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(len(rows),'independent unique NPC/event/English forms recovered from',len(manifest),'review documents')
