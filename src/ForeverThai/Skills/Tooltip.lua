local _, addon = ...
local S = addon.skills
local function createReader(name)
    local reader = CreateFrame("Frame", name, UIParent)
    reader:SetSize(350, 80)
    reader:SetFrameStrata("TOOLTIP")
    reader:SetClampedToScreen(true)
    reader:EnableMouse(false)
    reader:Hide()
    local background = reader:CreateTexture(nil, "BACKGROUND")
    background:SetAllPoints()
    background:SetColorTexture(0.035, 0.045, 0.065, 0.97)
    local title = S.CreateTextBlock(reader)
    title:SetPoint("TOPLEFT", 12, -10)
    local body = S.CreateTextBlock(reader)
    body:SetPoint("TOPLEFT", title, "BOTTOMLEFT", 0, -8)
    return reader, title, body
end
local frame, title, body = createReader("AlphaWoWSkillsReader")
local combatFrame, combatTitle, combatBody = createReader("AlphaWoWCombatReader")
S.reader = frame
local combatTooltip, combatUnit, combatSlot, combatLayout, combatFlyout
local flyoutHooks = setmetatable({}, { __mode = "k" })
local function hideCombatTooltip()
    combatUnit, combatSlot, combatFlyout = nil, nil, nil
    combatFrame:Hide()
end
local hooked = setmetatable({}, { __mode = "k" })
local owner, ownerBasic, ownerHasSnapshot
local anchorPoint, anchorRelative
local function hideFor(tooltip)
    if rawequal(owner, tooltip) then frame:Hide() end
end
local function dimension(value)
    return S.Public(value, "number") and value > 0 and value < 100000
end
local function readerAnchor(tooltip, height, independent)
    local screenWidth, screenHeight = S.Call(UIParent.GetWidth, UIParent), S.Call(UIParent.GetHeight, UIParent)
    local reader = independent and combatFrame or frame
    local readerWidth = S.Call(reader.GetWidth, reader)
    local parentScale = S.Call(UIParent.GetEffectiveScale, UIParent)
    local tooltipScale = S.Call(tooltip.GetEffectiveScale, tooltip)
    local ok, left, bottom, width, nativeHeight = pcall(tooltip.GetRect, tooltip)
    if not ok or not dimension(screenWidth) or not dimension(screenHeight) or not dimension(readerWidth)
        or not dimension(parentScale) or not dimension(tooltipScale)
        or not dimension(width) or not dimension(nativeHeight)
        or not S.Public(left, "number") or not S.Public(bottom, "number")
        or not (math.abs(left) < 100000 and math.abs(bottom) < 100000) then
        -- A post-call can run before the native tooltip has a rectangle.
        if independent then return nil end
        return "TOPRIGHT", "TOPLEFT", -8, 0
    end
    if readerWidth > screenWidth or height > screenHeight then return nil end
    local scale = tooltipScale / parentScale
    local right, top = (left + width) * scale, (bottom + nativeHeight) * scale
    if independent then
        left, bottom = left * scale, bottom * scale
        if scale < 0.1 or scale > 10 or left < 0 or bottom < 0 or right > screenWidth or top > screenHeight then
            return nil
        end
        if left >= readerWidth + 8 then return "TOPRIGHT", "BOTTOMLEFT", left - 8, top end
        if screenWidth - right >= readerWidth + 8 then return "TOPLEFT", "BOTTOMLEFT", right + 8, top end
        if screenHeight - top >= height + 8 then return "BOTTOMLEFT", "BOTTOMLEFT", left, top + 8 end
        if bottom >= height + 8 then return "TOPLEFT", "BOTTOMLEFT", left, bottom - 8 end
        return nil
    end
    if left * scale >= readerWidth + 8 then return "TOPRIGHT", "TOPLEFT", -8, 0 end
    if screenWidth - right >= readerWidth + 8 then return "TOPLEFT", "TOPRIGHT", 8, 0 end
    if screenHeight - top >= height + 8 then return "BOTTOMLEFT", "TOPLEFT", 0, 8 end
    if bottom * scale >= height + 8 then return "TOPLEFT", "BOTTOMLEFT", 0, -8 end
end

local function displayCombatTooltip(tooltip, data)
    if combatTooltip and S.Public(tooltip, "table") and rawequal(tooltip, combatTooltip)
        and S.Public(GameTooltip, "table") and rawequal(tooltip, GameTooltip)
        and S.supported and S.settings and S.settings.enabled and S.PublicCombatTooltip then
        local forbidden = S.Call(tooltip.IsForbidden, tooltip)
        local shown = S.Public(forbidden, "boolean") and not forbidden and S.Call(tooltip.IsShown, tooltip)
        if S.Public(shown, "boolean") and shown then
            local heading, text, unit, slot, partial, flyout = S.PublicCombatTooltip(tooltip, data)
            if heading and (not flyout or (S.Public(SpellFlyout, "table") and flyoutHooks[SpellFlyout])) then
                text = S.WithPartialNotice(text, partial)
                local size = S.settings.fontSize
                if not combatLayout or combatLayout.heading ~= heading or combatLayout.text ~= text
                    or combatLayout.size ~= size then
                    combatLayout = nil
                    local titleHeight = combatTitle:Draw(heading, 326, size + 1, 1, 0.84, 0.55)
                    local bodyHeight = combatBody:Draw(text, 326, size)
                    if titleHeight and bodyHeight then
                        local height = titleHeight + bodyHeight + 36
                        combatLayout = {heading = heading, text = text, size = size, height = height}
                        combatFrame:SetHeight(height)
                    end
                end
                if combatLayout then
                    local point, relative, x, y = readerAnchor(tooltip, combatLayout.height, true)
                    if point then
                        if combatLayout.point ~= point or combatLayout.x ~= x or combatLayout.y ~= y then
                            combatFrame:ClearAllPoints()
                            combatFrame:SetPoint(point, UIParent, relative, x, y)
                            combatLayout.point, combatLayout.x, combatLayout.y = point, x, y
                        end
                        combatUnit, combatSlot, combatFlyout = unit, slot, flyout
                        if not combatFrame:IsShown() then combatFrame:Show() end
                        return "shown"
                    end
                end
            end
        end
    end
    hideCombatTooltip()
    return "combat"
end
local function placeReader(tooltip, height)
    local point, relative, x, y = readerAnchor(tooltip, height)
    if not point then return false end
    if frame:GetHeight() ~= height then frame:SetHeight(height) end
    if not rawequal(owner, tooltip) or anchorPoint ~= point or anchorRelative ~= relative then
        anchorPoint, anchorRelative = nil, nil
        frame:ClearAllPoints()
        frame:SetPoint(point, tooltip, relative, x, y)
        anchorPoint, anchorRelative = point, relative
    end
    return true
end
local function placeHint(tooltip, overflow)
    local titleHeight = title:Draw("คำแปลภาษาไทย", 326, S.settings.fontSize + 1, 1, 0.84, 0.55)
    local hint = overflow and S.longTextHint or "พิมพ์ /alphathai read เพื่ออ่านทั้งหมด"
    local bodyHeight = body:Draw(hint, 326, S.settings.fontSize)
    if not titleHeight or not bodyHeight then return "text-render-failed" end
    local height = titleHeight + bodyHeight + 36
    if height > UIParent:GetHeight() - 40 or not placeReader(tooltip, height) then return "no-room" end
end
local function reflowReader(tooltip)
    if placeReader(tooltip, frame:GetHeight()) then return end
    if not ownerHasSnapshot or placeHint(tooltip) then frame:Hide() end
end
local function repositionReader(tooltip)
    if not rawequal(owner, tooltip) or not frame:IsShown()
        or (InCombatLockdown and InCombatLockdown()) then return end
    if not pcall(reflowReader, tooltip) then
        S.stats.errors = S.stats.errors + 1
        frame:Hide()
    end
end
local function show(tooltip, heading, text, basic)
    local titleHeight = title:Draw(heading, 326, S.settings.fontSize + 1, 1, 0.84, 0.55)
    local bodyHeight = body:Draw(text, 326, S.settings.fontSize)
    if not titleHeight or not bodyHeight then frame:Hide(); return "text-render-failed" end
    local remembered = S.RememberLongText and S.RememberLongText(heading,text)
    local height = titleHeight + bodyHeight + 36
    local overflow = height > UIParent:GetHeight() - 40
    if overflow then
        S.stats.overflow = (S.stats.overflow or 0) + 1
    end
    if overflow or not placeReader(tooltip, height) then
        local error = not remembered and "no-room" or placeHint(tooltip, overflow)
        if error then
            frame:Hide()
            return overflow and error == "no-room" and "overflow" or error
        end
    end
    owner, ownerBasic, ownerHasSnapshot = tooltip, basic, remembered
    if not hooked[tooltip] then
        tooltip:HookScript("OnShow", repositionReader)
        tooltip:HookScript("OnHide", function(self) if owner == self then frame:Hide() end end)
        tooltip:HookScript("OnTooltipCleared", function(self) if owner == self then frame:Hide() end end)
        hooked[tooltip] = true
    end
    frame:Show()
    return "shown"
end
local function translatedHeading(record)
    if S.settings.englishNames then return record.translatedName .. " (" .. record.originalName .. ")" end
    return record.translatedName
end

local function trainingText(context)
    local body = context.trainingBody
    if body and context.trainingPair then
        local text = S.RenderDB2(context.trainingPair, body)
        if text then
            if not S.settings.descriptions then text = ""
            elseif S.settings.original then text = text .. "\n" .. body end
            return translatedHeading(context.trainingTitle), text
        end
    end
    if body and not context.strictTrainerBody then
        local heading, text = S.Lookup(context.key, context.name, {body}, true)
        if heading then return heading, text end
    end
    return translatedHeading(context.trainingTitle), ""
end

local function display(tooltip, data, requirements, talentComplete)
    if InCombatLockdown and InCombatLockdown() then
        frame:Hide()
        return displayCombatTooltip(tooltip, data)
    end
    if combatFrame:IsShown() then hideCombatTooltip() end
    if not S.settings or not S.settings.enabled or not S.supported then frame:Hide(); return "disabled" end
    local heading, text
    local outcome = "unmatched"
    if S.ItemTranslation and S.Public(data, "table") and S.Public(data.type, "number")
        and Enum and Enum.TooltipDataType and data.type == Enum.TooltipDataType.Item then
        heading, text = S.ItemTranslation(tooltip, data)
    else
        local context = S.Context(tooltip, data, requirements and requirements.limit, talentComplete)
        if not context then
            S.stats.noContext = S.stats.noContext + 1
            hideFor(tooltip)
            return "no-context"
        end
        if context.titleOnly then return show(tooltip, translatedHeading(context.titleOnly), "") end
        if context.trainingTitle then
            heading, text = trainingText(context)
            return show(tooltip, heading, text)
        end
        if S.captureEnabled and S.Capture then S.Capture(context) end
        local before = S.stats.outdated
        heading, text = S.Lookup(context.key, context.name, context.lines, context.requireDescriptionMatch)
        if not heading then outcome = S.stats.outdated ~= before and "text-mismatch" or "missing" end
        if heading and S.settings.descriptions and S.SpellbookMetadata then
            local metadata = S.SpellbookMetadata(tooltip, data, context)
            if not metadata and S.ActionCastMetadata then metadata = S.ActionCastMetadata(tooltip, data, context) end
            if metadata then text = metadata .. (text ~= "" and "\n" .. text or "") end
        end
        if heading then text = S.WithPartialNotice(text, context.untranslatedSuffix) end
        -- Talent UI may append both current and next-rank descriptions.
        if heading and context.category == "talent" and S.Integer(context.rank) then
            heading = heading .. (context.previewRank and " — ตัวอย่างแรงก์ " or " — แรงก์ ") .. context.rank
            if requirements then text = (text ~= "" and text .. "\n" or "") .. requirements.text end
        end
    end
    if not heading then hideFor(tooltip); return outcome end
    return show(tooltip, heading, text)
end
function S.OnTooltip(tooltip, data, requirements, talentComplete)
    S.stats.callbacks = S.stats.callbacks + 1
    local ok, outcome = pcall(display, tooltip, data, requirements, talentComplete)
    if ok then return outcome end
    S.stats.errors = S.stats.errors + 1
    frame:Hide()
    combatLayout = nil
    hideCombatTooltip()
    return "lua-error"
end

local combatActionEvents = {
    ACTIONBAR_PAGE_CHANGED = true, UPDATE_BONUS_ACTIONBAR = true, UPDATE_OVERRIDE_ACTIONBAR = true,
    UPDATE_VEHICLE_ACTIONBAR = true, UPDATE_POSSESS_BAR = true,
    UPDATE_SHAPESHIFT_FORM = true, UPDATE_SHAPESHIFT_FORMS = true,
    SPELLS_CHANGED = true, PLAYER_TARGET_CHANGED = true,
}
local combatPetEvents = { PET_BAR_UPDATE = true, PET_UI_UPDATE = true, UNIT_PET = true }

function S.RegisterCombatTooltips()
    if combatTooltip or (InCombatLockdown and InCombatLockdown()) then return end
    local tooltip = GameTooltip
    if not S.supported or not S.Public(tooltip, "table") or type(tooltip.HookScript) ~= "function" then return end
    local forbidden = S.Call(tooltip.IsForbidden, tooltip)
    if not S.Public(forbidden, "boolean") or forbidden then return end
    tooltip:HookScript("OnHide", hideCombatTooltip)
    tooltip:HookScript("OnTooltipCleared", hideCombatTooltip)
    tooltip:HookScript("OnShow", function(self)
        if not InCombatLockdown or not InCombatLockdown() then return end
        local forbidden = S.Call(self.IsForbidden, self)
        if not S.Public(forbidden, "boolean") or forbidden then hideCombatTooltip(); return end
        local info = S.Call(self.GetProcessingTooltipInfo, self)
        if S.Public(info, "table") and S.Public(info.tooltipData, "table") then
            S.OnTooltip(self, info.tooltipData)
        else
            hideCombatTooltip()
        end
    end)
    combatFrame:RegisterEvent("ADDON_RESTRICTION_STATE_CHANGED")
    combatFrame:RegisterEvent("PLAYER_REGEN_DISABLED")
    combatFrame:RegisterEvent("PLAYER_REGEN_ENABLED")
    combatFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
    combatFrame:RegisterEvent("GROUP_ROSTER_UPDATE")
    combatFrame:RegisterEvent("UNIT_ENTERED_VEHICLE")
    combatFrame:RegisterEvent("UNIT_EXITED_VEHICLE")
    combatFrame:RegisterEvent("PLAYER_GAINS_VEHICLE_DATA")
    combatFrame:RegisterEvent("PLAYER_LOSES_VEHICLE_DATA")
    combatFrame:RegisterEvent("UNIT_AURA")
    combatFrame:RegisterEvent("ACTIONBAR_SLOT_CHANGED")
    combatFrame:RegisterEvent("SPELL_FLYOUT_UPDATE")
    for event in pairs(combatActionEvents) do combatFrame:RegisterEvent(event) end
    for event in pairs(combatPetEvents) do combatFrame:RegisterEvent(event) end
    combatFrame:SetScript("OnEvent", function(_, event, detail)
        if event == "ACTIONBAR_SLOT_CHANGED" then
            if combatFlyout or (combatSlot and (not S.Integer(detail) or detail == combatSlot)) then hideCombatTooltip() end
        elseif event == "SPELL_FLYOUT_UPDATE" then
            if combatFlyout then hideCombatTooltip() end
        elseif combatActionEvents[event] then
            if combatSlot or combatFlyout or combatUnit == "pet" then hideCombatTooltip() end
        elseif combatPetEvents[event] then
            if combatUnit == "pet" and (event ~= "UNIT_PET" or not S.Public(detail, "string") or detail == "player") then
                hideCombatTooltip()
            end
        elseif event ~= "UNIT_AURA" then
            combatLayout = nil
            hideCombatTooltip()
        elseif combatUnit or combatSlot or combatFlyout then
            local unit = combatUnit or "player"
            if S.Public(detail, "string") and detail ~= unit and C_Secrets then
                local comparable = S.Call(C_Secrets.CanCompareUnitTokens, detail, unit)
                if S.Public(comparable, "boolean") and comparable then
                    local same = S.Call(UnitIsUnit, detail, unit)
                    if S.Public(same, "boolean") and not same then return end
                end
            end
            hideCombatTooltip()
        end
    end)
    combatTooltip = tooltip
end

local function tooltipInfo(tooltip)
    local info = S.Call(tooltip.GetProcessingTooltipInfo, tooltip)
    if not S.Public(info, "table") then info = S.Call(tooltip.GetPrimaryTooltipInfo, tooltip) end
    if S.Public(info, "table") and S.Public(info.tooltipData, "table") then return info end
end

local function showBasicPetTooltip(button)
    if not S.supported or not S.settings or not S.settings.enabled
        or (InCombatLockdown and InCombatLockdown()) then
        if ownerBasic == "pet" then frame:Hide() end
        return
    end
    local mode = S.Call(GetCVar, "UberTooltips")
    local keybinding = S.Call(KeybindFrames_InQuickKeybindMode)
    if not S.Public(mode, "string") or mode ~= "0"
        or not S.Public(keybinding, "boolean") or keybinding then
        if ownerBasic == "pet" then frame:Hide() end
        return
    end
    local tooltip = GameTooltip
    if not S.Public(tooltip, "table") then return end
    local shown = S.Call(tooltip.IsShown, tooltip)
    if not S.Public(shown, "boolean") or not shown then return end
    local record = S.BasicPetActionRecord(tooltip, button)
    if not record then hideFor(tooltip); return end
    local heading = record.translatedName
    if S.settings.englishNames then heading = heading .. " (" .. record.originalName .. ")" end
    show(tooltip, heading, "", "pet")
end

local function basicPetHover(button)
    if not pcall(showBasicPetTooltip, button) then
        S.stats.errors = S.stats.errors + 1
        frame:Hide()
    end
end

local basicPetHooks = setmetatable({}, { __mode = "k" })
function S.RegisterBasicPetTooltips()
    local bar = PetActionBar
    if not S.supported or (InCombatLockdown and InCombatLockdown())
        or not S.Public(bar, "table") or not S.Public(bar.actionButtons, "table") then return end
    for slot = 1, 10 do
        local button = bar.actionButtons[slot]
        if S.Public(button, "table") and type(button.HookScript) == "function" and not basicPetHooks[button] then
            button:HookScript("OnEnter", basicPetHover)
            basicPetHooks[button] = true
        end
    end
    if type(hooksecurefunc) == "function" and type(bar.UpdateCooldowns) == "function" and not basicPetHooks[bar] then
        hooksecurefunc(bar, "UpdateCooldowns", function()
            local tooltip = GameTooltip
            if S.Public(tooltip, "table") and not (InCombatLockdown and InCombatLockdown()) then
                local button = S.Call(tooltip.GetOwner, tooltip)
                if S.Public(button, "table") and basicPetHooks[button] then basicPetHover(button) end
            end
        end)
        basicPetHooks[bar] = true
    end
end

local function hideBasicFlyout()
    if ownerBasic == "flyout" then frame:Hide() end
end

local function showBasicFlyoutTooltip(button)
    if not S.supported or not S.settings or not S.settings.enabled
        or (InCombatLockdown and InCombatLockdown()) then hideBasicFlyout(); return end
    local mode = S.Call(GetCVar, "UberTooltips")
    local quick = S.Call(KeybindFrames_InQuickKeybindMode)
    local tooltip = GameTooltip
    if not S.Public(mode, "string") or mode ~= "0" or not S.Public(quick, "boolean") or quick
        or not S.Public(tooltip, "table") then hideBasicFlyout(); return end
    local shown = S.Call(tooltip.IsShown, tooltip)
    if not S.Public(shown, "boolean") or not shown then hideBasicFlyout(); return end
    local record = S.BasicFlyoutRecord(tooltip, button)
    if not record then hideBasicFlyout(); return end
    show(tooltip, translatedHeading(record), "", "flyout")
end

local function basicFlyoutHover(button)
    if not pcall(showBasicFlyoutTooltip, button) then
        S.stats.errors = S.stats.errors + 1
        hideBasicFlyout()
    end
end

function S.RegisterBasicFlyoutTooltips()
    local flyout = SpellFlyout
    if not S.supported or (InCombatLockdown and InCombatLockdown()) or not S.Public(flyout, "table") then return end
    if not flyoutHooks[flyout] and type(flyout.HookScript) == "function" then
        flyout:HookScript("OnShow", S.RegisterBasicFlyoutTooltips)
        flyout:HookScript("OnHide", function()
            hideBasicFlyout()
            if combatFlyout then hideCombatTooltip() end
        end)
        flyoutHooks[flyout] = true
    end
    local buttons = flyout.buttons
    if not S.Public(buttons, "table") or #buttons > 128 then return end
    for index = 1, #buttons do
        local button = buttons[index]
        if S.Public(button, "table") and type(button.HookScript) == "function" and not flyoutHooks[button] then
            button:HookScript("OnEnter", basicFlyoutHover)
            flyoutHooks[button] = true
        end
    end
end

local function retryShownTooltip(tooltip, getter, slot)
    if not S.settings or not S.settings.enabled or not S.supported
        or (InCombatLockdown and InCombatLockdown()) then return end
    if not S.Public(tooltip, "table") then return end
    local alreadyShown = rawequal(owner, tooltip) and frame:IsShown()
    local shown = S.Call(tooltip.IsShown, tooltip)
    if not S.Public(shown, "boolean") or not shown then return end
    local info = tooltipInfo(tooltip)
    if not info or not S.Public(info.getterName, "string") or info.getterName ~= getter then return end
    if slot then
        if not S.Public(info.getterArgs, "table") or not S.Integer(info.getterArgs[1])
            or info.getterArgs[1] ~= slot then return end
    end
    if alreadyShown and (getter ~= "GetTraitEntry" or not S.settings.descriptions) then
        repositionReader(tooltip)
        return
    end
    local requirements
    if getter == "GetTraitEntry" and S.settings.descriptions then
        requirements = S.Call(S.TalentRequirements, tooltip, info.tooltipData)
    end
    if alreadyShown then
        if not requirements then return end
        -- An ordered card still needs the full visible text if its suffix
        -- contains lines other than recognized prerequisites and separators.
        if not requirements.limit and not S.Call(S.Context, tooltip, info.tooltipData, nil, true) then return end
    end
    S.OnTooltip(tooltip, info.tooltipData, requirements, getter == "GetTraitEntry")
end

function S.ProbeTooltip()
    if InCombatLockdown and InCombatLockdown() then return end
    local tooltip = GameTooltip
    local shown = S.Public(tooltip, "table") and S.Call(tooltip.IsShown, tooltip)
    if not S.Public(shown, "boolean") or not shown then
        print("Alpha WoW probe: no shown GameTooltip")
        return
    end
    local info = tooltipInfo(tooltip)
    if not info or not S.Public(info.getterName, "string") then
        print("Alpha WoW probe: no public tooltip info")
        return
    end
    local getter = info.getterName
    if getter ~= "GetAction" and getter ~= "GetTraitEntry" and getter ~= "GetSpellBookItem"
        and getter ~= "GetSpellByID" and getter ~= "GetPetAction" and getter ~= "GetShapeshift" then
        print("Alpha WoW probe: point at a spell or talent")
        return
    end
    local data = info.tooltipData
    local requirements
    if getter == "GetTraitEntry" and S.settings and S.settings.descriptions then
        requirements = S.Call(S.TalentRequirements, tooltip, data)
    end
    local context = S.Call(S.Context, tooltip, data, requirements and requirements.limit, getter == "GetTraitEntry")
    local args = S.Public(info.getterArgs, "table") and info.getterArgs or {}
    local function number(value)
        return S.Public(value, "number") and tostring(value) or "?"
    end
    local outcome = S.OnTooltip(tooltip, data, requirements, getter == "GetTraitEntry")
    local visible = S.Call(frame.IsVisible, frame)
    print("Alpha WoW probe: " .. getter .. " args=" .. number(args[1]) .. "/" .. number(args[2])
        .. " type/id=" .. number(data.type) .. "/" .. number(data.id))
    print((context and context.key or "no-key") .. " " .. outcome
        .. " visible=" .. tostring(S.Public(visible, "boolean") and visible))
    if context and outcome == "text-mismatch" then
        print(context.name:sub(1, 100) .. " | " .. table.concat(context.lines, " | "):sub(1, 360))
    end
end

function S.RegisterTooltips()
    S.RegisterCombatTooltips()
    S.RegisterBasicPetTooltips()
    S.RegisterBasicFlyoutTooltips()
    if TooltipDataProcessor and type(TooltipDataProcessor.AddTooltipPostCall) == "function" then
        TooltipDataProcessor.AddTooltipPostCall(TooltipDataProcessor.AllTypes, function(tooltip, data)
            S.OnTooltip(tooltip, data)
        end)
    end
    if EventRegistry and type(EventRegistry.RegisterCallback) == "function" then
        EventRegistry:RegisterCallback("TalentDisplay.TooltipCreated", function(_, talent, tooltip)
            if not S.Public(talent, "table") or not S.Public(tooltip, "table") then return end
            local tooltipOwner = S.Call(tooltip.GetOwner, tooltip)
            if S.Public(tooltipOwner, "table") and rawequal(tooltipOwner, talent) then
                retryShownTooltip(tooltip, "GetTraitEntry")
            end
        end, S)
    end
    if type(hooksecurefunc) == "function" and GameTooltip and type(GameTooltip.SetAction) == "function" then
        hooksecurefunc(GameTooltip, "SetAction", function(tooltip, slot)
            if S.Integer(slot) then retryShownTooltip(tooltip, "GetAction", slot) end
        end)
    end
    if type(hooksecurefunc) == "function" and GameTooltip and type(GameTooltip.SetPetAction) == "function" then
        hooksecurefunc(GameTooltip, "SetPetAction", function(tooltip, slot)
            if S.Integer(slot) then retryShownTooltip(tooltip, "GetPetAction", slot) end
        end)
    end
    if type(hooksecurefunc) == "function" and GameTooltip and type(GameTooltip.SetShapeshift) == "function" then
        hooksecurefunc(GameTooltip, "SetShapeshift", function(tooltip, slot)
            if S.Integer(slot) then retryShownTooltip(tooltip, "GetShapeshift", slot) end
        end)
    end
end
