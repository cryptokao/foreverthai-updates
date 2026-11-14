"""Distinct immutable through-main18 revision; package/hash checks only, no suite/join rerun."""
import pathlib,json,hashlib,zipfile,re,subprocess
R=pathlib.Path(__file__).resolve().parents[1];RUN=R/'src/ForeverThai';OUT=R/'work/private18';OUT.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();basepath=R/'work/private17/ForeverThai-0.465.0-cloud-main17-PRIVATE-TEST.zip';assert sha(basepath.read_bytes())=='373e17e2dff939737ae4b8556571625d83fe09dfb0cb22488a38050d53c3ad75'
review=json.loads((R/'evidence/root-main18-wording-review.json').read_text());doc=json.loads((R/'evidence/main18-translations.json').read_text());approved={(v['quest_id'],v['field']):v for v in review['approved_fields']}
for f in doc['fields']:
 v=approved[f['quest_id'],f['field']];assert f['english']==v['english'] and f['thai']==v['thai'];assert sha(f['english'].encode())==v['english_sha256'] and sha(f['thai'].encode())==v['thai_sha256']
cat=(RUN/'Catalog.lua').read_bytes();old17=subprocess.check_output(['git','-C',str(R),'show','f32eb64:src/ForeverThai/Catalog.lua']);old16=subprocess.check_output(['git','-C',str(R),'show','1e04b81:src/ForeverThai/Catalog.lua']);assert cat.startswith(old17) and old17.startswith(old16)
manifest={str(p.relative_to(R/'src')):sha(p.read_bytes()) for p in sorted(RUN.rglob('*')) if p.is_file()};assert len(manifest)==140
with zipfile.ZipFile(basepath) as base,zipfile.ZipFile(R/'work/customer4631/ForeverThai-0.463.1.zip') as customer:
 assert set(manifest)==set(base.namelist());changed=sorted(n for n in manifest if manifest[n]!=sha(base.read(n)));assert changed==['ForeverThai/Catalog.lua'];protected=[n for n in customer.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for n in protected+['ForeverThai/Speech.lua']:assert (R/'src'/n).read_bytes()==customer.read(n)
 toc=(RUN/'ForeverThai.toc').read_text();paths=[s.strip().replace('\\','/') for s in toc.splitlines() if s.strip() and not s.startswith('#')];assert len(paths)==24 and all('ForeverThai/'+n in manifest for n in paths);assert '## Version: 0.465.0' in toc and '## OptionalDeps: Questie' in toc
 for key in ['ForeverThaiDisplayMode','ForeverThaiObserved','ForeverThaiQuestieTracker','ForeverThaiAutoCaptureLog','ForeverThaiSpeech','AlphaWoWSkillsDB']:assert key in toc
artifact='ForeverThai-0.465.0-cloud-through-main18-PRIVATE-TEST.zip';p=OUT/artifact
with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n in manifest:
  info=zipfile.ZipInfo(n,date_time=(2026,11,13,0,0,0));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(R/'src'/n).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for n in manifest:assert z.read(n)==(R/'src'/n).read_bytes()
final=json.loads((R/'evidence/main17-final-text-hashes.json').read_text());final.update(root_review_main18='main0f7a1843',catalog_sha256=sha(cat),catalog16_and17_exact_prefix_preserved=True,main18_fields=[dict(quest_id=f['quest_id'],field=f['field'],english_sha256=f['english_sha256'],thai_sha256=f['thai_sha256']) for f in doc['fields']],combined_newly_supported_fields=24,combined_unique_quest_ids=19,combined_new_thai_fields=14,combined_reused_fields=10,scope='24supportedfields across19IDs, not19completequests or whole-game inventory.')
(R/'evidence/main18-final-text-hashes.json').write_text(json.dumps(final,indent=2)+'\n');(OUT/'final-text-hashes.json').write_text(json.dumps(final,indent=2)+'\n')
m=dict(version='0.465.0',revision='cloud-through-main18-PRIVATE-TEST',artifact=artifact,bytes=p.stat().st_size,sha256=sha(p.read_bytes()),files=140,runtime_manifest=manifest,changed_from_private17=changed,unchanged_private17_files=139,added_files=[],removed_files=[],toc_paths=24,toc_version_unchanged=True,savedvariables_questie_preserved=True,protected28_and_core_speech70938_equal_customer4631=True,atlas_all_font_bytes_unchanged=True,catalog16_17_exact_prefix_preserved=True,final_catalog_sha256=sha(cat),combined_newly_supported_fields=24,combined_unique_quest_ids=19,new_thai_fields=14,reused_fields=10,main18_new_thai_titles=2,main18_reused_title=1,new_main18_objectives=0,fonts_generated=False,main18_join_or_runtime_suites_rerun=False,customer_feed_changed=False,windows_mac_m2_in_game_verified=False)
(OUT/'package-manifest.json').write_text(json.dumps(m,indent=2)+'\n');(R/'evidence/private-package-manifest18.json').write_text(json.dumps(m,indent=2)+'\n');doc['root_wording_review']='approved unchanged main0f7a1843';(R/'evidence/main18-translations.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in m.items() if k!='runtime_manifest'},indent=2))
