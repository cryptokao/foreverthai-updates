local _, addon = ...
local S = addon.skills
local cache = setmetatable({}, { __mode = "k" })
local units = {
    sec = "วินาที", secs = "วินาที", second = "วินาที", seconds = "วินาที",
    min = "นาที", mins = "นาที", minute = "นาที", minutes = "นาที",
    hr = "ชั่วโมง", hrs = "ชั่วโมง", hour = "ชั่วโมง", hours = "ชั่วโมง",
    day = "วัน", days = "วัน",
}
local function normalize(text) return (text:gsub("%s+", " "):gsub("^ +", ""):gsub(" +$", "")) end
local function number(text)
    -- Keep the client's exact decimal/grouping display, but reject malformed values.
    if not text:match("^[%+%-]?%d[%d,%.]*$") or text:match("[,.]$") or text:find("..", 1, true) then return false end
    local plain = text:gsub(",", "")
    if not plain:match("^[%+%-]?%d+%.?%d*$") then return false end
    if text:find(",", 1, true) then
        local unsigned = text:gsub("^[%+%-]", "")
        local integer = unsigned:match("^([^%.]+)")
        local fractional = unsigned:match("%.(.*)$")
        if fractional and fractional:find(",", 1, true) then return false end
        local groups = {}
        for group in integer:gmatch("[^,]+") do groups[#groups + 1] = group end
        local _, commas = integer:gsub(",", "")
        if #groups ~= commas + 1 or #groups[1] > 3 then return false end
        for index = 2, #groups do if #groups[index] ~= 3 then return false end end
    end
    return true
end
local function positiveNumber(text)
    return text:match("^%d") and text:find("[1-9]") and number(text)
end
local function value(text, kind)
    if kind == "bind-location" then
        if text == "" or text:match("^%s") or text:match("%s$") or text:find("[|$%[%]{}<>%c]") then return nil end
        local location = S.Call(GetBindLocation)
        if S.Public(location, "string") and location == text then return text end
        return nil
    end
    if kind == "aura-caster" then
        if not text:match("^%s") and not text:match("[%s%.]$") and not text:find("%.%s")
            and not text:find("[|$%[%]{}<>%c]") and text:find("[^%d%p%s]") then return text end
        return nil
    end
    if kind == "duration" or kind == "positive-duration" or kind == "positive-seconds-duration" then
        local positive = kind ~= "duration"
        if not positive and (text == "until cancelled" or text == "until canceled") then return "จนกว่าจะยกเลิก" end
        local amount, unit = text:match("^([%+%-]?[%d,.]+) (%a+)%.?$")
        if amount and units[unit] and (kind ~= "positive-seconds-duration" or units[unit] == "วินาที")
            and (positive and positiveNumber(amount) or not positive and number(amount)) then
            return amount .. " " .. units[unit]
        end
        return nil
    end
    if kind == "unsigned-number" then
        if text:match("^%d") and number(text) then return text end
        return nil
    end
    if kind == "signed-number" then
        if number(text) then return text end
        return nil
    end
    if kind == "frost-ward-absorb" then
        if text:match("^%d") and number(text) then return text end
        local base, coefficient = text:match("^%(([%d,.]+) %+ ([%d,.]+)%% of Frost Spell Power%)$")
        if base and number(base) and number(coefficient) then
            return "(" .. base .. " + " .. coefficient .. "% ของพลังเวทน้ำแข็ง)"
        end
        return nil
    end
    if kind == "positive-number" or kind == "positive-integer" then
        if positiveNumber(text) and (kind == "positive-number" or not text:find(".", 1, true)) then return text end
        return nil
    end
    local positiveRange = kind == "positive-number-range"
    if not positiveRange and kind ~= "number-range" then return nil end
    local validNumber = positiveRange and positiveNumber or number
    if validNumber(text) then return text end
    local first, last = text:match("^([%+%-]?[%d,.]+) to ([%+%-]?[%d,.]+)$")
    local separator = " ถึง "
    if not first then
        first, last = text:match("^([%+%-]?[%d,.]+)%-([%+%-]?[%d,.]+)$")
        separator = "-"
    end
    if first and validNumber(first) and validNumber(last)
        and (not positiveRange or tonumber((first:gsub(",", ""))) <= tonumber((last:gsub(",", "")))) then
        return first .. separator .. last
    end
    return nil
end
local function renderLinear(pair, live)
    if not S.Public(live, "string") or #live > 8192 then return nil end
    local compiled = cache[pair]
    if not compiled then
        local literals, last, count = {}, 1, 0
        for first, index, finish in pair.source:gmatch("(){(%d+)}()") do
            count = count + 1
            if tonumber(index) ~= count or not pair.slots[count] then return nil end
            literals[count] = pair.source:sub(last, first - 1)
            if count > 1 and literals[count] == "" then return nil end
            last = finish
        end
        if count ~= #pair.slots or count > 32 then return nil end
        literals[count + 1] = pair.source:sub(last)
        compiled = {literals = literals, count = count}
        cache[pair] = compiled
    end
    if compiled.count ~= 1 or pair.slots[1].kind ~= "aura-caster" then live = normalize(live) end
    if compiled.count == 0 then return live == pair.source and pair.target or nil end
    local initial = compiled.literals[1]
    if live:sub(1, #initial) ~= initial then return nil end
    local position, captured, output = #initial + 1, {}, {}
    -- Plain literal searches with bounded typed values, never a backtracking pattern.
    -- Ambiguous boundaries fall back instead of choosing a different interpretation.
    for index, slot in ipairs(pair.slots) do
        local literal = compiled.literals[index + 1]
        local chosen, chosenEnd, chosenValue, search = nil, nil, nil, position
        if literal == "" then
            if index ~= compiled.count or #live - position + 1 > 96 then return nil end
            local raw = live:sub(position)
            chosenValue = value(raw, slot.kind)
            if not chosenValue then return nil end
            chosen, chosenEnd = raw, #live + 1
        else
            while search <= #live + 1 do
                local first = live:find(literal, search, true)
                if not first or first - position > 96 then break end
                local raw = live:sub(position, first - 1)
                if index ~= compiled.count or first + #literal == #live + 1 then
                    local converted = value(raw, slot.kind)
                    if converted then
                        if chosen then return nil end
                        chosen, chosenEnd, chosenValue = raw, first + #literal, converted
                    end
                end
                search = first + 1
            end
        end
        if not chosen then return nil end
        captured[index], output[index], position = chosen, chosenValue, chosenEnd
    end
    if position ~= #live + 1 then return nil end
    local repeated = {}
    for index, slot in ipairs(pair.slots) do
        local raw = captured[index]
        if repeated[slot.token] and repeated[slot.token] ~= raw then return nil end
        if slot.expectedNumber then
            local integer, fraction = raw:gsub(",", ""):match("^(%d+)%.?(%d*)$")
            if not integer or not number(raw) or integer:gsub("^0+", "") ~= tostring(slot.expectedNumber)
                or fraction:find("[1-9]") then return nil end
        end
        repeated[slot.token] = raw
    end
    return (pair.target:gsub("{(%d+)}", function(index) return output[tonumber(index)] or "" end))
end

local function renderOptionalSections(pair, live)
    if not S.Public(live, "string") or #live > 8192 then return nil end
    live = normalize(live)
    local position = #pair.source + 2
    if live:sub(1, position - 1) ~= pair.source .. " " then return nil end
    local output = {pair.target}
    for _, section in ipairs(pair.optionalSections) do
        local boundary = live:find(". ", position, true)
        local translated = renderLinear(section, live:sub(position, boundary or #live))
        if translated then
            output[#output + 1] = translated
            if not boundary then return table.concat(output, "\n") end
            position = boundary + 2
        end
    end
end

function S.RenderDB2(pair, live)
    if pair.optionalSections then return renderOptionalSections(pair, live) end
    if not pair.alternatives then return renderLinear(pair, live) end
    if #pair.alternatives == 0 or #pair.alternatives > 32 then return nil end
    local output
    -- The client has already chosen its conditions and computed its numbers.
    -- Match visible complete text only; never evaluate guards or spell formulas.
    for _, variant in ipairs(pair.alternatives) do
        local candidate = renderLinear(variant, live)
        if candidate then
            if output and output ~= candidate then return nil end
            output = candidate
        end
    end
    return output
end
