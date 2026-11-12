local directory, addon = ...
local events = {
    CHAT_MSG_MONSTER_SAY = true, CHAT_MSG_MONSTER_YELL = true,
    CHAT_MSG_MONSTER_WHISPER = true, CHAT_MSG_MONSTER_EMOTE = true,
}
local popup = CreateFrame("Frame", "ForeverThaiSpeechReader", UIParent)
popup:SetSize(520, 90)
popup:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, 170)
popup:SetFrameStrata("DIALOG")
popup:SetClampedToScreen(true)
popup:SetMovable(true)
popup:EnableMouse(true)
popup:RegisterForDrag("LeftButton")
popup:SetScript("OnDragStart", function() popup:StartMoving() end)
popup:SetScript("OnDragStop", function() popup:StopMovingOrSizing() end)
local background = popup:CreateTexture(nil, "BACKGROUND")
background:SetAllPoints()
background:SetColorTexture(0.035, 0.045, 0.065, 0.94)
local close = CreateFrame("Button", nil, popup, "UIPanelCloseButton")
close:SetPoint("TOPRIGHT", -2, -2)
local _, paint = addon.BitmapLayer(popup, "TOPLEFT", 16, -10, 484, 18)
local history, remaining, elapsedSinceSpeech = {}, 0, 100
local previousKey
local function hide()
    history, previousKey, remaining = {}, nil, 0
    popup:Hide()
end
close:SetScript("OnClick", hide)
popup:Hide()
addon.speechPanel = popup

local function settings()
    if type(ForeverThaiSpeech) ~= "table" then ForeverThaiSpeech = {} end
    return ForeverThaiSpeech
end
local function supported()
    local version, build, _, interface = GetBuildInfo()
    local locale = GetLocale()
    return version == "1.60.1" and interface == 16001
        and (build == "70862" or build == "70888")
        and (locale == "enUS" or locale == "enGB")
end
local function show(name, text, key)
    -- Each new line is painted immediately; keep just the preceding line for context.
    if key == previousKey and elapsedSinceSpeech < 0.5 then return end
    if remaining <= 0 then history = {} end
    previousKey, elapsedSinceSpeech, remaining = key, 0, 15
    history[#history + 1] = "|cffffd987" .. name .. "|r\n" .. text
    if #history > 2 then table.remove(history, 1) end
    popup:SetHeight(paint(table.concat(history, "\n\n"), 0.96, 0.95, 0.91) + 24)
    popup:Show()
end
popup:SetScript("OnUpdate", function(_, elapsed)
    remaining = remaining - elapsed
    elapsedSinceSpeech = elapsedSinceSpeech + elapsed
    if remaining <= 0 then hide() end
end)

-- Exact existing Player-target qualifications only; see party-source-audit11.json.
local playerSpeechTargets = {
    [3692] = {
        ["17:689065638:2099367606 N 93:978051723:628096343"] = { "Thank you again, ", ". I'll make my way to the road now. When you can, find Terenthis and let him know we escaped." },
    },
    [2610] = {
        ["6:1516321299:785938697 N 55:767366582:1974503773"] = { "Wait, ", "!!! It looks like we're going to need some help here..." },
    },
    [11016] = {
        ["11:1400068568:1359790444 N 74:1899615597:1371138480"] = { "I'm ready, ", ". Let's find my equipment and get out of here. I think I know where it is." },
    },
    [9598] = {
        ["82:1663469478:672223567 N 27:1164390671:1960387495"] = { "The corruption of the fel has not left any of the creatures of Felwood untouched, ", ". Please, be on your guard." },
        ["20:459407763:1459679563 N 32:1247190666:1608881964"] = { "I can sense it now, ", ". Ashenvale lies down this path." },
        ["N 129:2026889222:1757171275"] = { "", ", my form has now changed! The true strength of my spirit is returning to me now... The cursed grasp of the forest is leaving me." },
        ["11:1191658970:1224418299 N 41:852046583:704306828"] = { "Thank you, ", ". Now my spirit will finally be at peace." },
    },
    [10300] = {
        ["25:328543501:1621241081 N 37:781104468:1461312606"] = { "Thank you for your help, ", ". I wish you well in your adventures." },
    },
}

local function secret(value)
    return issecretvalue and issecretvalue(value)
end
local function identityLabel(value)
    return not secret(value) and type(value) == "string" and #value > 0 and #value <= 128
        and not value:find("[%z\1-\32\127|{}]")
end
local function groupIdentity(unit)
    local exists, player = UnitExists(unit), UnitIsPlayer(unit)
    if secret(exists) or secret(player) or exists ~= true or player ~= true then return end
    local party, raid = UnitInParty(unit), UnitInRaid(unit)
    if secret(party) or secret(raid) then return end
    if party ~= true and (type(raid) ~= "number" or raid < 1 or raid > 40 or raid % 1 ~= 0) then return end
    local guid = UnitGUID(unit)
    local name, realm = UnitName(unit)
    if not identityLabel(guid) or not guid:match("^Player%-") or not identityLabel(name)
        or secret(realm) or (realm ~= nil and realm ~= "" and not identityLabel(realm)) then return end
    return guid, name, realm or ""
end
local function speechSpace(text)
    return text:gsub("\194\160", " "):gsub("[ \t\r\n\f\011]+", " "):match("^ *(.-) *$")
end
local function partySpeech(id, event, entry, text)
    if event ~= "CHAT_MSG_MONSTER_SAY" then return end
    local known = playerSpeechTargets[id]
    local exact = known and known[entry[1]]
    if not exact or type(entry[2]) ~= "string" or not entry[2]:find("{name}", 1, true) then return end
    -- These APIs may be absent on unsupported test clients. Fail closed.
    for _, api in ipairs({"UnitExists", "UnitIsPlayer", "UnitInParty", "UnitInRaid", "UnitGUID", "UnitName"}) do
        if type(_G[api]) ~= "function" then return end
    end
    -- Reject unrelated bodies before reading a roster (no name wildcard/capture).
    local normalized = speechSpace(text)
    local before, after = speechSpace(exact[1]), speechSpace(exact[2])
    if (before ~= "" and normalized:sub(1, #before) ~= before)
        or (after ~= "" and normalized:sub(-#after) ~= after) then return end
    local candidates = {}
    local function add(label, unit, guid, name, realm)
        local previous = candidates[label]
        if previous and previous.guid ~= guid then
            previous.ambiguous = true
        elseif not previous then
            candidates[label] = {unit = unit, guid = guid, name = name, realm = realm}
        end
    end
    local function collect(unit)
        local guid, name, realm = groupIdentity(unit)
        if not guid then return end
        add(name, unit, guid, name, realm)
        if realm ~= "" then add(name .. "-" .. realm, unit, guid, name, realm) end
    end
    -- Never inspect target/focus/pets, nor use a chat argument as an identity.
    for i = 1, 4 do collect("party" .. i) end
    for i = 1, 40 do collect("raid" .. i) end
    for label, candidate in pairs(candidates) do
        if not candidate.ambiguous and normalized == speechSpace(exact[1] .. label .. exact[2]) then
            -- Recheck the current roster; do not retain names across events.
            local guid, name, realm = groupIdentity(candidate.unit)
            if guid == candidate.guid and name == candidate.name and realm == candidate.realm then
                return (entry[2]:gsub("{name}", function() return label end))
            end
        end
    end
end

local function onSpeech(_, event, ...)
    if event == "PLAYER_LEAVING_WORLD" then hide(); return end
    if not events[event] or not supported() then return end
    local config = settings()
    if config.enabled == false and config.capture ~= true then return end
    local text, guid = select(1, ...), select(12, ...)
    if issecretvalue and (issecretvalue(text) or issecretvalue(guid)) then return end
    if type(text) ~= "string" or #text > 2048 or not text:find("%S")
        or type(guid) ~= "string" then return end
    local id = tonumber(guid:match("^Creature%-%d+%-%d+%-%d+%-%d+%-(%d+)%-"))
    if not id then return end
    local npc = addon.speech[id]
    local translated
    for _, entry in ipairs(npc and npc[event] or {}) do
        translated = addon.Translate(entry, text) or partySpeech(id, event, entry, text)
        if translated then break end
    end
    if not translated then
        if config.capture == true then addon.Observe("speech", id, event, text) end
        return
    end
    if config.enabled ~= false then show(npc.name, translated, id .. ":" .. event .. ":" .. text) end
end
local frame = CreateFrame("Frame", "ForeverThaiSpeechEvents")
for event in pairs(events) do frame:RegisterEvent(event) end
frame:RegisterEvent("PLAYER_LEAVING_WORLD")
frame:SetScript("OnEvent", onSpeech)

function addon.SpeechCommand(command)
    local config = settings()
    if command == "speech on" or command == "speech off" then
        config.enabled = command == "speech on"
        if not config.enabled then hide() end
    elseif command == "speech capture on" or command == "speech capture off" then
        config.capture = command == "speech capture on"
    elseif command == "speech hide" then
        hide()
    elseif command == "speech test" then
        show("ForeverThai", "ทดสอบกล่องบทพูดภาษาไทยระหว่างคุ้มกัน NPC", "test")
        return
    end
    print("ForeverThai NPC subtitles: " .. (config.enabled == false and "off" or "on") ..
        (supported() and "" or " (unsupported client)") .. "; local source capture: " ..
        (config.capture == true and "on" or "off"))
    print("/fth speech on | off | test | hide | capture on | capture off")
end
