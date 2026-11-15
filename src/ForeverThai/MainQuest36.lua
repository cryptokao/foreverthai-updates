-- MAIN36: full literal own-ID fields only. Game chooses conditions; no inferred dispatch.
local _, addon = ...
assert(type(addon.quests[960].title) == "table", "MAIN36 canonical missing")
addon.quests[960].title.variants = addon.quests[960].title.variants or {}
table.insert(addon.quests[960].title.variants, { "17:1578583522:497806560", "Onu กำลังทำสมาธิ" })
assert(type(addon.quests[7025].description) == "table", "MAIN36 canonical missing")
addon.quests[7025].description.variants = addon.quests[7025].description.variants or {}
table.insert(addon.quests[7025].description.variants, { "361:1999400039:1370535986", "นี่ ช่วยคุณปู่วินเทอร์หน่อยได้ไหม เอ่อ เจ้าหนู?\n\nไม่ใช่ว่าอยากพูดถึงตัวเองเหมือนเป็นคนอื่นโดยไม่จำเป็นหรอกนะ แต่คุณปู่วินเทอร์ทำงานนี้มาทั้งวันแล้ว และอยากกินขนมบ้าง คุกกี้ขนมปังขิงกับนมเย็นจัดสักหน่อยคงชื่นใจทีเดียว เจ้าจะช่วยเป็นเพื่อนที่ดีของคุณปู่ ไปเอามาให้ข้าหน่อยได้ไหม?" })
assert(type(addon.quests[7630].objective) == "table", "MAIN36 canonical missing")
addon.quests[7630].objective.variants = addon.quests[7630].objective.variants or {}
table.insert(addon.quests[7630].objective.variants, { "57:2026677160:2090889121", "นำ Arcanite Bar 3 แท่งไปให้ Gorzeeki ใน Burning Steppes" })
assert(addon.quests[84156].objective == nil, "MAIN36 field baseline changed")
addon.quests[84156].objective = { "128:1987371442:1583139117", "รวบรวม Silithus Venom Samples 15 ชิ้นและทอง 20 เหรียญ แล้วนำไปพร้อมกับ Beaststalker's Bindings หนึ่งชุดให้ Mokvar ใน Orgrimmar" }
assert(type(addon.quests[99212].description) == "table", "MAIN36 canonical missing")
addon.quests[99212].description.variants = addon.quests[99212].description.variants or {}
table.insert(addon.quests[99212].description.variants, { "644:2098865895:2071569536", "ขอคารวะ วอร์ล็อก! ต้องยอมรับว่าข้าประหลาดใจที่เห็นผู้มีความสามารถอย่างเจ้ามาที่นี่ แต่ข้าก็ยังยินดีรับเงินของเจ้าอยู่ดี\n\nหากเจ้ากำลังมองหาพาหนะ ก็มาถูกที่แล้ว ถึงความรู้สึกเวลาขี่จะแตกต่างจาก Felsteed ที่เจ้าคุ้นเคยกับการอัญเชิญก็ตาม\n\nอย่างไรก็ดี ข้าอยากให้เจ้าลองดูเมคาโนสไตรเดอร์รุ่นล่าสุดของเรา หากเจ้าอยากได้สักตัว ถ้าเห็นตัวที่ถูกใจ ก็บอกข้า เพื่อเราจะได้ซิงก์ข้อมูลชีวมิติของเจ้ากับระบบตรวจจับผู้ขี่ ระบบนี้จะช่วยให้สไตรเดอร์แยกเจ้าออกจากคนอื่นที่อาจขึ้นขี่ได้\n\nไปดูเมคาโนสไตรเดอร์ แล้วบอกข้าหากเจ้าพบตัวที่ถูกใจ!" })
assert(addon.quests[99212].objective == nil, "MAIN36 field baseline changed")
addon.quests[99212].objective = { "70:2062305225:177481034", "ตรวจดูเมคาโนสไตรเดอร์รุ่นอัปเกรดเพื่อเลือกพาหนะระดับมหากาพย์ของเจ้า" }
assert(addon.quests[86792] == nil, "MAIN36 new quest baseline changed")
addon.quests[86792] = {}
assert(addon.quests[86792].title == nil, "MAIN36 field baseline changed")
addon.quests[86792].title = { "21:923662071:1867066988", "ลดกำลังศัตรู" }
assert(addon.quests[86792].description == nil, "MAIN36 field baseline changed")
addon.quests[86792].description = { "453:481854592:1715892420", "พวกซาเทียร์ในฐานที่มั่น Legashi น่ากลัวยิ่งกว่าพวกที่อยู่ตามค่ายรอบนอกเสียอีก เมื่อกลุ่มของเราถูกพบเข้า พวกเราก็ถูกโจมตีจนต้านไม่ไหว\n\nพวกเราคนหนึ่งถูกฆ่า อีกคนถูกจับตัวไป มีเพียงข้าที่ถอยหนีออกมาได้สำเร็จ ข้าไม่อาจกลับไปหา Rageroar โดยก้มหน้าด้วยความอับอาย แต่ข้าก็สู้กับพวก Legashi เพียงลำพังไม่ได้เช่นกัน\n\nข้าจึงขอให้เจ้าช่วยลดกำลังของพวกซาเทียร์ บุกเข้าไปในฐานที่มั่นแล้วสังหารพวกมัน" }
assert(addon.quests[86814] == nil, "MAIN36 new quest baseline changed")
addon.quests[86814] = {}
assert(addon.quests[86814].title == nil, "MAIN36 field baseline changed")
addon.quests[86814].title = { "26:1255820186:1483705033", "การโต้กลับของ Blackmaw" }
assert(addon.quests[86814].description == nil, "MAIN36 field baseline changed")
addon.quests[86814].description = { "258:2145320676:757238525", "ข้าจะส่งกำลังเสริมไปยัง Ursolan ทันที\n\nรับธงนี้ไป เมื่อเจ้าพร้อมเผชิญหน้ากับ Halanox ให้ปักธงในวงเวทอัญเชิญปีศาจของเขา นี่จะยั่วยุเขา และเป็นสัญญาณให้นักรบของเราเข้าโจมตี\n\nเมื่อปราบ Halanox ได้แล้ว ให้แจ้ง Gatekeeper Rageroar" }
assert(addon.quests[86814].objective == nil, "MAIN36 field baseline changed")
addon.quests[86814].objective = { "144:1756564002:1890887637", "ปัก Timbermaw War Banner ที่ Legashi Stronghold ใน Azshara สังหาร Prince Halanox แล้วรายงานชัยชนะต่อ Gatekeeper Rageroar ที่ Ursolan" }
assert(addon.quests[9556] == nil, "MAIN36 new quest baseline changed")
addon.quests[9556] = {}
assert(addon.quests[9556].title == nil, "MAIN36 field baseline changed")
addon.quests[9556].title = { "16:1989527230:1789345191", "แด่ผู้ชนะ..." }
assert(addon.quests[9556].objective == nil, "MAIN36 field baseline changed")
addon.quests[9556].objective = { "224:2042314211:936207554", "เก็บ Stratholme Holy Water หนึ่งขวดจากภายในเมือง Stratholme แล้วนำไปส่งให้ Lordaeron Mage ใน Mage Quarter ของ Stormwind หรือ Undercity เมื่อฝ่ายของเจ้าชนะใน Eastern Plaguelands" }
