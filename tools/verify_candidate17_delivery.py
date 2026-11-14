"""Download-back actual immutable private17 bytes/paths/TOC/components; no unchanged suites."""
import pathlib,json,urllib.request,hashlib,zipfile,io,stat
ROOT=pathlib.Path(__file__).resolve().parents[1];p=ROOT/'evidence/candidate17-delivery.json';d=json.loads(p.read_text());raw=urllib.request.urlopen(d['zip_url']).read();assert len(raw)==d['bytes'] and hashlib.sha256(raw).hexdigest()==d['sha256'];m=json.loads(urllib.request.urlopen(d['manifest_url']).read());h=json.loads(urllib.request.urlopen(d['final_text_hashes_url']).read());guide=urllib.request.urlopen(d['guide_url']).read();assert guide==(ROOT/'work/private17/INSTALL-0.465.0-PRIVATE-TH.txt').read_bytes();assert m==json.loads((ROOT/'work/private17/package-manifest.json').read_text());assert h==json.loads((ROOT/'evidence/main17-final-text-hashes.json').read_text());assert d['sha256'] in guide.decode()
with zipfile.ZipFile(io.BytesIO(raw)) as z,zipfile.ZipFile(ROOT/'work/private16/ForeverThai-0.464.0-cloud-main16-PRIVATE-TEST.zip') as base:
 assert z.testzip() is None and len(z.infolist())==len(set(z.namelist()))==140
 assert set(z.namelist())==set(m['runtime_manifest']);assert set(base.namelist())<=set(z.namelist())
 for i in z.infolist():
  name=i.filename;parts=pathlib.PurePosixPath(name);assert not parts.is_absolute() and '..' not in parts.parts and '\\' not in name and not stat.S_ISLNK(i.external_attr>>16);b=z.read(name);assert b==(ROOT/'src'/name).read_bytes() and hashlib.sha256(b).hexdigest()==m['runtime_manifest'][name]
 protected=[n for n in base.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for n in protected+['ForeverThai/Speech.lua','ForeverThai/Tracker.lua','ForeverThai/Match.lua']:assert z.read(n)==base.read(n)
 for n in base.namelist():
  if '/Fonts/' in n:assert z.read(n)==base.read(n)
 changed=sorted(n for n in base.namelist() if z.read(n)!=base.read(n));assert changed==['ForeverThai/Atlas.lua','ForeverThai/Catalog.lua','ForeverThai/ForeverThai.toc','ForeverThai/SOURCES-TH.txt'];assert sorted(set(z.namelist())-set(base.namelist()))==['ForeverThai/Fonts/Thai92.tga']
 toc=z.read('ForeverThai/ForeverThai.toc').decode();paths=[s.strip().replace('\\','/') for s in toc.splitlines() if s.strip() and not s.startswith('#')];assert len(paths)==24 and all('ForeverThai/'+n in z.namelist() for n in paths);assert '## Version: 0.465.0' in toc and '## OptionalDeps: Questie' in toc
 for v in ['ForeverThaiQuestieTracker','ForeverThaiDisplayMode','ForeverThaiObserved','ForeverThaiAutoCaptureLog','AlphaWoWSkillsDB','ForeverThaiSpeech']:assert v in toc
 assert hashlib.sha256(z.read('ForeverThai/Catalog.lua')).hexdigest()==h['catalog_sha256']
with zipfile.ZipFile(ROOT/'work/customer4631/ForeverThai-0.463.1.zip') as customer,zipfile.ZipFile(io.BytesIO(raw)) as candidate:
 for n in protected+['ForeverThai/Speech.lua']:assert candidate.read(n)==customer.read(n)
d.update(downloaded_back_verified=True,every_runtime_byte_verified=140,safe_unique_paths_verified=140,toc_paths_verified=24,protected_assets_unchanged_from4631=28,core_speech70938_unchanged_from4631=True,unchanged_private16_files=135,all_old_font_pages_unchanged=True,savedvariables_and_questie_retained=True,guide_manifest_final_text_hashes_download_verified=True,final_catalog_sha256=h['catalog_sha256'],runtime_suites_rerun=False)
p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
