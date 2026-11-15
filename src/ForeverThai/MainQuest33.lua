-- MAIN33 own-ID literal progress;reviewed exact-source reuse,no condition or identity inference.
local _, addon = ...
assert(type(addon.quests[97928]) == "table" and addon.quests[97928].progress == nil, "MAIN33 baseline changed")
addon.quests[97928].progress = { "21:597269750:1281937852", "ใช่ ข้าสอนเจ้าได้" }
