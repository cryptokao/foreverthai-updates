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
