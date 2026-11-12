local _, addon = ...
local S = addon.skills
local function argument(info, index)
    local args = info and info.getterArgs
    if not S.Public(args, "table") then return nil end
    return args[index]
end

local function displayedTalentConfig(tooltip, entry)
    -- Shared TalentDisplay owns the tooltip and its frame knows the displayed
    -- configuration, including Legacy. Negative inspect/view sentinel configs
    -- remain unsupported and fall back. Do not substitute
    -- the player's active class config when a displayed config is unavailable.
    local owner = S.Call(tooltip.GetOwner, tooltip)
    if S.Public(owner, "table") and type(owner.GetTalentFrame) == "function" then
        local ownerEntry = S.Call(owner.GetEntryID, owner)
        if not S.Integer(ownerEntry) or ownerEntry ~= entry then return nil end
        local talentFrame = S.Call(owner.GetTalentFrame, owner)
        if not S.Public(talentFrame, "table") then return nil end
        local config = S.Call(talentFrame.GetConfigID, talentFrame)
        if not S.Integer(config) then return nil end
        local name = S.Call(owner.GetName, owner)
        if not S.Public(name, "string") or name == "" then return nil end
        return config, name, owner, talentFrame
    end
    if C_ClassTalents then return S.Call(C_ClassTalents.GetActiveConfigID) end
end

local function isFirstRankPreview(owner, entry, info, data)
    if not owner or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data) then
        return false
    end
    local tooltipEntry = S.Call(owner.GetTooltipEntryInfo, owner)
    if not S.Public(tooltipEntry, "table") or not S.Public(tooltipEntry.ranksPurchased, "number")
        or tooltipEntry.ranksPurchased ~= 0 then return false end
    local current = tooltipEntry.currEntryInfo
    return S.Public(current, "table") and S.Integer(current.entryID) and current.entryID == entry
        and S.Public(current.rank, "number") and current.rank == 0
end

local function displayedSide(tooltip, getter, index, expected)
    local ok, region = pcall(getter, tooltip, index)
    if not ok then return false end
    if S.Public(region, "nil") then return expected == nil end
    if not S.Public(region, "table") then return false end
    local shown = S.Call(region.IsShown, region)
    if not S.Public(shown, "boolean") then return false end
    if not shown then return expected == nil end
    local actual = S.Call(region.GetText, region)
    if not S.Public(actual, "string") then return false end
    if expected == nil then return actual:match("^%s*$") ~= nil end
    return actual == expected
end

local function flyoutIdentity(info, getter)
    local slot = argument(info, 1)
    if not S.Integer(slot) then return nil end
    if getter == "GetAction" and type(GetActionInfo) == "function" then
        local ok, kind, id = pcall(GetActionInfo, slot)
        if ok and S.Public(kind, "string") and kind == "flyout" and S.Integer(id) then return id end
    elseif getter == "GetSpellBookItem" and C_SpellBook and Enum.SpellBookSpellBank and Enum.SpellBookItemType then
        local bank = argument(info, 2)
        if not S.Public(bank, "number") or bank ~= Enum.SpellBookSpellBank.Player then return nil end
        local entry = S.Call(C_SpellBook.GetSpellBookItemInfo, slot, bank)
        if S.Public(entry, "table") and S.Public(entry.itemType, "number")
            and entry.itemType == Enum.SpellBookItemType.Flyout and S.Integer(entry.actionID)
            and S.Public(entry.name, "string") then return entry.actionID, entry.name end
    end
end

local function flyoutContext(tooltip, info, data, getter)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Public(data.lines, "table") or #data.lines > 12 or type(GetFlyoutInfo) ~= "function" then return nil end
    local id, entryName = flyoutIdentity(info, getter)
    if not id or (not S.Public(data.id, "nil") and (not S.Integer(data.id) or data.id ~= id)) then return nil end
    local key = "flyout:" .. id
    local record = S.records[key]
    if not record or record.reviewStatus ~= "VERIFIED" then return nil end
    local ok, name, body, slots, known = pcall(GetFlyoutInfo, id)
    if not ok or not S.Public(known, "boolean") or not known or not S.Integer(slots)
        or not S.Public(name, "string") or name ~= record.originalName or (entryName and entryName ~= name)
        or not S.Public(body, "string") or body ~= record.lines[1].source then return nil end
    local title, count = data.lines[1], S.Call(tooltip.NumLines, tooltip)
    if not S.Public(title, "table") or not S.Public(title.leftText, "string") or title.leftText ~= name
        or not S.Integer(count) or count > 12
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, name) then return nil end
    for index = 2, #data.lines do
        local line = data.lines[index]
        if S.Public(line, "table") and S.Public(line.leftText, "string") and line.leftText == body then
            local visible = line.lineIndex
            if S.Public(visible, "nil") then visible = index end
            if S.Integer(visible) and visible > 1 and visible <= count
                and displayedSide(tooltip, tooltip.GetLeftLine, visible, body)
                and displayedSide(tooltip, tooltip.GetRightLine, visible, nil) then
                return { key = key, category = "flyout", name = name, lines = {body}, requireDescriptionMatch = true }
            end
        end
    end
end

local function petCommandContext(tooltip, info, data, token)
    if not S.Public(token, "string") or #token > 40
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Public(data.lines, "table") or #data.lines ~= 2 then return nil end
    local key = "pet-command:" .. token
    local command = S.records[key]
    local name = _G[token]
    if not command or not S.Public(name, "string") or name ~= command.originalName then return nil end
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    local count = S.Call(tooltip.NumLines, tooltip)
    if not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Integer(count) or count ~= 2 then return nil end
    local lines = {}
    for index = 1, 2 do
        local line = data.lines[index]
        if not S.Public(line, "table") then return nil end
        local left, right = line.leftText, line.rightText
        if not S.Public(left, "string") or #left > 8192
            or (not S.Public(right, "nil") and not (S.Public(right, "string") and right == ""))
            or not displayedSide(tooltip, tooltip.GetLeftLine, index, left)
            or not displayedSide(tooltip, tooltip.GetRightLine, index, nil) then return nil end
        lines[index] = left
    end
    if lines[1] ~= name then return nil end
    return {key = key, category = "pet-command", name = name, lines = {lines[2]}}
end

local function petCommandBarSet()
    local sets = Enum.ActionBarSet
    if not sets or not S.Public(sets.Mkb, "number") or not C_ActionBar
        or type(GetPetActionInfo) ~= "function" then return nil end
    if InputUtil and type(InputUtil.IsGamepadUIEnabled) == "function" then
        local gamepad = S.Call(InputUtil.IsGamepadUIEnabled)
        if not S.Public(gamepad, "boolean") or gamepad then return nil end
    end
    return sets.Mkb
end

local function mappedPetToken(actionID, set)
    -- GetPetActionInfo takes a pet bar slot.
    -- Use only current slots reported for that exact action, with no title-based lookup.
    local slots = S.Call(C_ActionBar.GetPetActionPetBarIndices, actionID, set)
    if not S.Public(slots, "table") or #slots == 0 or #slots > 10 then return nil end
    local token
    for index = 1, #slots do
        local petSlot = slots[index]
        if not S.Integer(petSlot) or petSlot > 10 then return nil end
        local ok, action, _, isToken = pcall(GetPetActionInfo, petSlot)
        if not ok or not S.Public(isToken, "boolean") or not isToken
            or not S.Public(action, "string") or #action > 40
            or (token and action ~= token) then return nil end
        token = action
    end
    return token
end

local function spellBookPetToken(info)
    local banks, types = Enum.SpellBookSpellBank, Enum.SpellBookItemType
    local set = petCommandBarSet()
    if not set or not banks or not types or not C_SpellBook then return nil end
    local slot, bank = argument(info, 1), argument(info, 2)
    if not S.Integer(slot) or not S.Public(bank, "number") or bank ~= banks.Pet then return nil end
    local entry = S.Call(C_SpellBook.GetSpellBookItemInfo, slot, bank)
    if not S.Public(entry, "table") or not S.Public(entry.itemType, "number") or entry.itemType ~= types.PetAction
        or not S.Integer(entry.actionID) or not S.Public(entry.name, "string") then return nil end
    local token = mappedPetToken(entry.actionID, set)
    local name = token and _G[token]
    if S.Public(name, "string") and name == entry.name then return token end
end

local function playerBarPetToken(info)
    local set, slot = petCommandBarSet(), argument(info, 1)
    if not set or not S.Integer(slot) or type(GetActionInfo) ~= "function" then return nil end
    local ok, kind, actionID = pcall(GetActionInfo, slot)
    if not ok or not S.Public(kind, "string") or not S.Integer(actionID) then return nil end
    -- The native reverse lookup confirms that the hovered slot contains this
    -- pet action, even if another action type has the same numeric ID.
    local slots = S.Call(C_ActionBar.FindPetActionButtons, actionID, set)
    if not S.Public(slots, "table") or #slots > 1024 then return nil end
    for index = 1, #slots do
        local candidate = slots[index]
        if S.Integer(candidate) and candidate == slot then return mappedPetToken(actionID, set) end
    end
end

function S.BasicPetActionRecord(tooltip, button)
    local bar = PetActionBar
    if not S.Public(bar, "table") or not S.Public(bar.actionButtons, "table")
        or not S.Public(button, "table") then return nil end
    local slot = S.Call(button.GetID, button)
    local owner = S.Call(tooltip.GetOwner, tooltip)
    if not S.Integer(slot) or slot > 10 or not S.Public(owner, "table") or not rawequal(owner, button) then return nil end
    local nativeButton = bar.actionButtons[slot]
    if not S.Public(nativeButton, "table") or not rawequal(nativeButton, button) then return nil end
    local count = S.Call(tooltip.NumLines, tooltip)
    if not S.Integer(count) or count > 2 or type(GetPetActionInfo) ~= "function" then return nil end
    local ok, action, _, isToken, _, _, _, spellID = pcall(GetPetActionInfo, slot)
    if not ok or not S.Public(isToken, "boolean") or not S.Public(action, "string") or #action > 128 then return nil end
    local name, record = action
    if isToken then
        if count ~= 1 then return nil end
        record = S.records["pet-command:" .. action]
        name = _G[action]
    else
        if not S.Integer(spellID) then return nil end
        record = S.records["spell:" .. spellID]
        if record and record.requireDescriptionMatch then return nil end
        if count == 2 then
            local subtext = C_Spell and S.Call(C_Spell.GetSpellSubtext, spellID)
            if not S.Public(subtext, "string") or subtext == "" or #subtext > 256
                or not displayedSide(tooltip, tooltip.GetLeftLine, 2, subtext)
                or not displayedSide(tooltip, tooltip.GetRightLine, 2, nil) then return nil end
        end
    end
    if not record or record.reviewStatus ~= "VERIFIED" or not S.Public(name, "string")
        or name ~= record.originalName or not S.Public(button.tooltipName, "string")
        or button.tooltipName ~= name then return nil end
    -- Match the same title shape the native basic handler constructs.
    local bindingOK, binding = pcall(function() return GetBindingText(GetBindingKey("BONUSACTIONBUTTON" .. slot)) end)
    if not bindingOK or (not S.Public(binding, "nil") and not S.Public(binding, "string")) then return nil end
    local expected = name
    if binding and binding ~= "" then
        if #binding > 256 or not S.Public(NORMAL_FONT_COLOR_CODE, "string")
            or not S.Public(FONT_COLOR_CODE_CLOSE, "string") then return nil end
        expected = name .. NORMAL_FONT_COLOR_CODE .. " (" .. binding .. ")" .. FONT_COLOR_CODE_CLOSE
    end
    if not displayedSide(tooltip, tooltip.GetLeftLine, 1, expected)
        or not displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then return nil end
    return record
end

local function activeFlyoutSpell(tooltip)
    local flyout = SpellFlyout
    if not S.Public(flyout, "table") or not S.Public(flyout.buttons, "table")
        or #flyout.buttons > 128 then return nil end
    local owner = S.Call(tooltip.GetOwner, tooltip)
    if not S.Public(owner, "table") or not S.Integer(owner.spellID)
        or (not S.Public(owner.offSpec, "nil") and not S.Public(owner.offSpec, "boolean"))
        or owner.offSpec then return nil end
    local open = S.Call(flyout.IsVisible, flyout)
    local visible = S.Call(owner.IsVisible, owner)
    if not S.Public(open, "boolean") or not open or not S.Public(visible, "boolean") or not visible then return nil end
    for index = 1, #flyout.buttons do
        local button = flyout.buttons[index]
        if S.Public(button, "table") and rawequal(button, owner) then return owner.spellID, owner end
    end
end

local function flyoutTitleRecord(id)
    local proof = S.flyoutTitleOnly and S.flyoutTitleOnly[id]
    if not proof or not C_Spell then return nil end
    local name = S.Call(C_Spell.GetSpellName, id)
    local rank = S.Call(C_Spell.GetSpellSubtext, id)
    if not S.Public(name, "string") or name ~= proof.name
        or not S.Public(rank, "string") or rank ~= proof.rank then return nil end
    local record = S.records["spell:" .. proof.learnedSpellID]
    if record and record.reviewStatus == "VERIFIED" and record.originalName == proof.name then
        return record, proof
    end
end

function S.BasicFlyoutRecord(tooltip, button)
    local id, owner = activeFlyoutSpell(tooltip)
    if not id or not rawequal(owner, button) or not C_Spell
        or (not S.Public(button.showFullTooltip, "nil") and not S.Public(button.showFullTooltip, "boolean"))
        or button.showFullTooltip then return nil end
    local count = S.Call(tooltip.NumLines, tooltip)
    if not S.Integer(count) or count ~= 1 then return nil end
    if S.flyoutTitleOnly and S.flyoutTitleOnly[id] then
        local record, proof = flyoutTitleRecord(id)
        if record and displayedSide(tooltip, tooltip.GetLeftLine, 1, proof.name)
            and displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then return record end
        return nil
    end
    local record = S.records["spell:" .. id]
    local name = S.Call(C_Spell.GetSpellName, id)
    if not record or record.reviewStatus ~= "VERIFIED" or record.requireDescriptionMatch
        or record.requireCompleteSpellBody or not S.Public(name, "string") or name ~= record.originalName
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, name)
        or not displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then return nil end
    return record
end

local function directFlyoutSpell(tooltip, info, spellID)
    local id, pet, subtext = argument(info, 1), argument(info, 2), argument(info, 3)
    -- Native popup members call SetSpellByID(id, false, true).
    return S.Integer(id) and id == spellID and S.Public(pet, "boolean") and not pet
        and S.Public(subtext, "boolean") and subtext and activeFlyoutSpell(tooltip) == spellID
end

local function detailedFlyoutTitle(tooltip, info, data, getter, id)
    if getter ~= "GetSpellByID" or not directFlyoutSpell(tooltip, info, id) then return nil end
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data) then return nil end
    local record, proof = flyoutTitleRecord(id)
    local count = S.Call(tooltip.NumLines, tooltip)
    if not record or not S.Integer(count) or count > 4
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, proof.name) then return nil end
    local hasRank = displayedSide(tooltip, tooltip.GetRightLine, 1, proof.rank)
    if not hasRank and not displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then return nil end
    for index = 2, count do
        if not displayedSide(tooltip, tooltip.GetRightLine, index, nil) then return nil end
        if not displayedSide(tooltip, tooltip.GetLeftLine, index, nil) then
            if hasRank or not displayedSide(tooltip, tooltip.GetLeftLine, index, proof.rank) then return nil end
            hasRank = true
        end
    end
    return {key = "flyout-title:" .. id, name = proof.name, titleOnly = record}
end

local function visibleLineText(tooltip, getter, index)
    local ok, region = pcall(getter, tooltip, index)
    if not ok then return nil end
    if S.Public(region, "nil") then return "" end
    if not S.Public(region, "table") then return nil end
    local shown = S.Call(region.IsShown, region)
    if not S.Public(shown, "boolean") then return nil end
    if not shown then return "" end
    local text = S.Call(region.GetText, region)
    if S.Public(text, "string") and #text <= 4096 then return text end
end

local function weaponStatBody(tooltip, info, data, getter, id, name)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    local count = S.Call(tooltip.NumLines, tooltip)
    if getter ~= "GetSpellByID" or not directFlyoutSpell(tooltip, info, id)
        or not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Integer(count) or count > 32 or count < 2
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, name) then return nil end
    local passive = C_Spell and S.Call(C_Spell.IsSpellPassive, id)
    local badge = S.Public(passive, "boolean") and passive
        and S.Public(SPELL_PASSIVE, "string") and SPELL_PASSIVE == "Passive" and SPELL_PASSIVE
    local rightTitle = visibleLineText(tooltip, tooltip.GetRightLine, 1)
    if not rightTitle or (not rightTitle:match("^%s*$") and rightTitle ~= badge) then return nil end
    local allowBadge = badge and rightTitle ~= badge
    local lines = {}
    for index = 2, count do
        local left = visibleLineText(tooltip, tooltip.GetLeftLine, index)
        local right = visibleLineText(tooltip, tooltip.GetRightLine, index)
        if not left or not right then return nil end
        if allowBadge and left == badge and right:match("^%s*$") then
            allowBadge = false
        elseif not left:match("^%s*$") or not right:match("^%s*$") then
            allowBadge = false
            lines[#lines + 1] = left .. " " .. right
        end
    end
    local body = table.concat(lines, "\n"):gsub("%s+$", "")
    -- The native expand-key hint remains visible on the original tooltip.
    body = body:gsub("%s*|cffBCBCBCHold [%w+ -]+ for additional info%.|r$", "")
    body = body:gsub("%s+Hold [%w+ -]+ for additional info%.$", "")
    local hint = "Your chance to glance isn't affected by weapon skill above your max."
    local colored = "|cff9d9d9d" .. hint .. "|r"
    if body:sub(-#colored) == colored then body = body:sub(1, -#colored - 1) .. hint end
    return body
end

local function orderedTalentText(tooltip, info, data, record, talentLast)
    if not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data) then return nil end
    if type(tooltip.GetLeftLine) ~= "function" or type(tooltip.GetRightLine) ~= "function" then return nil end
    local count = talentLast or S.Call(tooltip.NumLines, tooltip)
    if not S.Integer(count) or count > 80 or not displayedSide(tooltip, tooltip.GetLeftLine, 1, record.originalName)
        or not displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then return nil end
    local start = record.orderedTooltip.start
    local lines, prefix, previous, sectionFound = {}, {}, 0, false
    for i, line in ipairs(data.lines) do
        if i > 24 or not S.Public(line, "table") then return nil end
        local left, right = line.leftText, line.rightText
        if not S.Public(left, "string") or #left > 2048
            or (not S.Public(right, "nil") and not S.Public(right, "string"))
            or (right and #right > 256) then return nil end
        local text = left .. (right and " " .. right or "")
        local color = text:sub(1, 10):upper()
        if (color == "|CFFFFFFFF" or color == "|CFFFF2020") and text:sub(11, 10 + #start) == start
            and text:sub(11 + #start, 12 + #start):upper() == "|R" then
            text = start .. text:sub(13 + #start)
        end
        text = text:gsub("%s+", " "):match("^%s*(.-)%s*$")
        local index = line.lineIndex
        if not S.Integer(index) or index > count or (previous > 0 and index ~= previous + 1)
            or not displayedSide(tooltip, tooltip.GetLeftLine, index, left)
            or not displayedSide(tooltip, tooltip.GetRightLine, index, right) then return nil end
        if previous == 0 then
            for prior = 2, index - 1 do
                if not displayedSide(tooltip, tooltip.GetLeftLine, prior, nil)
                    or not displayedSide(tooltip, tooltip.GetRightLine, prior, nil) then return nil end
            end
        end
        previous = index
        if #lines > 0 or text == start or text:sub(1, #start + 1) == start .. " " then
            if text == record.orderedTooltip.section and not right then sectionFound = true end
            if text ~= "" then lines[#lines + 1] = text end
        elseif text ~= "" then
            prefix[#prefix + 1] = text
        end
    end
    local before = table.concat(prefix, " ")
    local metadata = record.orderedTooltip.prefix
    if previous == count and sectionFound and (before == "" or before == record.originalName
        or before == metadata or before == record.originalName .. " " .. metadata) then
        return {table.concat(lines, " ")}
    end
end

local auraTimerUnits = {
    second = true, seconds = true, minute = true, minutes = true,
    hour = true, hours = true, day = true, days = true,
}

local auraDispelLabels = { Magic = true, Curse = true, Disease = true, Poison = true }

local function completeAuraHeader(tooltip, data, name, aura)
    if not displayedSide(tooltip, tooltip.GetLeftLine, 1, name) then return false end
    if displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then return true end
    local header, dispel = data.lines[1], aura.dispelName
    return S.Public(aura.name, "string") and aura.name == name
        and S.Public(dispel, "string") and auraDispelLabels[dispel]
        and S.Public(header, "table") and S.Integer(header.lineIndex) and header.lineIndex == 1
        and S.Public(header.leftText, "string") and header.leftText == name
        and S.Public(header.rightText, "string") and header.rightText == dispel
        and displayedSide(tooltip, tooltip.GetRightLine, 1, dispel)
end

local function auraCasterFooter(tooltip, data, count)
    local casterType = Enum.TooltipDataLineType and Enum.TooltipDataLineType.AuraCaster
    if not S.Public(casterType, "number") then return nil end
    local casterIndex
    for index, line in ipairs(data.lines) do
        if index > 80 or not S.Public(line, "table") then return false end
        local kind = line.type
        if not S.Public(kind, "number") and not S.Public(kind, "nil") then return false end
        if kind == casterType then
            local visibleIndex, text = line.lineIndex, line.leftText
            if casterIndex or not S.Integer(visibleIndex) or visibleIndex < 3 or visibleIndex > count
                or not S.Public(AURA_CAST_BY, "string") or AURA_CAST_BY ~= "Cast by %s"
                or not S.Public(text, "string") or #text > 256 or not text:match("^Cast by %S")
                or text:find("[%c%%$|]")
                or (not S.Public(line.rightText, "nil") and
                    (not S.Public(line.rightText, "string") or line.rightText ~= ""))
                or not displayedSide(tooltip, tooltip.GetLeftLine, visibleIndex, text) then return false end
            casterIndex = visibleIndex
        end
    end
    return casterIndex
end

local function completeAuraBody(tooltip, info, data, record, aura)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    local count = S.Call(tooltip.NumLines, tooltip)
    local pair = record.lines and record.lines[1]
    local limit = pair and pair.optionalSections and 24 or 8
    if not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Integer(count) or count < 2 or count > limit
        or not completeAuraHeader(tooltip, data, record.originalName, aura) then return nil end
    local casterIndex = auraCasterFooter(tooltip, data, count)
    if casterIndex == false then return nil end
    local lines = {}
    local footer, timerSeen
    for index = 2, count do
        if not displayedSide(tooltip, tooltip.GetRightLine, index, nil) then return nil end
        local text = visibleLineText(tooltip, tooltip.GetLeftLine, index)
        if not text then return nil end
        local timer = (index == count or index + 1 == casterIndex)
            and auraTimerUnits[text:match("^%d+ (%a+) remaining$")]
        if index == casterIndex or timer then
            if #lines == 0 or (timer and timerSeen) then return nil end
            footer = true
            if timer then timerSeen = true end
        elseif not text:match("^%s*$") then
            if footer then return nil end
            lines[#lines + 1] = text
        end
    end
    if #lines > 0 then return table.concat(lines, " ") end
end

local auraInstanceGetters = {
    GetUnitAuraByAuraInstanceID = true, GetUnitBuffByAuraInstanceID = true,
    GetUnitDebuffByAuraInstanceID = true,
}
local combatRestrictionTypes = {"Combat", "Encounter", "ChallengeMode", "PvPMatch", "Map", "Chat"}

local function combatRestrictionsStable()
    local types, states = Enum.AddOnRestrictionType, Enum.AddOnRestrictionState
    if not C_RestrictedActions or not types or not states then return false end
    for _, name in ipairs(combatRestrictionTypes) do
        local kind = types[name]
        if not S.Public(kind, "number") then return false end
        local state = S.Call(C_RestrictedActions.GetAddOnRestrictionState, kind)
        -- Aura predicates can still report public data during Activating.
        if not S.Public(state, "number") or (state ~= states.Inactive and state ~= states.Active) then return false end
    end
    return true
end

local function nativeAuraUpdate(method, mixin)
    return S.Public(mixin, "table") and S.Public(mixin.UpdateTooltip, "function") and rawequal(method, mixin.UpdateTooltip)
end

local function groupAuraOwnerMatches(tooltip, getter, unit, instance)
    local party = unit:match("^party[1-4]$")
    local raid = tonumber(unit:match("^raid([1-9]%d?)$"))
    if not party and (not raid or raid > 40) then return false end
    if getter == "GetUnitAuraByAuraInstanceID" then return false end
    local owner = S.Call(tooltip.GetOwner, tooltip)
    if not S.Public(owner, "table") then return false end
    local forbidden = S.Call(owner.IsForbidden, owner)
    if not S.Public(forbidden, "boolean") or forbidden
        or not S.Integer(owner.auraInstanceID) or owner.auraInstanceID ~= instance
        or not S.Public(owner.UpdateTooltip, "function") then return false end
    local method = owner.UpdateTooltip
    if party and nativeAuraUpdate(method, PartyAuraFrameMixin) then
        return S.Public(owner.unit, "string") and owner.unit == unit
    end
    if not nativeAuraUpdate(method, CompactBuffMixin) and not nativeAuraUpdate(method, CompactDebuffMixin) then return false end
    local parent = S.Call(owner.GetParent, owner)
    if not S.Public(parent, "table") then return false end
    local parentForbidden = S.Call(parent.IsForbidden, parent)
    return S.Public(parentForbidden, "boolean") and not parentForbidden
        and S.Public(parent.displayedUnit, "string") and parent.displayedUnit == unit
end

local function publicCombatAura(tooltip, info, data)
    if not C_Secrets or not C_UnitAuras then return nil end
    local unit, instance = argument(info, 1), argument(info, 2)
    if not S.Public(unit, "string") or not S.Integer(instance) then return nil end
    if unit ~= "player" and not groupAuraOwnerMatches(tooltip, info.getterName, unit, instance) then return nil end
    local restricted = S.Call(C_Secrets.ShouldUnitAuraInstanceBeSecret, unit, instance)
    if not S.Public(restricted, "boolean") or restricted then return nil end
    local aura = S.Call(C_UnitAuras.GetAuraDataByAuraInstanceID, unit, instance)
    if not S.Public(aura, "table") or not S.Integer(aura.auraInstanceID) or aura.auraInstanceID ~= instance
        or not S.Integer(aura.spellId) or not S.Public(aura.name, "string") then return nil end
    local key = "aura:" .. aura.spellId
    local record = S.records[key]
    -- The complete card is checked here for every single-body aura, including
    -- records whose ordinary tooltip path does not require the full card.
    if not record or record.reviewStatus ~= "VERIFIED" or record.petSpeedAura or record.requireAuraCasterLine
        or not record.lines or #record.lines ~= 1 or record.originalName ~= aura.name then return nil end
    local body = completeAuraBody(tooltip, info, data, record, aura)
    if body then
        local title, text = S.Lookup(key, record.originalName, {body}, true)
        if title then return title, text, unit end
    end
end

local function casterAuraText(tooltip, info, data)
    if not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data) then return nil end
    local casterType = Enum.TooltipDataLineType and Enum.TooltipDataLineType.AuraCaster
    if not S.Public(casterType, "number") then return nil end
    local name, caster
    for i, line in ipairs(data.lines) do
        if i > 80 or not S.Public(line, "table") then return nil end
        local left, lineType = line.leftText, line.type
        if not S.Public(lineType, "nil") and not S.Public(lineType, "number") then return nil end
        if lineType == casterType then
            local index = line.lineIndex
            if not name or caster or not S.Public(left, "string") or not S.Public(line.rightText, "nil")
                or not S.Integer(index) or not displayedSide(tooltip, tooltip.GetLeftLine, index, left)
                or not displayedSide(tooltip, tooltip.GetRightLine, index, nil) then return nil end
            caster = left
        elseif i == 1 then
            if not S.Public(left, "string") then return nil end
            name = left
        end
    end
    if caster then return name, { caster } end
end

local function petPassiveText(tooltip, processing, data, record, spellID)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(processing, "table") or not S.Public(primary, "table") or not rawequal(processing, primary)
        or not S.Public(processing.tooltipData, "table") or not rawequal(processing.tooltipData, data) then return nil end
    local banks, types, lineTypes = Enum.SpellBookSpellBank, Enum.SpellBookItemType, Enum.TooltipDataLineType
    if not banks or not types or not lineTypes or not C_SpellBook then return nil end
    local slot, bank = argument(processing, 1), argument(processing, 2)
    if not S.Integer(slot) or not S.Public(bank, "number") or bank ~= banks.Pet then return nil end
    local entry = S.Call(C_SpellBook.GetSpellBookItemInfo, slot, bank)
    local rank = record.nativeRank
    if not S.Public(entry, "table") or not S.Integer(entry.spellID) or entry.spellID ~= spellID
        or not S.Public(entry.name, "string") or entry.name ~= record.originalName
        or not S.Public(entry.isPassive, "boolean") or not entry.isPassive
        or not S.Public(entry.itemType, "number") or entry.itemType ~= types.Spell then return nil end
    local subName = entry.subName
    if not S.Public(subName, "nil") and not S.Public(subName, "string") then return nil end
    if (subName or "") ~= (rank or "") then return nil end

    local count = S.Call(tooltip.NumLines, tooltip)
    if not S.Integer(count) or count > 12 then return nil end
    local body, passiveShown, rankShown, processed
    for index, line in ipairs(data.lines) do
        if index > count or not S.Public(line, "table") then return nil end
        local left, right, kind = line.leftText, line.rightText, line.type
        if not S.Integer(line.lineIndex) or line.lineIndex ~= index
            or (not S.Public(left, "nil") and not S.Public(left, "string"))
            or (not S.Public(right, "nil") and not S.Public(right, "string"))
            or (not S.Public(kind, "nil") and not S.Public(kind, "number")) then return nil end
        if left == "" then left = nil end
        if right == "" then right = nil end
        if not displayedSide(tooltip, tooltip.GetLeftLine, index, left)
            or not displayedSide(tooltip, tooltip.GetRightLine, index, right) then return nil end

        local untyped = kind == nil or kind == lineTypes.None
        if index == 1 then
            if left ~= entry.name or (not untyped and kind ~= lineTypes.SpellName)
                or (right and right ~= SPELL_PASSIVE and right ~= rank) then return nil end
            passiveShown = right ~= nil and right == SPELL_PASSIVE
            rankShown = right ~= nil and right == rank
        elseif (untyped or kind == lineTypes.Blank) and not left and not right then
            -- Blank native separators contain no source text.
        elseif rank and untyped and left == rank and not right then
            if body or rankShown then return nil end
            rankShown = true
        elseif (untyped or kind == lineTypes.SpellPassive) and left and left == SPELL_PASSIVE and not right then
            if body or passiveShown then return nil end
            passiveShown = true
        else
            if body or not left or right or (not untyped and kind ~= lineTypes.SpellDescription) then
                return nil
            end
            body = left
        end
        processed = index
    end
    if body and processed == count then return { body } end
end

local function professionHelperTitle(tooltip, info, data, id, title)
    local banks, types = Enum.SpellBookSpellBank, Enum.SpellBookItemType
    if not banks or not types or not C_SpellBook then return nil end
    local slot, bank = argument(info, 1), argument(info, 2)
    if not S.Integer(slot) or not S.Public(bank, "number") or bank ~= banks.Player then return nil end
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Public(data.lines, "table") then return nil end
    local header = data.lines[1]
    local name = title.originalName
    if not S.Public(header, "table") or not S.Public(header.leftText, "string") or header.leftText ~= name
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, name) then return nil end
    local entry = S.Call(C_SpellBook.GetSpellBookItemInfo, slot, bank)
    if not S.Public(entry, "table") or not S.Integer(entry.spellID) or entry.spellID ~= id
        or not S.Public(entry.itemType, "number") or entry.itemType ~= types.Spell
        or not S.Public(entry.name, "string") or entry.name ~= name then return nil end
    return {key = "profession-helper:" .. id, name = name, titleOnly = title}
end

local function directAction(info, actionKind, expectedID)
    local slot = argument(info, 1)
    if not S.Integer(slot) or type(GetActionInfo) ~= "function" then return false end
    local ok, kind, id = pcall(GetActionInfo, slot)
    return ok and S.Public(kind, "string") and kind == actionKind and S.Integer(id) and id == expectedID
end

local function stanceSpellID(tooltip, info, data)
    local slot = argument(info, 1)
    local bar = StanceBar
    if not S.Integer(slot) or slot > 10 or not S.Public(bar, "table")
        or not S.Public(bar.actionButtons, "table") or type(GetShapeshiftFormInfo) ~= "function" then return nil end
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data) then return nil end
    local button = bar.actionButtons[slot]
    local owner = S.Call(tooltip.GetOwner, tooltip)
    if not S.Public(button, "table") or not S.Public(owner, "table") or not rawequal(button, owner) then return nil end
    local ownerSlot, count = S.Call(button.GetID, button), S.Call(GetNumShapeshiftForms)
    if not S.Integer(ownerSlot) or ownerSlot ~= slot or not S.Integer(count) or slot > count then return nil end

    -- SetShapeshift takes a slot. Read the current spell from the same native
    -- getter used by the stance bar, never from the button's cached spell ID.
    local ok, _, _, _, spellID = pcall(GetShapeshiftFormInfo, slot)
    if not ok or not S.Integer(spellID) then return nil end
    if not S.Public(data.type, "nil")
        and (not S.Public(data.type, "number") or data.type ~= Enum.TooltipDataType.Spell) then return nil end
    if not S.Public(data.id, "nil") and (not S.Integer(data.id) or data.id ~= spellID) then return nil end
    return spellID
end

local function learnedPlayerSpell(info, spellID, name)
    local banks, types = Enum.SpellBookSpellBank, Enum.SpellBookItemType
    if not C_SpellBook or not banks or not types then return false end
    local slot, bank = argument(info, 1), argument(info, 2)
    if not S.Integer(slot) or not S.Public(bank, "number") or bank ~= banks.Player then return false end
    local entry = S.Call(C_SpellBook.GetSpellBookItemInfo, slot, bank)
    return S.Public(entry, "table") and S.Integer(entry.spellID) and entry.spellID == spellID
        and S.Public(entry.name, "string") and entry.name == name
        and S.Public(entry.itemType, "number") and entry.itemType == types.Spell
        and S.Public(entry.isPassive, "boolean") and not entry.isPassive
end

local function blankSpellRows(tooltip, first, last)
    for index = first, last do
        if not displayedSide(tooltip, tooltip.GetLeftLine, index, nil)
            or not displayedSide(tooltip, tooltip.GetRightLine, index, nil) then return false end
    end
    return true
end

local function visibleDescription(tooltip, data, maxParts, complete, talent, talentLast)
    local types = Enum.TooltipDataLineType
    if not types or not S.Public(types.SpellDescription, "number") then return nil end
    local parts, previous, first = {}, 1
    for index, line in ipairs(data.lines) do
        if index > 80 or not S.Public(line, "table") then return nil end
        local kind = line.type
        if not S.Public(kind, "nil") and not S.Public(kind, "number") then return nil end
        if kind == types.SpellDescription then
            local left, right, visibleIndex = line.leftText, line.rightText, line.lineIndex
            if #parts == maxParts or (not talent and index < 2)
                or not S.Integer(visibleIndex) or visibleIndex <= previous or visibleIndex > 80
                or not S.Public(left, "string") or #left > 8192
                or (not S.Public(right, "nil") and not (S.Public(right, "string") and right == ""))
                or not displayedSide(tooltip, tooltip.GetLeftLine, visibleIndex, left)
                or not displayedSide(tooltip, tooltip.GetRightLine, visibleIndex, nil) then return nil end
            if complete and #parts > 0 and not blankSpellRows(tooltip, previous + 1, visibleIndex - 1) then return nil end
            first = first or visibleIndex
            parts[#parts + 1] = left
            previous = visibleIndex
        end
    end
    if #parts == 0 then return nil end
    if complete then
        local count = talentLast or S.Call(tooltip.NumLines, tooltip)
        if not S.Integer(count) or count < previous or count > 80
            or not blankSpellRows(tooltip, previous + 1, count) then return nil end
    end
    return table.concat(parts, "\n\n"), first
end

local function visibleSpellBody(tooltip, info, getter, data, spellID, name, maxParts, complete)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(info, "table") or not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, name) then return nil end
    if not ((getter == "GetAction" and directAction(info, "spell", spellID))
        or (getter == "GetSpellBookItem" and learnedPlayerSpell(info, spellID, name))
        or (getter == "GetShapeshift" and stanceSpellID(tooltip, info, data) == spellID)
        or (getter == "GetSpellByID" and directFlyoutSpell(tooltip, info, spellID))) then return nil end
    return visibleDescription(tooltip, data, maxParts, complete)
end

local function stripUntranslatedSuffix(body, suffix)
    suffix = " " .. suffix
    body = body:gsub("%s+", " "):match("^ *(.-) *$")
    if body:sub(-#suffix) == suffix then return body:sub(1, -#suffix - 1) end
end

local function nativeActionSlot(owner, slot)
    local mixin = ActionBarActionButtonMixin
    return S.Public(mixin, "table") and S.Integer(owner.action) and owner.action == slot
        and S.Public(owner.SetTooltip, "function") and S.Public(mixin.SetTooltip, "function")
        and rawequal(owner.SetTooltip, mixin.SetTooltip)
end

local function nativeCombatPetSpell(owner, slot)
    local bar = PetActionBar
    if slot > 10 or not S.Public(bar, "table") or not S.Public(bar.actionButtons, "table")
        or type(GetPetActionInfo) ~= "function" then return nil end
    local forbidden = S.Call(bar.IsForbidden, bar)
    local button = bar.actionButtons[slot]
    local buttonSlot = S.Call(owner.GetID, owner)
    if not S.Public(forbidden, "boolean") or forbidden or not S.Public(button, "table")
        or not rawequal(button, owner) or not S.Integer(buttonSlot) or buttonSlot ~= slot then return nil end
    local ok, name, _, token, _, _, _, id = pcall(GetPetActionInfo, slot)
    if ok and S.Public(token, "boolean") and not token and S.Integer(id) and S.Public(name, "string") then
        return id, name
    end
end

local function publicCombatAction(tooltip, info, data)
    local slot = argument(info, 1)
    if not S.Integer(slot) then return nil end
    local owner = S.Call(tooltip.GetOwner, tooltip)
    if not S.Public(owner, "table") then return nil end
    local forbidden = S.Call(owner.IsForbidden, owner)
    if not S.Public(forbidden, "boolean") or forbidden then return nil end
    if info.getterName == "GetAction" and data.type == Enum.TooltipDataType.Item then
        local itemID = data.id
        if not S.ItemTranslation or not S.Integer(itemID) or not nativeActionSlot(owner, slot)
            or not directAction(info, "item", itemID) then return nil end
        local title, body = S.ItemTranslation(tooltip, data, true)
        if title then return title, body, nil, slot end
        return nil
    end
    local id, petName
    if info.getterName == "GetShapeshift" then
        local bar = StanceBar
        if not S.Public(bar, "table") then return nil end
        local barForbidden = S.Call(bar.IsForbidden, bar)
        if not S.Public(barForbidden, "boolean") or barForbidden then return nil end
        id = stanceSpellID(tooltip, info, data)
    elseif info.getterName == "GetPetAction" then
        id, petName = nativeCombatPetSpell(owner, slot)
    elseif info.getterName == "GetSpellByID" then
        local flyout, mixin = SpellFlyout, SpellFlyoutPopupButtonMixin
        if not S.Public(flyout, "table") or not S.Public(mixin, "table")
            or not S.Public(owner.isActionBar, "boolean") or not owner.isActionBar
            or not S.Public(owner.SetTooltip, "function") or not S.Public(mixin.SetTooltip, "function")
            or not rawequal(owner.SetTooltip, mixin.SetTooltip) then return nil end
        local flyoutForbidden = S.Call(flyout.IsForbidden, flyout)
        if not S.Public(flyoutForbidden, "boolean") or flyoutForbidden
            or not S.Integer(data.id) or data.id ~= slot or not directFlyoutSpell(tooltip, info, slot) then return nil end
        id = slot
    else
        id = data.id
        if not S.Integer(id) or not nativeActionSlot(owner, slot) or not directAction(info, "spell", id) then return nil end
    end
    if not id then return nil end
    local key = "spell:" .. id
    if petName then
        if S.records["pet-action:" .. id] then key = "pet-action:" .. id end
    elseif not S.records[key] and S.talentCastAliases and S.talentCastAliases[id] then
        key = S.talentCastAliases[id]
    end
    local record = S.records[key]
    if not record or record.reviewStatus ~= "VERIFIED" or record.weaponStat
        or (petName and (petName ~= record.originalName or not record.lines or #record.lines == 0))
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, record.originalName) then return nil end
    local parts = type(record.requireCompleteSpellBody) == "number" and record.requireCompleteSpellBody or 2
    local body = visibleDescription(tooltip, data, parts, true)
    if body and record.untranslatedSuffix then body = stripUntranslatedSuffix(body, record.untranslatedSuffix) end
    if body then
        local title, text = S.Lookup(key, record.originalName, {body}, true)
        if title then
            if petName then return title, text, "pet", nil, record.untranslatedSuffix ~= nil end
            if info.getterName == "GetSpellByID" then return title, text, nil, nil, record.untranslatedSuffix ~= nil, true end
            return title, text, nil, slot, record.untranslatedSuffix ~= nil
        end
    end
end

function S.PublicCombatTooltip(tooltip, data)
    if type(issecretvalue) ~= "function" or type(issecrettable) ~= "function" or type(canaccesstable) ~= "function"
        or not S.Public(data, "table") or not Enum or not Enum.TooltipDataType or not S.Public(data.lines, "table")
        or (not S.Public(data.type, "number") and not S.Public(data.type, "nil")) then return nil end
    local info = S.Call(tooltip.GetProcessingTooltipInfo, tooltip)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(info, "table") or not S.Public(primary, "table") or not rawequal(info, primary)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Public(info.getterName, "string") then return nil end
    local appended = info.append
    if not S.Public(appended, "nil") and (not S.Public(appended, "boolean") or appended) then return nil end
    local getter, kind = info.getterName, data.type
    if kind ~= nil and kind == Enum.TooltipDataType.UnitAura and auraInstanceGetters[getter] and combatRestrictionsStable() then
        return publicCombatAura(tooltip, info, data)
    elseif ((getter == "GetAction" and kind ~= nil
            and (kind == Enum.TooltipDataType.Spell or kind == Enum.TooltipDataType.Item))
        or (getter == "GetSpellByID" and kind ~= nil and kind == Enum.TooltipDataType.Spell)
        or (getter == "GetPetAction" and kind ~= nil and kind == Enum.TooltipDataType.PetAction)
        or (getter == "GetShapeshift" and (kind == nil or kind == Enum.TooltipDataType.Spell))) and combatRestrictionsStable() then
        return publicCombatAction(tooltip, info, data)
    end
end

local function petTrainingContext(tooltip, info, data, id, link)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    local count = S.Call(tooltip.NumLines, tooltip)
    if not S.Public(primary, "table") or not rawequal(primary, info)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Integer(argument(info, 1)) or not S.Integer(count) or count > 24 or not C_Spell
        or not S.Public(data.lines, "table") then return nil end
    local name = S.Call(C_Spell.GetSpellName, id)
    local rank = S.Call(C_Spell.GetSpellSubtext, id)
    if not S.Public(name, "string") or name ~= link.name or not S.Public(rank, "string") or rank ~= link.rank
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, name)
        or (not displayedSide(tooltip, tooltip.GetRightLine, 1, nil)
            and not displayedSide(tooltip, tooltip.GetRightLine, 1, rank)) then return nil end
    local record = S.records[link.key]
    if not record or record.reviewStatus ~= "VERIFIED" or record.originalName ~= name then return nil end
    local body, first = visibleDescription(tooltip, data, 2, true)
    for index = 2, (first or 2) - 1 do
        local left = visibleLineText(tooltip, tooltip.GetLeftLine, index)
        if not left or (not left:match("^%s*$") and left ~= "Instant" and left ~= "Passive")
            or not displayedSide(tooltip, tooltip.GetRightLine, index, nil) then
            body = nil
            break
        end
    end
    return {key = link.key, name = name, trainingTitle = record,
        trainingPair = link.remainingSpeedPair or link.bleedPrefixPair or link.nativeTrainerPair,
        trainingBody = body, strictTrainerBody = link.strictTrainerBody}
end

function S.Context(tooltip, data, talentLast, talentComplete)
    if not S.Public(data, "table") or not Enum or not Enum.TooltipDataType then return nil end
    local processing = S.Call(tooltip.GetProcessingTooltipInfo, tooltip)
    local info = processing
    if not S.Public(info, "table") then info = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip) end
    if not S.Public(info, "table") then info = nil end
    local getter = info and info.getterName
    if not S.Public(getter, "string") then getter = nil end
    local key, id, category, talentName, tooltipRank, previewRank, talentOwner, aura
    if S.Public(data.type, "number") and data.type == Enum.TooltipDataType.Flyout then
        return flyoutContext(tooltip, info, data, getter)
    elseif getter == "GetTraitEntry" then
        local entry, rank = argument(info, 1), argument(info, 2)
        -- A missing rank can mean current or preview rank; do not guess.
        if not S.Integer(entry) or not S.Public(rank, "number") or (rank ~= 0 and not S.Integer(rank)) then
            return nil
        end
        if not C_Traits then return nil end
        local config
        config, talentName, talentOwner = displayedTalentConfig(tooltip, entry)
        if not S.Integer(config) then return nil end
        if rank == 0 then
            if not rawequal(info, processing) or not isFirstRankPreview(talentOwner, entry, info, data) then return nil end
            rank, previewRank = 1, true
        end
        local entryInfo = S.Call(C_Traits.GetEntryInfo, config, entry)
        if not S.Public(entryInfo, "table") or not S.Integer(entryInfo.definitionID) then return nil end
        local definition = S.Call(C_Traits.GetDefinitionInfo, entryInfo.definitionID)
        if not S.Public(definition, "table") or not S.Integer(definition.spellID) then return nil end
        id, category = definition.spellID, "talent"
        tooltipRank = rank
        key = "talent-spell:" .. id .. ":" .. rank
    elseif getter == "GetPetAction" then
        if not S.Public(data.type,"number") or data.type ~= Enum.TooltipDataType.PetAction then return nil end
        local slot = argument(info,1)
        if not S.Integer(slot) or slot > 10 or type(GetPetActionInfo) ~= "function" then return nil end
        -- Token commands and spell actions share the same native getter.
        -- Neither the slot nor data.id identifies a spell.
        local ok, token, _, isToken, _, _, _, spellID = pcall(GetPetActionInfo, slot)
        if not ok or not S.Public(isToken, "boolean") then return nil end
        if isToken then return petCommandContext(tooltip, info, data, token) end
        if not S.Integer(spellID) then return nil end
        local scopedKey = "pet-action:" .. spellID
        local remote = S.records[scopedKey]
        local capture = S.captureEnabled and S.CapturePetAction and S.Public(token, "string")
        if remote or capture then
            local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
            local name = remote and remote.originalName or token
            local body
            if S.Public(primary, "table") and rawequal(primary, info)
                and S.Public(info.tooltipData, "table") and rawequal(info.tooltipData, data)
                and S.Public(data.lines, "table")
                and displayedSide(tooltip, tooltip.GetLeftLine, 1, name)
                and displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then
                body = visibleDescription(tooltip, data, 2, true)
            end
            if body and capture and not remote then S.CapturePetAction(spellID, name, body) end
            if remote then
                if not body then return nil end
                return {key = scopedKey, id = spellID, category = "pet-action", name = name, lines = {body}}
            end
        end
        id, key, category = spellID, "spell:" .. spellID, "spell"
    elseif getter == "GetSpellBookItem" and S.Public(data.type, "number")
        and data.type == Enum.TooltipDataType.PetAction then
        return petCommandContext(tooltip, info, data, spellBookPetToken(info))
    elseif getter == "GetAction" and S.Public(data.type, "number") and data.type == Enum.TooltipDataType.PetAction then
        return petCommandContext(tooltip, info, data, playerBarPetToken(info))
    elseif getter == "GetShapeshift" then
        id = stanceSpellID(tooltip, info, data)
        if not id then return nil end
        key, category = "spell:" .. id, "spell"
    elseif S.Public(data.type, "number") and data.type == Enum.TooltipDataType.Spell then
        id = data.id
        if not S.Integer(id) then return nil end
        if S.flyoutTitleOnly and S.flyoutTitleOnly[id] then
            return detailedFlyoutTitle(tooltip, info, data, getter, id)
        end
        if getter == "GetTrainerService" and S.petTrainingTooltips and S.petTrainingTooltips[id] then
            return petTrainingContext(tooltip, info, data, id, S.petTrainingTooltips[id])
        end
        local helper = S.professionHelperTitles and S.professionHelperTitles[id]
        if helper and getter == "GetSpellBookItem" then
            return professionHelperTitle(tooltip, info, data, id, helper)
        end
        key, category = "spell:" .. id, "spell"
    elseif S.Public(data.type, "number") and data.type == Enum.TooltipDataType.UnitAura and C_UnitAuras then
        local unit, indexOrInstance, filter = argument(info, 1), argument(info, 2), argument(info, 3)
        if not S.Public(unit, "string") or not S.Integer(indexOrInstance) then return nil end
        if not S.Public(filter, "nil") and not S.Public(filter, "string") then return nil end
        local byInstance = getter == "GetUnitAuraByAuraInstanceID" or getter == "GetUnitBuffByAuraInstanceID"
            or getter == "GetUnitDebuffByAuraInstanceID"
        if byInstance then
            -- The tooltip getter can carry a filter, but the instance lookup
            -- takes only a unit token and the specific instance ID.
            aura = S.Call(C_UnitAuras.GetAuraDataByAuraInstanceID, unit, indexOrInstance)
        else
            local fn
            if getter == "GetUnitAura" then fn = C_UnitAuras.GetAuraDataByIndex
            elseif getter == "GetUnitBuff" then fn = C_UnitAuras.GetBuffDataByIndex
            elseif getter == "GetUnitDebuff" then fn = C_UnitAuras.GetDebuffDataByIndex end
            aura = S.Call(fn, unit, indexOrInstance, filter)
        end
        if not S.Public(aura, "table") or not S.Integer(aura.spellId) then return nil end
        id, category = aura.spellId, "aura"
        key = "aura:" .. id
        local record = S.records[key]
        if record and record.petSpeedAura
            and (unit ~= "pet" or not S.Public(aura.name, "string") or aura.name ~= record.originalName
                or (byInstance and (not S.Integer(aura.auraInstanceID) or aura.auraInstanceID ~= indexOrInstance))) then
            return nil
        end
    else return nil end
    if not S.Public(data.lines, "table") then return nil end
    if category == "spell" and getter == "GetSpellBookItem" then
        local scopedKey = "pet-spellbook:" .. id
        local petRecord = S.records[scopedKey]
        if petRecord then
            local lines = petPassiveText(tooltip, processing, data, petRecord, id)
            if not lines then return nil end
            return { key = scopedKey, id = id, category = "pet-spellbook", name = petRecord.originalName, lines = lines }
        end
    end
    local record = S.records[key]
    if category == "aura" and record and record.requireCompleteAuraBody then
        local body = completeAuraBody(tooltip, info, data, record, aura)
        if not body then return nil end
        return {key = key, id = id, category = category, name = record.originalName, lines = {body}}
    end
    if category == "aura" and record and record.requireAuraCasterLine then
        local name, lines = casterAuraText(tooltip, info, data)
        if not name then return nil end
        return { key = key, id = id, category = category, name = name, lines = lines }
    end
    -- GetTraitEntry can be appended after a separately added talent title.
    -- Its first data line is then description text, not the title.
    local lines, name = {}, talentName
    for i, line in ipairs(data.lines) do
        if i > 80 then break end
        if S.Public(line, "table") and S.Public(line.leftText, "string") then
            if not name then name = line.leftText
            elseif not (i == 1 and talentName and line.leftText == talentName) then
                lines[#lines + 1] = line.leftText
            end
        end
    end
    if not name then return nil end
    local stance = getter == "GetShapeshift"
    if stance and not displayedSide(tooltip, tooltip.GetLeftLine, 1, name) then return nil end
    local bodyInfo = stance and info or processing
    local untranslatedSuffix
    local spellSurface = getter == "GetAction" or getter == "GetSpellBookItem" or getter == "GetSpellByID" or stance
    local alias = not record and category == "spell" and S.talentCastAliases and S.talentCastAliases[id]
    if alias and S.records[alias] and name == S.records[alias].originalName and spellSurface then
        local complete = stance or getter == "GetSpellByID"
        local body = visibleSpellBody(tooltip, bodyInfo, getter, data, id, name, complete and 2 or 1, complete)
        if body then
            return { key = alias, id = id, category = "spell", name = name, lines = {body}, requireDescriptionMatch = true }
        end
    end
    local talentNode = record and (record.requireCompleteTalentBody or record.requireNativeTalentBody)
    if talentNode then
        local complete = record.requireCompleteTalentBody ~= nil
        local node = talentOwner and S.Call(talentOwner.GetNodeID, talentOwner)
        if (complete and not talentComplete) or category ~= "talent" or not S.Integer(node) or node ~= talentNode
            or not S.Public(data.type, "number") or data.type ~= Enum.TooltipDataType.Spell
            or not S.Integer(data.id) or data.id ~= id
            or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
            or not displayedSide(tooltip, tooltip.GetLeftLine, 1, name)
            or not displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then return nil end
        local body = visibleDescription(tooltip, data, complete and 2 or 1, complete, true, talentLast)
        if not body then return nil end
        lines = {body}
    elseif record and record.weaponStat then
        local body = weaponStatBody(tooltip, info, data, getter, id, name)
        if not body then return nil end
        lines = {body}
    elseif record and record.requireCompleteSpellBody then
        local parts = type(record.requireCompleteSpellBody) == "number" and record.requireCompleteSpellBody or 2
        local body = visibleSpellBody(tooltip, bodyInfo, getter, data, id, name, parts, true)
        if not body then return nil end
        if record.untranslatedSuffix then
            body = stripUntranslatedSuffix(body, record.untranslatedSuffix)
            if not body then return nil end
            untranslatedSuffix = true
        end
        lines = {body}
    elseif record and stance and (S.Public(data.type, "nil") or S.Public(data.id, "nil")) then
        local body = visibleSpellBody(tooltip, bodyInfo, getter, data, id, name, 2, true)
        if not body then return nil end
        return { key = key, id = id, category = category, name = name, lines = {body}, requireDescriptionMatch = true }
    elseif record and record.verifiedSplitDescription and category == "spell" and spellSurface then
        local body = visibleSpellBody(tooltip, bodyInfo, getter, data, id, name, 2)
        if body then lines[#lines + 1] = body end
    end
    if category == "talent" and record and record.orderedTooltip and S.settings and S.settings.descriptions then
        lines = orderedTalentText(tooltip, info, data, record, talentLast)
        if not lines then return nil end
    end
    return { key = key, id = id, category = category, name = name, lines = lines, rank = tooltipRank,
        previewRank = previewRank, untranslatedSuffix = untranslatedSuffix }
end

local powerLabels = {
    Mana = "ใช้มานา",
    Rage = "ใช้ความโกรธ",
    Focus = "ใช้สมาธิ",
    Energy = "ใช้พลังงาน",
}

local function flatPowerCost(visibleLine, getCosts, ...)
    -- Only a simple enUS cost line whose amount agrees with the spell API.
    -- Percent, per-second, conditional and optional costs stay in English.
    if not Enum.PowerType or not S.Public(visibleLine, "string") or #visibleLine > 32 then return nil end
    local amount, power = visibleLine:match("^([1-9]%d*) (%a+)$")
    if not power or not powerLabels[power] or not S.Public(Enum.PowerType[power], "number") then return nil end
    local costs = S.Call(getCosts, ...)
    if not S.Public(costs, "table") or next(costs) ~= 1 or next(costs, 1) ~= nil then return nil end
    local info = costs[1]
    if not S.Public(info, "table") or not S.Public(info.type, "number") or info.type ~= Enum.PowerType[power]
        or not S.Integer(info.cost) or info.cost ~= tonumber(amount)
        or not S.Integer(info.minCost) or info.minCost ~= info.cost
        or not S.Public(info.costPercent, "number") or info.costPercent ~= 0
        or not S.Public(info.costPerSec, "number") or info.costPerSec ~= 0
        or not S.Public(info.requiredAuraID, "number") or info.requiredAuraID ~= 0 then return nil end
    return powerLabels[power] .. " " .. amount
end

local function currentSpellInfo(context)
    if not C_Spell then return nil end
    local spell = S.Call(C_Spell.GetSpellInfo, context.id)
    if S.Public(spell, "table") and S.Integer(spell.spellID) and spell.spellID == context.id
        and S.Public(spell.name, "string") and spell.name == context.name then return spell end
end

local function fixedSpellRange(context, line)
    local left, right = line.leftText, line.rightText
    local leftPublic, rightPublic = S.Public(left, "string"), S.Public(right, "string")
    if (not leftPublic and not S.Public(left, "nil")) or (not rightPublic and not S.Public(right, "nil")) then return nil end
    local pattern = "^([1-9]%d*) yd range$"
    local leftAmount = leftPublic and #left <= 32 and left:match(pattern)
    local rightAmount = rightPublic and #right <= 32 and right:match(pattern)
    if leftAmount and rightAmount then return nil end
    local amount = leftAmount or rightAmount
    if not amount then return nil end
    local spell = currentSpellInfo(context)
    if not spell or not S.Public(spell.minRange, "number") or spell.minRange ~= 0
        or not S.Integer(spell.maxRange) or spell.maxRange ~= tonumber(amount) then return nil end
    return "ระยะ " .. amount .. " หลา"
end

local cooldownUnits = { sec = "วินาที", min = "นาที", hour = "ชั่วโมง", day = "วัน" }

local function spellRankLabel(text)
    if not S.Public(text, "string") or #text > 32 then return nil end
    local rank = text:match("^Rank ([1-9]%d*)$")
    if rank then return "แรงก์ " .. rank end
end

local function cooldownLabel(text)
    if not text or #text > 32 then return nil end
    local amount, unit = text:match("^(%d+%.?%d*) (%a+) cooldown$")
    if not unit or not cooldownUnits[unit] then return nil end
    local number = tonumber(amount)
    if number > 0 and ("%.2g"):format(number) == amount then return "คูลดาวน์ " .. amount .. " " .. cooldownUnits[unit] end
end

local function spellCastLabel(tooltip, data, context, passive)
    local types = Enum.TooltipDataLineType
    if not types or not S.Public(passive, "boolean") or not S.Public(data.lines, "table") then return nil end
    local title = data.lines[1]
    if not S.Public(title, "table") or not S.Public(title.leftText, "string") or title.leftText ~= context.name
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, context.name) then return nil end
    if passive and S.Public(title.rightText, "string") and title.rightText == "Passive"
        and displayedSide(tooltip, tooltip.GetRightLine, 1, "Passive") then return "ติดตัว" end

    local candidate
    for index = 2, 3 do
        local line = data.lines[index]
        if not S.Public(line, "table") then break end
        local kind, left, right = line.type, line.leftText, line.rightText
        if not S.Public(kind, "number") or kind == types.SpellDescription then break end
        if (kind == types.None or (passive and kind == types.SpellPassive))
            and S.Public(left, "string") and #left <= 32 then
            local amount, unit = left:match("^(%d+%.?%d*) (%a+) cast$")
            if (passive and left == "Passive")
                or (not passive and (left == "Instant" or left == "Channeled" or unit == "sec" or unit == "min")) then
                if candidate or not S.Integer(line.lineIndex) or line.lineIndex ~= index
                    or (not S.Public(right, "nil") and not S.Public(right, "string"))
                    or not displayedSide(tooltip, tooltip.GetLeftLine, index, left)
                    or not displayedSide(tooltip, tooltip.GetRightLine, index, right ~= "" and right or nil) then return nil end
                candidate = { text = left, amount = amount, unit = unit, right = right }
            end
        end
    end
    if not candidate then return nil end
    if passive then return "ติดตัว" end
    local spell = currentSpellInfo(context)
    if not spell or not S.Public(spell.castTime, "number") then return nil end
    local cast
    if spell.castTime == 0 then
        if candidate.text == "Instant" then cast = "ร่ายทันที"
        elseif candidate.text == "Channeled" then cast = "ร่ายต่อเนื่อง" end
    elseif S.Integer(spell.castTime) and candidate.amount then
        local minutes = spell.castTime >= 60000
        local unit = minutes and "min" or "sec"
        local amount = ("%.2g"):format(spell.castTime / (minutes and 60000 or 1000))
        if candidate.unit == unit and candidate.amount == amount then
            cast = "ใช้เวลาร่าย " .. candidate.amount .. " " .. cooldownUnits[unit]
        end
    end
    if not cast then return nil end
    -- The right column is the tooltip's displayed label, not an active
    -- countdown. Keep its amount and unit exactly as the client shows them.
    local cooldown = cooldownLabel(candidate.right)
    return cooldown and cast .. "\n" .. cooldown or cast
end

function S.ActionCastMetadata(tooltip, data, context)
    if context.category ~= "spell" or not C_Spell or type(GetActionInfo) ~= "function" then return nil end
    local info = S.Call(tooltip.GetProcessingTooltipInfo, tooltip)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(info, "table") or not S.Public(primary, "table") or not rawequal(info, primary)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Public(info.getterName, "string") or info.getterName ~= "GetAction" then return nil end
    if not directAction(info, "spell", context.id) then return nil end
    local cast = spellCastLabel(tooltip, data, context, S.Call(C_Spell.IsSpellPassive, context.id))
    local types = Enum.TooltipDataLineType
    if not types or not rawequal(tooltip, GameTooltip) or not S.Public(data.lines, "table") then return cast end
    local title, details = data.lines[1], data.lines[2]
    if not S.Public(title, "table") or not S.Public(title.leftText, "string") or title.leftText ~= context.name
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, context.name) then return cast end
    local owner = S.Call(tooltip.GetOwner, tooltip)
    if not S.Public(owner, "table") then return cast end
    local forbidden = S.Call(owner.IsForbidden, owner)
    if not S.Public(forbidden, "boolean") or forbidden or not nativeActionSlot(owner, argument(info, 1)) then
        return cast
    end
    local lines = {}
    local rank = spellRankLabel(title.rightText)
    if rank and displayedSide(tooltip, tooltip.GetRightLine, 1, title.rightText) then
        local subtext = S.Call(C_Spell.GetSpellSubtext, context.id)
        if S.Public(subtext, "string") and subtext == title.rightText then lines[#lines + 1] = rank end
    end
    if S.Public(details, "table") and S.Public(details.type, "number") and details.type == types.None
        and S.Integer(details.lineIndex) and details.lineIndex == 2 then
        local left, right = details.leftText, details.rightText
        if (S.Public(left, "string") or S.Public(left, "nil"))
            and (S.Public(right, "string") or S.Public(right, "nil"))
            and displayedSide(tooltip, tooltip.GetLeftLine, 2, left ~= "" and left or nil)
            and displayedSide(tooltip, tooltip.GetRightLine, 2, right ~= "" and right or nil) then
            local cost = flatPowerCost(left, C_Spell.GetSpellPowerCost, context.id)
            if cost then lines[#lines + 1] = cost end
            local range = fixedSpellRange(context, details)
            if range then lines[#lines + 1] = range end
        end
    end
    if cast then lines[#lines + 1] = cast end
    if #lines > 0 then return table.concat(lines, "\n") end
end

function S.SpellbookMetadata(tooltip, data, context)
    if context.category ~= "spell" or not S.Public(tooltip, "table") or not C_SpellBook
        or not Enum.SpellBookSpellBank or not Enum.SpellBookItemType then return nil end
    local info = S.Call(tooltip.GetProcessingTooltipInfo, tooltip)
    local primary = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip)
    if not S.Public(info, "table") or not S.Public(primary, "table") or not rawequal(info, primary)
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Public(info.getterName, "string") or info.getterName ~= "GetSpellBookItem" then return nil end
    local slot, bank = argument(info, 1), argument(info, 2)
    local banks, types = Enum.SpellBookSpellBank, Enum.SpellBookItemType
    if not S.Integer(slot) or not S.Public(bank, "number") or (bank ~= banks.Player and bank ~= banks.Pet) then return nil end
    local entry = S.Call(C_SpellBook.GetSpellBookItemInfo, slot, bank)
    if not S.Public(entry, "table") or not S.Integer(entry.spellID) or entry.spellID ~= context.id
        or not S.Public(entry.itemType, "number") or (entry.itemType ~= types.Spell and entry.itemType ~= types.FutureSpell)
        or not S.Public(entry.name, "string") or entry.name ~= context.name then return nil end

    local lines = {}
    local rank = spellRankLabel(entry.subName)
    if rank then lines[#lines + 1] = rank end
    local level = S.Call(C_SpellBook.GetSpellBookItemLevelLearned, slot, bank)
    -- The current spellbook API incorporates level-link changes.
    if S.Integer(level) then lines[#lines + 1] = "เลเวลที่เรียนสกิล " .. level end
    if entry.itemType == types.Spell and S.Public(data.lines, "table") then
        local title, details = data.lines[1], data.lines[2]
        if S.Public(title, "table") and S.Public(title.leftText, "string") and title.leftText == context.name
            and S.Public(details, "table") then
            local cost = flatPowerCost(details.leftText, C_SpellBook.GetSpellBookItemPowerCost, slot, bank)
            if cost then lines[#lines + 1] = cost end
            local range = fixedSpellRange(context, details)
            if range then lines[#lines + 1] = range end
        end
        local cast = spellCastLabel(tooltip, data, context, entry.isPassive)
        if cast then lines[#lines + 1] = cast end
    end
    if #lines > 0 then return table.concat(lines, "\n") end
end

-- Build 70862 LegacyConsts IDs and corresponding native heading strings.
local legacyTalentTrees = {
    [1187] = { "Professions", "ด้านอาชีพ" },
    [1188] = { "Adventure", "ด้านผจญภัย" },
    [1189] = { "Resourcefulness", "ด้านความมีไหวพริบ" },
}

local function visibleTalentTree(owner, talentFrame)
    local nodeID = S.Call(owner.GetNodeID, owner)
    local node = S.Call(owner.GetNodeInfo, owner)
    local tree = S.Call(talentFrame.GetTalentTreeID, talentFrame)
    if not S.Integer(nodeID) or not S.Public(node, "table") or not S.Integer(node.ID) or node.ID ~= nodeID
        or not S.Public(node.groupIDs, "table") or not S.Integer(tree) then return nil end
    for index, group in ipairs(node.groupIDs) do
        if index > 64 or not S.Integer(group) then return nil end
    end
    local name = S.Call(talentFrame.GetTraitTreeName, talentFrame, tree, node.groupIDs)
    if not S.Public(name, "string") or #name > 64 or not name:match("^[%a][%a ]*$") then return nil end
    local classGroups = S.talentTreeNames and S.talentTreeNames[tree]
    if classGroups then
        for _, group in ipairs(node.groupIDs) do
            local row = classGroups[group]
            if row and row[2] == name then return name, row[3] end
        end
    end
    local legacy = legacyTalentTrees[tree]
    if legacy and legacy[1] == name then return name, nil, legacy[2] end
    return name
end

-- Exact, visible instructions from the pinned enUS talent button UI.
local talentFooterText = {
    ["Requires all preceding talents"] = "ต้องเรียนพรสวรรค์ก่อนหน้าที่เชื่อมมาทั้งหมด",
    ["Click to learn"] = "คลิกเพื่อเรียนพรสวรรค์",
    ["Right click to unlearn"] = "คลิกขวาเพื่อยกเลิกพรสวรรค์",
    ["Shift click to learn all connected history nodes"] = "กด Shift ค้างแล้วคลิกเพื่อเรียนพรสวรรค์ทั้งหมดที่เชื่อมถึงกันในประวัติการลงแต้ม",
    ["Right click to clear all history nodes"] = "คลิกขวาเพื่อล้างประวัติการลงแต้มทั้งหมด",
    ["No active links. Reconnect or unlearn this talent."] = "ไม่มีเส้นเชื่อมที่ใช้งานอยู่ ให้เชื่อมใหม่หรือยกเลิกพรสวรรค์นี้",
    ["Spend more points to restore this talent or right click to unlearn it"] = "ลงแต้มเพิ่มเพื่อให้พรสวรรค์นี้กลับมาใช้งานได้ หรือคลิกขวาเพื่อยกเลิก",
}

local function translateTalentRequirement(text, tree, className, legacyName)
    text = text:match("^|[cC][fF][fF][fF][fF]2020(.-)|[rR]$") or text
    if talentFooterText[text] then return talentFooterText[text] end
    if not tree then return nil end
    -- SharedString 911 and 1318 include native plural tokens. The amount
    -- comes only from the completed tooltip, which may retain those tokens.
    local amount, rest = text:match("^Spend ([1-9]%d?) more (.+)$")
    if not amount then return nil end
    local points = amount == "1" and "point" or "points"
    rest = rest:match("^" .. points .. " in (.+)$") or rest:match("^|4point:points; in (.+)$")
    if not rest then return nil end
    local talent = amount == "1" and "Talent" or "Talents"
    if rest == tree .. " " .. talent or rest == tree .. " |4Talent:Talents;" then
        return "ต้องลงแต้มพรสวรรค์สาย " .. (className or tree) .. " เพิ่มอีก " .. amount .. " แต้ม"
    elseif rest == "the " .. tree .. " Legacy Tree" then
        local name = legacyName or "สาย " .. tree
        return "ต้องลงแต้มในผัง Legacy " .. name .. " เพิ่มอีก " .. amount .. " แต้ม"
    end
end

function S.TalentRequirements(tooltip, data)
    local info = S.Call(tooltip.GetProcessingTooltipInfo, tooltip)
    if not S.Public(info, "table") or not S.Public(info.getterName, "string") or info.getterName ~= "GetTraitEntry"
        or not S.Public(info.tooltipData, "table") or not rawequal(info.tooltipData, data)
        or not S.Public(data.lines, "table") then return nil end
    local entry = argument(info, 1)
    if not S.Integer(entry) then return nil end
    local _, name, owner, talentFrame = displayedTalentConfig(tooltip, entry)
    local count = S.Call(tooltip.NumLines, tooltip)
    if not owner or not S.Integer(count) or count > 80
        or not displayedSide(tooltip, tooltip.GetLeftLine, 1, name)
        or not displayedSide(tooltip, tooltip.GetRightLine, 1, nil) then return nil end

    -- Native prerequisite lines are appended outside the trait description.
    local last = 1
    for index, line in ipairs(data.lines) do
        if index > 80 or not S.Public(line, "table") or not S.Integer(line.lineIndex)
            or line.lineIndex <= last or line.lineIndex > count then return nil end
        last = line.lineIndex
    end
    if last == 1 or last == count then return nil end
    local tree, className, legacyName = visibleTalentTree(owner, talentFrame)
    local translated, completeTail = {}, true
    for index = last + 1, count do
        local region = S.Call(tooltip.GetLeftLine, tooltip, index)
        local shown = S.Public(region, "table") and S.Call(region.IsShown, region)
        local text = S.Public(shown, "boolean") and shown and S.Call(region.GetText, region)
        local requirement
        if S.Public(text, "string") and #text <= 128 and displayedSide(tooltip, tooltip.GetRightLine, index, nil) then
            requirement = translateTalentRequirement(text, tree, className, legacyName)
        end
        if requirement then
            translated[#translated + 1] = requirement
        elseif not displayedSide(tooltip, tooltip.GetLeftLine, index, nil)
            or not displayedSide(tooltip, tooltip.GetRightLine, index, nil) then
            completeTail = false
        end
    end
    if #translated > 0 then
        return { text = table.concat(translated, "\n"), limit = completeTail and last or nil }
    end
end
