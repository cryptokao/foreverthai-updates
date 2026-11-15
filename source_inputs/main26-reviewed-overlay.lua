-- MAIN26 source-only overlay; Cloud bitmap integration required before packaging.
local _, addon = ...
assert(addon.quests[92457].progress == nil, "MAIN26 baseline changed")
addon.quests[92457].progress = { "35:897290514:1476474022", "เจ้าลดจำนวนพวกมันลงบ้างหรือยัง?" }
assert(type(addon.quests[78270].progress) == "table", "MAIN26 canonical missing")
addon.quests[78270].progress.variants = addon.quests[78270].progress.variants or {}
table.insert(addon.quests[78270].progress.variants, { "261:320399700:326419650", "เจ้าบอกว่าจะบุกเข้าไปใน Shadowfang...คนเดียวงั้นหรือ? ใจกล้าไม่เบาเลยนี่!\n\nข้าจัดหาระเบิดให้เจ้าใช้ฝ่าประตูเข้าไปได้ แต่ข้าต้องมีใบสั่งงานเพื่อให้รายการในบัญชีดูถูกต้องตามระเบียบ คนของ Venture Co. คนอื่นแถวนี้สักคนต้องมีติดตัวอยู่แน่ๆ" })
