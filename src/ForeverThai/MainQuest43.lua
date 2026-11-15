-- MAIN43: reviewed literal fields;match exact own-ID full UI source only.
-- No enabled-quest inventory,player condition or identity/quantity macro dispatch inferred.
local _, addon = ...
assert(addon.quests[96031].progress == nil, "MAIN43 field baseline changed")
addon.quests[96031].progress = { "21:597269750:1281937852", "ได้ ข้าสอนเจ้าได้" }
assert(addon.quests[97905].progress == nil, "MAIN43 field baseline changed")
addon.quests[97905].progress = { "20:562170160:239285947", "ได้ ข้าสอนเจ้าได้" }
assert(addon.quests[97906].progress == nil, "MAIN43 field baseline changed")
addon.quests[97906].progress = { "21:597269750:1281937852", "ได้ ข้าสอนเจ้าได้" }
assert(addon.quests[97929].progress == nil, "MAIN43 field baseline changed")
addon.quests[97929].progress = { "21:597269750:1281937852", "ได้ ข้าสอนเจ้าได้" }
assert(addon.quests[97940].progress == nil, "MAIN43 field baseline changed")
addon.quests[97940].progress = { "21:597269750:1281937852", "ได้ ข้าสอนเจ้าได้" }
assert(addon.quests[97948].progress == nil, "MAIN43 field baseline changed")
addon.quests[97948].progress = { "31:1115327614:632329784", "เจ้ามาขอฝึกหรือ?" }
assert(addon.quests[97958].progress == nil, "MAIN43 field baseline changed")
addon.quests[97958].progress = { "21:597269750:1281937852", "ได้ ข้าสอนเจ้าได้" }
assert(addon.quests[92646].progress == nil, "MAIN43 field baseline changed")
addon.quests[92646].progress = { "50:1166770872:1536718489", "ข้าเกรงว่าสถานการณ์ของพวกเรากำลังจะแย่ลงกว่านี้มาก" }
assert(addon.quests[98059].progress == nil, "MAIN43 field baseline changed")
addon.quests[98059].progress = { "31:1384298176:1936685465", "เจ้ามาแก้ไขรายงานหรือ?" }
assert(addon.quests[1144].progress == nil, "MAIN43 field baseline changed")
addon.quests[1144].progress = { "12:1836886045:1821925703", "ช่วยข้าด้วย!" }
assert(addon.quests[96261].progress == nil, "MAIN43 field baseline changed")
addon.quests[96261].progress = { "42:186319396:1361322106", "เจ้ากำจัดแม่พันธุ์แล้วหรือดรูอิด?" }
assert(addon.quests[92707].progress == nil, "MAIN43 field baseline changed")
addon.quests[92707].progress = { "60:234201751:1281995667", "มีอะไรจะบอกข้าหรือ? ก็พูดมา! ข้าไม่ทนพวกขี้กลัวหรอก" }
assert(addon.quests[97284].progress == nil, "MAIN43 field baseline changed")
addon.quests[97284].progress = { "23:1045674245:1801716632", "การสังหารเป็นอย่างไรบ้าง?" }
assert(addon.quests[97331].progress == nil, "MAIN43 field baseline changed")
addon.quests[97331].progress = { "81:751744102:2086831518", "ข้าคงถามว่าเจ้ามาส่งของหรือเปล่า แต่ข้าไม่เห็นลัง เรามีธุระอะไรกัน?" }
assert(addon.quests[93786].progress == nil, "MAIN43 field baseline changed")
addon.quests[93786].progress = { "32:1855442390:473733628", "สนุกกับความตื่นเต้นของการล่าอยู่หรือ?" }
assert(addon.quests[95534].progress == nil, "MAIN43 field baseline changed")
addon.quests[95534].progress = { "102:1710803524:1181285133", "หืม? เจ้ากำลังสืบปริศนาใน Strahnbrad อยู่หรือ? เชอะ เมืองร้างเก่านั่นไม่มีอะไรพิเศษหรอก" }
assert(addon.quests[92872].progress == nil, "MAIN43 field baseline changed")
addon.quests[92872].progress = { "172:680309178:599510973", "แม้สถานที่แห่งความตายอันสงบขรึมนี้ ก็ยังมีสสารใหม่ไหลเข้ามา การปลดปล่อยมันกลับสู่แสงด้วยวิธีนี้ มีเจตนาให้เป็นสัญลักษณ์ของการมุ่งสู่เมล็ดพันธุ์แห่งชีวิตใหม่" }
assert(addon.quests[95776].progress == nil, "MAIN43 field baseline changed")
addon.quests[95776].progress = { "142:1699940806:132623805", "ข้ายอมรับว่าเกลียดชังพวกนากาไม่น้อย แม้จะชื่นชมความทรหดและความแข็งแกร่งของพวกมัน\n\nพวกมันเป็นศัตรูที่คู่ควรกับคมดาบของข้า" }
assert(addon.quests[94483].progress == nil, "MAIN43 field baseline changed")
addon.quests[94483].progress = { "95:1949108596:1794700009", "เมื่อสกัดภัยคุกคามจากสหายของเราที่อยู่ปลายน้ำได้แล้ว เราจะหันความสนใจไปที่อื่น" }
assert(addon.quests[94924].progress == nil, "MAIN43 field baseline changed")
addon.quests[94924].progress = { "81:1972535692:831110515", "สักวันเราจะขับไล่ออร์กทั้งหมดออกไปจากที่นี่ แต่ตอนนี้ เราทำเท่าที่ทำได้" }
assert(addon.quests[95955].progress == nil, "MAIN43 field baseline changed")
addon.quests[95955].progress = { "86:1067743113:693009330", "เจ้าหาพวกครอคโคลิสก์ได้ตามแม่น้ำ แค่อย่าเข้าใกล้พวกมันนักล่ะ ฮี่ๆๆ" }
assert(addon.quests[95602].progress == nil, "MAIN43 field baseline changed")
addon.quests[95602].progress = { "42:389814263:1468121428", "แสงทำให้ Clubtoe เวียนหัว ทุบพวกมันให้เละ!" }
assert(addon.quests[95770].progress == nil, "MAIN43 field baseline changed")
addon.quests[95770].progress = { "89:1684089486:1957815155", "เจ้ากลับมาแล้ว! พบอะไรบ้างไหม? เจ้ารู้อะไรเกี่ยวกับพวกนากาที่นี่บ้าง?" }
assert(addon.quests[95791].progress == nil, "MAIN43 field baseline changed")
addon.quests[95791].progress = { "362:1673102159:943543572", "โธ่ เรือพวกนั้นน่าขนลุกจริง\n\nดูเหมือนโจรสลัด Saltseer จะมีวิธีเดินเรือที่ข้าไม่เคยเห็นมาก่อน มันผิดธรรมชาติ! แทบเหมือนกับว่าเรือมีชีวิต ข้าเคยเห็นโจรสลัดบนเรือเดินออกจากพวงมาลัยเรือ แล้วเรือก็ดูเหมือนแล่นเองได้!\n\nข้าไม่อยากรู้หรอกว่าพวกมันทำได้อย่างไร ข้ารู้สึกว่าเป็นเวทมนตร์ดำ" }
assert(addon.quests[96067].progress == nil, "MAIN43 field baseline changed")
addon.quests[96067].progress = { "112:739118178:579446813", "ข้าขอชี้แจงว่าข้าไม่ต้องรับผิดชอบเป็นการส่วนตัวต่อการบาดเจ็บใดๆที่เจ้าได้รับระหว่างการทดสอบความทนทาน" }
assert(addon.quests[97017].progress == nil, "MAIN43 field baseline changed")
addon.quests[97017].progress = { "204:832895451:1793998889", "กลับมาแล้วหรือ? เจ้าเลือกได้แล้วสินะ?\n\nแกะตัวผู้เหล่านี้อาจดื้อ แต่ไม่มีสัตว์ตัวไหนยอดเยี่ยมกว่านี้ในเทือกเขาฝั่งนี้ แทบไม่มีอะไรทำให้พวกมันหวั่นไหว!\n\nเจ้าหาสหายที่แข็งแกร่งทนทานกว่านี้ไม่ได้แล้ว" }
assert(addon.quests[97045].progress == nil, "MAIN43 field baseline changed")
addon.quests[97045].progress = { "154:416692439:279040156", "เจ้ากลับมาแล้ว! เลือกได้แล้วหรือ? ม้าเหล่านี้เป็นม้าชั้นเลิศแถบนี้ของ Eastern Kingdoms\n\nเจ้าหาม้าขี่ที่กล้าหาญกว่านี้ไม่ได้แล้ว" }
assert(addon.quests[97046].progress == nil, "MAIN43 field baseline changed")
addon.quests[97046].progress = { "386:133513189:1469138553", "เจ้าเลือกได้แล้วหรือ? เมคาโนสไตรเดอร์เหล่านี้มีคุณภาพสูงสุด และทำขึ้นด้วยมือของวิศวกรชั้นยอดแห่ง Gnomeregan! เอ่อ ข้าหมายถึง Ironforge สินะ\nพวกมันเชื่อถือได้มากกว่าสัตว์ชนิดใด ไม่มีความรู้สึกนึกคิด แต่ก็มีลักษณะเฉพาะตัว ส่วนใหญ่มาจากความแตกต่างในการสร้างโดยวิศวกรคนละคน แต่ถึงอย่างนั้น ส่วนใหญ่ก็เลือกกันตามสีที่ชอบ" }
assert(addon.quests[97188].progress == nil, "MAIN43 field baseline changed")
addon.quests[97188].progress = { "214:928132728:1380829371", "เมื่อเจ้าเรียนบังคับเมคาโนสไตรเดอร์ได้แล้ว เจ้าก็จะเดินทางไปทั่วโลกกับสัตว์ขี่ของเจ้าได้!\n\nเร็วกว่าวิ่งไปทุกที่แน่นอน แต่ถ้าเจ้าชอบวิ่ง ข้าก็ไม่ห้ามหรอก" }
assert(addon.quests[97194].progress == nil, "MAIN43 field baseline changed")
addon.quests[97194].progress = { "202:1608995991:908975933", "เมื่อเจ้าเรียนขี่หมาป่าได้แล้ว เจ้าก็จะเดินทางไปทั่วโลกกับสัตว์ขี่ของเจ้าได้\n\nเร็วกว่าวิ่งไปทุกที่แน่นอน แต่ถ้าเจ้าชอบวิ่ง ข้าก็ไม่ห้ามหรอก" }
assert(addon.quests[97200].progress == nil, "MAIN43 field baseline changed")
addon.quests[97200].progress = { "329:1740078172:1732553940", "เมื่อเจ้าเรียนขี่แรปเตอร์ได้แล้ว เจ้าก็จะเดินทางไปทั่วโลกกับสัตว์ขี่ของเจ้าได้!\n\nไม่มีอะไรทำให้รู้สึกเป็นอิสระยิ่งกว่าการอยู่บนหลังสัตว์เหล่านี้ แล้วรู้สึกว่าพื้นดินแล่นผ่านไปอย่างรวดเร็ว\n\nเร็วกว่าวิ่งไปทุกที่แน่นอน แต่ถ้าเจ้าชอบวิ่ง ข้าก็ไม่ห้ามหรอก" }
assert(addon.quests[97204].progress == nil, "MAIN43 field baseline changed")
addon.quests[97204].progress = { "203:1855914811:1065877534", "เมื่อเจ้าเรียนขี่โคโดได้แล้ว เจ้าก็จะเดินทางไปทั่วโลกกับสัตว์ขี่ของเจ้าได้\n\nเร็วกว่าวิ่งไปทุกที่แน่นอน แต่ถ้าเจ้าชอบวิ่ง ข้าก็ไม่ห้ามหรอก" }
assert(addon.quests[97205].progress == nil, "MAIN43 field baseline changed")
addon.quests[97205].progress = { "210:115049656:490021152", "เมื่อเจ้าเรียนขี่ galestrider ได้แล้ว เจ้าก็จะเดินทางไปทั่วโลกกับสัตว์ขี่ของเจ้าได้\n\nเร็วกว่าวิ่งไปทุกที่แน่นอน แต่ถ้าเจ้าชอบวิ่ง ข้าก็ไม่ห้ามหรอก" }
assert(addon.quests[94672].progress == nil, "MAIN43 field baseline changed")
addon.quests[94672].progress = { "66:1022248646:619398537", "ดูเหมือนจำนวนของพวกมันกำลังเพิ่มขึ้น เราต้องชะลอการรุกคืบของพวกมัน" }
assert(addon.quests[95118].progress == nil, "MAIN43 field baseline changed")
addon.quests[95118].progress = { "71:1990762200:1238162648", "ข้าไม่สนว่าเจ้าจะทำอย่างไร แค่ทำให้พวกตัวประหลาดมีเกล็ดนั่นกลายเป็นอาหารปลาก็พอ" }
assert(addon.quests[95424].progress == nil, "MAIN43 field baseline changed")
addon.quests[95424].progress = { "27:1846768603:384751347", "เจ้าไม่ทุบ เจ้าไม่ได้อยู่!" }
assert(addon.quests[93450].completion == nil, "MAIN43 field baseline changed")
addon.quests[93450].completion = { "433:285098364:977775743", "เดี๋ยว... เจ้าทำได้หรือ? เอ่อ ข้าหมายถึง... เจ้าทำได้แล้ว!\n\nปัญหาของข้าเป็นเรื่องจริง แต่ทางแก้ที่ข้าอยากได้นั้นไม่ใช่เรื่องที่เป็นไปได้จริงเลย ข้าไม่แน่ใจว่าอะไรทำให้ประหลาดใจที่สุด เจ้ากล้าเสี่ยงทำมัน? หรือใบมีดตามเจ้าเข้าไปในแดนวิญญาณ?\n<Vindael มองเจ้าตั้งแต่หัวจรดเท้าครั้งหนึ่ง แล้วอีกครั้งด้วยสีหน้าเริ่มระแวง>\n\nเจ้ายังดูมีชีวิตอยู่เต็มที่สำหรับคนที่ได้ลิ้มรสความตาย ทำไมไม่แบ่งปันความลับกับพวกเราบ้างล่ะ?" }
assert(addon.quests[94556].progress == nil, "MAIN43 field baseline changed")
addon.quests[94556].progress = { "3:4783604:1249934", "หืม?" }
assert(addon.quests[93066].progress == nil, "MAIN43 field baseline changed")
addon.quests[93066].progress = { "212:688667643:1754310729", "อา เจ้าคงเป็นคนนอกที่คอยทำธุระให้ Orgrul\n\nโชคดีจริงที่เจ้าย่องเงียบได้แย่มาก หากหน่วยสอดแนมของข้าไม่เห็นเจ้าเดินโครมครามทำธุระแทนเขา หัวเจ้าคงเสียบอยู่บนหอกเปื้อนเลือดแล้ว" }
assert(addon.quests[93341].progress == nil, "MAIN43 field baseline changed")
addon.quests[93341].progress = { "276:962842941:414105303", "ตอนเสาพลังของเราอ่อนกำลังที่สุด ข้าไม่อาจเข้าใกล้สวนเพื่อตรวจสอบปัญหาได้ ตอนนี้หมอกจางแล้ว แต่ข้ากลับทำใจเข้าใกล้อีกไม่ได้ ข้าเป็นห่วงพวกทรีแอนต์\n\nข้าไม่อยากให้ความทรงจำเกี่ยวกับสถานที่อันงดงามเช่นนั้นมัวหมองไปยิ่งกว่านี้" }
assert(addon.quests[94964].progress == nil, "MAIN43 field baseline changed")
addon.quests[94964].progress = { "20:1199145490:1700823422", "ว่าไง? เจ้าต้องการอะไร?" }
assert(addon.quests[95119].progress == nil, "MAIN43 field baseline changed")
addon.quests[95119].progress = { "124:57780004:327757892", "โดยหลักแล้ว ข้าไม่ได้ต่อต้านโจรสลัดทุกคน ข้าสนับสนุนการทำธุรกิจอย่างเสรีอยู่บ้าง แต่ไม่ใช่เมื่อมันมายุ่งกับธุรกิจเสรีของข้า" }
assert(addon.quests[95432].progress == nil, "MAIN43 field baseline changed")
addon.quests[95432].progress = { "106:1578881230:1901968721", "พวก Twilight คิดว่ายักษ์โง่ ใช้เป็นแรงงาน เปลืองศักยภาพของยักษ์ ฆ่าพวก Twilight ทุกคนที่ขวางทางเจ้า!" }
assert(addon.quests[99258].progress == nil, "MAIN43 field baseline changed")
addon.quests[99258].progress = { "172:940237052:1283601567", "ข้าเฝ้ารอผลการทดลองนี้ ข้าเฝ้าดูพลังอาร์เคนของสถานที่แห่งนี้ลดน้อยลงมาหลายปี และเกรงว่าตอนนี้พวกเราจะเปราะบางยิ่งกว่าครั้งใด" }
assert(addon.quests[94745].progress == nil, "MAIN43 field baseline changed")
addon.quests[94745].progress = { "71:1674610545:1334869436", "ชโลมทุ่งเหล่านี้ด้วยเลือดของ Twilight! ดินแดนเหล่านี้เป็นของ Horde!" }
assert(addon.quests[94748].progress == nil, "MAIN43 field baseline changed")
addon.quests[94748].progress = { "97:1436011366:593953201", "พวก Twilight Champions น่าจะถือกุญแจกรงขังนักรบของข้าอยู่ สังหารพวกมัน แล้วปลดปล่อยคนของเรา" }
assert(addon.quests[94888].progress == nil, "MAIN43 field baseline changed")
addon.quests[94888].progress = { "98:1368931359:287323989", "หากเจ้าพบเชลยของ Horde ก็ปล่อยให้เน่าอยู่ในห้องขังไป เรื่องปวดหัวจะได้น้อยลงอีกเรื่อง" }
assert(addon.quests[94907].progress == nil, "MAIN43 field baseline changed")
addon.quests[94907].progress = { "20:707148261:988037887", "ว่าไง? เจ้าทำแล้วหรือ?" }
assert(addon.quests[94965].progress == nil, "MAIN43 field baseline changed")
addon.quests[94965].progress = { "15:185938108:1208392855", "แล้วเป็นอย่างไรบ้าง?" }
assert(addon.quests[95122].progress == nil, "MAIN43 field baseline changed")
addon.quests[95122].progress = { "157:1073619338:199341167", "ปืนใหญ่ของ Eastsea ก็เรื่องหนึ่ง ก็อบลินคนไหนก็จัดการดอกไม้ไฟไม่กี่ดอกได้ ที่ทำให้ข้ากลัวคือพวกจู่โจม พวกคลั่งน้ำลายฟูมปากที่ถือขวานหรือ? ไม่เอาล่ะขอบคุณ!" }
assert(addon.quests[93604].completion == nil, "MAIN43 field baseline changed")
addon.quests[93604].completion = { "382:1980531307:829117720", "<สีหน้าของควิลบอร์สดใสขึ้นทันทีที่เห็นขวดซึ่งเต็มไปด้วยเลือด อารมณ์ของเขารุนแรงจนหมวกเกราะที่วางหมิ่นๆอยู่เหนือหน้าผากเคลื่อนจากที่>\n\nเลือดของ Agamaggan! เจ้าได้มาแล้ว!\n...Kog'thug นึกว่าเจ้าจะตาย ไม่คิดว่าจะกลับมา ทอเรนตัวโตทำให้ Kog'thug อยู่ในสถานการณ์ยุ่งยาก\n\n<Kog'thug ลังเลก่อนจะพูดต่อ>" }
assert(addon.quests[93604].progress == nil, "MAIN43 field baseline changed")
addon.quests[93604].progress = { "57:1312359446:1632319461", "เจ้ากลับมาแล้ว? เจ้าเอาเลือดมา หรือจะให้ Kog'thug เอาเลือดจากเจ้า!" }
assert(addon.quests[96771].progress == nil, "MAIN43 field baseline changed")
addon.quests[96771].progress = { "203:346045508:414796590", "Zalfan เคยเป็นสหายที่ดีมาก แต่เขาปล่อยให้ตัวเองหลงคำสัญญาเรื่องอำนาจที่ Twilight's Hammer เสนอให้ สำหรับข้า นี่เป็นเรื่องที่ไม่อาจให้อภัย\nโลกจะไม่อาลัยเขาหรอก" }
assert(addon.quests[97536].progress == nil, "MAIN43 field baseline changed")
addon.quests[97536].progress = { "143:2042582751:1338783028", "ข้าติดป้ายที่เขียนว่าอันตรายและมีพิษไว้แล้ว... พอเจ้าหาบ้านใหม่ให้พวกมันในทะเลทรายแล้ว คนก็จะรู้ว่าต้องปล่อยพวกมันไว้เฉยๆ" }
assert(addon.quests[98096].completion == nil, "MAIN43 field baseline changed")
addon.quests[98096].completion = { "285:1285764364:751178954", "Sentinel Keldara เป็นหนึ่งในคนเก่งที่สุดของเรา ข้าขอให้พี่น้องสาวของนางสบายดี\n\nนางถูกส่งไปเฝ้าดูความเคลื่อนไหวของซาเทอร์ที่ Haldarr Encampment ทางตะวันออกเฉียงเหนือ ดูเหมือนเจ้าจะเอาตัวรอดได้ ข้าจะขอบคุณมากหากเจ้าช่วยนางทำภารกิจ\n\nเราสูญเสียคนในหน่วยไปมากกว่านี้ไม่ได้แล้ว" }
assert(addon.quests[88807].progress == nil, "MAIN43 field baseline changed")
addon.quests[88807].progress = { "84:1296622766:1454481493", "ยังมีอีกมากที่ต้องทำในการต่อสู้กับ Spitelash แต่คนช่วยกลับมีน้อย" }
assert(addon.quests[89228].completion == nil, "MAIN43 field baseline changed")
addon.quests[89228].completion = { "33:1385579967:1994320890", "เยี่ยมเลย เอาพวกนี้ไปปรุงต้องออกมาดีแน่!" }
assert(addon.quests[89228].progress == nil, "MAIN43 field baseline changed")
addon.quests[89228].progress = { "76:754939859:1565756854", "ได้ปลาหมึกนั่นมาหรือยัง? พอพูดถึงมัน ข้าก็เริ่มหิวขึ้นมานิดหน่อย" }
assert(addon.quests[91608].progress == nil, "MAIN43 field baseline changed")
addon.quests[91608].progress = { "72:770134397:2011051086", "ถ้าพวกตัวต่อรุมเจ้า อย่าวิ่งกลับมาที่นี่ Ag'tor เอาข้าตายแน่!" }
assert(addon.quests[93404].completion == nil, "MAIN43 field baseline changed")
addon.quests[93404].completion = { "365:1392084965:1135564890", "<เปลวไฟที่เคยเผาผลาญร่างวิญญาณของทรีแอนต์จางลงแล้ว แต่สายตาของเขายังว่างเปล่า เขานิ่งอยู่หลายอึดใจ ก่อนจะรับรู้ถึงการมาของเจ้า>\n\nความทรมานของข้าสิ้นสุดแล้ว ความสงบกำลังเข้ามาหาข้า\n\nไม่มีเวลาอำลา ไม่มีเวลารอคนที่ลืมข้าไปแล้ว\nนักเดินทาง ข้ามีสิ่งสุดท้ายจะบอก ความหวังสุดท้ายสำหรับภารกิจของเจ้า" }
assert(addon.quests[93404].progress == nil, "MAIN43 field baseline changed")
addon.quests[93404].progress = { "130:1707246071:166975105", "<Woodwyrd ยืนแทบไม่เคลื่อนไหว เขามองผ่านเจ้าไป เช่นเดียวกับที่เจ้าอาจเคยมองผ่านภูตผีแห่ง Shen'dralas>" }
assert(addon.quests[88884].progress == nil, "MAIN43 field baseline changed")
addon.quests[88884].progress = { "127:1037487896:1876417104", "รายละเอียดปลีกย่อยของงานเขียนชาว Highborne อาจเกินความเข้าใจของเจ้า แต่ข้าแปลให้ได้เมื่อเจ้านำแผ่นจารึกมาให้" }
assert(addon.quests[90813].completion == nil, "MAIN43 field baseline changed")
addon.quests[90813].completion = { "330:1513086030:1360429259", "โอ้โฮ เจ้าได้ของดีเข้าแล้ว! มีแต่นักสำรวจแร่ที่แข็งแกร่งที่สุดเท่านั้นที่จะหวังขุดแร่จากตัวยักษ์ได้!\nสิ่งที่เจ้าถือคือก้อน Azsharite ดิบ บริสุทธิ์กว่าที่พวกยักษ์มักจะ... ขับถ่ายออกมา หาได้ยาก และมีค่ามาก!\n\nข้ายอมจ่ายอย่างงามเพื่อมัน หากเจ้ายินดีแลกเปลี่ยน" }
assert(addon.quests[90813].progress == nil, "MAIN43 field baseline changed")
addon.quests[90813].progress = { "25:386954833:796535030", "มีอะไรจะให้ข้าดูหรือ?" }
assert(addon.quests[91497].completion == nil, "MAIN43 field baseline changed")
addon.quests[91497].completion = { "182:1582021771:659353977", "<เมื่อศึกษาตราผนึกแต่ละดวง เจ้าเห็นว่ามันตรงกับตราในตำราจริงๆ เมื่อรู้สึกถึงพลังของผลึกที่สั่นสะท้อนตอบสนองต่อตราเหล่านั้น ความคิดบ้าบิ่นก็แล่นเข้ามาในหัวเจ้า>" }
assert(addon.quests[91497].progress == nil, "MAIN43 field baseline changed")
addon.quests[91497].progress = { "59:563182302:701538808", "<ตำราเปิดอยู่ตรงหน้าเจ้า มีรายละเอียดคาถาของ Rimtori>" }
assert(addon.quests[91569].completion == nil, "MAIN43 field baseline changed")
addon.quests[91569].completion = { "83:1624189733:1963461192", "เยี่ยมมาก! พอถึงเวลานี้สัปดาห์หน้า ข้าจะรวยทองจนล้นมือแล้ว\n\nเอาล่ะ แผนก็คือ..." }
assert(addon.quests[95194].completion == nil, "MAIN43 field baseline changed")
addon.quests[95194].completion = { "114:1154078921:2021739107", "Shaw ส่งเจ้ามาสินะ? ดี ข้ายังสงสัยอยู่เลยว่า Renzik ได้รับข้อความของข้าหรือไม่ มาสิ ที่นี่คุยกันไม่ปลอดภัย" }
assert(addon.quests[95198].progress == nil, "MAIN43 field baseline changed")
addon.quests[95198].progress = { "5:1151914372:80614369", "ว่าไง?" }
assert(addon.quests[95262].completion == nil, "MAIN43 field baseline changed")
addon.quests[95262].completion = { "272:1987371313:1315377420", "<พระราชาสวรรคตแล้ว เจ้าค่อยๆตระหนักถึงผลที่จะตามมามากขึ้นเรื่อยๆ ขณะพยายามทำความเข้าใจข่าวนี้\n\nดูเหมือนยังมีพลังที่ยิ่งใหญ่กว่ามังกรที่ด้อยอำนาจกว่าซึ่งเจ้าเพิ่งสังหารคอยชักใยอยู่\n\nถึงเวลาไปแจ้งสิ่งที่เจ้ารู้ให้ Sully ทราบแล้ว>" }
assert(addon.quests[95283].completion == nil, "MAIN43 field baseline changed")
addon.quests[95283].completion = { "47:1244326616:206295256", "Eitrigg ส่งเจ้ามาหรือ? หมาป่าแก่นั่นต้องการอะไร?" }
assert(addon.quests[95285].completion == nil, "MAIN43 field baseline changed")
addon.quests[95285].completion = { "134:636993564:994229756", "รายละเอียดภารกิจที่เหลือจะบอกเฉพาะผู้ที่จำเป็นต้องรู้ และเจ้าจำเป็นต้องรู้แค่นี้ ดังนั้น พร้อมทำหน้าที่ต่อจอมทัพของเจ้าหรือยัง?" }
assert(addon.quests[95285].progress == nil, "MAIN43 field baseline changed")
addon.quests[95285].progress = { "23:1454545945:970873987", "มีคำถามไหมทหารใหม่?" }
assert(addon.quests[95309].completion == nil, "MAIN43 field baseline changed")
addon.quests[95309].completion = { "252:1137695317:1836939107", "ถ้าอย่างนั้น Ulka รอดมาได้แล้วส่งเจ้าเข้ามาตามข้าสินะ? เจ้าพบนางอยู่ท่ามกลางศพมากมายหรือ? Ulka สร้างชื่อให้ Kor'kron และข้าจะดูแลให้นางได้เลื่อนยศในสนามรบเมื่อเราเสร็จธุระที่นี่\n\nแต่เรายังไปไม่ได้ ภารกิจของเรายังไม่เสร็จ" }
assert(addon.quests[95309].progress == nil, "MAIN43 field baseline changed")
addon.quests[95309].progress = { "25:1612441610:883444161", "อะ... อะไรนะ? Ulka ยังมีชีวิตอยู่หรือ?" }
assert(addon.quests[95454].completion == nil, "MAIN43 field baseline changed")
addon.quests[95454].completion = { "165:1643474509:1667077191", "<ดูเหมือนยังมีพลังที่ยิ่งใหญ่กว่ามังกรที่ด้อยอำนาจกว่าซึ่งเจ้าเพิ่งสังหารคอยชักใยอยู่ ถึงเวลาไปแจ้งสิ่งที่เจ้ารู้ให้ Commander Folkar ทราบแล้ว>" }
assert(addon.quests[95454].progress == nil, "MAIN43 field baseline changed")
addon.quests[95454].progress = { "127:804655152:352470488", "<แม้กลิ่นน้ำหอมจากกระดาษโน้ตจะหอมหวาน แต่ก็มีความผิดแปลกที่เหมือนถูกปรุงแต่งอยู่ด้วย มันไม่ชวนให้รู้สึกดี>" }
assert(addon.quests[96332].progress == nil, "MAIN43 field baseline changed")
addon.quests[96332].progress = { "18:1544470965:59821606", "เลือดและอสนีบาต!" }
assert(addon.quests[96334].completion == nil, "MAIN43 field baseline changed")
addon.quests[96334].completion = { "241:1745569194:1600537363", "ขอบคุณที่นำผ้าโพกเหล่านี้มาให้ข้า ข้าไม่สงสัยเลยว่ามันเป็นหน้ากากของ Defias Brotherhood เราเคยสงสัยว่าพวกมันเป็นผู้ดำเนินการคุกบน Alcaz และนี่ก็ยืนยันแล้ว\n\nข้าจะแจ้ง Thrall เรื่องนี้" }
assert(addon.quests[96335].completion == nil, "MAIN43 field baseline changed")
addon.quests[96335].completion = { "198:1202723733:984065387", "พอถอดตรวนออกแล้วรู้สึกดีจริงๆ ข้าจำไม่ได้ด้วยซ้ำว่าถูกล่ามมานานเท่าไร ตอนนี้ข้าแค่ต้องการโรงเตี๊ยม อาบน้ำ โกนหนวด... และความรู้สึกยามสวมสูท\n\nอาจตัดผมด้วย รู้สึกโทรมนิดหน่อย" }
assert(addon.quests[96335].progress == nil, "MAIN43 field baseline changed")
addon.quests[96335].progress = { "73:1999373792:1833852683", "เราเลิกคุยไร้สาระแล้วมุ่งช่วยข้าออกจากที่นี่กันดีไหม!" }
assert(addon.quests[96337].completion == nil, "MAIN43 field baseline changed")
addon.quests[96337].completion = { "502:1839948737:509694051", "<เจ้าพบหีบที่เต็มไปด้วยเอกสาร แผนที่ และวัสดุอื่นๆ เห็นตราของ Stormwind, Gilneas, Lordaeron และตราอื่นๆที่ดูเป็นทางการแต่เจ้าไม่คุ้นเคย\nเนื้อหาส่วนใหญ่ในเอกสารเหล่านี้ไม่ค่อยมีความหมายสำหรับเจ้า เจ้าเห็นแผนที่สถานที่ชื่อ Kalidar ภาพวาดพร่าเลือนของสิ่งที่ดูเหมือนยักษ์เพศหญิง และรายงานสำรวจที่ถูกเผาไปบางส่วน ติดป้ายว่า 'A. Crater; Kalimdor'\n\nเจ้าไม่ค่อยเข้าใจมัน แต่ของพวกนี้อาจมีค่ากับใครสักคนก็ได้?>" }
assert(addon.quests[96337].progress == nil, "MAIN43 field baseline changed")
addon.quests[96337].progress = { "110:1419615134:248750835", "<เจ้าพบหีบสีทองใบเล็กฝังอยู่ในหลุมตื้นบนพื้นดิน ไม่ว่าข้างในจะมีอะไร ก็ไม่ใช่ของชิ้นใหญ่>" }
assert(addon.quests[96369].completion == nil, "MAIN43 field baseline changed")
addon.quests[96369].completion = { "462:1652003147:1994611501", "ถ้าอย่างนั้น Wrynn ก็ตายแล้วสินะ...\nข้าจะไว้ทุกข์ให้นักรบที่ตายที่นี่ แต่ความตายของพวกเขาไม่สูญเปล่า เรารู้มากกว่าแต่ก่อน และความรู้เช่นนี้มีค่า Stormwind... ไม่สิ แม้แต่ Alliance เองก็ไม่เคยเปราะบางเท่านี้มาก่อน และการรู้เรื่องนี้ก็ทรงพลัง\n\nขอบคุณที่รับใช้ Horde ในส่วนตัวข้า ข้ายังติดค้างชีวิตเจ้าด้วย เป็นหนี้ที่ข้าจะไม่ลืมง่ายๆ ข้าจะหาทางออกจากที่นี่ และไปดูแล Sergeant Ulka ด้วยตัวเอง" }
assert(addon.quests[96377].completion == nil, "MAIN43 field baseline changed")
addon.quests[96377].completion = { "367:1259381735:915727728", "<Renzik เบิกตากว้างเมื่อเจ้าให้เขาดูกล่องเอกสารที่กู้มาจาก Westfall>\n\nเจ้าว่าได้ของพวกนี้มาจากไหนนะ? พบใต้กระดานพื้นในอาคารสักแห่งหรือ? ได้เลยสหาย... ตามที่เจ้าว่า\nเอ้า รับนี่เป็นรางวัลสำหรับ เอ่อ การรับใช้ของเจ้า... และจะได้ปิดปากเรื่องเอกสารเหล่านี้ รวมถึงสิ่งใดที่เจ้าอ่านหากแอบเปิดดู" }
assert(addon.quests[96377].progress == nil, "MAIN43 field baseline changed")
addon.quests[96377].progress = { "178:1663834445:886672754", "<เจ้าคิดขึ้นได้ว่าก็อบลินมือขวาของ Shaw อาจสนใจเอกสารที่เจ้าได้มาจาก Westfall ลองถามเขาดูว่าอ่านเอกสารเหล่านี้แล้วพอเข้าใจอะไรบ้างไหม>" }
assert(addon.quests[96379].completion == nil, "MAIN43 field baseline changed")
addon.quests[96379].completion = { "496:1806719149:1562478652", "<Rix เริ่มน้ำลายสออย่างเห็นได้ชัด ขณะมองของในกล่องเอกสารที่เจ้ากู้มาจาก Westfall>\nคอหอยของ Gallywix เอ๋ย สหาย นี่อาจเป็นขุมทรัพย์มหาศาล... เอ่อ ข้าหมายถึง อืม นี่ก็แค่ขยะชัดๆ เจ้าอาจต้องจ่ายให้ข้าช่วยกำจัดขยะพวกนี้ด้วยซ้ำ\n\nเอาอย่างนี้สหาย รับนี่ตอบแทนความพยายาม แล้วข้าจะจัดการของพวกนี้ให้ อย่าพยายามต่อราคาข้าด้วยล่ะ จริงๆข้าแค่ช่วยรับขยะไร้ประโยชน์ไปจากมือเจ้าเท่านั้น" }
assert(addon.quests[96379].progress == nil, "MAIN43 field baseline changed")
addon.quests[96379].progress = { "265:291930116:418846620", "<เจ้าคิดได้ว่ากอบลินที่ทำธุรกิจตามเอาทรัพย์สินคืนอาจอยากเห็นเอกสารที่เจ้าได้มาจาก Westfall ลองถามเขาว่าพอจะเข้าใจเอกสารพวกนี้บ้างไหม ที่สำคัญกว่านั้นคือเขายอมจ่ายเท่าไรถึงจะได้มันไป>" }
assert(addon.quests[96772].progress == nil, "MAIN43 field baseline changed")
addon.quests[96772].progress = { "28:1276839837:1251014496", "เจ้านำบันทึกกลับมาได้หรือยัง?" }
assert(addon.quests[86577].completion == nil, "MAIN43 field baseline changed")
addon.quests[86577].completion = { "279:151619508:1420131525", "อา ตัวอย่างพวกนี้... เหนียวเยิ้มทีเดียว\n\nเห็นไหมว่าพวกมันเต็มไปด้วยเนื้องอกและตุ่มหนอง? สัตว์เหล่านี้ทุกข์ทรมานอย่างแสนสาหัส ไม่ต้องสงสัยเลยว่านั่นทำให้พวกมันก้าวร้าว\nแต่ข้าไม่รู้วิธีรักษา ข้าสงสัยว่าวิธีแก้อยู่ที่ Hyjal ส่วนเราเพียงรับผลพวงจากมัน" }
assert(addon.quests[86577].progress == nil, "MAIN43 field baseline changed")
addon.quests[86577].progress = { "100:1721296095:806952714", "เราต้องค้นหาต้นตอของความแปดเปื้อนที่กำลังเปลี่ยน Felwood ให้เป็นป่าร้างอันเต็มไปด้วยปีศาจ!" }
assert(addon.quests[86611].completion == nil, "MAIN43 field baseline changed")
addon.quests[86611].completion = { "326:642772467:1262649708", "ข้าจำผลึกนี้ได้! รูปปั้นของ Malorne เคยประดับศาลของเขา แต่พวกปีศาจคงโยนมันลงจากไหล่เขาระหว่างสงคราม\n\nน่าเสียดาย ผลึกดูดซับพลังเฟลเข้าไป และตอนนี้ก็มีพลังอัปมงคลอยู่ส่วนหนึ่ง ข้าเกรงว่าต้องทำลายมัน\n\nขอบคุณที่นำสิ่งนี้มาให้ข้า" }
assert(addon.quests[86611].progress == nil, "MAIN43 field baseline changed")
addon.quests[86611].progress = { "13:597341597:1707287510", "นั่นอะไร?" }
assert(addon.quests[88812].completion == nil, "MAIN43 field baseline changed")
addon.quests[88812].completion = { "97:860789267:1153534936", "ทำได้ดีมาก เมื่อพลังของหินพลังถูกลบล้าง เวทมนตร์ของ Spitelash ก็น่าจะอ่อนลงมาก" }
assert(addon.quests[88812].progress == nil, "MAIN43 field baseline changed")
addon.quests[88812].progress = { "175:523853493:448948096", "ข้ายอมรับว่าภารกิจของเจ้าที่อนุสาวรีย์ Ravencrest เป็นเรื่องยุทธวิธีพอๆกับการอนุรักษ์ การสูญเสียความทรงจำของตระกูล Kaldorei อันสูงศักดิ์เช่นนี้ คงเป็นโศกนาฏกรรม" }
assert(addon.quests[88813].progress == nil, "MAIN43 field baseline changed")
addon.quests[88813].progress = { "109:495401099:1582838030", "ตอนนี้ไม่มีอะไรจะพูดมากไปกว่าให้รีบไปเถอะนักรบ ภารกิจของเจ้าสำคัญยิ่ง โชคดี" }
assert(addon.quests[90750].completion == nil, "MAIN43 field baseline changed")
addon.quests[90750].completion = { "192:1646609816:1668927856", "<Daythor หัวเราะเบาๆพร้อมส่ายศีรษะช้าๆ>\n\nดูเหมือนแม้แต่เจ้าก็ไม่อาจขัดขวางสหายของเราตรงนี้จากการทำตามจุดประสงค์ของตน น่าเสียดายจริง... แต่อย่างน้อยสหายเราก็ดูมีความสุข" }
assert(addon.quests[90750].progress == nil, "MAIN43 field baseline changed")
addon.quests[90750].progress = { "4:1517439344:201828488", "ว่าอย่างไร?" }
assert(addon.quests[91538].completion == nil, "MAIN43 field baseline changed")
addon.quests[91538].completion = { "92:1727110282:672110444", "เอาล่ะ บางทีความพยายามหยุมหยิมของ Belgrom เพื่อความมั่งคั่งและการแก้แค้นอาจไม่ได้สูญเปล่าไปทั้งหมด..." }
assert(addon.quests[91547].completion == nil, "MAIN43 field baseline changed")
addon.quests[91547].completion = { "108:685329426:1868143451", "<Zevrost เบิกตากว้างเมื่อเห็นตำรา เขารีบมองไปรอบๆ>\n\nมีใครอื่นรู้ไหมว่าเจ้ามีสิ่งนี้?" }
assert(addon.quests[91547].progress == nil, "MAIN43 field baseline changed")
addon.quests[91547].progress = { "39:1005796717:989275246", "Jediga ส่งเจ้ามาหรือ? นี่คงน่าสนใจแน่" }
assert(addon.quests[91952].completion == nil, "MAIN43 field baseline changed")
addon.quests[91952].completion = { "344:1479257063:1540343884", "Greta พูดถูก การทำลาย Archimonde ตอนจบสงคราม ทำให้เถ้าปนเปื้อนเฟลโปรยไปทั่วภูเขา แม้ข้าจะพยายามฟื้นฟูภูมิประเทศอยู่ แต่ก็คืบหน้าช้า ธรรมชาติจะกลับมาครอบครองพื้นที่อีกครั้งในที่สุด แต่กระบวนการนี้อาจกินเวลาหลายปี\n\nถึงอย่างนั้น ก็ดีที่รู้ว่ายังมีผู้คนอื่นที่ใส่ใจ" }
assert(addon.quests[92020].completion == nil, "MAIN43 field baseline changed")
addon.quests[92020].completion = { "337:1413286847:2050895397", "หนังสือภาพร่างกับบันทึกเกี่ยวกับ... กิ้งก่ายักษ์ใน Un'Goro Crater หรือ?\n\nเอาตรงๆ ข้าไม่รู้ว่าตอนนี้จะมีใครมีเวลาอ่านไหม แต่ผู้เขียนช่างสังเกต โดยเฉพาะภาพร่างที่ทั้งมีประโยชน์และให้ข้อมูลได้ดี\n\nขอบคุณที่นำมาส่ง ข้าจะดูแลให้มันถูกเพิ่มเข้าไปในห้องสมุดความรู้เรื่องโลกธรรมชาติของเหล่าดรูอิด" }
assert(addon.quests[92020].progress == nil, "MAIN43 field baseline changed")
addon.quests[92020].progress = { "17:1972634882:1176836437", "หนังสือนี่อะไร?" }
assert(addon.quests[92066].completion == nil, "MAIN43 field baseline changed")
addon.quests[92066].completion = { "127:85349498:81649986", "สรรเสริญเหล่าวิญญาณ! โทเท็มยังไม่แตกหัก แม้พวก Blackmaw จะสูญเสียไปมาก แต่เรื่องราวของเราจะคงอยู่ ขอบคุณนะทอเรน" }
assert(addon.quests[92066].progress == nil, "MAIN43 field baseline changed")
addon.quests[92066].progress = { "88:1510341637:778673906", "ข้าเข้าใจว่าทำไมเราต้องทิ้งโทเท็มไว้ ข้าแค่หวังว่าพวกซาเทอร์จะยังไม่ทำให้พวกมันเสียโฉม" }
assert(addon.quests[92070].progress == nil, "MAIN43 field baseline changed")
addon.quests[92070].progress = { "65:2146896604:529651575", "เจ้ารู้ไหมว่าลูกน้อยของข้าอยู่ไหน? ได้โปรด บอกอะไรข้าสักอย่าง! อะไรก็ได้!" }
assert(addon.quests[92343].progress == nil, "MAIN43 field baseline changed")
addon.quests[92343].progress = { "109:1762412313:831963342", "ปกติข้าไม่ใช่คนที่จะฉวยประโยชน์จากสถานการณ์เช่นนี้ แต่เราปล่อยโอกาสนี้ให้ผ่านไปไม่ได้" }
assert(addon.quests[92344].progress == nil, "MAIN43 field baseline changed")
addon.quests[92344].progress = { "191:2109244262:943493261", "ข้าเห็นใจพวกเฟอร์โบลก์ และอยากให้การค้นพบของเจ้าเกิดขึ้นภายใต้สถานการณ์ที่ดีกว่านี้ แต่พูดตามตรง เราพลาดโอกาสดึงพลังของ Nordrassil มาใช้ไม่ได้" }
assert(addon.quests[92345].completion == nil, "MAIN43 field baseline changed")
addon.quests[92345].completion = { "70:1833271011:1613883311", "เจ้าว่ามีอุโมงค์ใต้ Nordrassil หรือ? เจ้าทำให้ข้าสนใจจริงๆ" }
assert(addon.quests[92346].completion == nil, "MAIN43 field baseline changed")
addon.quests[92346].completion = { "69:661765951:244730007", "เจ้าพบอุโมงค์ใต้ต้นไม้โลกหรือ? เอาล่ะ ข้าฟังอยู่" }
assert(addon.quests[92842].completion == nil, "MAIN43 field baseline changed")
addon.quests[92842].completion = { "51:1086531304:308853728", "พอคิดย้อนดู การมาที่นี่น่าจะเป็นความคิดที่ไม่ดี" }
assert(addon.quests[97197].progress == nil, "MAIN43 field baseline changed")
addon.quests[97197].progress = { "100:1051087708:1528432387", "ความคิดเรื่องยักษ์สูงตระหง่านที่มีร่างเป็นหินหลอมเหลวล้วนๆ ทำให้ข้าทั้งตื่นเต้นและหวาดกลัว" }
assert(addon.quests[97319].completion == nil, "MAIN43 field baseline changed")
addon.quests[97319].completion = { "51:1086531304:308853728", "พอคิดย้อนดู การมาที่นี่น่าจะเป็นความคิดที่ไม่ดี" }
