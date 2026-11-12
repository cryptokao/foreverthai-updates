# สถานะชุดงาน Cloud

งานบน `codex/main-quest-cloud-continuation` ต่อจาก PR #1 และรวม main `41753e0` แล้ว เป้าหมายระยะยาวยังเป็น [GOAL.md](GOAL.md) ตารางนี้รายงานความคืบหน้า ไม่ใช่สถานะครบทั้งเกม

| Batch | งานจริง | หลักฐาน |
| --- | --- | --- |
| 01 | เพิ่ม objective ที่เดิมไม่มี 34 ฟิลด์ เลเวล 57–60; รักษาไว้และไม่นับซ้ำ | `evidence/main-objectives-01.json` |
| 02 | เพิ่มคำแปลตรงตัว skyborne 2 รูปแบบ ใน description 96987 L33 และ progress 92434 L34; ไม่ผูกคำนี้เป็น race ผู้เล่น | `evidence/main-phases-02.json` |
| 03 | เพิ่มรูปแบบจำนวน dynamic ให้ objective เดิม 5 ฟิลด์ L39–53; คงคำแปลและตัวเลขเดิมไว้ ไม่ใช่คำแปลเนื้อเรื่องใหม่ 5 ฟิลด์ | `evidence/main-counters-03.json` |
| 04 | เพิ่ม source variants จาก query 13 ฟิลด์ L40–60: เนื้อหาขยาย/สิ่งที่ต้องนำกลับเปลี่ยน 4 ฟิลด์ (7668, 8291, 8297, 8299); อีก 9 ฟิลด์เป็น aliases/typed slots/spelling/gender ของคำแปลเดิม | `evidence/main-query-04.json` |

แหล่งหลักชุดใหม่คือ `JIVESCORP/eg-link-output-wowf` commit `164bd1e2d89579ada4ee5e2de7e5fd4db684a9f1` ทั้ง query และ texts ของ wowf ไม่ใช้ normalized capture เพื่อเดาชนิด class/race ของบุคคลอื่น คง canonical/variants เดิมทุกค่าไว้ ใช้ Match.lua เดิม ไม่มีการ regenerate Catalog

## ผลตรวจรอบปัจจุบัน

`evidence/cloud-regression.json` แยก **56 unique source cases** (quest/field/template) ออกจาก **140 positive executions** และ **249 negative executions** มี unequal-counter oracles ที่เขียน source/expected เต็มแยกอิสระ 14 กรณี ครอบคลุม 90854/91564/92189, token เรียงกลับ 92465 และหลาย token อื่น การสลับ binding หรือช่องไทยทำให้ expected ผิดครบ 28 mutations ไม่สร้าง expected ด้วยการแทน token ชุดเดียวกับ source

ค่า 978,064 ค่าเดิมยังเท่าเดิม; ไฟล์ baseline 124 ไฟล์คง byte เดิม อีกสองไฟล์เป็น Catalog/Atlas ที่เพิ่มข้อมูลโดยรักษาข้อมูลเก่าไว้ Lua 5.1 และ TOC 24 paths ผ่าน ตรวจ font pages 95 หน้า ทั้งหมดนี้เป็น technical simulation

## Skill UI ที่กู้คืน

ดาวน์โหลด asset `ForeverThai-0.462.0-Legacy-Skill-Tests.zip` ขนาด 123544 bytes; SHA-256 `ca3559f718c688054a2f870117ad77007ad3fa3c6c8bcff0278eda38ed5706ab` ตรวจ path/symlink/manifest แล้ว เก็บ ZIP/extracted originals แยกใน `/workspace/foreverthai-dev` และสำเนาข้อความเดิม byte-identical ใน `tests/recovered_skill/`

`tools/legacy_skill_runner.py` ใช้ replay/assertions จาก reference เดิมครบและเลือกเพียง 9 named cases ไม่รันทั้ง modules เปลี่ยนเฉพาะ stage/ROOT และ wrapper ที่ต้องพึ่ง package helper/author archive/receipt ที่ไม่ได้ส่งมา เป็นการเทียบแพ็กกับ **src ปัจจุบัน** แทน ไม่เทียบ Catalog ใหม่กับ author ZIP เก่า

รันใหม่ผ่าน 9/9 รวม full TOC, slash commands, Questie/SavedVariables, Stoneform ที่ใช้ SkillsThai texture แม้ SetFont สำเร็จ, Devotion Aura rank 2 ที่คง 160 armor/30 yards/tooltip เดิม, Perception บน 70862/70888 และ gates build/locale/ข้อความเปลี่ยน การทดสอบเดี่ยวที่ตั้งใจใช้ font mode ยังคง explicit font mode; bitmap จริงตรวจแยกใน full TOC ไม่มีการแก้ runtime หรือสร้างฟอนต์เพื่อให้ชุดทดสอบนี้ผ่าน

หลักฐาน exact candidate/source/fixture SHA และชื่อทั้ง 9 กรณีอยู่ `evidence/legacy-skill-cloud.json` **ยังไม่ใช่ NPC686 และไม่ใช่ผลเล่นจริง Windows/Mac M2**

## แพ็ก private ที่ผ่าน Skill UI (batch04)

`ForeverThai-0.462.0-cloud-through-batch04-PRIVATE-TEST.zip` รวม 130 ไฟล์, 17232484 bytes

SHA-256 `785138246d531eae7d22286e26cb5ee301eb16b334c11fdfe7861caa59bf2796`

ประกอบและอ่านตรวจ ZIP จริงแล้ว รายไฟล์อยู่ `evidence/private-package-manifest04.json` แพ็กเก็บที่ `work/package04/` บน Cloud สร้างซ้ำได้ด้วย `tools/package.py` ไม่รวม development fixtures ใน payload ไม่มีการเพิ่ม version เปลี่ยน Launcher หรือ customer feed

## ช่องว่างและงานถัดไป

`evidence/quest-field-inventory.csv` บันทึก 6149 runtime IDs × 5 fields = 30745 แถว แยกข้อความที่ matcher รองรับ, source/token ที่ยังต้องตรวจ, placeholder และ current-usage-unconfirmed การที่ runtime ไม่มี field **ไม่ยืนยันว่า phase นั้นมีในเกม** ไม่ใช้ตัวหารนี้อ้างเปอร์เซ็นต์ทั้งเกม

`evidence/main-source-queue.json` เก็บรายการรายฟิลด์และ source hashes; `source-audit-through04.json` ระบุเหตุผล/สิ่งที่ต้องการเพิ่มเติม ให้เริ่มต่อจาก L1 92479/98574/98581/98601 ที่ capture อาจแทนคำอาชีพ/เผ่าคงที่ผิด ตรวจ own-ID primary ก่อนเพิ่ม typed aliases คิวจำนวน dynamic ที่ยังเหลือเป็นการขยายข้อความเดิม ไม่ใช่หลักฐานว่าคำแปลที่ recorded totals เดิมขาด

QuestieDB HEAD ใหม่ `d9caec6` เปลี่ยน metadata/gates และชื่อ 91907 แต่ยังไม่มี query record ปัจจุบันของรหัสนี้ จึงไม่อ้างว่าเป็นเควสต์ playable ใหม่ ส่วนต้นฉบับ primary ที่ www.wowhead.com ถูก Cloud proxy ปฏิเสธ CONNECT 403; ผู้ใช้ยืนยันให้คง network isolation/allowlist เดิม ใช้แหล่งที่เข้าถึงได้ต่อไป ไม่ย้ายออกจาก Cloud ที่ยังทำงานได้

ยังขาด typed phases บางรายการ (เช่น 6076/5642/5643 completion), current quest/phase inventory ที่พิสูจน์ playable ครบ, API archives ประกอบ NPC686 และผลเล่นจริง Windows/Mac M2 จึงยังไม่ผ่านเงื่อนไขจบ GOAL.md

## Batch 05 — Hyjal source amount forms

เพิ่ม dynamic source forms 16 ฟิลด์ใน 15 เควสต์ L55–57 (15 objectives + description93833) จาก query เดิมที่ pinned ไว้ คงข้อความและ fixed totals ที่แปลแล้วทุกค่า ไม่ใช่ 16 คำแปลเนื้อเรื่องใหม่ ไม่สร้างฟอนต์และไม่แก้ Skills เพิ่ม unequal-counter oracles อีก 4 กรณี พร้อมตรวจ fixed trainer literals ของ L1 ต่างคลาส 12 กรณี; ความเห็นบางส่วนจากหน้า98574ไม่ถูกใช้แทน raw body/hash และ progress ยัง hold binding ไว้

ผล main regression ล่าสุด: 72 unique source cases, 208 positive executions, 395 negative executions, 18 independent unequal-counter cases, 36 detected swaps ดู cloud-regression.json; ผล Skill UI candidate batch04 ยังคงเป็นผลของ SHA เดิม ไม่อ้างว่ารันใหม่เมื่อ Skills ไม่เปลี่ยน

## NPC replay ที่กู้คืน — ปิดงานก่อน union discovery

ต้นฉบับ `tests/recovered_npc/check_speech_v04230.py` คง bytes เดิม SHA256 `bdcf2ff10c973ab90cd372cfbd8f9416805f1fb0167be0d3e2d8a08193977b58` port fixture/event/settings/timer/capture/bitmap assertions แยกเป็น `tools/npc_replay.py` ไม่รัน original wrapper ที่ขาด helper/UI archives

`tools/build_npc_corpus.py` อ่านเฉพาะ entries ที่ review แล้วใน Dev/NPCSpeech-* จำนวน 18 เอกสารจาก Windows-Mac ZIP ที่ตรวจ hash เดิม ได้ 686 NPC/event/English/Thai forms ไม่ซ้ำ ไม่อ่าน expected จาก runtime SpeechData และไม่กรองตามผล runtime เพื่อให้ test ผ่าน corpus พร้อม file hashes อยู่ `tests/npc_corpus/reviewed-0462.json`

รันใหม่บน Cloud ผ่านสอง build 70862/70888: 1372 positive event executions, 8232 base negative event executions, wrong-player-name80, wrong-race2, fixed Ringo/Torta substitutions6 พร้อม assertions settings/dedup/timer/history/capture512/byte-limit/secret/real BitmapLayer ใน UI mock ตรวจ 102317 prior runs, 12403 glyphs และ 78 original TGA page bytes ที่คงเดิม แทน old-version wrapper อย่างมีขอบเขต ไม่มี runtime/font edits เพื่อให้ test ผ่าน

Exact candidate batch05: 130 ไฟล์, 17233223 bytes, SHA256 `3fd22cbac9c6eebddbf951da005267077414f074afee61b0aa127a0b09427b7d` รายงาน `evidence/npc-cloud-replay05.json` และ `private-package-manifest05.json` ผูก source/corpus/candidate hashes

ยังไม่มี Blizzard UI API archives จึงไม่อ้าง fresh event-argument documentation proof และยังไม่ใช่ผลเกม Windows/Mac M2 ชุด Skill UI 9 cases คงเป็นผล candidate batch04 ที่รายงานไว้ ไม่รีรันหรืออ้างว่าเป็นผลใหม่เมื่อ Skills ไม่เปลี่ยน Batch05 ได้ review สิ่งของ/NPC/จำนวนแล้วและไม่มีข้อแก้สำนวน; ยังนับเป็น 0 คำแปลเนื้อเรื่องใหม่

งานถัดไปเพิ่ม separate source-ID union audit จาก EG queries/texts, VO และ QuestieDB metadata เพื่อค้นรหัสนอก Catalog; ไม่ขยายตาราง runtime5fields และไม่ใช้ union เป็น playable-game denominator

## Source-ID discovery audit (separate from runtime inventory)

ตรวจ union จาก current EG query4846 IDs, all wowf texts1003, VO2076 และ QuestieDB Forever metadata5893 ที่ pinล่าสุด a444a64 ได้ union6114 IDs เทียบ runtime6149 พบ192 IDsนอกCatalog และ227 runtime IDsที่ไม่พบในunionนี้ ไม่ขยายตาราง5fields และไม่ใช้ตัวเลขใดเป็นwhole-game denominator

192 IDsนอกCatalogแยกเป็น test/development88, title/metadata-only9, disabled1, other-expansion/legacy uncertainty5 และ current-usage-unconfirmed89 (หลังแก้ classifier) ทุก IDนอกCatalogยังไม่มี own-ID current70862/70888 capture จาก EG texts หรือ VO (ต่างจาก query cache) จึงยังไม่ยืนยัน playable และไม่แปลเติมจาก Classic/SoD เพียงเพราะพบ prose

รายละเอียด source/commit/build/actual fields/title collisions/cross-flavor metadata อยู่ source-id-union.csv และ source-ids-outside-catalog.json; summaryบันทึกset differences/invariantsเพื่อไม่วนตรวจเดิมเมื่อsource pinsไม่เปลี่ยน ตรวจแหล่งเพิ่มเติม tyler3497/forever-quests ต่อเป็นprovenanceคนละชุด

## Classifier / API source proof / deliverable follow-up

แก้ substring test ให้ใช้เฉพาะ explicit source markers, exact developer labels และ known-ID/title pairs Testing the Wells / Contest / Greatest / A Test of Faith ไม่เป็น exclusion ผ่าน focused classifier tests 4 methods (รวม subcases) ทบทวน93outside holdsเดิมแล้ว5 IDsที่มีเพียงชื่อ Test Quest ย้ายกลับไป metadata/expansion uncertainty ไม่ได้ประกาศว่า playable อีก105แถว/21IDsในruntime inventoryพ้นสถานะtest จึงไม่ซ่อนช่องว่าง ดู source-classification-review.json ไม่มี runtime/NPC/Skill/font change หรือ rerunชุดเดิมจากงานauditนี้

ดาวน์โหลด raw ChatInfoDocumentation.lua จาก Gethe pins ของ70862/70888บนCloudเอง ตรวจอย่างละ132990bytes/SHA996cf3c4956d7d79716c082fa7bccf06e008fd191f108c85546f9fdec66e1a73 แล้ว รันเฉพาะ API-source assertions ผ่าน8event layouts: textarg1, guidarg12; playerName2arg5ไม่ใช่หลักฐานชื่อผู้รับในกลุ่ม รายงาน npc-api-proof.json แยกจาก NPC runtime invocation เดิม ไม่ต้องมีUIZIPใหญ่เพื่อพิสูจน์documentนี้ และไม่ใช่ผลเกม

Snapshotเพิ่มเติม tyler3497/forever-quests pin9f4c5a: main4630 IDs และForeverDB3862 IDs ไม่มีIDนอกCatalog/unionเดิม ทั้งสองprovenanceแยกกัน เก็บGPL3credit/MITหรือprovidercreditตามinput โดยเฉพาะ Data from ForeverDB.net (https://foreverdb.net) ไม่ใช้API meta6614เป็นcoverage ตัวเลือกobjectiveที่ดูเหมือนขาดสองรายการ5641/5679พบcurrentqueryเปลี่ยนเป็นChastise/Dark Sacrificeและไม่มีobjectiveปัจจุบัน จึงไม่คัดtravel textClassicเก่า; อีก4เป็นnull placeholders ไม่มีคำแปลเพิ่มจากauditนี้

ไฟล์ ZIP และคู่มือไทยของ candidate05 เก็บถาวรที่ artifact commit79009735547c6f0ca2ef998cecb9ed85eb52c108 บน branch codex/private-candidate05-artifacts แล้ว พร้อมmanifest ดาวน์โหลดกลับจากGitHubrawและตรวจSHAตรง3fd22c...27b7d ไฟล์ไม่ได้มีเพียงworkชั่วคราว อย่างไรก็ตาม path Cloud outputs /codex/browser/projectless/0001-alphaverse-thai-sub-codex-cloud-environment-fore/output ถูกLinuxปฏิเสธPermission denied (ทั้งexec/patch) จึงใช้GitHub artifactเป็นทางสำรอง ไม่อ้างว่าแนบในCloudoutputsสำเร็จ

Inventoryสั้น: 30745 runtime-field rows; มีอย่างน้อยหนึ่งfull sourceที่matcherรองรับ16826; ไม่มีsource record13859; รอtyped identity evidence51; usageยังไม่ยืนยัน7465 ตัวเลขเหล่านี้เป็นคนละมิติและทับซ้อนกัน ไม่ใช่เปอร์เซ็นต์หรือรายการplayableทั้งเกม

LibQuestDBofficialdownloadเคยติดCONNECT403 ผู้ใช้ส่งresearchsupplementใหม่เพื่ออ่านHarvestเท่านั้น เป็นงานถัดไปหลังcommitนี้ ไม่รันlibrary/scriptsและไม่เปลี่ยนnetworkpolicy/customerfeed

## LibQuestDB source supplement — completed restricted audit

ตรวจ research ZIP34441bytes SHA d28107f58f0e6facdd65de59b5e46217a096002695cc829a52e3a2dd05038a16, paths/symlinks และmanifest4ไฟล์ตรงทุกbyte เก็บoriginalแยกในforeverthai-devและสำเนาMIT sourceภายใต้tests/source_inputs/libquestdb-010 ไม่มีการติดตั้ง/รันlibrary/puller

Restricted parserรับเฉพาะnumericID/string literals และschemaคอลัมน์ที่อ่านจากformatที่กำหนด ปฏิเสธcalls/expressions/duplicateIDs/unsupportedescapes มีfocusedtests3methods รวมdecimal\031 และUTF8byteescapes ต่างจากPythonoctal ไม่ใช้LuaVMกับไฟล์บุคคลอื่น

ได้775IDs/775titles,723log summaries,186objective lines รวม1684field records:1672รองรับแล้ว,9รอsnapshot/currentbinding,1placeholderLog และ2ฟิลด์จาก94898ที่มีexplicitTempDisabled ไม่มีIDนอกunionเดิม และไม่มีcandidateพร้อมแปลจากหลักฐานชุดนี้ รายงานharvest-source-audit.json/differencesเรียงlow→high พร้อมsource hashes ไม่มีaccept/progress/completionจากClassicdumpปน ไม่มีคำแปลเพิ่ม

วันที่harvest09-28และInterface16001ไม่ใช่exactclientbuild; original9.6MBZIPมีhashในprovenanceที่ผู้ใช้ยืนยัน ส่วนCloudตรวจใหม่เฉพาะresearchsupplementและ4originalfilesที่อยู่ในmanifest ไม่อ้างว่าClouddownload/rehashedoriginalZIPแล้ว

คู่มือartifactแก้ตามreviewแล้วที่commit c50ce853f1090ab9c20340b19c5fca2fc1011ef6:ใช้client folderจริงที่Battle.netเปิด ไม่มีชื่อproduct folderตายตัว ZIPblobเดิม/SHAเดิมไม่เปลี่ยน ดูcandidate05-delivery.jsonสำหรับlinksล่าสุด

## Batch06 — all actionable current-query amount forms

หลังcommitHarvestaudit4146283และอัปเดตPRแล้ว แยกcompact queueที่มีsourceจริง106main fields เป็น34actionable current-query $ioaและ72blocked (typed51/rendering2/old-normalized4/non-enUS1/placeholders12/repurposed historical IDs2) ไม่รวม13kno-source rows ดูcompact-main-queue-before06.jsonซึ่งเก็บown-ID/level/field/build/source-kind/reason/next-action

ทำ34actionable objectives L57→60แล้ว คงwording/fixed totals/aliasesเดิม ไม่ใช่34new proseและไม่เพิ่มcanonical fields ไม่มีfont/Skills/Speech/Bitmap changes เพิ่มstatic unequal-count oraclesทุกmulti-tokenในชุด รวม3-token92011และsource-order2→1ของ96992 ตรวจสลับทุกคู่ทั้งsignatureและThai slots ผลmain regression106unique source cases/362positive/710negative executions,36independent unequal cases/80mutations ค่าเก่า978064ค่ายังคงเดิม

compact-main-queue.jsonปัจจุบันเหลือ0actionable/72blocked ไม่มีnew prose readyจากsourceที่มี จึงไม่อ้างว่าmainทั้งเกมครบและไม่วนblockedslotsเดิม ต้องได้exactown-ID typed/full-current-body/formatter proofตามnext_actionรายแถวก่อนเติม ส่วนสังเกตwebที่rootส่งเกี่ยวกับHarvesttypos/Optionalจะตรวจหลังcommitนี้ เฉพาะhistorical aliasesที่มีหลักฐาน ไม่สร้างsourceหรือstripOptionalทั่วเกม

ผลNPC686/API/SkillUIที่reviewแล้วคงเป็นผลcandidateเดิมตามSHA ไม่rerunชุดเดิมจากการเปลี่ยนquantityCatalogนี้ Candidate05ที่ส่งให้ผู้ใช้คงZIP/SHAเดิม ไม่มีผลliveWindows/MacM2กลับมา

## Batch07 — observed books and exact historical labels

ตรวจ20fullEnglishbodiesกับ857numeric book-page bindingsใน289title bindingsรวมvariants/title aliasesของcandidate05ที่มีSHAผูกไว้แล้ว ไม่มีbodyใดmatch จึงไม่ใช่แค่เห็นtitleใหม่แล้วนับเพิ่ม ดูbook-reuse-audit07.jsonและtools/audit_book_reuse.py

เพิ่ม20page fieldsจากEGwowf70888 pin164bd1e2:Belamoore's Research Journal(item3711)19observed pages และField Guide(item213563)page3 ทุกentryผูกitem/title/page/fullEnglish/Thai/source record/hash/meta คงชื่อคน/เผ่าในเรื่องตรงตัว ไม่มีplayerplaceholder ไม่มีหลักฐานtotalpagecount จึงไม่อ้างcompletewholebook

ตรวจความหมาย/ลำดับ/ชื่อ/จำนวน/การแบ่งpageในThaiครบbatchก่อนappendfont บนCloudเพิ่ม162runs/512glyphsในThai83–85เท่านั้น คงpriorfontpages/glyphs/runsเดิม Candidate05componentsที่ไม่ใช่Catalog/Atlas128ไฟล์คงSHAเดิม

Labeltyposทั้งสามcurrentcorrectedEnglishรองรับThaiเดิมแล้ว เพิ่มเฉพาะexactolderHarvestformsในown-IDsteps97223/93963/92679เป็น3historical aliases สองtypoใช้Thaiเดิม Optionalaliasคงความหมายด้วย(ไม่บังคับ) แต่ไม่stripOptionalทั่วเกม ไม่อ้างcurrentOptionalflag/coverageหรือnewproseจากaliases

Book regressionใช้readBookfunctionจริงจากEvents.luaในmock UI ผ่าน20exacttitle/page/fullbody positives +87wrongtitle/page/body/type/secret/mode negatives;historicalaliases6positives/4negatives ทั้งหมดมีbakedruns Mainregression106source cases/362positive/710negative/36independentcountercases/80swapmutationsยังผ่าน ค่าเก่า978064ค่ายังคงเดิม Fontpages98decodeได้ครบ ไม่rerununchangedSkill/NPCsuiteจากbook-onlychange ผลเก่าแต่ละชุดยังผูกcandidateSHAเดิม

compactmainqueueยัง0actionable/72heldsource records;72ไม่ใช่72เควสต์ที่ไม่แปลทั้งฟิลด์ หลายcanonicalรองรับอยู่แล้ว ดูruntime_canonical_present/ already_supported_source_versions รายrecord

ZIP05ที่ส่งผู้ใช้ยังไม่มี34forms06และหนังสือ07 จะสร้างcandidate07ชื่อ/hashใหม่เมื่อพร้อม โดยคงZIP05เดิมไว้ ไม่เปลี่ยนcustomerfeed และยังไม่มีผลเกมWindows/MacM2กลับมา

Candidate07 assembled and downloaded back on Cloud:133files/17533451bytes SHA256 ee59386cb62cafb3acfd85a8af4fec33ddc66b4a65fbdd5cfe5613a3cee9d781. Every ZIP byte matches source runtime tree1547af8d6d56fdd9a0f5234466b70799825dac7e at76b09b4 (includes Root review3c229f0, no runtime change). Immutable artifact commit4052d15c16e051dacf561df481ee9dc0e5c9407f contains ZIP/Thai guide/manifest; links in candidate07-delivery.json. Candidate05 is unchanged. Designated Cloud output path remains OS-unwritable, so permanent GitHub artifacts are the documented fallback, not a claim of an attached output. All required components retained; prior Skill04/NPC05 results remain scoped to their exact candidates, not rerun or relabeled07. No live Windows/MacM2 result and no feed change.

Next: examine actual remaining book/gossip/greeting/NPC/escort source records and full-body reuse across aliases. Do not re-audit unchanged775Harvest or reinterpret72held source variants as72untranslated quests. Main compact queue remains0actionable/72blocked (58 have an existing canonical field), with typed/current-body missing inputs per row.
