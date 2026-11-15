local _, addon = ...

local classes = {
    WARRIOR = "นักรบ", PALADIN = "พาลาดิน", HUNTER = "พราน",
    ROGUE = "โจร", PRIEST = "นักบวช", SHAMAN = "ชาแมน",
    MAGE = "จอมเวท", WARLOCK = "วอร์ล็อก", DRUID = "ดรูอิด",
}
local races = {
    ["Dwarf"] = "คนแคระ", ["Gnome"] = "โนม", ["Human"] = "มนุษย์",
    ["Night Elf"] = "ไนต์เอลฟ์", ["Orc"] = "ออร์ค", ["Skyborne"] = "สกายบอร์น",
    ["Tauren"] = "ทอเรน", ["Troll"] = "โทรลล์", ["Undead"] = "อันเดด",
    ["High Order Skyborne"] = "สกายบอร์นฝ่ายไฮออร์เดอร์",
    ["Windshaper Skyborne"] = "สกายบอร์นฝ่ายวินด์เชเปอร์",
}
local shortRaces = {
    ["High Order Skyborne"] = "Skyborne",
    ["Windshaper Skyborne"] = "Skyborne",
}

local function counter(value)
    if #value:gsub(",", "") > 18 then return false end
    if not value:find(",", 1, true) then return value:match("^[0-9]+$") ~= nil end
    local first, tail = value:match("^([0-9]+)(,.*)$")
    if not first or #first > 3 then return false end
    for group in tail:gmatch(",([^,]*)") do
        if not group:match("^[0-9][0-9][0-9]$") then return false end
    end
    return true
end

-- Capture only numbers present in the incoming full source. No world-state
-- API, saved number, guessed total, or numeric conversion supplies the value.
local function matches(signature, source, tokens)
    local pos, captures = 1, {}
    for segment in signature:gmatch("%S+") do
        local worldID = segment:match("^W([0-9]+)$")
        if worldID then
            local value = source:sub(pos):match("^([0-9][0-9,]*)")
            -- A comma immediately after a counter can be punctuation. Leave
            -- one trailing comma for the following literal span to verify.
            if value and value:sub(-1) == "," then value = value:sub(1, -2) end
            if not value or not counter(value) then return false end
            local key = "world" .. worldID
            if captures[key] and captures[key] ~= value then return false end
            captures[key] = value
            pos = pos + #value
        elseif segment == "N" or segment == "U" or segment == "C" or segment == "R" then
            local wanted = tokens[segment == "U" and "N" or segment]
            if type(wanted) ~= "string" or wanted == "" then return false end
            if segment == "U" then
                -- Captures establish uppercasing for ASCII character names.
                if not wanted:match("^[A-Za-z]+$") then return false end
                wanted = wanted:upper()
            end
            local actual = source:sub(pos, pos + #wanted - 1)
            if segment == "C" or segment == "R" then actual, wanted = actual:lower(), wanted:lower() end
            if actual ~= wanted then return false end
            pos = pos + #wanted
        else
            local length, hashA, hashB = segment:match("^(%d+):(%d+):(%d+)$")
            if not length then return false end
            local stop = pos + tonumber(length) - 1
            if stop > #source then return false end
            local a, b = 0, 0
            for i = pos, stop do
                local byte = source:byte(i)
                a = (a * 257 + byte) % 2147483647
                b = (b * 131 + byte) % 2147483629
            end
            if a ~= tonumber(hashA) or b ~= tonumber(hashB) then return false end
            pos = stop + 1
        end
    end
    if pos ~= #source + 1 then return false end
    return captures
end

function addon.TranslateNpc(npc, source)
    if not npc then return end
    for _, entry in ipairs(npc.lines or { npc.line }) do
        local translated = addon.Translate(entry, source)
        if translated then return translated end
    end
end

function addon.Translate(entry, source)
    if not entry or (issecretvalue and issecretvalue(source)) or type(source) ~= "string" then return end
    for _, version in ipairs(entry.variants or {}) do
        local translated = addon.Translate(version, source)
        if translated then return translated end
    end
    -- Lua's locale-sensitive %s can corrupt UTF-8 (for example the 0xA0 byte in à).
    source = source:gsub("\194\160", " "):gsub("[ \t\r\n\f\011]+", " "):match("^ *(.-) *$")
    if source == "" then return end
    local player = UnitName("player")
    local class, classID = UnitClass("player")
    local race = UnitRace("player")
    if issecretvalue and (issecretvalue(player) or issecretvalue(class) or issecretvalue(classID) or issecretvalue(race)) then return end
    local signatures = entry[1]
    if type(signatures) == "string" then signatures = { signatures } end
    local tokens = { N = player, C = class, R = race }
    local shortRace = shortRaces[race]
    local shortTokens = shortRace and { N = player, C = class, R = shortRace }
    for _, signature in ipairs(signatures) do
        local captured = matches(signature, source, tokens)
        local raceForm = race
        if not captured and shortTokens then
            captured = matches(signature, source, shortTokens)
            raceForm = shortRace
        end
        if captured then
            captured.name, captured.class, captured.race = player, classes[classID] or class, races[raceForm] or raceForm
            return (entry[2]:gsub("{([%a%d]+)}", captured))
        end
    end
    if entry.amount then
        return addon.Translate(entry.amount, source)
    end
end
