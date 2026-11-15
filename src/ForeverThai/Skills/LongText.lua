local _, addon = ...
local S = addon.skills
local snapshot, window, scroll, content, body, caption
local offset, maximum = 0, 0
S.longTextHint = "ข้อความยาว — พิมพ์ /alphathai read เพื่ออ่านทั้งหมด"
local function allowed()
    return S.supported and S.settings and S.settings.enabled
        and not (InCombatLockdown and InCombatLockdown())
end
function S.ClearLongText()
    snapshot = nil
    if window then window:Hide() end
end
function S.RememberLongText(heading, text)
    if not allowed() or not S.Public(heading,"string") or not S.Public(text,"string")
        or #heading > 4096 or #text > 32768 then S.ClearLongText();return false end
    -- One immutable displayed-text snapshot, never a second localization database.
    -- An already open reader retains its explicitly labelled snapshot until reopened.
    snapshot = {heading=heading,text=text}
    return true
end
local function move(amount)
    if not allowed() then S.ClearLongText(); return end
    if not S.Public(amount,"number") or amount ~= amount then return end
    offset = math.max(0,math.min(maximum,offset+amount))
    scroll:SetVerticalScroll(offset)
end
local function create()
    window = CreateFrame("Frame","AlphaWoWLongTextReader",UIParent)
    S.longTextReader = window
    window:SetPoint("CENTER");window:SetFrameStrata("DIALOG")
    window:SetClampedToScreen(true);window:EnableMouse(true);window:Hide()
    local bg = window:CreateTexture(nil,"BACKGROUND")
    bg:SetAllPoints();bg:SetColorTexture(0.035,0.045,0.065,0.98)
    caption = S.CreateTextBlock(window)
    caption:SetPoint("TOPLEFT",12,-12)
    scroll = CreateFrame("ScrollFrame",nil,window)
    scroll:SetPoint("TOPLEFT",12,-66);scroll:EnableMouseWheel(true)
    content = CreateFrame("Frame",nil,scroll)
    body = S.CreateTextBlock(content)
    body:SetPoint("TOPLEFT")
    scroll:SetScrollChild(content)
    scroll:SetScript("OnMouseWheel",function(_,delta)
        if S.Public(delta,"number") then move(-delta*40) end
    end)
    for i, spec in ipairs({{"ขึ้น",-180},{"ลง",180},{"ปิด",0}}) do
        local button = CreateFrame("Button",nil,window)
        button:SetSize(78,28);button:SetPoint("BOTTOMLEFT",12+(i-1)*88,10)
        local label = S.CreateTextBlock(button)
        label:SetPoint("TOPLEFT",10,-1);label:Draw(spec[1],68,16)
        local delta = spec[2]
        button:SetScript("OnClick",function() if delta==0 then window:Hide() else move(delta) end end)
    end
end
local function open()
    if window then window:Hide() end
    if not allowed() or not snapshot then return false end
    local screenHeight,screenWidth = UIParent:GetHeight(),UIParent:GetWidth()
    if not S.Public(screenHeight,"number") or not S.Public(screenWidth,"number")
        or screenHeight ~= screenHeight or screenWidth ~= screenWidth
        or screenHeight < 300 or screenWidth < 300 or screenHeight > 100000 or screenWidth > 100000 then return false end
    if not window then create() end
    window:Hide()
    local width,height = math.min(560,screenWidth-40),math.min(600,screenHeight-40)
    local innerWidth,viewHeight = width-24,height-112
    window:SetSize(width,height)
    scroll:SetSize(innerWidth,viewHeight);content:SetWidth(innerWidth)
    if not caption:Draw("ข้อความที่เปิดล่าสุด — ค่าต่าง ๆ ณ เวลาที่เปิดคำแปล",innerWidth,14) then return false end
    local textHeight = body:Draw(snapshot.heading .. "\n\n" .. snapshot.text,innerWidth,S.settings.fontSize)
    if not S.Public(textHeight,"number") or textHeight ~= textHeight or textHeight < 0 or textHeight > 100000 then return false end
    content:SetHeight(math.max(viewHeight,textHeight+8))
    maximum=math.max(0,textHeight+8-viewHeight);offset=0
    scroll:SetVerticalScroll(0);window:Show()
    return true
end
function S.OpenLongText()
    local ok,result=pcall(open)
    if not ok then S.stats.errors=S.stats.errors+1;if window then window:Hide() end end
    return ok and result or false
end
local events=CreateFrame("Frame")
events:RegisterEvent("PLAYER_REGEN_DISABLED")
events:RegisterEvent("PLAYER_LEAVING_WORLD")
events:RegisterEvent("DISPLAY_SIZE_CHANGED")
events:RegisterEvent("UI_SCALE_CHANGED")
events:SetScript("OnEvent",S.ClearLongText)
