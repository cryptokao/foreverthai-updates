local _, addon = ...
local S = addon.skills

local triggers = {
    { id = 0, kind = "ItemSpellTriggerOnUse", wrapper = "ITEM_SPELL_TRIGGER_ONUSE", label = "เมื่อใช้" },
    { id = 1, kind = "ItemSpellTriggerOnEquip", wrapper = "ITEM_SPELL_TRIGGER_ONEQUIP", label = "เมื่อสวมใส่" },
    { id = 2, kind = "ItemSpellTriggerOnProc", wrapper = "ITEM_SPELL_TRIGGER_ONPROC", label = "เมื่อเอฟเฟกต์ทำงาน" },
}

local function unwrap(text, wrapper)
    if not S.Public(wrapper, "string") or wrapper == "" or #wrapper > 128 then return nil end
    local slot = wrapper:find("%s", 1, true)
    local prefix, suffix
    if slot then
        prefix, suffix = wrapper:sub(1, slot - 1), wrapper:sub(slot + 2)
    else
        -- A literal label must have a delimiter before the effect body.
        if not wrapper:match("[:%s]$") then return nil end
        prefix, suffix = wrapper, ""
        if prefix:sub(-1) == ":" and not text:sub(#prefix + 1, #prefix + 1):match("%s") then return nil end
    end
    if (prefix == "" and suffix == "") or prefix:find("%", 1, true) or suffix:find("%", 1, true)
        or #text <= #prefix + #suffix or text:sub(1, #prefix) ~= prefix then return nil end
    if suffix ~= "" and text:sub(-#suffix) ~= suffix then return nil end
    return text:sub(#prefix + 1, #text - #suffix)
end

local function visibleText(tooltip, line, count)
    local index, text = line.lineIndex, line.leftText
    if not S.Integer(index) or index > count or not S.Public(text, "string") or #text > 8192
        or not S.Public(line.rightText, "nil") then return nil end
    local region = S.Call(tooltip.GetLeftLine, tooltip, index)
    if not S.Public(region, "table") then return nil end
    local shown = S.Call(region.IsShown, region)
    if not S.Public(shown, "boolean") or not shown then return nil end
    local actual = S.Call(region.GetText, region)
    if S.Public(actual, "string") and actual == text then return text end
end

local function emptyRight(tooltip, index)
    local ok, region = pcall(tooltip.GetRightLine, tooltip, index)
    if not ok then return false end
    if S.Public(region, "nil") then return true end
    if not S.Public(region, "table") then return false end
    local shown = S.Call(region.IsShown, region)
    if not S.Public(shown, "boolean") then return false end
    if not shown then return true end
    local actual = S.Call(region.GetText, region)
    return S.Public(actual, "string") and actual:match("^%s*$") ~= nil
end

local function renderEffect(pair, text)
    local intro = pair.stockCrateIntro
    if intro then
        local body = text:gsub("^%s+", "")
        if body:sub(1, #intro) == intro then
            -- The crate description may retain the native quality color on its list.
            local list = body:sub(#intro + 1):match("^%s*|cnIQ1:(.*)$")
            if list then text = intro .. " " .. list:gsub("|r%s*$", "") end
        end
    end
    local action = pair.violetDustAction
    if action then
        local body = text:gsub("^%s+", "")
        if body:sub(1, #action) == action then
            local condition = body:sub(#action + 1)
            local color, marked = condition:match("^%s*|c(%x%x%x%x%x%x%x%x)([^|]+)|r%s*$")
            text = action .. " " .. (color and color:lower() == "ffffffff" and marked or condition)
        end
    end
    if pair.feastFoodIcon then
        -- Match the Food heading when its exact native inline icon is present.
        local icon = tostring(pair.feastFoodIcon)
        text = text:gsub("(players%.)%s*|T" .. icon .. ":[%d:%.%-]+|t%s+Food%s+", "%1 Food ", 1)
    end
    if pair.quickDrawIcon then
        local icon = tostring(pair.quickDrawIcon)
        text = text:gsub("(Gain the Quick Draw ability:)%s*|T" .. icon .. ":[%d:%.%-]+|t%s+", "%1 ", 1)
    end
    return S.RenderDB2(pair, text)
end

local function matchEffect(keys, text, wrapper)
    local unwrapped = unwrap(text, wrapper)
    local selected, rendered
    for _, key in ipairs(keys) do
        local row = S.records[key]
        if not row or row.reviewStatus ~= "VERIFIED" then return nil end
        local pair = row.lines[1]
        local raw = renderEffect(pair, text)
        local stripped = unwrapped and renderEffect(pair, unwrapped)
        if raw and stripped and raw ~= stripped then return nil end
        local translated = raw or stripped
        if translated then
            if selected then return nil end
            selected, rendered = row, translated
        end
    end
    return selected, rendered
end

local itemCooldownUnits = {
    Sec = "วินาที", Min = "นาที", Hour = "ชั่วโมง", Hours = "ชั่วโมง", Day = "วัน", Days = "วัน",
    sec = "วินาที", min = "นาที", hour = "ชั่วโมง", hours = "ชั่วโมง", day = "วัน", days = "วัน",
}

local function splitItemCooldown(text)
    local body, amount, unit = text:match("^(.+) %(([1-9]%d*) (%a+) Cooldown%)$")
    if not amount or not S.Integer(tonumber(amount)) or not itemCooldownUnits[unit] then return text end
    local lower = unit:lower()
    if ((lower == "hour" or lower == "day") and amount ~= "1")
        or ((lower == "hours" or lower == "days") and amount == "1") then return text end
    return body, "คูลดาวน์ " .. amount .. " " .. itemCooldownUnits[unit]
end

local function unwrapSetBonus(text)
    if S.Public(ITEM_SET_BONUS_GRAY, "string") and ITEM_SET_BONUS_GRAY == "(%d) Set: %s" then
        local threshold, body = text:match("^%(([1-9]%d*)%) Set: (.+)$")
        if threshold and #threshold <= 2 then return body, tonumber(threshold) end
    end
    if S.Public(ITEM_SET_BONUS, "string")
        and (ITEM_SET_BONUS == "Set: " or ITEM_SET_BONUS == "Set: %s")
        and text:sub(1, 5) == "Set: " and #text > 5 then
        return text:sub(6)
    end
end

local function setDescriptions(itemID)
    if not C_Item or not C_Spell or not C_SpecializationInfo then return nil end
    local spec = 0
    local getSpec = C_SpecializationInfo.GetSpecialization
    if type(getSpec) ~= "function" then return nil end
    local ok, index = pcall(getSpec)
    if not ok then return nil end
    if S.Integer(index) then
        spec = S.Call(C_SpecializationInfo.GetSpecializationInfo, index)
        if not S.Integer(spec) then return nil end
    elseif not S.Public(index, "nil") and not (S.Public(index, "number") and index == 0) then
        return nil
    end
    local ids = S.Call(C_Item.GetSetBonusesForSpecializationByItemID, spec, itemID)
    if not S.Public(ids, "table") then return nil end
    local descriptions, seenIDs, count = {}, {}, 0
    for offset, sid in pairs(ids) do
        count = count + 1
        if count > 16 or not S.Integer(offset) or offset > 16 or not S.Integer(sid) or seenIDs[sid] then return nil end
        seenIDs[sid] = true
        local text = S.Call(C_Spell.GetSpellDescription, sid)
        if not S.Public(text, "string") or text == "" or #text > 8192 then return nil end
        -- Mark equal descriptions as ambiguous, including unreviewed spells.
        descriptions[text] = descriptions[text] == nil and sid or false
    end
    return descriptions
end

local function appendSetBonuses(tooltip, data, item, lines, output)
    if #lines == 0 then return end
    local descriptions = setDescriptions(data.id)
    if not descriptions then return end
    local translated, seen = {}, {}
    for _, line in ipairs(lines) do
        local sid = descriptions[line.body]
        local bonus = sid and item.bonuses[sid]
        local row = bonus and S.records[bonus.key]
        if row and row.reviewStatus == "VERIFIED" and (not line.threshold or line.threshold == bonus.threshold)
            and (not bonus.partial or emptyRight(tooltip, line.index)) then
            local name = S.Call(C_Spell.GetSpellName, sid)
            local body = S.RenderDB2(row.lines[1], line.body)
            if S.Public(name, "string") and name == row.originalName and body then
                if seen[sid] then return end
                seen[sid] = true
                local label = "โบนัสชุด"
                if line.threshold or bonus.partial then label = label .. " (" .. (line.threshold or bonus.threshold) .. " ชิ้น)" end
                label = label .. " — " .. row.translatedName
                if S.settings.englishNames then label = label .. " (" .. row.originalName .. ")" end
                translated[#translated + 1] = label
                local requirement = bonus.professionRequirement
                if requirement then
                    translated[#translated + 1] = "เงื่อนไขโบนัสชุด: ทักษะ" .. requirement.name .. " " .. requirement.rank
                end
                if S.settings.descriptions then
                    translated[#translated + 1] = S.WithPartialNotice(body, bonus.partial)
                    if S.settings.original then translated[#translated + 1] = line.live end
                end
            end
        end
    end
    for _, text in ipairs(translated) do output[#output + 1] = text end
end

local function appendEnchantment(tooltip, data, title, live, output)
    if not TooltipUtil or type(TooltipUtil.GetDisplayedItem) ~= "function" then return end
    -- The native getter uses the GUID before the raw hyperlink. Do not pass a
    -- secret GUID or link into it, even when the other field is public.
    if not (S.Public(data.guid, "nil") or S.Public(data.guid, "string"))
        or not (S.Public(data.hyperlink, "nil") or S.Public(data.hyperlink, "string")) then return end
    local ok, name, link, primaryID = pcall(TooltipUtil.GetDisplayedItem, tooltip)
    if not ok or not S.Public(name, "string") or name ~= title or not S.Integer(primaryID) or primaryID ~= data.id
        or not S.Public(link, "string") or #link > 2048 then return end
    local itemString = link:match("^item:[%d:%-]+$")
    if not itemString then
        local uncolored = link:match("^|c%x%x%x%x%x%x%x%x(.*)|r$") or link:match("^|cn[%w_]+:(.*)|r$") or link
        itemString = uncolored:match("^|H(item:[%d:%-]+)|h%[[^|]+%]|h$")
    end
    if not itemString then return end
    local linkedID, enchantID, tail = itemString:match("^item:([1-9]%d*):([1-9]%d*):(.*)$")
    enchantID = tonumber(enchantID)
    if tonumber(linkedID) ~= primaryID or not S.Integer(enchantID) then return end
    for field in (tail .. ":"):gmatch("([^:]*):") do
        if field ~= "" and not field:match("^%-?%d+$") then return end
    end
    local row = S.records[S.itemEnchantments[enchantID]]
    if not row or row.reviewStatus ~= "VERIFIED" then return end
    local body = S.RenderDB2(row.lines[1], live)
    local unwrapped = unwrap(live, ENCHANTED_TOOLTIP_LINE)
    local stripped = unwrapped and S.RenderDB2(row.lines[1], unwrapped)
    if body and stripped and body ~= stripped then return end
    body = body or stripped
    local labelOnly = row.equippedEnchantText and (live == row.originalName or unwrapped == row.originalName)
    if row.equippedEnchantText and not body and not labelOnly then
        local equipped = unwrap(unwrapped or live, ITEM_SPELL_TRIGGER_ONEQUIP)
        if equipped then body = S.RenderDB2(row.lines[1], equipped) end
    end
    if not body and not labelOnly then return end
    local label = "เสริมพลังถาวร — " .. row.translatedName
    local originalName = " (" .. row.originalName .. ")"
    if S.settings.englishNames and row.translatedName:sub(-#originalName) ~= originalName then
        label = label .. originalName
    end
    output[#output + 1] = label
    if S.settings.descriptions then
        if body and body ~= row.translatedName then output[#output + 1] = body end
        if S.settings.original then output[#output + 1] = live end
    end
end

function S.ItemTranslation(tooltip, data, useOnly)
    if not S.Public(tooltip, "table") or not S.Public(data, "table") or not S.Integer(data.id) then return nil end
    local item = S.itemEffects and S.itemEffects[data.id]
    if useOnly and (not item or not item.triggers[0] or item.partialTrigger == 0) then return nil end
    local set = not useOnly and S.itemSetBonuses and S.itemSetBonuses[data.id]
    local mayEnchant = not useOnly and S.itemEnchantments and next(S.itemEnchantments)
        and (S.Public(data.guid, "string") or S.Public(data.hyperlink, "string"))
    local lineTypes = Enum and Enum.TooltipDataLineType
    if not (item or set or mayEnchant) or not lineTypes or not S.Public(data.lines, "table") then return nil end
    local title = (item and item.name) or (set and set.name)
    if set and set.name ~= title then return nil end

    local processing = S.Call(tooltip.GetProcessingTooltipInfo, tooltip)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(processing, "table") or not S.Public(primary, "table") or not rawequal(processing, primary)
        or not S.Public(processing.tooltipData, "table") or not rawequal(processing.tooltipData, data) then return nil end
    local count = S.Call(tooltip.NumLines, tooltip)
    if not S.Integer(count) or count > 80 then return nil end

    local titleMatches, output, setLines, nested = 0, {}, {}, false
    local enchantLineCount, enchantLine, unknownLine = 0, nil, false
    local strictTrigger = useOnly and 0 or (item and (item.strictObservedTrigger or item.strictBaseTrigger or item.partialTrigger))
    local requiredTrigger = strictTrigger or (item and item.singleCompleteEquip and 1)
    local requiredCount = requiredTrigger == 1 and item.strictObservedTrigger == 1 and #item.triggers[1] or 1
    local requiredMatches = 0
    local seenLines, seenEffects = {}, {}
    for index, line in ipairs(data.lines) do
        if index > 80 then return nil end
        if S.Public(line, "table") and S.Public(line.type, "number") then
            if line.type == lineTypes.ItemName then
                local visible = visibleText(tooltip, line, count)
                if not visible or visible == "" or (title and visible ~= title)
                    or (strictTrigger and (line.lineIndex ~= 1 or not emptyRight(tooltip, 1))) then return nil end
                title = visible
                titleMatches = titleMatches + 1
            elseif line.type == lineTypes.NestedBlock then
                nested = true
            elseif mayEnchant and line.type == lineTypes.ItemEnchantmentPermanent then
                enchantLineCount = enchantLineCount + 1
                enchantLine = visibleText(tooltip, line, count)
            elseif set and line.type ~= lineTypes.ItemSpellTriggerOnUse and line.type ~= lineTypes.ItemSpellTriggerOnEquip
                and line.type ~= lineTypes.ItemSpellTriggerOnProc and S.Public(line.leftText, "string")
                and #line.leftText <= 8192 then
                local body, threshold = unwrapSetBonus(line.leftText)
                if body and visibleText(tooltip, line, count) then
                    setLines[#setLines + 1] = {body = body, threshold = threshold, live = line.leftText, index = line.lineIndex}
                end
            end
            for _, trigger in ipairs(triggers) do
                local keys = item and (not useOnly or trigger.id == 0) and item.triggers[trigger.id]
                if keys and line.type == lineTypes[trigger.kind] then
                    local live = visibleText(tooltip, line, count)
                    local required = trigger.id == requiredTrigger
                    if required and (requiredMatches >= requiredCount or not live or not emptyRight(tooltip, line.lineIndex)) then
                        return nil
                    end
                    if live then
                        if seenLines[line.lineIndex] then return nil end
                        seenLines[line.lineIndex] = true
                        local effectText, cooldown = live
                        if trigger.id == item.strictBaseTrigger then effectText, cooldown = splitItemCooldown(live) end
                        local row, translated = matchEffect(keys, effectText, _G[trigger.wrapper])
                        if required and not row then return nil end
                        if row then
                            if required then requiredMatches = requiredMatches + 1 end
                            if seenEffects[row] then return nil end
                            seenEffects[row] = true
                            local label = trigger.label .. " — " .. row.translatedName
                            if S.settings.englishNames then label = label .. " (" .. row.originalName .. ")" end
                            output[#output + 1] = label
                            if S.settings.descriptions then
                                output[#output + 1] = S.WithPartialNotice(translated, trigger.id == item.partialTrigger)
                                if cooldown then output[#output + 1] = cooldown end
                                if S.settings.original then output[#output + 1] = live end
                            end
                        end
                    end
                end
            end
        else
            unknownLine = true
        end
    end
    if titleMatches ~= 1 then return nil end
    if requiredTrigger and (requiredMatches ~= requiredCount or nested or unknownLine) then return nil end
    if set and not nested then appendSetBonuses(tooltip, data, set, setLines, output) end
    if enchantLineCount == 1 and enchantLine and not nested and not unknownLine then
        appendEnchantment(tooltip, data, title, enchantLine, output)
    end
    if #output == 0 then return nil end
    return title, table.concat(output, "\n")
end
