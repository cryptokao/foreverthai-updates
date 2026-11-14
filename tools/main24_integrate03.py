"""Integrate exact approved02 additively; existing canonical entries become variant parents."""
import pathlib,json,hashlib,re
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];p=R/'src/ForeverThai/Catalog.lua';raw=(R/'evidence/main24-proposal03.json').read_bytes();b=json.loads(raw);review=json.loads((R/'evidence/root-main24-proposal03-review.json').read_text());sha=lambda v:hashlib.sha256(v).hexdigest();assert review['status']=='ROOT_FULL_ENGLISH_THAI_MEANING_REVIEW_APPROVED_FOR_EXACT_SOURCE_INTEGRATION' and review['fields_approved']==42;assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==review['proposal_blob'];assert {(f['quest_id'],f['field'],f['english_sha256'],f['thai_sha256']) for f in b['fields']}=={(f['quest_id'],f['field'],f['english_sha256'],f['thai_sha256']) for f in review['fields']}
before=p.read_bytes();assert sha(before)==b['integrated_prior_Catalog_sha256'];l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n,s in [('Catalog',before.decode()),('Match',(R/'src/ForeverThai/Match.lua').read_text())]:l.execute(s,'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end');lines=['','-- MAIN24 proposal03: exact42 Root24860a9f approved; text-only pending fonts.'];added=[];variants=[]
for f in b['fields']:
 q,key=f['quest_id'],f['field'];assert q!=2752;assert sha(f['english'].encode())==f['english_sha256'] and sha(f['thai'].encode())==f['thai_sha256'];entry=a.quests[q][key] if a.quests[q] else None;assert a.Translate(entry,re.sub(r'\$[Bb]','\n',f['english'])) is None
 value='{ '+json.dumps(f['signature'])+', '+json.dumps(f['thai'],ensure_ascii=False)+' }';lines.append(f'addon.quests[{q}] = addon.quests[{q}] or {{}}')
 if entry is None:lines.append(f'addon.quests[{q}].{key} = '+value);added.append(dict(quest_id=q,field=key))
 else:
  parent=f'addon.quests[{q}].{key}';lines.extend([parent+'.variants = '+parent+'.variants or {}',parent+'.variants[#'+parent+'.variants + 1] = '+value]);variants.append(dict(quest_id=q,field=key))
p.write_bytes(before+('\n'.join(lines)+'\n').encode());report=dict(status='SOURCE_INTEGRATED122_TEXT_ONLY_PENDING_BITMAP_FONTS',Root_approval='main24860a9f4e0032f2effbe34024f76c2269aedfbb',proposal03_sha256=sha(raw),baseline_Catalog_sha256=sha(before),final_Catalog_sha256=sha(p.read_bytes()),old_Catalog_exact_prefix_preserved=True,approved03_fields=42,new_slots=added,existing_canonical_variant_appends=variants,prior80_retained_fields=80,total_MAIN24_integrated=122,new_Thai03=15,exact_reviewed_reuse03=27,quest2752_untouched=True,fonts_version_build_ZIP_feed_changed=False)
(R/'evidence/main24-integration03.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['new_slots','existing_canonical_variant_appends']},indent=2));print('newslots',len(added),'variants',len(variants))
