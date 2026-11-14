"""Independent Lua mocks of recipe companion; never operate real game/UI."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


class RecipePanelTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
            addon={}; frames={}; hookCalls={}; secret={}; inaccessible={}; mutations=0
            changing=false; minimized=false; combat=false; fontOK=true
            function issecretvalue(v) return secret[v]==true end
            function issecrettable(v) return secret[v]==true end
            function canaccesstable(v) return not inaccessible[v] end
            function GetBuildInfo() return "1.60.1","70862","",16001 end
            function GetLocale() return "enUS" end
            function InCombatLockdown() return combat end
            function forbidden() error("unexpected mutation or loader API") end
            function trap()
                return setmetatable({}, {__index=forbidden,__lt=forbidden,__le=forbidden,__tostring=forbidden})
            end
            function frame(parent)
                local f={parent=parent,shown=true,scripts={},hooks={},events={},fontstrings={},text="",height=12}
                function f:IsVisible() return self.shown and (not self.parent or self.parent:IsVisible()) end
                function f:IsShown() return self.shown end
                function f:SetShown(value) if value then self:Show() else self:Hide() end end
                function f:SetChecked(value) self.checked=value end
                function f:GetChecked() return self.checked end
                function f:Show() self.shown=true; self:Fire("OnShow") end
                function f:Hide() self.shown=false; self:Fire("OnHide") end
                function f:Fire(event,...)
                    if self.scripts[event] then self.scripts[event](self,...) end
                    for _,fn in ipairs(self.hooks[event] or {}) do fn(self,...) end
                end
                function f:HookScript(event,fn)
                    self.hooks[event]=self.hooks[event] or {}; table.insert(self.hooks[event],fn)
                end
                function f:SetScript(event,fn) self.scripts[event]=fn end
                function f:RegisterEvent(event) self.events[event]=true end
                function f:CreateTexture()
                    local t=frame(self); self.textures=self.textures or {}; table.insert(self.textures,t); return t
                end
                function f:CreateFontString() local c=frame(self);table.insert(self.fontstrings,c);return c end
                function f:SetFont(...) self.font={...};return fontOK end
                function f:SetText(t) self.text=t end
                function f:GetText() return self.text end
                function f:GetStringWidth() return #self.text * 8 end
                function f:GetStringHeight() return self.text=="" and 0 or 12 end
                function f:GetHeight() return self.height end
                function f:SetHeight(h) self.height=h end
                function f:SetSize(w,h) self.width=w;self.height=h end
                function f:SetWidth(w) self.width=w end
                function f:SetPoint(...) self.point={...} end
                function f:ClearAllPoints() self.point=nil end
                for _,method in ipairs({"SetFrameStrata","SetClampedToScreen","EnableMouse","SetAllPoints",
                    "SetColorTexture","SetJustifyH","SetWordWrap","SetNonSpaceWrap","SetSpacing","SetTextColor",
                    "SetTexCoord","SetVertexColor"}) do
                    f[method]=function() end
                end
                function f:SetTexture(path) self.texture=path; return true end
                return f
            end
            UIParent=frame();UIParent.height=1080
            function CreateFrame(kind,name,parent)
                local f=frame(parent);f.name=name;f.kind=kind;table.insert(frames,f);return f
            end
            function hooksecurefunc(object,method,fn)
                hookCalls[method]=(hookCalls[method] or 0)+1
                local original=object[method]
                object[method]=function(self,...) local value=original(self,...);fn(self,...);return value end
            end
            function event(name,...)
                for _,f in ipairs(frames) do if f.events[name] then f:Fire("OnEvent",name,...) end end
            end
            names={[101]="Recipe A",[202]="Recipe B",[301]="Empty Recipe"}
            descriptions={[101]="Heals 10 health.",[202]="Heals 20 health.",[301]=""}
            C_Spell={GetSpellName=function(id) return names[id] end}
            C_TradeSkillUI={IsDataSourceChanging=function() return changing end,
                GetRecipeDescription=function(id,reagents,guid)
                    lastQuery={id=id,reagents=reagents,guid=guid};return descriptions[id]
                end,CraftRecipe=forbidden,GetRecipeOutputItemData=forbidden}
            ProfessionsUtil={IsCraftingMinimized=function() return minimized end}
            Spell={CreateFromSpellID=forbidden};C_Timer={After=forbidden}
            function newForm()
                local root=frame(UIParent);local page=frame(root);local f=frame(page)
                root.CraftingPage=page;page.SchematicForm=f
                f.Description=frame(f);f.OutputText=frame(f);f.OutputText.text="Unrelated output item"
                function f:GetRecipeInfo() return self.currentRecipeInfo end
                function f:GetTransaction() return self.transaction end
                function f:Init(info) self.currentRecipeInfo=info end
                function f:UpdateRecipeDescription() end
                function f:UpdateOutputItem() end
                function f:ClearRecipeDescription() self.Description.text="" end
                function f:ClearTransaction() self.transaction=nil end
                return root,page,f
            end
            function selectRecipe(f,id)
                f.currentRecipeInfo={recipeID=id,skillLineAbilityID=9001,recipeLevel=7}
                f.recipeSchematic={recipeID=id,outputItemID=7777,name="Wrong schematic caption"}
                f.transaction={id=id,reagents={{itemID=88,quantity=2}},guid="allocation-A"}
                function f.transaction:GetRecipeID() return self.id end
                function f.transaction:IsRecraft() return false end
                function f.transaction:CreateCraftingReagentInfoTbl() return self.reagents end
                function f.transaction:GetAllocationItemGUID() return self.guid end
                f.Description.text=descriptions[id]
            end
            ProfessionsFrame,page,form=newForm();selectRecipe(form,101)
        ''')
        for name in ('Core', 'RawText', 'TextBlock'):
            self.lua.execute((ROOT / 'addon/ForeverThai/Skills' / (name + '.lua')).read_text(encoding='utf-8'),
                             'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            S=addon.skills;S.Initialize()
            S.records["spell:101"]={originalName="Recipe A",translatedName="สูตรเอ",reviewStatus="VERIFIED",
                lines={{source="Heals {1} health.",target="ฟื้นฟูพลังชีวิต {1}",format="db2",
                        slots={{token="$s1",kind="number-range"}}}}}
            S.records["spell:202"]={originalName="Recipe B",translatedName="สูตรบี",reviewStatus="VERIFIED",
                lines=S.records["spell:101"].lines}
            S.recipeNames={[301]={originalName="Empty Recipe",translatedName="สูตรชื่อเท่านั้น",reviewStatus="VERIFIED"}}
        ''')
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/Recipes.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.lua.execute('reader=S.recipeReader')

    def run_lua(self, code):
        self.lua.execute(code)

    def test_current_id_not_output_name_item_membership_or_base_rank(self):
        self.run_lua('''
            local c=S.RecipeContext(form)
            assert(c.id==101 and c.name=="Recipe A")
            assert(lastQuery.id==101 and lastQuery.reagents==form.transaction.reagents and lastQuery.guid=="allocation-A")
            S.RegisterRecipes();assert(reader:IsShown())
            assert(reader.fontstrings[1].text:find("สูตรเอ",1,true))
            assert(reader.fontstrings[2].text:find("10",1,true))
            assert(form.OutputText.text=="Unrelated output item" and form.Description.text=="Heals 10 health.")
            assert(form.OutputText.font==nil and form.Description.font==nil and form.Description.point==nil)
        ''')

    def test_recipe_list_hover_matches_current_rank_and_clears_on_recycling(self):
        self.run_lua('''
            local handlers, callbacks = {}, {}
            EventRegistry={RegisterCallback=function(_,event,fn,owner)
                assert(not handlers[event]);handlers[event]=function(...) fn(owner,...) end
            end}
            local events={OnScroll="OnScroll",OnInitializedFrame="OnInitializedFrame",
                OnReleasedFrame="OnReleasedFrame",OnDataProviderReassigned="OnDataProviderReassigned"}
            ScrollBoxListMixin={Event=events}
            local list=frame(page)
            local box=frame(list)
            page.RecipeList=list;list.ScrollBox=box
            function box:RegisterCallback(event,fn,owner)
                assert(not callbacks[event]);callbacks[event]=function(...) fn(owner,...) end
            end
            local button=frame(box)
            button.Label=frame(button)
            local base={recipeID=101,name="Recipe A"}
            local high={recipeID=202,name="Recipe B"}
            local nameOnly={recipeID=301,name="Empty Recipe"}
            local node={data={recipeInfo=base}}
            local member=button
            function button:GetElementData() return node end
            function box:FindFrame(element) assert(element==node);return member end
            local learned,localMode,stale=high,true,false
            Professions={InLocalCraftingMode=function() return localMode end,
                GetHighestLearnedRecipe=function(info) assert(info==node.data.recipeInfo);return learned end}
            C_TradeSkillUI.GetRecipeInfo=function(id)
                if stale then return base end
                return ({[101]=base,[202]=high,[301]=nameOnly})[id]
            end
            button.Label.text=high.name
            S.RegisterRecipes();S.RegisterRecipes()
            local hover
            for _,f in ipairs(frames) do if f.name=="AlphaWoWRecipeHover" then hover=f end end
            assert(hover and not hover:IsShown())
            local function enter(payload) handlers["Professions.RecipeListOnEnter"](button,payload or node.data) end
            local function shown(title)
                enter();assert(hover:IsShown() and hover.fontstrings[1].text==title)
                assert(hover.point[2]==button and button.Label.font==nil)
            end
            local function hidden() enter();assert(not hover:IsShown() and S.stats.errors==0) end
            shown("สูตรบี")
            assert(reader:IsShown() and reader.fontstrings[1].text:find("สูตรเอ",1,true))
            shown("สูตรบี");assert(#button.hooks.OnLeave==1 and #button.hooks.OnHide==1)
            button:Fire("OnLeave");assert(not hover:IsShown())
            for _,event in pairs(events) do shown("สูตรบี");callbacks[event]();assert(not hover:IsShown()) end
            shown("สูตรบี");button:Hide();assert(not hover:IsShown());button:Show()
            enter({recipeInfo=high});assert(not hover:IsShown())
            member=frame(box);hidden();member=button
            stale=true;hidden();stale=false
            changing=true;hidden();changing=false
            minimized=true;hidden();minimized=false
            localMode=false;hidden();localMode=true
            high.isRecraft=true;hidden();high.isRecraft=nil
            button.Label.text=base.name;hidden();button.Label.text=high.name
            shown("สูตรบี");combat=true;event("PLAYER_REGEN_DISABLED");hidden();combat=false
            shown("สูตรบี");event("TRADE_SKILL_DATA_SOURCE_CHANGING");hidden()
            event("TRADE_SKILL_DATA_SOURCE_CHANGED");hidden()
            form:Init(form.currentRecipeInfo);shown("สูตรบี")
            learned=nil;node.data.recipeInfo=nameOnly;button.Label.text=nameOnly.name
            shown("สูตรชื่อเท่านั้น")
            S.settings.englishNames=true;shown("สูตรชื่อเท่านั้น (Empty Recipe)")
            S.settings.enabled=false;S.RefreshRecipe();hidden()
        ''')

    def test_comprehend_scroll_recipes_use_each_exact_id_with_identical_text(self):
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.run_lua('''
            local sameDescription="Decipher an untranslated scroll."
            for _,id in ipairs({1309973,1309965,1310029,1310030}) do
                names[id]="Comprehend Scroll";descriptions[id]=sameDescription
            end
            selectRecipe(form,1309973);S.RegisterRecipes()
            for _,id in ipairs({1309973,1309965,1310029,1310030}) do
                selectRecipe(form,id);form:Init(form.currentRecipeInfo)
                assert(lastQuery.id==id and reader:IsShown())
                assert(reader.fontstrings[2].text:find("ถอดความคัมภีร์ที่ยังไม่ได้แปล",1,true))
            end
            form.transaction.id=1309973;form:UpdateRecipeDescription()
            assert(not reader:IsShown())
            names[9001]="Comprehend Scroll";descriptions[9001]=sameDescription
            selectRecipe(form,9001);form:Init(form.currentRecipeInfo)
            assert(not reader:IsShown())
        ''')

    def test_identity_mismatch_nil_info_or_unknown_name_falls_back(self):
        for code in ('form.currentRecipeInfo=nil', 'form.transaction.id=202', 'form.recipeSchematic.recipeID=202',
                     'names[101]=nil', 'form.currentRecipeInfo.recipeID=9001'):
            with self.subTest(code=code):
                self.run_lua('selectRecipe(form,101);names[101]="Recipe A";' + code + ';assert(S.RecipeContext(form)==nil)')

    def test_linked_tinker_recipes_use_visible_slots_and_permanence_branch(self):
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.run_lua('''
            local prefix="Augment your belt to give the following effect: "
            local warning=" This enhancement is permanent and cannot be removed or replaced."
            local cases={
                {1226210,"Tinker: Teleport","Teleport forward 17 yds.","17 หลา"},
                {1226211,"Tinker: Nitro Boosts","Activate a set of jets to increase your movement speed by up to 95%, for up to 4 sec.","95% เป็นเวลาสูงสุด 4 วินาที"},
                {1226212,"Tinker: Magnetic Displacement","Disrupt a magnetic field between you and your nearby enemy target, knocking you both away. Can only affect targets up to 3 levels higher than you. Some targets cannot be displaced. Targets can only be affected by this effect once every 2 min.","เพียงครั้งเดียวทุก 2 นาที"},
            }
            S.settings.original=false
            S.RegisterRecipes()
            for _,case in ipairs(cases) do
                local id=case[1]
                names[id]=case[2]
                descriptions[id]=prefix..case[3]
                selectRecipe(form,id);form:Init(form.currentRecipeInfo)
                assert(reader:IsShown() and reader.fontstrings[2].text:find(case[4],1,true))
                assert(not reader.fontstrings[2].text:find("ถาวร",1,true))
                descriptions[id]=descriptions[id]..warning
                selectRecipe(form,id);form:Init(form.currentRecipeInfo)
                assert(reader:IsShown() and reader.fontstrings[2].text:find("ถาวร",1,true))
                descriptions[id]=descriptions[id].." Unexpected effect."
                selectRecipe(form,id);form:Init(form.currentRecipeInfo)
                assert(not reader:IsShown())
            end
            descriptions[1226210]=prefix..cases[2][3]
            selectRecipe(form,1226210);form:Init(form.currentRecipeInfo)
            assert(not reader:IsShown())
        ''')

    def test_modes_hidden_ancestors_and_unknown_availability_decline(self):
        for code in ('form.isInspection=true', 'form.isRecraftOverride=true', 'form.isRecraft=true',
                     'form.currentRecipeInfo.isDummyRecipe=true', 'form.currentRecipeInfo.isRecraft=true',
                     'form.transaction.IsRecraft=function() return true end',
                     'form.transaction.IsRecraft=nil', 'changing=true', 'minimized=true',
                     'ProfessionsFrame.shown=false', 'page.shown=false', 'form.Description.shown=false'):
            with self.subTest(code=code):
                self.run_lua('''
                    selectRecipe(form,101);form.isInspection=nil;form.isRecraftOverride=nil;form.isRecraft=nil
                    changing=false;minimized=false;ProfessionsFrame.shown=true;page.shown=true;form.Description.shown=true
                ''' + code + ';assert(S.RecipeContext(form)==nil)')

    def test_stale_visible_description_does_not_match_current_allocation(self):
        self.run_lua('''
            S.RegisterRecipes();assert(reader:IsShown())
            descriptions[101]="Heals 40 health."
            form.transaction.guid="allocation-B"
            form:UpdateRecipeDescription();assert(not reader:IsShown())
            form.Description.text=descriptions[101];form:UpdateRecipeDescription()
            assert(reader:IsShown() and reader.fontstrings[2].text:find("40",1,true))
            assert(lastQuery.guid=="allocation-B")
        ''')

    def test_missing_allocation_guid_method_is_not_public_nil_guid(self):
        self.run_lua('''
            form.transaction.guid=nil
            assert(S.RecipeContext(form)~=nil)
            form.transaction.GetAllocationItemGUID=nil
            assert(S.RecipeContext(form)==nil)
        ''')

    def test_no_body_cache_across_a_b_a_new_transaction_and_level(self):
        self.run_lua('''
            S.RegisterRecipes()
            selectRecipe(form,202);form:Init(form.currentRecipeInfo)
            assert(reader.fontstrings[1].text:find("สูตรบี",1,true))
            descriptions[101]="Heals 55 health.";selectRecipe(form,101)
            form.currentRecipeInfo.recipeLevel=9;form:Init(form.currentRecipeInfo)
            assert(reader.fontstrings[1].text:find("สูตรเอ",1,true))
            assert(reader.fontstrings[2].text:find("55",1,true))
            form:Init(nil);assert(not reader:IsShown())
            form:UpdateOutputItem();assert(not reader:IsShown())
        ''')

    def test_name_only_requires_current_verified_name_and_confirmed_empty_text(self):
        self.run_lua('''
            selectRecipe(form,301);S.RegisterRecipes();assert(reader:IsShown())
            assert(reader.fontstrings[2].text=="")
            descriptions[301]="Loading description now";form:UpdateOutputItem();assert(not reader:IsShown())
            descriptions[301]="";S.recipeNames[301].reviewStatus="NEEDS_REVIEW"
            form:UpdateOutputItem();assert(not reader:IsShown())
            S.recipeNames[301].reviewStatus="VERIFIED";names[301]="Other name"
            form:UpdateOutputItem();assert(not reader:IsShown())
            names[301]="Empty Recipe";descriptions[301]=nil
            form:UpdateOutputItem();assert(not reader:IsShown())
        ''')

    def test_description_failure_does_not_downgrade_to_name_only(self):
        self.run_lua('''
            S.recipeNames[101]={originalName="Recipe A",translatedName="ชื่อแยก",reviewStatus="VERIFIED"}
            descriptions[101]="";form.Description.text=""
            S.RegisterRecipes();assert(not reader:IsShown())
            descriptions[101]="Heals 10 health during combat.";form.Description.text=descriptions[101]
            form:UpdateRecipeDescription();assert(not reader:IsShown())
        ''')

    def test_secret_values_and_protected_tables_decline_without_indexing(self):
        self.run_lua('''
            local bad=trap();secret[bad]=true
            assert(S.RecipeContext(bad)==nil)
            form.currentRecipeInfo=bad;assert(S.RecipeContext(form)==nil)
            selectRecipe(form,101);form.transaction=bad;assert(S.RecipeContext(form)==nil)
            selectRecipe(form,101);form.recipeSchematic=bad;assert(S.RecipeContext(form)==nil)
            selectRecipe(form,101);form.Description=bad;assert(S.RecipeContext(form)==nil)
        ''')

    def test_secret_numeric_id_boolean_name_text_and_reagents_decline(self):
        self.run_lua('''
            secret[101]=true;assert(S.RecipeContext(form)==nil);secret[101]=nil
            secret[false]=true;assert(S.RecipeContext(form)==nil);secret[false]=nil
            secret["Recipe A"]=true;assert(S.RecipeContext(form)==nil);secret["Recipe A"]=nil
            secret["Heals 10 health."]=true;assert(S.RecipeContext(form)==nil);secret["Heals 10 health."]=nil
            inaccessible[form.transaction.reagents]=true;assert(S.RecipeContext(form)==nil)
        ''')

    def test_later_addon_load_and_idempotent_hooks(self):
        self.run_lua('''
            local original=ProfessionsFrame;ProfessionsFrame=nil
            S.RegisterRecipes();assert(next(hookCalls)==nil)
            ProfessionsFrame=original;event("ADDON_LOADED","Blizzard_ProfessionsTemplates")
            assert(next(hookCalls)==nil)
            event("ADDON_LOADED","Blizzard_Professions")
            S.RegisterRecipes();event("ADDON_LOADED","Blizzard_Professions")
            for _,method in ipairs({"Init","UpdateRecipeDescription","UpdateOutputItem","ClearRecipeDescription","ClearTransaction"}) do
                assert(hookCalls[method]==1)
            end
            assert(#form.hooks.OnShow==1 and #form.hooks.OnHide==1)
        ''')

    def test_hide_clear_combat_and_disabled_setting_clear_reader(self):
        self.run_lua('''
            S.RegisterRecipes();assert(reader:IsShown())
            form:ClearRecipeDescription();assert(not reader:IsShown())
            form.Description.text=descriptions[101];form:UpdateRecipeDescription();assert(reader:IsShown())
            form:Hide();form:UpdateOutputItem();assert(not reader:IsShown())
            form:Show();assert(reader:IsShown())
            combat=true;event("PLAYER_REGEN_DISABLED");assert(not reader:IsShown())
            form:UpdateRecipeDescription();assert(not reader:IsShown());combat=false
            S.settings.enabled=false;S.RefreshRecipe();assert(not reader:IsShown())
            S.settings.enabled=true;S.RefreshRecipe();assert(reader:IsShown())
            form:ClearTransaction();assert(not reader:IsShown())
        ''')

    def test_source_change_blocks_late_old_form_updates(self):
        self.run_lua('''
            S.RegisterRecipes();assert(reader:IsShown())
            event("TRADE_SKILL_DATA_SOURCE_CHANGING");assert(not reader:IsShown())
            form:UpdateOutputItem();assert(not reader:IsShown())
            event("TRADE_SKILL_DATA_SOURCE_CHANGED");assert(not reader:IsShown())
            form:Fire("OnShow");assert(not reader:IsShown())
            -- Old Blizzard loader can still invoke these methods on retained fields.
            form:UpdateRecipeDescription();assert(not reader:IsShown())
            form:UpdateOutputItem();assert(not reader:IsShown())
            -- A fresh current Init can explicitly establish the new form context.
            selectRecipe(form,202);form:Init(form.currentRecipeInfo);assert(reader:IsShown())
        ''')

    def test_all_compiled_reviewed_recipe_names_obey_exact_lookup_gates(self):
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/RecipeData.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.run_lua('''
            local count=0
            for id,row in pairs(S.recipeNames) do
                count=count+1
                assert(row.reviewStatus=="VERIFIED")
                local title,body=S.LookupRecipeName(id,row.originalName,"")
                assert(title==row.translatedName and body=="")
                assert(S.LookupRecipeName(id,row.originalName.." changed","")==nil)
                assert(S.LookupRecipeName(id,row.originalName,"Unexpected new description")==nil)
                assert(S.LookupRecipeName(id,row.originalName,nil)==nil)
                row.reviewStatus="NEEDS_REVIEW"
                assert(S.LookupRecipeName(id,row.originalName,"")==nil)
                row.reviewStatus="VERIFIED"
                S.supported=false
                assert(S.LookupRecipeName(id,row.originalName,"")==nil)
                S.supported=true
            end
            assert(count>=329)
            compiledNameCount=count
        ''')

    def test_incomplete_parent_hooks_fail_without_partial_registration(self):
        self.run_lua('''
            page.HookScript=nil
            local ok=pcall(S.RegisterRecipes)
            assert(ok and next(hookCalls)==nil and not reader:IsShown())
        ''')

    def test_font_failure_oversize_or_changed_build_never_shows(self):
        self.run_lua('''
            fontOK=false;S.RegisterRecipes();assert(not reader:IsShown())
            fontOK=true;UIParent.height=40;S.RefreshRecipe();assert(not reader:IsShown())
            UIParent.height=1080;S.supported=false;S.RefreshRecipe();assert(not reader:IsShown())
        ''')

    def test_real_settings_startup_and_toggle_refresh_only_companion(self):
        self.run_lua('''
            SlashCmdList={};S.reader=frame(UIParent)
            function S.RegisterTooltips() tooltipRegistrations=(tooltipRegistrations or 0)+1 end
        ''')
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/Settings.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.run_lua('''
            event("ADDON_LOADED","ForeverThai")
            assert(tooltipRegistrations==1 and reader:IsShown())
            local check
            for _,f in ipairs(frames) do if f.kind=="CheckButton" then check=f;break end end
            assert(check)
            check:SetChecked(false);check:Fire("OnClick")
            assert(not S.settings.enabled and not reader:IsShown())
            check:SetChecked(true);check:Fire("OnClick")
            assert(S.settings.enabled and reader:IsShown())
            assert(form.OutputText.text=="Unrelated output item" and form.Description.text=="Heals 10 health.")
        ''')

    def test_toc_loads_name_data_and_companion_in_dependency_order(self):
        toc = (ROOT / 'addon/ForeverThai/ForeverThai.toc').read_text(encoding='utf-8').splitlines()
        paths = [line.strip().replace('\\', '/') for line in toc]
        order = {name: paths.index('Skills/' + name + '.lua')
                 for name in ('Core', 'RecipeData', 'RawText', 'Recipes', 'Settings')}
        self.assertLess(order['Core'], order['RawText'])
        self.assertLess(order['Core'], order['RecipeData'])
        self.assertLess(max(order['RawText'], order['RecipeData']), order['Recipes'])
        self.assertLess(order['Recipes'], order['Settings'])

    def test_hidden_parent_and_close_cannot_be_revived_by_method_hook(self):
        self.run_lua('''
            S.RegisterRecipes();ProfessionsFrame:Hide();assert(not reader:IsShown())
            form:UpdateOutputItem();assert(not reader:IsShown())
            ProfessionsFrame.shown=true;event("TRADE_SKILL_CLOSE")
            form:UpdateRecipeDescription();assert(not reader:IsShown())
        ''')


if __name__ == '__main__':
    unittest.main()
