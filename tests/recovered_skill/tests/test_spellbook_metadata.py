from pathlib import Path
import unittest

import test_recipe_panel

ROOT = Path(__file__).resolve().parents[1]


class SpellbookMetadataTests(unittest.TestCase):
    def setUp(self):
        test_recipe_panel.RecipePanelTests.setUp(self)
        for module in ('Adapter', 'Tooltip'):
            source = (ROOT / 'addon/ForeverThai/Skills' / (module + '.lua')).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum={TooltipDataType={Spell=1},SpellBookSpellBank={Player=0,Pet=1},
                SpellBookItemType={Spell=1,FutureSpell=2,Flyout=4}}
            data={type=1,id=101,lines={{leftText="Recipe A"},{leftText="Heals 10 health."}}}
            info={getterName="GetSpellBookItem",getterArgs={7,0},tooltipData=data}
            tip=frame(UIParent)
            function tip:GetProcessingTooltipInfo() return info end
            function tip:GetPrimaryTooltipInfo() return primary or info end
            entry={spellID=101,itemType=1,name="Recipe A",subName="Rank 2"}
            learnLevel=24
            calls=0
            C_SpellBook={GetSpellBookItemInfo=function(slot,bank)
                    assert(slot==7 and bank==0);return entry end,
                GetSpellBookItemLevelLearned=function(slot,bank)
                    assert(slot==7 and bank==0);calls=calls+1;return learnLevel end}
            function metadata() return S.SpellbookMetadata(tip,data,S.Context(tip,data)) end
        ''')

    def test_profession_helper_titles_require_the_current_native_player_spellbook_entry(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            local shown
            function tip:GetLeftLine(i)
                if i==1 then return {IsShown=function() return true end,GetText=function() return shown end} end
            end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            tip.ClearLines=forbidden
            tip.AddLine=forbidden
            for _,row in ipairs({{1235230,"Mining","การทำเหมือง"},
                {1235236,"Herb Gathering","เก็บสมุนไพร"},{1235244,"Engineering","วิศวกรรม"}}) do
                local id,name,thai=unpack(row)
                shown=name
                data={type=1,id=id,lines={{leftText=name}}}
                info.tooltipData=data
                entry={spellID=id,actionID=101,itemType=1,name=name}
                assert(S.OnTooltip(tip,data)=="shown" and titleSeen==thai and bodySeen=="")
                S.settings.englishNames=true
                assert(S.OnTooltip(tip,data)=="shown" and titleSeen==thai.." ("..name..")")
                S.settings.englishNames=false
                entry.spellID=101;entry.actionID=id;assert(not S.Context(tip,data));entry.spellID=id
                entry.itemType=2;assert(not S.Context(tip,data));entry.itemType=1
                entry.name="Other";assert(not S.Context(tip,data));entry.name=name
                shown="Other";assert(not S.Context(tip,data));shown=name
                primary={};assert(not S.Context(tip,data));primary=nil
                data.lines[1].leftText="Other";assert(not S.Context(tip,data));data.lines[1].leftText=name
                info.getterArgs[2]=1;assert(not S.Context(tip,data));info.getterArgs[2]=0
                info.getterName="GetAction";assert(S.OnTooltip(tip,data)=="missing")
                info.getterName="GetSpellBookItem"
            end
            for _,id in ipairs({2369,2371,2577,2578,2579,7738}) do
                assert(not S.professionHelperTitles[id])
            end
        ''')

    def test_opt_in_capture_keeps_creature_template_and_native_pet_action_only(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Capture.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            local title,body="Example Action","Stuns the target."
            local shown={title,body}
            local petGUID="Creature-0-999-888-777-89-00AABBCCDD"
            local guidCalls,actionID,isToken,inCombat=0,19482,false,false
            Enum.TooltipDataType.PetAction=11
            Enum.TooltipDataLineType={SpellDescription=2}
            data={type=11,id=900,lines={{leftText=title,lineIndex=1},
                {leftText=body,lineIndex=2,type=2}}}
            info={getterName="GetPetAction",getterArgs={3},tooltipData=data}
            function GetPetActionInfo(slot)
                assert(slot==3)
                return title,123,isToken,false,false,false,actionID
            end
            function UnitGUID(unit)
                assert(unit=="pet")
                guidCalls=guidCalls+1
                return petGUID
            end
            function InCombatLockdown() return inCombat end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local context=S.Context(tip,data)
            assert(context and context.key=="spell:19482")
            assert(guidCalls==0 and not AlphaWoWSkillsCapture)
            S.captureEnabled=true
            primary={}
            S.Context(tip,data)
            primary=nil
            shown[2]="A different action."
            S.Context(tip,data)
            shown[2]=body
            isToken=true
            S.Context(tip,data)
            isToken=false
            assert(guidCalls==0 and not AlphaWoWSkillsCapture)
            S.Context(tip,data)
            local db=AlphaWoWSkillsCapture
            local record=db.records["observed-pet-action:89:19482"]
            assert(record and record.id==19482 and record.creatureID==89 and record.category=="observed-pet-action")
            assert(record.name==title and #record.lines==1 and record.lines[1]==body and db.count==1)
            assert(not record.guid and not record.petGUID and not db.records["observed-pet-action:89:3"])
            petGUID="Pet-0-999-888-777-11859-0123456789"
            S.Context(tip,data)
            assert(db.count==2 and db.records["observed-pet-action:11859:19482"])
            petGUID="Pet-0-999-888-777-11859-9876543210"
            S.Context(tip,data)
            assert(db.count==2)
            local secret="Creature-0-0-0-0-39-9999"
            function issecretvalue(value) return value==secret end
            petGUID=secret
            S.Context(tip,data)
            petGUID="Player-0-0-0-0-40-9999"
            S.Context(tip,data)
            petGUID="Creature-0-0-0-0-not-an-id-9999"
            S.Context(tip,data)
            assert(db.count==2)
            local before=guidCalls
            inCombat=true
            S.Context(tip,data)
            assert(guidCalls==before and db.count==2)
        ''')

    def test_tonk_actions_use_only_the_matching_current_pet_action(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            local title="Activate MG Turret"
            local mana="10 mana per second."
            local shot="Automatically fires a shot at the nearest enemy tonk within 10 yards every 1 sec, dealing 2 to 4 damage per shot."
            local shown={title,"Instant",mana,shot}
            local actionID,isToken=25026,false
            Enum.TooltipDataType.PetAction=11
            Enum.TooltipDataLineType={SpellDescription=2}
            data={type=11,id=900,lines={{leftText=title,lineIndex=1},{leftText="Instant",lineIndex=2},
                {leftText=mana,lineIndex=3,type=2},{leftText=shot,lineIndex=4,type=2}}}
            info={getterName="GetPetAction",getterArgs={3},tooltipData=data}
            function GetPetActionInfo(slot)
                assert(slot==3)
                return title,123,isToken,false,false,false,actionID
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup()
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            local heading,body=lookup()
            assert(heading=="เปิดป้อมปืนกล" and body:find("10 หลา",1,true) and body:find("1 วินาที",1,true)
                and body:find("2 ถึง 4 หน่วยต่อนัด",1,true))
            shown[4]=shot.." Extra effect."
            assert(not lookup())
            data.lines[4].leftText=shown[4]
            S.settings.descriptions=false
            assert(not lookup())
            shown[4]=shot
            data.lines[4].leftText=shot
            local headingOnly,empty=lookup()
            assert(headingOnly and empty=="")
            shown[5]="Extra native effect."
            assert(not lookup())
            shown[5]=nil
            primary={}
            assert(not lookup())
            primary=nil
            isToken=true
            assert(not lookup())
            isToken=false
            actionID=25027
            assert(not lookup())
            actionID=25026
            data.type,data.id,info.getterName=1,25026,"GetSpellByID"
            assert(not lookup())
            assert(S.records["aura:24492"] and S.records["spell:24494"] and not S.records["aura:24494"])

            title,actionID="Flamethrower",25027
            data.type,data.id,info.getterName=11,900,"GetPetAction"
            shown[1],data.lines[1].leftText=title,title
            S.settings.descriptions=true
            local function flame(damage,interval,radius,speed,burn,duration)
                shown[4]=("Deals %s damage every %s sec to all tonks in front of you within %s yards. " ..
                    "Also slows movement to %s%% and deals %s damage per second for %s."):format(
                        damage,interval,radius,speed,burn,duration)
                data.lines[4].leftText=shown[4]
                return lookup()
            end
            local flameName,flameBody=flame("18 to 22","1","8","20","5","2 sec")
            assert(flameName=="เครื่องพ่นไฟ"
                and flameBody:find("18 ถึง 22",1,true) and flameBody:find("1 วินาที",1,true)
                and flameBody:find("8 หลา",1,true) and flameBody:find("5 หน่วยต่อวินาทีเป็นเวลา 2 วินาที",1,true)
                and flameBody:find("ดูผลต่อความเร็วเคลื่อนที่จากคำอธิบายเดิม",1,true)
                and not flameBody:find("20%%"))
            local _,otherSpeed=flame("18 to 22","1","8","80","5","2 seconds")
            assert(flameBody==otherSpeed)
            assert(flame("20","1","8","20","5","2 sec"))
            assert(flame("18-22","1","8","20","5","2 sec"))
            for _,damage in ipairs({"-18 to 22","0 to 22","22 to 18","0"}) do
                assert(not flame(damage,"1","8","20","5","2 sec"))
            end
            assert(not flame("20","2","8","20","5","2 sec"))
            assert(not flame("20","1","0","20","5","2 sec"))
            assert(not flame("20","1","8","30","5","2 sec"))
            assert(not flame("20","1","8","20","-5","2 sec"))
            assert(not flame("20","1","8","20","5","until cancelled"))
            assert(not flame("20","1","8","20","5","3 sec"))
            assert(flame("20","1","8","20","5","2 sec"))
            shown[3],data.lines[3].leftText="9 mana per second.","9 mana per second."
            assert(not lookup())
            shown[3],data.lines[3].leftText=mana,mana
            data.type,data.id,info.getterName=1,25027,"GetSpellByID"
            assert(not lookup())
        ''')

    def test_direct_equip_aura_matches_the_actual_child_and_complete_body(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id=1315971
            local body="In a Forest or Grassland area, Spell Piercing increased by an additional 4."
            local shown={"Rune of Perfection",body,"12 seconds remaining"}
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="player" and instance==23)
                return {spellId=id}
            end}
            data={type=7,id=23,lines={{leftText=shown[1]},{leftText=body}}}
            info={getterName="GetUnitBuffByAuraInstanceID",getterArgs={"player",23},tooltipData=data}
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup()
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            local title,text=lookup()
            assert(title=="รูนแห่งความสมบูรณ์แบบ" and text:find("ค่าเจาะเวทเพิ่มขึ้นอีก 4 หน่วย",1,true))
            shown[2]=body:gsub("additional 4","additional -4");assert(not lookup())
            shown[2]=body
            shown[3]="Another effect.";assert(not lookup())
            shown[3]=nil
            id=1315969;assert(not lookup())
            id=1316054;assert(not lookup())
            id=1315971
            primary={};assert(not lookup())
        ''')

    def test_pet_speed_aura_requires_current_pet_identity_and_unsigned_body(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local aura,shown
            C_UnitAuras={
                GetAuraDataByAuraInstanceID=function(unit,instance,...)
                    assert(instance==23 and select("#",...)==0)
                    return aura
                end,
                GetBuffDataByIndex=function(unit,index,filter)
                    assert(unit=="pet" and index==1 and filter=="HELPFUL")
                    return aura
                end,
            }
            local function card(id,title,body)
                aura={spellId=id,name=title,auraInstanceID=23}
                shown={title,body}
                data={type=7,id=23,lines={{leftText=title},{leftText=body}}}
                info={getterName="GetUnitBuffByAuraInstanceID",getterArgs={"pet",23,"HELPFUL"},tooltipData=data}
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup()
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            card(1263099,"Faster Attack I","Attack speed increased by 17%.")
            local title,text=lookup()
            assert(title=="โจมตีเร็วขึ้น I" and text:find("ความเร็วในการโจมตีเพิ่มขึ้น 17%",1,true))
            info.getterName,info.getterArgs="GetUnitBuff",{"pet",1,"HELPFUL"}
            assert(lookup())
            for _,amount in ipairs({"-20","+20","0","20 to 26"}) do
                card(1263113,"Slower Attack II","Attack speed decreased by "..amount.."%.")
                assert(not lookup())
            end
            card(1263113,"Slower Attack II","Attack speed decreased by 20%.")
            local title,text=lookup()
            assert(title=="โจมตีช้าลง II" and text:find("ความเร็วในการโจมตีลดลง 20%",1,true))
            info.getterArgs[1]="target";assert(not lookup())
            info.getterArgs[1]="pet"
            aura.auraInstanceID=24;assert(not lookup())
            aura.auraInstanceID=23
            aura.name="Another aura";assert(not lookup())
            aura.name=shown[1]
            shown[3]="Additional effect.";assert(not lookup())
            shown[3]="7 seconds remaining";assert(lookup())
            primary={};assert(not lookup())
            assert(S.records["pet-spellbook:1263113"] and not S.records["spell:1263113"])
            assert(S.records["spell:20582"] and not S.records["spell:21009"])
        ''')

    def test_periodic_debuff_uses_the_actual_child_spell_and_complete_visible_values(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="target" and instance==23)
                return {spellId=id}
            end}
            local function card(spellID,name,body,extra)
                id=spellID
                shown={name,body,extra}
                data={type=7,id=23,lines={{leftText=name},{leftText=body}}}
                info={getterName="GetUnitDebuffByAuraInstanceID",getterArgs={"target",23},tooltipData=data}
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup()
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            local blade="Loose Clearcutter Blade"
            card(1310167,blade,"Bleeding for 14 damage every 2.5 sec.","12 seconds remaining")
            local name,body=lookup()
            assert(name=="ใบเลื่อยเคลียร์คัตเตอร์หลุด" and body:find("14 ทุก 2.5 วินาที",1,true))
            id=1310168;assert(not lookup())
            id=1310167
            shown[2]="Bleeding for 14 damage every 0 sec.";assert(not lookup())
            shown[2]="Bleeding for -14 damage every 2.5 sec.";assert(not lookup())
            assert(S.records["item-effect:281059:236729"] and not S.records["aura:1310168"])

            local fire="Deals 5 damage every 1 sec."
            card(25029,"Flamethrower",fire,"Movement speed slowed by 20%.")
            local name,body=lookup()
            assert(name=="เครื่องพ่นไฟ" and body:find("5 หน่วยทุก 1 วินาที",1,true)
                and body:find("ความเร็วเคลื่อนที่ลดลง 20%",1,true))
            shown[3]="Movement speed slowed to 20%.";assert(not lookup())
            shown[3]="Movement speed slowed by -20%.";assert(not lookup())
            shown[3]=nil
            S.settings.descriptions=false;assert(not lookup())
            shown[3]="Movement speed slowed by 20%."
            local titleOnly,empty=lookup()
            assert(titleOnly=="เครื่องพ่นไฟ" and empty=="")
            primary={};assert(not lookup())
            assert(not S.records["spell:25027"] and S.records["pet-action:25027"])
        ''')

    def test_great_stamina_requires_the_current_pet_rank_and_exact_stamina_body(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataLineType={None=0,Blank=1,SpellName=13,SpellPassive=33,SpellDescription=34}
            SPELL_PASSIVE="Passive"
            local name="Great Stamina"
            local function card(spellID,rank,amount)
                local body="Stamina increased by "..amount.."."
                entry={spellID=spellID,itemType=1,isPassive=true,name=name,subName=rank}
                data={type=1,id=spellID,lines={{type=13,lineIndex=1,leftText=name,rightText=rank},
                    {type=33,lineIndex=2,leftText=SPELL_PASSIVE},{type=34,lineIndex=3,leftText=body}}}
                info={getterName="GetSpellBookItem",getterArgs={7,1},tooltipData=data}
            end
            function C_SpellBook.GetSpellBookItemInfo(slot,bank)
                assert(slot==7 and bank==1)
                return entry
            end
            local function region(text)
                if text then return {GetText=function() return text end,IsShown=function() return true end} end
            end
            function tip:GetLeftLine(index) return region(data.lines[index] and data.lines[index].leftText) end
            function tip:GetRightLine(index) return region(data.lines[index] and data.lines[index].rightText) end
            function tip:NumLines() return #data.lines end
            local function lookup()
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            for _,rank in ipairs({{5041,"Rank 9",32},{5042,"Rank 10",40}}) do
                card(rank[1],rank[2],rank[3])
                local title,description=lookup()
                assert(title=="ความอึดอันยิ่งใหญ่" and description=="เพิ่ม Stamina "..rank[3].." หน่วย")
                assert(not S.records["spell:"..rank[1]])
            end
            card(5041,"Rank 9",40);assert(not lookup())
            card(5041,"Rank 9","-32");assert(not lookup())
            card(5041,"Rank 9",32)
            entry.subName="Rank 10";assert(not lookup())
            entry.subName="Rank 9"
            data.lines[1].rightText="Rank 10";assert(not lookup())
            data.lines[1].rightText=nil
            data.lines[2].leftText,data.lines[2].type="Rank 9",0
            assert(lookup())
            info.getterArgs[2]=0;assert(not lookup())
            info.getterArgs[2]=1
            primary={};assert(not lookup())
            primary=nil
            data.lines[3].leftText="Health increased by 32."
            assert(not lookup())
            S.settings.descriptions=false
            assert(not lookup())
            data.lines[3].leftText="Stamina increased by 32."
            local title,description=lookup()
            assert(title=="ความอึดอันยิ่งใหญ่" and description=="")
        ''')

    def test_triggered_pet_and_drink_auras_use_the_exact_child_and_complete_body(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(instance==23)
                return {spellId=id}
            end}
            local function card(spellID,name,body,unit)
                id=spellID
                shown={name,body,"5 seconds remaining"}
                data={type=7,id=23,lines={{leftText=name},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={unit or "target",23},tooltipData=data}
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup()
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            card(25999,"Boar Charge","Immobilized.")
            local name,text=lookup()
            assert(name=="หมูป่าพุ่งชน" and text=="ถูกตรึงให้อยู่กับที่")
            id=7371;assert(not lookup())
            card(24259,"Spell Lock","Silenced.")
            local name,text=lookup()
            assert(name=="ผนึกเวท" and text=="ถูกใบ้เวท")
            shown[3]="School of magic locked.";assert(not lookup())
            for _,entry in ipairs({{19479,17},{19652,23},{19653,32},{19654,40}}) do
                card(entry[1],"Tainted Blood Effect","Melee attack power reduced by "..entry[2]..".")
                local name,text=lookup()
                assert(name=="ผลของโลหิตแปดเปื้อน"
                    and text=="พลังโจมตีระยะประชิดลดลง "..entry[2].." หน่วย")
                shown[2]="Melee attack power reduced by -"..entry[2]..".";assert(not lookup())
            end
            card(29040,"Fizzy Energy Drink","Mana Regeneration increased by 9 every 5 seconds.","player")
            local name,text=lookup()
            assert(name=="เครื่องดื่มชูกำลังรสซ่า" and text=="ฟื้นฟูมานาเพิ่มขึ้น 9 หน่วยทุก 5 วินาที")
            shown[2]="Mana Regeneration increased by 9 every 6 seconds."
            S.settings.descriptions=false;assert(not lookup())
            assert(S.records["aura:29038"] and S.records["aura:29039"] and not S.records["aura:29029"]
                and S.records["item-effect:23176:103753"])
        ''')

    def test_directional_pet_debuffs_reject_signed_or_non_scalar_display_values(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="target" and instance==23)
                return {spellId=id}
            end}
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup(spellID,title,body,extra)
                id=spellID
                shown={title,body,extra or "5 seconds remaining"}
                data={type=7,id=23,lines={{leftText=title},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"target",23},tooltipData=data}
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            for _,entry in ipairs({
                {{24423,24577,24578,24579},"Demoralizing Screech","Melee attack power reduced by 41.",
                    "พลังโจมตีระยะประชิดลดลง 41 หน่วย"},
                {{1264478,1264479,1264480,1264481,1264482},"Sonic Blast","Increases casting time by 41%.",
                    "เวลาร่ายเวทเพิ่มขึ้น 41%"},
                {{1264735,1264736,1264739,1264741,1264742},"Pinch","Movement slowed by 41%.",
                    "ความเร็วเคลื่อนที่ลดลง 41%"},
                {{1264758,1264927,1264929,1264930,1264933},"Dismember","Healing effects reduced by 41%.",
                    "ผลของการรักษาลดลง 41%"},
                {{1265038,1265039,1265040,1265041,1265042},"Tendon Rip",
                    "Movement slowed by 41%. 9 Bleed damage every 2.5 sec.",
                    "ความเร็วเคลื่อนที่ลดลง 41% ได้รับความเสียหายจากเลือดไหล 9 หน่วยทุก 2.5 วินาที"},
                {{1265899,1265901,1265902,1265903,1265904},"Dust Cloud","Decreases armor by 41.",
                    "เกราะลดลง 41 หน่วย"},
            }) do
                for _,spellID in ipairs(entry[1]) do
                    local title,body=lookup(spellID,entry[2],entry[3])
                    assert(title and body==entry[4])
                    for _,bad in ipairs({"-41","+41","0","40 to 41"}) do
                        assert(not lookup(spellID,entry[2],(entry[3]:gsub("41",bad))))
                    end
                    assert(not lookup(spellID,entry[2],entry[3],"Other effect."))
                end
            end
            assert(not lookup(1265038,"Tendon Rip","Movement slowed by 41%. -9 Bleed damage every 2.5 sec."))
            assert(not lookup(1265038,"Tendon Rip","Movement slowed by 41%. 9 Bleed damage every 0 sec."))
            assert(not lookup(1264735,"Tendon Rip","Movement slowed by 41%."))
            S.settings.descriptions=false
            assert(lookup(1264758,"Dismember","Healing effects reduced by 41%.")=="ฉีกแขนขา")
            assert(not lookup(1264758,"Dismember","Healing effects reduced by -41%."))
        ''')

    def test_combat_reader_only_shows_public_native_player_and_group_aura_instances(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            fontOK=false
            GameTooltip=tip
            Enum.AddOnRestrictionType={Combat=0,Encounter=1,ChallengeMode=2,PvPMatch=3,Map=4,Chat=5}
            Enum.AddOnRestrictionState={Inactive=0,Activating=1,Active=2}
            local restrictionState=2
            C_RestrictedActions={GetAddOnRestrictionState=function(kind)
                return kind==1 and restrictionState or 0
            end}
            local reader
            for _,f in ipairs(frames) do if f.name=="AlphaWoWCombatReader" then reader=f end end
            assert(reader and reader.parent==UIParent)
            function reader:GetWidth() return self.width end
            function UIParent:GetWidth() return 1920 end
            function UIParent:GetEffectiveScale() return 1 end
            function tip:GetEffectiveScale() return 1 end
            local badRect, forbiddenTooltip=false,false
            function tip:IsForbidden() return forbiddenTooltip end
            function tip:GetRect() return badRect and 2001 or 1000,400,200,80 end
            local nativeHook=tip.HookScript
            function tip:HookScript(...) assert(not combat);return nativeHook(self,...) end
            tip.SetPoint=forbidden;tip.ClearLines=forbidden;tip.AddLine=forbidden
            S.RememberLongText=forbidden;S.Capture=forbidden;S.captureEnabled=true
            local name,description="Arcane Resistance","Increases arcane resistance by 41."
            local shown={name,description}
            data={type=7,lines={{leftText=name},{leftText=description}}}
            info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"player",23},tooltipData=data}
            function tip:NumLines() return #shown end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return shown[i] end}
            end
            function tip:GetRightLine() end
            local aura={spellId=28770,auraInstanceID=23,name=name}
            local queries,restricted,expectedUnit=0,false,"player"
            C_Secrets={ShouldUnitAuraInstanceBeSecret=function(unit,id)
                assert(unit==expectedUnit and id==23);return restricted
            end}
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,id)
                assert(unit==expectedUnit and id==23);queries=queries+1;return aura
            end}
            local function rejected()
                assert(S.OnTooltip(tip,data)=="combat" and not reader:IsShown())
            end
            combat=true;S.RegisterCombatTooltips();rejected();assert(queries==0)
            combat=false;S.RegisterCombatTooltips();S.RegisterCombatTooltips();combat=true
            assert(#tip.hooks.OnShow==1)
            assert(S.OnTooltip(tip,data)=="shown" and reader:IsShown() and not S.reader:IsShown())
            assert(reader.point[2]==UIParent and reader.point[3]=="BOTTOMLEFT")
            assert(queries==1 and shown[2]==description)
            event("ADDON_RESTRICTION_STATE_CHANGED");assert(not reader:IsShown())
            restrictionState=1;rejected();assert(queries==1);restrictionState=2
            restricted=true;rejected();assert(queries==1);restricted=false
            info.getterArgs[1]="target";rejected();assert(queries==1);info.getterArgs[1]="player"
            info.append=true;rejected();info.append=nil
            info.getterName="GetUnitAura";rejected();info.getterName="GetUnitAuraByAuraInstanceID"
            primary={};rejected();primary=nil
            forbiddenTooltip=true;rejected();forbiddenTooltip=false
            assert(queries==1)
            aura.auraInstanceID=24;rejected();aura.auraInstanceID=23
            secret[aura]=true;rejected();secret[aura]=nil
            secret[description]=true;rejected();secret[description]=nil
            badRect=true;secret[2001]=true;rejected();badRect=false;secret[2001]=nil
            S.settings.descriptions=false
            shown[2]="Increases arcane resistance by -41.";rejected();shown[2]=description
            tip:Hide();rejected();tip:Show();assert(reader:IsShown())
            event("UNIT_AURA","player");assert(not reader:IsShown())
            assert(S.OnTooltip(tip,data)=="shown")
            tip:Fire("OnTooltipCleared");assert(not reader:IsShown() and S.stats.errors==0)

            PartyAuraFrameMixin={UpdateTooltip=forbidden}
            CompactBuffMixin={UpdateTooltip=function() forbidden() end}
            CompactDebuffMixin={UpdateTooltip=function() forbidden() end}
            local parent={displayedUnit="raid40",unit="raid39",IsForbidden=function() return false end}
            local button={unit="party4",auraInstanceID=23,UpdateTooltip=PartyAuraFrameMixin.UpdateTooltip,
                IsForbidden=function() return false end,GetParent=function() return parent end}
            function tip:GetOwner() return button end
            info.getterName="GetUnitBuffByAuraInstanceID"
            expectedUnit="party4";info.getterArgs[1]=expectedUnit
            assert(S.OnTooltip(tip,data)=="shown")
            local before=queries
            button.auraInstanceID=24;rejected();button.auraInstanceID=23
            button.unit="party3";rejected();button.unit="party4"
            button.UpdateTooltip=function() end;rejected()
            assert(queries==before)
            expectedUnit="raid40";info.getterArgs[1]=expectedUnit
            info.getterName="GetUnitDebuffByAuraInstanceID"
            button.UpdateTooltip=CompactDebuffMixin.UpdateTooltip
            assert(S.OnTooltip(tip,data)=="shown")
            parent.displayedUnit="raidpet40";rejected();parent.displayedUnit="raid40"
            info.getterArgs[1]="raid41";rejected();info.getterArgs[1]="raid040";rejected()
            info.getterArgs[1]=expectedUnit
            secret[button]=true;rejected();secret[button]=nil
            secret[parent]=true;rejected();secret[parent]=nil
            C_Secrets.CanCompareUnitTokens=function() return true end
            function UnitIsUnit(left,right) return left=="party4" and right=="raid40" end
            assert(S.OnTooltip(tip,data)=="shown")
            event("UNIT_AURA","raid3");assert(reader:IsShown())
            event("UNIT_AURA","party4");assert(not reader:IsShown())
            assert(S.OnTooltip(tip,data)=="shown")
            local unknown=trap();secret[unknown]=true
            event("UNIT_AURA",unknown);assert(not reader:IsShown())
            assert(S.OnTooltip(tip,data)=="shown")
            event("UNIT_ENTERED_VEHICLE","raid40");assert(not reader:IsShown())
            event("GROUP_ROSTER_UPDATE")

            local draws=0
            for _,f in ipairs(frames) do
                if f.parent==reader and f.Draw then
                    local draw=f.Draw
                    f.Draw=function(self,...) draws=draws+1;return draw(self,...) end
                end
            end
            assert(S.OnTooltip(tip,data)=="shown" and draws==2)
            before=queries
            assert(S.OnTooltip(tip,data)=="shown" and queries==before+1 and draws==2)
            event("GROUP_ROSTER_UPDATE");assert(not reader:IsShown())

            for _,sample in ipairs({
                {139,"Renew","Healing 12 damage every 3 seconds.","ฟื้นฟูพลังชีวิต 12 หน่วยทุก 3 วินาที"},
                {17,"Power Word: Shield","Absorbs 93 damage.","ดูดซับความเสียหาย 93 หน่วย"},
                {19740,"Blessing of Might","Increases melee attack power by 14.","เพิ่มพลังโจมตีระยะประชิด 14"},
            }) do
                local id,title,english,thai=unpack(sample)
                local row=S.records["aura:"..id]
                assert(row.reviewStatus=="VERIFIED" and not row.requireCompleteAuraBody)
                aura.spellId=id;aura.name=title
                shown={title,english,"16 seconds remaining"}
                data.lines={{leftText=title},{leftText=english},{leftText=shown[3]}}
                S.settings.descriptions=true
                assert(S.OnTooltip(tip,data)=="shown")
                local heading,body=S.PublicCombatTooltip(tip,data)
                assert(heading==row.translatedName and body==thai)
                shown[3]="Additional unreviewed effect.";rejected();shown[3]="16 seconds remaining"
                S.settings.descriptions=false
                shown[2]="An unrelated mechanic.";rejected();shown[2]=english
                row.reviewStatus="BLOCKED_SOURCE";rejected();row.reviewStatus="VERIFIED"
                row.requireAuraCasterLine=true;rejected();row.requireAuraCasterLine=nil
                row.lines[2]=row.lines[1];rejected();row.lines[2]=nil
                assert(S.OnTooltip(tip,data)=="shown")
            end
        ''')

    def test_combat_pet_actions_require_public_native_slot_and_complete_body(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            GameTooltip=tip
            Enum.TooltipDataType.PetAction=11
            Enum.TooltipDataLineType={SpellDescription=34}
            Enum.AddOnRestrictionType={Combat=0,Encounter=1,ChallengeMode=2,PvPMatch=3,Map=4,Chat=5}
            Enum.AddOnRestrictionState={Inactive=0,Activating=1,Active=2}
            local state=2
            C_RestrictedActions={GetAddOnRestrictionState=function() return state end}
            local reader
            for _,f in ipairs(frames) do if f.name=="AlphaWoWCombatReader" then reader=f end end
            function reader:GetWidth() return self.width end
            function UIParent:GetWidth() return 1920 end
            function UIParent:GetEffectiveScale() return 1 end
            function tip:GetEffectiveScale() return 1 end
            function tip:GetRect() return 1100,400,200,120 end
            function tip:IsForbidden() return false end
            tip.SetPoint=forbidden;tip.ClearLines=forbidden;tip.AddLine=forbidden
            S.captureEnabled=true;S.CapturePetAction=forbidden
            local buttonSlot=3
            local button={GetID=function() return buttonSlot end,IsForbidden=function() return false end}
            local owner=button
            function tip:GetOwner() return owner end
            PetActionBar={actionButtons={[3]=button},IsForbidden=function() return false end}
            local id,name,token,reads=17253,"Bite",false,0
            function GetPetActionInfo(slot)
                assert(slot==3);reads=reads+1;return name,nil,token,nil,nil,nil,id
            end
            local english="Bite the enemy, causing 19 damage."
            data={type=11,id=999,lines={{leftText="Bite"},
                {type=34,lineIndex=2,leftText=english}}}
            info={getterName="GetPetAction",getterArgs={3},tooltipData=data}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            local function shown()
                assert(S.OnTooltip(tip,data)=="shown" and reader:IsShown())
                local title,body,unit=S.PublicCombatTooltip(tip,data)
                assert(title=="กัด" and body=="กัดศัตรู สร้างความเสียหาย 19 หน่วย" and unit=="pet")
            end
            local function rejected() assert(S.OnTooltip(tip,data)=="combat" and not reader:IsShown()) end
            S.RegisterCombatTooltips();combat=true
            shown()
            event("UNIT_PET","party1");assert(reader:IsShown())
            event("UNIT_PET","player");assert(not reader:IsShown())
            for _,name in ipairs({"PET_BAR_UPDATE","PET_UI_UPDATE","PLAYER_TARGET_CHANGED"}) do
                shown();event(name);assert(not reader:IsShown())
            end
            local before=reads
            state=1;rejected();state=2
            buttonSlot=4;rejected();buttonSlot=3
            owner={GetID=button.GetID,IsForbidden=button.IsForbidden};rejected();owner=button
            primary={};rejected();primary=nil
            assert(reads==before)
            token=true;rejected();token=false
            name="Claw";rejected();name="Bite"
            secret[id]=true;rejected();secret[id]=nil
            data.lines[2].leftText=english.." Stuns the target.";rejected()
            data.lines[2].leftText=english;secret[english]=true;rejected();secret[english]=nil
            shown()
        ''')

    def test_combat_reader_translates_only_exact_native_action_cards(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua', 'Skills/ItemEffects.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            GameTooltip=tip
            Enum.TooltipDataLineType={SpellDescription=34}
            Enum.AddOnRestrictionType={Combat=0,Encounter=1,ChallengeMode=2,PvPMatch=3,Map=4,Chat=5}
            Enum.AddOnRestrictionState={Inactive=0,Activating=1,Active=2}
            local state=2
            C_RestrictedActions={GetAddOnRestrictionState=function() return state end}
            local reader
            for _,f in ipairs(frames) do if f.name=="AlphaWoWCombatReader" then reader=f end end
            function reader:GetWidth() return self.width end
            function UIParent:GetWidth() return 1920 end
            function UIParent:GetEffectiveScale() return 1 end
            function tip:GetEffectiveScale() return 1 end
            function tip:GetRect() return 1100,400,200,120 end
            function tip:IsForbidden() return false end
            tip.SetPoint=forbidden;tip.ClearLines=forbidden;tip.AddLine=forbidden
            S.RememberLongText=forbidden;S.Capture=forbidden;S.captureEnabled=true
            ActionBarActionButtonMixin={SetTooltip=forbidden}
            local button={action=6,IsForbidden=function() return false end,SetTooltip=forbidden}
            function tip:GetOwner() return button end
            local bodySeen
            for _,f in ipairs(frames) do
                if f.parent==reader and f.Draw then
                    local draw=f.Draw
                    f.Draw=function(self,text,...) bodySeen=text;return draw(self,text,...) end
                end
            end
            local function card(id,name,...)
                data={type=1,id=id,lines={{leftText=name}}}
                for _,text in ipairs({...}) do
                    table.insert(data.lines,{type=34,lineIndex=#data.lines+1,leftText=text})
                end
                info={getterName="GetAction",getterArgs={6},tooltipData=data}
            end
            local kind, actionID, reads="spell",nil,0
            function GetActionInfo(slot) assert(slot==6);reads=reads+1;return kind,actionID or data.id end
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            local function rejected() assert(S.OnTooltip(tip,data)=="combat" and not reader:IsShown()) end
            local blessing="Places a Blessing on the friendly target, increasing melee attack power by 14 for 1 hour.  "..
                "Players may only have one Blessing on them per Paladin at any one time."
            card(19740,"Blessing of Might",blessing)
            S.RegisterCombatTooltips();combat=true
            assert(S.OnTooltip(tip,data)=="shown" and reader.point[2]==UIParent)
            assert(bodySeen:find("14 หน่วยเป็นเวลา 1 ชั่วโมง",1,true))
            event("ACTIONBAR_SLOT_CHANGED",7);assert(reader:IsShown())
            event("ACTIONBAR_SLOT_CHANGED",0);assert(not reader:IsShown())
            assert(S.OnTooltip(tip,data)=="shown")
            event("UPDATE_SHAPESHIFT_FORM");assert(not reader:IsShown())
            assert(S.OnTooltip(tip,data)=="shown")
            event("UNIT_AURA","player");assert(not reader:IsShown())
            local before=reads
            state=1;rejected();state=2;assert(reads==before)
            button.action=7;rejected();button.action=6
            button.SetTooltip=function() end;rejected();button.SetTooltip=forbidden
            primary={};rejected();primary=nil
            kind="macro";rejected();kind="spell"
            actionID=19741;rejected();actionID=nil
            secret[19740]=true;rejected();secret[19740]=nil
            info.append=true;rejected();info.append=nil
            secret[blessing]=true;rejected();secret[blessing]=nil

            Enum.TooltipDataType.Item=0
            Enum.TooltipDataLineType.ItemName=22
            Enum.TooltipDataLineType.ItemSpellTriggerOnUse=44
            Enum.TooltipDataLineType.ItemSpellTriggerOnEquip=45
            Enum.TooltipDataLineType.NestedBlock=19
            ITEM_SPELL_TRIGGER_ONUSE="Use:"
            local use="Use: Restores 1,234.5 health."
            local useLine={type=44,lineIndex=2,leftText=use}
            kind="item"
            data={type=0,id=929,lines={{type=22,lineIndex=1,leftText="Healing Potion"},useLine}}
            info={getterName="GetAction",getterArgs={6},tooltipData=data}
            assert(S.OnTooltip(tip,data)=="shown" and bodySeen:find("ฟื้นฟูพลังชีวิต 1,234.5",1,true))
            assert(reader.point[2]==UIParent and tip:GetLeftLine(2):GetText()==use)
            event("ACTIONBAR_SLOT_CHANGED",7);assert(reader:IsShown())
            event("ACTIONBAR_SLOT_CHANGED",6);assert(not reader:IsShown())
            info.getterName="GetBagItem";rejected();info.getterName="GetAction"
            button.action=7;rejected();button.action=6
            kind="macro";rejected();kind="item"
            actionID=858;rejected();actionID=nil
            secret[use]=true;rejected();secret[use]=nil
            useLine.type=45;rejected();useLine.type=44
            useLine.leftText="Use: Unreviewed effect.";rejected();useLine.leftText=use
            data.lines[3]={type=44,lineIndex=3,leftText=use};rejected()
            data.lines[3]={type=19,lineIndex=3,leftText="Nested"};rejected()
            data.lines[3]=nil
            assert(S.OnTooltip(tip,data)=="shown")
            kind="spell"

            local seal="Fills the Paladin with holy spirit for 30 sec, granting each melee attack an additional "..
                "3 to 10 Holy damage.  Slower weapons cause more Holy damage per swing.  "..
                "Only one Seal can be active on the Paladin at any one time."
            local judgement="Unleashing this Seal's energy will cause 28 to 31 Holy damage to an enemy."
            card(20287,"Seal of Righteousness",seal,judgement)
            assert(S.OnTooltip(tip,data)=="shown" and bodySeen:find("28 ถึง 31 หน่วย",1,true))
            S.settings.descriptions=false
            data.lines[3]=nil;rejected()
            card(20287,"Seal of Righteousness",seal,judgement)
            assert(S.OnTooltip(tip,data)=="shown" and bodySeen=="")

            S.settings.descriptions=true
            local penance="Launches a volley of holy light at the target, causing 53 Holy damage to an enemy, "..
                "or 155 healing to an ally, instantly and every 1 sec for 2 sec."
            card(402174,"Penance",penance)
            assert(S.OnTooltip(tip,data)=="shown" and bodySeen:find("155 หน่วย",1,true))
            card(402174,"Penance",penance,"Unreviewed effect.");rejected()

            local nova="Causes an explosion of holy light around the caster, causing 49 to 57 Holy damage "..
                "to all enemy targets within 11 yards and healing all party members within 12 yards "..
                "for 81 to 93. These effects cause no threat."
            local proc="Each time Holy Fire deals damage, you have a 5% chance for your next Holy Nova to cost no Mana."
            card(15430,"Holy Nova",nova,proc)
            assert(S.OnTooltip(tip,data)=="shown" and bodySeen:find("49 ถึง 57",1,true)
                and bodySeen:find("ดูเงื่อนไขเพิ่มเติมในคำอธิบายเดิม",1,true)
                and not bodySeen:find("5%",1,true))
            S.settings.descriptions=false
            card(15430,"Holy Nova",nova);rejected()
            card(15430,"Holy Nova",nova,(proc:gsub("5%%","6%%")));rejected()
            S.settings.descriptions=true

            local liveID, ordinaryReads=2457,reads
            local stance={spellID=71,IsForbidden=function() return false end,GetID=function() return 2 end}
            StanceBar={IsForbidden=function() return false end,actionButtons={[2]=stance}}
            function GetNumShapeshiftForms() return 2 end
            function GetShapeshiftFormInfo(slot) assert(slot==2);return 123,true,true,liveID end
            button=stance
            card(nil,"Battle Stance","A balanced combat stance.")
            data.type=nil;info.getterName="GetShapeshift";info.getterArgs={2}
            assert(S.OnTooltip(tip,data)=="shown" and bodySeen=="ท่าต่อสู้ที่สมดุล" and reads==ordinaryReads)
            event("UPDATE_SHAPESHIFT_FORMS");assert(not reader:IsShown())
            data.id=71;rejected();data.id=nil
            secret[2457]=true;rejected();secret[2457]=nil
            button={IsForbidden=function() return false end,GetID=function() return 2 end};rejected();button=stance
            assert(S.OnTooltip(tip,data)=="shown")
            tip:Fire("OnTooltipCleared");assert(not reader:IsShown() and S.stats.errors==0)
        ''')

    def test_complete_aura_matching_separates_verified_native_metadata_from_the_body(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            Enum.TooltipDataLineType={AuraCaster=51}
            AURA_CAST_BY="Cast by %s"
            local title,body="Arcane Resistance","Increases arcane resistance by 41."
            local caster,timer="Cast by Example","5 seconds remaining"
            local aura={spellId=28770,auraInstanceID=23,name=title,dispelName="Magic"}
            local shown,right,header,footer
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="target" and instance==23)
                return aura
            end}
            local function region(value)
                if value then return {GetText=function() return value end,IsShown=function() return true end} end
            end
            function tip:GetLeftLine(i) return region(shown[i]) end
            function tip:GetRightLine(i) return region(right[i]) end
            function tip:NumLines() return #shown end
            local function card(label,first,last,casterIndex)
                shown,right={title,body,first,last},{[1]=label}
                header={lineIndex=1,leftText=title,rightText=label}
                data={type=7,id=23,lines={header,{lineIndex=2,leftText=body}}}
                if casterIndex then
                    footer={lineIndex=casterIndex,leftText=caster,type=51}
                    table.insert(data.lines,footer)
                end
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"target",23},tooltipData=data}
            end
            local function lookup()
                local context=S.Context(tip,data)
                if context then return S.Lookup(context.key,context.name,context.lines) end
            end
            local function translated()
                local context=S.Context(tip,data)
                assert(context and #context.lines==1 and context.lines[1]==body)
                local name,text=lookup()
                assert(name=="ต้านทานอาร์เคน" and text=="เพิ่มความต้านทานอาร์เคน 41 หน่วย")
            end
            card();translated()
            card("Magic",caster,timer,3);translated()
            card("Magic",timer,caster,4);translated()
            card("Curse",caster,nil,3);assert(not lookup())
            card("Magic",caster,nil,3)
            header.rightText=nil;assert(not lookup())
            header.rightText="Magic";header.lineIndex=2;assert(not lookup())
            header.lineIndex=1;aura.name="Different Aura";assert(not lookup());aura.name=title
            footer.leftText="Cast by Other";assert(not lookup())
            footer.leftText=caster;footer.rightText="Other";assert(not lookup())
            footer.rightText=nil;right[3]="Other";assert(not lookup())
            right[3]=nil;primary={};assert(not lookup());primary=nil
            table.insert(data.lines,{lineIndex=3,leftText=caster,type=51});assert(not lookup())
            card("Magic",caster);assert(not lookup())
            card("Magic",caster,"Other effect.",3);assert(not lookup())
            card("Magic",timer,timer);assert(not lookup())
            for _,invalid in ipairs({"Cast by %s","Cast by Example\\nOther effect.","Cast by |cffffffffName"}) do
                card("Magic",invalid,nil,3)
                footer.leftText=invalid
                assert(not lookup())
            end
            card("Magic",caster,nil,3);translated()
            S.settings.descriptions=false
            assert(lookup()=="ต้านทานอาร์เคน")
            shown[2]="Increases arcane resistance by -41.";assert(not lookup())
        ''')

    def test_camping_auras_keep_same_named_records_and_visible_duration_separate(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local id,name
            local instance=42
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,current)
                assert(unit=="player" and current==instance)
                return {spellId=id,name=name,auraInstanceID=instance}
            end}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function card(sid,title,body)
                id,name=sid,title
                data={type=7,lines={{leftText=title},{leftText=body},{leftText="16 seconds remaining"}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"player",instance},tooltipData=data}
            end
            local function outcome() return S.OnTooltip(tip,data) end
            card(1229739,"Welcoming Campfire","Grants various camp benefits after 1 min spent sitting near " ..
                "the campfire, based on what additional camp objects are placed near the campfire.")
            assert(outcome()=="shown" and titleSeen=="กองไฟต้อนรับ")
            assert(bodySeen=="เมื่อนั่งใกล้กองไฟเป็นเวลา 1 นาที จะได้รับประโยชน์ตามอุปกรณ์ค่ายที่วางไว้รอบกองไฟ")
            id=1289723;assert(outcome()=="text-mismatch")
            card(1289723,"Welcoming Campfire","Grants various camp benefits after 45 sec spent sitting near " ..
                "the campfire. You may also craft using tradeskills, as long as you do not move.")
            assert(outcome()=="shown" and bodySeen:find("45 วินาที",1,true) and bodySeen:find("ไม่ขยับตัว",1,true))
            id=1229739;assert(outcome()=="text-mismatch")
            card(1283391,"Campfire Nearby","The pleasant smoke of a campfire drifts in the air from somewhere nearby.")
            assert(outcome()=="shown" and titleSeen=="ใกล้กองไฟ")
            card(1328375,"Violet Flames","The enchanted flame resonates within you. Campfire effects gained " ..
                "while affected have increased duration.")
            assert(outcome()=="shown" and bodySeen:find("ที่ได้รับระหว่างนี้",1,true))
            data.lines[3].leftText="Also increases Spirit.";assert(outcome()=="text-mismatch")
            S.settings.descriptions=false;assert(outcome()=="text-mismatch")
            card(1230587,"Boosted Mana Regeneration","");assert(outcome()=="missing")
        ''')

    def test_camp_benefits_renders_the_complete_visible_aura_with_many_rows(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,id)
                assert(unit=="player" and id==42)
                return {spellId=1229741,name="Camp Benefits",auraInstanceID=42}
            end}
            local lines={"Camp Benefits","Gained the following camp benefits:",
                "Mana Well: Restores 10 Mana every 5 seconds.",
                "Sharpening Wheel: Strength increased by 6.",
                "Enchanted Lute: Armor increased by 28, all attributes increased by 0, and all resistances increased by 0.",
                "First Aid Kit: Stamina increased by 3.",
                "Fish Bowl: All stats increased by 8%.",
                "Incense Candle: Intellect increased by 5.",
                "Lodestone: Melee Attack Power increased by 11.",
                "Camp Chair: Critical strike chance with all spells and attacks increased by 2%.",
                "Faction Banner: Spirit increased by 7.","16 seconds remaining"}
            data={type=7,lines={}}
            for index,text in ipairs(lines) do data.lines[index]={leftText=text} end
            info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"player",42},tooltipData=data}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function outcome() return S.OnTooltip(tip,data) end
            assert(outcome()=="shown" and titleSeen=="ประโยชน์จากค่าย")
            assert(bodySeen:find("บ่อมานา: ฟื้นฟูมานา 10 หน่วยทุก 5 วินาที",1,true))
            assert(bodySeen:find("ลูทลงมนตร์: เพิ่มเกราะ 28 ค่าสถานะทั้งหมด 0 และค่าต้านทานทั้งหมด 0",1,true))
            assert(bodySeen:find("ธงประจำฝ่าย: เพิ่มค่าจิตวิญญาณ 7",1,true))
            assert(not bodySeen:find("seconds remaining",1,true))
            data.lines[3].leftText=lines[3]:gsub("5 seconds","0 seconds");assert(outcome()=="text-mismatch")
            data.lines[3].leftText=lines[3]
            data.lines[5].leftText=lines[5]:gsub("by 0","by -1");assert(outcome()=="text-mismatch")
            data.lines[5].leftText=lines[5]
            local secretText=lines[6];secret[secretText]=true;assert(outcome()=="no-context");secret[secretText]=nil
            S.settings.descriptions=false
            data.lines[7].leftText="Fish Bowl: All stats increased by 8.";assert(outcome()=="text-mismatch")
            data.lines[7].leftText=lines[7]
            assert(outcome()=="shown" and bodySeen=="")
        ''')

    def test_well_fed_aura_uses_its_own_stat_and_only_the_displayed_xp_branch(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local id
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="player" and instance==42)
                return {spellId=id,name="Well Fed",auraInstanceID=42}
            end}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function outcome() return S.OnTooltip(tip,data) end
            local xp="Experience gained from kills increased by 5%."
            local thaiXP="ค่าประสบการณ์ที่ได้รับจากการกำจัดศัตรูเพิ่มขึ้น 5%"
            for _,row in ipairs({
                {1248406,"Stamina","ค่าความทนทาน"},
                {1248420,"Agility","ค่าความคล่องแคล่ว"},
                {1248421,"Intellect","ค่าสติปัญญา"},
                {1248422,"Strength","ค่าพละกำลัง"},
                {1249519,"Attack Power","พลังโจมตี"},
                {1249520,"Spell Damage","ความเสียหายจากเวท"},
                {1249521,"Fishing Skill","ทักษะตกปลา"},
                {1249523,"Critical Strike chance","โอกาสเกิดคริติคอล","%"},
                {1249926,"Spirit","ค่าจิตวิญญาณ"},
                {1249927,"Healing Power","พลังรักษา"},
                {1319310,"Armor","ค่าเกราะ",nil,"0"},
            }) do
                id=row[1]
                local amount=(row[5] or "12.5")..(row[4] or "")
                local english="Your "..row[2].." is increased by "..amount.."."
                local thai=row[3].."เพิ่มขึ้น "..amount
                data={type=7,id=999,lines={{leftText="Well Fed"},{leftText=english}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"player",42},tooltipData=data}
                assert(outcome()=="shown" and titleSeen=="อิ่มท้อง" and bodySeen==thai)
                data.lines[3]={leftText=xp}
                assert(outcome()=="shown" and bodySeen==thai.." "..thaiXP)
                data.lines[3].leftText="All experience gained increased by 5%."
                assert(outcome()=="text-mismatch")
                data.lines[3]=nil
                data.lines[2].leftText="Your "..row[2].." is increased by -"..amount.."."
                assert(outcome()=="text-mismatch")
                if row[4] then
                    data.lines[2].leftText="Your "..row[2].." is increased by 12.5."
                    assert(outcome()=="text-mismatch")
                end
            end
            id=1249907
            data.lines[2].leftText="Your Herbalism skill is increased by 15."
            assert(outcome()=="missing")
        ''')

    def test_indexed_item_auras_preserve_only_their_own_displayed_duration(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local id,name
            C_UnitAuras={GetAuraDataByAuraInstanceID=function()
                return {spellId=id,name=name,auraInstanceID=42}
            end}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            for _,sample in ipairs({
                {430950,"Arcane Protection - Fire","Increases your fire resistance by 14 for 30 min.",
                    "เพิ่มค่าต้านทานไฟ 14 เป็นเวลา 30 นาที"},
                {430951,"Arcane Protection - Frost","Increases your frost resistance by 15 for 30 min.",
                    "เพิ่มค่าต้านทานน้ำแข็ง 15 เป็นเวลา 30 นาที"},
                {459613,"Guided Buoyancy Accelerant","Increases swim speed by 44%.",
                    "เพิ่มความเร็วในการว่ายน้ำ 44%"},
                {4079,"Cloaking","Invisible for 10 sec.","ล่องหนเป็นเวลา 10 วินาที"},
            }) do
                id,name=sample[1],sample[2]
                data={type=7,lines={{leftText=name},{leftText=sample[3]},{leftText="2 seconds remaining"}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"player",42},tooltipData=data}
                assert(S.OnTooltip(tip,data)=="shown" and bodySeen==sample[4])
                data.lines[2].leftText=sample[3].." Another effect."
                assert(S.OnTooltip(tip,data)=="text-mismatch")
            end
        ''')

    def test_base_item_auras_match_their_own_status_and_displayed_values(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local id,name
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="player" and instance==42)
                return {spellId=id,name=name,auraInstanceID=42}
            end}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function outcome() return S.OnTooltip(tip,data) end
            local function card(spell,title,body)
                id,name=spell,title
                data={type=7,id=999,lines={{leftText=title},{leftText=body},{leftText="16 seconds remaining"}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"player",42},tooltipData=data}
            end
            card(12257,"Breath of Fire","Breathing fire, dealing 76 to 80 Fire damage every 1 sec")
            assert(outcome()=="shown" and bodySeen=="พ่นไฟ สร้างความเสียหายไฟ 76 ถึง 80 หน่วยทุก 1 วินาที")
            card(23179,"Taint of Shadow","You are friendly to Jaedenar.")
            assert(outcome()=="shown" and bodySeen=="คุณเป็นมิตรกับชาวเจเดนาร์")
            card(1299440,"Demonbane","Feared.")
            assert(outcome()=="shown" and bodySeen=="ตกอยู่ในความหวาดกลัว")
            card(398196,"Quick Draw","Movement speed reduced by 52%.")
            assert(outcome()=="shown" and bodySeen=="ความเร็วเคลื่อนที่ลดลง 52%")
            id=398197; assert(outcome()=="missing")
            id=398196; data.lines[2].leftText="Movement speed reduced by -52%."
            assert(outcome()=="text-mismatch")
            card(1249118,"Eternal Power","Your casts of Healing Wave in combat grant up to 40 increased healing "..
                "and up to 13 increased damage for 15 sec.")
            assert(outcome()=="shown" and bodySeen:find("คลื่นรักษา",1,true))
            assert(bodySeen:find("ความเสียหายที่ทำได้",1,true))
            card(1249119,"Eternal Power","Healing done increased by up to 40 and spell damage done increased by up to 13.")
            assert(outcome()=="shown" and bodySeen:find("ความเสียหายเวทที่ทำได้",1,true))
            id=1249118; assert(outcome()=="text-mismatch")
            local function venom(radius,damage)
                return "Whenever you suffer Bleed damage, one dose is splashed onto a nearby enemy within "..
                    radius.." yds."..string.char(10,10).."When this effect expires, you will suffer "..damage.." Nature damage."
            end
            card(1251986,"Venomous Blood",venom("8","326"))
            assert(outcome()=="shown" and bodySeen:find("ศัตรูหนึ่งตัวในระยะ 8 หลา",1,true))
            assert(bodySeen:find("คุณจะได้รับความเสียหายธรรมชาติ 326 หน่วย",1,true))
            card(1251986,"Venomous Blood",venom("-8","326"))
            assert(outcome()=="text-mismatch")
            card(1251986,"Venomous Blood",venom("8","326"):gsub("you will suffer","the enemy will suffer"))
            assert(outcome()=="text-mismatch")
            for _,id in ipairs({20707,20762,20763,20764,20765}) do
                card(id,"Soulstone Resurrection","Soul is stored.")
                assert(outcome()=="shown" and titleSeen=="คืนชีพด้วยศิลาวิญญาณ" and bodySeen=="วิญญาณถูกเก็บไว้")
                data.lines[2].leftText="Soul is stored. Restores 200 health."
                assert(outcome()=="text-mismatch")
            end
            card(2379,"Speed","Increases run speed by 50%")
            assert(outcome()=="shown" and bodySeen=="เพิ่มความเร็วในการวิ่ง 50%")
            id=14530;assert(outcome()=="text-mismatch")
            data.lines[2].leftText="Increases run speed by 49.5%."
            assert(outcome()=="shown" and bodySeen=="เพิ่มความเร็วในการวิ่ง 49.5%")
            data.lines[2].leftText="Increases run speed by -49.5%."
            assert(outcome()=="text-mismatch")
            card(7840,"Swim Speed","Increases swim speed by 100%.")
            assert(outcome()=="shown" and bodySeen=="เพิ่มความเร็วในการว่ายน้ำ 100%")
            card(15279,"Crystal Spire","Causes 12 nature damage to attackers.")
            assert(outcome()=="shown" and bodySeen=="สร้างความเสียหายธรรมชาติ 12 หน่วยแก่ผู้ที่โจมตีคุณ")
            card(16621,"Self Invulnerability","Invulnerable to melee damage.")
            assert(outcome()=="shown" and bodySeen=="มีภูมิคุ้มกันต่อความเสียหายระยะประชิด")
            id=16620;assert(outcome()=="missing")
            card(5917,"Fumble","Lowered chance to hit with attacks.")
            assert(outcome()=="shown" and bodySeen=="โอกาสโจมตีโดนลดลง")
            for _,sample in ipairs({
                {470362,"Food","Restores 71.6 health per second.","ฟื้นฟูพลังชีวิต 71.6 หน่วยต่อวินาที"},
                {470369,"Food","Restores 46.4 health per second.","ฟื้นฟูพลังชีวิต 46.4 หน่วยต่อวินาที"},
                {26030,"Windblossom Berries","Restores 71.6 health per second.","ฟื้นฟูพลังชีวิต 71.6 หน่วยต่อวินาที"},
                {470361,"Increased Spell Damage","Spell Damage increased by 12.","ความเสียหายเวทเพิ่มขึ้น 12 หน่วย"},
                {470367,"Increased Healing Power","Healing done increased by 22.","ผลการรักษาที่ทำได้เพิ่มขึ้น 22 หน่วย"},
                {18191,"Increased Stamina","Stamina increased by 10.","ค่าความทนทานเพิ่มขึ้น 10 หน่วย"},
            }) do
                card(sample[1],sample[2],sample[3])
                assert(outcome()=="shown" and bodySeen==sample[4])
                data.lines[2].leftText=sample[3]:gsub("(%d)", "-%1",1)
                assert(outcome()=="text-mismatch")
            end
            card(470361,"Increased Spell Damage","Healing done increased by 22.")
            assert(outcome()=="text-mismatch")
            S.settings.descriptions=false
            card(5917,"Fumble","Lowered chance to hit with attacks.")
            data.lines[2].leftText="Lowered damage dealt.";assert(outcome()=="text-mismatch")
        ''')

    def test_observed_item_auras_require_own_complete_positive_native_text(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="target" and instance==23)
                return {spellId=id}
            end}
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function card(spellID,title,body,extra)
                id=spellID
                shown={title,body,extra or "5 seconds remaining"}
                data={type=7,id=23,lines={{leftText=title},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"target",23},tooltipData=data}
                return S.OnTooltip(tip,data)
            end
            for _,row in ipairs({
                {18820,"Insight","Mana costs reduced by 200.","ญาณหยั่งรู้","ค่ามานาที่ใช้ลดลง 200 หน่วย"},
                {17153,"Rend","Bleeding for 100 damage every 3 sec.","ฉีกบาดแผล","เลือดไหล ได้รับความเสียหาย 100 หน่วยทุก 3 วินาที"},
                {16415,"Fireball","25 Fire damage every 2 sec.","ลูกไฟ","ได้รับความเสียหายไฟ 25 หน่วยทุก 2 วินาที"},
                {13438,"Fireball","4 Fire damage every 2 sec.","ลูกไฟ","ได้รับความเสียหายไฟ 4 หน่วยทุก 2 วินาที"},
                {1314888,"Poison Sting","27 Nature damage inflicted every 3 sec.","เหล็กในพิษ","ได้รับความเสียหายธรรมชาติ 27 หน่วยทุก 3 วินาที"},
                {1320726,"Increased Feral Combat","Increased Feral Combat +1.","เพิ่มทักษะการต่อสู้แบบสัตว์ป่า","ทักษะการต่อสู้แบบสัตว์ป่าเพิ่มขึ้น +1"},
                {1292598,"Debt Collection","Regenerate 6 health and 2 mana every 5 sec.","ทวงหนี้","ฟื้นฟูพลังชีวิต 6 หน่วยและมานา 2 หน่วยทุก 5 วินาที"},
                {1294058,"White Obsidian","Mana cost of next spell cast reduced by 24.","ออบซิเดียนสีขาว","ค่ามานาที่ใช้ร่ายเวทครั้งถัดไปลดลง 24 หน่วย"},
                {1294645,"Blood Sacrifice","Drains 19 health every 2 sec to the caster.","บูชายัญโลหิต","พลังชีวิตถูกดูด 19 หน่วยส่งให้ผู้ร่ายทุก 2 วินาที"},
            }) do
                local spellID,title,body,thai,text=unpack(row)
                assert(card(spellID,title,body)=="shown" and titleSeen==thai and bodySeen==text)
                assert(card(spellID,title,body,"Immediate damage.")=="text-mismatch")
                assert(card(spellID,title,(body:gsub("%d+","-7",1)))=="text-mismatch")
                assert(card(spellID,title,(body:gsub("%d+","7 to 9",1)))=="text-mismatch")
            end
            assert(card(8191,"Zeal","Increased armor and damage done.")=="shown"
                and titleSeen=="ความฮึกเหิม" and bodySeen=="เกราะและความเสียหายที่สร้างเพิ่มขึ้น")
            assert(card(18798,"Freeze","Frozen.")=="shown" and bodySeen=="ติดผลแช่แข็ง")
            assert(card(18799,"Freeze","Frozen.")=="missing")
            assert(card(18798,"Freeze","Frozen. Additional damage.")=="text-mismatch")
            assert(card(1292594,"Debt Collection","Regenerate 6 health and 2 mana every 5 sec.")=="missing")
            assert(card(1294058,"White Obsidian","Mana cost of next spell cast reduced by 0.")=="text-mismatch")
            assert(card(1314040,"Burning Shell","Suffering 7 Fire damage every 4 sec.")=="text-mismatch")
            assert(S.records["item-effect:940:97151"] and not S.records["spell:18820"])
            assert(card(16415,"Fireball","25 Fire damage every 0 sec.")=="text-mismatch")
            S.settings.descriptions=false
            assert(card(18820,"Insight","Mana costs reduced by -200.")=="text-mismatch")
            assert(card(18820,"Insight","Mana costs reduced by 197.")=="shown" and bodySeen=="")
        ''')

    def test_set_reference_auras_keep_their_own_resistance_and_absorb_text(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function() return {spellId=id} end}
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup(spellID,title,body,extra)
                id=spellID
                shown={title,body,extra or "12 seconds remaining"}
                data={type=7,id=23,lines={{leftText=title},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"target",23},tooltipData=data}
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            for _,entry in ipairs({
                {28765,"Fire","ไฟ"}, {28766,"Frost","น้ำแข็ง"}, {28768,"Nature","ธรรมชาติ"},
                {28769,"Shadow","เงา"}, {28770,"Arcane","อาร์เคน"}
            }) do
                local id,school,thai=entry[1],entry[2],entry[3]
                local name,text=lookup(id,school.." Resistance","Increases "..school:lower().." resistance by 41.")
                assert(name=="ต้านทาน"..thai and text=="เพิ่มความต้านทาน"..thai.." 41 หน่วย")
                assert(not lookup(id,school.." Resistance","Increases "..school:lower().." resistance by 41%."))
            end
            local name,text=lookup(28810,"Armor of Faith","Absorbs damage.")
            assert(name=="เกราะแห่งศรัทธา" and text=="ดูดซับความเสียหาย")
            assert(not lookup(28810,"Armor of Faith","Absorbs 500 damage."))
            assert(not lookup(28809,"Armor of Faith","Absorbs damage."))
            assert(not lookup(28770,"Arcane Resistance","Increases shadow resistance by 41."))
            assert(not lookup(28770,"Arcane Resistance","Increases arcane resistance by 41.","Spell damage reduced."))
            S.settings.descriptions=false
            assert(lookup(28810,"Armor of Faith","Absorbs damage.")=="เกราะแห่งศรัทธา")
            assert(not lookup(28770,"Arcane Resistance","Increases arcane resistance by -41."))
            assert(not lookup(28770,"Arcane Resistance","Increases arcane resistance by 0."))
            assert(not S.records["aura:28820"] and not S.records["aura:1294070"])
        ''')

    def test_racial_state_auras_match_exact_ids_and_preserve_regeneration_values(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function() return {spellId=id} end}
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup(spellID,title,body,extra)
                id=spellID
                shown={title,body,extra}
                data={type=7,id=23,lines={{leftText=title},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"player",23},tooltipData=data}
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            local healing="Regenerate 7% of total Health and 8% of total Mana every 2 seconds."
            local name,text=lookup(20578,"Cannibalize",healing,"10 seconds remaining")
            assert(name=="กลืนกินศพ"
                and text=="ฟื้นฟูพลังชีวิต 7% ของพลังชีวิตสูงสุด และมานา 8% ของมานาสูงสุดทุก 2 วินาที")
            assert(not lookup(20577,"Cannibalize",healing))
            assert(not lookup(20578,"Cannibalize",healing,"Only works on Humanoid corpses."))
            local ghost="Move to the location of your corpse or speak with a spirit healer to be revived."
            for _,id in ipairs({8326,20584}) do
                name,text=lookup(id,"Ghost",ghost)
                assert(name=="วิญญาณ" and text=="ไปยังจุดที่ร่างของคุณอยู่ หรือคุยกับผู้รักษาวิญญาณเพื่อคืนชีพ")
            end
            assert(not lookup(1278162,"Ghost",ghost))
            assert(not lookup(20584,"Wisp Spirit",ghost))
            S.settings.descriptions=false
            assert(lookup(20578,"Cannibalize",healing)=="กลืนกินศพ")
            assert(not lookup(20578,"Cannibalize",(healing:gsub("8%%","-8%%"))))
            assert(not lookup(20578,"Cannibalize",(healing:gsub("7%%","0%%"))))
            assert(not lookup(20578,"Cannibalize",(healing:gsub("2 seconds","0 seconds"))))
            assert(not lookup(8326,"Ghost",ghost,"Movement speed increased."))
        ''')

    def test_weapon_enchant_procs_match_only_their_own_native_aura(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function() return {spellId=id} end}
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup(spellID,title,body,extra)
                id=spellID
                shown={title,body,extra or "12 seconds remaining"}
                data={type=7,id=23,lines={{leftText=title},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"target",23},tooltipData=data}
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            local chilled="Movement slowed by 31% and time between attacks increased by 22%."
            for _,entry in ipairs({
                {13907,"Smite Demon","Stunned.","พิฆาตปีศาจ","มึนงง"},
                {20005,"Chilled",chilled,"หนาวเย็น",
                    "ความเร็วเคลื่อนที่ลดลง 31% และช่วงเวลาระหว่างการโจมตีเพิ่มขึ้น 22%"},
                {20006,"Unholy Curse","Physical damage done reduced by 14.","คำสาปอัปมงคล",
                    "ความเสียหายกายภาพที่สร้างลดลง 14 หน่วย"},
                {20007,"Holy Strength","Strength Increased by 91.","พละกำลังศักดิ์สิทธิ์","พละกำลังเพิ่มขึ้น 91 หน่วย"},
                {1231124,"Righteous Strength","Strength increased by 120.","พละกำลังแห่งธรรม","พละกำลังเพิ่มขึ้น 120 หน่วย"},
                {1231138,"Righteous Fire","Spell Power increased by 139.","เพลิงแห่งธรรม","พลังเวทเพิ่มขึ้น 139 หน่วย"},
                {1231162,"Righteous Blasting","Spell Power increased by 70.","ระเบิดพลังแห่งธรรม","พลังเวทเพิ่มขึ้น 70 หน่วย"},
                {1232169,"Righteous Inquisition","Strength increased by 200.","การไต่สวนศักดิ์สิทธิ์","พละกำลังเพิ่มขึ้น 200 หน่วย"},
                {1299796,"Insight","Spirit increased by 37%.","ญาณหยั่งรู้","ค่าพลังวิญญาณเพิ่มขึ้น 37%"}
            }) do
                local name,text=lookup(entry[1],entry[2],entry[3])
                assert(name==entry[4] and text==entry[5])
            end
            assert(not lookup(1231152,"Righteous Fire","Spell Power increased by 139."))
            assert(not lookup(1231138,"Grand Arcanist","Spell Power increased by 139."))
            assert(not lookup(1231138,"Righteous Fire","Spell Power increased by 139.","Restores 400 mana."))
            assert(not lookup(20006,"Unholy Curse","Physical damage taken reduced by 14."))
            assert(not lookup(1299796,"Insight","Spirit increased by 37."))
            S.settings.descriptions=false
            assert(lookup(20005,"Chilled",chilled)=="หนาวเย็น")
            assert(not lookup(20005,"Chilled",(chilled:gsub("31%%","-31%%"))))
            assert(not lookup(20005,"Chilled",(chilled:gsub("22%%","0%%"))))
            assert(not lookup(20006,"Unholy Curse","Physical damage done reduced by -14."))
        ''')

    def test_eclipse_aura_preserves_visible_values_in_both_plural_forms(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function() return {spellId=id} end}
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup(body,spellID,title,extra)
                id=spellID or 408255
                shown={title or "Eclipse",body,extra or "14 seconds remaining"}
                data={type=7,id=23,lines={{leftText=shown[1]},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"player",23},tooltipData=data}
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            local singular="Your next 1 Starfire cast has 0.5 sec reduced cast time."
            local plural="Your next 3 Starfire casts have 0.33 sec reduced cast time."
            local title,body=lookup(singular)
            assert(title=="คราส" and body=="Starfire 1 ครั้งถัดไปของคุณใช้เวลาร่ายลดลง 0.5 วินาที")
            title,body=lookup(plural)
            assert(title=="คราส" and body=="Starfire 3 ครั้งถัดไปของคุณใช้เวลาร่ายลดลง 0.33 วินาที")
            assert(not lookup(singular,408248))
            assert(not lookup(plural,nil,"Lunar Eclipse"))
            assert(not lookup(plural,nil,nil,"Wrath damage increased."))
            S.settings.descriptions=false
            assert(lookup(singular)=="คราส" and lookup(plural)=="คราส")
            for _,changed in ipairs({
                singular:gsub("0.5","-0.5"), plural:gsub("0.33","0"),
                plural:gsub("next 3 ","next 0 "), plural:gsub("next 3 ","next 1.5 "),
                plural:gsub("next 3 ","next 2 to 3 "), (plural:gsub("casts have","cast have"))
            }) do
                assert(not lookup(changed))
            end
        ''')

    def test_contingency_plan_matches_each_active_buff_and_preserves_native_amounts(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            local title="Contingency Plan"
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="target" and instance==23)
                return {spellId=id}
            end}
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup(spellID,body,name,extra)
                id=spellID
                shown={name or title,body,extra or "12 seconds remaining"}
                data={type=7,id=23,lines={{leftText=shown[1]},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"target",23},tooltipData=data}
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            local healIds={1277456,1277457,1277458,1277459,1277460}
            local shieldIds={1277463,1277464,1277465,1277467,1277466}
            for rank,heal in ipairs(healIds) do
                local amount=25*rank
                local name,text=lookup(heal,"Healing "..amount.." damage every 3 sec.")
                assert(name=="แผนรับเหตุฉุกเฉิน" and text=="ฟื้นฟูพลังชีวิต "..amount.." หน่วยทุก 3 วินาที")
                local shield=shieldIds[rank]
                assert(not S.records["spell:"..shield] and not S.records["spell:"..heal])
                name,text=lookup(shield,"Absorbing "..amount.." damage.")
                assert(name=="แผนรับเหตุฉุกเฉิน" and text=="ดูดซับความเสียหายได้ "..amount.." หน่วย")
                assert(not lookup(shield,"Healing 25 damage every 3 sec."))
                assert(not lookup(heal,"Absorbing 155 damage."))
            end
            assert(not lookup(1277462,"Absorbing 155 damage."))
            assert(not lookup(1277463,"Absorbing 155 damage.","Power Word: Shield"))
            assert(not lookup(1277463,"Absorbing 0 damage."))
            assert(not lookup(1277456,"Healing 25 damage every -3 sec."))
            assert(not lookup(1277463,"Absorbing 155 damage.",nil,"Increases healing taken."))
            S.settings.descriptions=false
            assert(lookup(1277463,"Absorbing 155 damage.")=="แผนรับเหตุฉุกเฉิน")
            assert(not lookup(1277463,"Absorbs 155 damage."))
        ''')

    def test_equipment_and_racial_auras_use_complete_child_text_and_native_values(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum.TooltipDataType.UnitAura=7
            local id,shown
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(_,instance)
                assert(instance==23)
                return {spellId=id}
            end}
            local function card(spellID,name,body)
                id=spellID
                shown={name,body,"12 seconds remaining"}
                data={type=7,id=23,lines={{leftText=name},{leftText=body}}}
                info={getterName="GetUnitAuraByAuraInstanceID",getterArgs={"target",23},tooltipData=data}
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {GetText=function() return shown[i] end,IsShown=function() return true end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local function lookup()
                local c=S.Context(tip,data)
                if c then return S.Lookup(c.key,c.name,c.lines) end
            end
            local examples={
                {26129,"Enigma's Answer","Spell hit chance increased by 7%.","เพิ่มขึ้น 7%"},
                {27779,"Divine Protection","Absorbs 452 damage.","ดูดซับความเสียหาย 452 หน่วย"},
                {27868,"Freeze","Frozen.","ถูกแช่แข็งอยู่กับที่"},
                {27499,"Crusader's Wrath","Magical damage and healing dealt is increased by 64","เวทมนตร์เพิ่มขึ้น 64 หน่วย"},
                {27775,"The Furious Storm","Magical damage and healing dealt is increased by 64","เวทมนตร์เพิ่มขึ้น 64 หน่วย"},
                {26121,"Stormcaller's Wrath","Damage done by Nature spells and effects increased by up to 51.",
                    "เวทธรรมชาติและเอฟเฟกต์ธรรมชาติเพิ่มขึ้นสูงสุด 51 หน่วย"},
                {28846,"Cheat Death","Increases healing received by up to 161.","ได้รับการรักษาเพิ่มขึ้นสูงสุด 161 หน่วย"},
                {28804,"Epiphany","Restores 25 mana per 5 sec.","ฟื้นฟูมานา 25 หน่วยทุก 5 วินาที"},
                {28772,"Elemental Vulnerability","Vulnerable to elemental power, increasing the damage taken from spells by up to 201.",
                    "ได้รับความเสียหายจากเวทเพิ่มขึ้นสูงสุด 201 หน่วย"},
                {21330,"Corrupted Fear","Fear and reduced movement speed.","ติดผลหวาดกลัวและเคลื่อนที่ช้าลง"},
                {1294071,"Ferocity of the Barkskin","Attack Power increased by 42.","พลังโจมตีเพิ่มขึ้น 42 หน่วย"},
                {1259688,"Elemental Blessing","Movement speed and mounted movement speed increased by 15%.",
                    "ความเร็วขณะขี่พาหนะเพิ่มขึ้น 15%"},
                {1259688,"Elemental Blessing","Movement speed and mounted movement speed increased by 30%.",
                    "ความเร็วขณะขี่พาหนะเพิ่มขึ้น 30%"},
                {1270842,"Energized","Mana and health regeneration rate increased by 50%.",
                    "อัตราการฟื้นฟูมานาและพลังชีวิตเพิ่มขึ้น 50%"},
                {1270842,"Energized","Mana and health regeneration rate increased by 100%.",
                    "อัตราการฟื้นฟูมานาและพลังชีวิตเพิ่มขึ้น 100%"},
                {1259691,"Attuned","Attuned to nearby leylines, increasing the benefit of your Read Leyline ability by 100%.",
                    "ผลของหยั่งกระแสเวทเพิ่มขึ้น 100%"},
                {1270893,"Charged","Charged by an elemental convergence, increasing the benefit of your Skysight ability by 100%.",
                    "ผลของเนตรเวหาเพิ่มขึ้น 100%"},
            }
            for _,example in ipairs(examples) do
                card(example[1],example[2],example[3])
                local name,text=lookup()
                assert(name and text and text:find(example[4],1,true))
                shown[3]="Additional effect.";assert(not lookup())
            end
            card(28804,"Epiphany","Restores -25 mana per 5 sec.");assert(not lookup())
            card(1259688,"Elemental Blessing","Movement speed and mounted movement speed increased by -15%.")
            assert(not lookup())
            card(1259688,"Elemental Blessing","Movement speed and mounted movement speed increased by 15%.")
            id=1259686;assert(not lookup())
            card(1270842,"Energized","Mana and health regeneration rate increased by 0%.")
            assert(not lookup())
            card(1270842,"Attuned","Mana and health regeneration rate increased by 100%.")
            assert(not lookup())
            card(1270893,"Charged","Movement speed increased by 100%.")
            S.settings.descriptions=false;assert(not lookup())
            card(28804,"Epiphany","Restores 25 mana per 6 sec.")
            S.settings.descriptions=false;assert(not lookup())
            card(28804,"Epiphany","Restores 25 mana per 5 sec.")
            local title,description=lookup()
            assert(title=="การรู้แจ้ง" and description=="")
            id=28802;assert(not lookup())
            assert(not S.records["aura:1294070"])
            S.settings.descriptions=true
            local _,skysight=S.Lookup("spell:1259686","Skysight",{
                "Attempt to draw power from a convergence of elements and receive its blessing, increasing your movement and mounted movement speeds by 15% for 30 sec. If an elemental convergence is nearby, you will become Charged for the next 1 hour and the effect of this ability will be increased by 100%."})
            assert(skysight:find("ผลอัดพลังธาตุ",1,true))
            local _,leyline=S.Lookup("spell:1259705","Read Leyline",{
                "Attempt to tap into the power of a nearby leyline, increasing your Health and Mana regeneration by 50% for 15 sec. If a leyline is nearby, you will become Attuned for the next 1 hour and the effect of this ability will be increased by 100%."})
            assert(leyline:find("ผลประสานเส้นพลังเวท",1,true))
        ''')

    def test_unspent_redoubt_uses_first_rank_preview_and_native_spacing(self):
        data = ROOT / 'addon/ForeverThai/Skills/Data.lua'
        self.lua.execute(data.read_text(encoding='utf-8'), 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            local S=addon.skills
            local displayRank,purchased=0,0
            local expected="Damaging melee attacks against you have a 10% chance to increase your chance to block by 6%.  Lasts 10 sec or 5 blocks."
            local data={type=1,lines={{leftText=expected}}}
            local info={getterName="GetTraitEntry",getterArgs={201,0},tooltipData=data}
            local owner={GetEntryID=function() return 201 end,GetName=function() return "Redoubt" end,
                GetTalentFrame=function() return {GetConfigID=function() return 7 end} end,
                GetTooltipEntryInfo=function()
                    return {currEntryInfo={entryID=201,rank=displayRank},ranksPurchased=purchased}
                end}
            local tip=frame(UIParent)
            function tip:GetProcessingTooltipInfo() return info end
            function tip:GetOwner() return owner end
            C_Traits={
                GetEntryInfo=function(c,e) assert(c==7 and e==201);return {definitionID=801} end,
                GetDefinitionInfo=function(d) assert(d==801);return {spellID=20127} end,
            }
            local function lookup()
                local c=S.Context(tip,data)
                if not c then return end
                local title,body=S.Lookup(c.key,c.name,c.lines)
                return title,body,c
            end
            local shownTitle,shownBody
            function S.RememberLongText(title,body) shownTitle,shownBody=title,body end
            S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and shownTitle:find("ตัวอย่างแรงก์ 1",1,true))
            assert(shownBody:find("เพิ่มโอกาสบล็อกของคุณ 6%",1,true))
            local title,body,context=lookup()
            assert(title and body:find("เพิ่มโอกาสบล็อกของคุณ 6%",1,true))
            assert(context.rank==1 and context.previewRank and context.key=="talent-spell:20127:1")
            data.lines[1].leftText=expected:gsub("5 blocks","5 seconds")
            assert(not lookup())
            data.lines[1].leftText=expected
            purchased=1
            assert(not lookup())
            purchased=0
            displayRank=1
            assert(not lookup())
            displayRank=0
            info.tooltipData={}
            assert(not lookup())
            info.tooltipData=data
            info.getterArgs[2]=1
            title,body,context=lookup()
            assert(title and body:find("เพิ่มโอกาสบล็อกของคุณ 6%",1,true) and not context.previewRank)
            info.getterArgs[2]=nil
            assert(not lookup())
        ''')

    def test_font_rejection_draws_real_skill_atlas_and_preserves_visible_numbers(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            GameTooltip=tip
            local owner={GetEntryID=function() return 130350 end,GetName=function() return "Redoubt" end,
                GetTalentFrame=function() return {GetConfigID=function() return 7 end} end,
                GetTooltipEntryInfo=function() return {currEntryInfo={entryID=130350,rank=0},ranksPurchased=0} end}
            function tip:GetOwner() return owner end
            C_Traits={GetEntryInfo=function() return {definitionID=801} end,
                GetDefinitionInfo=function() return {spellID=20127} end}
            data={type=1,id=20127,lines={{leftText="Damaging melee attacks against you have a 10% chance to " ..
                "increase your chance to block by 6%.  Lasts 10 sec or 5 blocks."}}}
            info={getterName="GetTraitEntry",getterArgs={130350,0},tooltipData=data}
            S.settings.original=false
            function S.RememberLongText(title,text) savedTitle,savedText=title,text end
            assert(S.OnTooltip(tip,data)=="shown" and S.reader:IsVisible())
            assert(savedTitle:find("ตัวอย่างแรงก์ 1",1,true))
            assert(savedText:find("6%",1,true) and savedText:find("5 ครั้ง",1,true))
            local sawTexture, sawPercent = false, false
            for _,layer in ipairs(frames) do
                if layer:IsVisible() and layer.parent and layer.parent.parent==S.reader then
                    for _,texture in ipairs(layer.textures or {}) do
                        if texture:IsShown() and texture.texture:find("Fonts\\\\SkillsThai",1,true) then sawTexture=true end
                    end
                    for _,label in ipairs(layer.fontstrings) do
                        if label:IsShown() and label.text=="6%" then sawPercent=true end
                    end
                end
            end
            assert(sawTexture and sawPercent)
            Enum.TooltipDataLineType={None=0,SpellDescription=34}
            data={type=1,id=25780,lines={{leftText="Righteous Fury"},
                {leftText="62 Mana",lineIndex=2,type=0},{leftText="Instant",lineIndex=3,type=0},
                {type=34,leftText="Increases all threat generated by 33%, and all threat generated by your Holy attacks by " ..
                    "an additional 90%. Lasts 30 min."}}}
            info={getterName="GetAction",getterArgs={6},tooltipData=data}
            function tip:GetLeftLine(i)
                local line=data.lines[i]
                return {IsShown=function() return true end,GetText=function() return line.leftText end}
            end
            function tip:GetRightLine() return nil end
            C_Spell={IsSpellPassive=function() return false end,
                GetSpellInfo=function() return {spellID=25780,name="Righteous Fury",castTime=0} end}
            local actionType,actionID="spell",25780
            function GetActionInfo(slot) assert(slot==6); return actionType,actionID end
            assert(S.OnTooltip(tip,data)=="shown" and savedText:find("90%",1,true))
            assert(savedText:find("ร่ายทันที",1,true))
            actionType="macro"
            assert(S.OnTooltip(tip,data)=="shown" and not savedText:find("ร่ายทันที",1,true))
            actionType="spell";actionID=100
            assert(S.OnTooltip(tip,data)=="shown" and not savedText:find("ร่ายทันที",1,true))
            combat=true
            assert(S.OnTooltip(tip,data)=="combat" and not S.reader:IsShown())
        ''')

    def test_completed_action_and_talent_tooltips_retry_and_probe_exact_payload(self):
        data_source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(data_source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            GameTooltip=tip
            function tip:SetAction() end
            function S.reader:IsVisible() return self:IsShown() end
            local actionHook,talentCallback,postCall
            function hooksecurefunc(widget,method,callback)
                assert(widget==tip and method=="SetAction")
                actionHook=callback
            end
            EventRegistry={RegisterCallback=function(_,event,callback,owner)
                assert(event=="TalentDisplay.TooltipCreated" and owner==S)
                talentCallback=callback
            end}
            TooltipDataProcessor={AllTypes=99,AddTooltipPostCall=function(types,callback)
                assert(types==99)
                postCall=callback
            end}
            S.RegisterTooltips()
            data={type=1,id=25780,lines={{leftText="Righteous Fury"},{leftText="62 Mana"},{leftText="Instant"},
                {leftText="Increases all threat generated by 33%, and all threat generated by your Holy attacks by an additional 90%.  Lasts 30 min."}}}
            info={getterName="GetAction",getterArgs={6},tooltipData=data}
            tip:Show()
            actionHook(tip,5)
            assert(not S.reader:IsShown())
            actionHook(tip,6)
            assert(S.reader:IsShown())
            local count=S.stats.callbacks
            actionHook(tip,6)
            assert(S.stats.callbacks==count)
            local output={}
            function print(text) output[#output+1]=text end
            S.ProbeTooltip()
            assert(output[1]:find("GetAction",1,true) and output[2]=="spell:25780 shown visible=true")
            data.lines[4].leftText="Reduces all threat."
            S.ProbeTooltip()
            assert(output[4]=="spell:25780 text-mismatch visible=false")
            assert(output[5]:find("Reduces all threat.",1,true))
            assert(postCall(tip,data)==nil)

            data={type=1,lines={{leftText="Increases your total Intellect by 2%."}}}
            info={getterName="GetTraitEntry",getterArgs={501,0},tooltipData=data}
            local owner={GetEntryID=function() return 501 end,GetName=function() return "Divine Intellect" end,
                GetTalentFrame=function() return {GetConfigID=function() return 7 end} end,
                GetTooltipEntryInfo=function() return {currEntryInfo={entryID=501,rank=0},ranksPurchased=0} end}
            function tip:GetOwner() return owner end
            C_Traits={
                GetEntryInfo=function(c,e) assert(c==7 and e==501); return {definitionID=502} end,
                GetDefinitionInfo=function(d) assert(d==502); return {spellID=20257} end,
            }
            talentCallback(S,{},tip)
            assert(not S.reader:IsShown())
            talentCallback(S,owner,tip)
            assert(S.reader:IsShown())
            S.ProbeTooltip()
            assert(output[#output]=="talent-spell:20257:1 shown visible=true")
            fontOK=false
            S.ProbeTooltip()
            assert(output[#output]=="talent-spell:20257:1 text-render-failed visible=false")
        ''')

    def test_completed_talent_reads_visible_requirements_and_preserves_native_tooltip(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua', 'Skills/TalentTreeNames.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            local completed, post
            EventRegistry={RegisterCallback=function(_,event,fn)
                assert(event=="TalentDisplay.TooltipCreated"); completed=fn
            end}
            TooltipDataProcessor={AllTypes=99,AddTooltipPostCall=function(_,fn) post=fn end}
            S.RegisterTooltips()
            local config,treeID,nodeID,entryID,spellID=7,1100,105630,130354,20143
            local tree,talent="Protection","Toughness"
            local node={ID=nodeID,groupIDs={11541}}
            local talentFrame={GetConfigID=function() return config end,GetTalentTreeID=function() return treeID end,
                GetTraitTreeName=function(_,id,groups)
                    assert(id==treeID and groups==node.groupIDs); return tree
                end}
            local owner={GetName=function() return talent end,GetEntryID=function() return entryID end,
                GetNodeID=function() return nodeID end,GetNodeInfo=function() return node end,
                GetTalentFrame=function() return talentFrame end}
            C_Traits={GetEntryInfo=function(c,e) assert(c==config and e==entryID); return {definitionID=42} end,
                GetDefinitionInfo=function() return {spellID=spellID} end}
            local left,right={},{}
            local count=3
            local function line(index,text)
                left[index]=frame(tip);left[index]:SetText(text)
            end
            function tip:GetOwner() return owner end
            function tip:GetLeftLine(i) return left[i] end
            function tip:GetRightLine(i) return right[i] end
            function tip:NumLines() return count end
            function S.RememberLongText(_,text) body=text end
            local function card(description)
                data={type=1,id=spellID,lines={{leftText=description,lineIndex=3}}}
                info={getterName="GetTraitEntry",getterArgs={entryID,1},tooltipData=data}
                line(1,talent);line(3,description);count=3
                post(tip,data)
                assert(S.reader:IsShown() and not body:find("ต้องลงแต้ม",1,true))
            end
            S.settings.original=false
            card("Increases your armor value from items by 2%.")
            count=7
            line(4,"Click to learn")
            line(5,"|cffff2020Spend 3 more points in Protection Talents|r")
            line(6,"Requires all preceding talents")
            line(7,"Requires 10 points in Protection Talents")
            completed(S,{},tip)
            assert(not body:find("เพิ่มอีก",1,true))
            completed(S,owner,tip)
            assert(S.reader:IsShown() and body:find("ป้องกัน เพิ่มอีก 3 แต้ม",1,true))
            assert(body:find("คลิกเพื่อเรียนพรสวรรค์",1,true))
            assert(body:find("ต้องเรียนพรสวรรค์ก่อนหน้าที่เชื่อมมาทั้งหมด",1,true))
            assert(not body:find("10 แต้ม",1,true) and left[5]:GetText():find("Spend 3",1,true))
            node.groupIDs={11559}
            assert(S.TalentRequirements(tip,data).text:find("Protection เพิ่มอีก 3 แต้ม",1,true))
            node.groupIDs={11559,11541}
            assert(S.TalentRequirements(tip,data).text:find("ป้องกัน เพิ่มอีก 3 แต้ม",1,true))
            node.groupIDs={11541}
            line(4,"Click to preview")
            line(5,"Spend 3 more points in Holy Talents")
            local partial=S.TalentRequirements(tip,data)
            assert(partial and not partial.text:find("เพิ่มอีก",1,true) and not partial.limit)
            right[6]=frame(tip);right[6]:SetText("Unexpected second column")
            assert(not S.TalentRequirements(tip,data));right[6]=nil
            secret[left[6]]=true
            assert(not S.TalentRequirements(tip,data));secret[left[6]]=nil
            config=-7;assert(not S.TalentRequirements(tip,data));config=7

            local footers={
                {"Right click to unlearn","คลิกขวาเพื่อยกเลิกพรสวรรค์"},
                {"Shift click to learn all connected history nodes","กด Shift ค้างแล้วคลิกเพื่อเรียนพรสวรรค์ทั้งหมดที่เชื่อมถึงกันในประวัติการลงแต้ม"},
                {"Right click to clear all history nodes","คลิกขวาเพื่อล้างประวัติการลงแต้มทั้งหมด"},
                {"No active links. Reconnect or unlearn this talent.","ไม่มีเส้นเชื่อมที่ใช้งานอยู่ ให้เชื่อมใหม่หรือยกเลิกพรสวรรค์นี้"},
                {"Spend more points to restore this talent or right click to unlearn it","ลงแต้มเพิ่มเพื่อให้พรสวรรค์นี้กลับมาใช้งานได้ หรือคลิกขวาเพื่อยกเลิก"},
            }
            count=4
            for _,footer in ipairs(footers) do
                line(4,footer[1])
                local localized=S.TalentRequirements(tip,data)
                assert(localized.limit==3 and localized.text==footer[2] and left[4]:GetText()==footer[1])
                completed(S,owner,tip)
                assert(S.reader:IsShown() and body:find(footer[2],1,true))
                line(4,footer[1].."!")
                assert(not S.TalentRequirements(tip,data))
            end

            treeID,nodeID,entryID,spellID=1187,110289,136850,1225457
            node={ID=nodeID,groupIDs={12440}}
            tree,talent="Professions","Master Chef"
            card("Your cooking recipes have a 10% chance to create an extra result.")
            line(4,"");line(5,"Spend 1 more |4point:points; in the Professions Legacy Tree");count=5
            assert(S.TalentRequirements(tip,data).limit==3)
            completed(S,owner,tip)
            assert(S.reader:IsShown() and body:find("ผัง Legacy ด้านอาชีพ เพิ่มอีก 1 แต้ม",1,true))
            treeID,tree=1188,"Adventure"
            line(5,"Spend 5 more points in the Adventure Legacy Tree")
            assert(S.TalentRequirements(tip,data).text=="ต้องลงแต้มในผัง Legacy ด้านผจญภัย เพิ่มอีก 5 แต้ม")
            treeID,tree=1189,"Resourcefulness"
            line(5,"Spend 5 more points in the Resourcefulness Legacy Tree")
            assert(S.TalentRequirements(tip,data).text=="ต้องลงแต้มในผัง Legacy ด้านความมีไหวพริบ เพิ่มอีก 5 แต้ม")
            treeID=1188
            assert(S.TalentRequirements(tip,data).text=="ต้องลงแต้มในผัง Legacy สาย Resourcefulness เพิ่มอีก 5 แต้ม")
            treeID,tree=1187,"Professions"
            line(5,"Spend 1 more points in the Professions Legacy Tree")
            assert(not S.TalentRequirements(tip,data))
            S.settings.descriptions=false
            post(tip,data)
            line(5,"Spend 5 more points in the Professions Legacy Tree")
            completed(S,owner,tip)
            assert(body=="" and S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_tooltip_uses_live_rank_and_learn_level_and_respects_setting(self):
        self.lua.execute('''
            function S.RememberLongText(title,text) body=text end
            S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and body:find("แรงก์ 2",1,true))
            assert(body:find("เลเวลที่เรียนสกิล 24",1,true) and body:find("ฟื้นฟูพลังชีวิต 10",1,true))
            entry.subName="Rank 3";learnLevel=30
            S.OnTooltip(tip,data)
            assert(body:find("แรงก์ 3",1,true) and body:find("เลเวลที่เรียนสกิล 30",1,true))
            S.settings.descriptions=false
            S.OnTooltip(tip,data)
            assert(body=="" and calls==2 and S.stats.errors==0)
        ''')

    def test_quick_draw_spellbook_matches_both_verified_description_paragraphs(self):
        source = (ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8')
        self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            Enum.TooltipDataLineType={SpellDescription=34}
            entry={spellID=398196,itemType=1,name="Quick Draw",isPassive=false}
            data.id=398196
            local first="Draw your ranged weapon and fire a quick shot at an enemy, causing normal ranged weapon damage "..
                "and reducing the target's movement speed by 51% for 7 sec. Awards 1 combo point."
            local second="Quick Draw benefits from all talents and effects that trigger from or modify Sinister Strike."
            data.lines={{leftText="Quick Draw"},{leftText=first,type=34,lineIndex=2},{leftText=second,type=34,lineIndex=3}}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                if data.lines[i] then
                    return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
                end
            end
            function tip:GetRightLine() end
            local function lookup()
                local context=S.Context(tip,data)
                if context then return S.Lookup(context.key,context.name,context.lines) end
            end
            local title,body=lookup()
            assert(title=="ชักปืนไว" and body:find("51% เป็นเวลา 7 วินาที",1,true))
            assert(body:find("1 แต้มคอมโบ",1,true) and body:find("ฟันอำมหิต",1,true))
            data.lines[3]=nil
            assert(not lookup())
            assert(not S.records["spell:399954"])
        ''')

    def test_cast_uses_exact_live_spellbook_label_and_spell_identity(self):
        self.lua.execute('''
            Enum.TooltipDataLineType={None=0,SpellPassive=33,SpellDescription=34}
            entry.isPassive=false
            data.lines[3]=data.lines[2];data.lines[3].type=34
            data.lines[2]={type=0,lineIndex=2,leftText="1.5 sec cast",rightText="30 sec cooldown"}
            local detail=data.lines[2]
            local actual,visible,right=1470,detail.leftText,detail.rightText
            local spellID,spellName=101,"Recipe A"
            C_Spell={GetSpellInfo=function(id)
                assert(id==101);return {spellID=spellID,name=spellName,castTime=actual}
            end}
            local function region(text) return {IsShown=function() return true end,GetText=function() return text end} end
            function tip:GetLeftLine(i) return region(i==1 and "Recipe A" or visible) end
            function tip:GetRightLine(i) if i==2 and right then return region(right) end end
            local function label(text,value)
                detail.leftText=text;visible=text;actual=value
            end
            local function missing()
                local value=metadata()
                assert(not value:find("เวลาร่าย",1,true) and not value:find("ร่ายทันที",1,true)
                    and not value:find("ติดตัว",1,true) and not value:find("ร่ายต่อเนื่อง",1,true)
                    and not value:find("คูลดาวน์",1,true))
            end
            assert(metadata():find("ใช้เวลาร่าย 1.5 วินาที",1,true))
            assert(metadata():find("คูลดาวน์ 30 วินาที",1,true))
            visible="2 sec cast";missing();visible=detail.leftText
            right="29 sec cooldown";missing();right=detail.rightText
            spellID=102;missing();spellID=101
            spellName="Other Spell";missing();spellName="Recipe A"
            label("1.6 sec cast",1470);missing()
            label("5.9 sec cast",5882);assert(metadata():find("ใช้เวลาร่าย 5.9 วินาที",1,true))
            label("1 min cast",60000);assert(metadata():find("ใช้เวลาร่าย 1 นาที",1,true))
            label("Instant",0);assert(metadata():find("ร่ายทันที",1,true))
            entry.itemType=2;missing();entry.itemType=1
            detail.type=34;missing();detail.type=0
            label("Channeled",0)
            assert(metadata():find("ร่ายต่อเนื่อง",1,true) and not metadata():find("ร่ายทันที",1,true))
            label("Channeled",1500);missing()
            label("Passive",0);missing()
            detail.type=33;entry.isPassive=true
            assert(metadata():find("ติดตัว",1,true))
            entry.isPassive=false;missing()
        ''')

    def test_cooldown_mirrors_only_paired_native_right_column(self):
        self.lua.execute(r'''
            Enum.TooltipDataLineType={None=0,SpellPassive=33,SpellDescription=34}
            C_Spell={GetSpellInfo=function() return {spellID=101,name="Recipe A",castTime=0} end,
                IsSpellPassive=function() return false end}
            function GetActionInfo(slot) assert(slot==6);return "spell",101 end
            info.getterName="GetAction";info.getterArgs={6}
            local detail={type=0,lineIndex=3,leftText="Channeled"}
            data.lines[2]={type=0,lineIndex=2,leftText="80 Mana",rightText="30 yd range"}
            data.lines[3]=detail
            data.lines[4]={type=34,lineIndex=4,leftText="Heals 10 health."}
            local actualRight
            local function region(text) return {IsShown=function() return true end,GetText=function() return text end} end
            function tip:GetLeftLine(i) return region(data.lines[i].leftText) end
            function tip:GetRightLine(i) if i==3 and actualRight then return region(actualRight) end end
            local function cast(text)
                actualRight=text;detail.rightText=text
                return S.ActionCastMetadata(tip,data,S.Context(tip,data))
            end
            for _,sample in ipairs({
                {"12 sec cooldown","12 วินาที"},{"2.5 min cooldown","2.5 นาที"},
                {"3 hour cooldown","3 ชั่วโมง"},{"2 day cooldown","2 วัน"},
            }) do
                assert(cast(sample[1])=="ร่ายต่อเนื่อง\nคูลดาวน์ "..sample[2])
            end
            for _,text in ipairs({"12 sec recharge","Cooldown remaining: 12 sec","Instant cooldown",
                "12 secs cooldown","12.0 sec cooldown","0 sec cooldown","12 sec cooldown extra"}) do
                assert(cast(text)=="ร่ายต่อเนื่อง")
            end
            assert(cast(nil)=="ร่ายต่อเนื่อง")
            data.lines[4].rightText="12 sec cooldown"
            assert(cast(nil)=="ร่ายต่อเนื่อง")
            detail.type=34
            assert(not cast("12 sec cooldown"))
        ''')

    def test_native_action_cost_and_range_match_holy_light_rank_two(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            GameTooltip=tip
            Enum.PowerType={Mana=0}
            Enum.TooltipDataLineType={None=0,SpellDescription=34}
            local details={type=0,lineIndex=2,leftText="60 Mana",rightText="40 yd range"}
            data.id=639
            data.lines={{leftText="Holy Light",rightText="Rank 2"},details,
                {type=0,lineIndex=3,leftText="2.5 sec cast"},
                {type=34,lineIndex=4,leftText="Heals a friendly target for 81 to 96."}}
            info.getterName="GetAction";info.getterArgs={6}
            local actionType,actionID="spell",639
            function GetActionInfo(slot) assert(slot==6);return actionType,actionID end
            ActionBarActionButtonMixin={SetTooltip=forbidden}
            local owner={action=6,SetTooltip=forbidden,IsForbidden=function() return false end}
            function tip:GetOwner() return owner end
            local cost={type=0,cost=60,minCost=60,costPercent=0,costPerSec=0,requiredAuraID=0}
            local costs={cost}
            local powerCalls=0
            local spell={spellID=639,name="Holy Light",castTime=2500,minRange=0,maxRange=40}
            local subtext="Rank 2"
            C_Spell={GetSpellInfo=function(id) assert(id==639);return spell end,
                GetSpellSubtext=function(id) assert(id==639);return subtext end,
                IsSpellPassive=function() return false end,
                GetSpellPowerCost=function(id) assert(id==639);powerCalls=powerCalls+1;return costs end}
            local rightOverride,titleRankOverride
            local function region(text) return {IsShown=function() return true end,GetText=function() return text end} end
            function tip:GetLeftLine(i) return region(data.lines[i].leftText) end
            function tip:GetRightLine(i)
                local value=(i==1 and titleRankOverride) or (i==2 and rightOverride) or data.lines[i].rightText
                if value then return region(value) end
            end
            function S.RememberLongText(title,text) titleSeen,bodySeen=title,text end
            local function metadata() return S.ActionCastMetadata(tip,data,S.Context(tip,data)) end
            local cast="ใช้เวลาร่าย 2.5 วินาที"
            assert(S.OnTooltip(tip,data)=="shown" and titleSeen=="แสงศักดิ์สิทธิ์")
            assert(bodySeen=="แรงก์ 2\nใช้มานา 60\nระยะ 40 หลา\n"..cast..
                "\nฟื้นฟูพลังชีวิตให้เป้าหมายฝ่ายเดียวกัน 81 ถึง 96 หน่วย")
            assert(powerCalls==1)
            local rest="ใช้มานา 60\nระยะ 40 หลา\n"..cast
            titleRankOverride="Rank 1";assert(metadata()==rest);titleRankOverride=nil
            subtext="Rank 1";assert(metadata()==rest);subtext="Rank 2"
            details.lineIndex=3;assert(metadata()=="แรงก์ 2\n"..cast);details.lineIndex=2
            local hidden=trap();secret[hidden]=true
            subtext=hidden;assert(metadata()==rest);subtext=nil
            local before=powerCalls
            rightOverride="39 yd range";assert(metadata()==cast);rightOverride=nil
            owner.action=5;assert(metadata()==cast);owner.action=6
            details.lineIndex=3;assert(metadata()==cast);details.lineIndex=2
            assert(powerCalls==before)
            actionType="macro";assert(not metadata());actionType="spell"
            actionID=635;assert(not metadata());actionID=639
            costs[2]=cost;assert(metadata()=="ระยะ 40 หลา\n"..cast);costs[2]=nil
            cost.requiredAuraID=1;assert(metadata()=="ระยะ 40 หลา\n"..cast);cost.requiredAuraID=0
            cost.minCost=59;assert(metadata()=="ระยะ 40 หลา\n"..cast);cost.minCost=60
            spell.minRange=5;assert(metadata()=="ใช้มานา 60\n"..cast);spell.minRange=0
            data.lines[4].leftText="Unknown tooltip body."
            before=powerCalls
            assert(S.OnTooltip(tip,data)=="text-mismatch" and powerCalls==before)
            data.lines[4].leftText="Heals a friendly target for 81 to 96."
            S.settings.descriptions=false
            assert(S.OnTooltip(tip,data)=="shown" and bodySeen=="" and powerCalls==before)
            function InCombatLockdown() return true end
            S.settings.descriptions=true
            S.OnTooltip(tip,data)
            assert(powerCalls==before)
        ''')

    def test_talent_spell_alias_requires_current_action_or_learned_spellbook_and_full_body(self):
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            local sid=402174
            assert(S.talentCastAliases[sid]=="talent-spell:402174:1" and not S.records["spell:402174"])
            assert(not S.talentCastAliases[11426] and not S.talentCastAliases[20127])
            Enum.TooltipDataLineType={None=0,SpellDescription=34}
            local description="Launches a volley of holy light at the target, causing 53 Holy damage to an enemy, " ..
                "or 155 healing to an ally, instantly and every 1 sec for 2 sec."
            local line={type=34,lineIndex=3,leftText=description}
            data={type=1,id=sid,lines={{leftText="Penance"},{leftText="Channeled"},line}}
            info={getterName="GetAction",getterArgs={6},tooltipData=data}
            local visible=description
            local function region(text) return {IsShown=function() return true end,GetText=function() return text end} end
            function tip:GetLeftLine(i) return region(i==1 and "Penance" or visible) end
            function tip:GetRightLine() end
            local actionType, actionID="spell",sid
            function GetActionInfo(slot) assert(slot==6);return actionType,actionID end
            function S.RememberLongText(title,text) titleSeen,bodySeen=title,text end
            local function outcome() return S.OnTooltip(tip,data) end
            assert(outcome()=="shown" and titleSeen=="ชำระบาป")
            assert(bodySeen:find("53 หน่วย",1,true) and bodySeen:find("155 หน่วย",1,true))
            actionType="macro";assert(outcome()=="missing");actionType="spell"
            actionID=1240720;assert(outcome()=="missing");actionID=sid
            primary={tooltipData=data};assert(outcome()=="missing");primary=nil
            line.type=0;assert(outcome()=="missing");line.type=34
            visible="Unrelated visible description.";assert(outcome()=="missing")
            visible="Different native effect.";line.leftText=visible
            S.settings.descriptions=false
            assert(outcome()=="text-mismatch")
            visible=description;line.leftText=description
            assert(outcome()=="shown" and bodySeen=="")
            S.settings.descriptions=true
            info.getterName="GetSpellBookItem";info.getterArgs={7,0}
            entry={name="Penance",spellID=sid,itemType=1,isPassive=false}
            assert(outcome()=="shown" and bodySeen:find("155 หน่วย",1,true))
            entry.itemType=2;assert(outcome()=="missing");entry.itemType=1
            entry.isPassive=true;assert(outcome()=="missing");entry.isPassive=false
            S.records["spell:402174"]={originalName="Penance",translatedName="ชื่อเฉพาะ",
                lines={{source="Canonical description.",target="คำอธิบาย"}},reviewStatus="VERIFIED"}
            assert(S.Context(tip,data).key=="spell:402174" and outcome()=="text-mismatch")
        ''')

    def test_user_reported_paladin_tooltips_use_packaged_thai_and_preserve_visible_values(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={None=0,SpellDescription=34}
            local prefix="Fills the Paladin with holy spirit for 30 sec, granting each melee attack an additional "
            local suffix=" Holy damage.  Slower weapons cause more Holy damage per swing.  " ..
                "Only one Seal can be active on the Paladin at any one time."
            local judged="Unleashing this Seal's energy will cause 28 to 31 Holy damage to an enemy."
            local function card(id,name,...)
                data={type=1,id=id,lines={{leftText=name}}}
                for _,text in ipairs({...}) do
                    table.insert(data.lines,{type=34,lineIndex=#data.lines+1,leftText=text})
                end
                info={getterName="GetAction",getterArgs={6},tooltipData=data}
            end
            function GetActionInfo(slot) assert(slot==6);return "spell",data.id end
            local function region(text) return {IsShown=function() return true end,GetText=function() return text end} end
            function tip:GetLeftLine(i) return region(data.lines[i].leftText) end
            function tip:GetRightLine() end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            card(20287,"Seal of Righteousness",prefix.."3 to 10"..suffix,judged)
            assert(outcome()=="shown" and bodySeen:find("3 ถึง 10 หน่วย",1,true))
            assert(bodySeen:find("28 ถึง 31 หน่วย",1,true) and not bodySeen:find("พลังเวท",1,true))
            data.lines[3]=nil;assert(outcome()=="text-mismatch")
            card(20287,"Seal of Righteousness",prefix.."3 to 10"..suffix.."\r\n\r\n"..judged)
            assert(outcome()=="shown")
            for id=20288,20293 do
                local rank=id-20285
                local melee=rank.." to "..(rank+9)
                local judgement="Unleashing this Seal's energy will cause "..(rank+30).." to "..(rank+35)..
                    " Holy damage to an enemy."
                card(id,"Seal of Righteousness",prefix..melee..suffix,judgement)
                assert(outcome()=="shown" and bodySeen:find(rank.." ถึง "..(rank+9).." หน่วย",1,true))
                assert(bodySeen:find((rank+30).." ถึง "..(rank+35).." หน่วย",1,true))
                data.lines[3].leftText="Different Judgement effect."
                assert(outcome()=="text-mismatch")
            end
            card(25740,"Seal of Righteousness",prefix.."3 to 10"..suffix,judged)
            assert(outcome()=="missing")
            card(20287,"Seal of Righteousness",
                prefix.."(4 + 7.7% of Holy Spell Power) to (13 + 12% of Holy Spell Power)"..suffix,judged)
            assert(outcome()=="shown" and bodySeen:find("7.7% ของพลังเวทศักดิ์สิทธิ์",1,true))
            card(19740,"Blessing of Might","Places a Blessing on the friendly target, increasing melee attack power " ..
                "by 14 for 1 hour.  Players may only have one Blessing on them per Paladin at any one time.")
            assert(outcome()=="shown" and bodySeen:find("14 หน่วยเป็นเวลา 1 ชั่วโมง",1,true))
            assert(S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_rank_one_seal_cast_ids_require_their_complete_visible_description(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={None=0,SpellDescription=34}
            local title="Seal of Righteousness"
            local first="Fills the Paladin with holy spirit for 30 sec, granting each melee attack an additional " ..
                "0 to 9 Holy damage. Slower weapons cause more Holy damage per swing. " ..
                "Only one Seal can be active on the Paladin at any one time."
            local judgement="Unleashing this Seal's energy will cause 25 to 27 Holy damage to an enemy."
            local shown,actionID
            local function card(sid,...)
                actionID=sid
                data={type=1,id=sid,lines={{leftText=title}}}
                shown={title}
                for _,text in ipairs({...}) do
                    table.insert(data.lines,{type=34,lineIndex=#data.lines+1,leftText=text})
                    table.insert(shown,text)
                end
                info={getterName="GetAction",getterArgs={6},tooltipData=data}
            end
            function GetActionInfo(slot) assert(slot==6);return "spell",actionID end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            card(20154,first)
            assert(outcome()=="shown" and bodySeen:find("0 ถึง 9 หน่วย",1,true))
            assert(bodySeen:find("30 วินาที",1,true) and not bodySeen:find("ปลดปล่อย",1,true))
            shown[3]=judgement
            assert(outcome()=="no-context")
            card(20154,first,judgement)
            assert(outcome()=="text-mismatch")
            card(21084,first)
            assert(outcome()=="text-mismatch")
            S.settings.descriptions=false
            assert(outcome()=="text-mismatch")
            S.settings.descriptions=true
            card(21084,first,judgement)
            assert(outcome()=="shown" and bodySeen:find("25 ถึง 27 หน่วย",1,true))
            actionID=20154;assert(outcome()=="no-context")
            card(21084,first.."\r\n\r\n"..judgement)
            assert(outcome()=="shown")
            card(21084,first:gsub("0 to 9","-1 to 9"),judgement)
            assert(outcome()=="text-mismatch")
            card(21084,first,judgement)
            info.getterName="GetSpellBookItem";info.getterArgs={7,0}
            entry={name=title,spellID=21084,itemType=1,isPassive=false}
            assert(outcome()=="shown" and bodySeen:find("25 ถึง 27 หน่วย",1,true))
            entry.itemType=2;assert(outcome()=="no-context")
            assert(S.stats.errors==0)
        ''')

    def test_pet_trainer_reuses_titles_but_requires_complete_verified_child_body(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/RawText.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellName=13,SpellDescription=34}
            local shown, rank, name, right, id, count = {}, nil, nil, nil, nil, 0
            C_Spell={GetSpellName=function(sid) assert(sid==id);return name end,
                GetSpellSubtext=function(sid) assert(sid==id);return rank end}
            local function card(spellID,text,prefix,tail)
                id=spellID
                local link=S.petTrainingTooltips[id]
                name,rank,right=link.name,link.rank,link.rank
                shown={name}
                data={type=1,id=id,lines={{type=13,leftText=name,lineIndex=1}}}
                if prefix then shown[#shown+1]=prefix end
                if text then
                    shown[#shown+1]=text
                    data.lines[#data.lines+1]={type=34,leftText=text,lineIndex=#shown}
                end
                if tail then shown[#shown+1]=tail end
                info={getterName="GetTrainerService",getterArgs={17},tooltipData=data}
            end
            local function region(text)
                return {IsShown=function() return true end,GetText=function() return text end}
            end
            function tip:GetLeftLine(i) if shown[i] then return region(shown[i]) end end
            function tip:GetRightLine(i) if i==1 and right then return region(right) end end
            function tip:NumLines() return #shown end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function outcome() return S.OnTooltip(tip,data) end
            for _,sid in ipairs({24451,24454,24455,24599,24607,24608,24609,
                1265831,1265833,1265834,1265835,1265836,444682}) do
                card(sid,"Legacy training wording.")
                assert(outcome()=="shown" and bodySeen=="" and titleSeen==S.records[S.petTrainingTooltips[sid].key].translatedName)
                count=count+1
            end
            assert(count==13)
            local function howl(radius, amount)
                return "The wolf howls, increasing the melee attack power of all party or raid members within " ..
                    radius .. " yards by " .. amount .. "."
            end
            for _,sid in ipairs({24599,24607,24608,24609}) do
                card(sid,howl("15","34 to 38"),"Instant")
                assert(outcome()=="shown" and bodySeen:find("15 หลา 34 ถึง 38 หน่วย",1,true))
                assert(not bodySeen:find("คงอยู่",1,true))
                card(sid,howl("18","42").." Lasts 1 min.")
                assert(outcome()=="shown" and bodySeen:find("18 หลา 42 หน่วย คงอยู่ 1 นาที",1,true))
            end
            for _,text in ipairs({howl("0","34"),howl("15","-34"),howl("15","38 to 34"),
                    howl("15","34").." Lasts 0 sec.",howl("15","34").." Additional clause.",
                    "Party members within 15 yards receive an extra 34 damage to their next Physical attack. Lasts 1 min."}) do
                card(24609,text)
                assert(outcome()=="shown" and bodySeen=="" and titleSeen=="หอนเกรี้ยวกราด")
            end
            local function prowl(speed, bonus)
                return "Puts your pet in stealth mode, but slows its movement to "..speed.."% of normal. "..
                    "The first attack from stealth receives a "..bonus.."% bonus to damage. Lasts until cancelled."
            end
            for _,rankData in ipairs({{24451,50},{24454,55},{24455,60}}) do
                card(rankData[1],prowl(rankData[2],37),"Instant")
                assert(outcome()=="shown" and bodySeen:find("เหลือ "..rankData[2].."%",1,true)
                    and bodySeen:find("37%",1,true))
            end
            card(24454,prowl(45,35));assert(outcome()=="shown" and bodySeen=="")
            card(24455,prowl(40,50));assert(outcome()=="shown" and bodySeen=="")
            card(24454,prowl(55,-35));assert(outcome()=="shown" and bodySeen=="")
            local function savage(damage, duration, modifier)
                return "Slash an enemy with razor talons, causing the target to Bleed for "..damage..
                    " damage over "..duration.." and take "..modifier..
                    "% additional damage from Bleed effects for the duration."
            end
            local notice="ดูเงื่อนไขเพิ่มเติมในคำอธิบายเดิม"
            for _,sid in ipairs({1265831,1265833,1265834,1265835,1265836}) do
                card(sid,savage(57,"18 sec",0),"Instant")
                assert(outcome()=="shown" and bodySeen:find("57 หน่วยตลอด 18 วินาที",1,true)
                    and bodySeen:find(notice,1,true) and not bodySeen:find("0%%"))
            end
            card(1265836,savage(57,"18 seconds",0))
            assert(outcome()=="shown" and bodySeen:find(notice,1,true))
            S.settings.original=true
            assert(outcome()=="shown" and bodySeen:find(savage(57,"18 seconds",0),1,true))
            S.settings.original=false
            for _,text in ipairs({savage(57,"18 sec",10),savage(57,"0 sec",0),savage(-57,"18 sec",0),
                    savage(57,"until cancelled",0),savage(57,"18 sec",0).." Additional clause."}) do
                card(1265831,text)
                assert(outcome()=="shown" and bodySeen=="")
            end
            card(1265831,savage(57,"18 sec",0));S.settings.descriptions=false
            assert(outcome()=="shown" and bodySeen=="")
            S.settings.descriptions=true
            local function lava(damage, slow, time, target)
                return "Breathes molten lava at "..(target or "the target")..", instantly dealing "..damage..
                    " Fire damage and reducing the target's casting speed by "..slow.."% for "..time.."."
            end
            card(444682,lava("99 to 113","25","10 sec"),"Instant")
            assert(outcome()=="shown" and titleSeen=="ลมหายใจลาวา"
                and bodySeen:find("99 ถึง 113 หน่วยทันที",1,true)
                and bodySeen:find("25% เป็นเวลา 10 วินาที",1,true))
            local exactLava=lava("106","25","10 seconds")
            card(444682,exactLava)
            S.settings.original=true
            assert(outcome()=="shown" and bodySeen:find(exactLava,1,true))
            S.settings.original=false
            for _,text in ipairs({lava("0","25","10 sec"),lava("-99 to 113","25","10 sec"),
                    lava("113 to 99","25","10 sec"),lava("106","$25","10 sec"),
                    lava("106","20","10 sec"),lava("106","25","12 sec"),exactLava.." More text."}) do
                card(444682,text)
                assert(outcome()=="shown" and bodySeen=="")
            end
            card(444682,exactLava,nil,"Unexpected tail")
            assert(outcome()=="shown" and bodySeen=="")
            card(444682,exactLava);rank="Rank 1"
            assert(outcome()=="no-context")
            card(444682,exactLava);info.getterName="GetAction"
            assert(outcome()=="missing")
            card(444682,lava("106","25","10 sec","2 nearby enemies"))
            assert(outcome()=="shown" and bodySeen:find("ศัตรูใกล้เคียง 2 ตัว",1,true))

            local howl="The wolf howls, increasing the melee attack power of all party or raid members within 21 yards by 64. Lasts 12 sec."
            card(24607,howl)
            assert(outcome()=="shown" and bodySeen:find("พลังโจมตีระยะประชิด",1,true)
                and bodySeen:find("21 หลา",1,true) and bodySeen:find("64 หน่วย",1,true))
            card(24607,howl,"Legacy wording");assert(outcome()=="shown" and bodySeen=="")
            card(24607,howl,nil,"Unexpected tail");assert(outcome()=="shown" and bodySeen=="")
            card(24607,"Party members within 21 yards receive an extra 64 damage to their next Physical attack. Lasts 12 sec.")
            assert(outcome()=="shown" and bodySeen=="")
            card(24607,howl);right="Rank 4";assert(outcome()=="no-context")
            card(24607,howl);rank="Rank 4";assert(outcome()=="no-context")
            card(24607,howl);name="Unknown";assert(outcome()=="no-context")
            card(24607,howl);primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            card(24607,howl);info.getterName="GetAction";assert(outcome()=="missing")
            card(24607,howl);data.id=nil;assert(outcome()=="no-context")
            card(24607,howl);S.settings.descriptions=false
            assert(outcome()=="shown" and bodySeen=="" and S.stats.errors==0)
        ''')

    def test_bear_and_defensive_stance_translate_only_the_reviewed_native_aura_scope(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/RawText.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local auraID, shown = nil, {}
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="player" and instance==23);return {spellId=auraID}
            end}
            local function card(sid,name,text,tail)
                auraID=sid
                shown={name,text}
                if tail then shown[3]=tail end
                data={type=7,id=23,lines={{leftText=name},{leftText=text}}}
                info={getterName="GetUnitBuffByAuraInstanceID",getterArgs={"player",23},tooltipData=data}
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function outcome() return S.OnTooltip(tip,data) end
            local bearPrefix="Immune to Polymorph effects. Increases Attack Power by 127, Armor contribution from items by 182%"
            local bear=bearPrefix..", and Health by 271."
            card(5487,"Bear Form",bear)
            assert(outcome()=="shown" and titleSeen=="ร่างหมี"
                and bodySeen:find("พลังโจมตี 127 หน่วย",1,true) and bodySeen:find("เกราะที่ได้จากไอเทม 182%",1,true)
                and bodySeen:find("ดูค่าพลังชีวิตในคำอธิบายเดิม",1,true)
                and not bodySeen:find("271",1,true) and shown[2]==bear)
            S.settings.original=true
            assert(outcome()=="shown" and bodySeen:find(bear,1,true));S.settings.original=false
            card(5487,"Bear Form",bearPrefix..".");assert(outcome()=="text-mismatch")
            card(5487,"Bear Form",bearPrefix..", and Health by -271.");assert(outcome()=="text-mismatch")
            card(5487,"Bear Form",bear,"Another effect.");assert(outcome()=="text-mismatch")
            card(5487,"Bear Form",bear);auraID=9634;assert(outcome()=="text-mismatch")
            local function stance(threat)
                return "A defensive combat stance. Decreases damage taken by 10.5% and damage caused by 11%. "..
                    "Increases all threat generated by "..threat.."%."
            end
            card(71,"Defensive Stance",stance("80.0"),"1 second remaining")
            assert(outcome()=="shown" and titleSeen=="ท่าตั้งรับ"
                and bodySeen:find("ลดความเสียหายที่ได้รับ 10.5%",1,true)
                and bodySeen:find("ความเสียหายที่สร้าง 11%",1,true) and bodySeen:find("80.0%",1,true))
            for _,bad in ipairs({"95","-80","+80","80 to 90","0"}) do
                card(71,"Defensive Stance",stance(bad))
                assert(outcome()=="text-mismatch" and not S.reader:IsShown())
            end
            card(71,"Defensive Stance",stance("80"));primary={tooltipData=data}
            assert(outcome()=="no-context");primary=nil
            S.settings.descriptions=false
            card(71,"Defensive Stance",stance("95"));assert(outcome()=="text-mismatch")
            card(5487,"Bear Form",bear);assert(outcome()=="shown" and bodySeen=="" and S.stats.errors==0)
        ''')

    def test_not_there_aura_only_translates_the_next_damage_spell_and_keeps_the_sign(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/RawText.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local auraID,shown=28762,{}
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="player" and instance==19);return {spellId=auraID}
            end}
            local function card(amount,affected,tail)
                shown={"Not There","Reduces the threat generated by your next "..
                    (affected or "damage spell").." by "..amount.."%."}
                if tail then shown[3]=tail end
                data={type=7,id=19,lines={{leftText=shown[1]},{leftText=shown[2]}}}
                info={getterName="GetUnitBuffByAuraInstanceID",getterArgs={"player",19},tooltipData=data}
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function outcome() return S.OnTooltip(tip,data) end
            card("100",nil,"1 second remaining")
            assert(outcome()=="shown" and titleSeen=="เลือนหาย"
                and bodySeen=="ลดค่าความคุกคามจากเวทสร้างความเสียหายครั้งถัดไปลง 100%")
            card("-100.0")
            assert(outcome()=="shown" and bodySeen=="ค่าความคุกคามจากเวทสร้างความเสียหายครั้งถัดไปเปลี่ยนไป -100.0%")
            card("100","spell");assert(outcome()=="text-mismatch")
            for _,bad in ipairs({"--100","+100","-90","0","90 to 100"}) do
                card(bad);assert(outcome()=="text-mismatch" and not S.reader:IsShown())
            end
            card("100",nil,"Another effect.");assert(outcome()=="text-mismatch")
            card("100");auraID=28761;assert(outcome()=="missing");auraID=28762
            card("100");primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            S.settings.descriptions=false
            card("0");assert(outcome()=="text-mismatch")
            card("100");assert(outcome()=="shown" and bodySeen=="" and S.stats.errors==0)
        ''')

    def test_righteous_fury_aura_requires_complete_visible_text_and_unsigned_reduction(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/RawText.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local unit, auraID, shown, right = "player", 25780, {}, nil
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(token, instance)
                assert(token==unit and instance==71);return {spellId=auraID}
            end}
            local base="Increases all threat generated by 34%, and all threat generated by your Holy attacks by an additional 91%."
            local function card(...)
                shown={"Righteous Fury",...}
                data={type=7,id=71,lines={{leftText="Righteous Fury"}}}
                for i=2,#shown do data.lines[i]={leftText=shown[i]} end
                info={getterName="GetUnitBuffByAuraInstanceID",getterArgs={unit,71},tooltipData=data}
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine(i)
                if right and i==2 then return {IsShown=function() return true end,GetText=function() return right end} end
            end
            function tip:NumLines() return #shown end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function outcome() return S.OnTooltip(tip,data) end
            card(base,"29 minutes remaining")
            assert(outcome()=="shown" and titleSeen=="โทสะชอบธรรม"
                and bodySeen:find("34%",1,true) and bodySeen:find("91%",1,true)
                and not bodySeen:find("ลดความเสียหาย",1,true))
            unit="target"
            for _,value in ipairs({"3","6.0","9"}) do
                card(base,"Reduces damage taken by "..value.."%.","1 second remaining")
                assert(outcome()=="shown" and bodySeen:find("ลดความเสียหายที่ได้รับ "..value.."%",1,true))
            end
            card(base.." Reduces damage taken by 9%.");assert(outcome()=="shown")
            for _,value in ipairs({"-3","+3","0","4","3 to 9"}) do
                card(base,"Reduces damage taken by "..value.."%.")
                assert(outcome()=="text-mismatch" and not S.reader:IsShown())
            end
            card((base:gsub("34%%","-34%%")));assert(outcome()=="text-mismatch")
            card(base,"Another effect.");assert(outcome()=="text-mismatch")
            card(base,"29 minutes remaining","Another effect.");assert(outcome()=="text-mismatch")
            card(base);auraID=25781;assert(outcome()=="missing");auraID=25780
            card(base);right="Unexpected value";assert(outcome()=="no-context");right=nil
            card(base);primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            card(base);shown[1]="Other buff";assert(outcome()=="no-context")
            S.settings.descriptions=false
            card(base,"Reduces damage taken by -3%.");assert(outcome()=="text-mismatch")
            card(base);assert(outcome()=="shown" and bodySeen=="" and S.stats.errors==0)
        ''')

    def test_instant_poison_rank_four_requires_the_complete_native_130_charge_text(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/RawText.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            local title="Instant Poison IV"
            local first="Coats a weapon with poison that lasts for 30 minutes."
            local effect="Each strike has a 20% chance of poisoning the enemy which instantly inflicts 46 to 58 Nature damage."
            local correct=effect.." 130 charges."
            local shown
            local function card(...)
                data={type=1,id=11341,lines={{leftText=title}}}
                shown={title}
                for _,line in ipairs({...}) do
                    shown[#shown+1]=line
                    data.lines[#data.lines+1]={type=34,lineIndex=#shown,leftText=line}
                end
                info={getterName="GetSpellBookItem",getterArgs={7,0},tooltipData=data}
                entry={name=title,spellID=11341,itemType=1,isPassive=false}
            end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            function S.RememberLongText(heading,text) titleSeen,bodySeen=heading,text end
            local function outcome() return S.OnTooltip(tip,data) end
            card(first,correct)
            assert(outcome()=="shown" and titleSeen=="พิษฉับพลัน" and bodySeen:find("130 ชาร์จ",1,true))
            assert(bodySeen:find("46 ถึง 58",1,true) and bodySeen:find("20%",1,true))
            card(first.."\r\n"..correct);assert(outcome()=="shown")
            info.getterName="GetAction";info.getterArgs={6}
            function GetActionInfo() return "spell",11341 end
            assert(outcome()=="shown")
            for _,charge in ipairs({"1800","1,800","131"}) do
                card(first,effect.." "..charge.." charges.")
                assert(outcome()=="text-mismatch" and not S.reader:IsShown())
                assert(shown[3]==effect.." "..charge.." charges.")
            end
            card(first:gsub("30","31"),correct);assert(outcome()=="text-mismatch")
            card(first,correct,"Unexpected extra line.");assert(outcome()=="no-context")
            card(first,correct);entry.spellID=11338;assert(outcome()=="no-context")
            title="Instant Poison";card(first,correct);assert(outcome()=="text-mismatch")
            title="Instant Poison IV"
            S.settings.descriptions=false
            card(first,effect.." 1800 charges.");assert(outcome()=="text-mismatch")
            card(first,correct);assert(outcome()=="shown" and bodySeen=="" and S.stats.errors==0)
        ''')

    def test_holy_nova_ranks_translate_only_verified_paragraph_of_exact_native_tooltip(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            local title="Holy Nova"
            local base="Causes an explosion of holy light around the caster, causing 49 to 57 Holy damage " ..
                "to all enemy targets within 11 yards and healing all party members within 12 yards " ..
                "for 81 to 93. These effects cause no threat."
            local proc="Each time Holy Fire deals damage, you have a 5% chance for your next Holy Nova to cost no Mana."
            local notice="ดูเงื่อนไขเพิ่มเติมในคำอธิบายเดิม"
            local shown, actionID
            local function card(sid,...)
                actionID=sid
                data={type=1,id=sid,lines={{leftText=title}}}
                shown={title}
                for _,line in ipairs({...}) do
                    shown[#shown+1]=line
                    data.lines[#data.lines+1]={type=34,lineIndex=#shown,leftText=line}
                end
                info={getterName="GetAction",getterArgs={6},tooltipData=data}
            end
            function GetActionInfo(slot) assert(slot==6);return "spell",actionID end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            for _,id in ipairs({15430,15431,27799,27800,27801}) do
                card(id,base,proc)
                assert(outcome()=="shown" and bodySeen:find("49 ถึง 57",1,true)
                    and bodySeen:find("81 ถึง 93",1,true) and bodySeen:find("11 หลา",1,true)
                    and bodySeen:find("12 หลา",1,true) and bodySeen:find(notice,1,true))
                assert(not bodySeen:find("5%",1,true) and shown[3]==proc)
            end
            card(27801,base.."\r\n\r\n"..proc);assert(outcome()=="shown")
            info.getterName="GetSpellBookItem";info.getterArgs={7,0}
            entry={name=title,spellID=27801,itemType=1,isPassive=false}
            assert(outcome()=="shown");entry.spellID=27800;assert(outcome()=="no-context")
            card(27801,base);assert(outcome()=="no-context" and not S.reader:IsShown())
            card(27801,base,proc:gsub("5%%","6%%"));assert(outcome()=="no-context")
            card(27801,base,proc,"Unexpected extra clause.");assert(outcome()=="no-context")
            card(27801,base.." Unexpected extra clause.",proc);assert(outcome()=="text-mismatch")
            S.settings.descriptions=false
            card(27801,base,proc);assert(outcome()=="shown" and bodySeen=="")
            card(27801,base:gsub("no threat","threat"),proc);assert(outcome()=="text-mismatch")
            assert(S.stats.errors==0)
        ''')

    def test_seal_of_command_uses_both_native_judgement_values_for_each_cast_rank(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            local title="Seal of Command"
            local first="Gives the Paladin a chance to deal additional Holy damage equal to 70% " ..
                "of normal weapon damage. Only one Seal can be active on the Paladin at any one time. Lasts 30 sec."
            local function judgement(normal, disabled)
                return "Unleashing this Seal's energy will judge an enemy, instantly causing " .. normal ..
                    " Holy damage, " .. disabled .. " if the target is stunned or incapacitated."
            end
            local function card(sid,...)
                data={type=1,id=sid,lines={{leftText=title}}}
                for _,text in ipairs({...}) do
                    table.insert(data.lines,{type=34,lineIndex=#data.lines+1,leftText=text})
                end
                info={getterName="GetAction",getterArgs={6},tooltipData=data}
            end
            function GetActionInfo(slot) assert(slot==6);return "spell",data.id end
            function tip:GetLeftLine(i)
                local line=data.lines[i]
                if line then
                    return {IsShown=function() return true end,GetText=function() return line.leftText end}
                end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #data.lines end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            for rank,sid in ipairs({20375,20915,20918,20919,20920}) do
                local normal=(65+rank).." to "..(72+rank)
                local disabled=(135+rank).." to "..(148+rank)
                card(sid,first,judgement(normal,disabled))
                assert(outcome()=="shown" and bodySeen:find("70%",1,true) and bodySeen:find("30 วินาที",1,true))
                assert(bodySeen:find((65+rank).." ถึง "..(72+rank).." หน่วย",1,true))
                assert(bodySeen:find((135+rank).." ถึง "..(148+rank).." หน่วย",1,true))
            end
            local footer=judgement("81","144 to 152")
            card(20375,first.."\r\n\r\n"..footer)
            info.getterName="GetSpellBookItem";info.getterArgs={7,0}
            entry={name=title,spellID=20375,itemType=1,isPassive=false}
            assert(outcome()=="shown" and bodySeen:find("81 หน่วย",1,true))
            assert(bodySeen:find("144 ถึง 152 หน่วย",1,true))
            entry.spellID=20915;assert(outcome()=="no-context")
            card(20375,first)
            S.settings.descriptions=false
            assert(outcome()=="text-mismatch")
            S.settings.descriptions=true
            card(20375,first,(footer:gsub("stunned or incapacitated","silenced")))
            assert(outcome()=="text-mismatch")
            card(20375,first,footer)
            info.getterName="GetSpellByID";assert(outcome()=="no-context")
            card(20424,first,footer);assert(outcome()=="missing")
            assert(not S.records["spell:20375"].requireCompleteTalentBody and S.stats.errors==0)
        ''')

    def test_seal_of_command_talent_uses_completed_trait_tooltip_and_exact_owner(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            local title="Seal of Command"
            local entryID,nodeID,definitionSpell=130425,105696,20375
            local ranksPurchased=0
            local first="Gives the Paladin a chance to deal additional Holy damage equal to 70% " ..
                "of normal weapon damage. Only one Seal can be active on the Paladin at any one time. Lasts 30 sec."
            local footer="Unleashing this Seal's energy will judge an enemy, instantly causing 46 to 51 Holy damage, " ..
                "93 to 101 if the target is stunned or incapacitated."
            local owner={GetEntryID=function() return entryID end,GetNodeID=function() return nodeID end,
                GetName=function() return title end,GetTalentFrame=function() return {GetConfigID=function() return 7 end} end,
                GetTooltipEntryInfo=function()
                    return {currEntryInfo={entryID=130425,rank=ranksPurchased},ranksPurchased=ranksPurchased}
                end}
            C_Traits={GetEntryInfo=function(config,id)
                    assert(config==7 and id==130425);return {definitionID=502}
                end,GetDefinitionInfo=function(def)
                    assert(def==502);return {spellID=definitionSpell}
                end}
            local shown={title,"Rank 0/1",first,"",footer}
            function tip:GetOwner() return owner end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #shown end
            local heading,body
            function S.RememberLongText(name,text) heading,body=name,text end
            data={type=1,id=20375,lines={{type=34,lineIndex=3,leftText=first},{type=34,lineIndex=5,leftText=footer}}}
            info={getterName="GetTraitEntry",getterArgs={130425,0},tooltipData=data}
            local postCall,talentCallback
            TooltipDataProcessor={AllTypes=99,AddTooltipPostCall=function(_,callback) postCall=callback end}
            EventRegistry={RegisterCallback=function(_,event,callback)
                assert(event=="TalentDisplay.TooltipCreated");talentCallback=callback
            end}
            S.RegisterTooltips()
            tip:Show()
            postCall(tip,data);assert(not S.reader:IsShown())
            talentCallback(S,{},tip);assert(not S.reader:IsShown())
            talentCallback(S,owner,tip);assert(S.reader:IsShown() and heading:find("ตัวอย่างแรงก์ 1",1,true))
            assert(body:find("46 ถึง 51 หน่วย",1,true) and body:find("93 ถึง 101 หน่วย",1,true))
            ranksPurchased=1;shown[2]="Rank 1/1";info.getterArgs[2]=1
            shown[3]=first.."\r\n\r\n"..footer
            data.lines={{type=34,lineIndex=3,leftText=shown[3]}}
            shown[4]=nil;shown[5]=nil
            assert(S.OnTooltip(tip,data,nil,true)=="shown" and heading:find("แรงก์ 1",1,true))
            assert(not heading:find("ตัวอย่าง",1,true))
            local function rejected() assert(S.OnTooltip(tip,data,nil,true)=="no-context") end
            nodeID=105697;rejected();nodeID=105696
            entryID=130426;rejected();entryID=130425
            data.id=20915;rejected();data.id=20375
            data.lines[1].type=0;rejected();data.lines[1].type=34
            shown[4]="Unrecognized extra effect.";rejected();shown[4]=nil
            shown[3]=first;data.lines[1].leftText=first
            S.settings.descriptions=false
            assert(S.OnTooltip(tip,data,nil,true)=="text-mismatch")
            assert(not S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_mage_hunter_casts_match_complete_native_text_and_preserve_values(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            local function card(sid,name,...)
                data={type=1,id=sid,lines={{leftText=name}}}
                for _,text in ipairs({...}) do
                    table.insert(data.lines,{type=34,lineIndex=#data.lines+1,leftText=text})
                end
                info={getterName="GetAction",getterArgs={6},tooltipData=data}
            end
            function GetActionInfo(slot) assert(slot==6);return "spell",data.id end
            function tip:GetLeftLine(i)
                local line=data.lines[i]
                if line then
                    return {IsShown=function() return true end,GetText=function() return line.leftText end}
                end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #data.lines end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            local footer="Conjured items disappear if logged out for more than 15 minutes."
            for _,owner in ipairs({"his","her"}) do
                for _,amount in ipairs({1,19}) do
                    local unit=amount==1 and "bottle" or "bottles"
                    local first="Conjures "..amount.." "..unit.." of mountain spring water, " ..
                        "providing the mage and "..owner.." allies with something to drink."
                    card(468766,"Conjure Water",first,footer)
                    assert(outcome()=="shown" and bodySeen:find(amount.." ขวด",1,true))
                    assert(bodySeen:find("นานกว่า 15 นาที",1,true))
                end
            end
            data.lines[3].leftText="Conjured items disappear after 10 minutes."
            assert(outcome()=="text-mismatch")
            data.lines[3].leftText=footer
            info.getterName="GetSpellBookItem";info.getterArgs={7,0}
            entry={name="Conjure Water",spellID=468766,itemType=1,isPassive=false}
            assert(outcome()=="shown")
            entry.spellID=10140;assert(outcome()=="no-context")

            local viper="The hunter takes on the aspect of the viper, causing your ranged and melee auto " ..
                "attacks to regenerate mana but reducing your total damage done by 9%. In addition, " ..
                "you gain 11% of maximum mana every 4 sec. Mana gained is based on the speed of your weapon. " ..
                "Only one Aspect can be active at a time."
            card(415423,"Aspect of the Viper",viper)
            assert(outcome()=="shown" and bodySeen:find("ลง 9%",1,true) and bodySeen:find("11%",1,true))
            assert(bodySeen:find("ทุก 4 วินาที",1,true))
            data.lines[2].leftText=viper:gsub("by 9%%","by -9%%")
            S.settings.descriptions=false;assert(outcome()=="text-mismatch");S.settings.descriptions=true
            for _,sid in ipairs({34074,415424,415718}) do
                card(sid,"Aspect of the Viper",viper);assert(outcome()=="missing")
            end
            local falcon="The hunter takes on the aspects of a Falcon, increasing melee and ranged " ..
                "Attack Power by the same amount as their highest rank of Aspect of the Hawk."
            local perk="While Aspect of the Falcon is active, the Improved Aspect of the Hawk talent can " ..
                "now proc from and benefit melee attacks. Only one Aspect can be active at a time."
            card(469145,"Aspect of the Falcon",falcon,perk)
            assert(outcome()=="shown" and bodySeen:find("วิถีเหยี่ยวแรงก์สูงสุด",1,true))
            data.lines[3]=nil;assert(outcome()=="text-mismatch")
            card(469144,"Aspect of the Falcon",falcon,perk);assert(outcome()=="missing")

            local lion="The hunter invokes the heart of a lion, increasing total stats by 10% and Attack " ..
                "Power by 243 for all nearby allies, and increasing total stats for the Hunter by an additional 12%."
            card(409580,"Heart of the Lion",lion)
            assert(outcome()=="shown" and bodySeen:find("243 หน่วย",1,true) and bodySeen:find("อีก 12%",1,true))
            card(409583,"Heart of the Lion",lion);assert(outcome()=="missing")
            assert(S.stats.errors==0)
        ''')

    def test_hunter_auras_render_exact_self_and_ally_effects(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local auraID,expectedUnit
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit==expectedUnit and instance==12)
                return {spellId=auraID}
            end}
            local function buff(sid,unit,title,description)
                auraID,expectedUnit=sid,unit
                -- Native aura identity comes from C_UnitAuras, not data.id.
                data={type=7,id=999,lines={{leftText=title},{leftText=description}}}
                info={getterName="GetUnitBuffByAuraInstanceID",getterArgs={unit,12,"HELPFUL"},tooltipData=data}
            end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            local viper="Your ranged and melee auto attacks regenerate a percentage of your base mana, " ..
                "but your total damage done is reduced by 9%. In addition, you gain 11% of maximum mana every 4 sec."
            buff(415423,"player","Aspect of the Viper",viper)
            assert(outcome()=="shown" and bodySeen:find("มานาพื้นฐาน",1,true))
            assert(bodySeen:find("มานาสูงสุดทุก 4 วินาที",1,true) and bodySeen:find("ลง 9%",1,true))
            data.lines[2].leftText=viper:gsub("by 9%%","by -9%%")
            S.settings.descriptions=false;assert(outcome()=="text-mismatch");S.settings.descriptions=true
            data.lines[2].leftText=viper:gsub("base mana","maximum mana")
            assert(outcome()=="text-mismatch")
            buff(469145,"player","Aspect of the Falcon","Increases Attack Power by 257.")
            assert(outcome()=="shown" and bodySeen:find("257 หน่วย",1,true))
            local own="Increases Hunter's stats by 12%."
            local party="Increases stats by 10% and Attack Power by 243."
            buff(409580,"player","Heart of the Lion",own)
            assert(outcome()=="shown" and bodySeen:find("ฮันเตอร์ 12%",1,true))
            assert(not bodySeen:find("พลังโจมตี",1,true))
            buff(409583,"party2","Heart of the Lion",party)
            assert(outcome()=="shown" and bodySeen:find("10% และพลังโจมตี 243 หน่วย",1,true))
            auraID=409580;assert(outcome()=="text-mismatch")
            buff(409583,"party2","Heart of the Lion",own)
            assert(outcome()=="text-mismatch")
            buff(469144,"player","Quick Strikes","Melee attack speed increased by 28%.")
            assert(outcome()=="shown" and bodySeen:find("ระยะประชิดเพิ่มขึ้น 28%",1,true))
            auraID=469145;assert(outcome()=="text-mismatch")
            assert(S.stats.errors==0)
        ''')

    def test_trap_area_debuffs_and_seal_buff_use_their_own_effect_text(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            local auraID
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert((unit=="target" or unit=="player") and instance==51)
                return {spellId=auraID}
            end}
            local function aura(id,getter,unit,name,description)
                auraID=id
                data={type=7,id=999,lines={{leftText=name},{leftText=description}}}
                info={getterName=getter,getterArgs={unit,51},tooltipData=data}
            end
            local function debuff(id,name,description)
                aura(id,"GetUnitDebuffByAuraInstanceID","target",name,description)
            end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            debuff(13810,"Frost Trap","Movement speed slowed by 55%.")
            assert(outcome()=="shown" and bodySeen:find("ลดลง 55%",1,true))
            data.lines[2].leftText="Movement speed slowed by -55%."
            S.settings.descriptions=false;assert(outcome()=="text-mismatch");S.settings.descriptions=true
            auraID=14207;assert(outcome()=="missing")
            for rank,id in ipairs({13812,14314,14315}) do
                local damage,period=14+rank,rank+1
                debuff(id,"Explosive Trap",damage.." Fire damage every "..period.." seconds.")
                assert(outcome()=="shown" and bodySeen:find(damage.." หน่วยทุก "..period.." วินาที",1,true))
                data.lines[2].leftText=damage.." Frost damage every "..period.." seconds."
                assert(outcome()=="text-mismatch")
            end
            auraID=13813;assert(outcome()=="missing")
            aura(21084,"GetUnitBuffByAuraInstanceID","player","Seal of Righteousness",
                "Melee attacks cause an additional 0 to 9 Holy damage.")
            assert(outcome()=="shown" and bodySeen:find("0 ถึง 9 หน่วย",1,true))
            assert(not bodySeen:find("ปลดปล่อย",1,true))
            data.lines[2].leftText="Unleashing this Seal's energy will cause 25 to 27 Holy damage to an enemy."
            assert(outcome()=="text-mismatch")
            assert(S.stats.errors==0)
        ''')

    def test_vindication_matches_each_native_rank_and_its_separate_debuff(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            Enum.TooltipDataType.UnitAura=7
            local title="Vindication"
            local nodeID=105702
            local shown={title,"Rank 0/3"}
            local function english(amount,seconds)
                return "Gives your damaging melee attacks a chance to reduce the target's Attack Power by " ..
                    amount .. " for " .. seconds .. " sec."
            end
            local owner={GetEntryID=function() return 130431 end,GetNodeID=function() return nodeID end,
                GetName=function() return title end,GetTalentFrame=function() return {GetConfigID=function() return 7 end} end,
                GetTooltipEntryInfo=function()
                    return {currEntryInfo={entryID=130431,rank=0},ranksPurchased=0}
                end}
            C_Traits={GetEntryInfo=function(config,id)
                    assert(config==7 and id==130431);return {definitionID=135232}
                end,GetDefinitionInfo=function(def)
                    assert(def==135232);return {spellID=9452}
                end}
            function tip:GetOwner() return owner end
            function tip:GetLeftLine(i)
                if shown[i] then return {IsShown=function() return true end,GetText=function() return shown[i] end} end
            end
            function tip:GetRightLine() end
            local heading
            function S.RememberLongText(name,text) heading,bodySeen=name,text end
            local function rankPayload(rank,index,text)
                shown[index]=text
                data={type=1,id=9452,lines={{type=34,lineIndex=index,leftText=text}}}
                info={getterName="GetTraitEntry",getterArgs={130431,rank},tooltipData=data}
            end
            local function outcome() return S.OnTooltip(tip,data) end
            rankPayload(0,3,english(67,30))
            assert(outcome()=="shown" and heading:find("ตัวอย่างแรงก์ 1",1,true))
            assert(bodySeen:find("67 หน่วยเป็นเวลา 30 วินาที",1,true))
            for rank=1,3 do
                local index=2*rank+1
                local amount,seconds=43*rank,20+rank
                rankPayload(rank,index,english(amount,seconds))
                assert(outcome()=="shown" and heading:find("แรงก์ "..rank,1,true))
                assert(bodySeen:find(amount.." หน่วยเป็นเวลา "..seconds.." วินาที",1,true))
            end
            data.lines[2]={type=34,lineIndex=9,leftText=english(99,25)};shown[9]=data.lines[2].leftText
            assert(outcome()=="no-context");data.lines[2]=nil
            nodeID=105703;assert(outcome()=="no-context");nodeID=105702
            data.id=67;assert(outcome()=="no-context");data.id=9452
            rankPayload(3,7,english(-129,23))
            S.settings.descriptions=false;assert(outcome()=="text-mismatch")
            rankPayload(3,7,"Gives the Paladin's damaging melee attacks a chance to reduce the target's " ..
                "Strength and Agility by 5% for 10 sec.")
            assert(outcome()=="text-mismatch");S.settings.descriptions=true
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="target" and instance==54);return {spellId=440667}
            end}
            data={type=7,id=999,lines={{leftText=title},{leftText="Attack Power reduced by 138."}}}
            info={getterName="GetUnitDebuffByAuraInstanceID",getterArgs={"target",54},tooltipData=data}
            assert(outcome()=="shown" and bodySeen=="พลังโจมตีลดลง 138 หน่วย")
            data.lines[2].leftText="Attack Power increased by 3%."
            assert(outcome()=="text-mismatch" and S.stats.errors==0)
        ''')

    def test_shank_matches_each_complete_conditional_tooltip_for_both_ranks(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            local prefix="Instantly strike with your off-hand weapon, dealing 51% weapon damage"
            local venom=", increasing your Poison damage dealt by 31% and your chance to apply Poisons by 21% for 7 sec,"
            local combo="  39% Chance to award 2 Combo Points."
            local function body(energy,hasVenom,hasCombo)
                return prefix..(hasVenom and venom or "").." and generating "..energy.." Energy." ..
                    (hasCombo and combo or "").." Shank cannot Miss."
            end
            local function tooltip(id,getter,text)
                data={type=1,id=id,lines={{leftText="Shank"},{leftText=text}}}
                info={getterName=getter,getterArgs={7,0},tooltipData=data}
                entry={spellID=id,name="Shank",itemType=1,isPassive=false}
            end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            for rank,id in ipairs({1329283,1329549}) do
                local energy=rank==1 and 18 or 27
                for _,hasVenom in ipairs({false,true}) do
                    for _,hasCombo in ipairs({false,true}) do
                        local getter=rank==1 and "GetAction" or "GetSpellBookItem"
                        tooltip(id,getter,body(energy,hasVenom,hasCombo))
                        assert(outcome()=="shown" and bodySeen:find("พลังงาน "..energy.." หน่วย",1,true))
                        assert(bodySeen:find("51% ของความเสียหายอาวุธ",1,true))
                        assert(bodySeen:find("แทงมือรองไม่สามารถโจมตีพลาดได้",1,true))
                        assert((bodySeen:find("31% และเพิ่มโอกาสทำให้ติดพิษ 21% เป็นเวลา 7 วินาที",1,true)~=nil)==hasVenom)
                        assert((bodySeen:find("39% ที่จะได้รับ 2 แต้มคอมโบ",1,true)~=nil)==hasCombo)
                    end
                end
            end
            tooltip(1329283,"GetSpellByID",body(15,false,false));assert(outcome()=="shown")
            tooltip(1329283,"GetAction",(body(15,true,true):gsub("by 31%%","by -31%%")))
            S.settings.descriptions=false;assert(outcome()=="text-mismatch");S.settings.descriptions=true
            tooltip(1329549,"GetSpellBookItem",(body(25,true,true):gsub("2 Combo Points","3 Combo Points")))
            assert(outcome()=="text-mismatch")
            tooltip(1329549,"GetAction",prefix..venom);assert(outcome()=="text-mismatch")
            tooltip(15248,"GetSpellByID",body(15,true,true));assert(outcome()=="missing")
            assert(S.stats.errors==0)
        ''')

    def test_conditional_cast_cohort_uses_exact_branches_and_native_values(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            local function card(id,name,text)
                data={type=1,id=id,lines={{leftText=name},{leftText=text}}}
                info={getterName="GetAction",getterArgs={7},tooltipData=data}
            end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            for _,id in ipairs({543,8457,8458,10223,10225}) do
                card(id,"Fire Ward","Absorbs 163 Fire damage. Lasts 31 sec.")
                assert(outcome()=="shown" and bodySeen:find("163 หน่วย",1,true))
                assert(not bodySeen:find("สะท้อน",1,true))
                data.lines[2].leftText="Absorbs 163 Fire damage and grants a 28% chance to reflect Fire spells and effects. Lasts 31 sec."
                assert(outcome()=="shown" and bodySeen:find("28% ที่จะสะท้อน",1,true))
            end
            for _,id in ipairs({6143,8461,8462,10177,28609}) do
                card(id,"Frost Ward","Absorbs (173 + 12.5% of Frost Spell Power) Frost damage. Lasts 31 sec.")
                assert(outcome()=="shown" and bodySeen:find("(173 + 12.5% ของพลังเวทน้ำแข็ง)",1,true))
                data.lines[2].leftText="Absorbs 192 Frost damage and grants a 27% chance to negate Frost damage. Lasts 31 sec."
                assert(outcome()=="shown" and bodySeen:find("27% ที่จะทำให้ความเสียหายน้ำแข็งไม่มีผล",1,true))
            end
            data.lines[2].leftText="Absorbs (173 + 12.5% of Fire Spell Power) Frost damage. Lasts 31 sec."
            assert(outcome()=="text-mismatch")
            local sap="Incapacitates the target for up to 38 sec. Only works on Humanoids that are not in combat. " ..
                "Any damage taken will break the effect. Only "
            for _,id in ipairs({6770,2070,11297}) do
                for count=1,2 do
                    card(id,"Sap",sap..count..(count==1 and " target" or " targets")..
                        " may be sapped at a time. Does not break Stealth.")
                    assert(outcome()=="shown" and bodySeen:find("เพียง "..count.." ตัว",1,true))
                    assert(bodySeen:find("สูงสุด 38 วินาที",1,true))
                end
            end
            data.lines[2].leftText=sap.."3 targets may be sapped at a time. Does not break Stealth."
            S.settings.descriptions=false;assert(outcome()=="text-mismatch");S.settings.descriptions=true
            local heal="Heals the friendly target for 251 to 283, then jumps to heal additional nearby targets. " ..
                "If cast on a party member, the heal will only jump to other party members. Each jump is "
            for _,id in ipairs({1064,10622,10623}) do
                for _,pct in ipairs({50,65}) do
                    card(id,"Chain Heal",heal..pct.."% as effective as the previous target. Heals 4 total targets.")
                    assert(outcome()=="shown" and bodySeen:find(pct.."% ของการรักษาเป้าหมายก่อนหน้า",1,true))
                    assert(bodySeen:find("251 ถึง 283",1,true) and bodySeen:find("รักษารวม 4 เป้าหมาย",1,true))
                end
            end
            local lightning="Hurls a lightning bolt at the enemy, dealing 209 to 237 Nature damage and then " ..
                "jumping to additional nearby enemies. Each jump reduces the damage by "
            for _,id in ipairs({421,930,2860,10605}) do
                for _,pct in ipairs({30,20}) do
                    card(id,"Chain Lightning",lightning..pct.."%. Affects 4 total targets.")
                    assert(outcome()=="shown" and bodySeen:find("ลดลง "..pct.."%",1,true))
                    assert(bodySeen:find("209 ถึง 237",1,true) and bodySeen:find("เป้าหมายรวม 4 ตัว",1,true))
                end
            end
            data.lines[2].leftText=lightning.."65%. Affects 4 total targets."
            assert(outcome()=="text-mismatch" and S.stats.errors==0)
        ''')

    def test_entangling_roots_copies_visible_values_for_each_overgrowth_rank(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            local start="Roots the target in place and causes 54 Nature damage over 15 sec. " ..
                "Damage caused may interrupt the effect. You may "
            local finish=" Rooted at a time."
            for _,id in ipairs({339,1062,5195,5196,9852,9853}) do
                data={type=1,id=id,lines={{leftText="Entangling Roots"},{}}}
                info={getterName="GetAction",getterArgs={7},tooltipData=data}
                for count,branch in ipairs({"only have 1 target","have up to 2 targets","have up to 3 targets"}) do
                    data.lines[2].leftText=start..branch..finish
                    assert(outcome()=="shown")
                    assert(bodySeen:find("54 หน่วยตลอด 15 วินาที",1,true))
                    local limit=count==1 and "เพียง " or "สูงสุด "
                    assert(bodySeen:find(limit..count.." เป้าหมาย",1,true))
                end
                S.settings.descriptions=false
                for _,bad in ipairs({"have up to 1 target","have up to 2 target","have up to 4 targets",
                        "have up to 2.5 targets","only have 2 targets"}) do
                    data.lines[2].leftText=start..bad..finish
                    assert(outcome()=="text-mismatch" and not S.reader:IsShown())
                end
                S.settings.descriptions=true
                data.lines[2].leftText=start.."only have 1 target"..finish
                assert(outcome()=="shown")
                data.lines[2].leftText=data.lines[2].leftText.." Outdoors only."
                assert(outcome()=="text-mismatch")
            end
            data.id=19970
            data.lines[2].leftText=start.."only have 1 target"..finish
            assert(outcome()~="shown" and not S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_shield_and_tactical_mastery_copy_separate_native_values(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            local function shield(absorb,duration,lockout)
                return "Draws on the soul of the party member to shield them, absorbing "..absorb..
                    " damage. Lasts "..duration..". While the shield holds, spellcasting will not be interrupted by damage. " ..
                    "Once shielded, the target cannot be shielded again for "..lockout.."."
            end
            local function card(id,name,text,getter,args)
                data={type=1,id=id,lines={{leftText=name},{leftText=text}}}
                info={getterName=getter,getterArgs=args,tooltipData=data}
            end
            for rank,id in ipairs({17,592,600,3747,6065,6066,10898,10899,10900,10901}) do
                local absorb=(40+rank*7)..".5"
                card(id,"Power Word: Shield",shield(absorb,"30 sec","15 sec"),"GetAction",{7})
                assert(outcome()=="shown" and bodySeen:find(absorb.." หน่วย",1,true))
                assert(bodySeen:find("30 วินาที",1,true) and bodySeen:find("15 วินาที",1,true))
                data.lines[2].leftText=shield("50","1 min","12 sec")
                assert(outcome()=="shown" and bodySeen:find("1 นาที",1,true) and bodySeen:find("12 วินาที",1,true))
                data.lines[2].leftText=shield("-50","30 sec","15 sec")
                assert(outcome()=="text-mismatch")
            end
            data.lines[2].leftText=shield("250","30 sec","15 sec"):gsub("Once shielded.*","")
            S.settings.descriptions=false
            assert(outcome()=="text-mismatch" and not S.reader:IsShown())
            S.settings.descriptions=true
            local function tactical(rage) return "You retain up to "..rage.." Rage when you change Stances." end
            card(1310185,"Tactical Mastery",tactical("10"),"GetSpellBookItem",{3,0})
            for _,rage in ipairs({"10","15","20","25"}) do
                data.lines[2].leftText=tactical(rage)
                assert(outcome()=="shown" and bodySeen:find("สูงสุด "..rage.." หน่วย",1,true))
            end
            for _,rage in ipairs({"0","-5","2.5","10 to 25"}) do
                data.lines[2].leftText=tactical(rage)
                assert(outcome()=="text-mismatch")
            end
            data.id=12295
            data.lines[2].leftText=tactical("25")
            assert(outcome()~="shown" and not S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_conjure_food_and_water_keep_each_product_and_visible_count(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            function S.RememberLongText(_,text) bodySeen=text end
            function tip:GetLeftLine(i)
                local line=data.lines[i]
                if line then
                    return {IsShown=function() return true end,GetText=function() return line.leftText end}
                end
            end
            function tip:GetRightLine() end
            local actionKind="spell"
            function GetActionInfo(slot) assert(slot==6);return actionKind,data.id end
            local function outcome() return S.OnTooltip(tip,data) end
            local footer="Conjured items disappear if logged out for more than 15 minutes."
            local spells={
                {5504,"bottle of water","bottles of water","น้ำดื่ม","ขวด"},
                {5505,"bottle of fresh water","bottles of fresh water","น้ำสะอาด","ขวด"},
                {5506,"bottle of purified water","bottles of purified water","น้ำบริสุทธิ์","ขวด"},
                {6127,"bottle of spring water","bottles of spring water","น้ำจากตาน้ำ","ขวด"},
                {10138,"bottle of mineral water","bottles of mineral water","น้ำแร่","ขวด"},
                {10139,"bottle of sparkling water","bottles of sparkling water","น้ำซ่า","ขวด"},
                {10140,"bottle of crystal water","bottles of crystal water","น้ำผลึก","ขวด"},
                {587,"muffin","muffins","มัฟฟิน","ชิ้น"},
                {597,"loaf of bread","loaves of bread","ขนมปัง","ก้อน"},
                {990,"loaf of rye","loaves of rye","ขนมปังไรย์","ก้อน"},
                {6129,"loaf of pumpernickel","loaves of pumpernickel","ขนมปังพัมเปอร์นิกเกิล","ก้อน"},
                {10144,"loaf of sourdough","loaves of sourdough","ขนมปังซาวร์โดว์","ก้อน"},
                {10145,"sweet roll","sweet rolls","ขนมปังโรลหวาน","ชิ้น"},
                {28612,"cinnamon roll","cinnamon rolls","ซินนามอนโรล","ชิ้น"},
            }
            for index,spell in ipairs(spells) do
                local water=index<=7
                local name=water and "Conjure Water" or "Conjure Food"
                local function text(amount, unit, owner)
                    return "Conjures "..amount.." "..unit..", providing the mage and "..owner..
                        " allies with something to "..(water and "drink." or "eat.")
                end
                local body={type=34,lineIndex=2}
                local tail={type=34,lineIndex=3,leftText=footer}
                data={type=1,id=spell[1],lines={{leftText=name},body,tail}}
                info={getterName="GetAction",getterArgs={6},tooltipData=data}
                for _,owner in ipairs({"his","her"}) do
                    for _,amount in ipairs({1,13,23}) do
                        body.leftText=text(amount,spell[amount==1 and 2 or 3],owner)
                        assert(outcome()=="shown")
                        assert(bodySeen:find(spell[4].." "..amount.." "..spell[5],1,true))
                        assert(bodySeen:find("ออกจากเกมนานกว่า 15 นาที",1,true))
                    end
                end
                actionKind="macro";assert(outcome()=="text-mismatch");actionKind="spell"
                info.getterName="GetSpellBookItem";info.getterArgs={7,0}
                entry={name=name,spellID=spell[1],itemType=1,isPassive=false}
                assert(outcome()=="shown")
                entry.spellID=999;assert(outcome()=="text-mismatch")
                data.lines[3]=nil
                body.leftText=text(13,spell[3],"her").."\r\n\r\n"..footer
                assert(outcome()=="shown")
                body.leftText=text("1.5",spell[3],"her").." "..footer
                assert(outcome()=="text-mismatch")
                body.leftText=text(13,spell[3],"her")
                S.settings.descriptions=false
                assert(outcome()=="text-mismatch" and not S.reader:IsShown())
                S.settings.descriptions=true
            end
            assert(S.stats.errors==0)
        ''')

    def test_combo_builders_preserve_native_values_and_rank_mechanics(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            local cases={
                {1752,"Sinister Strike","An instant strike that causes 5 damage in addition to your normal weapon damage.",
                    "เพิ่ม 5 หน่วยจากความเสียหายอาวุธปกติ"},
                {53,"Backstab","Backstab the target, causing 160% weapon damage plus 20 to the target. " ..
                    "Must be behind the target. Requires a dagger in the main hand.","ถือมีดสั้นในมือหลัก"},
                {1776,"Gouge","Causes 11 damage, stops your attack, and incapacitates the target for 5 sec. " ..
                    "The target must be facing you. Any damage taken will break the effect.","ไร้ความสามารถเป็นเวลา 5 วินาที"},
                {703,"Garrote","Garrote the enemy, causing 132 damage over 18 sec, increased by your Attack Power. " ..
                    "Must be stealthed and behind the target.","132 หน่วยตลอด 18 วินาที"},
                {8676,"Ambush","Ambush the target, causing 250% weapon damage plus 70 to the target. " ..
                    "Must be stealthed and behind the target. Requires a dagger in the main hand.","บวก 70 หน่วย"},
                {1833,"Cheap Shot","Stuns the target for 4 sec. Must be stealthed.","มึนงงเป็นเวลา 4 วินาที"},
                {1241582,"Mutilate","Instantly attacks with both weapons for 90% weapon damage plus an additional " ..
                    "56.7 with each weapon. Damage increased by 20% against Poisoned targets.","บวก 56.7 หน่วย"},
                {1082,"Claw","Claw the enemy for 140% normal damage plus 27.","140% ของความเสียหายปกติ"},
                {5221,"Shred","Shred the target, causing 200% damage plus 44 to the target. " ..
                    "Must be behind the target.","บวก 44 หน่วย ต้องอยู่ด้านหลังเป้าหมาย"},
                {1822,"Rake","Rake the target for 27 damage and an additional 60 damage over 9 sec.",
                    "อีก 60 หน่วยตลอด 9 วินาที"},
                {6785,"Ravage","Ravage the target, causing 435% damage plus 147 to the target. " ..
                    "Must be prowling and behind the target.","ย่องพรางตัว และอยู่ด้านหลังเป้าหมาย"},
                {9005,"Pounce","Pounce, stunning the target for 2 sec and causing 114 damage over 18 sec. " ..
                    "Must be prowling and behind the target.","มึนงงเป็นเวลา 2 วินาที และสร้างความเสียหาย 114 หน่วยตลอด 18 วินาที"},
            }
            for _,case in ipairs(cases) do
                local awards=case[1]==1241582 and {" Combo Point."," Combo Points."} or {" combo point."," combo points."}
                data={type=1,id=case[1],lines={{leftText=case[2]},{}}}
                info={getterName="GetAction",getterArgs={7},tooltipData=data}
                for count,ending in ipairs(awards) do
                    data.lines[2].leftText=case[3].." Awards "..count..ending
                    assert(outcome()=="shown" and bodySeen:find(case[4],1,true))
                    assert(bodySeen:find("ได้รับ "..count.." แต้มคอมโบ",1,true))
                end
                S.settings.descriptions=false
                data.lines[2].leftText=case[3].." Awards 1.5"..awards[2]
                assert(outcome()=="text-mismatch" and not S.reader:IsShown())
                S.settings.descriptions=true
            end
            data.id=8724
            data.lines={{leftText="Ambush"},{leftText=cases[5][3].." Awards 1 combo point."}}
            assert(outcome()=="text-mismatch")
            data.lines[2].leftText=data.lines[2].leftText:gsub("plus 70","plus 100")
            assert(outcome()=="shown" and bodySeen:find("บวก 100 หน่วย",1,true))
            data.id=399956
            data.lines={{leftText="Mutilate"},{leftText=cases[7][3].." Awards 2 Combo Points."}}
            assert(S.records["spell:399956"]==nil and S.records["talent-spell:399956:1"])
            assert(outcome()~="shown" and S.stats.errors==0)
        ''')

    def test_utility_spellbook_keeps_paired_grammar_and_rank_specific_effects(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            local function card(id,name,text)
                data={type=1,id=id,lines={{leftText=name},{leftText=text}}}
                info={getterName="GetAction",getterArgs={7},tooltipData=data}
            end
            for _,id in ipairs({527,988}) do
                card(id,"Dispel Magic","Dispels magic on the target, removing 2 harmful spells " ..
                    "from a friend or 2 beneficial spells from an enemy.")
                assert(outcome()=="shown" and bodySeen:find("เป็นโทษ 2",1,true) and bodySeen:find("เป็นประโยชน์ 2",1,true))
                local original=data.lines[2].leftText
                data.lines[2].leftText=original:gsub("2 beneficial spells","3 beneficial spells")
                assert(outcome()=="text-mismatch")
                data.lines[2].leftText=original:gsub("2 beneficial spells","2 beneficial spell")
                assert(outcome()=="text-mismatch")
            end
            local cures={
                {528,"Cure Disease","Removes 1 disease from the friendly target.","โรค 1 เอฟเฟกต์"},
                {2870,"Cure Disease","Cures 1 disease on the target.","โรค 1 เอฟเฟกต์"},
                {526,"Cure Poison","Cures 1 poison effect on the target.","พิษ 1 เอฟเฟกต์"},
                {8946,"Cure Poison","Cures 1 poison effect on the target.","พิษ 1 เอฟเฟกต์"},
                {370,"Purge","Purges the enemy target, removing 1 magic effect.","ลบล้างเอฟเฟกต์เวท 1"},
                {8012,"Purge","Purges the enemy target, removing 2 beneficial magic effects.","ที่เป็นประโยชน์ 2"},
            }
            for _,row in ipairs(cures) do
                card(row[1],row[2],row[3])
                assert(outcome()=="shown" and bodySeen:find(row[4],1,true))
            end
            data.lines[2].leftText=data.lines[2].leftText:gsub("beneficial ","")
            assert(outcome()=="text-mismatch")
            for rank,id in ipairs({16689,16810,16811,16812,16813,17329}) do
                local suffix=" the caster will afflict the attacker with Entangling Roots (Rank "..rank..
                    "). Castable while shapeshifted. Lasts 43 sec."
                card(id,"Nature's Grasp","The next 1 melee attack that strikes"..suffix)
                assert(outcome()=="shown" and bodySeen:find("รากพันธนาการ (แรงก์ "..rank..")",1,true))
                assert(bodySeen:find("ใช้ขณะแปลงร่างได้ คงอยู่ 43 วินาที",1,true))
                data.lines[2].leftText="The next 2 melee attacks that strike"..suffix
                assert(outcome()=="shown" and bodySeen:find("ระยะประชิด 2 ครั้ง",1,true))
                data.lines[2].leftText="The next 2 melee attacks that strikes"..suffix
                assert(outcome()=="text-mismatch")
            end
            for rank,id in ipairs({8232,8235,10486,16362}) do
                local applied=rank==2 and "appied" or "applied"
                local body="Imbue the Shaman's weapon with wind. Each hit has a 20% chance of granting you " ..
                    "2 extra attacks with 317.5 extra melee attack power. When "..applied..
                    " to main hand, disables any benefit you personally receive from Windfury Totem. Lasts for 60 minutes."
                card(id,"Windfury Weapon",body)
                assert(outcome()=="shown" and bodySeen:find("โจมตีเพิ่ม 2 ครั้ง",1,true))
                assert(bodySeen:find("พลังโจมตีระยะประชิดเพิ่ม 317.5 หน่วย",1,true))
                assert(bodySeen:find("คุณจะไม่ได้รับผลจากโทเท็มพิโรธวายุ",1,true))
                S.settings.descriptions=false
                data.lines[2].leftText=body:gsub("2 extra attacks","2.5 extra attacks")
                assert(outcome()=="text-mismatch")
                data.lines[2].leftText=body:gsub("main hand","off hand")
                assert(outcome()=="text-mismatch" and not S.reader:IsShown())
                S.settings.descriptions=true
            end
            assert(S.stats.errors==0)
        ''')

    def test_new_trainer_and_quest_ids_match_their_own_spell_or_aura_text(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            local function spell(id,name,text,getter)
                data={type=1,id=id,lines={{leftText=name},{leftText=text}}}
                info={getterName=getter,getterArgs={7,0},tooltipData=data}
            end
            spell(674,"Dual Wield","Allows one-hand and off-hand weapons to be equipped in the off-hand.","GetSpellBookItem")
            assert(outcome()=="shown" and bodySeen:find("ช่องมือรอง",1,true))
            spell(3127,"Parry","Gives a chance to parry enemy melee attacks.","GetSpellBookItem")
            assert(outcome()=="shown" and bodySeen:find("มีโอกาสปัดป้อง",1,true))
            local omen="Your spells and attacks have a chance to grant you Clearcasting, reducing the Mana, Rage, " ..
                "or Energy cost of your next damage or healing spell or offensive ability by 100%. " ..
                "Clearcasting is not consumed by Wrath or by spells or abilities that cost no resources."
            spell(16864,"Omen of Clarity",omen,"GetSpellBookItem")
            assert(outcome()=="shown" and bodySeen:find("100%",1,true) and bodySeen:find("พิโรธธรรมชาติ",1,true))
            S.settings.descriptions=false
            data.lines[2].leftText=omen:gsub("100%%","-100%%")
            assert(outcome()=="text-mismatch" and not S.reader:IsShown())
            S.settings.descriptions=true
            spell(5502,"Sense Undead","Shows the location of all nearby undead on the minimap until cancelled. " ..
                "Only one type of tracking can be used at a time.","GetAction")
            assert(outcome()=="shown" and bodySeen:find("แผนที่ย่อ",1,true))
            for _,id in ipairs({13819,1279399}) do
                spell(id,"Summon Warhorse","Summons a warhorse, which serves as a mount.","GetAction")
                assert(outcome()=="shown" and bodySeen:find("เรียกม้าศึกมาใช้เป็นพาหนะ",1,true))
                data.lines[2].leftText=data.lines[2].leftText.." Speed is increased by 60%."
                assert(outcome()=="text-mismatch")
            end
            data.id=13820
            assert(outcome()=="missing")
            Enum.TooltipDataType.UnitAura=7
            local auraID
            C_UnitAuras={GetAuraDataByAuraInstanceID=function(unit,instance)
                assert(unit=="player" and instance==9); return {spellId=auraID}
            end}
            local function aura(id,name,text)
                auraID=id
                data={type=7,id=123,lines={{leftText=name},{leftText=text}}}
                info={getterName="GetUnitBuffByAuraInstanceID",getterArgs={"player",9},tooltipData=data}
            end
            aura(5502,"Sense Undead","Detecting Undead.")
            assert(outcome()=="shown" and bodySeen=="กำลังตรวจจับอันเดด")
            aura(16870,"Clearcasting","Your next damage or healing spell or offensive ability has its mana, " ..
                "rage or energy cost reduced by 90%.")
            assert(outcome()=="shown" and bodySeen:find("90%",1,true))
            data.lines[2].leftText=omen
            assert(outcome()=="text-mismatch" and not S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_quest_felsteed_and_tome_spells_require_exact_native_bodies(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            function S.RememberLongText(_,text) bodySeen=text end
            function tip:GetLeftLine(i)
                local line=data.lines[i]
                if line then return {IsShown=function() return true end,GetText=function() return line.leftText end} end
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #data.lines end
            local actionID
            function GetActionInfo(slot) assert(slot==6);return "spell",actionID end
            local function card(id,name,...)
                actionID=id
                data={type=1,id=id,lines={{leftText=name}}}
                info={getterName="GetAction",getterArgs={6},tooltipData=data}
                for _,line in ipairs({...}) do
                    table.insert(data.lines,{type=34,lineIndex=#data.lines+1,leftText=line})
                end
            end
            local function outcome() return S.OnTooltip(tip,data) end
            card(5784,"Summon Felsteed","Summons a Felsteed, which serves as a mount for the caster.")
            assert(outcome()=="shown" and bodySeen:find("พาหนะของผู้ร่าย",1,true))
            data.id=5785;assert(outcome()=="missing")
            local cow="Transforms the enemy into a cow, forcing it to wander around for up to 45 sec. " ..
                "While wandering, the cow cannot attack or cast spells but will regenerate very quickly. " ..
                "Any damage will transform the target back into its normal form. Only one target can be " ..
                "polymorphed at a time. Only works on Beasts, Humanoids and Critters."
            card(28270,"Polymorph: Cow",cow)
            assert(outcome()=="shown" and bodySeen:find("เป็นวัว",1,true) and bodySeen:find("45 วินาที",1,true))
            actionID=28271;assert(outcome()=="no-context");actionID=28270
            data.lines[2].leftText=cow:gsub("cow","turtle")
            assert(outcome()=="text-mismatch")
            info.getterName="GetSpellBookItem";info.getterArgs={7,0}
            entry={name="Polymorph: Cow",spellID=28270,itemType=1,isPassive=false}
            data.lines[2].leftText=cow
            assert(outcome()=="shown")
            local eviscerate={"Finishing move that causes damage per combo point, increased by Attack Power:",
                "1 point : 224-332 damage","2 points: 394-502 damage","3 points: 564-672 damage",
                "4 points: 734-842 damage","5 points: 904-1,012 damage"}
            card(31016,"Eviscerate",unpack(eviscerate))
            assert(outcome()=="shown" and bodySeen:find("\n1 แต้ม สร้างความเสียหาย 224-332 หน่วย",1,true))
            assert(bodySeen:find("\n5 แต้ม สร้างความเสียหาย 904-1,012 หน่วย",1,true))
            data.lines[3].leftText="2 points: 224-332 damage"
            S.settings.descriptions=false
            assert(outcome()=="text-mismatch" and not S.reader:IsShown())
            S.settings.descriptions=true
            card(31016,"Eviscerate",table.concat(eviscerate,"\r\n"))
            assert(outcome()=="shown")
            card(31018,"Ferocious Bite",
                "Finishing move that causes damage per combo point and converts each extra point of energy into " ..
                "3.3 additional damage. Damage is increased by your Attack Power.",
                "1 point : 245-321 damage","2 points: 426-502 damage","3 points: 607-683 damage",
                "4 points: 788-864 damage","5 points: 969-1045 damage")
            assert(outcome()=="shown" and bodySeen:find("เพิ่มความเสียหาย 3.3 หน่วย",1,true))
            assert(bodySeen:find("\n5 แต้ม สร้างความเสียหาย 969-1045 หน่วย",1,true))
            data.lines[7].leftText="5 points: 969-1046 damage"
            assert(outcome()=="text-mismatch")
            Enum.TooltipDataType.UnitAura=7
            C_UnitAuras={GetAuraDataByAuraInstanceID=function() return {spellId=28270} end}
            data={type=7,id=42,lines={{leftText="Polymorph: Cow"},{leftText="Cannot attack or cast spells. Increased regeneration."}}}
            info={getterName="GetUnitDebuffByAuraInstanceID",getterArgs={"target",9},tooltipData=data}
            assert(outcome()=="shown" and bodySeen=="โจมตีหรือร่ายเวทไม่ได้ ฟื้นฟูเร็วขึ้น")
            assert(S.stats.errors==0)
        ''')

    def test_native_pet_commands_use_token_and_complete_tooltip(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.PetAction=11
            local token, isToken, spellID
            local visibleBody, visibleRight, visibleCount
            local function region(text)
                return {IsShown=function() return true end,GetText=function() return text end}
            end
            function tip:GetLeftLine(index)
                return region(index==2 and visibleBody or data.lines[index].leftText)
            end
            function tip:GetRightLine()
                if visibleRight then return region(visibleRight) end
            end
            function tip:NumLines() return visibleCount or #data.lines end
            function GetPetActionInfo(slot)
                assert(slot==3)
                return token,123,isToken,false,false,false,spellID
            end
            function S.RememberLongText(heading,text) titleSeen,bodySeen=heading,text end
            local function outcome() return S.OnTooltip(tip,data) end
            local commands={
                {"PET_ACTION_ATTACK","Attack","Orders your pet to attack your current target.","โจมตีเป้าหมายปัจจุบัน"},
                {"PET_ACTION_FOLLOW","Follow","Orders your pet to follow you.","สัตว์เลี้ยงตามคุณ"},
                {"PET_ACTION_MOVE_TO","Move To","Orders your pet to move to a target location.","ตำแหน่งที่เลือก"},
                {"PET_ACTION_WAIT","Stay","Orders your pet to stay at its current location.","ตำแหน่งปัจจุบัน"},
                {"PET_MODE_AGGRESSIVE","Aggressive","Your pet will attack any nearby enemies.","ศัตรูทุกตัวที่อยู่ใกล้"},
                {"PET_MODE_DEFENSIVE","Defensive","Your pet will only attack enemies that attack you or your pet.","เฉพาะศัตรู"},
                {"PET_MODE_PASSIVE","Passive","Your pet won't attack until ordered to do so.","เมื่อได้รับคำสั่งเท่านั้น"},
                {"PET_MODE_ASSIST","Assist","Your pet will assist you.","สัตว์เลี้ยงจะช่วยเหลือคุณ"},
                {"PET_MODE_DEFENSIVEASSIST","Defensive","Your pet will only attack enemies that attack you or your pet.","เฉพาะศัตรู"},
            }
            for _,command in ipairs(commands) do
                token,isToken,spellID=command[1],true,nil
                _G[token]=command[2]
                data={type=11,id=17253,lines={{leftText=command[2]},{leftText=command[3]}}}
                info={getterName="GetPetAction",getterArgs={3},tooltipData=data}
                local context=S.Context(tip,data)
                assert(context.key=="pet-command:"..token and context.id==nil)
                assert(outcome()=="shown" and bodySeen:find(command[4],1,true))
                assert(titleSeen==S.records[context.key].translatedName)
            end
            S.settings.descriptions=false
            data.lines[2].leftText="Your pet will attack any nearby enemies."
            assert(outcome()=="text-mismatch" and not S.reader:IsShown())
            data.lines[2].leftText=commands[9][3]
            visibleBody="Different visible instruction."
            assert(outcome()=="no-context");visibleBody=nil
            visibleRight="Additional visible instruction."
            assert(outcome()=="no-context");visibleRight=nil
            visibleCount=3;assert(outcome()=="no-context");visibleCount=nil
            data.lines[2].rightText="Hidden stale instruction."
            assert(outcome()=="no-context");data.lines[2].rightText=nil
            data.lines[3]={leftText="Unrecognized additional command effect."}
            assert(outcome()=="no-context")
            data.lines[3]=nil
            assert(outcome()=="shown" and bodySeen=="")
            S.settings.descriptions=true
            info.tooltipData={};assert(outcome()=="no-context");info.tooltipData=data
            primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            info.getterArgs[1]=11;assert(outcome()=="no-context");info.getterArgs[1]=3
            _G[token]="Changed";assert(outcome()=="no-context");_G[token]=commands[9][2]
            isToken=false;assert(outcome()=="no-context");isToken=true
            token="PET_MODE_UNKNOWN";assert(outcome()=="no-context");token=commands[9][1]
            data.type=1;assert(outcome()=="no-context");data.type=11
            info.getterName="GetAction";assert(outcome()=="no-context");info.getterName="GetPetAction"
            GameTooltip=tip
            function tip:SetPetAction() end
            local retry
            function hooksecurefunc(widget,method,callback)
                assert(widget==tip and method=="SetPetAction")
                retry=callback
            end
            S.RegisterTooltips()
            tip:Show()
            retry(tip,3)
            assert(S.reader:IsShown() and bodySeen:find("เฉพาะศัตรู",1,true))
            tip:Hide()
            assert(not S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_pet_spellbook_commands_require_a_current_exact_pet_bar_link(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.PetAction=11
            Enum.SpellBookSpellBank={Player=0,Pet=1}
            Enum.SpellBookItemType={Spell=1,PetAction=3}
            Enum.ActionBarSet={Mkb=1,Gamepad=2,All=3}
            local title, body = "Defensive", "Your pet will only attack enemies that attack you or your pet."
            PET_MODE_DEFENSIVE, PET_MODE_DEFENSIVEASSIST = title, title
            data={type=11,lines={{leftText=title},{leftText=body}}}
            info={getterName="GetSpellBookItem",getterArgs={7,1},tooltipData=data}
            local entry={itemType=3,actionID=203,name=title}
            local slots, token, secondToken, isToken = {8}, "PET_MODE_DEFENSIVE", "PET_MODE_DEFENSIVE", true
            local gamepad = false
            InputUtil={IsGamepadUIEnabled=function() return gamepad end}
            C_SpellBook={GetSpellBookItemInfo=function(slot,bank)
                assert(slot==7 and bank==1); return entry
            end}
            C_ActionBar={GetPetActionPetBarIndices=function(action,set)
                assert(set==1)
                if action==203 then return slots end
            end}
            function GetPetActionInfo(slot)
                assert(slot==8 or slot==9)
                return slot==8 and token or secondToken,123,isToken
            end
            function tip:GetLeftLine(index)
                return {IsShown=function() return true end,GetText=function() return data.lines[index].leftText end}
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #data.lines end
            function S.RememberLongText(_,text) bodySeen=text end
            local function outcome() return S.OnTooltip(tip,data) end
            assert(S.Context(tip,data).key=="pet-command:PET_MODE_DEFENSIVE")
            assert(outcome()=="shown" and bodySeen:find("เฉพาะศัตรู",1,true))
            slots={8,9};assert(outcome()=="shown")
            secondToken="PET_MODE_DEFENSIVEASSIST";assert(outcome()=="no-context")
            slots={9}
            assert(S.Context(tip,data).key=="pet-command:PET_MODE_DEFENSIVEASSIST")
            data.lines[2].leftText="Different visible effect.";assert(outcome()=="text-mismatch")
            data.lines[2].leftText=body
            entry.actionID=204;assert(outcome()=="no-context");entry.actionID=203
            entry.name="Wrong book title";assert(outcome()=="no-context");entry.name=title
            entry.itemType=1;assert(outcome()=="no-context");entry.itemType=3
            info.getterArgs[2]=0;assert(outcome()=="no-context");info.getterArgs[2]=1
            gamepad=true;assert(outcome()=="no-context");gamepad=false
            slots={11};assert(outcome()=="no-context");slots={8}
            isToken=false;assert(outcome()=="no-context");isToken=true
            slots=nil;assert(outcome()=="no-context");slots={8}
            primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            assert(outcome()=="shown" and S.stats.errors==0)
        ''')

    def test_player_action_bar_pet_commands_require_reverse_slot_confirmation(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.PetAction=11
            Enum.ActionBarSet={Mkb=1,Gamepad=2,All=3}
            PET_ACTION_ATTACK="Attack"
            local text="Orders your pet to attack your current target."
            data={type=11,id=42,lines={{leftText=PET_ACTION_ATTACK},{leftText=text}}}
            info={getterName="GetAction",getterArgs={42},tooltipData=data}
            local actionID, kind, actionSlots, petSlots, token = 203, "petaction", {9,42}, {3}, true
            local petQueries, gamepad = 0, false
            InputUtil={IsGamepadUIEnabled=function() return gamepad end}
            function GetActionInfo(slot)
                assert(slot==42)
                return kind,actionID
            end
            C_ActionBar={
                FindPetActionButtons=function(id,set)
                    assert(set==1)
                    if id==203 then return actionSlots end
                end,
                GetPetActionPetBarIndices=function(id,set)
                    assert(id==203 and set==1)
                    petQueries=petQueries+1
                    return petSlots
                end
            }
            function GetPetActionInfo(slot)
                assert(slot==3)
                return "PET_ACTION_ATTACK",123,token
            end
            function tip:GetLeftLine(index)
                return {IsShown=function() return true end,GetText=function() return data.lines[index].leftText end}
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #data.lines end
            function S.RememberLongText(_,body) bodySeen=body end
            local function outcome() return S.OnTooltip(tip,data) end
            assert(S.Context(tip,data).key=="pet-command:PET_ACTION_ATTACK")
            assert(outcome()=="shown" and bodySeen:find("โจมตีเป้าหมายปัจจุบัน",1,true))
            local priorQueries=petQueries
            actionSlots={9};kind="macro"
            assert(outcome()=="no-context" and not S.reader:IsShown() and petQueries==priorQueries)
            kind="petaction";actionSlots={42}
            actionID=204;assert(outcome()=="no-context");actionID=203
            kind=nil;assert(outcome()=="no-context");kind="petaction"
            gamepad=true;assert(outcome()=="no-context");gamepad=false
            petSlots={};assert(outcome()=="no-context");petSlots={3}
            token=false;assert(outcome()=="no-context");token=true
            data.lines[2].leftText="Different command.";assert(outcome()=="text-mismatch")
            data.lines[2].leftText=text
            data.lines[3]={leftText="Additional visible effect."};assert(outcome()=="no-context")
            data.lines[3]=nil
            primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            assert(outcome()=="shown" and S.stats.errors==0)
        ''')

    def test_weapon_flyout_compact_and_expanded_cards_keep_every_visible_value(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            SpellFlyout=frame(UIParent)
            local button=frame(SpellFlyout)
            SpellFlyout.buttons={button}
            function tip:GetOwner() return button end
            local visible={}
            function tip:NumLines() return #visible end
            local function region(text)
                return {IsShown=function() return true end,GetText=function() return text end}
            end
            function tip:GetLeftLine(i) return region(visible[i][1]) end
            function tip:GetRightLine(i)
                if visible[i][2] then return region(visible[i][2]) end
            end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local hint="Your chance to glance isn't affected by weapon skill above your max."
            local function card(id,expanded)
                button.spellID=id
                local record=S.records["spell:"..id]
                local pair=record.lines[1].alternatives[expanded and 2 or 1]
                local function value(i)
                    i=tonumber(i)
                    if i==1 then return "0" end
                    if i==2 then return "1,234" end
                    if i==4 then return "-0.50" end
                    return tostring(i)
                end
                local english=pair.source:gsub("{(%d+)}",value)
                if expanded and english:sub(-#hint)==hint then
                    english=english:sub(1,-#hint-1).."|cff9d9d9d"..hint.."|r"
                elseif not expanded then
                    english=english.."\n|cffBCBCBCHold Shift for additional info.|r"
                end
                data={type=1,id=id,lines={{leftText=record.originalName},{leftText=english}}}
                info={getterName="GetSpellByID",getterArgs={id,false,true},tooltipData=data}
                visible={{record.originalName},{english}}
                return record.translatedName,(pair.target:gsub("{(%d+)}",value))
            end
            local function outcome() return S.OnTooltip(tip,data) end
            local count=0
            for key,record in pairs(S.records) do
                if record.weaponStat then
                    local id=tonumber(key:match("^spell:(%d+)$"))
                    for _,expanded in ipairs({false,true}) do
                        local title,body=card(id,expanded)
                        assert(outcome()=="shown" and titleSeen==title and bodySeen==body)
                        assert(bodySeen:find("0/1,234",1,true) and bodySeen:find("-0.50%",1,true))
                        assert(bodySeen:find("\nเป้าหมายเลเวล",1,true))
                    end
                    count=count+1
                end
            end
            assert(count==17)
            local _,full=card(1303009,true)
            assert(full:find("ถูกปัดป้อง",1,true) and not full:find("โจมตีเฉี่ยว",1,true))
            local _,bow=card(1302995,true)
            assert(not bow:find("ถูกปัดป้อง",1,true) and not bow:find("โจมตีเฉี่ยว",1,true))
            SPELL_PASSIVE="Passive"
            C_Spell={IsSpellPassive=function(id) return id==1303007 end}
            card(1303007,false)
            visible[1][2]="Passive";assert(outcome()=="shown")
            card(1303007,false)
            table.insert(visible,2,{""});table.insert(visible,3,{"Passive"});assert(outcome()=="shown")
            card(1302995,false)
            table.insert(visible,2,{"Passive"});assert(outcome()=="text-mismatch")
            card(1303007,false)
            local body=visible[2][1]
            local first,second,rest=body:match("^(.-) (Hit, Dodge, and Parry:) (.+)$")
            local number,tail=rest:match("^(%-0%.50%%) (.+)$")
            visible[2]={first};visible[3]={second,number};visible[4]={tail}
            assert(outcome()=="shown")
            visible[4][1]=tail.."\nUnrecognized effect.";assert(outcome()=="text-mismatch")
            card(1303007,false)
            visible[2][1]=visible[2][1]:gsub("0/1,234","0/1,23")
            S.settings.descriptions=false;assert(outcome()=="text-mismatch")
            card(1303007,false);assert(outcome()=="shown" and bodySeen=="")
            primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            SpellFlyout:Hide();assert(outcome()=="no-context")
            assert(S.stats.errors==0)
        ''')

    def test_flyout_resistance_cards_copy_only_complete_live_numeric_values(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            SpellFlyout=frame(UIParent)
            local button=frame(SpellFlyout)
            SpellFlyout.buttons={button}
            function tip:GetOwner() return button end
            function tip:NumLines() return #data.lines end
            local override
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,
                    GetText=function() return i==2 and override or data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function card(id,school,resistance,percent)
                button.spellID=id
                local name=school.." Resistance"
                local body="You have "..resistance.." resistance to "..school..", reducing average "..
                    school.." damage taken and chance to be hit by "..school.." spells by "..percent.."%."
                data={type=1,id=id,lines={{leftText=name},{type=34,leftText=body,lineIndex=2}}}
                info={getterName="GetSpellByID",getterArgs={id,false,true},tooltipData=data}
            end
            local function outcome() return S.OnTooltip(tip,data) end
            local cards={{1296596,"Arcane","อาร์เคน","0","0.00"},{1296597,"Fire","ไฟ","1,234","12.30"},
                {1296598,"Frost","น้ำแข็ง","27","6.75"},{1296599,"Nature","ธรรมชาติ","-2","-0.50"},
                {1296601,"Shadow","เงา","15","3.75"}}
            for _,row in ipairs(cards) do
                card(row[1],row[2],row[4],row[5])
                assert(outcome()=="shown" and titleSeen=="ความต้านทานเวท"..row[3])
                assert(bodySeen:find(row[4].." หน่วย",1,true) and bodySeen:find(row[5].."%",1,true))
            end
            card(1296597,"Fire","5 to 7","2.00");assert(outcome()=="text-mismatch")
            card(1296597,"Fire","5","1-2");assert(outcome()=="text-mismatch")
            card(1296597,"Fire","5","2.00")
            data.lines[2].leftText=data.lines[2].leftText:gsub("Fire spells","Frost spells")
            S.settings.descriptions=false;assert(outcome()=="text-mismatch")
            card(1296597,"Fire","5","2.00");assert(outcome()=="shown" and bodySeen=="")
            override="Stale body.";assert(outcome()=="no-context");override=nil
            data.lines[3]={leftText="Another effect."};assert(outcome()=="no-context");data.lines[3]=nil
            button.spellID=1296598;assert(outcome()=="no-context");button.spellID=1296597
            SpellFlyout:Hide();assert(outcome()=="no-context")
            assert(S.stats.errors==0)
        ''')

    def test_reviewed_flyout_members_keep_cast_and_aura_text_and_values_separate(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.UnitAura=7
            function S.RememberLongText(title,text) titleSeen,bodySeen=title,text end
            local function cast(id,title,body)
                data={type=1,id=id,lines={{leftText=title},{leftText=body}}}
                info={getterName="GetSpellByID",getterArgs={id,false,true},tooltipData=data}
            end
            local function outcome() return S.OnTooltip(tip,data) end
            cast(20217,"Blessing of Kings","Places a Blessing on the friendly target, increasing total stats by 11% for 1 hour.  " ..
                "Players may only have one Blessing on them per Paladin at any one time.")
            assert(outcome()=="shown" and titleSeen=="พรแห่งราชัน" and bodySeen:find("11% เป็นเวลา 1 ชั่วโมง",1,true))
            assert(bodySeen:find("พาลาดินแต่ละคน",1,true))
            data.lines[2].leftText=data.lines[2].leftText:gsub("11%%","-11%%")
            assert(outcome()=="text-mismatch")
            cast(20218,"Sanctity Aura","Increases Holy damage done by party members within 30 yards by 10%.  " ..
                "Players may only have one Aura on them per Paladin at any one time.")
            assert(outcome()=="shown" and titleSeen=="ออร่าแห่งความศักดิ์สิทธิ์")
            assert(bodySeen:find("30 หลา",1,true) and bodySeen:find("10%",1,true))
            local auraSpell=20218
            C_UnitAuras={GetBuffDataByIndex=function(unit,index,filter)
                assert(unit=="target" and index==2 and filter=="HELPFUL")
                return {spellId=auraSpell}
            end}
            info.getterName="GetUnitBuff";info.getterArgs={"target",2,"HELPFUL"}
            data.type=7;data.id=999
            assert(outcome()=="text-mismatch")
            data.lines[2].leftText="Increases Holy damage done by 9%."
            assert(outcome()=="shown" and bodySeen:find("9%",1,true) and not bodySeen:find("หลา",1,true))
            auraSpell=20217
            data.lines={{leftText="Blessing of Kings"},{leftText="Increases stats by 10%."}}
            assert(outcome()=="shown" and bodySeen=="เพิ่มค่าสถานะ 10%")
            cast(20801,"Firebolt","Shoots a bolt of flame at an enemy, inflicting Fire damage.")
            assert(outcome()=="shown" and titleSeen=="ศรเพลิง" and bodySeen=="ยิงศรเพลิงใส่ศัตรู สร้างความเสียหายไฟ")
            data.id=3110;assert(outcome()=="text-mismatch")
            data.id=2949;assert(outcome()=="no-context")
            assert(S.stats.errors==0)
        ''')

    def test_combat_flyout_spell_requires_native_popup_and_full_visible_body(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            GameTooltip=tip
            Enum.TooltipDataLineType={SpellDescription=34}
            Enum.AddOnRestrictionType={Combat=0,Encounter=1,ChallengeMode=2,PvPMatch=3,Map=4,Chat=5}
            Enum.AddOnRestrictionState={Inactive=0,Activating=1,Active=2}
            C_RestrictedActions={GetAddOnRestrictionState=function() return 2 end}
            local reader
            for _,f in ipairs(frames) do if f.name=="AlphaWoWCombatReader" then reader=f end end
            function reader:GetWidth() return self.width end
            function UIParent:GetWidth() return 1920 end
            function UIParent:GetEffectiveScale() return 1 end
            function tip:GetEffectiveScale() return 1 end
            function tip:GetRect() return 1100,400,200,120 end
            function tip:IsForbidden() return false end
            tip.SetPoint=forbidden;tip.ClearLines=forbidden;tip.AddLine=forbidden
            SpellFlyoutPopupButtonMixin={SetTooltip=forbidden}
            SpellFlyout=frame(UIParent)
            function SpellFlyout:IsForbidden() return false end
            local button=frame(SpellFlyout)
            button.spellID=3561;button.isActionBar=true;button.SetTooltip=forbidden
            function button:IsForbidden() return false end
            SpellFlyout.buttons={button}
            local owner=button
            function tip:GetOwner() return owner end
            local english="Teleports the caster to Stormwind."
            data={type=1,id=3561,lines={{leftText="Teleport: Stormwind"},
                {type=34,lineIndex=2,leftText=english}}}
            info={getterName="GetSpellByID",getterArgs={3561,false,true},tooltipData=data}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i)
                return {IsShown=function() return true end,GetText=function() return data.lines[i].leftText end}
            end
            function tip:GetRightLine() end
            local function shown()
                assert(S.OnTooltip(tip,data)=="shown" and reader:IsShown())
                local title,body,_,_,_,flyout=S.PublicCombatTooltip(tip,data)
                assert(title=="เคลื่อนย้าย: Stormwind" and body=="เคลื่อนย้ายผู้ร่ายไปยัง Stormwind" and flyout)
            end
            local function rejected() assert(S.OnTooltip(tip,data)=="combat" and not reader:IsShown()) end
            S.RegisterCombatTooltips();combat=true
            rejected() -- No popup close hook installed yet.
            combat=false;S.RegisterBasicFlyoutTooltips();combat=true
            shown();SpellFlyout:Hide();assert(not reader:IsShown());rejected();SpellFlyout:Show()
            shown();event("SPELL_FLYOUT_UPDATE");assert(not reader:IsShown())
            shown();event("ACTIONBAR_SLOT_CHANGED",6);assert(not reader:IsShown())
            button.spellID=3562;rejected();button.spellID=3561
            button.offSpec=true;rejected();button.offSpec=nil
            button.isActionBar=false;rejected();button.isActionBar=true
            button.SetTooltip=function() end;rejected();button.SetTooltip=forbidden
            info.getterArgs[2]=true;rejected();info.getterArgs[2]=false
            info.getterArgs[3]=false;rejected();info.getterArgs[3]=true
            secret[data.id]=true;rejected();secret[data.id]=nil
            data.lines[3]={leftText="Additional unreviewed effect."};rejected();data.lines[3]=nil
            data.lines[2].leftText="Teleports the caster to Ironforge.";rejected();data.lines[2].leftText=english
            shown()
        ''')

    def test_native_flyout_members_support_basic_titles_and_detailed_aliases(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            local mode, quick, name, count, currentOwner = "0", false, "Teleport: Stormwind", 1
            function GetCVar(key) assert(key=="UberTooltips");return mode end
            function KeybindFrames_InQuickKeybindMode() return quick end
            C_Spell={GetSpellName=function(id)
                if id==3561 then return "Teleport: Stormwind" end
                if id==3562 then return "Teleport: Ironforge" end
            end}
            local function region(text)
                return {IsShown=function() return true end,GetText=function() return text end}
            end
            function tip:GetOwner() return currentOwner end
            function tip:NumLines() return count end
            function tip:GetLeftLine(i) return region(i==1 and name or data.lines[i].leftText) end
            function tip:GetRightLine() end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            GameTooltip=tip
            SpellFlyout=frame(UIParent)
            SpellFlyout:Hide()
            SpellFlyout.buttons={}
            local button=frame(SpellFlyout)
            button.spellID=3561
            currentOwner=button
            function button:SetTooltip() tip:Show() end
            button:SetScript("OnEnter",button.SetTooltip)
            S.RegisterTooltips()
            assert(not button.hooks.OnEnter)
            SpellFlyout.buttons={button}
            SpellFlyout:Show()
            assert(#button.hooks.OnEnter==1)
            button:Fire("OnEnter")
            assert(S.reader:IsShown() and titleSeen=="เคลื่อนย้าย: Stormwind" and bodySeen=="")
            SpellFlyout:Hide();assert(not S.reader:IsShown())
            button.spellID,name=3562,"Teleport: Ironforge"
            SpellFlyout:Show();button:Fire("OnEnter")
            assert(#button.hooks.OnEnter==1 and titleSeen=="เคลื่อนย้าย: Ironforge")
            SpellFlyout.buttons={};button:Fire("OnEnter");assert(not S.reader:IsShown())
            SpellFlyout.buttons={button}
            name="Teleport: Stormwind";button:Fire("OnEnter");assert(not S.reader:IsShown())
            name="Teleport: Ironforge"
            quick=true;button:Fire("OnEnter");assert(not S.reader:IsShown());quick=false
            count=2;button:Fire("OnEnter");assert(not S.reader:IsShown());count=1
            button.offSpec=true;button:Fire("OnEnter");assert(not S.reader:IsShown());button.offSpec=false
            button.showFullTooltip=true;button:Fire("OnEnter");assert(not S.reader:IsShown());button.showFullTooltip=nil
            local key="spell:3562"
            S.records[key].requireDescriptionMatch=true
            button:Fire("OnEnter");assert(not S.reader:IsShown())
            S.records[key].requireDescriptionMatch=nil
            button:Fire("OnEnter");assert(S.reader:IsShown())
            combat=true;button:Fire("OnEnter");assert(not S.reader:IsShown());combat=false
            mode="1";button:Fire("OnEnter");assert(not S.reader:IsShown())
            button.spellID,name=24858,"Moonkin Form"
            local body=S.records["talent-spell:24858:1"].lines[1].source
                :gsub("{1}","20"):gsub("{2}","360"):gsub("{3}","30"):gsub("{4}","3")
            local first,second=body:match("^(.-)\n\n(.+)$")
            data={type=1,id=24858,lines={{leftText=name},{type=34,leftText=first,lineIndex=2},
                {type=34,leftText=second,lineIndex=3}}}
            count=3;info={getterName="GetSpellByID",getterArgs={24858,false,true},tooltipData=data}
            local function outcome() return S.OnTooltip(tip,data) end
            assert(outcome()=="shown" and titleSeen=="ร่าง Moonkin" and bodySeen:find("360%",1,true))
            info.getterArgs[2]=true;assert(outcome()=="missing");info.getterArgs[2]=false
            info.getterArgs[3]=false;assert(outcome()=="missing");info.getterArgs[3]=true
            currentOwner=frame(SpellFlyout);currentOwner.spellID=24858
            assert(outcome()=="missing");currentOwner=button
            data.lines[4]={leftText="Other effect."};count=4;assert(outcome()=="missing")
            data.lines[4]=nil;count=3
            S.settings.descriptions=false
            data.lines[3].leftText="Different movement effect."
            assert(outcome()=="text-mismatch")
            data.lines[3].leftText=second
            assert(outcome()=="shown" and bodySeen=="" and S.stats.errors==0)
            tip:Hide();assert(not S.reader:IsShown())
        ''')

    def test_imp_fire_shield_learning_member_only_displays_reviewed_title(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            local mode, rank, right = "0", "Rank 1", ""
            local lines = {"Fire Shield"}
            function GetCVar() return mode end
            function KeybindFrames_InQuickKeybindMode() return false end
            C_Spell={GetSpellName=function(id) assert(id==2949);return "Fire Shield" end,
                GetSpellSubtext=function(id) assert(id==2949);return rank end}
            local function region(text)
                return {IsShown=function() return true end,GetText=function() return text end}
            end
            GameTooltip=tip
            SpellFlyout=frame(UIParent)
            local button=frame(SpellFlyout)
            button.spellID=2949
            SpellFlyout.buttons={button}
            local currentOwner=button
            function tip:GetOwner() return currentOwner end
            function tip:NumLines() return #lines end
            function tip:GetLeftLine(i) return region(lines[i]) end
            function tip:GetRightLine(i) if i==1 then return region(right) end end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            button:SetScript("OnEnter",function() tip:Show() end)
            S.RegisterTooltips()
            button:Fire("OnEnter")
            assert(S.reader:IsShown() and titleSeen=="โล่เพลิง" and bodySeen=="")
            rank="Rank 2";button:Fire("OnEnter");assert(not S.reader:IsShown());rank="Rank 1"

            mode="1"
            data={type=1,id=2949,lines={{leftText="Fire Shield"}}}
            info={getterName="GetSpellByID",getterArgs={2949,false,true},tooltipData=data}
            local function showsTitle() return S.OnTooltip(tip,data)=="shown" and bodySeen=="" end
            assert(showsTitle() and titleSeen=="โล่เพลิง")
            right="Rank 1";assert(showsTitle())
            right="";lines[2]="Rank 1";lines[3]=" ";assert(showsTitle())
            S.settings.englishNames=true
            assert(showsTitle() and titleSeen=="โล่เพลิง (Fire Shield)")
            S.settings.descriptions=false
            lines[3]="Unexpected body";assert(not showsTitle() and not S.reader:IsShown())
            lines[3]="";right="Rank 1";assert(not showsTitle())
            lines[2]=nil;lines[3]=nil;right="Rank 2";assert(not showsTitle());right=""
            info.getterArgs[1]=2947;assert(not showsTitle());info.getterArgs[1]=2949
            currentOwner=frame(SpellFlyout);currentOwner.spellID=2949
            assert(not showsTitle());currentOwner=button
            info.tooltipData={};assert(not showsTitle());info.tooltipData=data
            local child=S.records["spell:2947"]
            child.reviewStatus="NEEDS_REVIEW";assert(not showsTitle());child.reviewStatus="VERIFIED"
            assert(showsTitle() and S.stats.errors==0)
        ''')

    def test_native_flyout_headers_use_reviewed_group_identity_and_visible_body(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataType.Flyout=22
            local id, record, entry, kind, known, sourceBody, override
            function GetActionInfo(slot) assert(slot==4);return kind,id end
            function GetFlyoutInfo(flyoutID)
                assert(flyoutID==id);return record.originalName,sourceBody,2,known
            end
            C_SpellBook={GetSpellBookItemInfo=function(slot,bank)
                assert(slot==4 and bank==0);return entry
            end}
            function tip:NumLines() return #data.lines end
            local function region(text)
                return {IsShown=function() return true end,GetText=function() return text end}
            end
            function tip:GetLeftLine(i)
                return region(i==2 and override or data.lines[i].leftText)
            end
            function tip:GetRightLine(i)
                if data.lines[i].rightText then return region(data.lines[i].rightText) end
            end
            function S.RememberLongText(title,body) titleSeen,bodySeen=title,body end
            local function card(flyoutID)
                id=flyoutID;record=S.records["flyout:"..id]
                kind,known,sourceBody,override="flyout",true,record.lines[1].source,nil
                data={type=22,id=id,lines={{leftText=record.originalName},
                    {leftText=sourceBody,lineIndex=2},{leftText="Click to open."}}}
                info={getterName="GetAction",getterArgs={4},tooltipData=data}
                entry={name=record.originalName,itemType=Enum.SpellBookItemType.Flyout,actionID=id}
            end
            local function outcome() return S.OnTooltip(tip,data) end
            for _,group in ipairs({248,249,250,251,252,253,257,259,261,262,263,264,265,267,268,269,270,272,273}) do
                card(group)
                assert(outcome()=="shown" and titleSeen==record.translatedName and bodySeen==record.lines[1].target)
                info.getterName="GetSpellBookItem";info.getterArgs[2]=0
                assert(outcome()=="shown" and titleSeen==record.translatedName)
            end
            card(248)
            data.id=249;assert(outcome()=="no-context");data.id=nil
            assert(outcome()=="shown" and S.Context(tip,data).key=="flyout:248")
            kind="macro";assert(outcome()=="no-context");kind="flyout"
            known=false;assert(outcome()=="no-context");known=true
            local opaque=trap();secret[opaque]=true
            data.id=opaque;assert(outcome()=="no-context");data.id=nil
            sourceBody="Different portal rules.";assert(outcome()=="no-context");sourceBody=record.lines[1].source
            S.settings.descriptions=false
            override="Different visible body.";assert(outcome()=="no-context");override=nil
            data.lines[2].rightText="Other instruction";assert(outcome()=="no-context");data.lines[2].rightText=nil
            assert(outcome()=="shown" and bodySeen=="")
            S.settings.descriptions=true
            primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            info.getterName="GetSpellBookItem";info.getterArgs[2]=0
            entry.itemType=1;assert(outcome()=="no-context");entry.itemType=Enum.SpellBookItemType.Flyout
            entry.name="Teleport";assert(outcome()=="no-context");entry.name="Portal"
            info.getterArgs[2]=1;assert(outcome()=="no-context");info.getterArgs[2]=0
            assert(outcome()=="shown" and S.stats.errors==0)
        ''')

    def test_native_stance_slots_show_reviewed_casts_and_complete_talent_aliases(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            Enum.TooltipDataLineType={SpellDescription=34}
            local button=frame(UIParent)
            local currentOwner, ownerSlot, count, liveID = button, 2, 3, 2457
            StanceBar={actionButtons={[2]=button}}
            button.spellID=71
            function button:GetID() return ownerSlot end
            function tip:GetOwner() return currentOwner end
            function GetNumShapeshiftForms() return count end
            function GetShapeshiftFormInfo(slot)
                assert(slot==2)
                return 12345,true,true,liveID
            end
            local function card(name,...)
                data={lines={{leftText=name}}}
                for _,body in ipairs({...}) do
                    local index=#data.lines+1
                    data.lines[index]={type=34,leftText=body,lineIndex=index}
                end
                info={getterName="GetShapeshift",getterArgs={2},tooltipData=data}
            end
            local visibleOverride
            function tip:GetLeftLine(index)
                local line=data.lines[index]
                return {IsShown=function() return true end,
                    GetText=function() return index==2 and visibleOverride or line.leftText end}
            end
            function tip:GetRightLine() end
            function tip:NumLines() return #data.lines end
            function S.RememberLongText(title,text) titleSeen,bodySeen=title,text end
            local function outcome() return S.OnTooltip(tip,data) end
            card("Battle Stance","A balanced combat stance.")
            assert(outcome()=="shown" and titleSeen=="ท่ารบ" and bodySeen=="ท่าต่อสู้ที่สมดุล")
            data.type,data.id=1,2457
            assert(outcome()=="shown")
            data.id=71;assert(outcome()=="no-context");data.id=2457
            data.type=7;assert(outcome()=="no-context");data.type=1
            currentOwner={};assert(outcome()=="no-context");currentOwner=button
            ownerSlot=3;assert(outcome()=="no-context");ownerSlot=2
            count=1;assert(outcome()=="no-context");count=3
            primary={tooltipData=data};assert(outcome()=="no-context");primary=nil
            local opaque=trap();secret[opaque]=true
            liveID=opaque;assert(outcome()=="no-context");liveID=2457
            data.id=opaque;assert(outcome()=="no-context");data.id=nil
            visibleOverride="Different visible effect."
            assert(outcome()=="no-context");visibleOverride=nil
            liveID=15473
            local shadow=S.records["talent-spell:15473:1"].lines[1].source
                :gsub("{1}","15"):gsub("{2}","10"):gsub("{3}","50"):gsub("{4}","10")
            card("Shadowform",shadow)
            assert(S.Context(tip,data).key=="talent-spell:15473:1")
            assert(outcome()=="shown" and titleSeen=="ร่างเงา" and bodySeen:find("50%",1,true))
            S.settings.descriptions=false
            data.lines[2].leftText="Different healing restriction."
            assert(outcome()=="text-mismatch")
            data.lines[2].leftText=shadow
            assert(outcome()=="shown" and bodySeen=="")
            S.settings.descriptions=true
            liveID=24858
            local moonkin=S.records["talent-spell:24858:1"].lines[1].source
                :gsub("{1}","20"):gsub("{2}","360"):gsub("{3}","30"):gsub("{4}","3")
            local first,second=moonkin:match("^(.-)\n\n(.+)$")
            card("Moonkin Form",first,second)
            assert(outcome()=="shown" and titleSeen=="ร่าง Moonkin" and bodySeen:find("360%",1,true))
            data.lines[4]={leftText="Additional effect."}
            assert(outcome()=="missing")
            data.lines[4]=nil
            GameTooltip=tip
            function tip:SetShapeshift() end
            function tip:GetProcessingTooltipInfo() end
            local retry
            function hooksecurefunc(widget,method,callback)
                assert(widget==tip and method=="SetShapeshift")
                retry=callback
            end
            S.RegisterTooltips()
            tip:Show()
            retry(tip,3);assert(not S.reader:IsShown())
            retry(tip,2);assert(S.reader:IsShown() and titleSeen=="ร่าง Moonkin")
            tip:Hide();assert(not S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_basic_pet_tooltip_shows_only_verified_titles_on_hover_and_refresh(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua', 'Skills/Data.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('SlashCmdList={}')
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/Settings.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            local button=frame(UIParent)
            function button:GetID() return 3 end
            button.tooltipName="Attack"
            local currentOwner=button
            local mode, binding, quick, combat="0","",false,false
            function InCombatLockdown() return combat end
            function GetCVar(key) assert(key=="UberTooltips"); return mode end
            function KeybindFrames_InQuickKeybindMode() return quick end
            function GetBindingKey(action) assert(action=="BONUSACTIONBUTTON3"); return "CTRL-1","CTRL-2" end
            function GetBindingText(first,second)
                assert(first=="CTRL-1" and second=="CTRL-2")
                return binding
            end
            NORMAL_FONT_COLOR_CODE="|cffffd200"
            FONT_COLOR_CODE_CLOSE="|r"
            local action,isToken,spellID="PET_ACTION_ATTACK",true,nil
            PET_ACTION_ATTACK="Attack"
            function GetPetActionInfo(slot)
                assert(slot==3)
                return action,123,isToken,false,false,false,spellID
            end
            local left,right,count={"Attack"},{},1
            local function region(text)
                if text~=nil then return {IsShown=function() return true end,GetText=function() return text end} end
            end
            function tip:GetOwner() return currentOwner end
            function tip:NumLines() return count end
            function tip:GetLeftLine(index) return region(left[index]) end
            function tip:GetRightLine(index) return region(right[index]) end
            function S.RememberLongText(heading,body) titleSeen,bodySeen=heading,body end
            GameTooltip=tip
            PetActionBar={actionButtons={[3]=button}}
            function PetActionBar:UpdateCooldowns() tip:Fire("OnTooltipCleared") end
            combat=true
            event("ADDON_LOADED","Blizzard_ActionBar")
            assert(not button.hooks.OnEnter)
            combat=false
            event("PLAYER_REGEN_ENABLED")
            S.RegisterBasicPetTooltips()
            assert(#button.hooks.OnEnter==1 and hookCalls.UpdateCooldowns==1)
            tip:Show()
            local function shown(title)
                button:Fire("OnEnter")
                assert(S.reader:IsShown() and titleSeen==title and bodySeen=="")
            end
            local function hidden()
                button:Fire("OnEnter")
                assert(not S.reader:IsShown())
            end
            shown("โจมตี")
            binding="CTRL-1"
            left[1]="Attack|cffffd200 (CTRL-1)|r"
            S.settings.englishNames=true
            shown("โจมตี (Attack)")
            PetActionBar:UpdateCooldowns()
            assert(S.reader:IsShown() and bodySeen=="")
            left[1]="Attack|cffffd200 (CTRL-2)|r";hidden()
            binding="";left[1]="Attack"
            right[1]="Unrecognized right text";hidden();right[1]=nil
            count=2;left[2]="Unexpected command description.";hidden();count=1;left[2]=nil
            currentOwner=frame(UIParent);hidden();currentOwner=button
            PetActionBar.actionButtons[3]=frame(UIParent);hidden();PetActionBar.actionButtons[3]=button
            button.tooltipName="Follow";hidden();button.tooltipName="Attack"
            shown("โจมตี (Attack)");mode="1";hidden();mode="0"
            shown("โจมตี (Attack)");quick=true;hidden();quick=false
            shown("โจมตี (Attack)");combat=true;hidden();combat=false
            shown("โจมตี (Attack)");S.settings.enabled=false;hidden();S.settings.enabled=true
            S.settings.englishNames=false
            action,isToken,spellID="Bite",false,17253
            button.tooltipName="Bite"
            left={"Bite","Rank 4"};count=2
            function C_Spell.GetSpellSubtext(id) assert(id==17253); return "Rank 4" end
            shown("กัด")
            left[2]="Rank 5";hidden();left[2]="Rank 4"
            S.records["spell:17253"].requireDescriptionMatch=true;hidden()
            S.records["spell:17253"].requireDescriptionMatch=nil
            shown("กัด")
            Enum.TooltipDataType.PetAction=11
            mode="1";action,isToken,spellID="PET_ACTION_ATTACK",true,nil
            button.tooltipName="Attack"
            left={"Attack","Orders your pet to attack your current target."}
            data={type=11,lines={{leftText=left[1]},{leftText=left[2]}}}
            info={getterName="GetPetAction",getterArgs={3},tooltipData=data}
            assert(S.OnTooltip(tip,data)=="shown" and bodySeen:find("เป้าหมายปัจจุบัน",1,true))
            button:Fire("OnEnter")
            assert(S.reader:IsShown() and bodySeen:find("เป้าหมายปัจจุบัน",1,true))
            tip:Hide()
            assert(not S.reader:IsShown() and S.stats.errors==0)
        ''')

    def test_reviewed_class_spells_use_exact_ids_and_do_not_mix_feral_forms(self):
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            function S.RememberLongText(title,text) body=text end
            info.getterName="GetSpellByID"
            data.id=407632
            data.lines={{leftText="Hammer of the Righteous"},{leftText="Hammer the current target and up to 3 "..
                "additional nearby targets, causing Holy damage to each equal to 3 times the damage per second of "..
                "your main hand weapon. Cooldown shared with Crusader Strike."}}
            S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and body:find("เพิ่มเติมสูงสุด 3",1,true) and body:find("3 เท่า",1,true))
            data.id=409922;S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            data.id=414924
            data.lines={{leftText="Feral Charge (Cat)"},{leftText="Leap behind an enemy."}}
            S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and body:find("กระโจนไปด้านหลังศัตรู",1,true))
            assert(not body:find("ขัดจังหวะ",1,true))
            data.id=1238122;S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            data.id=414924;data.lines[1].leftText="Feral Charge (Bear)"
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
        ''')

    def test_feral_talent_card_matches_visible_ordered_forms_and_copies_values(self):
        self.lua.execute((ROOT / 'addon/ForeverThai/Skills/Data.lua').read_text(encoding='utf-8'),
                         'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            function S.RememberLongText(title,text) body=text end
            S.settings.original=false
            info.getterName="GetTraitEntry";info.getterArgs={10001,1}
            C_ClassTalents={GetActiveConfigID=function() return 300 end}
            C_Traits={GetEntryInfo=function(config, id)
                    assert(config==300 and id==10001);return {definitionID=400}
                end, GetDefinitionInfo=function(id) assert(id==400);return {spellID=1238122} end}
            local regions={}
            function tip:NumLines() return #data.lines end
            function tip:GetLeftLine(i) return regions[i] and regions[i].left end
            function tip:GetRightLine(i) return regions[i] and regions[i].right end
            local function setLine(i,left,right)
                data.lines[i]={leftText=left,rightText=right,lineIndex=i}
                regions[i]={left={GetText=function() return left end,IsShown=function() return true end}}
                if right then regions[i].right={GetText=function() return right end,IsShown=function() return true end} end
            end
            local bear="Charge an enemy, immobilizing them and interrupting any spell they are casting for 5 sec."
            setLine(1,"Feral Charge")
            setLine(2,"|CFFFF2020Requires Bear Form, Dire Bear Form|R"..string.char(10)..bear)
            setLine(3,"")
            setLine(4,"Feral Charge (Cat)")
            setLine(5,"9-24 yd range")
            setLine(6,"Instant","29 sec cooldown")
            setLine(7,"Requires Cat Form")
            S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and body:find("5 วินาที",1,true))
            assert(body:find("ระยะ 9–24 หลา",1,true) and body:find("คูลดาวน์ 29 วินาที",1,true))
            assert(body:find("ต้องอยู่ในร่างแมว",1,true) and not body:find("กระโจน",1,true))
            regions[1].left.GetText=function() return "Unrelated talent" end
            S.OnTooltip(tip,data);assert(not S.reader:IsShown());setLine(1,"Feral Charge")
            function tip:NumLines() return #data.lines+1 end
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            function tip:NumLines() return #data.lines end
            regions[4].right={GetText=function() return "Unexpected side text" end,IsShown=function() return true end}
            S.OnTooltip(tip,data);assert(not S.reader:IsShown());setLine(4,"Feral Charge (Cat)")
            local rightGetter=tip.GetRightLine
            tip.GetRightLine=function() error("region inaccessible") end
            S.OnTooltip(tip,data);assert(not S.reader:IsShown());tip.GetRightLine=rightGetter
            setLine(8,"Leap behind an enemy.");S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and body:find("กระโจนไปด้านหลังศัตรู",1,true))
            setLine(8,"Interrupts the enemy.");S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            setLine(8,"Leap behind an enemy.");setLine(4,"Feral Charge (Bear)")
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            setLine(4,"Feral Charge (Cat)");regions[6].right.GetText=function() return "Stale cooldown" end
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            data.lines={}
            setLine(1,"Feral Charge")
            setLine(2,"|CFFFFFFFFRequires Bear Form, Dire Bear Form|R")
            setLine(3,bear);setLine(4,"Feral Charge (Cat)");setLine(5,"Requires Cat Form")
            S.OnTooltip(tip,data);assert(S.reader:IsShown() and not body:find("คูลดาวน์",1,true))
            setLine(2,"Unexpected preface");setLine(3,"Requires Bear Form, Dire Bear Form "..bear)
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            data.lines={};setLine(1,"Feral Charge")
            setLine(2,"Requires Bear Form, Dire Bear Form "..bear.." Feral Charge (Cat) Requires Cat Form")
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            setLine(2,"Requires Bear Form, Dire Bear Form "..bear)
            setLine(3,"Requires Cat Form");setLine(4,"Feral Charge (Cat)")
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            data.lines={}
            setLine(1,"Feral Charge");setLine(2," ")
            setLine(3,"Requires Bear Form, Dire Bear Form "..bear)
            setLine(4,"Feral Charge (Cat)");setLine(5,"Requires Cat Form")
            table.remove(data.lines,1);table.remove(data.lines,1)
            function tip:NumLines() return 5 end
            function tip:GetOwner()
                return {GetName=function() return "Feral Charge" end,GetEntryID=function() return 10001 end,
                    GetTalentFrame=function() return {GetConfigID=function() return 300 end} end}
            end
            S.OnTooltip(tip,data);assert(S.reader:IsShown())
            local function addSuffix(text)
                regions[6]={left={GetText=function() return text end,IsShown=function() return true end}}
                function tip:NumLines() return 6 end
            end
            addSuffix("Requires all preceding talents")
            local requirements=S.TalentRequirements(tip,data)
            assert(requirements.limit==5 and S.OnTooltip(tip,data,requirements)=="shown")
            assert(body:find("ต้องเรียนพรสวรรค์ก่อนหน้าที่เชื่อมมาทั้งหมด",1,true))
            addSuffix("Leap behind an enemy.")
            assert(not S.TalentRequirements(tip,data) and S.OnTooltip(tip,data)=="no-context")
            function tip:NumLines() return 5 end
            regions[2].left.GetText=function() return "Unexpected visible restriction" end
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
            assert(S.stats.errors==0)
        ''')

    def test_stale_slot_or_tooltip_identity_does_not_supply_metadata(self):
        self.lua.execute('''
            primary={tooltipData=data};assert(not metadata());primary=nil
            info.tooltipData={id=101};assert(not metadata());info.tooltipData=data
            entry.spellID=202;assert(not metadata());entry.spellID=101
            entry.name="Changed";assert(not metadata());entry.name="Recipe A"
            entry.itemType=4;assert(not metadata());entry.itemType=1
            info.getterArgs={7,9};assert(not metadata());info.getterArgs={7,0}
            info.getterName="GetSpellByID";assert(not metadata())
            assert(calls==0)
        ''')

    def test_missing_and_secret_values_fall_back_independently(self):
        self.lua.execute('''
            local hidden=trap();secret[hidden]=true
            entry.subName=hidden;assert(metadata()=="เลเวลที่เรียนสกิล 24")
            entry.subName="Rank 2";learnLevel=hidden;assert(metadata()=="แรงก์ 2")
            entry.subName="Passive";learnLevel=0;assert(not metadata())
            entry=hidden;assert(not metadata())
        ''')

    def test_only_visible_matching_simple_cost_is_translated(self):
        self.lua.execute('''
            Enum.PowerType={Mana=0,Rage=1,Focus=2,Energy=3}
            costs={{type=0,cost=35,minCost=35,costPercent=0,costPerSec=0,requiredAuraID=0}}
            C_SpellBook.GetSpellBookItemPowerCost=function(slot,bank)
                assert(slot==7 and bank==0);return costs
            end
            table.insert(data.lines,2,{leftText="35 Mana"})
            function S.RememberLongText(title,text) body=text end
            S.OnTooltip(tip,data)
            assert(body:find("ใช้มานา 35",1,true))
            assert(body:find("ฟื้นฟูพลังชีวิต 10",1,true))
            for _,line in ipairs({"34 Mana","35 Rage","35% Mana","35 Mana per sec","Instant"}) do
                data.lines[2].leftText=line
                assert(not metadata():find("ใช้",1,true))
            end
            data.lines[2].leftText="35 Mana"
            local hidden=trap();secret[hidden]=true
            table.insert(data.lines,2,{leftText=hidden})
            assert(not metadata():find("ใช้",1,true))
            table.remove(data.lines,2)
            table.insert(data.lines,1,{leftText=hidden})
            assert(not metadata():find("ใช้",1,true))
            table.remove(data.lines,1)
            entry.itemType=Enum.SpellBookItemType.FutureSpell
            assert(not metadata():find("ใช้",1,true))
            assert(S.stats.errors==0)
        ''')

    def test_optional_conditional_multi_resource_or_inaccessible_cost_is_omitted(self):
        self.lua.execute('''
            Enum.PowerType={Mana=0}
            table.insert(data.lines,2,{leftText="35 Mana"})
            local base={type=0,cost=35,minCost=35,costPercent=0,costPerSec=0,requiredAuraID=0}
            local values={base}
            C_SpellBook.GetSpellBookItemPowerCost=function() return values end
            for field,value in pairs({minCost=15,costPercent=10,costPerSec=2,requiredAuraID=123}) do
                local old=base[field];base[field]=value
                assert(not metadata():find("ใช้",1,true))
                base[field]=old
            end
            values[2]=base;assert(not metadata():find("ใช้",1,true));values[2]=nil
            local hidden=trap();secret[hidden]=true
            base.cost=hidden;assert(not metadata():find("ใช้",1,true))
            values=hidden;assert(not metadata():find("ใช้",1,true))
            C_SpellBook.GetSpellBookItemPowerCost=function() error("cost unavailable") end
            assert(not metadata():find("ใช้",1,true))
        ''')

    def test_fixed_range_uses_exact_spell_and_current_raw_line(self):
        self.lua.execute('''
            local spell={spellID=101,name="Recipe A",minRange=0,maxRange=40}
            C_Spell={GetSpellInfo=function(id) assert(id==101);return spell end}
            local line={leftText="35 Mana",rightText="40 yd range"}
            table.insert(data.lines,2,line)
            function S.RememberLongText(title,text) body=text end
            S.OnTooltip(tip,data)
            assert(body:find("ระยะ 40 หลา",1,true) and body:find("ฟื้นฟูพลังชีวิต 10",1,true))
            line.leftText,line.rightText="40 yd range",nil
            assert(metadata():find("ระยะ 40 หลา",1,true))
            line.rightText="40 yd range";assert(not metadata():find("ระยะ",1,true))
            line.leftText="35 Mana"
            for _,text in ipairs({"41 yd range","8-40 yd range","Melee Range","40.5 yd range"}) do
                line.rightText=text
                assert(not metadata():find("ระยะ",1,true))
            end
            line.rightText="40 yd range"
            local hidden=trap();secret[hidden]=true
            for field,value in pairs({spellID=102,name="Other",minRange=8,maxRange=hidden}) do
                local old=spell[field];spell[field]=value
                assert(not metadata():find("ระยะ",1,true))
                spell[field]=old
            end
            line.rightText=hidden;assert(not metadata():find("ระยะ",1,true))
            line.rightText="40 yd range"
            line.leftText=hidden;assert(not metadata():find("ระยะ",1,true));line.leftText="35 Mana"
            table.insert(data.lines,2,{leftText=hidden})
            assert(not metadata():find("ระยะ",1,true));table.remove(data.lines,2)
            entry.itemType=Enum.SpellBookItemType.FutureSpell
            assert(not metadata():find("ระยะ",1,true))
        ''')
