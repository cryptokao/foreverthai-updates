from pathlib import Path
import unittest

import test_recipe_panel

ROOT = Path(__file__).resolve().parents[1]


class ItemTooltipTests(unittest.TestCase):
    def setUp(self):
        test_recipe_panel.RecipePanelTests.setUp(self)
        for module in ('Data', 'ItemEffects', 'Tooltip'):
            source = (ROOT / 'addon/ForeverThai/Skills' / (module + '.lua')).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            Enum={TooltipDataType={Item=0},TooltipDataLineType={ItemName=22,
                NestedBlock=19,ItemEnchantmentPermanent=15,GemSocketEnchantment=30,
                ItemSpellTriggerOnUse=44,ItemSpellTriggerOnEquip=45,ItemSpellTriggerOnProc=46}}
            ITEM_SPELL_TRIGGER_ONUSE="Use:"
            tip=frame(UIParent)
            info={append=true} -- Same primary and processing block, as in a shopping tooltip.
            function tip:GetProcessingTooltipInfo() return info end
            function tip:GetPrimaryTooltipInfo() return primary or info end
            function tip:NumLines() return #data.lines end
            local regions={}
            function tip:GetLeftLine(i) return regions[i] end
            function setData(id, name, kind, text)
                data={type=0,id=id,lines={}}
                info.tooltipData=data
                setLine(1,22,name)
                setLine(2,kind,text)
            end
            function setLine(i,kind,text)
                data.lines[i]={type=kind,leftText=text,lineIndex=i}
                regions[i]={GetText=function() return text end,IsShown=function() return true end}
            end
            -- A compiled healing effect with an item ID distinct from the root SpellID.
            for id,item in pairs(S.itemEffects) do
                local keys=item.triggers[0]
                if keys and #keys==1 and S.records[keys[1]].originalName=="Healing Potion" then
                    itemId,itemName,key=id,item.name,keys[1];break
                end
            end
            assert(itemId and key)
            setData(itemId,itemName,44,"Use: Restores 1,234.5 health.")
        ''')

    def test_real_compiled_effect_through_tooltip_callback(self):
        self.lua.execute('''
            S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and S.stats.errors==0)
            local heading,text=S.ItemTranslation(tip,data)
            assert(heading==itemName and text:find("เมื่อใช้",1,true))
            assert(text:find("ฟื้นฟูพลังชีวิต 1,234.5",1,true))
            assert(not text:find("Use: Restores 1,234.5 health.",1,true))
            assert(tip:GetLeftLine(2):GetText()==data.lines[2].leftText)
            tip:Hide();assert(not S.reader:IsShown())
            S.OnTooltip(tip,data);assert(S.reader:IsShown())
            tip:Fire("OnTooltipCleared");assert(not S.reader:IsShown())
        ''')

    def test_wrong_kind_wrong_item_and_replaced_live_text_fall_back(self):
        self.lua.execute('''
            for _,kind in ipairs({0,19,37,38,45,46}) do
                setLine(2,kind,"Use: Restores 1,234.5 health.")
                assert(not S.ItemTranslation(tip,data))
            end
            setLine(2,44,"Use: Restores 1,234.5 health.")
            data.id=439;assert(not S.ItemTranslation(tip,data));data.id=itemId
            setLine(1,22,"Different item");assert(not S.ItemTranslation(tip,data))
            setLine(1,22,itemName)
            tip:GetLeftLine(2).GetText=function() return "Use: Restores 9 health." end
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_exact_wrapper_and_full_body_required(self):
        self.lua.execute('''
            ITEM_SPELL_TRIGGER_ONUSE=nil
            assert(not S.ItemTranslation(tip,data))
            setLine(2,44,"Restores 1,234.5 health.");assert(S.ItemTranslation(tip,data))
            ITEM_SPELL_TRIGGER_ONUSE="Action [%s]"
            setLine(2,44,"Action [Restores 12 health.]");assert(S.ItemTranslation(tip,data))
            setLine(2,44,"Action [Restores 12 health.] (3 min cooldown)");assert(not S.ItemTranslation(tip,data))
            ITEM_SPELL_TRIGGER_ONUSE="Action [%s]%s"
            setLine(2,44,"Action [Restores 12 health.]");assert(not S.ItemTranslation(tip,data))
        ''')

    def test_reviewed_base_casts_require_full_native_text_and_preserve_visible_values(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            function tip:GetRightLine() end
            local function translation(id,name,text)
                setData(id,name,44,"Use: "..text)
                local title,body=S.ItemTranslation(tip,data)
                assert(title==name and body)
                return body
            end
            local function rejected()
                assert(not S.ItemTranslation(tip,data))
            end
            local swift="Increases run speed by 50% for 15 sec."
            assert(translation(2459,"Swiftness Potion",swift):find("50% เป็นเวลา 15 วินาที",1,true))
            assert(S.OnTooltip(tip,data)=="shown")
            setLine(3,44,"Use: "..swift);rejected();data.lines[3]=nil
            setLine(2,44,"Use: Increases run speed by 50%.");rejected()
            setLine(2,44,"Use: "..swift.." An extra effect.");rejected()
            assert(translation(6372,"Swim Speed Potion","Increases swim speed by 100% for 20 sec."):
                find("ว่ายน้ำ 100% เป็นเวลา 20 วินาที",1,true))
            local marbles="Decreases target's chance to hit with attacks by 25% for 10 sec."
            assert(translation(1191,"Bag of Marbles",marbles):find("25% เป็นเวลา 10 วินาที",1,true))
            setLine(2,44,"Use: "..marbles:gsub("25%%","-25%%"));rejected()
            local crystal="A crystal shield surrounds the friendly target, doing 12 damage to anyone who hits %s. Lasts 10 min."
            local him=translation(11567,"Crystal Spire",crystal:format("him"))
            local her=translation(11567,"Crystal Spire",crystal:format("her"))
            assert(him==her and her:find("12 หน่วย",1,true) and her:find("10 นาที",1,true))
            local soul="Stores the friendly target's soul. If the target dies while their soul is stored, " ..
                "they will be able to resurrect with %s health and %s mana."
            for _,item in ipairs({
                {5232,"Minor Soulstone"},{16892,"Lesser Soulstone"},{16893,"Soulstone"},
                {16895,"Greater Soulstone"},{16896,"Major Soulstone"},
            }) do
                local body=translation(item[1],item[2],soul:format("1,123","1,789"))
                assert(body:find("พลังชีวิต 1,123 หน่วยและมานา 1,789 หน่วย",1,true))
                setLine(2,44,"Use: "..soul:format("-400","700"));rejected()
                setLine(2,44,"Use: "..soul:format("400","$3026q1"));rejected()
                setLine(2,44,"Use: Soul is stored.");rejected()
            end
        ''')

    def test_reviewed_item_cast_cooldown_suffix_requires_complete_matching_use_line(self):
        self.lua.execute('''
            function tip:GetRightLine() end
            local function line(id,name,text)
                setData(id,name,44,"Use: "..text)
                local title,body=S.ItemTranslation(tip,data)
                if title then assert(title==name) end
                return body
            end
            local cloak="Gives invisibility for 10 sec."
            for _,entry in ipairs({
                {4397,"Gnomish Cloaking Device"},{260806,"Emergency Field Cloak"},
            }) do
                local body=line(entry[1],entry[2],cloak.." (1 hour Cooldown)")
                assert(body:find("ล่องหนเป็นเวลา 10 วินาที",1,true) and body:find("คูลดาวน์ 1 ชั่วโมง",1,true))
                body=line(entry[1],entry[2],cloak.." (2 Hours Cooldown)")
                assert(body:find("คูลดาวน์ 2 ชั่วโมง",1,true))
                body=line(entry[1],entry[2],cloak)
                assert(body and not body:find("คูลดาวน์",1,true))
                for _,suffix in ipairs({" (1 hours Cooldown)"," (0 Min Cooldown)",
                    " (1 Hour Cooldown) Remaining"," (1.5 Hour Cooldown)"," (Cooldown remaining: 20 sec)"}) do
                    assert(not line(entry[1],entry[2],cloak..suffix))
                end
                assert(not line(entry[1],entry[2],"Gives invisibility. (1 Hour Cooldown)"))
            end
            for _,id in ipairs({2459,287975,288898}) do
                local body=line(id,"Swiftness Potion","Increases run speed by 50% for 15 sec. (2 Min Cooldown)")
                assert(body:find("50% เป็นเวลา 15 วินาที",1,true) and body:find("คูลดาวน์ 2 นาที",1,true))
            end
            assert(not line(2459,"Another Potion","Increases run speed by 50% for 15 sec. (2 Min Cooldown)"))
        ''')

    def test_hearthstone_requires_the_current_public_bind_location(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            function tip:GetRightLine() end
            local destination="Lion's Pride Inn"
            function GetBindLocation() return destination end
            local function use(location)
                return "Use: Returns you to "..location..
                    ". Speak to an Innkeeper in a different place to change your home location. (30 Min Cooldown)"
            end
            setData(6948,"Hearthstone",44,use(destination))
            local title,body=S.ItemTranslation(tip,data)
            assert(title=="Hearthstone" and body:find(destination,1,true) and body:find("คูลดาวน์ 30 นาที",1,true))
            assert(S.OnTooltip(tip,data)=="shown")
            assert(tip:GetLeftLine(2):GetText()==use(destination))
            destination="Stonard"
            assert(not S.ItemTranslation(tip,data))
            setLine(2,44,use(destination))
            title,body=S.ItemTranslation(tip,data)
            assert(title=="Hearthstone" and body:find(destination,1,true))
            setLine(2,44,use(destination):gsub("Speak to an Innkeeper","Speak to a Guard"))
            assert(not S.ItemTranslation(tip,data))
            setData(282006,"Hearthstone",44,use(destination))
            assert(not S.ItemTranslation(tip,data))
            setData(6948,"Hearthstone",45,use(destination))
            assert(not S.ItemTranslation(tip,data))
            destination="|cffffffffStonard|r"
            setData(6948,"Hearthstone",44,use(destination))
            assert(not S.ItemTranslation(tip,data))
            destination="Stonard"
            setLine(2,44,use(destination))
            GetBindLocation=function() return "restricted location" end
            issecretvalue=function(value) return value=="restricted location" end
            assert(not S.ItemTranslation(tip,data))
            GetBindLocation=nil
            assert(not S.ItemTranslation(tip,data))
            GetBindLocation=function() error("unavailable") end
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_faction_items_translate_only_the_complete_displayed_branch(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            function tip:GetRightLine() end
            local function use(id,name,line,expected)
                local live="Use: "..line
                setData(id,name,44,live)
                local title,body=S.ItemTranslation(tip,data)
                assert(title==name and body:find(expected,1,true))
                assert(S.OnTooltip(tip,data)=="shown" and tip:GetLeftLine(2):GetText()==live)
                setLine(2,44,live.." Additional clause.")
                assert(not S.ItemTranslation(tip,data))
            end
            for _,sample in ipairs({{"Orgrimmar","ออร์กริมมาร์"},{"Stormwind","สตอร์มวินด์"}}) do
                use(282006,"Crumbling Hearthstone","Returns you to "..sample[1]..". Single-use.",sample[2].." ใช้ได้ครั้งเดียว")
            end
            setData(282006,"Crumbling Hearthstone",44,"Use: Returns you to Orgrimmar.")
            assert(not S.ItemTranslation(tip,data))
            setLine(2,44,"Use: Returns you to Darnassus. Single-use.")
            assert(not S.ItemTranslation(tip,data))
            local receipt="Slap a forged delivery receipt onto an empty Waylaid Crate, allowing you to return it to the %s for +%s reputation."
            for _,faction in ipairs({"Durotar Supply and Logistics","Azeroth Commerce Authority"}) do
                use(262902,"Forged Delivery Receipt",receipt:format(faction,"50"),faction)
            end
            for _,value in ipairs({"-50","0","1.5"}) do
                setLine(2,44,"Use: "..receipt:format("Durotar Supply and Logistics",value))
                assert(not S.ItemTranslation(tip,data))
            end
            local sign="Add this profession's sign to your %s toy for all characters on your account. Characters that wish to display this sign must have that profession."
            for i,name in ipairs({"Alchemy","Blacksmithing","Cooking","Enchanting","Engineering","Leatherworking","Tailoring"}) do
                use(270876+i,name.." Sign",sign:format("Orcish Tradeskill Sign"),"ป้ายวิชาชีพของออร์ค")
                use(270876+i,name.." Sign",sign:format("Dwarven Tradeskill Sign"),"ป้ายวิชาชีพของคนแคระ")
                setLine(2,44,"Use: "..sign:format("Dwarven Tradeskill Sign"))
                local _,body=S.ItemTranslation(tip,data)
                assert(body:find(string.char(10).."ตัวละครที่ต้องการแสดงป้ายนี้",1,true))
            end
            setData(270877,"Alchemy Sign",44,"Use: Add this profession's sign to your Orcish Tradeskill Sign toy for all characters on your account.")
            assert(not S.ItemTranslation(tip,data))
            setData(270878,"Alchemy Sign",44,"Use: "..sign:format("Orcish Tradeskill Sign"))
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_waylaid_supplies_preserves_the_visible_amount_and_ingredient_identity(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            function tip:GetRightLine() end
            local namePrefix="Waylaid Supplies: "
            local line="Use: Add %s %s to complete the shipment."
            for _,sample in ipairs({
                {210771,"20","Copper Bars","ทองแดง 20 แท่ง"},
                {211819,"12","Bronze Bars","สำริด 12 แท่ง"},
                {220930,"8","Major Healing Potions","ยาฟื้นฟูพลังชีวิตขั้นเอก 8 ขวด"},
            }) do
                local id,amount,ingredient,expected=unpack(sample)
                local live=line:format(amount,ingredient)
                setData(id,namePrefix..ingredient,44,live)
                local title,body=S.ItemTranslation(tip,data)
                assert(title==namePrefix..ingredient and body:find(expected,1,true))
                assert(S.OnTooltip(tip,data)=="shown" and tip:GetLeftLine(2):GetText()==live)
            end
            setData(210771,namePrefix.."Copper Bars",44,line:format("24","Copper Bars"))
            local _,body=S.ItemTranslation(tip,data)
            assert(body:find("ทองแดง 24 แท่ง",1,true))
            for _,invalid in ipairs({"0","-20","1.5"}) do
                setLine(2,44,line:format(invalid,"Copper Bars"))
                assert(not S.ItemTranslation(tip,data))
            end
            setLine(2,44,line:format("20","Bronze Bars"))
            assert(not S.ItemTranslation(tip,data))
            setLine(2,44,"Use: Add 20 Copper Bars.")
            assert(not S.ItemTranslation(tip,data))
            setData(215394,namePrefix.."Lesser Stoneshield Potions",44,line:format("20","Copper Bars"))
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_stock_crate_preserves_order_and_each_visible_bundle_amount(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            function tip:GetRightLine() end
            local intro="Use: Fill the crate with any bundle from the following list:"
            local list="\n- 19 Copper Bar\n- 20 Tin Bar\n- 10 Bronze Bar"
            local item="Waylaid Crate: Apprentice Ingots"
            local expected="เมื่อใช้ — เติมเสบียงลงลัง\nเลือกวัตถุดิบหนึ่งชุดจากรายการต่อไปนี้เพื่อเติมลัง"..
                "\n- ทองแดง 19 แท่ง\n- ดีบุก 20 แท่ง\n- สำริด 10 แท่ง"
            for _,live in ipairs({intro..list,intro.."|cnIQ1:"..list,intro.."|cnIQ1:"..list.."|r"}) do
                setData(248703,item,44,live)
                local title,body=S.ItemTranslation(tip,data)
                assert(title==item and body==expected)
                assert(S.OnTooltip(tip,data)=="shown" and tip:GetLeftLine(2):GetText()==live)
            end
            for _,invalid in ipairs({
                "\n- 19 Copper Bar\n- 20 Tin Bar",
                "\n- 20 Tin Bar\n- 19 Copper Bar\n- 10 Bronze Bar",
                "\n- 19 Copper Bar\n- 20 Tin Bar\n- 10 Bronze Bar\n- 1 Iron Bar",
                "\n- 0 Copper Bar\n- 20 Tin Bar\n- 10 Bronze Bar",
                "\n- 19/20 Copper Bar\n- 20 Tin Bar\n- 10 Bronze Bar",
                "|cnIQ2:"..list.."|r",
                list.."|r",
            }) do
                setData(248703,item,44,intro..invalid)
                assert(not S.ItemTranslation(tip,data))
            end
            setData(248704,item,44,intro..list)
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_scoped_item_use_text_keeps_visible_mechanics_and_requirements(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute(r'''
            fontOK=false
            function tip:GetRightLine() end
            local function use(id,name,line,expected)
                local live="Use: "..line
                setData(id,name,44,live)
                local title,body=S.ItemTranslation(tip,data)
                assert(title==name and body:find(expected,1,true))
                assert(S.OnTooltip(tip,data)=="shown" and tip:GetLeftLine(2):GetText()==live)
                return body
            end
            use(213564,"Scroll of Minor Evocation","Restores 302 Mana over 4 sec.","302 หน่วยตลอด 4 วินาที")
            setLine(2,44,"Use: Restores Mana over 4 sec.")
            assert(not S.ItemTranslation(tip,data))
            use(276337,"Thaelemaches' Talisman","Fear all Demons within 15 yds for 6 sec.","15 หลา")
            setLine(2,44,"Use: Fear all enemies within 15 yds for 6 sec.")
            assert(not S.ItemTranslation(tip,data))
            for _,who in ipairs({"him","her"}) do
                use(18802,"Shadowy Potion","Infuses imbiber with a taint of shadow, making "..who..
                    " friendly to the denizens of Jaedenar. Lasts 20 minutes.","เจเดนาร์")
            end
            local venom="Gain %s doses of Venomous Blood. Whenever you suffer Bleed damage, one dose is spread "..
                "to a nearby enemy within 8 yds. Lasts up to 20 sec.\n\nVenomous Blood deals 325 Nature damage per dose when it expires."
            use(250950,"Potion of Venomous Blood",venom:format("10"),"10 โดส")
            setLine(2,44,"Use: "..venom:format("1.5"))
            assert(not S.ItemTranslation(tip,data))
            use(744,"Thunderbrew's Boot Flask","Deals 75 Fire damage every 1 sec for 5 sec to all enemies in front of you. "..
                "Deals 2 times as much damage to Plants. Gets you quite drunk too!","2 เท่า")
            local action="Throw a handful into the campfire, transforming its flames."
            local requirement="Requires WoW: Forever Launch Celebration"
            local suffix=" (30 Min Cooldown)"
            for _,line in ipairs({action.."\n"..requirement,action..requirement,
                action.."\n|cFFffffff"..requirement.." |r",action.."\n|cffffffff"..requirement.."|r"}) do
                local body=use(289439,"Pouch of Violet Dust",line..suffix,"ช่วงงานฉลองเปิดตัว WoW: Forever")
                assert(body:find("30 นาที",1,true))
            end
            for _,line in ipairs({action,action.." Requires another event",
                action.."\n|cffff2020"..requirement.."|r"}) do
                setLine(2,44,"Use: "..line..suffix)
                assert(not S.ItemTranslation(tip,data))
            end
            setData(289438,"Pouch of Violet Dust",44,"Use: "..action.."\n"..requirement)
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_linked_item_use_text_uses_visible_branch_and_feast_values(self):
        self.lua.execute(r'''
            function tip:GetRightLine() end
            local function use(id,name,line)
                setData(id,name,44,"Use: "..line)
                local title,body=S.ItemTranslation(tip,data)
                assert(title==name and body)
                return body
            end
            local body=use(286405,"Blooming Heart","They love me... (3 Sec Cooldown)")
            assert(body:find("เขารักฉัน...",1,true) and body:find("3 วินาที",1,true))
            body=use(286405,"Blooming Heart","They love me not...")
            assert(body:find("เขาไม่รักฉัน...",1,true))
            setLine(2,44,"Use: They love me not... Another clause.")
            assert(not S.ItemTranslation(tip,data))

            local lead="Serve a delicious feast that lasts for 3 min and serves up to 40 players."
            local food="Food\nRestores 2,452 health over 30 sec. Must remain seated while eating. "..
                "If you spend at least 10 sec eating you will become Well Fed and gain "..
                "20 Attack Power, 23 Spell Damage, 44 Healing Power, and 10 Stamina for 45 min."
            body=use(238641,"Specklefin Feast",lead.."\n\n|T134062:16:16|t "..food.." (5 Min Cooldown)")
            assert(body:find("ผู้เล่นได้สูงสุด 40 คน",1,true) and body:find("2,452 หน่วย",1,true))
            assert(body:find("พลังการรักษา 44",1,true) and body:find("คูลดาวน์ 5 นาที",1,true))
            body=use(238642,"Grand Lobster Banquet",lead.."\n\n"..food:gsub("2,452","425"))
            assert(body:find("425 หน่วย",1,true) and body:find("ผลอิ่มท้อง",1,true))
            for _,bad in ipairs({lead,lead.."\n\n|T1:16:16|t "..food,lead.." "..food:gsub("44 Healing","44 Damage")}) do
                setLine(2,44,"Use: "..bad)
                assert(not S.ItemTranslation(tip,data))
            end
        ''')

    def test_equipment_proc_text_keeps_the_displayed_scope_and_healing_choices(self):
        self.lua.execute(r'''
            function tip:GetRightLine() end
            ITEM_SPELL_TRIGGER_ONEQUIP="Equip:"
            local mail="Equip: When struck in combat has a 5.5% chance to make you invulnerable to melee damage for 4 sec. "..
                "This effect can only occur once every 11 sec."
            setData(12641,"Invulnerable Mail",45,mail)
            local title,body=S.ItemTranslation(tip,data)
            assert(title=="Invulnerable Mail" and body:find("5.5%",1,true) and body:find("4 วินาที",1,true))
            assert(body:find("ระยะประชิด",1,true) and body:find("11 วินาที",1,true))
            setLine(2,45,mail:gsub("melee damage","all damage"))
            assert(not S.ItemTranslation(tip,data))
            setData(227876,"Invulnerable Mail",45,mail)
            assert(not S.ItemTranslation(tip,data))
            local prefix="Equip: Your casts of "
            local tail=" in combat grant up to 41 increased healing and up to 14 increased damage for 16 sec."
            for _,choice in ipairs({
                {"Greater Heal","มหาเวทรักษา"},{"Healing Touch","สัมผัสเยียวยา"},
                {"Healing Wave","คลื่นรักษา"},{"Holy Light","แสงศักดิ์สิทธิ์"},
                {"Greater Heal, Healing Touch, Healing Wave, or Holy Light",
                    "มหาเวทรักษา สัมผัสเยียวยา คลื่นรักษา หรือแสงศักดิ์สิทธิ์"},
            }) do
                setData(249473,"Dormant Heart of the Mountain",45,prefix..choice[1]..tail)
                title,body=S.ItemTranslation(tip,data)
                assert(title=="Dormant Heart of the Mountain" and body:find(choice[2],1,true))
                assert(body:find("สูงสุด 41 หน่วย",1,true) and body:find("สูงสุด 14 หน่วย",1,true))
            end
            setLine(2,45,prefix.."Lesser Heal"..tail)
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_quick_draw_equip_uses_the_complete_verified_granted_spell(self):
        self.lua.execute(r'''
            function tip:GetRightLine() end
            ITEM_SPELL_TRIGGER_ONEQUIP="Equip:"
            local lead="Equip: Gain the Quick Draw ability:"
            local detail="Draw your ranged weapon and fire a quick shot at an enemy, causing normal ranged weapon damage "..
                "and reducing the target's movement speed by 51% for 7 sec. Awards 2 combo points.\n\n"..
                "Quick Draw benefits from all talents and effects that trigger from or modify Sinister Strike."
            setData(202256,"Privateer's Ornate Pistol",45,lead.."\n\n|T134536:16:16|t\n"..detail)
            local title,body=S.ItemTranslation(tip,data)
            assert(title=="Privateer's Ornate Pistol" and body:find("51% เป็นเวลา 7 วินาที",1,true))
            assert(body:find("2 แต้มคอมโบ",1,true) and body:find("ฟันอำมหิต",1,true))
            setLine(2,45,lead.." "..detail:gsub("51%%","-51%%"))
            assert(not S.ItemTranslation(tip,data))
            setLine(2,45,lead.."\n|T1:16:16|t\n"..detail)
            assert(not S.ItemTranslation(tip,data))
            setLine(2,45,lead)
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_meal_use_tooltips_preserve_the_displayed_healing_and_linked_buff(self):
        self.lua.execute('''
            function tip:GetRightLine() end
            local prefix="Use: Restores 1,234.5 health over 27 sec. Must remain seated while eating. "
            for _,sample in ipairs({
                {232436,"Darkclaw Bisque","If you eat for 10 seconds will also increase your Spell Damage by 12 for 10 min.",
                    "เมื่อกินครบ 10 วินาที ความเสียหายเวทจะเพิ่มขึ้น 12 หน่วย"},
                {232438,"Smoked Redgill","If you eat for 10 seconds will also increase your Healing done by 22 for 10 min.",
                    "เมื่อกินครบ 10 วินาที ผลการรักษาที่ทำได้จะเพิ่มขึ้น 22 หน่วย"},
                {11950,"Windblossom Berries","Also increases your Stamina by 10 for 10 min.",
                    "และเพิ่มค่าความทนทาน 10 หน่วย"},
            }) do
                local id,name,tail=sample[1],sample[2],sample[3]
                local live=prefix..tail
                setData(id,name,44,live)
                local title,body=S.ItemTranslation(tip,data)
                assert(title==name and body:find("ฟื้นฟูพลังชีวิต 1,234.5 หน่วยในเวลา 27 วินาที",1,true))
                assert(body:find(sample[4].."เป็นเวลา 10 นาที",1,true))
                assert(tip:GetLeftLine(2):GetText()==live)
                setLine(2,44,prefix);assert(not S.ItemTranslation(tip,data))
                setLine(2,44,prefix..tail:gsub("for 10 min","for -10 min"))
                assert(not S.ItemTranslation(tip,data))
                setLine(2,44,prefix..tail:gsub("by ","by -"))
                assert(not S.ItemTranslation(tip,data))
            end
            setData(232436,"Darkclaw Bisque",44,prefix..
                "If you eat for 9 seconds will also increase your Spell Damage by 12 for 10 min.")
            assert(not S.ItemTranslation(tip,data))
            setData(232438,"Smoked Redgill",44,prefix..
                "If you eat for 10 seconds will also increase your Spell Damage by 12 for 10 min.")
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_mage_scrolls_keep_displayed_damage_radius_and_level_cap(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            function tip:GetRightLine() end
            for _,sample in ipairs({
                {217495,"Scroll of Cryoblast","yard","42 to 57","115 to 129"},
                {277499,"Scroll of Greater Cryoblast","yd","340 to 459","448 to 568"},
            }) do
                for _,damage in ipairs({sample[4],sample[5]}) do
                    local live="Use: Inflicts "..damage.." Frost damage in a 5 "..sample[3].." radius. (1 Min Cooldown)"
                    setData(sample[1],sample[2],44,live)
                    local title,body=S.ItemTranslation(tip,data)
                    local expected=damage:gsub(" to "," ถึง ")
                    assert(title==sample[2] and body:find(expected.." หน่วยในรัศมี 5 หลา",1,true))
                    assert(body:find("คูลดาวน์ 1 นาที",1,true) and S.OnTooltip(tip,data)=="shown")
                    assert(tip:GetLeftLine(2):GetText()==live)
                    setLine(2,44,live:gsub("Frost","Fire"))
                    assert(not S.ItemTranslation(tip,data))
                end
                for _,damage in ipairs({"129 to 115","0","-12","$s1","[42 to 57]"}) do
                    setData(sample[1],sample[2],44,"Use: Inflicts "..damage.." Frost damage in a 5 "..sample[3].." radius.")
                    assert(not S.ItemTranslation(tip,data))
                end
            end
            local name="Scroll of Rebuke Elemental"
            local prefix="Use: Increases damage the target Elemental takes from your spells by 15% for 20 sec."
            setData(277491,name,44,prefix.." Only affects enemies level 50 and below. (5 Sec Cooldown)")
            local title,body=S.ItemTranslation(tip,data)
            assert(title==name and body:find("15% เป็นเวลา 20 วินาที",1,true))
            assert(body:find("เลเวล 50 หรือต่ำกว่าเท่านั้น",1,true) and S.OnTooltip(tip,data)=="shown")
            for _,suffix in ipairs({"", " Only affects enemies level 50.5 and below.",
                                    " Only affects enemies level 50 and above."}) do
                setLine(2,44,prefix..suffix)
                assert(not S.ItemTranslation(tip,data))
            end
            assert(not S.records["aura:1302301"])
        ''')

    def test_camping_items_use_displayed_bonus_shape_and_matching_faction(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            function tip:GetRightLine() end
            local footer=" Requires a Campfire nearby. All camping features share a cooldown of 47 min."
            local function use(id,name,body,expected,exclusion)
                local live="Use: "..body..footer
                setData(id,name,44,live)
                local title,thai=S.ItemTranslation(tip,data)
                assert(title==name and thai:find(expected,1,true) and thai:find(exclusion,1,true))
                assert(thai:find("47 นาที",1,true) and S.OnTooltip(tip,data)=="shown")
                assert(tip:GetLeftLine(2):GetText()==live)
                setLine(2,44,"Use: "..body)
                assert(not S.ItemTranslation(tip,data))
                setLine(2,44,"Use: "..body..footer:gsub("Campfire","Tent"))
                assert(not S.ItemTranslation(tip,data))
            end
            for _,sample in ipairs({
                {279944,"Sharpening Wheel","Constructs a sharpening wheel that grants you and others sitting nearby 34 increased Strength, mutually exclusive with Strength of Earth Totem.","34 หน่วย","โทเท็มพลังธรณี"},
                {279956,"Mana Well","Constructs a mana well that allows you and others sitting nearby to regenerate 29 Mana every 5 sec, mutually exclusive with Blessing of Wisdom.","29 หน่วยให้คุณและคนอื่น ๆ ขณะนั่งอยู่ใกล้ ๆ ทุก 5 วินาที","พรแห่งปัญญา"},
                {279960,"Lodestone","Erects a lodestone that allows you and others sitting nearby to gain 80 increased melee Attack Power, mutually exclusive with Blessing of Might.","80 หน่วย","พรแห่งพละกำลัง"},
                {279962,"Incense Candle","Ignites an incense candle that allows you and others sitting nearby to gain 25 increased Intellect, mutually exclusive with Arcane Intellect.","25 หน่วย","ปัญญาอาร์เคน"},
                {279968,"First Aid Kit","Unpacks a first aid kit that allows you and others sitting nearby to gain 56 increased Stamina, mutually exclusive with Power Word: Fortitude.","56 หน่วย","วาจาทรงพลัง: ทรหด"},
            }) do
                use(unpack(sample))
            end
            local banner="Unrolls a banner that allows you and other members of the %s sitting nearby to gain 32 increased Spirit, mutually exclusive with Divine Spirit."
            use(279972,"Faction Banner",banner:format("Horde"),"สมาชิกฮอร์ด","วิญญาณศักดิ์สิทธิ์")
            use(279973,"Faction Banner",banner:format("Alliance"),"สมาชิกพันธมิตร","วิญญาณศักดิ์สิทธิ์")
            setData(279972,"Faction Banner",44,"Use: "..banner:format("Alliance")..footer)
            assert(not S.ItemTranslation(tip,data))
            local lute="Summons an enchanted lute that allows you and others sitting nearby to gain %s, mutually exclusive with Mark of the Wild."
            use(279976,"Enchanted Lute",lute:format("28 Armor"),"เกราะ 28 หน่วย","ตราแห่งพงไพร")
            use(279976,"Enchanted Lute",lute:format("71 Armor and 2 increase to all stats"),"ค่าสถานะทั้งหมด 2 หน่วย","ตราแห่งพงไพร")
            use(279976,"Enchanted Lute",lute:format("163 Armor, 7 increase to all stats, and 6 increase to all resistances"),
                "ค่าต้านทานทุกประเภท 6 หน่วย","ตราแห่งพงไพร")
            for _,bonus in ipairs({"0 Armor","-28 Armor","2.5 Armor","71 Armor and 2 increase to Intellect",
                                  "163 Armor and 6 increase to all resistances"}) do
                setData(279976,"Enchanted Lute",44,"Use: "..lute:format(bonus)..footer)
                assert(not S.ItemTranslation(tip,data))
            end
        ''')

    def test_earth_crest_scroll_matches_its_exact_native_tooltip(self):
        self.lua.execute('''
            local name="Scroll: Create Crest of Beckoning"
            local body="Use: Combine with 1 Rugged Leather and 1 Dense Stone to create a Crest of Beckoning: Earth."
            setData(20527,name,44,body)
            local title,text=S.ItemTranslation(tip,data)
            assert(title==name and text:find("หนังทนทาน (Rugged Leather) 1 ชิ้น",1,true)
                and text:find("หินเนื้อแน่น (Dense Stone) 1 ก้อน",1,true)
                and text:find("ตราเรียกธาตุ (ดิน)",1,true))
            assert(tip:GetLeftLine(2):GetText()==body)
            setLine(2,44,(body:gsub("Earth","Stone")));assert(not S.ItemTranslation(tip,data))
            setLine(2,44,(body:gsub("1 Dense Stone","2 Dense Stone")));assert(not S.ItemTranslation(tip,data))
            setData(20526,name,44,body);assert(not S.ItemTranslation(tip,data))
            setData(20527,name,45,body);assert(not S.ItemTranslation(tip,data))
        ''')

    def test_observed_items_require_one_exact_primary_native_trigger_line(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            ITEM_SPELL_TRIGGER_ONEQUIP="Equip:"
            ITEM_SPELL_TRIGGER_ONPROC="Chance on hit:"
            function tip:GetRightLine() end
            local name="Robes of Insight"
            local body="Use: Reduces the Mana cost of all spells by 200 for 12 sec."
            setData(940,name,44,body)
            setLine(3,45,"Equip: +33 Healing Power.")
            local title,text=S.ItemTranslation(tip,data)
            assert(title==name and text:find("มานาที่ใช้ในการร่ายเวททั้งหมดลง 200 หน่วย",1,true)
                and text:find("12 วินาที",1,true) and not text:find("33",1,true))
            assert(tip:GetLeftLine(2):GetText()==body)
            for _,duration in ipairs({"0 sec","-12 sec","12 turns","until cancelled"}) do
                setLine(2,44,(body:gsub("12 sec",duration)));assert(not S.ItemTranslation(tip,data))
            end
            setLine(2,44,(body:gsub("200","-200")));assert(not S.ItemTranslation(tip,data))
            setLine(2,45,body);assert(not S.ItemTranslation(tip,data))
            setLine(2,44,body);setLine(3,44,"Use: Different effect.");assert(not S.ItemTranslation(tip,data))
            setLine(3,19,"Nested item");assert(not S.ItemTranslation(tip,data))
            setData(940,name,44,body);primary={};assert(not S.ItemTranslation(tip,data));primary=nil
            setLine(1,22,"Other item");assert(not S.ItemTranslation(tip,data))
            setLine(1,22,name);tip:GetLeftLine(2).GetText=function() return "Changed effect" end
            assert(not S.ItemTranslation(tip,data))

            setData(2163,"Shadowblade",46,"Chance on hit: Sends a shadowy bolt at the enemy causing 41 to 54 Shadow damage.")
            title,text=S.ItemTranslation(tip,data)
            assert(title=="Shadowblade" and text:find("ศรเงา",1,true) and text:find("41 ถึง 54",1,true))
            setLine(2,46,"Chance on hit: Sends a shadowy bolt at the enemy causing 54 to 41 Shadow damage.")
            assert(not S.ItemTranslation(tip,data))
            setData(871,"Flurry Axe",46,"Chance on hit: Grants 1.5 extra attack on your next swing.")
            assert(not S.ItemTranslation(tip,data))
            setLine(2,46,"Chance on hit: Grants 2 extra attack on your next swing.")
            assert(S.ItemTranslation(tip,data))
            setData(2662,"Ribbly's Quiver",45,"Equip: Increases ranged attack speed by 15%.")
            title,text=S.ItemTranslation(tip,data)
            assert(title=="Ribbly's Quiver" and text:find("เพิ่มความเร็วโจมตีระยะไกล 15%",1,true))
            setData(273824,"Defias Jailbreakers",45,"Equip: Lockpicking +4.")
            title,text=S.ItemTranslation(tip,data)
            assert(title=="Defias Jailbreakers" and text:find("สะเดาะกุญแจ",1,true) and text:find("4",1,true))
            setLine(2,45,"Equip: Lockpicking +0.");assert(not S.ItemTranslation(tip,data))
            setLine(2,45,"Equip: Lockpicking +4.");setLine(1,22,"Other item");assert(not S.ItemTranslation(tip,data))
            local battery="Restore %s charges to a Manual Crowd Pummeler device in your possession."
            setData(274048,"9-60 Battery Pack",44,"Use: "..battery:format("3"))
            title,text=S.ItemTranslation(tip,data)
            assert(title=="9-60 Battery Pack" and text:find("เติม 3 ชาร์จ",1,true))
            setLine(2,44,"Use: "..battery:format("3.5"));assert(not S.ItemTranslation(tip,data))
            setLine(2,45,"Use: "..battery:format("3"));assert(not S.ItemTranslation(tip,data))
            setData(227813,"Drinkable Stratholme Holy Water",44,"Use: Restores 660 mana over 30 sec. Must remain seated while drinking.")
            title,text=S.ItemTranslation(tip,data)
            assert(title=="Drinkable Stratholme Holy Water" and text:find("660 หน่วยตลอด 30 วินาที",1,true)
                and text:find("ต้องนั่งอยู่ขณะดื่ม",1,true))
            setLine(2,44,"Use: Restores 660 mana over 30 sec.");assert(not S.ItemTranslation(tip,data))
            local debt="Equip: Grants 6 health and 2 mana every 5 sec for 20 sec when one of your spells is resisted."
            setData(273827,"Debt Collector",45,debt)
            title,text=S.ItemTranslation(tip,data)
            assert(title=="Debt Collector" and text:find("เมื่อเวทของคุณถูกต้านทาน",1,true)
                and text:find("มานา 2 หน่วยทุก 5 วินาที เป็นเวลา 20 วินาที",1,true))
            setLine(2,45,(debt:gsub("5 sec","4 sec")));assert(not S.ItemTranslation(tip,data))
            local obsidian="Equip: Chance on hit to reduce the mana cost of your next spell cast within 10 sec by %s."
            setData(274425,"White Obsidian Wand",45,obsidian:format("24"))
            title,text=S.ItemTranslation(tip,data)
            assert(title=="White Obsidian Wand" and text:find("10 วินาที ลง 24 หน่วย",1,true))
            setLine(2,45,obsidian:format("-24"));assert(not S.ItemTranslation(tip,data))
            setData(274265,"Brush Cutter",46,"Chance on hit: Assault the target with a dangerous toxin, dealing 24 Nature damage. Deals 2.5 times as much damage to Plants.")
            title,text=S.ItemTranslation(tip,data)
            assert(title=="Brush Cutter" and text:find("2.5 เท่าของปกติ",1,true))
            setLine(2,46,"Chance on hit: Assault the target with a dangerous toxin, dealing 24 Nature damage. Deals 2 to 5 times as much damage to Plants.")
            assert(not S.ItemTranslation(tip,data))

            local zeal="Chance on hit: A burst of energy fills the caster, increasing %s damage by 10 and armor by 150 for 15 sec."
            setData(6622,"Sword of Zeal",46,zeal:format("his"))
            local _,his=S.ItemTranslation(tip,data)
            setLine(2,46,zeal:format("her"))
            local _,her=S.ItemTranslation(tip,data)
            assert(his and his==her and her:find("เกราะ 150",1,true))
            setLine(2,46,zeal:format("their"));assert(not S.ItemTranslation(tip,data))

            local poison="Chance on hit: Strike your target with a Poisonous Sting, inflicting 27 damage every 3 sec for %s."
            setData(284050,"High Elf's Recurve",46,poison:format("11 sec"))
            local _,sting=S.ItemTranslation(tip,data)
            assert(sting and sting:find("ทุก 3 วินาที เป็นเวลา 11 วินาที",1,true))
            for _,value in ipairs({"0 sec","-9 sec","9 min","until cancelled","$d1"}) do
                setLine(2,46,poison:format(value));assert(not S.ItemTranslation(tip,data))
            end

            fontOK=false
            local kinds, wrappers = {[0]=44,[1]=45,[2]=46},
                {[0]="Use: ",[1]="Equip: ",[2]="Chance on hit: "}
            for _,id in ipairs({2662,871,940,2163,2291,2915,9386,13053,13060,942,
                274265,274270,274271,280032,282632,276743,284699,286616,6622,284050}) do
                local item=S.itemEffects[id]
                local trigger=item.strictObservedTrigger
                local pair=S.records[item.triggers[trigger][1]].lines[1]
                local live=pair.source:gsub("{(%d+)}", function(i)
                    return pair.slots[tonumber(i)].kind:find("duration",1,true) and "5 sec" or "17"
                end)
                setData(id,item.name,kinds[trigger],wrappers[trigger]..live)
                assert(S.OnTooltip(tip,data)=="shown", item.name)
            end
        ''')

    def test_observed_multi_effect_items_require_every_equip_line(self):
        self.lua.execute('''
            ITEM_SPELL_TRIGGER_ONEQUIP="Equip:"
            function tip:GetRightLine() end
            local name="Cloak of Hermitic Bliss"
            local land="Equip: Movement speed reduced by 25%."
            local water="Equip: Swim speed increased by 33%."
            setData(273084,name,45,land)
            assert(not S.ItemTranslation(tip,data))
            setLine(3,45,water)
            local title,text=S.ItemTranslation(tip,data)
            assert(title==name and text:find("25%",1,true) and text:find("33%",1,true))
            setLine(2,45,water);setLine(3,45,land)
            title,text=S.ItemTranslation(tip,data)
            assert(title==name and text:find("33%",1,true)<text:find("25%",1,true))
            setLine(2,45,"Equip: Swim speed increased by 34%.")
            setLine(3,45,"Equip: Movement speed reduced by 28%.")
            title,text=S.ItemTranslation(tip,data)
            assert(title==name and text:find("34%",1,true) and text:find("28%",1,true)
                and not text:find("33%",1,true) and not text:find("25%",1,true))
            setLine(2,45,water)
            setLine(3,45,water);assert(not S.ItemTranslation(tip,data))
            setLine(3,46,land);assert(not S.ItemTranslation(tip,data))
            setLine(3,45,"Equip: Movement speed reduced by -25%.");assert(not S.ItemTranslation(tip,data))
            setLine(3,45,land);setLine(4,45,"Equip: Other effect.");assert(not S.ItemTranslation(tip,data))
            setLine(4,19,"Nested item");assert(not S.ItemTranslation(tip,data))

            setData(273820,"Nightskulker Ring",45,"Equip: Reduces the hit chance of Fear effects against you by 4%.")
            setLine(3,45,"Equip: Increases movement speed by 2% in Duskwood.")
            title,text=S.ItemTranslation(tip,data)
            assert(title=="Nightskulker Ring" and text:find("4%",1,true) and text:find("ดัสก์วูด",1,true))
            setLine(3,45,"Equip: Increases movement speed by 2%.");assert(not S.ItemTranslation(tip,data))
            assert(not S.itemEffects[1204])
        ''')

    def test_reviewed_equip_siblings_require_one_complete_visible_equip_line(self):
        self.lua.execute('''
            ITEM_SPELL_TRIGGER_ONEQUIP="Equip:"
            function tip:GetRightLine() end
            local body="Equip: Increases all Resistances by 11. Gain an additional 17 to all Resistances in Forest and Grassland areas."
            setData(21568,"Rune of Duty",45,body)
            local title,text=S.ItemTranslation(tip,data)
            assert(title=="Rune of Duty" and text:find("เพิ่มค่าต้านทานทุกชนิด 11",1,true)
                and text:find("เพิ่มอีก 17",1,true))
            setLine(3,45,"Equip: Separate effect.");assert(not S.ItemTranslation(tip,data))
            setLine(3,45,body);assert(not S.ItemTranslation(tip,data))
            setLine(3,19,"Nested card");assert(not S.ItemTranslation(tip,data))
            setLine(3,nil,"Untyped line");assert(not S.ItemTranslation(tip,data))
            data.lines[3]=nil
            function tip:GetRightLine(i)
                if i==2 then return {GetText=function() return "Other effect" end,IsShown=function() return true end} end
            end
            assert(not S.ItemTranslation(tip,data))
            function tip:GetRightLine() end
            setLine(2,45,body.." Another effect.");assert(not S.ItemTranslation(tip,data))

            local pierce="Equip: Your spells pierce 2 Magical Resistances. Gain an additional 4 Spell Piercing in Forest and Grassland areas."
            setData(21566,"Rune of Perfection",45,pierce)
            local _,text=S.ItemTranslation(tip,data)
            assert(text:find("ได้ 2",1,true) and text:find("เพิ่มอีก 4",1,true))
            setLine(2,45,pierce:gsub("pierce 2","pierce -2"));assert(not S.ItemTranslation(tip,data))
            setLine(2,45,pierce:gsub("additional 4","additional -4"));assert(not S.ItemTranslation(tip,data))

            local disk="Equip: When the shield blocks, it releases an electrical charge that damages all nearby enemies."
            setData(18168,"Force Reactive Disk",45,disk.." This also has a chance of damaging the shield.")
            local _,text=S.ItemTranslation(tip,data)
            assert(text:find("ทำให้โล่เสียหาย",1,true))
            setLine(2,45,disk);assert(not S.ItemTranslation(tip,data))
        ''')

    def test_well_fed_reads_only_visible_xp_branch_and_keeps_live_values(self):
        self.lua.execute('''
            local body="Use: Restores 789 health over 18 sec. Must remain seated while eating. "..
                "If you spend at least 10 sec eating, you will become well fed and gain 12 Strength for 15 min."
            local xp=" Additionally, experience gained from kills is increased by 4%."
            setData(724,"Goretusk Liver Pie",44,body..xp)
            local _,withXP=S.ItemTranslation(tip,data)
            assert(withXP:find("789 หน่วยตลอด 18 วินาที",1,true))
            assert(withXP:find("ค่าพละกำลัง 12 เป็นเวลา 15 นาที",1,true))
            assert(withXP:find("เพิ่มขึ้น 4%",1,true))
            setLine(2,44,body)
            local _,withoutXP=S.ItemTranslation(tip,data)
            assert(withoutXP:find("ค่าพละกำลัง 12",1,true) and not withoutXP:find("ค่าประสบการณ์",1,true))
            setLine(2,44,body..xp:gsub("kills", "quests"))
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_well_fed_duration_is_independent_of_health_restoration_duration(self):
        self.lua.execute('''
            local body="Use: Restores 300 health over 20 sec. Must remain seated while eating. "..
                "If you spend at least 9 sec eating you will become Well Fed and gain 18 Strength and 7 Stamina for 45 min."
            setData(238637,"Prowler Steak",44,body)
            local _,text=S.ItemTranslation(tip,data)
            assert(text:find("300 หน่วยตลอด 20 วินาที",1,true) and text:find("9 วินาที",1,true))
            assert(text:find("ค่าพละกำลัง 18 และค่าความทนทาน 7 เป็นเวลา 45 นาที",1,true))
            setLine(2,44,body:gsub("7 Stamina", "7 Agility"))
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_distinct_effects_are_rendered_but_ambiguous_attribution_declines(self):
        self.lua.execute('''
            ITEM_SPELL_TRIGGER_ONEQUIP="Equip:"
            local other={reviewStatus="VERIFIED",originalName="Other",translatedName="อีกเอฟเฟกต์",
                lines={{source="Adds {1} armor.",target="เพิ่มเกราะ {1}",slots={{kind="number-range",token="$s1"}}}}}
            S.records.other=other
            S.itemEffects[itemId].triggers[1]={"other"}
            setLine(3,45,"Equip: Adds 7 armor.")
            local _,text=S.ItemTranslation(tip,data)
            assert(text:find("เพิ่มเกราะ 7",1,true) and text:find("1,234.5",1,true))
            S.records.duplicate=S.records[key]
            table.insert(S.itemEffects[itemId].triggers[0],"duplicate")
            local _,partial=S.ItemTranslation(tip,data)
            assert(partial:find("เพิ่มเกราะ 7",1,true) and not partial:find("1,234.5",1,true))
            data.lines[3]=nil;assert(not S.ItemTranslation(tip,data))
        ''')

    def test_appended_mismatch_and_secret_context_fail_closed(self):
        self.lua.execute('''
            primary={tooltipData={type=0,id=itemId}}
            assert(not S.ItemTranslation(tip,data));primary=nil
            local old=info.tooltipData;info.tooltipData={type=0,id=itemId}
            assert(not S.ItemTranslation(tip,data));info.tooltipData=old
            local hidden=trap();secret[hidden]=true
            ITEM_SPELL_TRIGGER_ONUSE=hidden;assert(not S.ItemTranslation(tip,data))
            data.id=hidden;assert(not S.ItemTranslation(tip,data));data.id=itemId
            data.lines[2].leftText=hidden;assert(not S.ItemTranslation(tip,data))
            S.OnTooltip(tip,hidden);assert(not S.reader:IsShown())
        ''')

    def test_untranslated_comparison_does_not_hide_other_tooltip_reader(self):
        self.lua.execute('''
            S.OnTooltip(tip,data);assert(S.reader:IsShown())
            S.OnTooltip(frame(UIParent),{type=0,id=99999999,lines={}})
            assert(S.reader:IsShown())
            setLine(2,44,"Changed source text.")
            S.OnTooltip(tip,data);assert(not S.reader:IsShown())
        ''')

    def set_bonus_fixture(self):
        self.lua.execute('''
            setId=15062;spellId=460230;bonusKey="item-set-bonus:143:7872"
            bonusText="Improves your chance to hit by 2.0%."
            assert(S.itemSetBonuses[setId].bonuses[spellId].key==bonusKey)
            ITEM_SET_BONUS_GRAY="(%d) Set: %s";ITEM_SET_BONUS="Set: %s"
            C_SpecializationInfo={GetSpecialization=function() return 2 end,
                GetSpecializationInfo=function(index) assert(index==2);return 260 end}
            bonusIds={spellId,14590}
            descriptions={[spellId]=bonusText,[14590]="A different bonus."}
            C_Item={GetSetBonusesForSpecializationByItemID=function(spec,id)
                assert(spec==260 and id==setId);return bonusIds
            end}
            C_Spell={GetSpellDescription=function(id) return descriptions[id] end,
                GetSpellName=function(id) assert(id==spellId);return "Increased Hit Chance 02" end}
            setData(setId,"Devilsaur Leggings",0,"(2) Set: "..bonusText)
        ''')

    def test_set_bonus_real_index_and_template_match_active_and_inactive(self):
        self.set_bonus_fixture()
        self.lua.execute('''
            S.settings.original=true
            S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and S.stats.errors==0)
            local heading,text=S.ItemTranslation(tip,data)
            assert(heading=="Devilsaur Leggings" and text:find("โบนัสชุด (2 ชิ้น)",1,true))
            assert(text:find("โอกาสโจมตีโดนเพิ่มขึ้น 2.0%",1,true))
            assert(text:find("(2) Set: "..bonusText,1,true))
            assert(tip:GetLeftLine(2):GetText()=="(2) Set: "..bonusText)
            setLine(2,0,"Set: "..bonusText)
            local _,active=S.ItemTranslation(tip,data)
            assert(active:find("โบนัสชุด —",1,true) and not active:find("2 ชิ้น",1,true))
        ''')

    def test_deathdealer_evasion_keeps_the_visible_sign_and_exact_three_piece_bonus(self):
        self.set_bonus_fixture()
        for module in ('Bitmap', 'Skills/BitmapData'):
            path = ROOT / 'addon/ForeverThai' / (module + '.lua')
            self.lua.execute(path.read_text(encoding='utf-8'), 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            setId,spellId=21359,26112
            bonusIds={spellId}
            C_Spell.GetSpellName=function() return "Deathdealer Evasion Bonus" end
            local function card(value,threshold)
                local english="Reduces the cooldown of your Evasion ability by "..value.." min."
                descriptions[spellId]=english
                setData(setId,"Deathdealer's Boots",0,"("..(threshold or 3)..") Set: "..english)
            end
            S.settings.original=true
            fontOK=false
            card("-1.0")
            assert(S.OnTooltip(tip,data)=="shown" and S.reader:IsShown())
            local _,signed=S.ItemTranslation(tip,data)
            assert(signed:find("โบนัสชุด (3 ชิ้น)",1,true)
                and signed:find("คูลดาวน์ของหลบหลีกเหนือชั้นเปลี่ยนไป -1.0 นาที",1,true)
                and signed:find("by -1.0 min.",1,true))
            card("1")
            local _,unsigned=S.ItemTranslation(tip,data)
            assert(unsigned:find("ลดคูลดาวน์ของหลบหลีกเหนือชั้นลง 1 นาที",1,true))
            for _,bad in ipairs({"--1","+1","-2","0","1 to 2"}) do
                card(bad);assert(not S.ItemTranslation(tip,data))
            end
            card("-1",5);assert(not S.ItemTranslation(tip,data))
            card("-1");descriptions[spellId]="Different spell text.";assert(not S.ItemTranslation(tip,data))
            card("-1");bonusIds={2840};assert(not S.ItemTranslation(tip,data))
        ''')

    def test_frostfire_set_translates_only_verified_trigger_from_complete_native_line(self):
        self.set_bonus_fixture()
        for module in ('Bitmap', 'Skills/BitmapData'):
            path = ROOT / 'addon/ForeverThai' / (module + '.lua')
            self.lua.execute(path.read_text(encoding='utf-8'), 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            setId,spellId=22496,28761
            bonusIds={spellId}
            local source="Your damage spells have a chance to displace you, causing the next spell cast to generate no threat."
            C_Spell.GetSpellName=function() return "Not There" end
            local side
            function tip:GetRightLine(i)
                if side and i==2 then return {GetText=function() return side end,IsShown=function() return true end} end
            end
            local function card(body,prefix)
                descriptions[spellId]=body
                setData(setId,"Frostfire Robe",0,(prefix or "(8) Set: ")..body)
            end
            fontOK=false
            card(source)
            assert(S.OnTooltip(tip,data)=="shown" and S.reader:IsShown())
            local heading,text=S.ItemTranslation(tip,data)
            assert(heading=="Frostfire Robe" and text:find("โบนัสชุด (8 ชิ้น) — เลือนหาย",1,true)
                and text:find("เวทที่สร้างความเสียหายมีโอกาสทำให้คุณได้รับผลเลือนหาย",1,true)
                and text:find("ดูเงื่อนไขเพิ่มเติมในคำอธิบายเดิม",1,true)
                and not text:find("ความคุกคาม",1,true))
            assert(tip:GetLeftLine(2):GetText()=="(8) Set: "..source)
            card(source,"Set: ")
            local _,active=S.ItemTranslation(tip,data);assert(active:find("8 ชิ้น",1,true))
            card(source,"(6) Set: ");assert(not S.ItemTranslation(tip,data))
            card(source.." Additional effect.");assert(not S.ItemTranslation(tip,data))
            card("Your damage spells have a chance to displace you.");assert(not S.ItemTranslation(tip,data))
            card(source);bonusIds={spellId,28762};descriptions[28762]=source;assert(not S.ItemTranslation(tip,data))
            bonusIds={spellId};side="Unreviewed condition";assert(not S.ItemTranslation(tip,data));side=nil
            S.settings.descriptions=false
            local _,nameOnly=S.ItemTranslation(tip,data);assert(nameOnly=="โบนัสชุด (8 ชิ้น) — เลือนหาย")
            card((source:gsub("spell cast","damage spell")));assert(not S.ItemTranslation(tip,data))
        ''')

    def test_set_bonus_declines_wrong_identity_threshold_and_nested_lines(self):
        self.set_bonus_fixture()
        self.lua.execute('''
            setLine(2,0,"(3) Set: "..bonusText);assert(not S.ItemTranslation(tip,data))
            setLine(2,45,"(2) Set: "..bonusText);assert(not S.ItemTranslation(tip,data))
            setLine(2,0,"(2) Set: "..bonusText);assert(S.ItemTranslation(tip,data))
            setLine(3,19,"Nested block");assert(not S.ItemTranslation(tip,data))
            setLine(3,0,"Set: "..bonusText);assert(not S.ItemTranslation(tip,data))
            data.lines[3]=nil
            tip:GetLeftLine(2).GetText=function() return "(2) Set: changed" end
            assert(not S.ItemTranslation(tip,data))
            setLine(2,0,"(2) Set: "..bonusText)
            C_Spell.GetSpellName=function() return "Changed identity" end
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_set_bonus_declines_competitors_missing_api_and_different_value(self):
        self.set_bonus_fixture()
        self.lua.execute('''
            local other=descriptions[14590]
            descriptions[14590]=bonusText;assert(not S.ItemTranslation(tip,data))
            descriptions[14590]=nil;assert(not S.ItemTranslation(tip,data))
            descriptions[14590]=other
            bonusIds={7872};assert(not S.ItemTranslation(tip,data)) -- DB2 row ID, not SpellID
            bonusIds={spellId,14590}
            descriptions[spellId]="Improves your chance to hit by 3.0%."
            assert(not S.ItemTranslation(tip,data));descriptions[spellId]=bonusText
            local hidden=trap();secret[hidden]=true
            descriptions[14590]=hidden;assert(not S.ItemTranslation(tip,data));descriptions[14590]=other
            C_SpecializationInfo.GetSpecialization=function() error("Unavailable") end
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_set_bonus_profession_requirement_visible_without_descriptions(self):
        self.set_bonus_fixture()
        self.lua.execute('''
            setId=19688;spellId=7597
            bonusIds={spellId}
            bonusText="Improves your chance to get a critical strike with melee attacks by 1.0%."
            descriptions={[spellId]=bonusText}
            C_Spell.GetSpellName=function() return "Increased Critical 1" end
            setData(setId,"Blood Tiger Breastplate",0,"(2) Set: "..bonusText)
            S.settings.descriptions=false
            local _,text=S.ItemTranslation(tip,data)
            assert(text:find("โบนัสชุด (2 ชิ้น)",1,true))
            assert(text:find("เงื่อนไขโบนัสชุด: ทักษะการทำเครื่องหนัง 300",1,true))
            assert(not text:find("1.0%",1,true))
            setLine(2,0,"Set: "..bonusText)
            local _,active=S.ItemTranslation(tip,data)
            assert(active:find("ทักษะการทำเครื่องหนัง 300",1,true) and not active:find("2 ชิ้น",1,true))
        ''')

    def test_set_bonus_proc_values_copied_from_full_visible_description(self):
        self.set_bonus_fixture()
        self.lua.execute('''
            setId=22078;spellId=27778
            bonusIds={spellId}
            bonusText="When struck in combat has a 7% chance of shielding the wearer in a protective shield which will absorb 410 damage. Can only occur once every 95 sec."
            descriptions={[spellId]=bonusText}
            C_Spell.GetSpellName=function() return "Divine Protection" end
            setData(setId,"Virtuous Belt",0,"(4) Set: "..bonusText)
            local _,text=S.ItemTranslation(tip,data)
            assert(text:find("7%",1,true) and text:find("410 หน่วย",1,true) and text:find("95 วินาที",1,true))
            local other=bonusText:gsub("95 sec.","2 min.")
            descriptions[spellId]=other
            setLine(2,0,"(4) Set: "..other)
            assert(not S.ItemTranslation(tip,data))
        ''')

    def enchant_fixture(self):
        self.lua.execute('''
            assert(S.itemEnchantments[723]=="item-enchant:723")
            local iid,name=999991,"Example Greatsword"
            setData(iid,name,15,"Enchanted: Intellect +17")
            data.hyperlink="|cff1eff00|Hitem:999991:723:0:0:0:0:0|h[Example Greatsword]|h|r"
            ENCHANTED_TOOLTIP_LINE="Enchanted: %s"
            TooltipUtil={GetDisplayedItem=function(t)
                assert(t==tip)
                return name,data.hyperlink,iid
            end}
        ''')

    def test_enchantment_copies_displayed_amount_with_primary_link_and_typed_line(self):
        self.enchant_fixture()
        self.lua.execute('''
            S.settings.original=true
            S.OnTooltip(tip,data)
            assert(S.reader:IsShown() and S.stats.errors==0)
            local heading,text=S.ItemTranslation(tip,data)
            assert(heading=="Example Greatsword" and text:find("ค่าสติปัญญา +17",1,true))
            assert(text:find("Enchanted: Intellect +17",1,true))
            assert(tip:GetLeftLine(2):GetText()=="Enchanted: Intellect +17")
            setLine(2,15,"Intellect +21")
            data.hyperlink="item:999991:723:0:0:0"
            local _,bare=S.ItemTranslation(tip,data)
            assert(bare:find("ค่าสติปัญญา +21",1,true))
        ''')

    def test_armor_kits_require_matching_use_values_and_equipped_enchantment_id(self):
        for relative in ('Bitmap.lua', 'Skills/BitmapData.lua'):
            source = (ROOT / 'addon/ForeverThai' / relative).read_text(encoding='utf-8')
            self.lua.execute(source, 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            function tip:GetRightLine() end
            local use="Use: Permanently increase the Stamina value by 3 and armor value by 24 of an item worn on the chest, legs, hands or feet. Only usable on items level 15 and above."
            setData(4265,"Heavy Armor Kit",44,use)
            local title,body=S.ItemTranslation(tip,data)
            assert(title=="Heavy Armor Kit" and body:find("ค่าความทนทาน 3 หน่วยและค่าเกราะ 24 หน่วย",1,true))
            assert(body:find("เลเวล 15 ขึ้นไปเท่านั้น",1,true) and S.OnTooltip(tip,data)=="shown")
            assert(tip:GetLeftLine(2):GetText()==use)
            for _,pair in ipairs({{"level 15","level 16"},{"by 24","by 25"},{"chest","head"},{"Stamina","Strength"}}) do
                setLine(2,44,use:gsub(pair[1],pair[2]));assert(not S.ItemTranslation(tip,data))
            end
        ''')
        self.lua.execute('''
            local name="Example Chestguard"
            setData(999991,name,15,"")
            ENCHANTED_TOOLTIP_LINE="Enchanted: %s"
            TooltipUtil={GetDisplayedItem=function() return name,data.hyperlink,999991 end}
            for _,sample in ipairs({
                {8484,"Stamina +3 and Armor +24","ค่าความทนทาน +3 และเกราะ +24"},
                {8485,"Spell Power +4 and Armor +24","พลังเวท +4 และเกราะ +24"},
                {8486,"Attack Power +6 and Armor +24","พลังโจมตี +6 และเกราะ +24"},
                {2503,"Defense +3","ทักษะการป้องกัน +3"},
                {8719,"Defense +4 and Stamina +10","ทักษะการป้องกัน +4 และค่าความทนทาน +10"},
            }) do
                data.hyperlink="item:999991:"..sample[1]..":0:0:0"
                local live="Enchanted: "..sample[2]
                setLine(2,15,live)
                local title,body=S.ItemTranslation(tip,data)
                assert(title==name and body:find(sample[3],1,true))
                assert(S.OnTooltip(tip,data)=="shown" and tip:GetLeftLine(2):GetText()==live)
                setLine(2,15,live:gsub("(%d+)", "99",1))
                assert(not S.ItemTranslation(tip,data))
            end
            data.hyperlink="item:999991:8487:0:0:0"
            setLine(2,15,"Enchanted: Stamina +3 and Armor +24")
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_tinker_enchantment_matches_visible_description_and_exact_link(self):
        self.enchant_fixture()
        self.lua.execute('''
            S.settings.original=false
            data.hyperlink="item:999991:7919:0:0:0"
            setLine(2,15,"Enchanted: Teleport forward 17 yds.")
            local _,text=S.ItemTranslation(tip,data)
            assert(text and text:find("เทเลพอร์ตไปข้างหน้า 17 หลา",1,true))
            assert(not text:find("ถอดออกหรือแทนที่ไม่ได้",1,true))
            data.hyperlink="item:999991:7920:0:0:0"
            assert(not S.ItemTranslation(tip,data))
            data.hyperlink="item:999991:7919:0:0:0"
            setLine(2,15,"Enchanted: Teleport forward 17 yds. This enhancement is permanent and cannot be removed or replaced.")
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_wolfshead_enchant_distinguishes_exact_equipped_text_from_stale_consumable(self):
        for module in ('Bitmap', 'Skills/BitmapData'):
            path = ROOT / 'addon/ForeverThai' / (module + '.lua')
            self.lua.execute(path.read_text(encoding='utf-8'), 'ForeverThai', self.lua.globals().addon)
        self.enchant_fixture()
        self.lua.execute('''
            data.hyperlink="item:999991:7124:0:0:0"
            ITEM_SPELL_TRIGGER_ONEQUIP="Equip: %s"
            S.settings.original=false
            local name="Wolfshead Trophy"
            local old="Permanently enchant a helm slot item, causing you to gain 20 energy or 5 rage " ..
                "when shapeshifting into Cat or Bear form."
            local current="You gain an additional 5 Rage from activating Enrage and an additional " ..
                "5 Energy from activating Shifting Power."
            setLine(2,15,"Enchanted: "..name)
            local _,body=S.ItemTranslation(tip,data)
            assert(body=="เสริมพลังถาวร — เครื่องหมายเชิดชูหัวหมาป่า")
            setLine(3,45,"Equip: "..current)
            local _,labelOnly=S.ItemTranslation(tip,data)
            assert(labelOnly==body)
            data.lines[3]=nil
            for _,visible in ipairs({current,"Enchanted: "..current,"Equip: "..current,"Enchanted: Equip: "..current}) do
                setLine(2,15,visible)
                local _,translated=S.ItemTranslation(tip,data)
                assert(translated and translated:find("ค่าความโกรธเพิ่มอีก 5",1,true)
                    and translated:find("พลังงานเพิ่มอีก 5 เมื่อใช้พลังแปรสภาพ",1,true))
                assert(tip:GetLeftLine(2):GetText()==visible)
            end
            S.settings.original=true
            local _,withOriginal=S.ItemTranslation(tip,data)
            assert(withOriginal:find("Enchanted: Equip: "..current,1,true))
            fontOK=false
            S.settings.original=false
            assert(S.OnTooltip(tip,data)=="shown" and S.reader:IsShown())
            for _,invalid in ipairs({old,current:gsub("5 Energy","20 Energy"),
                current:gsub("5 Rage","-5 Rage"),current.." Additional effect."}) do
                setLine(2,15,invalid);assert(not S.ItemTranslation(tip,data))
            end
            setLine(2,45,"Equip: "..current);assert(not S.ItemTranslation(tip,data))
            setLine(2,15,current);data.hyperlink="item:999991:723:0:0:0"
            assert(not S.ItemTranslation(tip,data))
            data.hyperlink="item:999991:7124:0:0:0";setLine(3,15,name)
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_wolfshead_trophy_use_shows_only_helm_application(self):
        for module in ('Bitmap', 'Skills/BitmapData'):
            path = ROOT / 'addon/ForeverThai' / (module + '.lua')
            self.lua.execute(path.read_text(encoding='utf-8'), 'ForeverThai', self.lua.globals().addon)
        self.lua.execute('''
            fontOK=false
            local name="Wolfshead Trophy"
            local rightText
            function tip:GetRightLine(i)
                if i==2 and rightText then
                    return {IsShown=function() return true end,GetText=function() return rightText end}
                end
            end
            local full="Use: Permanently enchant a helm slot item, causing you to gain 20 energy or 5 rage " ..
                "when shapeshifting into Cat or Bear form."
            setData(212568,name,44,full)
            local title,body=S.ItemTranslation(tip,data)
            assert(title==name)
            assert(body=="เมื่อใช้ — เครื่องหมายเชิดชูหัวหมาป่า\\nลงมนตร์ถาวรให้ไอเทมช่องศีรษะ" ..
                "\\nดูเงื่อนไขเพิ่มเติมในคำอธิบายเดิม")
            assert(tip:GetLeftLine(2):GetText()==full and S.OnTooltip(tip,data)=="shown")
            S.settings.descriptions=false
            local _,label=S.ItemTranslation(tip,data)
            assert(label=="เมื่อใช้ — เครื่องหมายเชิดชูหัวหมาป่า")
            S.settings.descriptions=true
            setLine(2,44,full:gsub("20 energy","5 energy"))
            assert(not S.ItemTranslation(tip,data))
            setLine(2,45,full);assert(not S.ItemTranslation(tip,data))
            setLine(2,44,full)
            setLine(3,44,full);assert(not S.ItemTranslation(tip,data));data.lines[3]=nil
            setLine(3,19,"Nested");assert(not S.ItemTranslation(tip,data));data.lines[3]=nil
            rightText="Other";assert(not S.ItemTranslation(tip,data));rightText=nil
            primary={tooltipData=data};assert(not S.ItemTranslation(tip,data));primary=nil
            setLine(1,22,"Another Trophy");assert(not S.ItemTranslation(tip,data))
            setLine(1,22,name);data.id=8345;assert(not S.ItemTranslation(tip,data))
        ''')

    def test_equipped_stat_labels_require_the_exact_reviewed_id_stat_and_amount(self):
        self.enchant_fixture()
        self.lua.execute('''
            S.settings.englishNames=true
            S.settings.original=false
            for _,entry in ipairs({
                {925,"Defense +2","ค่าป้องกัน +2","Defense +5","Defense"},
                {2618,"Agility +9","ค่าความคล่องแคล่ว +9","Agility +15","Agility"},
                {8214,"Defense +9","ค่าป้องกัน +9","Defense +5","Defense"}
            }) do
                data.hyperlink="item:999991:"..entry[1]..":0:0:0"
                setLine(2,15,"Enchanted: "..entry[2])
                local _,body=S.ItemTranslation(tip,data)
                assert(body and body:find(entry[3],1,true) and body:find("("..entry[5]..")",1,true))
                assert(not body:find(entry[4],1,true) and tip:GetLeftLine(2):GetText()=="Enchanted: "..entry[2])
                setLine(2,15,entry[2]);assert(S.ItemTranslation(tip,data))
                setLine(2,15,"Enchanted: "..entry[4]);assert(not S.ItemTranslation(tip,data))
                setLine(2,15,"Enchanted: "..entry[2].." and another stat.");assert(not S.ItemTranslation(tip,data))
                setLine(2,45,"Equip: "..entry[2]);assert(not S.ItemTranslation(tip,data))
                setLine(2,15,entry[2]);setLine(3,15,entry[2]);assert(not S.ItemTranslation(tip,data))
                data.lines[3]=nil
            end
            data.hyperlink="item:999991:925:0:0:0"
            setLine(2,15,"Defense +9");assert(not S.ItemTranslation(tip,data))
            data.hyperlink="item:999991:8203:0:0:0"
            setLine(2,15,"Spirit +4");assert(not S.ItemTranslation(tip,data))
            setLine(2,15,"Resistance +4");assert(not S.ItemTranslation(tip,data))
        ''')

    def test_enchantment_rejects_inconsistent_item_link_or_stat_text(self):
        self.enchant_fixture()
        self.lua.execute('''
            local link=data.hyperlink
            for _,bad in ipairs({"item:42:723:0","item:999991:0:0","item:999991:-723:0",
                "item:999991::723:0","item:999991:8203:0","item:999991:723:bad",
                "item:999991:723:--","item:999991:723:1-2","x"..link}) do
                data.hyperlink=bad;assert(not S.ItemTranslation(tip,data))
            end
            data.hyperlink=link
            setLine(2,15,"Enchanted: Strength +17");assert(not S.ItemTranslation(tip,data))
            setLine(2,30,"Enchanted: Intellect +17");assert(not S.ItemTranslation(tip,data))
            setLine(2,15,"Enchanted: Intellect +17");assert(S.ItemTranslation(tip,data))
            TooltipUtil.GetDisplayedItem=function() return "Other item",link,999991 end
            assert(not S.ItemTranslation(tip,data))
            TooltipUtil.GetDisplayedItem=function() return "Example Greatsword",link,42 end
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_enchantment_rejects_competing_nested_stale_or_secret_lines(self):
        self.enchant_fixture()
        self.lua.execute('''
            setLine(3,15,"An inaccessible competing enchant")
            tip:GetLeftLine(3).IsShown=function() return false end
            assert(not S.ItemTranslation(tip,data))
            setLine(3,19,"Nested item");assert(not S.ItemTranslation(tip,data))
            data.lines[3]=nil
            tip:GetLeftLine(2).GetText=function() return "Enchanted: Intellect +19" end
            assert(not S.ItemTranslation(tip,data))
            setLine(2,15,"Enchanted: Intellect +17")
            local hidden=trap();secret[hidden]=true
            data.lines[3]=hidden;assert(not S.ItemTranslation(tip,data));data.lines[3]=nil
            data.guid=hidden;assert(not S.ItemTranslation(tip,data));data.guid=nil
            TooltipUtil.GetDisplayedItem=function() return "Example Greatsword",hidden,999991 end
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_enchantment_dual_amounts_are_separate_and_literal_stats_stay_exact(self):
        self.enchant_fixture()
        self.lua.execute('''
            data.hyperlink="item:999991:8208:0:0:0"
            setLine(2,15,"Enchanted: Healing Spells +17, Damage Spells +8")
            local _,dual=S.ItemTranslation(tip,data)
            assert(dual:find("การรักษาจากเวท +17, ความเสียหายจากเวท +8",1,true))
            setLine(2,15,"Enchanted: Damage Spells +8, Healing Spells +17")
            assert(not S.ItemTranslation(tip,data))
            data.hyperlink="item:999991:241:0:0:0"
            setLine(2,15,"Weapon Damage +2")
            local _,weapon=S.ItemTranslation(tip,data)
            assert(weapon:find("ความเสียหายอาวุธ +2",1,true))
            setLine(2,15,"Weapon Damage +3")
            assert(not S.ItemTranslation(tip,data))
            data.hyperlink="item:999991:24:0:0:0"
            setLine(2,15,"Intellect +2")
            assert(S.ItemTranslation(tip,data))
            setLine(2,15,"Intellect +9")
            assert(not S.ItemTranslation(tip,data))
            data.hyperlink="item:999991:7442:0:0:0" -- Child SpellID cannot select the enchantment.
            setLine(2,15,"Intellect +2")
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_enchantment_literal_percent_and_healing_only_label_stay_exact(self):
        self.enchant_fixture()
        self.lua.execute('''
            data.hyperlink="item:999991:863:0:0:0"
            setLine(2,15,"Blocking +2%")
            local _,block=S.ItemTranslation(tip,data)
            assert(block:find("โอกาสบล็อก +2%",1,true))
            setLine(2,15,"Blocking +2")
            assert(not S.ItemTranslation(tip,data))
            data.hyperlink="item:999991:2505:0:0:0"
            setLine(2,15,"Healing Spells +55")
            local _,healing=S.ItemTranslation(tip,data)
            assert(healing:find("การรักษาจากเวท +55",1,true) and not healing:find("19",1,true))
            setLine(2,15,"Healing Spells +55/Damage Spells +19")
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_enchantment_keeps_armor_kit_values_and_crit_units_in_source_order(self):
        self.enchant_fixture()
        self.lua.execute('''
            data.hyperlink="item:999991:15:0:0:0"
            setLine(2,15,"Stamina +3 and Armor +21")
            local _,kit=S.ItemTranslation(tip,data)
            assert(kit:find("ค่าความทนทาน +3 และค่าเกราะ +21",1,true))
            setLine(2,15,"Armor +21 and Stamina +3")
            assert(not S.ItemTranslation(tip,data))
            data.hyperlink="item:999991:7664:0:0:0"
            setLine(2,15,"+2.5% Critical Strike Chance")
            local _,crit=S.ItemTranslation(tip,data)
            assert(crit:find("โอกาสเกิดคริติคอล +2.5%",1,true))
            setLine(2,15,"+2.5 Critical Strike Chance")
            assert(not S.ItemTranslation(tip,data))
        ''')

    def test_enchantment_name_only_preserves_original_without_repeating_thai(self):
        self.enchant_fixture()
        self.lua.execute('''
            S.settings.original=true
            data.hyperlink="item:999991:803:0:0:0"
            setLine(2,15,"Enchanted: Fiery Weapon")
            local _,text=S.ItemTranslation(tip,data)
            local _,count=text:gsub("อาวุธเพลิง", "")
            assert(count==1 and text:find("Enchanted: Fiery Weapon",1,true))
            setLine(2,15,"Enchanted: Fiery Weapon (40 Fire damage)")
            assert(not S.ItemTranslation(tip,data))
        ''')
