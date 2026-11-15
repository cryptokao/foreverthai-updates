local directory, addon = ...
local font = "Interface\\AddOns\\" .. directory .. "\\Fonts\\Sarabun-Regular.ttf"
local panel = CreateFrame("Frame", "ForeverThaiReader", UIParent)
panel:SetSize(396, 350)
panel:SetFrameStrata("DIALOG")
panel:SetClampedToScreen(true)
panel:SetMovable(true)
panel:Hide()
addon.panel = panel

local function reset()
    panel:ClearAllPoints()
    panel:SetPoint("CENTER", UIParent, "CENTER", UIParent:GetWidth() * 0.19, 0)
end
addon.ResetPosition = reset
reset()

local background = panel:CreateTexture(nil, "BACKGROUND")
background:SetAllPoints()
background:SetColorTexture(0.055, 0.063, 0.079, 0.97)
local strip = panel:CreateTexture(nil, "ARTWORK")
strip:SetPoint("TOPLEFT", 0, 0)
strip:SetPoint("TOPRIGHT", 0, 0)
strip:SetHeight(2)
strip:SetColorTexture(0.85, 0.65, 0.32, 1)

local handle = CreateFrame("Frame", nil, panel)
handle:SetPoint("TOPLEFT")
handle:SetPoint("TOPRIGHT", -34, 0)
handle:SetHeight(44)
handle:EnableMouse(true)
handle:RegisterForDrag("LeftButton")
handle:SetScript("OnDragStart", function() panel:StartMoving() end)
handle:SetScript("OnDragStop", function() panel:StopMovingOrSizing() end)
local close = CreateFrame("Button", nil, panel, "UIPanelCloseButton")
close:SetPoint("TOPRIGHT", -3, -4)
close:SetScript("OnClick", function() panel:Hide() end)

local heading = handle:CreateFontString(nil, "OVERLAY")
heading:SetPoint("LEFT", 16, 0)
heading:SetJustifyH("LEFT")
heading:SetTextColor(1, 0.84, 0.55)
local scroll = CreateFrame("ScrollFrame", nil, panel, "UIPanelScrollFrameTemplate")
scroll:SetPoint("TOPLEFT", 16, -46)
scroll:SetPoint("BOTTOMRIGHT", -32, 14)
local content = CreateFrame("Frame", nil, scroll)
content:SetSize(346, 1)
scroll:SetScrollChild(content)
local body = content:CreateFontString(nil, "OVERLAY")
body:SetPoint("TOPLEFT")
body:SetWidth(346)
body:SetJustifyH("LEFT")
body:SetJustifyV("TOP")
body:SetWordWrap(true)
body:SetNonSpaceWrap(true)
body:SetSpacing(4)
body:SetTextColor(0.96, 0.95, 0.91)
local headingOK = heading:SetFont(font, 20, "")
local bodyOK = body:SetFont(font, 17, "")
addon.fontOK = headingOK and bodyOK

local banner, paintBanner = addon.BitmapLayer(handle, "TOPLEFT", 16, -7, 330, 20)
local page, paintPage = addon.BitmapLayer(content, "TOPLEFT", 0, 0, 346, 17)
local lastTitle, lastText
function addon.ShowPage(title, text)
    lastTitle, lastText = title, text
    if ForeverThaiDisplayMode == "font" and addon.fontOK then
        banner:Hide()
        page:Hide()
        heading:SetText(title)
        heading:Show()
        body:SetText(text)
        body:Show()
        content:SetHeight(math.max(1, body:GetStringHeight() + 10))
    else
        heading:Hide()
        body:Hide()
        paintBanner(title, 1, 0.84, 0.55)
        content:SetHeight(paintPage(text, 0.96, 0.95, 0.91) + 10)
    end
    panel:Show()
    scroll:SetVerticalScroll(0)
end

function addon.SetMode(value)
    ForeverThaiDisplayMode = value
    if panel:IsShown() then addon.ShowPage(lastTitle, lastText) end
    print("ForeverThai display: " .. (value == "font" and addon.fontOK and "font" or "image"))
end
