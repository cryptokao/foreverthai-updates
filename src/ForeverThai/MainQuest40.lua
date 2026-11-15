-- MAIN40: reviewed literal fields;match exact own-ID full UI source only.
-- No enabled-quest inventory,player condition or identity/quantity macro dispatch inferred.
local _, addon = ...
assert(addon.quests[93362].progress == nil, "MAIN40 field baseline changed")
addon.quests[93362].progress = { "11:1082766384:663732441", "เสร็จแล้วหรือ?" }
assert(addon.quests[93601].completion == nil, "MAIN40 field baseline changed")
addon.quests[93601].completion = { "324:95956270:1764847553", "ไนต์เอลฟ์ตัวโตอยากได้สร้อยหรือ? แต่ไนต์เอลฟ์ตัวโตเอาไปไม่ได้!\nพวก Thornweavers ต้องใช้สร้อย ผืนดินตายสนิท ไม่มีสร้อย หนามก็ไม่งอก! เซนทอร์ย่ำเข้ามาตรงที่หนามไม่งอก เห็นปัญหาหรือยัง หรือไนต์เอลฟ์ตัวโตตาบอด?\n\n<Kog'thug หยุดพูดพล่ามด้วยท่าทีดูแคลน แล้วพ่นลมหายใจทางจมูกอย่างครุ่นคิด>\n\nKog'thug คิดออกแล้ว อยากแลกกันไหม?" }
