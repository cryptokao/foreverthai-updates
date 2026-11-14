"""Actual immutable download-back; no runtime/matcher/font/game suite."""
import pathlib,json,urllib.request,hashlib,zipfile,io,stat
R=pathlib.Path(__file__).resolve().parents[1];OUT=R/'work/private-main21-r1';p=R/'evidence/candidate-main21-r1-delivery.json';d=json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();download={}
for key,name in [('zip_url','ForeverThai-0.466.0-cloud-main21-r1-PRIVATE-TEST.zip'),('guide_url','INSTALL-0.466.0-MAIN21-R1-PRIVATE-TH.txt'),('manifest_url','package-manifest.json'),('receipt_url','release-receipt.json')]:
 raw=urllib.request.urlopen(d[key],timeout=60).read();assert raw==(OUT/name).read_bytes(),name;download[name]=raw
raw=download['ForeverThai-0.466.0-cloud-main21-r1-PRIVATE-TEST.zip'];assert len(raw)==d['bytes'] and sha(raw)==d['sha256'];m=json.loads(download['package-manifest.json']);receipt=json.loads(download['release-receipt.json']);assert receipt['sha256']==sha(raw) and receipt['source_commit']==d['source_commit'];assert sha(raw) in download['INSTALL-0.466.0-MAIN21-R1-PRIVATE-TH.txt'].decode();manifest=m['runtime_manifest']
with zipfile.ZipFile(io.BytesIO(raw)) as z,zipfile.ZipFile(R/'work/private19/ForeverThai-0.466.0-cloud-main19-PRIVATE-TEST.zip') as b:
 assert z.testzip() is None and len(z.infolist())==len(set(z.namelist()))==141;assert set(z.namelist())==set(manifest)==set(b.namelist())
 for i in z.infolist():
  n=i.filename;parts=pathlib.PurePosixPath(n);assert not parts.is_absolute() and '..' not in parts.parts and '\\' not in n and not stat.S_ISLNK(i.external_attr>>16);blob=z.read(n);assert blob==(R/'src'/n).read_bytes();assert len(blob)==manifest[n]['bytes'] and sha(blob)==manifest[n]['sha256']
 changed=sorted(n for n in z.namelist() if z.read(n)!=b.read(n));assert changed==['ForeverThai/Catalog.lua'];assert sha(z.read('ForeverThai/Catalog.lua'))=='43ec92f88113114aef4918dcbe10c0bb89b7f222d6658dc5183c08c706f94f50'
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for n in protected+['ForeverThai/Speech.lua','ForeverThai/Atlas.lua','ForeverThai/Tracker.lua','ForeverThai/Match.lua']:assert z.read(n)==b.read(n)
 toc=z.read('ForeverThai/ForeverThai.toc').decode();paths=[s.strip().replace('\\','/') for s in toc.splitlines() if s.strip() and not s.startswith('#')];assert len(paths)==24 and all('ForeverThai/'+n in z.namelist() for n in paths);assert '## Version: 0.466.0' in toc and '## OptionalDeps: Questie' in toc
 for v in ['ForeverThaiDisplayMode','ForeverThaiObserved','ForeverThaiQuestieTracker','ForeverThaiAutoCaptureLog','ForeverThaiSpeech','AlphaWoWSkillsDB']:assert v in toc
 for n in ['ForeverThai/Skills/Core.lua','ForeverThai/Speech.lua']:assert 'build == "70938"' in z.read(n).decode()
 for n in m['atlas_texture_references']:assert n in z.namelist()
d.update(status='DOWNLOAD_BACK_VERIFIED',downloaded_back_verified=True,every_runtime_byte_verified=141,safe_unique_paths_verified=141,toc_paths_verified=24,protected28_byte_identical_to_MAIN19=True,unchanged_MAIN19_files=140,changed_from_MAIN19=changed,Core_Speech70938_Settings_Questie_SavedVariables_preserved=True,guide_manifest_receipt_exact_bytes_verified=True,all_old_fonts_Atlas_preserved=True,downloaded_artifact_hashes={n:dict(bytes=len(v),sha256=sha(v)) for n,v in download.items()},matching_rerun=False,old_suites_fonts_game_execution=False,customer_feed_changed=False)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(d,ensure_ascii=False,indent=2))
