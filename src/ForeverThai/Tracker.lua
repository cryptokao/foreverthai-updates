local directory, addon = ...
local atlas = "Interface\\AddOns\\" .. directory .. "\\Fonts\\Thai"
local thaiCharacter = "\224[\184\185][\128-\191]"
local tracker, nativeTracker, settingsCategory, checkbox
local hookedBlocks = setmetatable({}, {__mode = "k"})
local refreshAfterCombat
local english = GetLocale() == "enUS" or GetLocale() == "enGB"

local function isString(value)
    return not (issecretvalue and issecretvalue(value)) and type(value) == "string" and value ~= ""
end

local function getQuest(id)
    if not (issecretvalue and issecretvalue(id)) and type(id) == "number" then
        return addon.quests[id]
    end
end

-- Reuse the reader's pre-shaped words and let the tracker draw Latin text with its own font.
local function bitmapMarkup(thai, size, color)
    if thai:find("[|\r\n]") or type(size) ~= "number" or size <= 0 then return end
    local pieces, index = {}, 1
    local r = tonumber(color:sub(1, 2), 16)
    local g = tonumber(color:sub(3, 4), 16)
    local b = tonumber(color:sub(5, 6), 16)
    -- Questie's title and objective FontStrings can be fixed at a single font-size height.
    local height = math.max(1, math.floor(size + 0.5))
    local scale = size / 48
    while true do
        local first, last = thai:find(thaiCharacter, index)
        if not first then break end
        local nextStart, nextEnd = thai:find(thaiCharacter, last + 1)
        while nextStart == last + 1 do
            last = nextEnd
            nextStart, nextEnd = thai:find(thaiCharacter, last + 1)
        end
        pieces[#pieces + 1] = thai:sub(index, first - 1)
        local run = addon.runs[thai:sub(first, last)]
        if not run then return end
        for _, word in ipairs(run) do
            local glyph = addon.glyphs[word]
            local width = math.max(1, math.floor(glyph[4] * scale + 0.5))
            pieces[#pieces + 1] = ("|T%s%d.tga:%d:%d:0:0:1024:1024:%d:%d:%d:%d:%d:%d:%d|t"):format(
                atlas, glyph[1], height, width, glyph[2], glyph[2] + glyph[4], glyph[3], glyph[3] + 56, r, g, b)
        end
        index = last + 1
    end
    if index == 1 then return end
    pieces[#pieces + 1] = thai:sub(index)
    return table.concat(pieces)
end

local function replaceLabel(text, source, thai, size, baseColor)
    if not thai or not isString(source) or not isString(text) or source:find("|", 1, true) then return text end
    local first, last = text:find(source, 1, true)
    if not first or text:find(source, last + 1, true) then return text end
    local prefix = text:sub(1, first - 1)
    -- Leave links, icons, and other control sequences to the tracker.
    if text:gsub("|[cC]%x%x%x%x%x%x%x%x", ""):gsub("|[rR]", ""):find("|", 1, true) then return text end
    baseColor = baseColor or "ffffff"
    local color = baseColor
    for pos in prefix:gmatch("()|") do
        local code = prefix:sub(pos, pos + 9):match("^|[cC]%x%x(%x%x%x%x%x%x)$")
        color = code or baseColor
    end
    local translated = bitmapMarkup(thai, size, color)
    if translated then return prefix .. translated .. text:sub(last + 1) end
    return text
end

local function translateStep(quest, kind, source)
    local labels = quest.objectiveLabels and quest.objectiveLabels[kind]
    if kind == "spell" then return labels and labels[source] end
    for _, step in ipairs(quest.steps or {}) do
        local thai = addon.Translate(step, source)
        if thai then return thai end
    end
    return labels and labels[source] or addon.Translate(quest.objective, source)
end

local function translateObjective(quest, kind, source)
    if kind == "log" then return source, addon.Translate(quest.objective, source) end
    local label = source:match("^(.-):%s*%d+%s*/%s*%d+%s*$")
        or source:match("^%d+%s*/%s*%d+%s+(.+)$")
    if not label and (kind == "item" or kind == "object" or kind == "monster") then
        label = source:match("^%d+ x (.+)$")
    end
    if not label and kind == "item" then label = source:match("^(.-): %(%d+%)$") end
    local thai = label and translateStep(quest, kind, label)
    if thai then return label, thai end
    return source, translateStep(quest, kind, source)
end

local function active()
    return english and ForeverThaiQuestieTracker == true
end

local function nativeObjective(block, fontString, text, quest)
    for key, line in pairs(block.usedLines) do
        if line.used and line.Text == fontString then
            if key == "QuestComplete" then
                if text == QUEST_WATCH_QUEST_COMPLETE then return text, "เควสสำเร็จแล้ว" end
                if text == QUEST_WATCH_QUEST_READY then return text, "พร้อมส่งเควส" end
                return text, addon.Translate(quest.logReady, text) or addon.Translate(quest.objective, text)
            end
            if key == "ClickComplete" and text == QUEST_WATCH_CLICK_TO_COMPLETE then
                return text, "คลิกเพื่อส่งเควส"
            end
            if key == "Failed" and text == FAILED then return text, "เควสล้มเหลว" end
            if type(key) ~= "number" then return end
            local index = C_QuestLog.GetLogIndexForQuestID(block.id)
            if (issecretvalue and issecretvalue(index)) or type(index) ~= "number" or index < 1 then return end
            local source, kind = GetQuestLogLeaderBoard(key, index, true)
            if isString(source) and source == text and isString(kind) then
                return translateObjective(quest, kind, source)
            end
            return
        end
    end
end

local function translateNative(block, fontString, text)
    if not active() or block.parentModule ~= nativeTracker or not isString(text) then return end
    if InCombatLockdown() then
        refreshAfterCombat = true
        return
    end
    local quest = getQuest(block.id)
    if not quest then return end
    local source, thai
    if fontString == block.HeaderText then
        source = C_QuestLog.GetTitleForQuestID(block.id)
        thai = addon.Translate(quest.title, source)
    else
        source, thai = nativeObjective(block, fontString, text, quest)
    end
    if not thai then return end
    local _, size = fontString:GetFont()
    local r, g, b = fontString:GetTextColor()
    local color = ("%02x%02x%02x"):format(math.floor(r * 255 + 0.5), math.floor(g * 255 + 0.5), math.floor(b * 255 + 0.5))
    local translated = replaceLabel(text, source, thai, size, color)
    if translated == text then return end
    -- The secure hook cannot change the height already returned to Blizzard's layout.
    local height = fontString:GetHeight()
    fontString:SetText(translated)
    if fontString:IsTruncated() or fontString:GetHeight() > height + 0.5 then
        fontString:SetText(text)
    end
end

local function connectNative()
    if nativeTracker or not active() or not QuestObjectiveTracker or type(hooksecurefunc) ~= "function"
        or type(QuestObjectiveTracker.AnchorBlock) ~= "function" or type(QuestObjectiveTracker.MarkDirty) ~= "function"
        or not C_QuestLog or type(C_QuestLog.GetLogIndexForQuestID) ~= "function"
        or type(C_QuestLog.GetTitleForQuestID) ~= "function" or type(GetQuestLogLeaderBoard) ~= "function" then return end
    nativeTracker = QuestObjectiveTracker
    hooksecurefunc(nativeTracker, "AnchorBlock", function(_, block)
        if hookedBlocks[block] or type(block.SetStringText) ~= "function" or type(block.usedLines) ~= "table" then return end
        hooksecurefunc(block, "SetStringText", translateNative)
        hookedBlocks[block] = true
    end)
end

local function withText(options, text)
    if text == options.text then return options end
    local copy = {}
    for key, value in pairs(options) do copy[key] = value end
    copy.text = text
    return copy
end

local function connect()
    if tracker or not active() or not QuestieLoader or type(QuestieLoader.ImportModule) ~= "function" then return end
    if C_AddOns and C_AddOns.IsAddOnLoaded and not C_AddOns.IsAddOnLoaded("Questie") then return end
    local questieTracker = QuestieLoader:ImportModule("QuestieTracker")
    local data = QuestieLoader:ImportModule("TrackerData")
    local lines = QuestieLoader:ImportModule("LineBuilder")
    if type(questieTracker.Update) ~= "function" or type(data.GetObjectiveText) ~= "function"
        or type(lines.AddTitle) ~= "function" or type(lines.AddObjective) ~= "function" then return end

    local addTitle, addObjective, getObjectiveText = lines.AddTitle, lines.AddObjective, data.GetObjectiveText
    lines.AddTitle = function(options)
        if active() and options.clickMode == "quest" then
            local target = options.target
            local quest = target and getQuest(target.Id)
            local source = quest and target.name
            local thai = quest and addon.Translate(quest.title, source)
            options = withText(options, replaceLabel(options.text, source, thai, Questie.db.profile.trackerFontSizeQuest))
        end
        return addTitle(options)
    end
    data.GetObjectiveText = function(objective)
        local text = getObjectiveText(objective)
        if not active() then return text end
        local quest = getQuest(objective.questId)
        local kind, source = objective.Type, objective.Description
        if not quest or not isString(kind) or not isString(source) then return text end
        local label, thai = translateObjective(quest, kind, source)
        return replaceLabel(text, label, thai, Questie.db.profile.trackerFontSizeObjective)
    end
    lines.AddObjective = function(options)
        if active() and options.clickMode == "quest" and not options.objective and isString(options.text) then
            local source = options.text:gsub("|[cC]%x%x%x%x%x%x%x%x", ""):gsub("|[rR]", "")
            local target = options.target
            local quest = target and getQuest(target.Id)
            local thai = source == "Quest Complete!" and "เควสสำเร็จแล้ว"
                or source == "Quest Failed!" and "เควสล้มเหลว"
                or quest and (addon.Translate(quest.logReady, source) or addon.Translate(quest.objective, source))
            options = withText(options, replaceLabel(options.text, source, thai, Questie.db.profile.trackerFontSizeObjective))
        end
        return addObjective(options)
    end
    tracker = questieTracker
end

local function refresh()
    if not tracker and not nativeTracker then return end
    if InCombatLockdown() then
        refreshAfterCombat = true
    else
        refreshAfterCombat = nil
        if nativeTracker then nativeTracker:MarkDirty() end
        if tracker then tracker:Update() end
    end
end

function addon.SetQuestieTrackerThai(enabled)
    ForeverThaiQuestieTracker = enabled == true
    if checkbox then checkbox:SetChecked(ForeverThaiQuestieTracker) end
    connect()
    connectNative()
    refresh()
    return english and (tracker ~= nil or nativeTracker ~= nil)
end

local function createSettings()
    if settingsCategory or not Settings or type(Settings.RegisterCanvasLayoutCategory) ~= "function"
        or type(Settings.RegisterAddOnCategory) ~= "function" then return end
    local panel = CreateFrame("Frame", nil, UIParent)
    panel:Hide()
    local title = panel:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
    title:SetPoint("TOPLEFT", 20, -20)
    title:SetText("ForeverThai")

    checkbox = CreateFrame("CheckButton", nil, panel, "UICheckButtonTemplate")
    checkbox:SetPoint("TOPLEFT", title, "BOTTOMLEFT", -3, -14)
    local label = panel:CreateFontString(nil, "ARTWORK", "GameFontHighlight")
    label:SetPoint("LEFT", checkbox, "RIGHT", 5, 0)
    label:SetText("Translate Quest Tracker to Thai")
    checkbox:SetScript("OnClick", function(self) addon.SetQuestieTrackerThai(not not self:GetChecked()) end)
    panel:SetScript("OnShow", function() checkbox:SetChecked(ForeverThaiQuestieTracker == true) end)
    settingsCategory = Settings.RegisterCanvasLayoutCategory(panel, "ForeverThai")
    Settings.RegisterAddOnCategory(settingsCategory)
end

function addon.OpenTrackerSettings()
    if settingsCategory and type(Settings.OpenToCategory) == "function" then
        Settings.OpenToCategory(settingsCategory:GetID())
    else
        print("ForeverThai Quest Tracker: /fth tracker on | /fth tracker off")
    end
end

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("PLAYER_REGEN_ENABLED")
events:SetScript("OnEvent", function(_, event, name)
    if event == "PLAYER_REGEN_ENABLED" then
        if refreshAfterCombat then refresh() end
    elseif name == directory then
        createSettings()
        connect()
        connectNative()
        if active() then refresh() end
    elseif name == "Questie" then
        connect()
        if active() then refresh() end
    elseif event == "PLAYER_LOGIN" or name == "Blizzard_ObjectiveTracker" then
        connectNative()
        if active() then refresh() end
    end
end)
