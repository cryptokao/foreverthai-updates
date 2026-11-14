"""Download actual immutable24 artifacts and compare every byte/reference; no old suites."""
import pathlib,json,hashlib,urllib.request,zipfile,io,stat
R=pathlib.Path(__file__).resolve().parents[1];OUT=R/'work/private24';p=R/'evidence/candidate24-delivery.json';d=json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();got={}
for key,name in [('zip_url','ForeverThai-0.467.0-cloud-main24-PRIVATE-TEST.zip'),('guide_url','INSTALL-0.467.0-PRIVATE-TH.txt'),('manifest_url','package-manifest.json'),('receipt_url','release-receipt.json'),('final_text_hashes_url','final-text-hashes.json')]:
 raw=urllib.request.urlopen(d[key],timeout=60).read();assert raw==(OUT/name).read_bytes(),name;got[name]=raw
raw=got['ForeverThai-0.467.0-cloud-main24-PRIVATE-TEST.zip'];assert sha(raw)==d['sha256'] and len(raw)==d['bytes'];m=json.loads(got['package-manifest.json']);assert sha(raw) in got['INSTALL-0.467.0-PRIVATE-TH.txt'].decode()
with zipfile.ZipFile(io.BytesIO(raw)) as z,zipfile.ZipFile(R/'work/private-main21-r1/ForeverThai-0.466.0-cloud-main21-r1-PRIVATE-TEST.zip') as b:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==145 and set(z.namelist())==set(m['runtime_manifest'])
 for i in z.infolist():
  n=i.filename;v=z.read(n);pp=pathlib.PurePosixPath(n);assert not pp.is_absolute() and '..' not in pp.parts and '\\' not in n and not stat.S_ISLNK(i.external_attr>>16);assert v==(R/'src'/n).read_bytes() and sha(v)==m['runtime_manifest'][n]['sha256'] and len(v)==m['runtime_manifest'][n]['bytes']
 assert sorted(n for n in b.namelist() if b.read(n)!=z.read(n))==m['changed_from_MAIN21r1'];assert sorted(set(z.namelist())-set(b.namelist()))==m['added_files']
 protected=[n for n in b.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for n in protected+['ForeverThai/Speech.lua','ForeverThai/Tracker.lua','ForeverThai/Match.lua','ForeverThai/Events.lua','ForeverThai/Bitmap.lua','ForeverThai/Panel.lua']:assert z.read(n)==b.read(n)
 fonts=[n for n in b.namelist() if '/Fonts/' in n];assert len(fonts)==108
 for n in fonts:assert z.read(n)==b.read(n)
 for n in ['Atlas.lua','Catalog.lua']:assert z.read('ForeverThai/'+n).startswith(b.read('ForeverThai/'+n))
 toc=z.read('ForeverThai/ForeverThai.toc').decode();paths=[v.strip().replace('\\','/') for v in toc.splitlines() if v.strip() and not v.startswith('#')];assert len(paths)==24 and all('ForeverThai/'+n in z.namelist() for n in paths);assert '## Version: 0.467.0' in toc and '## OptionalDeps: Questie' in toc
 for s in ['ForeverThaiDisplayMode','ForeverThaiObserved','ForeverThaiQuestieTracker','ForeverThaiAutoCaptureLog','ForeverThaiSpeech','AlphaWoWSkillsDB']:assert s in toc
 for n in ['ForeverThai/Skills/Core.lua','ForeverThai/Speech.lua']:assert 'build == "70938"' in z.read(n).decode()
 for n in m['atlas_texture_references']:assert n in z.namelist()
d.update(status='DOWNLOAD_BACK_ALL_BYTES_VERIFIED',downloaded_back_verified=True,safe_paths_verified=145,every_runtime_byte_verified=145,toc_paths_verified=24,old_font_assets_exact_bytes_preserved=108,protected28_exact_bytes_preserved=True,CoreSpeech70938_Tracker_Settings_Questie_preserved=True,guide_manifest_receipt_finalhashes_exact_bytes_verified=True,downloaded_artifact_hashes={n:dict(bytes=len(v),sha256=sha(v)) for n,v in got.items()},known_Tracker_multiline_fallback_retained='84213objective English in native/Questie; questpane BitmapLayer Thai passes',game_verified=False,old_suites_rerun=False,customer_feed_changed=False)
p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
