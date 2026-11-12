"""Replay the combined Launcher ZIP and its existing skill UI test fixtures."""
import argparse
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from lupa.lua51 import LuaRuntime
from package_combined_launcher import ADDON, SKILLS_PROJECT, TOC, modules, sha, validate_public_zip


def lua_with_font_setting(*args, **kwargs):
    lua = LuaRuntime(*args, **kwargs)
    lua.globals().ForeverThaiDisplayMode = "font"
    return lua


def check(archive, quest_archive):
    validate_public_zip(archive)
    sys.path.insert(0, str(SKILLS_PROJECT / "tests"))
    import test_item_tooltip
    import test_recipe_panel
    import test_spellbook_metadata

    with (TemporaryDirectory() as tmp, ZipFile(archive) as combined, ZipFile(quest_archive) as quests):
        assert combined.testzip() is None
        assert not any("/Dev/" in name or name.endswith(("/Discovery.lua", "/Capture.lua"))
                       for name in combined.namelist())
        toc = combined.read(TOC).decode("utf-8")
        paths = modules(toc)
        assert {"Tracker.lua", "Observe.lua", "Skills/Data.lua", "Skills/RecipeData.lua",
                "Skills/TalentTreeLabels.lua", "Skills/ItemEffects.lua"} <= set(paths)
        for name in ("Catalog.lua", "Match.lua", "Events.lua", "Observe.lua", "Tracker.lua", "Atlas.lua"):
            assert combined.read(ADDON + name) == quests.read(ADDON + name)
        if "Speech.lua" in paths:
            assert "SpeechData.lua" in paths
            for name in ("Speech.lua", "SpeechData.lua"):
                assert combined.read(ADDON + name) == quests.read(ADDON + name)
            assert "ForeverThaiSpeech" in re.search(r"^## SavedVariables: (.+)$", toc, re.M)[1]
        for variable in ("ForeverThaiQuestieTracker", "ForeverThaiDisplayMode", "ForeverThaiObserved",
                         "ForeverThaiAutoCaptureLog", "AlphaWoWSkillsDB"):
            assert variable in re.search(r"^## SavedVariables: (.+)$", toc, re.M)[1]
        combined.extractall(Path(tmp) / "addon")
        addon = Path(tmp) / "addon/ForeverThai"

        # Reuse the UI fixture and load the entire real TOC into one namespace.
        fixture = test_recipe_panel.RecipePanelTests()
        with patch.object(test_recipe_panel, "ROOT", Path(tmp)):
            fixture.setUp()
        lua = fixture.lua
        lua.execute('''
            addon={};frames={};SlashCmdList={};STANDARD_TEXT_FONT="DefaultFont"
            function GetBuildInfo() return "1.60.1","70888","",16001 end
            function UnitName() return "Aeri" end
            function UnitClass() return "Druid","DRUID" end
            function UnitRace() return "Night Elf" end
            TooltipDataProcessor={AllTypes=-1,AddTooltipPostCall=function(id,fn) tooltip=fn end}
            function UIParent:GetWidth() return 1920 end
            function UIParent:GetEffectiveScale() return 1 end
            local makeFrame=CreateFrame
            function CreateFrame(...)
                local f=makeFrame(...)
                local createLabel=f.CreateFontString
                function f:CreateFontString(...)
                    local label=createLabel(self,...)
                    label.SetJustifyV=function() end
                    return label
                end
                for _,name in ipairs({"SetMovable","RegisterForDrag","SetScrollChild","SetVerticalScroll"}) do
                    f[name]=function() end
                end
                return f
            end
            ForeverThaiDisplayMode="image"
            ForeverThaiQuestieTracker=true
            AlphaWoWSkillsDB={enabled=true,fontSize=19,original=false}
        ''')
        load = lua.eval("function(source, name) assert(loadstring(source, name))('ForeverThai', addon) end")
        for name in paths:
            load((addon / name).read_text("utf-8-sig"), "@" + name)
        lua.execute('''
            event("ADDON_LOADED","ForeverThai")
            S=addon.skills
            assert(S.supported and S.settings.fontSize==19, "Skills failed at startup on build 70888")
            assert(SlashCmdList.FOREVERTHAI and SlashCmdList.ALPHAWOWSKILLS)
            assert(ForeverThaiQuestieTracker==true and type(tooltip)=="function")
            assert(addon.Translate(addon.quests[456].title,"The Balance of Nature")=="สมดุลแห่งธรรมชาติ")
            local stoneform=S.records["spell:20594"]
            assert(stoneform and stoneform.originalName=="Stoneform")
            local widget=S.CreateTextBlock(UIParent)
            assert(widget:Draw(stoneform.translatedName,350,19)>0)
            local drawn=false
            for _,f in ipairs(frames) do
                for _,tx in ipairs(f.textures or {}) do
                    if tx:IsShown() and tx.texture and tx.texture:find("SkillsThai",1,true) then drawn=true end
                end
            end
            assert(drawn, "Stoneform must use the Thai atlas even when SetFont succeeds")
        ''')
        print(f"Combined TOC loaded {len(paths)} modules. Quest text and Stoneform atlas passed.")
        lua.execute('''
            Enum={TooltipDataType={Item=0,Spell=1},TooltipDataLineType={SpellDescription=34}}
            local tip=frame(UIParent)
            local name, rank="Devotion Aura", "Rank 2"
            local description="Gives 160 additional armor to party members within 30 yards. "..
                "Players may only have one Aura on them per Paladin at any one time."
            local data={type=1,id=10290,lines={{leftText=name,rightText=rank},
                {leftText="Instant"},{type=34,lineIndex=3,leftText=description}}}
            local info={getterName="GetAction",getterArgs={6},tooltipData=data}
            function GetActionInfo(slot) assert(slot==6);return "spell",10290 end
            function tip:GetProcessingTooltipInfo() return info end
            function tip:GetPrimaryTooltipInfo() return info end
            function tip:GetEffectiveScale() return 1 end
            function tip:GetRect() return 1372,300,246,94 end
            function tip:GetLeftLine(index)
                local line=data.lines[index]
                return line and {IsShown=function() return true end,GetText=function() return line.leftText end}
            end
            function tip:NumLines() return #data.lines end
            tip.ClearLines=forbidden
            tip.AddLine=forbidden
            local heading, text
            local remember=S.RememberLongText
            function S.RememberLongText(h,b) heading,text=h,b;return remember(h,b) end
            assert(S.OnTooltip(tip,data)=="shown" and S.reader:IsShown())
            assert(heading=="ออร่าแห่งความภักดี")
            assert(text:find("เพิ่มเกราะ 160 หน่วย",1,true) and text:find("ระยะ 30 หลา",1,true))
            assert(data.lines[1].rightText==rank and data.lines[3].leftText==description)
            tip:Fire("OnTooltipCleared")
            assert(not S.reader:IsShown())
        ''')
        print("Devotion Aura rank 2 action-bar tooltip: exact screenshot wording and 160 armor/30 yards passed.")
        lua.execute('''
            local build, locale = "70862", "enUS"
            function GetBuildInfo() return "1.60.1", build, "", 16001 end
            function GetLocale() return locale end
            local tip=frame(UIParent)
            local description="Dramatically increases stealth detection for 20 sec."
            local data={type=1,id=20600,lines={{leftText="Perception",rightText="Racial"},
                {leftText="Instant",rightText="3 min cooldown"},
                {type=34,lineIndex=3,leftText=description}}}
            local info={getterName="GetAction",getterArgs={6},tooltipData=data}
            function GetActionInfo(slot) assert(slot==6);return "spell",20600 end
            function tip:GetProcessingTooltipInfo() return info end
            function tip:GetPrimaryTooltipInfo() return info end
            function tip:GetEffectiveScale() return 1 end
            function tip:GetRect() return 1085,87,248,70 end
            function tip:GetLeftLine(index)
                local line=data.lines[index]
                return line and {IsShown=function() return true end,GetText=function() return line.leftText end}
            end
            function tip:NumLines() return #data.lines end
            tip.ClearLines=forbidden
            tip.AddLine=forbidden
            local heading, text
            local remember=S.RememberLongText
            function S.RememberLongText(h,b) heading,text=h,b;return remember(h,b) end
            for _,supportedBuild in ipairs({"70862","70888"}) do
                build=supportedBuild
                S.Initialize()
                assert(S.supported and S.settings.enabled, "Skills disabled on build "..build)
                tooltip(tip,data)
                assert(S.reader:IsShown(), "Perception failed on build "..build)
                assert(heading=="ประสาทสัมผัสเฉียบคม")
                assert(text:find("เพิ่มความสามารถในการตรวจจับผู้พรางตัวอย่างมากเป็นเวลา 20 วินาที",1,true))
                assert(data.lines[1].rightText=="Racial" and data.lines[3].leftText==description)
                tip:Fire("OnTooltipCleared")
                assert(not S.reader:IsShown())
            end
            data.lines[3].leftText="Increases stealth detection slightly for 20 sec."
            tooltip(tip,data)
            assert(not S.reader:IsShown(), "Unverified Perception wording must stay in English")
            build="70889"
            S.Initialize()
            assert(not S.supported)
            build,locale="70888","frFR"
            S.Initialize()
            assert(not S.supported)
        ''')
        print("Perception action-bar screenshot replay passed on builds 70862 and 70888.")

        suite = unittest.TestSuite()
        for cls, names in (
            (test_recipe_panel.RecipePanelTests, (
                "test_all_compiled_reviewed_recipe_names_obey_exact_lookup_gates",
                "test_recipe_list_hover_matches_current_rank_and_clears_on_recycling",
                "test_toc_loads_name_data_and_companion_in_dependency_order",
            )),
            (test_item_tooltip.ItemTooltipTests, (
                "test_real_compiled_effect_through_tooltip_callback",
                "test_wrong_kind_wrong_item_and_replaced_live_text_fall_back",
                "test_reviewed_base_casts_require_full_native_text_and_preserve_visible_values",
            )),
            (test_spellbook_metadata.SpellbookMetadataTests, (
                "test_profession_helper_titles_require_the_current_native_player_spellbook_entry",
                "test_combat_reader_translates_only_exact_native_action_cards",
                "test_completed_talent_reads_visible_requirements_and_preserves_native_tooltip",
            )),
        ):
            suite.addTests(cls(name) for name in names)
        # Some isolated fixtures model explicit font mode and omit the texture renderer.
        with (patch.object(test_recipe_panel, "ROOT", Path(tmp)),
              patch.object(test_item_tooltip, "ROOT", Path(tmp)),
              patch.object(test_spellbook_metadata, "ROOT", Path(tmp)),
              patch.object(test_recipe_panel, "LuaRuntime", lua_with_font_setting)):
            result = unittest.TextTestRunner(verbosity=2).run(suite)
        assert result.wasSuccessful()

    receipt_path = archive.with_suffix(".json")
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt["sha256"] == sha(archive.read_bytes())
    receipt.update(combined_toc_replay_passed=True, skill_ui_fixture_tests_passed=result.testsRun,
                   devotion_aura_rank_2_screenshot_replay_passed=True,
                   perception_screenshot_builds=["70862", "70888"])
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", "utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("quest_archive", type=Path)
    args = parser.parse_args()
    check(args.archive, args.quest_archive)
