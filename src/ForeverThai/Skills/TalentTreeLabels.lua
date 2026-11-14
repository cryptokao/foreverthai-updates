local _, addon = ...
local S = addon.skills
local labels = setmetatable({}, { __mode = "k" })
local registered

local controlNames = {
    DUAL_SPEC_PRIMARY = { "Primary", "ชุดหลัก" },
    DUAL_SPEC_SECONDARY = { "Secondary", "ชุดรอง" },
    UNSPENT_POINTS = { "Unspent Talents", "แต้มที่ยังไม่ได้ใช้" },
    TALENT_FRAME_APPLY_BUTTON_TEXT = { "Apply Changes", "ใช้การเปลี่ยนแปลง" },
}

local function hideLabels()
    for _, label in pairs(labels) do label:Hide() end
end

local function drawLabel(parent, anchor, point, relativePoint, x, y, width, size, text)
    local label = labels[anchor]
    if not label then
        label = CreateFrame("Frame", nil, parent)
        label:EnableMouse(false)
        label:SetSize(width, 27)
        label:SetPoint(point, anchor, relativePoint, x, y)
        label.text = S.CreateTextBlock(label)
        label.text:SetPoint("TOPLEFT", 0, 0)
        labels[anchor] = label
    end
    local height = label.text:Draw(text, width, size, 1, 0.84, 0.55)
    if height and height > 0 and height <= 27 then label:Show() end
end

local function isVisible(frame)
    local shown = S.Public(frame, "table") and S.Call(frame.IsVisible, frame)
    return S.Public(shown, "boolean") and shown
end

local function exactText(region, row, token)
    if not S.Public(region, "table") then return false end
    local english, global = S.Call(region.GetText, region), _G[token]
    return S.Public(english, "string") and english == row[1]
        and S.Public(global, "string") and global == row[1]
end

local function drawTab(tabs, id, token)
    if not S.Integer(id) then return end
    local tab = S.Call(tabs.GetTabButton, tabs, id)
    if not isVisible(tab) or not S.Public(tab.Text, "table") then return end
    local row, global = controlNames[token], _G[token]
    if not S.Public(global, "string") or global ~= row[1]
        or not S.Public(tab.tabText, "string") or tab.tabText ~= row[1] then return end
    local current = S.Call(tab.Text.GetText, tab.Text)
    local expected = S.Call(tab.GetTabText, tab)
    local disabled = S.Call(tab.IsForceDisabled, tab)
    if not S.Public(current, "string") or not S.Public(expected, "string")
        or (not S.Public(disabled, "boolean") and not S.Public(disabled, "nil")) then return end
    if disabled then
        if not S.Public(DISABLED_FONT_COLOR, "table") then return end
        expected = S.Call(DISABLED_FONT_COLOR.WrapTextInColorCode, DISABLED_FONT_COLOR, expected)
    end
    if S.Public(expected, "string") and current == expected then
        drawLabel(tab, tab, "TOPLEFT", "BOTTOMLEFT", 12, -1, 115, 12, row[2])
    end
end

local function drawControls(frame)
    local inspecting = S.Call(frame.IsInspecting, frame)
    if not S.Public(inspecting, "boolean") or inspecting then return end
    local tabs = frame.TabSystem
    if isVisible(tabs) then
        drawTab(tabs, frame.primarySpecTabID, "DUAL_SPEC_PRIMARY")
        drawTab(tabs, frame.secondarySpecTabID, "DUAL_SPEC_SECONDARY")
    end
    local points = frame.ClassCurrencyDisplay
    local unspent = controlNames.UNSPENT_POINTS
    if isVisible(points) and isVisible(points.CurrentAmountContainer)
        and exactText(points.UnspentLabel, unspent, "UNSPENT_POINTS") then
        drawLabel(points.CurrentAmountContainer, points.UnspentLabel, "TOPLEFT", "BOTTOMLEFT", 0, 1, 125, 12, unspent[2])
    end
    local apply = frame.ApplyButton
    local applyChanges = controlNames.TALENT_FRAME_APPLY_BUTTON_TEXT
    if isVisible(apply) and exactText(apply, applyChanges, "TALENT_FRAME_APPLY_BUTTON_TEXT") then
        drawLabel(apply, apply, "RIGHT", "LEFT", -8, 0, 115, 12, applyChanges[2])
    end
end

local function drawLabels(frame)
    if not S.settings or not S.settings.enabled or (InCombatLockdown and InCombatLockdown()) then return end
    if not isVisible(frame) then return end
    local treeID = S.Call(frame.GetTalentTreeID, frame)
    if not S.Integer(treeID) then return end
    local tree = S.talentTreeNames[treeID]
    if not tree then return end
    drawControls(frame)
    local headers = frame.treeHeaders
    if not S.Public(headers, "table") or #headers > 3 then return end

    for index = 1, #headers do
        local header = headers[index]
        local shown = S.Public(header, "table") and S.Call(header.IsShown, header)
        if S.Public(shown, "boolean") and shown then
            local info, name = header.displayInfo, header.Name
            if S.Public(info, "table") and S.Public(name, "table")
                and S.Integer(info.treeID) and info.treeID == treeID and S.Integer(info.groupID) then
                local row = tree[info.groupID]
                local english = S.Call(name.GetText, name)
                if row and S.Integer(info.skillLineID) and info.skillLineID == row[1]
                    and S.Public(info.displayName, "string") and info.displayName == row[2]
                    and S.Public(english, "string") and english == row[2] then
                    drawLabel(header, name, "TOPLEFT", "BOTTOMLEFT", 0, 1, 190, 14, row[3])
                end
            end
        end
    end
end

function S.RefreshTalentTreeNames()
    hideLabels()
    if not registered or not S.supported then return end
    if not pcall(drawLabels, registered) then
        hideLabels()
        S.stats.errors = S.stats.errors + 1
    end
end

function S.RegisterTalentTreeNames()
    if registered then S.RefreshTalentTreeNames(); return end
    if not S.supported or type(hooksecurefunc) ~= "function"
        or (InCombatLockdown and InCombatLockdown()) then return end
    local spells = PlayerSpellsFrame
    local frame = S.Public(spells, "table") and spells.TalentsFrame
    if not S.Public(frame, "table") or type(frame.RefreshTreeHeaders) ~= "function"
        or type(frame.HookScript) ~= "function" then return end
    hooksecurefunc(frame, "RefreshTreeHeaders", S.RefreshTalentTreeNames)
    for _, method in ipairs({ "UpdateTabs", "UpdateConfigButtonsState", "UpdateInspecting" }) do
        if type(frame[method]) == "function" then hooksecurefunc(frame, method, S.RefreshTalentTreeNames) end
    end
    frame:HookScript("OnShow", S.RefreshTalentTreeNames)
    registered = frame
    S.RefreshTalentTreeNames()
end
