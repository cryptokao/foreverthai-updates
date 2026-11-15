-- MAIN40 exact retained Sarabun shaping; additive reviewed word boundaries.
local _, addon = ...
assert(addon.glyphs[14600] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14600] = { 105, 2, 2, 35, -1, 33.53 }
assert(addon.glyphs[14601] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14601] = { 105, 41, 2, 64, 0, 63.72 }
assert(addon.glyphs[14602] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14602] = { 105, 109, 2, 81, 0, 80.64 }
assert(addon.glyphs[14603] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14603] = { 105, 194, 2, 36, 0, 35.94 }
assert(addon.glyphs[14604] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14604] = { 105, 234, 2, 100, 0, 99.14 }
assert(addon.glyphs[14605] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14605] = { 105, 338, 2, 82, 0, 81.56 }
assert(addon.glyphs[14606] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14606] = { 105, 424, 2, 62, 0, 61.17 }
assert(addon.glyphs[14607] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14607] = { 105, 490, 2, 102, 0, 101.69 }
assert(addon.glyphs[14608] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14608] = { 105, 596, 2, 47, 0, 46.14 }
assert(addon.glyphs[14609] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14609] = { 105, 647, 2, 130, 0, 129.92 }
assert(addon.glyphs[14610] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14610] = { 105, 781, 2, 60, 0, 59.36 }
assert(addon.glyphs[14611] == nil, "MAIN40 glyph baseline changed")
addon.glyphs[14611] = { 105, 845, 2, 100, 0, 99.23 }
assert(addon.runs["ไนต์เอลฟ์ตัวโตอยากได้สร้อยหรือ"] == nil, "MAIN40 run baseline changed")
addon.runs["ไนต์เอลฟ์ตัวโตอยากได้สร้อยหรือ"] = { 12245, 3475, 3156, 14600, 8954, 12197, 7834, 8597 }
assert(addon.runs["แต่ไนต์เอลฟ์ตัวโตเอาไปไม่ได้"] == nil, "MAIN40 run baseline changed")
addon.runs["แต่ไนต์เอลฟ์ตัวโตเอาไปไม่ได้"] = { 11298, 12245, 3475, 3156, 14600, 11093, 12248, 12274, 12197 }
assert(addon.runs["ต้องใช้สร้อย"] == nil, "MAIN40 run baseline changed")
addon.runs["ต้องใช้สร้อย"] = { 3455, 12042, 7834 }
assert(addon.runs["ผืนดินตายสนิท"] == nil, "MAIN40 run baseline changed")
addon.runs["ผืนดินตายสนิท"] = { 5243, 3286, 14601 }
assert(addon.runs["ไม่มีสร้อย"] == nil, "MAIN40 run baseline changed")
addon.runs["ไม่มีสร้อย"] = { 12274, 6149, 7834 }
assert(addon.runs["หนามก็ไม่งอก"] == nil, "MAIN40 run baseline changed")
addon.runs["หนามก็ไม่งอก"] = { 14602, 696, 12274, 2000 }
assert(addon.runs["เซนทอร์ย่ำเข้ามาตรงที่หนามไม่งอก"] == nil, "MAIN40 run baseline changed")
addon.runs["เซนทอร์ย่ำเข้ามาตรงที่หนามไม่งอก"] = { 9831, 3695, 14603, 9506, 6089, 3002, 3937, 14602, 12274, 2000 }
assert(addon.runs["เห็นปัญหาหรือยัง"] == nil, "MAIN40 run baseline changed")
addon.runs["เห็นปัญหาหรือยัง"] = { 11050, 5020, 8597, 6340 }
assert(addon.runs["หรือไนต์เอลฟ์ตัวโตตาบอด"] == nil, "MAIN40 run baseline changed")
addon.runs["หรือไนต์เอลฟ์ตัวโตตาบอด"] = { 8597, 12245, 3475, 3156, 14600, 14604 }
assert(addon.runs["หยุดพูดพล่ามด้วยท่าทีดูแคลน"] == nil, "MAIN40 run baseline changed")
addon.runs["หยุดพูดพล่ามด้วยท่าทีดูแคลน"] = { 8580, 5782, 14605, 2941, 14606, 14607 }
assert(addon.runs["แล้วพ่นลมหายใจทางจมูกอย่างครุ่นคิด"] == nil, "MAIN40 run baseline changed")
addon.runs["แล้วพ่นลมหายใจทางจมูกอย่างครุ่นคิด"] = { 11603, 14608, 14609, 3773, 14610, 8971, 14611 }
assert(addon.runs["อยากแลกกันไหม"] == nil, "MAIN40 run baseline changed")
addon.runs["อยากแลกกันไหม"] = { 8954, 11592, 345, 12376 }
