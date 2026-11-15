local _, addon = ...
local maxBytes = 16 * 1024 * 1024
local maxText = 16384
local maxQuestPanels = 2048

local function getStore()
    if type(ForeverThaiObserved) ~= "table" then
        ForeverThaiObserved = { schema = 1, bytes = 0, count = 0, quests = {}, npcs = {} }
    end
    local db = ForeverThaiObserved
    if db.schema ~= 1 or type(db.bytes) ~= "number" or type(db.count) ~= "number"
        or type(db.quests) ~= "table" or type(db.npcs) ~= "table" then return end
    return db
end

-- Keep missing source variants locally so new Forever quests can be translated
-- from server text. Never replace a recorded variant with another variant.
function addon.Observe(kind, id, field, text, questContext)
    if issecretvalue and (issecretvalue(id) or issecretvalue(text)) then return end
    if type(id) ~= "number" or id <= 0 or type(text) ~= "string" or #text > maxText or not text:find("%S") then return end
    local db = getStore()
    if not db then return end
    if (kind == "objects" or kind == "speech") and db[kind] == nil then db[kind] = {} end
    local group = db[kind]
    if type(group) ~= "table" then return end
    local subject = group[id] or {}
    local variants = subject[field] or {}
    local version, build, _, interface = GetBuildInfo()
    local locale = GetLocale()
    for _, item in ipairs(variants) do
        if item.text == text then
            if questContext and item.build == build and item.version == version and item.locale == locale
                and item.interface == interface
                and (not item.questContext or (not item.questContext.npcID and questContext.npcID)) then
                item.questContext = questContext
            end
            return
        end
    end
    if db.bytes + #text > maxBytes then return end
    if kind == "speech" then
        if (db.speechCount or 0) >= 512 or (db.speechBytes or 0) + #text > 256 * 1024 then return end
    end
    local player = UnitName("player")
    local class = UnitClass("player")
    local race = UnitRace("player")
    if issecretvalue and (issecretvalue(player) or issecretvalue(class) or issecretvalue(race)) then return end
    variants[#variants + 1] = {
        text = text, player = player, class = class, race = race,
        locale = locale, version = version, build = build, interface = interface, questContext = questContext,
    }
    subject[field] = variants
    group[id] = subject
    db.bytes = db.bytes + #text
    db.count = db.count + 1
    if kind == "speech" then
        db.speechCount = (db.speechCount or 0) + 1
        db.speechBytes = (db.speechBytes or 0) + #text
    end
    return true
end

-- An empty string is an observation for this panel only. A nil or secret
-- value can mean the client has not supplied the field, so do not record it.
function addon.ObserveQuestPanel(id, phase, fields)
    local states, keyParts = {}, {}
    for _, field in ipairs(fields) do
        local name, value = field[1], field[2]
        if not (issecretvalue and issecretvalue(value)) and type(value) == "string" then
            local state = value == "" and "empty" or value:find("%S") and "text" or "whitespace"
            states[name] = state
            keyParts[#keyParts + 1] = name .. "=" .. state
        end
    end
    if #keyParts == 0 then return end

    local db = getStore()
    if not db then return end
    if db.questPanels == nil then db.questPanels, db.questPanelCount = {}, 0 end
    if type(db.questPanels) ~= "table" or type(db.questPanelCount) ~= "number"
        or db.questPanelCount >= maxQuestPanels then return end
    local _, build = GetBuildInfo()
    local locale = GetLocale()
    local key = build .. ":" .. locale .. ":" .. phase .. ":" .. table.concat(keyParts, ",")
    local panels = db.questPanels[id] or {}
    if type(panels) ~= "table" or panels[key] then return end
    panels[key] = { build = build, locale = locale, phase = phase, fields = states }
    db.questPanels[id] = panels
    db.questPanelCount = db.questPanelCount + 1
end
