-- MAIN35 additive bitmap data;exact retained Sarabun shaping and reviewed word boundaries.
local _, addon = ...
assert(addon.glyphs[14477] == nil, "MAIN35 glyph baseline changed")
addon.glyphs[14477] = { 101, 2, 2, 124, 0, 123.72 }
assert(addon.glyphs[14478] == nil, "MAIN35 glyph baseline changed")
addon.glyphs[14478] = { 101, 130, 2, 103, 0, 102.41 }
assert(addon.glyphs[14479] == nil, "MAIN35 glyph baseline changed")
addon.glyphs[14479] = { 101, 237, 2, 140, 0, 138.98 }
assert(addon.runs["ตรวจดูโคโดหุ้มเกราะเพื่อเลือกพาหนะระดับมหากาพย์ของเจ้า"] == nil, "MAIN35 run baseline changed")
addon.runs["ตรวจดูโคโดหุ้มเกราะเพื่อเลือกพาหนะระดับมหากาพย์ของเจ้า"] = { 3020, 11722, 11782, 14477, 10437, 10711, 14478, 6650, 14479, 839, 9731 }
assert(addon.runs["แล้วนำทั้งหมดไปให้"] == nil, "MAIN35 run baseline changed")
addon.runs["แล้วนำทั้งหมดไปให้"] = { 11603, 4304, 3766, 12248, 12124 }
