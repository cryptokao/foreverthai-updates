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

## Batch08 — current exact NPC gossip/greetings after candidate07

CurrentEG1.60.1.70888 own-ID texts + independent NPC metadata atpin164bd1e2 provide10literal records:4new prose (Karn Stonehoof2998, Saru Steelfury3355, Gilliwigs260559, Commander Aggro'gosh2464),3exactskyborne variants with fixed literal targets,1Nimboya own-ID form reusing checked Thai,2new NPC bindings reusing existing full-body translations (Krix260558/Maurin4498). Only4new prose counted. No player/class/race slots inferred; Blacksmith stays literal. All ten English/Thai reviewed as a batch before Cloud font append17runs/66glyphs/Thai86; prior images and entries unchanged.

Focused actual npcPage/readGossipOptions/dialogTarget handler test:10unique source cases/40positive/150negative executions passed. Independent evidence full English/Thai, source-record/hash+NPC metadata, wrong ID/GUID/body/type/secret/locale/fallback gates, different player identities, all982861candidate07 values preserved,131unchanged component hashes and appended Catalog/Atlas prefixes. Decode newThai86 only; no unchanged Skills/NPC686/main/book suite rerun. Main regression tool now permits only the enumerated additional NPC entries; existing cloud-regression.json is explicitly scoped to07runtime tree, not relabeled08.

Candidate07 immutable ZIP remains the deliverable; batch08 is source-only and NOT in ZIP07 or05. New source queue covers only219book/gossip/greeting records in the pinned currentEGfile:168literal already supported,25explicit broadcast templates match both gender-rendered samples diagnostically,10literal records addressed by08,2explicitbroadcast templates ready for independent Thai review,11unproven normalized binding records (7Arathor book pages +4greetings),3blank. This is not a playable/full-game denominator. Next actionable sources:217412 broadcast255583 and2519 broadcast311861, exact current $c templates; do these before revisiting the11unproven slots. No feed/live-game claims.

## Batch09 — two explicit typed broadcast templates

Completed both remaining explicit source-template candidates:Amaryllis Webb217412 broadcast255583 (NPCobserved35;quest93176L35) andKin'weelay2519 broadcast311861 (NPCobserved39;quests596/629L37). Exact own-ID current70888 source records explicitly tag broadcastText and contain$c, soC/{class} is source-bound rather than inferred from normalized race/class words.2newprose/2templates; no old full-body matches forDruid/Mage/Warrior across oldNPCcatalog. Thai preserves general “subjects” without inventing a species. All two English/Thai reviewed before append4runs/31glyphs/Thai87; all08font pages/values kept.

ActualnpcPage +independent static six full English/Thai classcases:2unique templates/6rendered oracles/12positive/108negative executions passed,983466old08values and132othercomponent bytes preserved;Lua5.1/TOC24paths. First fixture attempt used “เมจ”; corrected fixture-only to preserved glossary“จอมเวท”, no runtime/Match/font changes to force pass. Evidence records this explicitly. No unchanged Skills/NPC686/main/book rerun. Batch08preservation harness and general main runner allow only enumerated09additions for future reruns; they were not rerun solely for that allowance update.

09is source-only, not in deliveredcandidate07. Next fresh book comparison of the preexisting112source-candidate list finds21full-body reuse (including20from07),51tokenholds,1single-letter fragment and39literal records needing source/semantic triage; several are Darnassian rather than English and3are image-only HTML. Keep historicalbuild/usage uncertainty separate and do not count generic titles/new title aliases as new prose. Do not call all39ready or allbookscomplete. No customerfeed/livegame change.

## Batch10 — fourteen public literal NPC records + two museum pages (wording review stage)

Continued current build70888 public Forever-VO issue captures3419–3424, exact source record/index/decoded+body hashes in public-literals-10.json.14NPCrecords:8new Thai texts,2own-ID forms reusing checked old Thai (Tognus1241/Mountaineer727),4new NPC bindings reusing existing full-body translations (Kingsguard274781three/Cadoc267279one). Museum2new pagefields: Pteradon Skeleton/Saurial Egg, observedpage1only; no total/itemID supplied, no complete-book claim. Full bodies compared across all existing book title/page aliases and NPCs before counting. Total10new Thai text bodies,6reuse forms; not16newprose. Fixed lad/boyo/profession/species retained, no player placeholders introduced.

Text-stage actual existing handler regressions passed:14uniqueNPCcases/56positive/210negative,2bookcases/2positive/10negative;983730oldruntime values/133othercomponent bytes preserved vs09 tree de598aad7331bed8831e391b6cef50fa1fd9e188. Catalog append only; Atlas/fonts unchanged.38Thai runs explicitly pending Root whole-batch wording review before Cloud append-font and next package. This is NOT bitmap-ready or a new ZIP. Root asked to review evidence/Thai/tests before packaging; candidate07 remains immutable and contains none of08/09/10. No unchanged Skills/NPC686/main/book07 runtime tests rerun. Earlier preservation harnesses/general runner now allow only enumerated10 additions for future reruns; Python syntax compiled, not a claim their runtime suites were rerun.

Current public supporting queue:494unique records across issues3419–3425;419exactliteral supported,71normalized-token records need independently qualified binding/current typed source (NOT71untranslated texts),3literal-player-name holds,1blank,0remaining literal actionable in this bounded source set. See public-supporting-remaining10.json; no player-specific body copied into remaining queue. Exact missing inputs: npc342greeting typed current-player-name source; Jordan's Weapon Notes pages1/5 own exact full body+typed recipient binding; normalized records need own-ID full current literal/typed source and independent fixed-vs-player binding. Main72held source variants remain separately scoped,58alreadyhavecanonical. No whole-game/live-game claim.

Next: Root review public-literals-10.json all16pairs, then append the38missing Thai runs on Cloud and run new-font/pack checks; produce a new candidate name/hash preserving07. Source search afterward should target qualified current own-ID evidence for listed normalized variants and historical-book current identity rather than repeat775Harvest or unchanged suites. The older VO literal book candidates are not automatically current-playable/newprose; many canonical current pages already exist and foreign-language/image-only/fragment records must be separated.

Batch10 wording review a4ebbf1 merged. Cloud appended exactly38missing Thai runs (including book titles),208glyphs,oneThai88page. font-readiness10.json:all134other pre-font runtime file bytes unchanged,Atlas oldprefix and all old images retained,28protectedSkill/font assets identical to462baseline,36actualBitmapLayer draws for08–10texts/titles/class oracles passed with no Thai live-font fallback. Prior text-stage font_pending report remains historical; this fresh affected-font report resolves it. No unchanged UI suites rerun.

Candidate10 complete runtime136files/17712731bytes SHA2562b4d3b8e506f4e85dfa38d652de3440a4fbfe9b215106799416efe2848d7ae0b, source362e748/runtime tree2ed51a804aec9956e82ffe33377dbbefb7f7757a. Permanent artifact8d91d47c561881090c1a4e38dd929f383af4bd2c ZIP+Thai guide+manifest downloaded back on Cloud; all136safe ZIP paths/every file byte/28protected assets/TOC24paths/SavedVariables/Questie/guide/manifest verified. Names/hash separate07; no party-speech runtime change in this immutable10candidate. Links in candidate10-delivery.json. Cloud output path remains OS-unwritable; permanent GitHub fallback retained. Feed/runtime version unchanged; no game verification.

Root candidate10 review f12e02d merged. font_readiness10 now pins actualpre-font tree d2562e61bec8ab0be3c5bd5e2f645d755eb55238 rather than movingHEAD. Initial edit put a same-line comment before prior= and caused NameError; corrected the script only, then the single completed affected check reproduced the original report exactly (38runs/208glyphs/Thai88/36draws/28protected). Runtime/ZIP10 unchanged; no unrelated suites rerun.

## Batch11 — speech-specific finite party/raid name support, review snapshot

Candidate10 remains delivered/immutable. Reused only8already-qualified Player-name templates from original Dev NPCSpeech-0.462.0.json, archive/hash/index/typed historical Player callers preserved in party-source-audit11.json. Historical C++ files themselves were not transferred/newly rehashed; no current server-code/live-proof claim. Fresh pinned70862/70888UnitDocumentation downloads verify12Unit API function contracts; existingChat API proof textarg1/speakerguidarg12 remains separate, arg5neverread as recipient. Durable API pins under tests/source_inputs/party-unit-api-pins.json.

Runtime delta onlySpeech.lua: finite exact NPC/SAY/signature/prefix/suffix whitelist; current party1–4/raid1–40 unit existence/player/GUID/membership/name/realm checks, duplicate-base/fullname ambiguity rejection, revalidation before use, no cache/wildcard/current-class/race inference. Only returns existing{name}Thai. Match.lua/Catalog/SpeechData/quest/gossip/Tracker/Skills/font/TOC/SavedVariables all byte-identical to candidate10. No new translations/version/feed.

Testing status at this requested review snapshot: PASSED against internal ZIP136files SHA d3b84137a952fca0a9ee3b1a1891d1723e50bb24a1a14cc35a7b8bb21753dbfb, not uploaded. Full original686independent Dev corpus on70862/70888:1372positive/8232base negatives +80wrong-player/2wrong-race and retainedsettings/timers/capture/realBitmapLayer assertions. With current roster active:additional1372positive/1372changed-body negatives. Eight static rendered oracles:116group-positive/626negative event executions +6timer controls/16sharedTranslate identity checks. Includes party/raid/nonparty/secret/arg5ignored/duplicate names+realm/non-player units/roster changes/fixedRingoTorta/unqualifiedN/settings/build/locale/missinggroup-onlyAPI gates.135other candidate10 file bytes unchanged, including all28protected assets. Exact fresh report party-speech-regression11.json; unique source cases remain686legacy/eightqualified templates, parameter executions are not new translations.

Debug history: first snapshot caught a roster-change case after unrelated template attempts; added literal-body prefilter before roster reads, kept revalidation/negative assertion. A deliberately removed UnitName fixture failed in unchanged core Match (UnitName is an existing required core dependency), so missing-API negatives cover the five group-only dependencies; secret group UnitName returns still fully tested. Static Thai oracles were checked against original immutable Dev wording and retain it exactly. Final debug+exactZIP rerun passed; unchanged Skills/main/book suites were not rerun. No ZIP11 uploaded yet; Root requested source/evidence review snapshot, runtime remains single-writer on Cloud, no live game proof.

Review snapshot13c5238 pushed as requested with fresh passingZIP results; no ZIP11uploaded. Source audit tool rerun after replacing ephemeral API pin input with committedpins reproduced identical proof JSON (no runtime/fullsuite rerun). General main regression preservation guard now permits Speech.lua only when its exactSHA equals passing party-speech-regression11 and that report assertsonlySpeechchanged; actual unchanged-file count is computed rather than stale124. Python syntax compiled; unchanged main suite not rerun solely to update this bounded authorized-delta guard. Original07main report remains scoped to its tested runtime.

Root party11 review cf66a1e merged, no runtime changes. Published exact already-tested ZIP SHA d3b84137a952fca0a9ee3b1a1891d1723e50bb24a1a14cc35a7b8bb21753dbfb (17714575bytes/136files) at immutable artifact0b73eafbedc1474820d34238a64fd75f0a97420d withnew manifest/Thai guide. candidate11-delivery.json records downloaded-back ZIP/hash/every current source byte/24TOC paths/28protected Skillfont assets/SavedVariables/Questie/guide/manifest verification. Relative10onlySpeech.lua changed,135files unchanged;10/07/05/feeds untouched. Includes8templates/5NPCs,0newprose. No686/party rerun from review or artifact upload. Runtime tree0a13f71e462c3c6c0a0c92f238ccc8984b8b2a5d; source d963e62 includesRootreview.

Post-artifact source-head check: EG164bd1e2,VOd562be62,Questiea444a641 unchanged. New publicVOissues3426(133lines),3427(74),3428(73), all70888enUS, downloaded/decoded separately for incremental own-ID review. Do not repeat unchanged775Harvest, fullinventory or tests. Main fields from these three new captures take low-level priority before supporting text; normalized/unbound identity slots remain holds unless direct typed evidence is available.

## Batch12 — new-source incremental review after delivered11

Source heads EG/VO/QuestieDB/additional forever-quests unchanged. Only newpublic issues3426–3428 (280input/278unique records, all70888enUS) parsed/compared against verified11runtime, with body/decoded hashes and entry indices. Main:99exact supported,27normalized diagnostic supported (not new typed proof),1blank,1new97048completionvariant held. Primary own-ID97048 websearch exposed known description/objective only; directopen403, no full completion/typed$N proof. Similar oldcanonical is preserved, not used to infer identity. Supporting:113exactNPC+22diagnostic,8exactbooks,1blank,4gossip+1booktyped variants held,1literal own-ID reuse candidate.

Completed the literal candidate:Deathguard Kristof251001 exactgeneric unavailable-service directions now reuse the already checked full-body Thai from12priorBrill guards; source70888own-ID/index/metadata preserved.0new Thai/prose,1new binding. No font/version changes. Actual NPC page4positive/15negative passed;985609old values and135other11component bytes preserved, including Speech/Match/Atlas/fonts/Skills. All reused Thai runs already exist. Only targeted one-case checks rerun when adding source-hash assertion; no unchanged686/party/Skills/main/Harvest suites. Generic preservation runner allows only enumerated12line, syntax compiled; no newmain test result claimed.12binding is source-only, NOT in immutable11ZIP.

New capture IDs:97ownquestIDs,0outsidepriorunion6114;59IDs receive their first70888phase observation relative to previous union evidence. source-id-current-capture-delta12.json stores exactissue/phase/index/hash. These are bounded observed records, not an authoritative active/playable quest list or denominator.

Current missing inputs:current-missing-inputs12.json gives exact73main field/source-variant holds (59existingcanonicals,14withoutcanonical; not73untranslated quests), five new supporting held records and links to older exactqueues. New support holds:5145trainer/visitorclass slots separately;259084fixed-vs-player race;5497class greeting;11956bear-context fixed-vs-class;Plain Letterpage1class/item identity/level14. Main97048completion$N needs fullown-ID typed proof. Existing source-ready current literal queue exhausted after this onebinding; no whole-game completion claim. Full current enabled-playable index with build/date/disabled/flavor/prerequisite/faction/race/class applicability still absent. Prior13859no-source rows are explicitly oldsnapshot counts, not regenerated/current inferred phases.

No collector added: existing /fth capture showslocalcounts, capturelog/id onlyAPI-accessiblefields (not unknownhistoricalcompletion), captureauto andspeechcapture toggles already exist. Missing panel source can be observed during ordinaryplay; share only relevant ForeverThaiObserved excerpts privately first for review/minimization/build/locale/ID/phase context, never auto-publish raw SavedVariables/playernames or infer typed slots from uploader identity. Game tests remainunverified/not failed; user said“not yet tested” on earlier05question, no immediate repeat prompt. Root already sentverified11+guide.

Targeted Druid corroboration completed before candidate12: exactly11956andPlainLetterpage1 only. Downloaded/hash+Gitblob verified two small pinned historical primary rawfiles (34KBMaNGOSupdate/18KBClassicUI MailTemplate), parsed literals without execution.11956maps3882→option3881→npc_text4721, literal“druid”,not$c. MailTemplate112fullbody/Mathrengyl/Darnassus/14thlevel matches normalized capture only when$c is diagnostically replaced by fixed“druid”; no dynamictoken, and no primary currentPlainLettertitle/page/item association. No Classicwords imported. Prior literalForever70790NPCfullbody already exists and matches; both existing literal-druid canonicals work with currentDruid ORMage,4positive/4changed-class-wordnegative probes on pinned11data. This is an existing-alias check, not70888livecoverage/roleproof. Current70888normalized$c holds remain; do not deriveclass from uploader or generalizefixedDruid. No runtime/font/newThai change or unchangedsuite rerun. Exactpins/hashes/association/limits in druid-role-check12.json. Root's PCdraft read-only assessment will be considered separately; no localdraft runtime merged.

Root PCdraft lead b5eed66 merged as documentation only. IndependentCloud verification: originalDev45642987bytes/hash0b161ac...,existingSpeechData signatures/Thai and independent686corpus indices, plus fresh raw C++pinned hashes/constants/referenceIDs/explicitPlayer* callscopes all match forMuglash12717q6641L23five andProfessor2768q665L40three. party-source-audit12.json adds only these8qualifications to previous8(total16/7NPCs),0newThai/prose. No PCdraftMatch/Speech imported, no claimdraftpassed. Runtime delta vs11now reviewedKristofCatalogbinding plus only8privatewhitelist entries/source-comment inSpeech; algorithmbody unchanged by exactsource comparison. SharedMatch/quest/gossip/Tracker/Atlas/Skills untouched.

Review snapshot stage: source-debug12passed with16staticfullEnglish/Thai oracles (old8unchanged+new8), retained686assertions/active-groupreplay and completeparty/secret/realm/non-player/settings/build/locale/bitmap negatives. UnqualifiedNcase set recomputed from16qualified,24remain/48eventrejections, so the newlyqualified8are not wrongly retained as negative. FreshactualcombinedZIP12 build/test pending at snapshot; no ZIP12uploaded. evidence/party-speech-debug12.json is explicitlysource-only, not a ZIP orlive result. Combiningwhitelist16+Kristof into one12candidate per user toavoidpiecemeal packages.

Fresh actual combined12ZIP passed fullregression:136files/17715324bytes SHA5a5c6d276ed150b15633ada2378a3dbc80a051f73e4a34fa89716ceb635d80f9.16unique qualified templates/7NPCs,16staticoracles (8new). Original686×2builds:1372positive/8232base negatives+80wrong-player/2wrong-race andretainedsettings/capture/timer/realbitmap assertions; active-group additional1372positive/1372negative. Party228positive/1138negative events+6timercontrols/32sharedidentitychecks. Unqualified24Nforms produce48negatives; newlyqualified8removedfromthatnegative set. Exact whitelist16asserted, algorithm11body unchanged. Relative11onlyCatalog(Kristofhashchecked)andSpeechwhitelist/sourcecomment changed;134otherfiles incl28protectedassets/Match/Atlas/TOC/SavedVars/QuestTracker remainidentical. No newThai/prose/fonts/version. Fresh reportparty-speech-regression12.json, preparedmanifest12 pinnedsource4dc29c4; this ZIP has NOT been uploaded while newwhitelist16awaitsRootreview peruser'scombinedcandidateinstruction. Main preservation guard now accepts only the exactfresh12SpeechSHA/report delta; syntaxchecked only, no unrelatedmain/Skill rerun.

Root whitelist16 review9a4b441/sourceavailability83c6ff8 merged. Exacttested combined12ZIP published immutable artifactbc5e309d14e380f02c1946e7ee1e26d0b199d21e withnewThai guide/manifest,136files/17715324bytes/SHA5a5c6d276ed150b15633ada2378a3dbc80a051f73e4a34fa89716ceb635d80f9. Runtime tree f15e81e113bc38214f7a22f4179d3380ce812ea9/source b0cb96e. Downloaded-back everybyte/current-source/safepath/24TOC/28protected/SavedVariables/Questie/guide/manifest verified. Initial delivery-script copy still named comparisonmanifest10 (the resulting two-file delta happened to be the same); corrected explicitly to11 and reran only asset-readback verification, nowreceipt names the exact11manifest/134unchangedfiles. No runtime/ZIP or686/party rerun from review or this verifier fix.10/11andfeeds unchanged.

Final currenthandoff:Root approvedall runtime changes; candidate12includesKristofreuse1and16partytemplates/7NPCs,0newThai/prose in12. New8qualifications independently verified fromDev456+freshprimaryhistoricalPlayer*callers;PCdraft runtime nevermerged orclaimedpassed. Main73heldsourcevariants remain(59canonical/14placeholder-or-repurposed),5freshsupportingholds incl2Druidnormalizedslots; rawhistoricalfixedDruid andexistingliteralcoverage are separated fromcurrentroleproof. Missingfull enabled/playableinventory/phase/typed evidence remains explicit, not a whole-game100%claim. User currentlyhasnoadditionalsource/maintainerlink; Windows/MacM2notyettested,notfailed. No repeatedask/search/poll/Harvest/unchangedsuite toholdworkopen. Existingcollector/privacy guidance retained;rawpersonalSavedVariablesarenotautomaticallypublic. README/current-missing-inputs12 updated with these exactlimitations andimmutablecandidate12receipt. No newruntime is pendingRootreview; futureworkrequires genuinelynewcorroboratedsource or actualgameacceptance evidence.

Bounded24role audit STOPPED at user priority correction before implementation. remaining-speech-role-checkpoint.json preserves verified originalDev metadata for24forms,22singleN/one repeatedN/one mixedC+N. Exact originalhashes for10NPCcpp+Player.cpp/ScriptMgr.cpp recovered from explicit480077ad revision, plus288KBScriptDev2 literal table (read-only).12exactSQLbody matches are provisional; no final per-form qualification/signatureaudit approved, no runtime/whitelist change or tests/ZIP13. Gadrin3188/q808L9still lacks raw DBquest-end/script/text/buddy/flags chain; proofkey/namedquotes are not approval. SQLite exactrelativepath/hash recorded only, no transfer/compression requested and no wait for118MB DB. Namedobservations/playernames omitted. Runtime remains candidate12; stop allNPC/party24research now. Next and only scope: main questaccept/objective/progress/completion from newpublic3429 against actualcandidate12; translate genuinely source-ready newtext before any font work or reportheld/source-ready0andstop. No NPC/book/toolcleanup substitute, versionbump or alias/test translation counts.

## MAIN ONLY — public issue3429, stopped with source-ready0

Aftercheckpoint4b046db, checked onlyquestfields innewissue3429(created2026-11-12T18:08:15Z),70888enUS, against actual immutablecandidate12Catalog/Match bytes.243exportlines contain88mainrecords:description13/progress39/completion36,zeroobjective records.71exact supported,16normalized diagnostic supported (not typedproof/newtranslations),oneheldq95772SongbladeSearchL31completion$r. Existingcanonical retained; the exact field/sourcehash was already held atcompact-main-queue record61, so no newheldfieldcount. Need exactcurrentown-IDfullbody and independentfixed-vs-playerrace evidence; do notderive$rfromuploader or infer from similar canonical/third-party description. main-quest-3429-audit.json preserves sourcepins/hash/index andboundedcounts.

Result:0source-ready mainfields,0newmainThai/prose/aliases,0runtime/font/version change. Stop here peruserpriority; noNPC/book/party24continuation,DBwait/compression,ZIP13,oldsourcepoll orunchanged686/party/Skillstests. Audit24checkpointis incomplete/unapproved and cannotextendwhitelist16. Candidate12/runtime tree unchanged; wholecurrentinventory/missingmainphase and actualWindows/MacM2evidence remainunproven. No repeated userquestion.


## Main13 — resumed new-source search, own-ID typed quest prose

- User explicitly resumed independent main-source discovery; no NPC/book/party work resumed. Merged latest main documents without resetting the branch.
- Own-ID Wowhead Forever pages with full slugs corroborate typed completion bodies for q6076 L10 and q5642/q5643 L20. Added three translated fields across three IDs, with two unique new prose/Thai bodies and one same-batch reuse (q5643). Preserved all old canonicals/aliases.
- q98574 L1 progress: primary full body corroborates only the addressed race slot; general `gnomes` remains literal. Added one typed variant reusing existing Thai wording, not new prose. Page build is not displayed; rendered web observations are not raw-body hashes or 70888/game acceptance claims.
- Scoped comparison also searched for the two new rendered bodies across the existing quest Catalog; no existing matching translation found. New-source details/pins and excluded fallback provenance are in main-new-source-discovery13.json; no raw concrete player names were published.
- Affected-only Lua5.1 checks: four unique source cases, six independent static rendered positives,20 negatives;97,814 old Catalog data values and the full prior Catalog byte prefix retained;135 other runtime files byte-identical to candidate12, including shared Match/Skills/fonts/settings. Initial harness incorrectly compared separately loaded function identities; moved data preservation comparison before loading unchanged Match and reran only this affected harness. Final report is main-primary-regression13.json.
- Root Thai review pending. No font rebuild/append, ZIP13, version bump, customer feed change or unchanged full/NPC686/Skills/party suite rerun.
