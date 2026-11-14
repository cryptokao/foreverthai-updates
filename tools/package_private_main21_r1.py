"""One approved MAIN21 delivery revision; read-only runtime, no matching/font/game suites."""
import pathlib,json,hashlib,zipfile,stat,subprocess,re
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];RUN=R/'src/ForeverThai';OUT=R/'work/private-main21-r1';OUT.mkdir(exist_ok=True)
SOURCE='814e4c7c289f46bc58b2ead3ef2a40e00a5cdb13';CAT='43ec92f88113114aef4918dcbe10c0bb89b7f222d6658dc5183c08c706f94f50';NAME='ForeverThai-0.466.0-cloud-main21-r1-PRIVATE-TEST.zip';BASE=R/'work/private19/ForeverThai-0.466.0-cloud-main19-PRIVATE-TEST.zip';sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes())=='9721987d00e96dcc595faf1c2cbcce4af82884d5c29f8118788a38eeb270bec5'
paths=sorted(p.relative_to(R/'src').as_posix() for p in RUN.rglob('*') if p.is_file());assert len(paths)==141
for n in paths:assert (R/'src'/n).read_bytes()==subprocess.check_output(['git','-C',str(R),'show',SOURCE+':src/'+n]),n
manifest={n:dict(bytes=(R/'src'/n).stat().st_size,sha256=sha((R/'src'/n).read_bytes())) for n in paths};assert manifest['ForeverThai/Catalog.lua']['sha256']==CAT
with zipfile.ZipFile(BASE) as b:
 assert set(b.namelist())==set(paths)
 changes=[n for n in paths if b.read(n)!=(R/'src'/n).read_bytes()];assert changes==['ForeverThai/Catalog.lua'];assert (RUN/'Catalog.lua').read_bytes().startswith(b.read('ForeverThai/Catalog.lua'))
 protected=[n for n in paths if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for n in protected+['ForeverThai/Speech.lua','ForeverThai/Match.lua','ForeverThai/Tracker.lua','ForeverThai/Atlas.lua']:assert b.read(n)==(R/'src'/n).read_bytes()
 toc=(RUN/'ForeverThai.toc').read_text();mods=[v.strip().replace('\\','/') for v in toc.splitlines() if v.strip() and not v.startswith('#')];assert len(mods)==24 and all('ForeverThai/'+m in paths for m in mods)
 assert '## Version: 0.466.0' in toc and '## OptionalDeps: Questie' in toc
 for setting in ['ForeverThaiDisplayMode','ForeverThaiObserved','ForeverThaiQuestieTracker','ForeverThaiAutoCaptureLog','ForeverThaiSpeech','AlphaWoWSkillsDB']:assert setting in toc
 for f in ['Skills/Core.lua','Speech.lua']:assert 'build == "70938"' in (RUN/f).read_text()
 # Data-only atlas reference inspection: no rendering/regeneration or old glyph suite.
 l=LuaRuntime(unpack_returned_tuples=True);a=l.table();a.skills=l.table();l.execute((RUN/'Atlas.lua').read_text(),'ForeverThai',a);l.execute((RUN/'Skills/BitmapData.lua').read_text(),'ForeverThai',a)
 refs=sorted({'ForeverThai/Fonts/Thai'+str(int(v[1]))+'.tga' for _,v in a.glyphs.items()}|{'ForeverThai/Fonts/SkillsThai'+str(int(v[1]))+'.tga' for _,v in a.skills.bitmapAtlas.glyphs.items()});assert all(n in paths for n in refs)
 fontfiles=[n for n in paths if '/Fonts/' in n]
 for n in fontfiles:assert b.read(n)==(R/'src'/n).read_bytes()
archive=OUT/NAME
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n in paths:
  info=zipfile.ZipInfo(n,date_time=(2026,11,14,0,0,0));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(R/'src'/n).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==141
 for i in z.infolist():
  n=i.filename;p=pathlib.PurePosixPath(n);assert not p.is_absolute() and '..' not in p.parts and '\\' not in n and not stat.S_ISLNK(i.external_attr>>16);assert z.read(n)==(R/'src'/n).read_bytes()
proof=json.loads((R/'evidence/main21-affected-regression.json').read_text());assert proof['catalog_sha256']==CAT and proof['positive_executions']==1 and proof['negative_executions']==3
report=dict(status='fresh_final_zip_static_integrity_passed',version='0.466.0',display_version='0.466.0 MAIN21 revision1 PRIVATE TEST',candidate_revision='main21-r1',source_commit=SOURCE,runtime_git_tree=subprocess.check_output(['git','-C',str(R),'rev-parse',SOURCE+':src/ForeverThai'],text=True).strip(),artifact=NAME,bytes=archive.stat().st_size,sha256=sha(archive.read_bytes()),files=141,final_catalog_sha256=CAT,runtime_manifest=manifest,changed_from_immutable_MAIN19=changes,unchanged_MAIN19_files=140,added_files=[],removed_files=[],toc_paths=mods,atlas_texture_references=refs,all_font_files_byte_identical_to_MAIN19=len(fontfiles),protected28_byte_identical_to_MAIN19=True,Core_Speech70938_Settings_Questie_SavedVariables_byte_preserved=True,source_code_metadata_changed=False,main21_exact_variants_included=1,new_thai_fields=0,new_prose=0,books22_included=False,matching_proof_reused=dict(path='evidence/main21-affected-regression.json',sha256=sha((R/'evidence/main21-affected-regression.json').read_bytes()),catalog_sha256=CAT,positive=1,negative=3,fresh_matching_rerun=False),fresh_verification='Actual final ZIP safe unique paths/CRC/141sourcebytes/TOC24/modules/atlas texture references, unchanged build gates/settings and protected28 vs verified immutable MAIN19. No runtime fixtures or fonts/old suites rerun.',windows_mac_m2_game_verified=False,customer_feed_changed=False)
(OUT/'package-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(R/'evidence/private-package-main21-r1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
receipt={k:v for k,v in report.items() if k not in ['runtime_manifest','toc_paths','atlas_texture_references']};receipt['toc_paths_verified']=24;receipt['delivery_readback_report']='evidence/candidate-main21-r1-delivery.json on source branch records actual post-upload download-back; no claim of readback before that step.';(OUT/'release-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
guide=f'''Alphaverse THAI SUB — 0.466.0 MAIN21 revision1 PRIVATE TEST

ไฟล์: {NAME}
ขนาด: {report['bytes']} bytes /141ไฟล์
SHA256: {report['sha256']}
Source commit: {SOURCE}
Runtime Catalog SHA256: {CAT}

เป็น private revision ของ0.466.0 ไม่ใช่เวอร์ชันใหม่ เก็บ MAIN19 ZIP เดิมไว้ไม่ทับ
รวม MAIN19 ทุกส่วนและ MAIN21 exact94233.progress variant ที่ Root อนุมัติ ใช้คำไทยเดิม ไม่เพิ่มคำแปล/เนื้อเรื่องใหม่ ไม่รวมหนังสือ books22 หรือบทสรุปแทนคำแปล
เทียบ MAIN19 เปลี่ยนเฉพาะ Catalog.lua อีก140ไฟล์ตรงทุกbyte รวม Quest/Tracker/Questie(optional)/NPC/Skill/Talent/Profession/Item/fonts/settings ครบ เก็บ protected28/SkillsCore/Speech70938/Atlas/ฟอนต์เดิมทั้งหมด ไม่มีสร้างฟอนต์ใหม่

ติดตั้งด้วยตนเองเมื่อพร้อมทดสอบ
1. ปิดเกม สำรองโฟลเดอร์ ForeverThai เดิม และเก็บ WTF/SavedVariables ไว้
2. เปิดตำแหน่ง client จริงผ่าน Battle.net (Windows Open in Explorer / Mac Show in Finder) เลือกโฟลเดอร์ที่มีไฟล์เกมจริง ไม่ยึดชื่อ product folder ตายตัว
3. ตรวจขนาด/SHA256 แล้วแตก ZIP ภายนอกเกม วาง ForeverThai ลง Interface/AddOns ให้เป็น Interface/AddOns/ForeverThai/ForeverThai.toc ไม่ซ้อนโฟลเดอร์ คงชื่อ ForeverThai/Fonts และไฟล์ทั้งหมด
4. เปิด AddOn ที่หน้าตัวละคร ไม่ล้าง settings/WTF ไม่ต้องรัน Python/สคริปต์พัฒนา/AI local และไม่ใช้โปรแกรม Windows บน Mac หากย้อนกลับให้ปิดเกมแล้วคืนโฟลเดอร์สำรอง

ขอบเขตหลักฐาน
- ใช้ผล MAIN21 เดิม 1positive/3negative ที่ Catalog hash เดียวกัน ไม่อ้างว่ารัน matcher ใหม่
- ตรวจใหม่เฉพาะ ZIP จริง: safe paths/CRC/141sourcebytes/TOC24/module/texture references และ hash การคง protected28/gates70938/settings/Questie เทียบ MAIN19
- รายงาน download-back จริงอยู่ evidence/candidate-main21-r1-delivery.json บน source branch หลังอัปโหลด เปรียบเทียบ ZIP และคู่มือ/manifest/receipt ทุกbyte
- ไม่มีการรัน old9Skills/NPC686/party/fullfont suite ไม่มีการติดตั้ง/ควบคุมเกมหรือทดสอบ Windows/MacM2 จริง
- Header capture ไม่ยืนยัน per-row build/current enabled inventory; ไม่อ้างทั้งเกมครบหรือใกล้100% ไม่ตัดสินว่าเนื้อหาทั่วไปของ94233เป็นเจตนาเซิร์ฟเวอร์หรือบั๊ก
- books22 จำนวน17หน้ายัง hold รอต้นฉบับจากผู้ใช้ ไม่มี payload ในแพ็กนี้ MAIN22 ไม่มี approved additions

customer feed คง0.463.1 ไม่เผยแพร่ผ่าน Launcher; นโยบายปกติ milestone0.470.0
เครดิตแหล่งเดิมคงใน SOURCES-TH.txt; MAIN21 source/proof: Forever-VO issue3481 และ Root review b7cb1abe ใน source repository ไม่มี raw captures/player context/tooling ลง runtime
ดู package-manifest.json /release-receipt.json และ PR https://github.com/cryptokao/foreverthai-updates/pull/1
'''
(OUT/'INSTALL-0.466.0-MAIN21-R1-PRIVATE-TH.txt').write_text(guide)
print(json.dumps({k:v for k,v in receipt.items() if k!='matching_proof_reused'},ensure_ascii=False,indent=2))
