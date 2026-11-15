-- MAIN25 reviewed literals only. Cloud must add bitmap coverage before packaging.
local _, addon = ...
assert(addon.quests[94829].progress == nil, "MAIN25 baseline changed")
addon.quests[94829].progress = { "123:1004955921:428165482", "ทุกนาทีที่พวก Twilight Raiders ทำให้บ้านของข้าแปดเปื้อน ล้วนเป็นการลบหลู่ความทรงจำเกี่ยวกับบ้านแห่งนี้ จงกำจัดพวกมัน แล้วทวงคืนสิ่งที่เป็นของเรา" }
assert(type(addon.quests[94236].completion) == "table", "MAIN25 canonical missing")
addon.quests[94236].completion.variants = addon.quests[94236].completion.variants or {}
table.insert(addon.quests[94236].completion.variants, { "281:1740501113:411929229", "เฮ้ ระเบิดที่ข้าสั่งไว้นี่นา!\n\nเอาเถอะ อย่างน้อยก็ได้มาลูกหนึ่ง แต่ข้าต้องการชุดคละแบบ! ต้องมากพอให้ข้าได้ทดสอบประสิทธิภาพของแต่ละแบบ และยังเหลือไว้ใช้เองอีกสักหน่อยด้วย!\n\nช่างเถอะ นี่คือส่วนแบ่งของเจ้าบางส่วน--ข้าจะให้ส่วนที่เหลือเมื่อเจ้านำของที่ข้าสั่งมาให้ข้าจนครบ!" })
