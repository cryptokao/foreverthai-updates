import pathlib,zipfile,hashlib,json,sys,time
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;sys.stdout.reconfigure(encoding='utf8');t=time.perf_counter();cpu=time.process_time();base=R.parent/'package-main44/build-0.480.0-compact/ForeverThai-0.480.0-main44-COMBINED.zip';sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(base.read_bytes())=='7bdbf55bf8f38974a8a55cc80cc0e83dbed1df951b69bf21f1d8f3291ca48208';z=zipfile.ZipFile(base);core=z.read('ForeverThai/Skills/Core.lua').decode();toc=z.read('ForeverThai/ForeverThai.toc').decode()
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();l.execute(core,'ForeverThai',a);l.execute('function GetBuildInfo() return "1.60.1","70959","",16001 end;function GetLocale() return "enUS" end');assert a.skills.Compatible()==False
old='''    return version == "1.60.1" and (build == "70862" or build == "70888" or build == "70938") and interface == 16001
        and type(GetLocale) == "function" and GetLocale() == "enUS"'''
new='''    -- Forever patch builds keep this client family and interface. Reviewed
    -- names and complete tooltip lines are still checked by Lookup/Render, so
    -- changed or unknown spell/item wording keeps the original tooltip.
    -- Do not switch every translation off when only the patch build changes.
    return version == "1.60.1" and interface == 16001
        and type(build) == "string" and build:match("^%d+$") ~= nil
        and type(GetLocale) == "function" and GetLocale() == "enUS"'''
assert core.count(old)==1;core=core.replace(old,new).replace('version = "0.285.0"','version = "0.480.1"');assert core.count('version = "0.480.1"')==1;toc=toc.replace('## Version: 0.480.0','## Version: 0.480.1');assert '## Version: 0.480.1' in toc
src=z.read('ForeverThai/SOURCES-TH.txt')+b'\nHOTFIX04801: userreported all Skills/Items/Talents missing on actual installed client1.60.1.70959. Files present;Core.Compatible allowedonly70862/70888/70938,so all lookups disabled. Replace exact patch allowlist with same1.60.1/interface16001/enUS clientfamily and numericbuild gate. Full original-name/fulltooltip-wording/quantity/secretvalue/combat safeguards preserved;unknownchangedrecords stay original. Datasetunchanged2026.11.09.1. No newtranslation/fontshaping. Immediate customerhotfix explicitlyrequested;normal milestone0.490.0unchanged. Questtranslation goalPAUSED;MAIN45reviewed15fields NOTincluded. Actualgameacceptance still unverified.\n'
changed={'ForeverThai/Skills/Core.lua':core.encode(),'ForeverThai/ForeverThai.toc':toc.encode(),'ForeverThai/SOURCES-TH.txt':src};out=R/'ForeverThai-0.480.1-SKILLS-HOTFIX-COMBINED.zip';assert not out.exists();manifest={};preserved=[]
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as zz:
 for n in z.namelist():
  b=changed.get(n,z.read(n));zz.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b));
  if n not in changed:preserved.append(n)
with zipfile.ZipFile(out) as zz:
 assert len(zz.namelist())==183 and len(preserved)==180
 assert sum(i.file_size for i in zz.infolist())<=512*1024*1024
 for n,v in manifest.items():assert sha(zz.read(n))==v['sha256']
 fonts=[n for n in z.namelist() if '/Fonts/' in n];skill=[n for n in z.namelist() if '/Skills/' in n];assert len(fonts)==125 and len(skill)==14
 assert all(zz.read(n)==z.read(n) for n in fonts)
 assert all(zz.read(n)==z.read(n) for n in skill if not n.endswith('/Core.lua'))
 sv=lambda s:next(x for x in s.splitlines() if x.startswith('## SavedVariables:'));assert sv(toc)==sv(z.read('ForeverThai/ForeverThai.toc').decode())
 for n in changed:
  p=R/'runtime-delta'/pathlib.PurePosixPath(n).relative_to('ForeverThai');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(zz.read(n))
 # Physical test fixture only: no game directory or executable is used.
 testsrc=R/'src';testsrc.mkdir(exist_ok=True);zz.extractall(testsrc)
receipt=dict(status='BUILT_NOT_PUBLISHED_NEEDS_SKILL_UI_TESTS',version='0.480.1',zip=dict(path=out.name,bytes=out.stat().st_size,sha256=sha(out.read_bytes())),expanded_bytes=sum(v['bytes'] for v in manifest.values()),runtime_files=183,unchanged_runtime_files=180,all125_fonts_exact=True,all13_other_skill_modules_exact=True,skill_modules=14,changed=list(changed),old70959_gate_reproduced_false=True,dataset_unchanged=True,quest_translations_changed=0,MAIN45_15_reviewed_not_included=True,goal_paused=True,actual_client_version_readonly='1.60.1.70959',real_game_acceptance=False,no_game_install_or_control=True,no_local_AI_or_font_rebuild=True,wall=time.perf_counter()-t,cpu=time.process_time()-cpu)
for n,v in [('package-receipt.json',receipt),('manifest.json',manifest)]:(R/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt,indent=2))
