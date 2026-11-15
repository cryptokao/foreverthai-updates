local _, addon = ...
local S = addon.skills
local function ordinaryFalse(value)
    return S.Public(value,"nil") or (S.Public(value,"boolean") and value == false)
end
local function visible(frame)
    local value = S.Call(frame.IsVisible,frame)
    return S.Public(value,"boolean") and value
end

local function recipeHeading(row, name)
    if not row or row.reviewStatus ~= "VERIFIED" or not S.Public(name,"string") or name ~= row.originalName then return nil end
    local heading = row.translatedName
    if S.settings.englishNames then heading = heading .. " (" .. name .. ")" end
    return heading
end

function S.LookupRecipeName(id, name, description)
    if not S.supported or not S.settings or not S.settings.enabled or not S.Integer(id) then return nil end
    if not S.Public(description,"string") or description ~= "" then return nil end
    local heading = recipeHeading(S.recipeNames and S.recipeNames[id], name)
    if heading then return heading, "" end
end

function S.RecipeContext(form)
    if not S.Public(form,"table") or not visible(form) then return nil end
    if not C_Spell or not C_TradeSkillUI or not ProfessionsUtil then return nil end
    local changing = S.Call(C_TradeSkillUI.IsDataSourceChanging)
    local minimized = S.Call(ProfessionsUtil.IsCraftingMinimized)
    if not S.Public(changing,"boolean") or changing or not S.Public(minimized,"boolean") or minimized then return nil end
    if not ordinaryFalse(form.isInspection) or not ordinaryFalse(form.isRecraftOverride) or not ordinaryFalse(form.isRecraft) then return nil end
    local info = S.Call(form.GetRecipeInfo,form)
    local transaction = S.Call(form.GetTransaction,form)
    local schematic = form.recipeSchematic
    if not S.Public(info,"table") or not S.Public(transaction,"table") or not S.Public(schematic,"table") then return nil end
    local id = info.recipeID
    local transactionID = S.Call(transaction.GetRecipeID,transaction)
    if not S.Integer(id) or not S.Integer(transactionID) or not S.Integer(schematic.recipeID)
        or transactionID ~= id or schematic.recipeID ~= id then return nil end
    if not ordinaryFalse(info.isDummyRecipe) or not ordinaryFalse(info.isRecraft) then return nil end
    local recraft = S.Call(transaction.IsRecraft,transaction)
    if not S.Public(recraft,"boolean") or recraft then return nil end
    local name = S.Call(C_Spell.GetSpellName,id)
    if not S.Public(name,"string") or name == "" then return nil end
    local descriptionFrame = form.Description
    if not S.Public(descriptionFrame,"table") then return nil end
    local description = S.Call(descriptionFrame.GetText,descriptionFrame)
    if not S.Public(description,"string") or #description > 8192 then return nil end
    if description ~= "" and not visible(descriptionFrame) then return nil end
    -- Independently reread the current allocation's text. This rejects stale
    -- loader callbacks and an initially blank field while data is still loading.
    -- It never substitutes generic spell or output-item text for this panel.
    local reagents = S.Call(transaction.CreateCraftingReagentInfoTbl,transaction)
    if type(transaction.GetAllocationItemGUID) ~= "function" then return nil end
    local guid = S.Call(transaction.GetAllocationItemGUID,transaction)
    if not S.Public(reagents,"table") or not (S.Public(guid,"nil") or S.Public(guid,"string")) then return nil end
    local current = S.Call(C_TradeSkillUI.GetRecipeDescription,id,reagents,guid)
    if not S.Public(current,"string") or current ~= description then return nil end
    -- No deferred companion callbacks or body cache: every invocation samples
    -- the selected ID, transaction, allocation and visible text again.
    return {id=id,name=name,description=description}
end

local reader = CreateFrame("Frame","AlphaWoWRecipeReader",UIParent)
S.recipeReader = reader
reader:SetSize(330,80);reader:SetFrameStrata("DIALOG");reader:SetClampedToScreen(true)
reader:EnableMouse(false);reader:Hide()
local background = reader:CreateTexture(nil,"BACKGROUND")
background:SetAllPoints();background:SetColorTexture(0.035,0.045,0.065,0.97)
local title = S.CreateTextBlock(reader)
title:SetPoint("TOPLEFT",12,-10)
local body = S.CreateTextBlock(reader)
body:SetPoint("TOPLEFT",title,"BOTTOMLEFT",0,-8)
local hooked = setmetatable({},{__mode="k"})
local boundForm
local sourceClosed = false
local hover, hoverTitle, hoverOwner
local hoverRegistered

local function hideHover(button)
    if hoverOwner and (not button or rawequal(button, hoverOwner)) then
        hoverOwner = nil
        hover:Hide()
    end
end

local function showRecipeHover(button, payload)
    hideHover()
    if sourceClosed or not S.supported or not S.settings or not S.settings.enabled
        or (InCombatLockdown and InCombatLockdown()) or not C_TradeSkillUI or not C_Spell
        or not Professions or not ProfessionsUtil or not S.Public(ProfessionsFrame,"table")
        or not S.Public(button,"table") or not S.Public(payload,"table") then return end
    local page = ProfessionsFrame.CraftingPage
    local list = S.Public(page,"table") and page.RecipeList
    local box = S.Public(list,"table") and list.ScrollBox
    if not S.Public(box,"table") or not hooked[box] or not visible(list) or not visible(button) then return end
    local changing = S.Call(C_TradeSkillUI.IsDataSourceChanging)
    local minimized = S.Call(ProfessionsUtil.IsCraftingMinimized)
    local localMode = S.Call(Professions.InLocalCraftingMode)
    if not S.Public(changing,"boolean") or changing or not S.Public(minimized,"boolean") or minimized
        or not S.Public(localMode,"boolean") or not localMode then return end
    local node = S.Call(button.GetElementData,button)
    if not S.Public(node,"table") or not S.Public(node.data,"table") or not rawequal(node.data,payload) then return end
    local currentButton = S.Call(box.FindFrame,box,node)
    if not S.Public(currentButton,"table") or not rawequal(button,currentButton) then return end
    local base = payload.recipeInfo
    if not S.Public(base,"table") or type(Professions.GetHighestLearnedRecipe) ~= "function" then return end
    local ok, learned = pcall(Professions.GetHighestLearnedRecipe,base)
    if not ok or (not S.Public(learned,"nil") and not S.Public(learned,"table")) then return end
    local info = learned or base
    local id, label = info.recipeID, button.Label
    if not S.Integer(id) or not ordinaryFalse(info.isDummyRecipe) or not ordinaryFalse(info.isRecraft)
        or not S.Public(label,"table") or not S.Public(info.name,"string") then return end
    local current = S.Call(C_TradeSkillUI.GetRecipeInfo,id)
    local name = S.Call(C_Spell.GetSpellName,id)
    if not S.Public(current,"table") or not S.Integer(current.recipeID) or current.recipeID ~= id
        or not ordinaryFalse(current.isDummyRecipe) or not ordinaryFalse(current.isRecraft)
        or not S.Public(current.name,"string") or current.name ~= info.name
        or not S.Public(name,"string") or name ~= info.name then return end
    local visibleName = S.Call(label.GetText,label)
    if not S.Public(visibleName,"string") or visibleName ~= name then return end
    local record = S.recipeNames and S.recipeNames[id] or S.records["spell:" .. id]
    local heading = recipeHeading(record,name)
    if not heading or type(button.HookScript) ~= "function" then return end
    if not hooked[button] then
        button:HookScript("OnLeave",hideHover)
        button:HookScript("OnHide",hideHover)
        hooked[button] = true
    end
    local height = hoverTitle:Draw(heading,256,S.settings.fontSize+1,1,0.84,0.55)
    if not height or height > 120 then return end
    hover:SetHeight(height+20)
    hover:ClearAllPoints()
    hover:SetPoint("BOTTOMLEFT",button,"TOPLEFT",0,3)
    hoverOwner = button
    hover:Show()
end

local function registerRecipeHover(page)
    local list = page.RecipeList
    local box = S.Public(list,"table") and list.ScrollBox
    local events = S.Public(ScrollBoxListMixin,"table") and ScrollBoxListMixin.Event
    if not S.Public(box,"table") or type(box.RegisterCallback) ~= "function"
        or type(list.HookScript) ~= "function" or not S.Public(events,"table")
        or not EventRegistry or type(EventRegistry.RegisterCallback) ~= "function"
        or (InCombatLockdown and InCombatLockdown()) then return end
    if not hooked[box] then
        local invalidations = {"OnScroll","OnInitializedFrame","OnReleasedFrame","OnDataProviderReassigned"}
        for _,event in ipairs(invalidations) do
            if not S.Public(events[event],"string") then return end
        end
        for _,event in ipairs(invalidations) do
            box:RegisterCallback(events[event],function() hideHover() end,S)
        end
        list:HookScript("OnHide",function() hideHover() end)
        hooked[box] = true
    end
    if hoverRegistered then return end
    hover = CreateFrame("Frame","AlphaWoWRecipeHover",UIParent)
    hover:SetSize(280,40);hover:SetFrameStrata("TOOLTIP");hover:SetClampedToScreen(true)
    hover:EnableMouse(false);hover:Hide()
    local background = hover:CreateTexture(nil,"BACKGROUND")
    background:SetAllPoints();background:SetColorTexture(0.035,0.045,0.065,0.97)
    hoverTitle = S.CreateTextBlock(hover)
    hoverTitle:SetPoint("TOPLEFT",12,-10)
    EventRegistry:RegisterCallback("Professions.RecipeListOnEnter",function(_,button,payload)
        if not pcall(showRecipeHover,button,payload) then
            S.stats.errors = S.stats.errors+1
            hideHover()
        end
    end,S)
    hoverRegistered = true
end

local function refresh(form)
    hideHover()
    reader:Hide()
    if sourceClosed or form ~= boundForm or not S.supported or not S.settings or not S.settings.enabled then return end
    if InCombatLockdown and InCombatLockdown() then return end
    local context = S.RecipeContext(form)
    if not context then return end
    local heading,text
    if S.records["spell:" .. context.id] then
        heading,text = S.Lookup("spell:" .. context.id,context.name,{context.description})
    else heading,text = S.LookupRecipeName(context.id,context.name,context.description) end
    if not heading then return end
    heading = "สูตร: " .. heading
    local titleHeight = title:Draw(heading,306,S.settings.fontSize+1,1,0.84,0.55)
    local bodyHeight = body:Draw(text,306,S.settings.fontSize)
    if not titleHeight or not bodyHeight then return end
    local remembered = S.RememberLongText and S.RememberLongText(heading,text)
    local height = titleHeight + bodyHeight + 36
    if height > UIParent:GetHeight() - 40 then
        if not remembered then return end
        titleHeight=title:Draw("คำแปลสูตร",306,S.settings.fontSize+1,1,0.84,0.55)
        bodyHeight=body:Draw(S.longTextHint,306,S.settings.fontSize)
        if not titleHeight or not bodyHeight then return end
        height=titleHeight+bodyHeight+36
        if height > UIParent:GetHeight()-40 then return end
    end
    reader:SetHeight(height);reader:ClearAllPoints()
    reader:SetPoint("TOPLEFT",ProfessionsFrame,"TOPRIGHT",35,-30)
    reader:Show()
end
function S.RefreshRecipe(form)
    local ok = pcall(refresh,form or boundForm)
    if not ok then S.stats.errors = S.stats.errors + 1;reader:Hide() end
end
function S.RegisterRecipes()
    if not S.supported or not S.settings or type(hooksecurefunc) ~= "function" then return end
    if not S.Public(ProfessionsFrame,"table") then return end
    local page = ProfessionsFrame.CraftingPage
    if not S.Public(page,"table") then return end
    local form = page.SchematicForm
    if not S.Public(form,"table") or type(form.HookScript) ~= "function" then return end
    if type(page.HookScript) ~= "function" or type(ProfessionsFrame.HookScript) ~= "function" then return end
    local methods={"Init","UpdateRecipeDescription","UpdateOutputItem","ClearRecipeDescription","ClearTransaction"}
    for _,method in ipairs(methods) do if type(form[method]) ~= "function" then return end end
    if not hooked[form] then
        for _,method in ipairs(methods) do
            local clear = method == "ClearRecipeDescription" or method == "ClearTransaction"
            hooksecurefunc(form,method,function(self)
                if method == "Init" then
                    local changing = C_TradeSkillUI and S.Call(C_TradeSkillUI.IsDataSourceChanging)
                    if S.Public(changing,"boolean") and not changing then sourceClosed=false end
                end
                if clear then reader:Hide() else S.RefreshRecipe(self) end
            end)
        end
        form:HookScript("OnShow",function(self) S.RefreshRecipe(self) end)
        form:HookScript("OnHide",function() reader:Hide() end)
        page:HookScript("OnHide",function() reader:Hide() end)
        ProfessionsFrame:HookScript("OnHide",function() reader:Hide() end)
        hooked[form] = true
    end
    boundForm = form
    registerRecipeHover(page)
    S.RefreshRecipe(form)
end
local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("TRADE_SKILL_DATA_SOURCE_CHANGING")
events:RegisterEvent("TRADE_SKILL_DATA_SOURCE_CHANGED")
events:RegisterEvent("TRADE_SKILL_CLOSE")
events:RegisterEvent("PLAYER_REGEN_DISABLED")
events:SetScript("OnEvent",function(_,event,name)
    if event == "ADDON_LOADED" then
        if name == "Blizzard_Professions" then S.RegisterRecipes() end
    elseif event == "TRADE_SKILL_DATA_SOURCE_CHANGED" then
        hideHover()
        reader:Hide() -- Only a new Init can unlock a changed/closed source.
    elseif event == "PLAYER_REGEN_DISABLED" then hideHover();reader:Hide()
    else sourceClosed=true;hideHover();reader:Hide() end
end)
