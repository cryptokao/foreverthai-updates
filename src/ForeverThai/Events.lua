local addonName, addon = ...
local eventFrame = CreateFrame("Frame", "ForeverThaiEvents")
local mode
local captions = {
    objective = "เป้าหมาย", description = "เรื่องราว", progress = "ระหว่างทำเควส",
    completion = "เมื่อส่งเควส", logReady = "เมื่อเควสพร้อมส่ง",
}
local english = GetLocale() == "enUS" or GetLocale() == "enGB"

local function clear(which)
    if which == nil or mode == which then
        mode = nil
        addon.panel:Hide()
    end
end

local function dialogTarget(unit)
    local guid = UnitGUID(unit)
    if (issecretvalue and issecretvalue(guid)) or type(guid) ~= "string" then return end
    local kind, id = guid:match("^(%a+)%-%d+%-%d+%-%d+%-%d+%-(%d+)%-")
    if kind == "Creature" or kind == "GameObject" then return tonumber(id), kind end
end

local function npcID()
    local id, kind = dialogTarget("npc")
    if kind == "Creature" then return id end
end

local function translateQuestField(quest, field, source)
    if not quest then return end
    return addon.Translate(quest[field], source)
        or field == "logReady" and addon.Translate(quest.objective, source)
end

local function observeQuestPanel(quest, id, title, phase, fields)
    if not quest then return end
    local missingPhase = (phase == "progress" or phase == "completion") and not quest[phase]
    if (not quest.objective or not quest.description or missingPhase) and addon.Translate(quest.title, title) then
        addon.ObserveQuestPanel(id, phase, fields)
    end
end

local function questPage(context, id, title, fields, phase, extraText, extraCaption)
    clear()
    if not english or (issecretvalue and issecretvalue(id)) then return end
    local quest = addon.quests[id]
    if ForeverThaiAutoCaptureLog == true then observeQuestPanel(quest, id, title, phase, fields) end
    local evidence
    local function observe(field, source)
        if not evidence then
            evidence = { phase = phase, npcID = context == "quest" and npcID() or nil }
            if not (issecretvalue and issecretvalue(title)) and type(title) == "string"
                and title ~= "" and #title <= 512 then evidence.title = title end
        end
        addon.Observe("quests", id, field, source, evidence)
    end
    if not addon.Translate(quest and quest.title, title) then observe("title", title) end
    for _, field in ipairs(fields) do
        if not translateQuestField(quest, field[1], field[2]) then
            observe(field[1], field[2])
        end
    end
    if not quest then return end
    local translatedTitle = addon.Translate(quest.title, title)
    local parts, missing = {}, false
    if translatedTitle then parts[1] = "|cffffd987" .. translatedTitle .. "|r" end
    for _, field in ipairs(fields) do
        local key, source = field[1], field[2]
        local thai = translateQuestField(quest, key, source)
        if thai then
            parts[#parts + 1] = "|cffedc27b" .. captions[key] .. "|r\n" .. thai
        elseif not (issecretvalue and issecretvalue(source)) and type(source) == "string" and source ~= "" then
            missing = true
        end
    end
    if extraText then
        parts[#parts + 1] = "|cffedc27b" .. extraCaption .. "|r\n" .. extraText
    end
    if #parts == 0 then return end
    if missing then parts[#parts + 1] = "บางส่วนยังไม่มีคำแปลที่ตรงกับข้อความในเกม โปรดดูต้นฉบับในหน้าต่างเควส" end
    mode = context
    addon.ShowPage("บันทึกเควส  ·  #" .. id, table.concat(parts, "\n\n"))
end

local function readGossipOptions(known)
    if not known or type(C_GossipInfo.GetOptions) ~= "function" then return end
    local options = C_GossipInfo.GetOptions()
    if (issecretvalue and issecretvalue(options)) or type(options) ~= "table" then return end
    local lines = {}
    for _, option in ipairs(options) do
        local id = option.gossipOptionID
        if not (issecretvalue and issecretvalue(id)) and type(id) == "number" then
            local source = option.name
            local exact = known[id]
            local thai = addon.Translate(exact, source)
            if not exact and known.lines then
                thai = addon.TranslateNpc(known, source)
            end
            if thai then
                local englishName = source:gsub("%s+", " "):gsub("^ ", ""):gsub(" $", "")
                lines[#lines + 1] = thai .. "\n|cffbbbbbb" .. englishName .. "|r"
            end
        end
    end
    if #lines > 0 then return table.concat(lines, "\n") end
end

local function npcPage(context, text)
    clear()
    if not english then return end
    local id, kind = dialogTarget("npc")
    if not id and context == "quest" then id, kind = dialogTarget("questnpc") end
    if not id then return end
    if kind == "GameObject" then
        local object = addon.objects[id]
        local message = addon.TranslateNpc(object, text)
        if message then
            mode = context
            addon.ShowPage("ข้อความจากวัตถุ", "|cffffd987" .. object.name .. "|r\n\n" .. message)
        elseif not (issecretvalue and issecretvalue(text)) and type(text) == "string" and text:find("%S") then
            addon.Observe("objects", id, context == "quest" and "greeting" or "gossip", text)
        end
        return
    end
    local npc = addon.npcs[id]
    local message = addon.TranslateNpc(npc, text)
    if not message then addon.Observe("npcs", id, "greeting", text) end
    local knownOptions = context == "gossip" and addon.gossipOptions[id]
    local choices = readGossipOptions(knownOptions)
    if not message and not choices then return end
    local name = message and npc.name or knownOptions.name
    local parts = { "|cffffd987" .. name .. "|r" }
    if message then parts[#parts + 1] = message end
    if choices then
        parts[#parts + 1] = "|cffedc27bตัวเลือกตอบ NPC|r\n" .. choices
    end
    mode = context
    addon.ShowPage("บทสนทนา", table.concat(parts, "\n\n"))
end

local function splitStepCount(source, kind)
    local label, count = source:match("^(.-):%s*(%d+%s*/%s*%d+)%s*$")
    if label then return label, " (" .. count .. ")" end
    count, label = source:match("^(%d+%s*/%s*%d+)%s+(.+)$")
    if label then return label, " (" .. count .. ")" end
    if kind == "item" or kind == "object" or kind == "monster" then
        count, label = source:match("^(%d+) x (.+)$")
        if label then return label, " ×" .. count, true end
    end
    if kind == "item" then
        label, count = source:match("^(.-): %((%d+)%)$")
        if label then return label, " ×" .. count end
    end
end

local function readSteps(id, index, title)
    if type(GetNumQuestLeaderBoards) ~= "function" or type(GetQuestLogLeaderBoard) ~= "function" then return end
    local count = GetNumQuestLeaderBoards(index)
    if (issecretvalue and issecretvalue(count)) or type(count) ~= "number" then return end
    local quest = addon.quests[id]
    local lines = {}
    local steps = quest and quest.steps or {}
    local objectiveLabels = quest and quest.objectiveLabels
    local evidence
    for i = 1, count do
        local source, kind = GetQuestLogLeaderBoard(i, index)
        if not (issecretvalue and (issecretvalue(source) or issecretvalue(kind)))
            and type(source) == "string" and kind ~= "log" then
            local label, suffix, quantityOnly = splitStepCount(source, kind)
            local thai
            if kind ~= "spell" then
                for _, entry in ipairs(steps) do
                    thai = addon.Translate(entry, source)
                    if not thai and label then
                        thai = addon.Translate(entry, label)
                        if thai then thai = thai .. suffix end
                    end
                    if thai then break end
                end
            end
            local labels = objectiveLabels and objectiveLabels[kind]
            if not thai and labels then
                thai = labels[source]
                if not thai and label then
                    thai = labels[label]
                    if not thai and quantityOnly and kind == "monster" then
                        thai = labels[label .. " slain"]
                    end
                    if thai then thai = thai .. suffix end
                end
            end
            if thai then
                lines[#lines + 1] = thai
            elseif type(kind) == "string" and #kind <= 32 and kind:match("^[%a][%w_]*$") and source ~= "" then
                if not evidence then
                    evidence = { phase = "log" }
                    if not (issecretvalue and issecretvalue(title)) and type(title) == "string"
                        and title ~= "" and #title <= 512 then evidence.title = title end
                end
                addon.Observe("quests", id, "step:" .. kind .. ":" .. i, source, evidence)
            end
        end
    end
    if #lines > 0 then return table.concat(lines, "\n") end
end

local function readRequiredItems(id)
    if not english or (issecretvalue and issecretvalue(id)) then return end
    local quest = addon.quests[id]
    if not quest or not quest.required or type(GetNumQuestItems) ~= "function"
        or type(IsQuestItemHidden) ~= "function" or type(GetQuestItemInfo) ~= "function"
        or not C_QuestOffer or type(C_QuestOffer.GetHideRequiredItems) ~= "function"
        or C_QuestOffer.GetHideRequiredItems() then return end
    local lines = {}
    for i = 1, GetNumQuestItems() do
        if IsQuestItemHidden(i) == 0 then
            local name, _, count, _, _, itemID = GetQuestItemInfo("required", i)
            if not (issecretvalue and (issecretvalue(itemID) or issecretvalue(count)))
                and type(itemID) == "number" and type(count) == "number" and count > 0 then
                local thai = addon.Translate(quest.required[itemID], name)
                if thai then lines[#lines + 1] = thai .. " ×" .. count end
            end
        end
    end
    if #lines > 0 then return table.concat(lines, "\n") end
end

local function readRequiredMoney(id)
    if type(C_QuestLog.GetRequiredMoney) ~= "function" then return end
    local amount = C_QuestLog.GetRequiredMoney(id)
    if (issecretvalue and issecretvalue(amount)) or type(amount) ~= "number"
        or amount <= 0 or amount % 1 ~= 0 then return end
    local gold = math.floor(amount / 10000)
    local silver = math.floor(amount / 100) % 100
    local copper = amount % 100
    local coins = {}
    if gold > 0 then coins[#coins + 1] = gold .. " ทอง" end
    if silver > 0 then coins[#coins + 1] = silver .. " เงิน" end
    if copper > 0 then coins[#coins + 1] = copper .. " ทองแดง" end
    return "เงินที่ต้องจ่าย " .. table.concat(coins, " ")
end

local function readReadyText(id, index)
    if type(GetQuestLogCompletionText) ~= "function" or type(C_QuestLog.IsComplete) ~= "function" then return end
    local complete = C_QuestLog.IsComplete(id)
    if (issecretvalue and issecretvalue(complete)) or not complete then return end
    local text = GetQuestLogCompletionText(index)
    if (issecretvalue and issecretvalue(text)) or text == QUEST_WATCH_QUEST_READY then return end
    return text
end

local function readLog(id)
    local details = QuestMapFrame and QuestMapFrame.DetailsFrame
    if (issecretvalue and issecretvalue(id)) or not details or not details:IsVisible() or details.questID ~= id then
        clear("log")
        return
    end
    if not C_QuestLog or C_QuestLog.GetSelectedQuest() ~= id then
        clear("log")
        return
    end
    local description, objective = GetQuestLogQuestText()
    local title = C_QuestLog.GetTitleForQuestID(id)
    local readyText, steps
    if english and type(C_QuestLog.GetLogIndexForQuestID) == "function" then
        local index = C_QuestLog.GetLogIndexForQuestID(id)
        if not (issecretvalue and issecretvalue(index)) and index then
            readyText = readReadyText(id, index)
            steps = readSteps(id, index, title)
            if addon.quests[id] then
                local requiredMoney = readRequiredMoney(id)
                if requiredMoney then steps = steps and steps .. "\n" .. requiredMoney or requiredMoney end
            end
        end
    end
    questPage("log", id, title, {
        {"objective", objective}, {"description", description}, {"logReady", readyText},
    }, "log", steps, "เป้าหมายย่อย")
end

local function canCaptureLog()
    return english and C_QuestLog and type(C_QuestLog.GetNumQuestLogEntries) == "function"
        and type(C_QuestLog.GetInfo) == "function" and type(C_QuestLog.GetLogIndexForQuestID) == "function"
        and type(GetQuestLogQuestText) == "function"
end

local function captureLog()
    if not canCaptureLog() then return end
    local entries = C_QuestLog.GetNumQuestLogEntries()
    if (issecretvalue and issecretvalue(entries)) or type(entries) ~= "number"
        or entries < 0 or entries > 1000 or entries % 1 ~= 0 then return end
    for index = 1, entries do
        local info = C_QuestLog.GetInfo(index)
        if not (issecretvalue and issecretvalue(info)) and type(info) == "table" then
            local id, title, header = info.questID, info.title, info.isHeader
            if not (issecretvalue and (issecretvalue(id) or issecretvalue(title) or issecretvalue(header)))
                and not header and type(id) == "number" and id > 0
                and type(title) == "string" and title ~= "" and #title <= 512 then
                local logIndex = C_QuestLog.GetLogIndexForQuestID(id)
                if not (issecretvalue and issecretvalue(logIndex)) and logIndex == index then
                    local description, objective = GetQuestLogQuestText(index)
                    local ready = readReadyText(id, index)
                    local quest = addon.quests[id]
                    local evidence = { phase = "log", title = title }
                    observeQuestPanel(quest, id, title, "log", {{"objective", objective},
                        {"description", description}, {"logReady", ready}})
                    for _, field in ipairs({{"title", title}, {"objective", objective},
                        {"description", description}, {"logReady", ready}}) do
                        if not translateQuestField(quest, field[1], field[2]) then
                            addon.Observe("quests", id, field[1], field[2], evidence)
                        end
                    end
                end
            end
        end
    end
    return true
end

local captureScheduled
local function canAutoCaptureLog()
    return canCaptureLog() and C_Timer and type(C_Timer.After) == "function"
end

local function scheduleLogCapture()
    if ForeverThaiAutoCaptureLog ~= true or captureScheduled or not canAutoCaptureLog() then return end
    captureScheduled = true
    C_Timer.After(1, function()
        if ForeverThaiAutoCaptureLog == true then captureLog() end
        captureScheduled = nil
    end)
end

local lookup
local function finishLookupRequest(batch, id, success)
    if lookup ~= batch or batch.pending ~= id then return end
    batch.pending = nil
    if success then
        local title = C_QuestLog.GetTitleForQuestID(id)
        if not (issecretvalue and issecretvalue(title)) and type(title) == "string"
            and title:find("%S") and #title <= 512 then
            local quest = addon.quests[id]
            local evidence = { phase = "lookup", title = title }
            if not translateQuestField(quest, "title", title)
                and addon.Observe("quests", id, "title", title, evidence) then
                batch.recorded = batch.recorded + 1
            end
            local objectives = C_QuestLog.GetQuestObjectives(id)
            if not (issecretvalue and issecretvalue(objectives)) and type(objectives) == "table" then
                for _, objective in ipairs(objectives) do
                    if not (issecretvalue and issecretvalue(objective)) and type(objective) == "table" then
                        local kind, text = objective.type, objective.text
                        if not (issecretvalue and (issecretvalue(kind) or issecretvalue(text)))
                            and kind == "log" and type(text) == "string" then
                            local trimmed = text:match("^%s*(.-)%s*$"):lower()
                            if trimmed ~= "log" and trimmed ~= "description"
                                and not translateQuestField(quest, "objective", text)
                                and addon.Observe("quests", id, "objective", text, evidence) then
                                batch.recorded = batch.recorded + 1
                            end
                        end
                    end
                end
            end
        end
    else
        batch.unavailable = batch.unavailable + 1
    end
    C_Timer.After(0.25, batch.nextRequest)
end

local function startLookup(input)
    if not english or not C_QuestLog or type(C_QuestLog.RequestLoadQuestByID) ~= "function"
        or type(C_QuestLog.GetTitleForQuestID) ~= "function" or type(C_QuestLog.GetQuestObjectives) ~= "function"
        or not C_Timer or type(C_Timer.After) ~= "function" then
        print("ForeverThai quest-ID capture requires an English client and the quest lookup API.")
        return
    end
    if lookup then
        print("ForeverThai quest-ID capture is already running.")
        return
    end
    local ids, seen = {}, {}
    for value in input:gmatch("%S+") do
        local id = #value <= 10 and value:match("^%d+$") and tonumber(value)
        if not id or id < 1 or id > 2147483647 or (#ids == 8 and not seen[id]) then
            print("ForeverThai usage: /fth capture id <up to 8 distinct quest IDs>")
            return
        end
        if not seen[id] then ids[#ids + 1], seen[id] = id, true end
    end
    if #ids == 0 then
        print("ForeverThai usage: /fth capture id <up to 8 distinct quest IDs>")
        return
    end
    local batch = { index = 1, recorded = 0, unavailable = 0 }
    batch.nextRequest = function()
        if lookup ~= batch then return end
        local id = ids[batch.index]
        if InCombatLockdown and InCombatLockdown() then
            lookup = nil
            print("ForeverThai quest-ID capture stopped in combat.")
        elseif not id then
            lookup = nil
            print(("ForeverThai new local quest-ID records: %d; failed or timed out: %d."):format(
                batch.recorded, batch.unavailable))
        else
            batch.index, batch.pending = batch.index + 1, id
            C_Timer.After(5, function() finishLookupRequest(batch, id, false) end)
            if not pcall(C_QuestLog.RequestLoadQuestByID, id) then finishLookupRequest(batch, id, false) end
        end
    end
    lookup = batch
    batch.nextRequest()
end

local logHooked = false
local function hookLog()
    if logHooked or not QuestMapFrame_ShowQuestDetails or not QuestMapFrame or not QuestMapFrame.DetailsFrame then return end
    hooksecurefunc("QuestMapFrame_ShowQuestDetails", readLog)
    QuestMapFrame.DetailsFrame:HookScript("OnHide", function() clear("log") end)
    logHooked = true
end

local function readBook()
    clear("book")
    if not english or type(ItemTextGetItem) ~= "function" or type(ItemTextGetPage) ~= "function"
        or type(ItemTextGetText) ~= "function" then return end
    local title, page = ItemTextGetItem(), ItemTextGetPage()
    if (issecretvalue and (issecretvalue(title) or issecretvalue(page)))
        or type(title) ~= "string" or type(page) ~= "number" then return end
    local book = addon.books[title]
    local entry = book and book[page]
    if not entry then return end
    local message = addon.Translate(entry, ItemTextGetText())
    if not message then return end
    mode = "book"
    addon.ShowPage("เอกสาร · หน้า " .. page, "|cffffd987" .. book.title .. "|r\n\n" .. message)
end

local handlers = {
    PLAYER_LOGIN = function()
        hookLog()
        scheduleLogCapture()
    end,
    ADDON_LOADED = hookLog,
    QUEST_LOG_UPDATE = scheduleLogCapture,
    QUEST_DATA_LOAD_RESULT = function(id, success)
        if lookup and not (issecretvalue and (issecretvalue(id) or issecretvalue(success)))
            and type(id) == "number" and type(success) == "boolean" then
            finishLookupRequest(lookup, id, success)
        end
    end,
    PLAYER_LEAVING_WORLD = function() lookup = nil; clear() end,
    QUEST_FINISHED = function() clear("quest") end,
    GOSSIP_CLOSED = function() clear("gossip") end,
    ITEM_TEXT_BEGIN = function() clear("book") end,
    ITEM_TEXT_READY = readBook,
    ITEM_TEXT_CLOSED = function() clear("book") end,
    QUEST_DETAIL = function()
        questPage("quest", GetQuestID(), GetTitleText(), {
            {"objective", GetObjectiveText()}, {"description", GetQuestText()},
        }, "detail")
    end,
    QUEST_PROGRESS = function()
        local id = GetQuestID()
        questPage("quest", id, GetTitleText(), {{"progress", GetProgressText()}}, "progress",
            readRequiredItems(id), "ไอเท็มที่ต้องส่ง")
    end,
    QUEST_COMPLETE = function()
        questPage("quest", GetQuestID(), GetTitleText(), {{"completion", GetRewardText()}}, "completion")
    end,
    QUEST_GREETING = function() npcPage("quest", GetGreetingText()) end,
    GOSSIP_SHOW = function() npcPage("gossip", C_GossipInfo.GetText()) end,
}
for event in pairs(handlers) do eventFrame:RegisterEvent(event) end
eventFrame:SetScript("OnEvent", function(_, event, ...) handlers[event](...) end)

SLASH_FOREVERTHAI1 = "/fth"
SlashCmdList.FOREVERTHAI = function(command)
    command = (command or ""):lower():match("^%s*(.-)%s*$")
    if command == "test" then
        clear()
        mode = "test"
        addon.ShowPage("ทดสอบฟอนต์ภาษาไทย", "น้ำค้างยามเช้า • ปี่ ขลุ่ย กุ้ง เก้าอี้\n\nตัวอย่างเป้าหมายจากเควส #783\n" .. addon.quests[783].objective[2])
    elseif command == "capture log" then
        local before = type(ForeverThaiObserved) == "table" and tonumber(ForeverThaiObserved.count) or 0
        if captureLog() then
            local after = type(ForeverThaiObserved) == "table" and tonumber(ForeverThaiObserved.count) or 0
            print("ForeverThai new local quest-log source records: " .. (after - before))
        else
            print("ForeverThai quest-log capture requires an English client and accessible quest log.")
        end
    elseif command == "capture" then
        print("ForeverThai local source records: " .. tostring(type(ForeverThaiObserved) == "table" and ForeverThaiObserved.count or 0))
        print("ForeverThai quest panel observations: " .. tostring(type(ForeverThaiObserved) == "table" and ForeverThaiObserved.questPanelCount or 0))
        print("Saved on logout in WTF/Account/<account>/SavedVariables/ForeverThai.lua")
    elseif command == "capture id" or command:match("^capture id%s") then
        startLookup(command:sub(11))
    elseif command == "capture auto on" or command == "capture auto off" then
        if command == "capture auto on" and not canAutoCaptureLog() then
            print("ForeverThai automatic capture requires an English client and accessible quest log.")
            return
        end
        ForeverThaiAutoCaptureLog = command == "capture auto on"
        scheduleLogCapture()
        print("ForeverThai automatic local quest-log capture: " .. (ForeverThaiAutoCaptureLog and "on" or "off"))
    elseif (command == "speech" or command:match("^speech%s")) and addon.SpeechCommand then
        addon.SpeechCommand(command)
    elseif command == "tracker" and addon.OpenTrackerSettings then
        addon.OpenTrackerSettings()
    elseif (command == "tracker on" or command == "tracker off") and addon.SetQuestieTrackerThai then
        local enabled = command == "tracker on"
        local available = addon.SetQuestieTrackerThai(enabled)
        print("ForeverThai Quest Tracker: " .. (enabled and "Thai" or "English") ..
            (enabled and not available and " (requires an English client and a supported tracker)" or ""))
    elseif command == "image" or command == "font" then
        addon.SetMode(command)
    elseif command == "hide" then
        clear()
    elseif command == "reset" then
        addon.ResetPosition()
    else
        local version, build, _, toc = GetBuildInfo()
        local metadata = C_AddOns and C_AddOns.GetAddOnMetadata or GetAddOnMetadata
        local addonVersion = type(metadata) == "function" and metadata(addonName, "Version")
        print(("ForeverThai%s | WoW %s (%s) | Interface %s | %s | font %s"):format(
            addonVersion and (" " .. addonVersion) or "", tostring(version), tostring(build), tostring(toc),
            GetLocale(), addon.fontOK and "OK" or "FAILED"))
        print("Display: " .. (ForeverThaiDisplayMode == "font" and addon.fontOK and "font" or "image") ..
            ". English quests only. /fth test, /fth image, /fth font, /fth hide, /fth reset, /fth tracker")
        print("Local source capture: /fth capture | /fth capture log | /fth capture id <quest IDs> | /fth capture auto on/off")
        print("NPC subtitles: /fth speech | /fth speech on | /fth speech off | /fth speech test")
    end
end
