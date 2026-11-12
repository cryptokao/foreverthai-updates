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
        translated = addon.Translate(entry, text)
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
