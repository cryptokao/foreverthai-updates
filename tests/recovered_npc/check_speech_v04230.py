"""Exercise real subtitle Lua and font assets without an interactive game client."""
import hashlib
import json
import re
import zipfile
import sys
from pathlib import Path
from lupa.lua51 import LuaRuntime
from io import BytesIO
from PIL import Image

work = Path(__file__).resolve().parent
addon = work.parent / "outputs/ForeverThai"
review = json.loads((work / "npc-speech-reviewed-v04230.json").read_text(encoding="utf8"))
package = zipfile.ZipFile(sys.argv[1]) if len(sys.argv) > 1 else None
def payload(name):
    return package.read("ForeverThai/" + name) if package else (addon / name).read_bytes()
tested_version = re.search(r"^## Version: (.+)$", payload("ForeverThai.toc").decode(), re.M)[1].strip()
baseline_version = sys.argv[2] if len(sys.argv) > 2 else "0.422.0"
extra_rows = []
if tuple(map(int, tested_version.split("."))) >= (0, 424, 0):
    from forever_speech_source import load as load_forever_speech
    extra_rows = load_forever_speech(work, tested_version)
review["entries"] += extra_rows

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

api_proofs = []
for build in ("70862", "70888"):
    path, = work.glob(f"blizzard-ui-{build}-*.zip")
    with zipfile.ZipFile(path) as z:
        name, = [n for n in z.namelist() if n.endswith("/ChatInfoDocumentation.lua")]
        source = z.read(name).decode()
    for event in ("CHAT_MSG_MONSTER_SAY", "CHAT_MSG_MONSTER_YELL", "CHAT_MSG_MONSTER_WHISPER", "CHAT_MSG_MONSTER_EMOTE"):
        block = source.split('LiteralName = "' + event + '"', 1)[1].split('\n\t\t},', 1)[0]
        fields = re.findall(r'Name = "([^"]+)"', block)
        assert fields[0] == "text" and fields[11] == "guid", (build, event, fields)
    api_proofs.append({"build": build, "archive": path.name,
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "four_events_have_guid_in_argument_12": True})

with zipfile.ZipFile(work.parent / f"outputs/ForeverThai-{baseline_version}-Windows-Mac.zip") as baseline:
    prior_core_bytes_identical=all(baseline.read("ForeverThai/"+name)==payload(name)
                                   for name in ("Catalog.lua","Match.lua","Tracker.lua"))
    for name in ("Catalog.lua", "Match.lua", "Tracker.lua"):
        before = baseline.read("ForeverThai/" + name)
        if name == "Catalog.lua" and before != payload(name):
            if (baseline_version, tested_version) == ("0.427.0", "0.428.0"):
                from verify_catalog_v04280 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.430.0", "0.431.0"):
                from verify_catalog_v04310 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.432.0", "0.434.0"):
                from verify_catalog_v04340 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.434.0", "0.435.0"):
                from verify_catalog_v04350 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.435.0", "0.436.0"):
                from verify_catalog_v04360 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.436.0", "0.437.0"):
                from verify_catalog_v04370 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.437.0", "0.438.0"):
                from verify_catalog_v04380 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.438.0", "0.439.0"):
                from verify_catalog_v04390 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.440.0", "0.441.0"):
                from verify_catalog_v04410 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.441.0", "0.442.0"):
                from verify_catalog_v04420 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.442.0", "0.443.0"):
                from verify_catalog_v04430 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.443.0", "0.444.0"):
                from verify_catalog_v04440 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.444.0", "0.445.0"):
                from verify_catalog_v04450 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.445.0", "0.446.0"):
                from verify_catalog_v04460 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.446.0", "0.447.0"):
                from verify_catalog_v04470 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.447.0", "0.448.0"):
                from verify_catalog_v04480 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.450.0", "0.451.0"):
                from verify_catalog_v04510 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.457.0", "0.458.0"):
                from verify_catalog_v04580 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.458.0", "0.459.0"):
                from verify_catalog_v04590 import verify as verify_catalog_delta
            elif (baseline_version, tested_version) == ("0.460.0", "0.461.0"):
                from verify_catalog_v04610 import verify as verify_catalog_delta
            else:
                assert (baseline_version, tested_version) == ("0.431.0", "0.432.0")
                from verify_catalog_v04320 import verify as verify_catalog_delta
            verify_catalog_delta(before, payload(name), work)
        elif name == "Match.lua" and before != payload(name):
            from unicode_whitespace_fix import verify as verify_unicode_fix
            verify_unicode_fix(before, payload(name))
        else:
            assert before == payload(name), name
    old = lua.table()
    lua.execute(baseline.read("ForeverThai/Atlas.lua").decode(), "ForeverThai", old)
    images, shape_cache = {}, {}
    def shape(namespace, glyph_id, is_old):
        key = (is_old, glyph_id)
        if key not in shape_cache:
            page, x, y, width, offset, advance = [namespace.glyphs[glyph_id][n] for n in range(1, 7)]
            image_key = (is_old, page)
            if image_key not in images:
                pixels_file = baseline.read(f"ForeverThai/Fonts/Thai{page}.tga") if is_old else payload(f"Fonts/Thai{page}.tga")
                images[image_key] = Image.open(BytesIO(pixels_file))
            pixels = images[image_key].crop((x, y, x + width, y + 56)).tobytes()
            shape_cache[key] = (width, offset, advance, hashlib.sha256(pixels).hexdigest())
        return shape_cache[key]
    old_run_count = 0
    for run, pieces in old.runs.items():
        replacement = ns.runs[run]
        assert replacement is not None and len(pieces) == len(replacement), run
        assert [shape(old, n, True) for n in pieces.values()] == [shape(ns, n, False) for n in replacement.values()], run
        old_run_count += 1
    for image in images.values():
        image.close()
result = {"version": tested_version, "reviewed_reference_lines": 12,
          "reviewed_published_forever_source_forms": len(extra_rows),
          "baseline": baseline_version,
          "replayed_builds": ["70862", "70888"], "api_proofs": api_proofs,
          "positive_and_negative_event_tests_passed": True,
          "opt_in_capture_deduplication_and_512_record_limit_passed": True,
          "all_prior_quest_gossip_book_and_tracker_records_byte_identical": prior_core_bytes_identical,
          "prior_quest_gossip_book_and_tracker_preserved_or_verified_source_delta": True,
          "all_thai_runs_in_atlas": True, "live_forever_speech_transcript_confirmed": False,
          "previous_thai_runs_with_identical_pixel_shapes": old_run_count,
          "tested_archive": Path(sys.argv[1]).name if package else None,
          "tested_archive_sha256": hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() if package else None,
          "in_game_windows_verified": False, "in_game_mac_m2_verified": False}
(work / f"npc-speech-replay-v{int(tested_version.split('.')[1]):04d}0.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
print(f"NPC subtitles: {len(review['entries'])} reviewed forms on two builds; wrong NPC/event/text/player, secret values, settings, timers, bounded history, capture limits and Thai atlas passed.")
if package:
    package.close()
