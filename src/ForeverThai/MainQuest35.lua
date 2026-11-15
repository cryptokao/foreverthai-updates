-- MAIN35: four exact own-ID literal objective fields;retain all old quest data.
local _, addon = ...
assert(type(addon.quests[96075]) == "table" and addon.quests[96075].objective == nil, "MAIN35 baseline changed")
addon.quests[96075].objective = { "253:216259650:1576876786", "รวบรวม Nefarian's Remit จาก General Drakkisath ใน Blackrock Spire, Overseer's License จาก Overlord Wyrmthalak ใน Blackrock Spire และ Bronzebeard Wedding Contract จาก Emperor Thaurissan ใน Blackrock Depths แล้วนำทั้งหมดไปให้ Pix Xizzix ที่ Booty Bay" }
assert(type(addon.quests[96087]) == "table" and addon.quests[96087].objective == nil, "MAIN35 baseline changed")
addon.quests[96087].objective = { "210:1547182205:1253971353", "รวบรวม Headmaster's Records จาก Darkmaster Gandling, Grain Shipment Orders จาก Baron Rivendare และ Dathrohan's Correspondence จาก Grand Crusader Saidan Dathrohan แล้วนำทั้งหมดไปให้ Pix Xizzix ที่ Booty Bay" }
assert(type(addon.quests[96088]) == "table" and addon.quests[96088].objective == nil, "MAIN35 baseline changed")
addon.quests[96088].objective = { "224:276163498:1251445746", "รวบรวม Ysera's Tear จาก Shade of Eranikus ใน Sunken Temple, Mark of Xavius จาก Varrox Bleakhoof ใน Blackmaw Hold และ Freya's Sigil จาก Nanaya ใน Shaper's Terrace แล้วนำทั้งหมดไปให้ Pix Xizzix ที่ Booty Bay" }
assert(type(addon.quests[99217]) == "table" and addon.quests[99217].objective == nil, "MAIN35 baseline changed")
addon.quests[99217].objective = { "59:1451828752:1995723374", "ตรวจดูโคโดหุ้มเกราะเพื่อเลือกพาหนะระดับมหากาพย์ของเจ้า" }
