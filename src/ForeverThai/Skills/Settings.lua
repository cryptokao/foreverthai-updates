local directory, addon = ...
local S = addon.skills
local panel = CreateFrame("Frame", "AlphaWoWSkillsSettings", UIParent)
panel:SetSize(470, 330)
panel:SetPoint("CENTER")
panel:SetFrameStrata("DIALOG")
panel:SetClampedToScreen(true)
panel:Hide()
local bg = panel:CreateTexture(nil, "BACKGROUND")
bg:SetAllPoints(); bg:SetColorTexture(0.04, 0.05, 0.075, 0.98)
local function label(text, x, y, size)
    local block = S.CreateTextBlock(panel)
    block:SetPoint("TOPLEFT", x, y)
    local function set(value) block:Draw(value, 444 - x, size or 16) end
    set(text)
    return set
end
label("Alpha WoW Thai Localization", 20, -18, 20)
label("Skills & Talents " .. S.version .. " / " .. S.datasetVersion, 20, -48, 13)
local close = CreateFrame("Button", nil, panel, "UIPanelCloseButton")
close:SetPoint("TOPRIGHT", -3, -3); close:SetScript("OnClick", function() panel:Hide() end)
local checks = {}
for i, option in ipairs({
    { "enabled", "เปิดคำแปลภาษาไทย" }, { "englishNames", "แสดงชื่อภาษาอังกฤษคู่กับชื่อไทย" },
    { "descriptions", "แสดงคำอธิบายภาษาไทย" }, { "original", "แสดงต้นฉบับในหน้าต่างคำแปล" },
}) do
    local key = option[1]
    local button = CreateFrame("CheckButton", nil, panel, "UICheckButtonTemplate")
    button:SetPoint("TOPLEFT", 18, -70 - i * 33)
    label(option[2], 56, -76 - i * 33)
    button:SetScript("OnClick", function(self)
        if InCombatLockdown and InCombatLockdown() then self:SetChecked(S.settings[key]); return end
        S.settings[key] = self:GetChecked() and true or false
        S.reader:Hide()
        if S.ClearLongText then S.ClearLongText() end
        if S.RefreshRecipe then S.RefreshRecipe() end
        if key == "enabled" and S.RefreshTalentTreeNames then S.RefreshTalentTreeNames() end
    end)
    checks[key] = button
end
local sizeLabel = label("", 56, -255)
for i, delta in ipairs({ -1, 1 }) do
    local b = CreateFrame("Button", nil, panel, "UIPanelButtonTemplate")
    b:SetSize(32, 24); b:SetPoint("TOPLEFT", 280 + i * 38, -250)
    b:SetText(delta < 0 and "-" or "+")
    b:SetScript("OnClick", function()
        if InCombatLockdown and InCombatLockdown() then return end
        S.settings.fontSize = math.max(12, math.min(24, S.settings.fontSize + delta))
        sizeLabel("ขนาดตัวอักษร: " .. S.settings.fontSize)
        S.reader:Hide()
        if S.ClearLongText then S.ClearLongText() end
        if S.RefreshRecipe then S.RefreshRecipe() end
    end)
end
local status = label("", 20, -300, 12)
panel:SetScript("OnShow", function()
    for key, button in pairs(checks) do button:SetChecked(S.settings[key]) end
    sizeLabel("ขนาดตัวอักษร: " .. S.settings.fontSize)
    local _, build = GetBuildInfo()
    status(S.supported and "Build " .. build .. " / ใช้เฉพาะคำแปลที่ผ่านการตรวจทาน" or "ไม่รองรับ build หรือภาษานี้ — แสดงต้นฉบับ")
end)
local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("PLAYER_REGEN_DISABLED")
events:RegisterEvent("PLAYER_REGEN_ENABLED")
events:SetScript("OnEvent", function(_, event, name)
    if event == "PLAYER_REGEN_DISABLED" then
        panel:Hide()
        S.reader:Hide()
        if S.RefreshTalentTreeNames then S.RefreshTalentTreeNames() end
        return
    end
    if event == "PLAYER_LOGIN" or event == "PLAYER_REGEN_ENABLED" or name == "Blizzard_PlayerSpells" then
        if S.RegisterTalentTreeNames then S.RegisterTalentTreeNames() end
    end
    if event == "PLAYER_LOGIN" or event == "PLAYER_REGEN_ENABLED" or name == "Blizzard_ActionBar" then
        if S.RegisterCombatTooltips then S.RegisterCombatTooltips() end
        S.RegisterBasicPetTooltips()
        if S.RegisterBasicFlyoutTooltips then S.RegisterBasicFlyoutTooltips() end
        return
    end
    if name == directory then
        S.Initialize()
        S.RegisterTooltips()
        if S.RegisterRecipes then S.RegisterRecipes() end
        if S.RegisterTalentTreeNames then S.RegisterTalentTreeNames() end
    end
end)
SLASH_ALPHAWOWSKILLS1 = "/alphathai"
SlashCmdList.ALPHAWOWSKILLS = function(command)
    if not S.settings then return end
    if InCombatLockdown and InCombatLockdown() then return end
    if command == "read" then
        if not S.OpenLongText or not S.OpenLongText() then print("Alpha WoW: No translation ready to read.") end
    elseif command == "scan" then
        print(S.Scan and S.Scan() and "Alpha WoW: collecting available spellbook and talent tooltips. /reload to save." or "Alpha WoW: scan unavailable or already running.")
    elseif command == "capture" then
        if S.Capture then
            S.captureEnabled = not S.captureEnabled
            print("Alpha WoW: tooltip capture " .. (S.captureEnabled and "ON" or "OFF") .. ". /reload to save.")
        else
            print("Alpha WoW: tooltip capture unavailable in this package.")
        end
    elseif command == "probe" then
        print("Alpha WoW: Hover over a spell or talent for 3 seconds.")
        C_Timer.After(3, S.ProbeTooltip)
    elseif command == "status" then
        local _, build, _, interface = GetBuildInfo()
        print("Alpha WoW " .. S.version .. " / " .. tostring(build) .. "/" .. tostring(interface)
            .. " " .. GetLocale() .. " supported=" .. tostring(S.supported) .. " enabled=" .. tostring(S.settings.enabled))
        print("callbacks=" .. S.stats.callbacks .. " noContext=" .. S.stats.noContext .. " lookups=" .. S.stats.lookups
            .. " matched=" .. S.stats.matched .. " missing=" .. S.stats.missing .. " outdated=" .. S.stats.outdated
            .. " errors=" .. S.stats.errors)
    else panel:SetShown(not panel:IsShown()) end
end
