"""Apply reviewed additive fields without regenerating any existing Catalog aliases."""
import json,pathlib,re
root=pathlib.Path(__file__).resolve().parents[1];p=root/'src/ForeverThai/Catalog.lua';data=p.read_bytes();batch=json.loads((root/'evidence/main-objectives-01.json').read_text())
for f in batch['fields']:
 pattern=rb'(    \['+str(f['quest_id']).encode()+rb'\] = \{ --[^\r\n]*\r?\n)'
 block=re.search(pattern+rb'(.*?)(?=\r?\n    \[|\Z)',data,re.S);assert block,f['quest_id']
 line=('        objective = { '+json.dumps(f['signature'])+', '+json.dumps(f['thai'],ensure_ascii=False)+' },\r\n').encode()
 if b'        objective = ' in block[0]:assert line in block[0],f['quest_id'];continue
 data=re.sub(pattern,lambda m:m[0]+line,data,count=1)
p.write_bytes(data)
