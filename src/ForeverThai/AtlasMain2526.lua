-- MAIN25/26 additive run aliases and bounded shaped words. Existing Atlas is unchanged.
local _, addon = ...
assert(addon.runs["ข้าจะให้ส่วนที่เหลือเมื่อเจ้านำของที่ข้าสั่งมาให้ข้าจนครบ"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["ข้าจะให้ส่วนที่เหลือเมื่อเจ้านำของที่ข้าสั่งมาให้ข้าจนครบ"] = { 1088, 2125, 12124, 8341, 3937, 11016, 10507, 9731, 4304, 839, 3937, 1088, 8010, 6089, 12124, 1088, 2076, 1228 }
assert(addon.glyphs[14334] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14334] = { 98, 2, 2, 78, 0, 77.14 }
assert(addon.runs["ข้าจัดหาระเบิดให้เจ้าใช้ฝ่าประตูเข้าไปได้"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["ข้าจัดหาระเบิดให้เจ้าใช้ฝ่าประตูเข้าไปได้"] = { 1088, 14334, 6694, 12124, 9731, 12042, 5491, 4828, 9506, 12248, 12197 }
assert(addon.glyphs[14335] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14335] = { 98, 84, 2, 40, 0, 39.3 }
assert(addon.glyphs[14336] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14336] = { 98, 128, 2, 63, 0, 62.45 }
assert(addon.runs["คนอื่นแถวนี้สักคนต้องมีติดตัวอยู่แน่ๆ"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["คนอื่นแถวนี้สักคนต้องมีติดตัวอยู่แน่ๆ"] = { 1143, 9224, 11331, 4355, 14335, 1143, 3455, 6149, 3319, 8958, 14336 }
assert(addon.runs["คนเดียวงั้นหรือ"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["คนเดียวงั้นหรือ"] = { 1201, 2010, 8597 }
assert(addon.glyphs[14337] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14337] = { 98, 195, 2, 35, 0, 34.34 }
assert(addon.glyphs[14338] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14338] = { 98, 234, 2, 104, 0, 104.0 }
assert(addon.runs["จงกำจัดพวกมัน"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["จงกำจัดพวกมัน"] = { 14337, 610, 14338 }
assert(addon.glyphs[14339] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14339] = { 98, 342, 2, 180, 0, 179.27 }
assert(addon.glyphs[14340] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14340] = { 98, 526, 2, 79, 0, 78.2 }
assert(addon.runs["ต้องมากพอให้ข้าได้ทดสอบประสิทธิภาพของแต่ละแบบ"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["ต้องมากพอให้ข้าได้ทดสอบประสิทธิภาพของแต่ละแบบ"] = { 3455, 6090, 5623, 12124, 1088, 12197, 3622, 14339, 839, 14340, 11393 }
assert(addon.runs["ทำให้บ้านของข้าแปดเปื้อน"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["ทำให้บ้านของข้าแปดเปื้อน"] = { 3901, 4741, 839, 1088, 11418 }
assert(addon.runs["ทุกนาทีที่พวก"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["ทุกนาทีที่พวก"] = { 4013, 4275, 3937, 5617 }
assert(addon.glyphs[14341] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14341] = { 98, 609, 2, 116, 0, 115.84 }
assert(addon.runs["นี่คือส่วนแบ่งของเจ้าบางส่วน"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["นี่คือส่วนแบ่งของเจ้าบางส่วน"] = { 4352, 1869, 14341, 839, 9731, 4638 }
assert(addon.glyphs[14342] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14342] = { 98, 729, 2, 39, 0, 38.14 }
assert(addon.runs["ระเบิดที่ข้าสั่งไว้นี่นา"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["ระเบิดที่ข้าสั่งไว้นี่นา"] = { 6694, 3937, 1088, 8010, 12358, 4352, 14342 }
assert(addon.glyphs[14343] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14343] = { 98, 772, 2, 59, 0, 58.78 }
assert(addon.glyphs[14344] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14344] = { 98, 835, 2, 107, 0, 106.98 }
assert(addon.glyphs[14345] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14345] = { 98, 2, 62, 83, 0, 83.0 }
assert(addon.runs["ล้วนเป็นการลบหลู่ความทรงจำเกี่ยวกับบ้านแห่งนี้"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["ล้วนเป็นการลบหลู่ความทรงจำเกี่ยวกับบ้านแห่งนี้"] = { 14343, 14344, 14345, 1435, 9430, 4741, 11680, 4355 }
assert(addon.runs["อย่างน้อยก็ได้มาลูกหนึ่ง"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["อย่างน้อยก็ได้มาลูกหนึ่ง"] = { 8971, 4452, 703, 6089, 7251, 8428 }
assert(addon.runs["เจ้าบอกว่าจะบุกเข้าไปใน"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["เจ้าบอกว่าจะบุกเข้าไปใน"] = { 9731, 4577, 284, 2125, 4684, 9561, 12073 }
assert(addon.runs["เจ้าลดจำนวนพวกมันลงบ้างหรือยัง"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["เจ้าลดจำนวนพวกมันลงบ้างหรือยัง"] = { 9731, 7040, 2194, 5617, 6063, 7010, 4740, 8598 }
assert(addon.glyphs[14346] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14346] = { 98, 89, 62, 59, 0, 58.38 }
assert(addon.runs["แต่ข้าต้องการชุดคละแบบ"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["แต่ข้าต้องการชุดคละแบบ"] = { 11298, 1088, 3457, 2542, 14346, 11393 }
assert(addon.glyphs[14347] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14347] = { 98, 152, 62, 105, 0, 104.91 }
assert(addon.glyphs[14348] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14348] = { 98, 261, 62, 71, 0, 70.77 }
assert(addon.glyphs[14349] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14349] = { 98, 336, 62, 109, 0, 108.48 }
assert(addon.runs["แต่ข้าต้องมีใบสั่งงานเพื่อให้รายการในบัญชีดูถูกต้องตามระเบียบ"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["แต่ข้าต้องมีใบสั่งงานเพื่อให้รายการในบัญชีดูถูกต้องตามระเบียบ"] = { 11298, 1088, 3455, 6149, 12091, 8012, 10448, 14347, 12073, 14348, 2906, 3584, 3245, 14349 }
assert(addon.glyphs[14350] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14350] = { 98, 449, 62, 72, 0, 71.84 }
assert(addon.runs["และยังเหลือไว้ใช้เองอีกสักหน่อยด้วย"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["และยังเหลือไว้ใช้เองอีกสักหน่อยด้วย"] = { 11597, 6340, 14350, 12358, 12042, 11077, 9197, 7956, 2941 }
assert(addon.runs["แล้วทวงคืนสิ่งที่เป็นของเรา"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["แล้วทวงคืนสิ่งที่เป็นของเรา"] = { 11603, 3663, 1859, 8141, 3937, 10224, 839, 10577 }
assert(addon.glyphs[14351] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14351] = { 98, 525, 62, 90, -2, 87.55 }
assert(addon.glyphs[14352] == nil, "MAIN25/26 Atlas baseline mismatch")
addon.glyphs[14352] = { 98, 619, 62, 49, 0, 48.97 }
assert(addon.runs["ใจกล้าไม่เบาเลยนี่"] == nil, "MAIN25/26 run baseline mismatch")
addon.runs["ใจกล้าไม่เบาเลยนี่"] = { 14351, 12274, 14352, 10667, 4352 }
