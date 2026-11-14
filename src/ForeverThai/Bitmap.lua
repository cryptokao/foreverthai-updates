local directory, addon = ...
local base = "Interface\\AddOns\\" .. directory .. "\\Fonts\\Thai"
local function thaiAt(s, i)
    local a, b, c = s:byte(i, i + 2)
    return a == 224 and (b == 184 or b == 185) and c and c >= 128 and c <= 191
end

-- Shape Thai offline so tone marks do not depend on the client's text engine.
-- Build the page from reusable word textures; player names remain live text.
function addon.BitmapLayer(parent, point, left, top, width, fontSize, atlas)
    local layer = CreateFrame("Frame", nil, parent)
    layer:SetPoint(point, parent, point, left, top)
    layer:SetSize(width, 1)
    local textures, labels = {}, {}

    local function draw(text, red, green, blue, newWidth, newSize)
        width, fontSize = newWidth or width, newSize or fontSize
        local scale = fontSize / 34
        local lineHeight = (atlas and atlas.lineHeight or 56) * scale
        local x, y, pendingSpace = 0, 0, 0
        local nrTextures, nrLabels = 0, 0
        local defaultR, defaultG, defaultB = red, green, blue
        local function newline()
            x, y, pendingSpace = 0, y + lineHeight, 0
        end
        local function place(advance)
            if x > 0 and x + pendingSpace + advance > width then newline() end
            x = x + pendingSpace
            pendingSpace = 0
            local start = x
            x = x + advance
            return start
        end
        local function word(g, textureBase)
            local glyphHeight = g[7] or 56
            local start = place(g[6] * scale)
            nrTextures = nrTextures + 1
            local tx = textures[nrTextures] or layer:CreateTexture(nil, "ARTWORK")
            textures[nrTextures] = tx
            tx:SetTexture(textureBase .. g[1] .. ".tga")
            tx:SetTexCoord(g[2]/1024, (g[2]+g[4])/1024, g[3]/1024, (g[3]+glyphHeight)/1024)
            tx:SetSize(g[4] * scale, glyphHeight * scale)
            tx:ClearAllPoints()
            tx:SetPoint("TOPLEFT", layer, "TOPLEFT", start + g[5]*scale, -y - (g[8] or 0)*scale)
            tx:SetVertexColor(red, green, blue)
            tx:Show()
        end
        local function plain(token)
            nrLabels = nrLabels + 1
            local fs = labels[nrLabels] or layer:CreateFontString(nil, "OVERLAY", "GameFontNormal")
            labels[nrLabels] = fs
            if STANDARD_TEXT_FONT then fs:SetFont(STANDARD_TEXT_FONT, fontSize, "") end
            fs:SetTextColor(red, green, blue)
            fs:SetText(token)
            local start = place(fs:GetStringWidth())
            fs:ClearAllPoints()
            fs:SetPoint("LEFT", layer, "TOPLEFT", start, -y - lineHeight/2)
            fs:Show()
        end
        local i = 1
        while i <= #text do
            local ch = text:sub(i, i)
            local color = ch == "|" and text:sub(i, i + 9):match("^|cff(%x%x%x%x%x%x)$")
            if color then
                red = tonumber(color:sub(1,2),16)/255
                green = tonumber(color:sub(3,4),16)/255
                blue = tonumber(color:sub(5,6),16)/255
                i = i + 10
            elseif text:sub(i, i+1) == "|r" then
                red, green, blue = defaultR, defaultG, defaultB
                i = i + 2
            elseif ch == "\n" then
                newline()
                i = i + 1
            elseif ch == " " then
                if x > 0 then pendingSpace = fontSize * 0.28 end
                i = i + 1
            elseif thaiAt(text, i) then
                local start = i
                repeat i = i + 3 until not thaiAt(text, i)
                local token = text:sub(start,i - 1)
                local pieces = atlas and atlas.runs[token] or addon.runs and addon.runs[token]
                local own = atlas and atlas.runs[token] ~= nil
                if pieces then
                    local glyphs, textureBase = addon.glyphs, base
                    if own then glyphs, textureBase = atlas.glyphs, atlas.base end
                    for _, id in ipairs(pieces) do word(glyphs[id], textureBase) end
                elseif atlas then
                    layer:Hide()
                    return nil
                else
                    plain(token)
                end
            else
                local start = i
                repeat i = i + 1 until i > #text or text:sub(i,i):find("[ |\n]") or thaiAt(text,i)
                plain(text:sub(start, i - 1))
            end
        end
        for n = nrTextures + 1, #textures do textures[n]:Hide() end
        for n = nrLabels + 1, #labels do labels[n]:Hide() end
        if newWidth then layer:SetWidth(width) end
        layer:SetHeight(y + lineHeight)
        layer:Show()
        return y + lineHeight
    end
    return layer, draw
end
