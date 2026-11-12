"""Port only the recovered selected Skill UI checks to the current Cloud candidate.

The full-TOC/Stoneform/Devotion/Perception replay and nine-case selection below
are retained verbatim from the transferred reference. Its unavailable packaging
helper, old-author comparison and old receipt wrapper are intentionally replaced.
Original fixture files remain byte-identical under tests/recovered_skill/.
"""
import argparse,ast,hashlib,json,pathlib,re,sys,traceback,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile
from lupa.lua51 import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]
RECOVERED=ROOT/"tests/recovered_skill"
def sha(data):return hashlib.sha256(data).hexdigest()
def modules(toc):return [v.strip().replace("\\","/") for v in toc.splitlines() if v.strip() and not v.startswith("#")]
def lua_with_font_setting(*args,**kwargs):
    lua=LuaRuntime(*args,**kwargs)
    lua.globals().ForeverThaiDisplayMode="font"
    return lua

def verify_fixture_manifest():
    manifest=json.loads((RECOVERED/"manifest.json").read_text())
    for item in manifest:
        data=(RECOVERED/item["path"]).read_bytes()
        assert len(data)==item["bytes"] and sha(data)==item["sha256"],item["path"]
    # Exact original replay assertions, including the explicit-font patch, stay intact.
    reference=(RECOVERED/"reference/check_combined_launcher.py").read_text()
    begin=reference.index("        # Reuse the UI fixture")
    end=reference.index('\n    receipt_path = archive.with_suffix')
    assert reference[begin:end] in Path(__file__).read_text(),"Reference replay was modified"
    return manifest

def check(archive):
    sys.path.insert(0,str(RECOVERED/"tests"))
    import test_item_tooltip
    import test_recipe_panel
    import test_spellbook_metadata
    with (TemporaryDirectory() as tmp, ZipFile(archive) as combined):
        assert combined.testzip() is None
        names=combined.namelist()
        assert len(names)==len(set(names))
        expected={str(p.relative_to(ROOT/"src")):p for p in (ROOT/"src/ForeverThai").rglob("*") if p.is_file()}
        assert set(names)==set(expected),"Candidate differs from current source tree"
        for name in names:
            path=pathlib.PurePosixPath(name)
            assert not path.is_absolute() and ".." not in path.parts and "\\" not in name
            assert (combined.getinfo(name).external_attr>>16&0o170000)!=0o120000
            assert combined.read(name)==expected[name].read_bytes(),name
        assert not any("/Dev/" in name or name.endswith(("/Discovery.lua","/Capture.lua")) for name in names)
        toc=combined.read("ForeverThai/ForeverThai.toc").decode()
        paths=modules(toc)
        assert {"Tracker.lua","Observe.lua","Skills/Data.lua","Skills/RecipeData.lua","Skills/TalentTreeLabels.lua","Skills/ItemEffects.lua"}<=set(paths)
        assert all("ForeverThai/"+p in names for p in paths)
        for variable in ("ForeverThaiQuestieTracker","ForeverThaiDisplayMode","ForeverThaiObserved","ForeverThaiAutoCaptureLog","AlphaWoWSkillsDB","ForeverThaiSpeech"):
            assert variable in re.search(r"^## SavedVariables: (.+)$",toc,re.M)[1]
        assert "SpeechData.lua" in paths and "Speech.lua" in paths
        combined.extractall(Path(tmp)/"addon")
        addon=Path(tmp)/"addon/ForeverThai"
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

    assert result.testsRun==9 and not result.skipped
    return result.testsRun,len(paths)

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive",type=Path)
    parser.add_argument("--report",type=Path,default=ROOT/"evidence/legacy-skill-cloud.json")
    args=parser.parse_args()
    source_manifest={str(p.relative_to(ROOT/"src")):sha(p.read_bytes()) for p in sorted((ROOT/"src/ForeverThai").rglob("*")) if p.is_file()}
    report=dict(candidate_path=args.archive.name,candidate_sha256=sha(args.archive.read_bytes()),source_manifest_sha256=sha(json.dumps(source_manifest,sort_keys=True).encode()),fixture_zip_sha256="ca3559f718c688054a2f870117ad77007ad3fa3c6c8bcff0278eda38ed5706ab",scope="Recovered nine selected Skill UI simulations plus original full-TOC bitmap/tooltip/build gates. Not NPC686 or in-game verification.")
    try:
        manifest=verify_fixture_manifest()
        selected,toc_count=check(args.archive)
        report.update(status="passed",selected_tests_passed=selected,toc_modules=toc_count,stoneform_real_bitmap_passed=True,devotion_aura_160_armor_30_yards_passed=True,perception_builds_passed=["70862","70888"],unsupported_build_and_locale_gates_passed=True,fixture_manifest=manifest)
        report["selected_cases"]=re.findall(r'"(test_[^"]+)"',(RECOVERED/"reference/check_combined_launcher.py").read_text())
    except Exception:
        report.update(status="failed",error=traceback.format_exc())
        raise
    finally:
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
