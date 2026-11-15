-- MAIN38: reviewed literal fields;match exact own-ID full UI source only.
-- No enabled-quest inventory,player condition or identity/quantity macro dispatch inferred.
local _, addon = ...
assert(addon.quests[80325] == nil, "MAIN38 quest baseline changed")
addon.quests[80325] = {}
assert(addon.quests[80325].title == nil, "MAIN38 field baseline changed")
addon.quests[80325].title = { "12:990632469:2056706464", "ราชาผู้บ้าคลั่ง" }
assert(addon.quests[80325].description == nil, "MAIN38 field baseline changed")
addon.quests[80325].description = { "243:1703652264:1928633836", "เจ้าพบสมุดบันทึกที่สกปรกและขาดรุ่งริ่ง ภายในเต็มไปด้วยแบบร่างและบันทึกที่ขีดเขียนไว้ เพียงเหลือบมองก็เห็นได้ชัดว่า หากมีใครโง่พอจะสร้างขึ้นมา สิ่งประดิษฐ์เหล่านี้แต่ละชิ้นล้วนใช้ก่อหายนะร้ายแรงได้" }
assert(addon.quests[80325].objective == nil, "MAIN38 field baseline changed")
addon.quests[80325].objective = { "82:1621377549:130502004", "นำ Thermaplugg's Engineering Notes ไปให้ Nogg ที่ Valley of Honor ใน Orgrimmar" }
assert(addon.quests[81768] == nil, "MAIN38 quest baseline changed")
addon.quests[81768] = {}
assert(addon.quests[81768].title == nil, "MAIN38 field baseline changed")
addon.quests[81768].title = { "34:506849163:1901586744", "ภารกิจ Ashenvale I: ปราบซาเทียร์" }
assert(addon.quests[81768].description == nil, "MAIN38 field baseline changed")
addon.quests[81768].description = { "244:681064262:78960982", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Bough Shadow แล้วไปยัง Nightmare Incursion ใน Satyrnaar ปราบพวกซาเทียร์ที่นั่น แล้วกลับมาหาข้า" }
assert(addon.quests[81768].objective == nil, "MAIN38 field baseline changed")
addon.quests[81768].objective = { "146:570116538:1779812511", "ปราบ Dreamfire Betrayers 10 ตัวและ Dreamfire Hellcallers 10 ตัวใน Ashenvale Nightmare Incursion ที่ Satyrnaar แล้วกลับไปหา Field Captain Hannalah" }
assert(addon.quests[81770] == nil, "MAIN38 quest baseline changed")
addon.quests[81770] = {}
assert(addon.quests[81770].title == nil, "MAIN38 field baseline changed")
addon.quests[81770].title = { "39:1811098856:1974240176", "ภารกิจ Ashenvale III: ปราบเผ่ามังกร" }
assert(addon.quests[81770].description == nil, "MAIN38 field baseline changed")
addon.quests[81770].description = { "249:161708564:1183842656", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Bough Shadow แล้วไปยัง Nightmare Incursion ใน Forest Song ปราบเผ่ามังกรที่นั่น แล้วกลับมาหาข้า" }
assert(addon.quests[81770].objective == nil, "MAIN38 field baseline changed")
addon.quests[81770].objective = { "141:222897067:406474633", "ปราบ Wyrmkin Nightstalkers 3 ตัวและ Terror Whelps 10 ตัวใน Ashenvale Nightmare Incursion ที่ Forest Song แล้วกลับไปหา Field Captain Hannalah" }
assert(addon.quests[81772] == nil, "MAIN38 quest baseline changed")
addon.quests[81772] = {}
assert(addon.quests[81772].title == nil, "MAIN38 field baseline changed")
addon.quests[81772].title = { "39:355137704:101831354", "ภารกิจ Ashenvale V: ข่าวกรองซาเทียร์" }
assert(addon.quests[81772].description == nil, "MAIN38 field baseline changed")
addon.quests[81772].description = { "288:1949210410:780319850", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Bough Shadow แล้วไปยัง Nightmare Incursion ที่ Satyrnaar รับรายงานข่าวกรองจาก Dreamwarden Mandoran ที่นั่น แล้วกลับมาหาข้า" }
assert(addon.quests[81772].objective == nil, "MAIN38 field baseline changed")
addon.quests[81772].objective = { "154:751669813:615390520", "รับข่าวกรองจาก Dreamwarden Mandoran ใน Ashenvale Nightmare Incursion ที่วงประกอบพิธีใน Satyrnaar แล้วกลับไปหา Field Captain Hannalah" }
assert(addon.quests[81773] == nil, "MAIN38 quest baseline changed")
addon.quests[81773] = {}
assert(addon.quests[81773].title == nil, "MAIN38 field baseline changed")
addon.quests[81773].title = { "41:561054678:529817589", "ภารกิจ Ashenvale VI: ข่าวกรองทรีแอนต์" }
assert(addon.quests[81773].description == nil, "MAIN38 field baseline changed")
addon.quests[81773].description = { "301:300013518:2056888537", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Bough Shadow แล้วไปยัง Nightmare Incursion ที่ Warsong Lumber Camp รับรายงานข่าวกรองจาก Dreamwarden Lanaria ที่นั่น แล้วกลับมาหาข้า" }
assert(addon.quests[81773].objective == nil, "MAIN38 field baseline changed")
addon.quests[81773].objective = { "168:1703626412:207136548", "รับข่าวกรองจาก Dreamwarden Lanaria ใน Ashenvale Nightmare Incursion ภายใน Kargathia Keep ที่ Warsong Lumber Camp แล้วกลับไปหา Field Captain Hannalah" }
assert(addon.quests[81776] == nil, "MAIN38 quest baseline changed")
addon.quests[81776] = {}
assert(addon.quests[81776].title == nil, "MAIN38 field baseline changed")
addon.quests[81776].title = { "53:1259008904:2006352168", "ภารกิจ Ashenvale IX: นำ Dream-Touched Dragonegg กลับคืน" }
assert(addon.quests[81776].description == nil, "MAIN38 field baseline changed")
addon.quests[81776].description = { "265:1825486484:798885166", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Bough Shadow แล้วไปยัง Nightmare Incursion ใน Forest Song นำ Dream-Touched Dragonegg มาส่งให้ข้า" }
assert(addon.quests[81776].objective == nil, "MAIN38 field baseline changed")
addon.quests[81776].objective = { "145:1088134175:1770001142", "นำ Dream-Touched Dragonegg จากซากอาคารตรงกลาง Forest Song ใน Ashenvale Nightmare Incursion กลับไปหา Field Captain Hannalah" }
assert(addon.quests[81782] == nil, "MAIN38 quest baseline changed")
addon.quests[81782] = {}
assert(addon.quests[81782].title == nil, "MAIN38 field baseline changed")
addon.quests[81782].title = { "42:1861511820:470817121", "ภารกิจ Ashenvale XV: ปราบ Shredder 9000" }
assert(addon.quests[81782].description == nil, "MAIN38 field baseline changed")
addon.quests[81782].description = { "265:866314907:568904549", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Bough Shadow แล้วไปยัง Nightmare Incursion ที่ Warsong Lumber Camp ปราบ Shredder 9000 ที่นั่น แล้วกลับมาหาข้า" }
assert(addon.quests[81782].objective == nil, "MAIN38 field baseline changed")
addon.quests[81782].objective = { "141:1135470581:794597800", "ปราบ Shredder 9000 ใน Ashenvale Nightmare Incursion ใกล้เครนยกไม้ใน Warsong Lumber Camp แล้วกลับไปหา Field Captain Hannalah" }
assert(addon.quests[81783] == nil, "MAIN38 quest baseline changed")
addon.quests[81783] = {}
assert(addon.quests[81783].title == nil, "MAIN38 field baseline changed")
addon.quests[81783].title = { "49:686808803:1261389235", "ภารกิจ Ashenvale XVI: ช่วยเหลือ Alyssian Windcaller" }
assert(addon.quests[81783].description == nil, "MAIN38 field baseline changed")
addon.quests[81783].description = { "327:2058171485:1151740822", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Bough Shadow แล้วไปยัง Nightmare Incursion ที่ Warsong Lumber Camp หา Alyssian Windcaller ดรูอิดแห่งกรงเล็บที่หลับใหลอยู่ที่นั่น และคุ้มกันนางไปยังที่ปลอดภัย จากนั้นกลับมาหาข้า" }
assert(addon.quests[81783].objective == nil, "MAIN38 field baseline changed")
addon.quests[81783].objective = { "161:292220109:815727655", "ช่วยเหลือ Alyssian Windcaller จาก Ashenvale Nightmare Incursion ที่ฐานหอคอยเฝ้าระวังใน Warsong Lumber Camp แล้วกลับไปหา Field Captain Hannalah" }
assert(addon.quests[80454] == nil, "MAIN38 quest baseline changed")
addon.quests[80454] = {}
assert(addon.quests[80454].title == nil, "MAIN38 field baseline changed")
addon.quests[80454].title = { "13:1405642217:677200324", "ส่งของเป็นครั้งสุดท้าย" }
assert(addon.quests[80454].description == nil, "MAIN38 field baseline changed")
addon.quests[80454].description = { "315:2001080663:1171622700", "เหยื่อพร้อมแล้ว ทีนี้เราต้องวางกับดัก ข้าปรับแต่งเครื่องรางตามคำสั่งของ Fahrad แล้ว เหลือเพียงให้เจ้านำมันไปส่งเช่นเดียวกับวัตถุชิ้นอื่นที่เคยส่งก่อนหน้านี้\n\nไปยังกระท่อมใกล้ Pyrewood Village แล้วใส่เครื่องรางที่ปรับแต่งแล้วนี้ลงในจุดฝากของลับของ Caius\n\nเรื่องที่จะเกิดขึ้นหลังจากนั้นอยู่นอกเหนือการควบคุมของเรา อย่างน้อยก็ในตอนนี้" }
assert(addon.quests[80454].objective == nil, "MAIN38 field baseline changed")
addon.quests[80454].objective = { "69:432550878:120517211", "นำ Modified Talisman ไปยังจุดฝากของลับของ Caius ใกล้ Pyrewood Village" }
assert(addon.quests[80455] == nil, "MAIN38 quest baseline changed")
addon.quests[80455] = {}
assert(addon.quests[80455].title == nil, "MAIN38 field baseline changed")
addon.quests[80455].title = { "15:2063242986:1214798587", "รอจังหวะของเรา" }
assert(addon.quests[80455].description == nil, "MAIN38 field baseline changed")
addon.quests[80455].description = { "63:314353310:463833191", "งานเสร็จแล้ว ควรกลับไป Ravenholdt และแจ้ง Fahrad" }
assert(addon.quests[80455].objective == nil, "MAIN38 field baseline changed")
addon.quests[80455].objective = { "42:480865581:1090234661", "กลับไปรายงานต่อ Fahrad ที่ Ravenholdt Manor" }
assert(addon.quests[81787] == nil, "MAIN38 quest baseline changed")
addon.quests[81787] = {}
assert(addon.quests[81787].title == nil, "MAIN38 field baseline changed")
addon.quests[81787].title = { "44:1503135168:524829644", "ภารกิจ Hinterlands II: ปราบเต่ายักษ์" }
assert(addon.quests[81787].description == nil, "MAIN38 field baseline changed")
addon.quests[81787].description = { "249:1323484661:280045722", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Seradane แล้วไปยัง Nightmare Incursion ที่ Shaol'watha ปราบเต่ายักษ์ที่นั่น แล้วกลับมาหาข้า" }
assert(addon.quests[81787].objective == nil, "MAIN38 field baseline changed")
addon.quests[81787].objective = { "119:1262583754:1995266617", "ปราบ Dreamwater Visejaw 20 ตัวใน Hinterlands Nightmare Incursion ที่ Shaol'watha แล้วกลับไปหา Field Captain Korlian" }
assert(addon.quests[81830] == nil, "MAIN38 quest baseline changed")
addon.quests[81830] = {}
assert(addon.quests[81830].title == nil, "MAIN38 field baseline changed")
addon.quests[81830].title = { "46:1885878467:256936923", "ภารกิจ Hinterlands VIII: นำ Elunar Relic กลับคืน" }
assert(addon.quests[81830].description == nil, "MAIN38 field baseline changed")
addon.quests[81830].description = { "280:1713779378:430693254", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Seradane แล้วไปยัง Nightmare Incursion ที่ Skulk Rock นำ Elunar Relic ที่พวกมูนคินซ่อนไว้ที่นั่นมาส่งให้ข้า" }
assert(addon.quests[81830].objective == nil, "MAIN38 field baseline changed")
addon.quests[81830].objective = { "137:304361134:1444438427", "นำ Elunar Relic จากชะง่อนหินสูงภายใน Skulk Rock ใน Hinterlands Nightmare Incursion กลับไปหา Field Captain Korlian" }
assert(addon.quests[81850] == nil, "MAIN38 quest baseline changed")
addon.quests[81850] = {}
assert(addon.quests[81850].title == nil, "MAIN38 field baseline changed")
addon.quests[81850].title = { "53:621221777:1823569575", "ภารกิจ Hinterlands XVI: ช่วยเหลือ Elianar Shadowdrinker" }
assert(addon.quests[81850].description == nil, "MAIN38 field baseline changed")
addon.quests[81850].description = { "312:1932353385:1437722717", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Seradane แล้วไปยัง Nightmare Incursion ที่ Agol'watha หา Elianar Shadowdrinker ดรูอิดแห่งกรงเล็บที่หลับใหลอยู่ที่นั่น และคุ้มกันเขาไปยังที่ปลอดภัย จากนั้นกลับมาหาข้า" }
assert(addon.quests[81850].objective == nil, "MAIN38 field baseline changed")
addon.quests[81850].objective = { "149:1567817319:294661556", "ช่วยเหลือ Elianar Shadowdrinker จาก Hinterlands Nightmare Incursion ที่แนวป้องกันของโทรลล์ใกล้ Agol'watha แล้วกลับไปหา Field Captain Korlian" }
assert(addon.quests[81857] == nil, "MAIN38 quest baseline changed")
addon.quests[81857] = {}
assert(addon.quests[81857].title == nil, "MAIN38 field baseline changed")
addon.quests[81857].title = { "37:2112264911:558963074", "ภารกิจ Feralas III: ปราบเผ่ามังกร" }
assert(addon.quests[81857].description == nil, "MAIN38 field baseline changed")
addon.quests[81857].description = { "244:1519943585:69519278", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Dream Bough แล้วไปยัง Nightmare Incursion ที่ Oneiros ปราบเผ่ามังกรที่นั่น แล้วกลับมาหาข้า" }
assert(addon.quests[81857].objective == nil, "MAIN38 field baseline changed")
addon.quests[81857].objective = { "133:1386536954:791307406", "ปราบ Frenzied Whelps 10 ตัวและ Wyrmkin Berserkers 3 ตัวใน Feralas Nightmare Incursion ที่ Oneiros แล้วกลับไปหา Field Captain Arunnel" }
assert(addon.quests[81859] == nil, "MAIN38 quest baseline changed")
addon.quests[81859] = {}
assert(addon.quests[81859].title == nil, "MAIN38 field baseline changed")
addon.quests[81859].title = { "40:913140354:48841486", "ภารกิจ Feralas V: ข่าวกรอง Cenarion" }
assert(addon.quests[81859].description == nil, "MAIN38 field baseline changed")
addon.quests[81859].description = { "294:854012163:1077808564", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Dream Bough แล้วไปยัง Nightmare Incursion ที่ Twin Colossals รับรายงานข่าวกรองจาก Dreamwarden Gorlas ที่นั่น แล้วกลับมาหาข้า" }
assert(addon.quests[81859].objective == nil, "MAIN38 field baseline changed")
addon.quests[81859].objective = { "156:1605997793:810200605", "รับข่าวกรองจาก Dreamwarden Gorlas ใน Feralas Nightmare Incursion ใกล้น้ำตกที่ Twin Colossals แล้วกลับไปหา Field Captain Arunnel" }
assert(addon.quests[81861] == nil, "MAIN38 quest baseline changed")
addon.quests[81861] = {}
assert(addon.quests[81861].title == nil, "MAIN38 field baseline changed")
addon.quests[81861].title = { "47:311294120:2038385198", "ภารกิจ Feralas VII: นำ Moonglow Dragonegg กลับคืน" }
assert(addon.quests[81861].description == nil, "MAIN38 field baseline changed")
addon.quests[81861].description = { "255:449995766:1233951551", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Dream Bough แล้วไปยัง Nightmare Incursion ที่ Oneiros นำ Moonglow Dragonegg มาส่งให้ข้า" }
assert(addon.quests[81861].objective == nil, "MAIN38 field baseline changed")
addon.quests[81861].objective = { "127:595207019:1516395477", "นำ Moonglow Dragonegg จากศาลาที่ Oneiros ใน Feralas Nightmare Incursion กลับไปหา Field Captain Arunnel" }
assert(addon.quests[81865] == nil, "MAIN38 quest baseline changed")
addon.quests[81865] = {}
assert(addon.quests[81865].title == nil, "MAIN38 field baseline changed")
addon.quests[81865].title = { "27:775906856:402583775", "ภารกิจ Feralas X: Moonroot" }
assert(addon.quests[81865].description == nil, "MAIN38 field baseline changed")
addon.quests[81865].description = { "304:1443352863:1139687273", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Dream Bough แล้วเก็บ Moonroot จากภายใน Nightmare Incursions เราสามารถใช้เวทมนตร์ของมันฟื้นฟูความเสียหายที่เกิดขึ้นได้ เจ้าจะต้องอาศัยความช่วยเหลือจากผู้มีวิชาเก็บสมุนไพร" }
assert(addon.quests[81865].objective == nil, "MAIN38 field baseline changed")
addon.quests[81865].objective = { "91:2088901045:2147399236", "เก็บ Moonroot 10 ชิ้นใน Feralas Nightmare Incursions แล้วกลับไปหา Field Captain Arunnel" }
assert(addon.quests[81874] == nil, "MAIN38 quest baseline changed")
addon.quests[81874] = {}
assert(addon.quests[81874].title == nil, "MAIN38 field baseline changed")
addon.quests[81874].title = { "48:791038588:1913895841", "ภารกิจ Feralas XVIII: ช่วยเหลือ Jamniss Treemender" }
assert(addon.quests[81874].description == nil, "MAIN38 field baseline changed")
addon.quests[81874].description = { "324:1613464582:1478578525", "ขณะที่ปีศาจเหล่านี้คอยเบี่ยงเบนความสนใจของเราอยู่ที่นี่ Emerald Dream กำลังถูกบิดเบือนให้กลายเป็นฝันร้าย รีบเดินทางผ่าน Emerald Dream Portal ใน Dream Bough แล้วไปยัง Nightmare Incursion ที่ Ruins of Ravenwind หา Jamnice Treemender ดรูอิดแห่งกรงเล็บที่หลับใหลอยู่ที่นั่น และคุ้มกันนางไปยังที่ปลอดภัย จากนั้นกลับมาหาข้า" }
assert(addon.quests[81874].objective == nil, "MAIN38 field baseline changed")
addon.quests[81874].objective = { "146:249332095:2079518260", "ช่วยเหลือ Jamnice Treemender จาก Feralas Nightmare Incursion ที่ขอบด้านเหนือของ Ruins of Ravenwind แล้วกลับไปหา Field Captain Arunnel" }
assert(addon.quests[81790] == nil, "MAIN38 quest baseline changed")
addon.quests[81790] = {}
assert(addon.quests[81790].title == nil, "MAIN38 field baseline changed")
addon.quests[81790].title = { "25:749265385:797437307", "วัตถุดิบที่มีความสำคัญ" }
assert(addon.quests[81790].description == nil, "MAIN38 field baseline changed")
addon.quests[81790].description = { "464:71641192:1992272566", "ลูกแก้ว Echoing Orb แต่ละลูกเชื่อมโยงกับด้านหนึ่งที่ต่างกันของผู้เป็นนาย วิธีที่เจ้าใช้ใน Ashenvale เพื่อทำลาย Althalaxx Orb จะใช้กับลูกแก้วที่เราครอบครองอยู่ไม่ได้ ข้ารู้จักพิธีกรรมที่อาจทำให้ลูกแก้วไม่เสถียรและเปิดโอกาสให้เราทำลายมันได้ แต่พิธีนี้ต้องใช้วัตถุดิบที่มีความหมายเฉพาะทางเวทมนตร์ เรามีวัตถุดิบที่ต้องใช้บางส่วนแล้ว แต่เจ้าต้องไปหาส่วนที่เหลือ\n\nรับนี่ไป มันน่าจะช่วยในการค้นหาของเจ้า" }
assert(addon.quests[81790].objective == nil, "MAIN38 field baseline changed")
addon.quests[81790].objective = { "145:1234781847:860291685", "ใช้คำใบ้ใน Gregory's Note เพื่อหาว่าจะหาวัตถุดิบเวทมนตร์ที่จำเป็นสำหรับพิธีกรรมได้จากที่ไหน งานนี้เจ้าจะต้องอาศัยความช่วยเหลือจากพันธมิตร" }
assert(addon.quests[82135] == nil, "MAIN38 quest baseline changed")
addon.quests[82135] = {}
assert(addon.quests[82135].title == nil, "MAIN38 field baseline changed")
addon.quests[82135].title = { "17:121969296:1831628882", "ราคาของความหวัง" }
assert(addon.quests[82135].description == nil, "MAIN38 field baseline changed")
addon.quests[82135].description = { "65:1291673620:731103692", "<Aeonas ไม่พูดอะไร เขาเพียงยื่นลูกแก้วให้เจ้าแล้วหันจากไป>" }
assert(addon.quests[82135].objective == nil, "MAIN38 field baseline changed")
addon.quests[82135].objective = { "66:71038856:1743194881", "นำ Mannoroc Echoing Orb ไปให้ Katherine the Pure ใน Stormwind" }
assert(addon.quests[84414] == nil, "MAIN38 quest baseline changed")
addon.quests[84414] = {}
assert(addon.quests[84414].title == nil, "MAIN38 field baseline changed")
addon.quests[84414].title = { "17:570955482:133109477", "ส่งข้าเดินทางต่อ" }
assert(addon.quests[84414].description == nil, "MAIN38 field baseline changed")
addon.quests[84414].description = { "105:676759711:990194754", "<เจ้าได้ยินเสียงที่ไร้ร่างของ Orthas ในจิตใจ>\n\nเอาละ เรามาถึงแล้ว เริ่มกันเลยดีไหม?" }
assert(addon.quests[84414].objective == nil, "MAIN38 field baseline changed")
addon.quests[84414].objective = { "46:1782341874:645730117", "เฝ้าดู Orthas ขณะที่เขาจากโลกนี้ไป" }
assert(addon.quests[84146] == nil, "MAIN38 quest baseline changed")
addon.quests[84146] = {}
assert(addon.quests[84146].title == nil, "MAIN38 field baseline changed")
addon.quests[84146].title = { "13:274248890:1873039198", "ความกลุ้มใจเรื่องถุงสีแดง" }
assert(addon.quests[84146].description == nil, "MAIN38 field baseline changed")
addon.quests[84146].description = { "420:1965269590:1753744790", "สิ่งที่เจ้าต้องการถูกซ่อนไว้อย่างปลอดภัยแล้ว และข้าก็ได้แต่หวังว่าสิ่งที่ข้าตามหาจะเป็นเช่นนั้นด้วย\n\nข้ามีถุงสีแดงใบหนึ่ง ใส่เครื่องมือมีค่าที่ข้าใช้ในงาน electro-optics แต่ข้าทำมันหายในอุบัติเหตุเรือเหาะเหนือ Burning Steppes! ถุงอาจยังอยู่ที่นั่น แต่เพราะมีทั้งออร์ค โอเกอร์ และพวกลักลอบล่าสัตว์ ข้าจึงต้องพักงานไว้ก่อน\n\nหากเจ้าหามันพบและนำกลับมาให้ข้า ข้าจะให้หนังสือเก่าของ Jurgens แก่เจ้า" }
assert(addon.quests[84146].objective == nil, "MAIN38 field baseline changed")
addon.quests[84146].objective = { "88:1277783929:2017086916", "หา Red Bag ที่ Nami แห่ง Everlook ทำหายไปในอุบัติเหตุเรือเหาะเหนือ Burning Steppes" }
assert(addon.quests[84160] == nil, "MAIN38 quest baseline changed")
addon.quests[84160] = {}
assert(addon.quests[84160].title == nil, "MAIN38 field baseline changed")
addon.quests[84160].title = { "22:1183475074:147978204", "ข้อเสนอที่จริงใจ" }
assert(addon.quests[84160].objective == nil, "MAIN38 field baseline changed")
addon.quests[84160].objective = { "129:941893961:316611341", "รวบรวม Silithus Venom Samples 15 ชิ้นและทอง 20 เหรียญ แล้วนำไปพร้อมกับ Bindings of the Elements หนึ่งชุดให้ Mokvar ใน Orgrimmar" }
assert(addon.quests[84163] == nil, "MAIN38 quest baseline changed")
addon.quests[84163] = {}
assert(addon.quests[84163].title == nil, "MAIN38 field baseline changed")
addon.quests[84163].title = { "17:479802657:1407557245", "ค่าตอบแทนที่เหมาะสม" }
assert(addon.quests[84163].description == nil, "MAIN38 field baseline changed")
addon.quests[84163].description = { "259:1216461947:593867283", "เจ้ารักษาคำพูดและนำอุปกรณ์ที่ Mux สร้างมาแล้ว ข้าคิดว่าควรให้รางวัล เพื่อให้เจ้ายังสนใจช่วยชีวิตข้าต่อ นำเข็มขัดกับถุงมือที่อยากอัปเกรดมา ข้าสัญญาว่าของที่ให้แลกกลับไปจะดีกว่ามาก" }
assert(addon.quests[84163].objective == nil, "MAIN38 field baseline changed")
addon.quests[84163].objective = { "74:624044070:1282990164", "นำ Wildheart Belt และ Wildheart Gloves ไปให้ Deliana ที่ Ironforge" }
assert(addon.quests[84165] == nil, "MAIN38 quest baseline changed")
addon.quests[84165] = {}
assert(addon.quests[84165].title == nil, "MAIN38 field baseline changed")
addon.quests[84165].title = { "17:479802657:1407557245", "ค่าตอบแทนที่เหมาะสม" }
assert(addon.quests[84165].description == nil, "MAIN38 field baseline changed")
addon.quests[84165].description = { "207:93466123:251441568", "เจ้ารักษาคำพูดและนำอุปกรณ์ที่ Mux สร้างมาแล้ว ข้าคิดว่าควรให้รางวัล เพื่อให้เจ้ายังสนใจช่วยชีวิตข้าต่อ นำเข็มขัดธรรมดากับถุงมือที่อยากอัปเกรดมา" }
assert(addon.quests[84165].objective == nil, "MAIN38 field baseline changed")
addon.quests[84165].objective = { "79:1400312166:609455990", "นำ เข็มขัดของจอมเวท และ ถุงมือของจอมเวท ไปให้ Deliana ที่ Ironforge" }
assert(addon.quests[84168] == nil, "MAIN38 quest baseline changed")
addon.quests[84168] = {}
assert(addon.quests[84168].title == nil, "MAIN38 field baseline changed")
addon.quests[84168].title = { "17:479802657:1407557245", "ค่าตอบแทนที่เหมาะสม" }
assert(addon.quests[84168].description == nil, "MAIN38 field baseline changed")
addon.quests[84168].description = { "259:1216461947:593867283", "เจ้ารักษาคำพูดและนำอุปกรณ์ที่ Mux สร้างมาแล้ว ข้าคิดว่าควรให้รางวัล เพื่อให้เจ้ายังสนใจช่วยชีวิตข้าต่อ นำเข็มขัดกับถุงมือที่อยากอัปเกรดมา ข้าสัญญาว่าของที่ให้แลกกลับไปจะดีกว่ามาก" }
assert(addon.quests[84168].objective == nil, "MAIN38 field baseline changed")
addon.quests[84168].objective = { "81:1169569682:1895209806", "นำ เข็มขัดช่างเงา และ ถุงมือช่างเงา ไปให้ Deliana ที่ Ironforge" }
assert(addon.quests[84173] == nil, "MAIN38 quest baseline changed")
addon.quests[84173] = {}
assert(addon.quests[84173].title == nil, "MAIN38 field baseline changed")
addon.quests[84173].title = { "17:479802657:1407557245", "ค่าตอบแทนที่เหมาะสม" }
assert(addon.quests[84173].objective == nil, "MAIN38 field baseline changed")
addon.quests[84173].objective = { "78:1530699334:500177513", "นำ เข็มขัดของจอมเวท และ ถุงมือของจอมเวท ไปให้ Mokvar ที่ Orgrimmar" }
assert(addon.quests[84192] == nil, "MAIN38 quest baseline changed")
addon.quests[84192] = {}
assert(addon.quests[84192].title == nil, "MAIN38 field baseline changed")
addon.quests[84192].title = { "23:573656928:1309079977", "คำอำลาของ Anthion" }
assert(addon.quests[84192].description == nil, "MAIN38 field baseline changed")
addon.quests[84192].description = { "454:1366191329:981737942", "วิญญาณของ Valthalak ถูกเก็บอยู่ในเครื่องรางนี้ ด้วยความโลภ เราโง่เขลาแบ่งมันเป็นสามส่วน โดยไม่รู้คำสาปที่รออยู่\n\nหนทางเดียวที่จะหยุดคาถาของ Valthalak คือประกอบเครื่องรางกลับเข้าด้วยกัน กลับไปบอก Mokvar ว่า Bodley เป็นความหวังเดียวที่จะหาส่วนที่เหลือได้ คุยกับเขาเรื่องรางวัลที่ตกลงกันไว้ด้วย\n\nคราวนี้ข้าจะได้พักอย่างสงบ ขอให้เจ้าโชคดีที่สุด เพราะเจ้าจะต้องใช้โชคทั้งหมดที่มี!" }
assert(addon.quests[84192].objective == nil, "MAIN38 field baseline changed")
addon.quests[84192].objective = { "105:843878935:1177516525", "กลับไปหา Mokvar ที่ Orgrimmar พร้อม รองเท้าบูตแห่งธาตุ, กระโปรงเกราะแห่งธาตุ และ เกราะไหล่แห่งธาตุ" }
