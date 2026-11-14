"""Only38 manually written proposal fields: read-only pin/hash/quantity checks, no integration."""
import pathlib,json,subprocess,hashlib,re
R=pathlib.Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/main24-proposal01.json').read_text());sha=lambda v:hashlib.sha256(v).hexdigest();cache={};checks=0
assert b['status']=='ROOT_FULL_MEANING_REVIEW_PENDING_NOT_IN_RUNTIME' and len(b['fields'])==38
for f in b['fields']:
 assert f['quest_id']!=2752 and sha(f['english'].encode())==f['english_sha256'] and sha(f['thai'].encode())==f['thai_sha256'];assert '$' not in f['english'] and not re.search(r'\{[^}]*\}',f['thai'])
 for ref in f['source_refs']:
  path=ref['path']
  if path not in cache:cache[path]=json.loads(subprocess.check_output(['git','-C',str(R/'work/eg'),'show',f['source_pin']+':'+path]))
  v=cache[path]
  for k in ref['pointer'].split('/')[1:]:v=v[int(k)] if isinstance(v,list) else v[k]
  assert v==f['english'];checks+=1
by={(f['quest_id'],f['field']):f for f in b['fields']}
for q,en,th in [(81769,'7 Vengeful Ancients','Vengeful Ancients จำนวน 7 ตน'),(81777,'10 Dreamroot','Dreamroot จำนวน 10 ชิ้น')]:assert en in by[q,'objective']['english'] and th in by[q,'objective']['thai']
for q,num in {81769:'II',81774:'VII',81775:'VIII',81777:'X',81780:'XIII',81781:'XIV',81784:'XVII'}.items():assert f'Ashenvale Mission {num}:' in by[q,'title']['english'] and f'Ashenvale {num}:' in by[q,'title']['thai']
for q,f,en,th in [(80411,'description','alone','เพียงลำพัง'),(80453,'description','into, or out of','เข้าไปหรือดึงพลังเวทออกมา'),(82068,'description','today','วันนี้'),(81777,'description','assistance of an herbalist','ความช่วยเหลือจากนักสมุนไพร')]:assert en in by[q,f]['english'] and th in by[q,f]['thai']
assert sha((R/'src/ForeverThai/Catalog.lua').read_bytes())==b['baseline_Catalog_sha256'];assert not subprocess.check_output(['git','-C',str(R),'diff',b['baseline_source'],'--','src/ForeverThai'])
print(json.dumps(dict(status='proposal_source_hash_static_checks_passed',unique_fields=38,source_pointer_checks=checks,runtime_integration=False,matcher_or_old_suites=False)))
