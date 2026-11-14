"""Freeze combined main19 private candidate; no old Skill/NPC/party suite rerun."""
import ast,hashlib,json,pathlib,re,sys,tempfile,zipfile,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';OUT=ROOT/'work/private19';OUT.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();baseline=ROOT/'work/private18/ForeverThai-0.465.0-cloud-through-main18-PRIVATE-TEST.zip';assert sha(baseline.read_bytes())=='a1eb804cdf7648f259c8868202b85f91d401400a84802aa2fa7a62775c16eaa1'
p=RUN/'ForeverThai.toc';oldtoc=p.read_bytes();assert oldtoc.count(b'## Version: 0.465.0')==1 or b'## Version: 0.466.0' in oldtoc;p.write_bytes(oldtoc.replace(b'## Version: 0.465.0',b'## Version: 0.466.0'))
manifest={str(p.relative_to(ROOT/'src')):sha(p.read_bytes()) for p in sorted(RUN.rglob('*')) if p.is_file()}
with zipfile.ZipFile(baseline) as base:
 assert len(base.namelist())==140 and len(manifest)==141
 assert set(base.namelist())<=set(manifest)
 changed=sorted(n for n in base.namelist() if sha(base.read(n))!=manifest[n]);added=sorted(set(manifest)-set(base.namelist()));assert changed==['ForeverThai/Atlas.lua','ForeverThai/Catalog.lua','ForeverThai/ForeverThai.toc','ForeverThai/SOURCES-TH.txt'];assert added==['ForeverThai/Fonts/Thai93.tga']
 protected=[n for n in base.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for n in protected+['ForeverThai/Speech.lua','ForeverThai/Match.lua','ForeverThai/Tracker.lua']:assert (ROOT/'src'/n).read_bytes()==base.read(n)
 assert p.read_bytes()==base.read('ForeverThai/ForeverThai.toc').replace(b'## Version: 0.465.0',b'## Version: 0.466.0')
artifact='ForeverThai-0.466.0-cloud-main19-PRIVATE-TEST.zip';archive=OUT/artifact
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in manifest:
  info=zipfile.ZipInfo(name,date_time=(2026,11,13,0,0,0));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(ROOT/'src'/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
# Actual candidate ZIP only: basic combined TOC/settings fixture, not nine Skill cases.
import legacy_skill_runner as legacy
sys.path.insert(0,str(legacy.RECOVERED/'tests'));import test_recipe_panel
with zipfile.ZipFile(archive) as z,tempfile.TemporaryDirectory() as tmp:
 assert z.testzip() is None and len(z.namelist())==141
 for name,h in manifest.items():assert sha(z.read(name))==h and z.read(name)==(ROOT/'src'/name).read_bytes()
 toc=z.read('ForeverThai/ForeverThai.toc').decode();paths=legacy.modules(toc);assert len(paths)==24 and all('ForeverThai/'+n in z.namelist() for n in paths);assert '## OptionalDeps: Questie' in toc
 for k in ['ForeverThaiDisplayMode','ForeverThaiObserved','ForeverThaiQuestieTracker','ForeverThaiAutoCaptureLog','ForeverThaiSpeech','AlphaWoWSkillsDB']:assert k in toc
 z.extractall(pathlib.Path(tmp)/'addon');test_recipe_panel.ROOT=pathlib.Path(tmp);fixture=test_recipe_panel.RecipePanelTests();fixture.setUp();lua=fixture.lua
 parsed=ast.parse((ROOT/'tools/legacy_skill_runner.py').read_text());check=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='check');init=next(n.value for n in ast.walk(check) if isinstance(n,ast.Constant) and isinstance(n.value,str) and 'addon={};frames={};SlashCmdList' in n.value).replace('"70888"','"70938"');lua.execute(init);a=lua.globals().addon
 for name in paths:lua.execute(z.read('ForeverThai/'+name).decode(),'ForeverThai',a)
 lua.execute('event("ADDON_LOADED","ForeverThai");assert(addon.skills.supported and addon.skills.settings.fontSize==19 and AlphaWoWSkillsDB.enabled);assert(ForeverThaiQuestieTracker==true);assert(SlashCmdList.FOREVERTHAI and SlashCmdList.ALPHAWOWSKILLS)')
 lua.execute('messages={};print=function(s)messages[#messages+1]=s end;addon.SpeechCommand("speech on");assert(not messages[1]:find("unsupported client",1,true));assert(ForeverThaiSpeech.enabled==true);addon.SpeechCommand("speech off");assert(ForeverThaiSpeech.enabled==false)')
 for text in [z.read('ForeverThai/Skills/Core.lua').decode(),z.read('ForeverThai/Speech.lua').decode()]:assert 'build == "70938"' in text
with zipfile.ZipFile(ROOT/'work/customer4631/ForeverThai-0.463.1.zip') as customer:
 for name in protected+['ForeverThai/Speech.lua']:assert (ROOT/'src'/name).read_bytes()==customer.read(name)
report=dict(status='passed',version='0.466.0',artifact=artifact,sha256=sha(archive.read_bytes()),bytes=archive.stat().st_size,files=141,runtime_manifest=manifest,changed_from_through18=changed,added_files=added,removed_files=[],unchanged_through18_files=136,protected_assets_byte_identical_to4631=28,core_and_speech70938_byte_identical_to4631=True,combined_toc_settings70938_passed=True,toc_paths=24,savedvariables_and_optional_questie_preserved=True,root_wording_review='main ef2d6a22',new_thai_fields=16,reused_thai_fields=17,newly_supported_fields=33,unique_quest_ids=20,fonts='Append32missing runs/127glyphs in Thai93 only; font-readiness19.json',unchanged_skill_npc_party_suites_rerun=False,customer_feed_changed=False,windows_mac_m2_in_game_verified=False,actual_game_or_launcher_run=False,final_catalog_sha256=manifest['ForeverThai/Catalog.lua'])
(OUT/'package-manifest.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'evidence/private-package-manifest19.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='runtime_manifest'},indent=2))
