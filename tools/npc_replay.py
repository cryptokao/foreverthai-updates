"""Replay recovered speech fixture against an independently reviewed Dev corpus.
No original source helper, old Catalog delta wrapper or absent API archive is run.
"""
import argparse,hashlib,json,pathlib,re,subprocess,textwrap,traceback,zipfile
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1]
REFERENCE=ROOT/'tests/recovered_npc/check_speech_v04230.py'
EXPECTED_REFERENCE='bdcf2ff10c973ab90cd372cfbd8f9416805f1fb0167be0d3e2d8a08193977b58'
sha=lambda b:hashlib.sha256(b).hexdigest()

def verify_corpus(review):
    original=pathlib.Path('/workspace/foreverthai-dev/downloads')/review['source_zip']
    assert sha(original.read_bytes())==review['source_zip_sha256']
    with zipfile.ZipFile(original) as z:
        documents={}
        for item in review['source_files']:
            raw=z.read(item['path']);assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
            documents[item['path']]=json.loads(raw)['entries']
        assert sum(len(v) for v in documents.values())==len(review['entries'])
        keys=set()
        for row in review['entries']:
            source=documents[row['evidence_file']][row['evidence_entry_index']]
            for k,v in source.items():assert row[k]==v,(row['evidence_file'],k)
            key=(row['npc_id'],row['event'],row['english']);assert key not in keys;keys.add(key)
    assert sha(REFERENCE.read_bytes())==EXPECTED_REFERENCE
    ref=REFERENCE.read_text();chunk=ref[ref.index("fixture = "+chr(39)*3):ref.index('\napi_proofs = []')]
    assert textwrap.indent(chunk,'    ') in pathlib.Path(__file__).read_text(),'Original replay assertions changed'

def replay(payload,review):
    fixture = '''
    frames={}; draws={}; printed={}; playerName="Aeri"; locale="enUS"; build="70888"; version="1.60.1"
    function GetBuildInfo() return version,build,"",16001 end
    function GetLocale() return locale end
    function UnitName() return playerName end
    function UnitClass() return "Druid","DRUID" end
    function UnitRace() return "Night Elf" end
    function issecretvalue(value) return value==SECRET end
    SECRET={}
    function print(text) printed[#printed+1]=text end
    local methods={}
    local function noop() end
    for _,key in ipairs({"SetSize","SetPoint","SetFrameStrata","SetClampedToScreen","SetMovable",
    "EnableMouse","RegisterForDrag","StartMoving","StopMovingOrSizing","SetAllPoints","SetColorTexture",
    "SetTexture","SetTexCoord","ClearAllPoints","SetVertexColor","SetFont","SetTextColor"}) do methods[key]=noop end
    function methods:Show() self.visible=true end
    function methods:Hide() self.visible=false end
    function methods:IsShown() return self.visible end
    function methods:SetScript(key,fn) self.scripts[key]=fn end
    function methods:RegisterEvent(key) self.events[key]=true end
    function methods:SetHeight(value) self.height=value end
    function methods:SetText(value) self.text=value end
    function methods:GetStringWidth() return #(self.text or "")*8 end
    function methods:CreateTexture() local f=make(); self.textures[#self.textures+1]=f; return f end
    function methods:CreateFontString() local f=make();self.labels[#self.labels+1]=f;return f end
    function make() return setmetatable({scripts={},events={},textures={},labels={}}, {__index=methods}) end
    function CreateFrame(_,name) local f=make(); if name then frames[name]=f end; return f end
    UIParent=make(); STANDARD_TEXT_FONT="Default"
    function event(kind,text,id,guidOverride)
     local f=frames.ForeverThaiSpeechEvents
     local guid=guidOverride or ("Creature-0-1-2-3-"..id.."-012ABC")
     f.scripts.OnEvent(f,kind,text,"Ignored name","Common","","","",0,0,"",0,123,guid)
    end
    function tick(seconds)
     local f=frames.ForeverThaiSpeechReader
     if f.visible then f.scripts.OnUpdate(f,seconds) end
    end
    '''

    lua = LuaRuntime()
    lua.execute(fixture)
    ns = lua.table()
    for name in ("Catalog.lua", "Match.lua", "Observe.lua", "Atlas.lua", "Bitmap.lua", "SpeechData.lua"):
        lua.execute(payload(name).decode("utf8"), "ForeverThai", ns)
    # Retain the real bitmap rendering and also observe what the popup paints.
    lua.execute('''
    local addon=...
    local original=addon.BitmapLayer
    addon.BitmapLayer=function(...)
     local layer,draw=original(...)
     return layer,function(text,...)
      draws[#draws+1]=text
      return draw(text,...)
     end
    end
    ''', ns)
    lua.execute(payload("Speech.lua").decode("utf8"), "ForeverThai", ns)
    g = lua.globals()
    popup = g.frames.ForeverThaiSpeechReader
    assert not popup.IsShown(popup)
    assert ns.speech[3519] and ns.speech[3568] is None  # Arynia speaks the reunion line, not Mist.
    assert all(g.frames.ForeverThaiSpeechEvents.events[event] for event in
               ("CHAT_MSG_MONSTER_SAY", "CHAT_MSG_MONSTER_YELL", "CHAT_MSG_MONSTER_WHISPER", "CHAT_MSG_MONSTER_EMOTE"))

    for build in ("70862", "70888"):
        g.build = build
        for row in review["entries"]:
            ns.SpeechCommand("speech hide")
            raw = row["english"].replace("$N", "Aeri").replace("$C", "druid").replace("$R", "night elf")
            expected = row["thai"].replace("{name}", "Aeri").replace("{class}", "ดรูอิด").replace("{race}", "ไนต์เอลฟ์")
            g.event(row["event"], raw, row["npc_id"])
            assert popup.IsShown(popup) and expected in g.draws[len(g.draws)], row
            # Every Thai run must be baked, including adjacent punctuation and dynamic names.
            for run in re.findall(r"[\u0e00-\u0e7f]+", expected):
                assert ns.runs[run], run
            for event, text, npc, guid in (
                ("CHAT_MSG_SAY", raw, row["npc_id"], None),
                ("CHAT_MSG_MONSTER_YELL" if row["event"] != "CHAT_MSG_MONSTER_YELL" else "CHAT_MSG_MONSTER_SAY", raw, row["npc_id"], None),
                (row["event"], raw + " changed", row["npc_id"], None),
                (row["event"], raw, 999999, None),
                (row["event"], raw, row["npc_id"], "Player-1-1978"),
                (row["event"], raw, row["npc_id"], "Pet-0-1-2-3-1978-012ABC"),
            ):
                ns.SpeechCommand("speech hide")
                g.event(event, text, npc, guid)
                assert not popup.IsShown(popup), (event, text, npc, guid)
            if "$N" in row["english"]:
                g.event(row["event"], row["english"].replace("$N", "Someoneelse").replace("$C", "druid"), row["npc_id"])
                assert not popup.IsShown(popup)
            if "$R" in row["english"]:
                g.event(row["event"], row["english"].replace("$R", "human"), row["npc_id"])
                assert not popup.IsShown(popup)

    sample = review["entries"][3]
    raw, npc = sample["english"], sample["npc_id"]
    ns.SpeechCommand("speech off")
    g.event(sample["event"], raw, npc)
    assert not popup.IsShown(popup)
    ns.SpeechCommand("speech on")
    g.event(sample["event"], raw, npc)
    assert popup.IsShown(popup)
    before = len(g.draws)
    g.event(sample["event"], raw, npc)
    assert len(g.draws) == before  # Duplicate event within 0.5 seconds.
    g.tick(0.6)
    g.event(sample["event"], raw, npc)
    assert len(g.draws) == before + 1
    g.tick(15.1)
    assert not popup.IsShown(popup)
    for row in review["entries"][:3]:
        g.event(row["event"], row["english"].replace("$N", "Aeri"), row["npc_id"])
        g.tick(0.6)
    last = g.draws[len(g.draws)]
    assert review["entries"][0]["thai"] not in last
    assert review["entries"][1]["thai"].replace("{name}", "Aeri") in last
    assert review["entries"][2]["thai"] in last
    g.frames.ForeverThaiSpeechEvents.scripts.OnEvent(None, "PLAYER_LEAVING_WORLD")
    assert not popup.IsShown(popup)
    for key, value in (("build", "70999"), ("locale", "frFR"), ("version", "12.1.5")):
        old = g[key]; g[key] = value
        g.event(sample["event"], raw, npc)
        assert not popup.IsShown(popup)
        g[key] = old
    g.event(sample["event"], g.SECRET, npc)
    g.event(sample["event"], raw, npc, g.SECRET)
    assert not popup.IsShown(popup)
    assert g.ForeverThaiObserved is None  # Collection is opt-in.
    ns.SpeechCommand("speech capture on")
    g.event("CHAT_MSG_MONSTER_EMOTE", "A newly observed escort line.", 275744)
    assert g.ForeverThaiObserved.speech[275744].CHAT_MSG_MONSTER_EMOTE[1].text == "A newly observed escort line."
    assert g.ForeverThaiObserved.speechCount == 1
    assert not popup.IsShown(popup)
    g.event("CHAT_MSG_MONSTER_EMOTE", "A newly observed escort line.", 275744)
    assert g.ForeverThaiObserved.speechCount == 1
    for n in range(600):
        g.event("CHAT_MSG_MONSTER_SAY", f"New observed line {n}.", 275744)
    assert g.ForeverThaiObserved.speechCount == 512
    assert g.ForeverThaiObserved.speechBytes <= 256 * 1024
    ns.SpeechCommand("speech capture off")
    ns.SpeechCommand("speech test")
    assert popup.IsShown(popup) and "ทดสอบกล่อง" in g.draws[len(g.draws)]
    for run in re.findall(r"[\u0e00-\u0e7f]+", g.draws[len(g.draws)]):
        assert ns.runs[run], run
    g.tick(16)

    return lua,ns

def preserved_font_pages_and_coordinates(payload,ns):
    baseline=pathlib.Path('/workspace/foreverthai-dev/downloads/ForeverThai-0.462.0-Quest-Skills-PRIVATE-TEST.zip')
    assert sha(baseline.read_bytes())=='d36621b9357a33e909777f31fdc5745ddf96aa579add740364ac60011f30cb62'
    old=LuaRuntime();addon=old.table()
    with zipfile.ZipFile(baseline) as z:
        for name in ['Speech.lua','SpeechData.lua','Match.lua','Bitmap.lua','Observe.lua']:
            assert z.read('ForeverThai/'+name)==payload(name),name
        old.execute(z.read('ForeverThai/Atlas.lua').decode(),'ForeverThai',addon)
        pages=set()
        for idx,glyph in addon.glyphs.items():
            assert [glyph[i] for i in range(1,7)]==[ns.glyphs[idx][i] for i in range(1,7)]
            pages.add(glyph[1])
        for run,indices in addon.runs.items():
            assert ns.runs[run] is not None and list(indices.values())==list(ns.runs[run].values()),run
        for page in pages:assert z.read(f'ForeverThai/Fonts/Thai{page}.tga')==payload(f'Fonts/Thai{page}.tga')
    return dict(baseline='0.462.0 PRIVATE-TEST',prior_runs_checked=sum(1 for _ in addon.runs.items()),prior_glyphs_checked=len(addon.glyphs),prior_page_bytes_checked=len(pages),method='Identical original TGA bytes, glyph rectangles, offsets, advances and run indices imply identical prior pixel shapes. This replaces the unavailable old-version Catalog-delta/UI-archive wrapper; no current API proof is claimed.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=pathlib.Path);parser.add_argument('--report',type=pathlib.Path,default=ROOT/'evidence/npc-cloud-replay05.json');args=parser.parse_args()
    corpus_path=ROOT/'tests/npc_corpus/reviewed-0462.json';review=json.loads(corpus_path.read_text())
    source_manifest={str(p.relative_to(ROOT/'src')):sha(p.read_bytes()) for p in sorted((ROOT/'src/ForeverThai').rglob('*')) if p.is_file()}
    result=dict(candidate=args.archive.name,candidate_sha256=sha(args.archive.read_bytes()),source_manifest_sha256=sha(json.dumps(source_manifest,sort_keys=True).encode()),corpus_sha256=sha(corpus_path.read_bytes()),reference_sha256=sha(REFERENCE.read_bytes()),api_proofs=[],missing_dependencies=['Original forever_speech_source loader and its initial work corpus not supplied; replaced by explicit independent reviewed Dev records.','Blizzard UI archives for 70862/70888 not supplied; no fresh API event-argument documentation proof.','Old version-specific Catalog delta wrappers not supplied; current baseline/data/texture preservation verified separately.'],in_game_windows_verified=False,in_game_mac_m2_verified=False)
    try:
        verify_corpus(review)
        with zipfile.ZipFile(args.archive) as z:
            assert z.testzip() is None
            assert set(z.namelist())==set(source_manifest)
            for name,digest in source_manifest.items():assert sha(z.read(name))==digest,name
            def payload(name):return z.read('ForeverThai/'+name)
            lua,ns=replay(payload,review)
            result['font_preservation']=preserved_font_pages_and_coordinates(payload,ns)
            # Additional adversarial tests preserve fixed NPC-to-NPC names.
            fixed_name_cases=0
            g=lua.globals()
            for row in review['entries']:
                if not re.search(r'\b(Ringo|Torta)\b',row['english']):continue
                raw=row['english'].replace('$N','Aeri').replace('$C','druid').replace('$R','night elf')
                for name in ['Ringo','Torta']:
                    if name not in raw:continue
                    ns.SpeechCommand('speech hide');g.event(row['event'],raw.replace(name,'Aeri'),row['npc_id'])
                    assert not g.frames.ForeverThaiSpeechReader.IsShown(g.frames.ForeverThaiSpeechReader)
                    fixed_name_cases+=1
            rows=review['entries'];result.update(status='passed',independent_unique_forms=len(rows),replayed_builds=['70862','70888'],positive_event_executions=2*len(rows),base_negative_event_executions=12*len(rows),wrong_player_name_executions=2*sum('$N' in r['english'] for r in rows),wrong_race_executions=2*sum('$R' in r['english'] for r in rows),additional_fixed_npc_name_rejections=fixed_name_cases,settings_dedup_timers_bounded_history_opt_in_capture_secret_gates_passed=True,real_bitmap_renderer_and_all_replayed_thai_runs_passed=True)
    except Exception:
        result.update(status='failed',error=traceback.format_exc());raise
    finally:
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
