"""Verify immutable published13 against every current source byte and candidate12. No runtime suite rerun."""
import pathlib,json,urllib.request,hashlib,zipfile,re,io
r=pathlib.Path(__file__).resolve().parents[1];p=r/'evidence/candidate13-delivery.json';d=json.loads(p.read_text());b=urllib.request.urlopen(d['zip_url']).read();assert len(b)==d['bytes'] and hashlib.sha256(b).hexdigest()==d['sha256'];(r/'work/artifact13-download-verified.zip').write_bytes(b);m=json.loads(urllib.request.urlopen(d['manifest_url']).read());assert m['sha256']==d['sha256'] and m['party_templates']==16 and m['party_npcs']==7;checks=0
with zipfile.ZipFile(io.BytesIO(b)) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==137;assert set(z.namelist())==set(m['runtime_manifest'])
 for name,h in m['runtime_manifest'].items():
  path=pathlib.PurePosixPath(name);assert not path.is_absolute() and '..' not in path.parts and '\\' not in name;assert (z.getinfo(name).external_attr>>16&0o170000)!=0o120000;v=z.read(name);assert hashlib.sha256(v).hexdigest()==h and v==(r/'src'/name).read_bytes();checks+=1
 toc=z.read('ForeverThai/ForeverThai.toc').decode();paths=[v.strip().replace('\\','/') for v in toc.splitlines() if v.strip() and not v.startswith('#')];assert all('ForeverThai/'+v in z.namelist() for v in paths)
 for v in ['Tracker.lua','Observe.lua','Speech.lua','SpeechData.lua','Skills/Data.lua','Skills/RecipeData.lua','Skills/TalentTreeLabels.lua','Skills/ItemEffects.lua']:assert v in paths
 variables=re.search(r'^## SavedVariables: (.+)$',toc,re.M)[1]
 for v in ['ForeverThaiQuestieTracker','ForeverThaiDisplayMode','ForeverThaiObserved','ForeverThaiAutoCaptureLog','AlphaWoWSkillsDB','ForeverThaiSpeech']:assert v in variables
 assert '## OptionalDeps: Questie' in toc and len(paths)==24
 old=json.loads((r/'evidence/private-package-manifest12.json').read_text());changed=[n for n,h in old['runtime_manifest'].items() if hashlib.sha256(z.read(n)).hexdigest()!=h];assert sorted(changed)==['ForeverThai/Atlas.lua','ForeverThai/Catalog.lua']
 assert hashlib.sha256(z.read('ForeverThai/Catalog.lua')).hexdigest()==json.loads((r/'evidence/main-primary-regression13.json').read_text())['catalog_sha256']
 assert z.read('ForeverThai/Fonts/Thai89.tga')==(r/'src/ForeverThai/Fonts/Thai89.tga').read_bytes()
 assert sorted(set(z.namelist())-set(old['runtime_manifest']))==['ForeverThai/Fonts/Thai89.tga']
 baseline=zipfile.ZipFile('/workspace/foreverthai-dev/downloads/ForeverThai-0.462.0-Quest-Skills-PRIVATE-TEST.zip');protected=[n for n in baseline.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for name in protected:assert z.read(name)==baseline.read(name)
guide=urllib.request.urlopen(d['guide_url']).read().decode();assert d['sha256'] in guide and 'Interface/AddOns/ForeverThai/ForeverThai.toc' in guide and '_forever_' not in guide
d.update(downloaded_back_and_verified_on_cloud=True,downloaded_zip_every_byte_matches_current_src=True,downloaded_guide_and_manifest_verified=True,unique_safe_paths_checked=checks,toc_load_paths_checked=len(paths),protected_skill_font_assets_verified=28,saved_variables_and_questie_retained=True,changed_from_candidate12=changed,unchanged_candidate12_files=134,runtime_suites_rerun=False,comparison_manifest="private-package-manifest12.json");p.write_text(json.dumps(d,indent=2)+'\n');print('candidate13 downloaded ZIP/137 safe file paths/every byte/28 protected assets/TOC/SavedVariables/guide/manifest passed')
