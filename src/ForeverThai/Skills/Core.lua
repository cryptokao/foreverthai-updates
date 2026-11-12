local directory, addon = ...
local S = { version = "0.285.0", datasetVersion = "2026.11.09.1" }
addon.skills = S
S.records = {}
S.stats = { callbacks = 0, noContext = 0, lookups = 0, matched = 0, missing = 0, outdated = 0, errors = 0 }
S.defaults = { enabled = true, englishNames = false, descriptions = true, original = false, fontSize = 16 }

function S.Public(value, kind)
    if issecretvalue and issecretvalue(value) then return false end
    if type(value) ~= kind then return false end
    if kind == "table" then
        if issecrettable and issecrettable(value) then return false end
        if canaccesstable and not canaccesstable(value) then return false end
    end
    return true
end
function S.Integer(value)
    return S.Public(value, "number") and value > 0 and value < 100000000 and value == math.floor(value)
end
function S.Call(fn, ...)
    if type(fn) ~= "function" then return nil end
    local ok, value = pcall(fn, ...)
    if ok then return value end
end
function S.Compatible()
    if type(GetBuildInfo) ~= "function" then return false end
    local version, build, _, interface = GetBuildInfo()
    return version == "1.60.1" and (build == "70862" or build == "70888") and interface == 16001
        and type(GetLocale) == "function" and GetLocale() == "enUS"
end
function S.Initialize()
    local old = type(AlphaWoWSkillsDB) == "table" and AlphaWoWSkillsDB or {}
    local settings = {}
    for key, default in pairs(S.defaults) do
        if type(old[key]) == type(default) then settings[key] = old[key] else settings[key] = default end
    end
    -- Older versions saved both English flags as true even on an untouched
    -- install. Migrate that exact pair once and retain other existing choices.
    if old.thaiOnlyDefaultApplied ~= true and old.englishNames == true and old.original == true then
        settings.englishNames, settings.original = false, false
    end
    settings.thaiOnlyDefaultApplied = true
    settings.fontSize = math.max(12, math.min(24, settings.fontSize))
    AlphaWoWSkillsDB = settings
    S.settings = settings
    S.supported = S.Compatible()
end

-- Templates contain only numbered numeric placeholders. Everything else is literal.
-- Full-line matching avoids displaying a translation after a condition/wording change.
function S.Render(source, target, live)
    if not S.Public(live, "string") or #live > 8192 then return nil end
    -- Client strings can retain source spacing that the catalog export collapses.
    source = source:gsub("%s+", " "):match("^ *(.-) *$")
    live = live:gsub("%s+", " "):match("^ *(.-) *$")
    local pattern, last, count = "^", 1, 0
    for first, number, finish in source:gmatch("(){(%d+)}()") do
        count = count + 1
        if tonumber(number) ~= count then return nil end
        pattern = pattern .. source:sub(last, first - 1):gsub("([%(%)%.%%%+%-%*%?%[%]%^%$])", "%%%1") .. "([%d][%d,%.]*)"
        last = finish
    end
    pattern = pattern .. source:sub(last):gsub("([%(%)%.%%%+%-%*%?%[%]%^%$])", "%%%1") .. "$"
    if count == 0 then return source == live and target or nil end
    -- Lua 5.1 allows 32 captures. Rogue combo-point tables need up to 26.
    if count > 32 then return nil end
    local values = { live:match(pattern) }
    if #values ~= count then return nil end
    return (target:gsub("{(%d+)}", function(index) return values[tonumber(index)] or "" end))
end

local function renderPair(pair, live)
    if pair.format == "db2" then return S.RenderDB2 and S.RenderDB2(pair, live) end
    if not pair.alternatives then return S.Render(pair.source, pair.target, live) end
    local result
    for _, variant in ipairs(pair.alternatives) do
        local text = S.Render(variant.source, variant.target, live)
        if text then
            if result and result ~= text then return nil end
            result = text
        end
    end
    return result
end

function S.Lookup(key, name, lines, requireDescriptionMatch)
    S.stats.lookups = S.stats.lookups + 1
    if not S.supported or not S.settings or not S.settings.enabled then return nil end
    local row = S.records[key]
    if not row or row.reviewStatus ~= "VERIFIED" then S.stats.missing = S.stats.missing + 1; return nil end
    if not S.Public(name, "string") or name ~= row.originalName then
        S.stats.outdated = S.stats.outdated + 1; return nil
    end
    local output = {}
    if S.settings.descriptions or row.requireAuraCasterLine or row.requireDescriptionMatch or requireDescriptionMatch then
        for _, pair in ipairs(row.lines or {}) do
            local found = false
            for _, live in ipairs(lines or {}) do
                local text = renderPair(pair, live)
                if text then
                    if S.settings.descriptions then
                        output[#output + 1] = text
                        if S.settings.original then output[#output + 1] = live end
                    end
                    found = true
                    break
                end
            end
            if not found then S.stats.outdated = S.stats.outdated + 1; return nil end
        end
    end
    S.stats.matched = S.stats.matched + 1
    local title = row.translatedName
    if S.settings.englishNames then title = title .. " (" .. name .. ")" end
    return title, table.concat(output, "\n")
end

function S.WithPartialNotice(text, partial)
    if partial and S.settings.descriptions then return text .. "\nดูเงื่อนไขเพิ่มเติมในคำอธิบายเดิม" end
    return text
end
