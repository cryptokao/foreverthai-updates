"""Download-back package-only verification for immutable through-main18 revision."""
import pathlib,json,urllib.request,hashlib,zipfile,io,stat
R=pathlib.Path(__file__).resolve().parents[1];p=R/'evidence/candidate18-delivery.json';d=json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();raw=urllib.request.urlopen(d['zip_url']).read();assert len(raw)==d['bytes'] and sha(raw)==d['sha256'];files={}
for key,n in [('guide_url','INSTALL-THROUGH-MAIN18-PRIVATE-TH.txt'),('manifest_url','package-manifest.json'),('final_text_hashes_url','final-text-hashes.json'),('receipt_url','release-receipt.json')]:
 b=urllib.request.urlopen(d[key]).read();assert b==(R/'work/private18'/n).read_bytes();files[n]=b
m=json.loads(files['package-manifest.json']);h=json.loads(files['final-text-hashes.json']);receipt=json.loads(files['release-receipt.json']);assert receipt['sha256']==sha(raw) and receipt['source_commit']==d['source_commit'];baseline=R/'work/private17/ForeverThai-0.465.0-cloud-main17-PRIVATE-TEST.zip';assert sha(baseline.read_bytes())=='373e17e2dff939737ae4b8556571625d83fe09dfb0cb22488a38050d53c3ad75'
with zipfile.ZipFile(io.BytesIO(raw)) as z,zipfile.ZipFile(baseline) as old,zipfile.ZipFile(R/'work/customer4631/ForeverThai-0.463.1.zip') as customer:
 assert z.testzip() is None and len(z.infolist())==len(set(z.namelist()))==140;assert set(z.namelist())==set(old.namelist())==set(m['runtime_manifest'])
 for i in z.infolist():
  name=i.filename;parts=pathlib.PurePosixPath(name);assert not parts.is_absolute() and '..' not in parts.parts and '\\' not in name and not stat.S_ISLNK(i.external_attr>>16);b=z.read(name);assert b==(R/'src'/name).read_bytes() and sha(b)==m['runtime_manifest'][name]
 changed=sorted(n for n in old.namelist() if z.read(n)!=old.read(n));assert changed==['ForeverThai/Catalog.lua'];assert z.read('ForeverThai/Catalog.lua').startswith(old.read('ForeverThai/Catalog.lua'))
 protected=[n for n in customer.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for n in protected+['ForeverThai/Speech.lua']:assert z.read(n)==customer.read(n)
 toc=z.read('ForeverThai/ForeverThai.toc').decode();paths=[s.strip().replace('\\','/') for s in toc.splitlines() if s.strip() and not s.startswith('#')];assert len(paths)==24 and all('ForeverThai/'+n in z.namelist() for n in paths);assert '## Version: 0.465.0' in toc and '## OptionalDeps: Questie' in toc
 for v in ['ForeverThaiQuestieTracker','ForeverThaiDisplayMode','ForeverThaiObserved','ForeverThaiAutoCaptureLog','AlphaWoWSkillsDB','ForeverThaiSpeech']:assert v in toc
 assert sha(z.read('ForeverThai/Catalog.lua'))==h['catalog_sha256']
d.update(downloaded_back_verified=True,every_runtime_byte_verified=140,safe_unique_paths_verified=140,toc_paths_verified=24,changed_from_private17=changed,unchanged_private17_runtime_files=139,added_files=[],removed_files=[],atlas_all_fonts_toc_settings_questie_byte_unchanged=True,protected_assets_unchanged_from_customer4631=28,core_speech70938_equal_customer4631=True,catalog16_17_exact_prefix_preserved=True,guide_manifest_hashes_receipt_download_verified=True,final_catalog_sha256=h['catalog_sha256'],main18_join_or_runtime_suites_rerun=False,verification_scope='Package/hash/path/TOC/declaration and exact-byte preservation only; no join/old tests/Skills/NPC/party rerun or game proof.')
p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
