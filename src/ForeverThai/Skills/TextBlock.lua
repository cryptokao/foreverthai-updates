local directory, addon = ...
local S = addon.skills
local font = "Interface\\AddOns\\" .. directory .. "\\Fonts\\Sarabun-Regular.ttf"

function S.CreateTextBlock(parent)
    local block = CreateFrame("Frame", nil, parent)
    local label = parent:CreateFontString(nil, "OVERLAY")
    label:SetPoint("TOPLEFT", block, "TOPLEFT")
    label:SetJustifyH("LEFT")
    label:SetWordWrap(true)
    label:SetNonSpaceWrap(true)
    label:SetSpacing(3)
    local bitmap, paint
    function block:Draw(text, width, size, red, green, blue)
        red, green, blue = red or 0.96, green or 0.95, blue or 0.91
        self:SetWidth(width)
        if text == "" then
            label:Hide()
            if bitmap then bitmap:Hide() end
            self:SetHeight(1)
            return 0
        end
        local height
        -- The client can accept SetFont while still drawing Thai as missing glyphs.
        local hasThai = text:find("\224[\184\185][\128-\191]") ~= nil
        local useFont = ForeverThaiDisplayMode == "font" or not hasThai
        if useFont and addon.fontOK ~= false and S.Call(label.SetFont, label, font, size, "") == true then
            if bitmap then bitmap:Hide() end
            label:SetWidth(width)
            label:SetTextColor(red, green, blue)
            label:SetText(text)
            label:Show()
            height = label:GetStringHeight()
        elseif addon.BitmapLayer and S.bitmapAtlas then
            label:Hide()
            if not bitmap then
                bitmap, paint = addon.BitmapLayer(self, "TOPLEFT", 0, 0, width, size, S.bitmapAtlas)
            end
            height = paint(text, red, green, blue, width, size)
        end
        if not S.Public(height, "number") or height ~= height or height < 0 or height > 100000 then
            label:Hide()
            if bitmap then bitmap:Hide() end
            self:Hide()
            return nil
        end
        self:SetHeight(math.max(1, height))
        self:Show()
        return height
    end
    return block
end
