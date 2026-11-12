"""Independent current English/Thai fixtures through actual npcPage and own-ID gates.
Preserve candidate07 runtime values/bytes; do not rerun unchanged speech or Skills.
"""
import collections,hashlib,json,pathlib,re,subprocess
from lupa.lua51 import LuaRuntime,lua_type
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';batch=json.loads((ROOT/'evidence/npc-gossip-08.json').read_text());prior_manifest=json.loads((ROOT/'evidence/private-package-manifest07.json').read_text());source=ROOT/'work/eg'/batch['source_path'];metadata=ROOT/'work/eg'/batch['npc_metadata_path'];assert hashlib.sha256(source.read_bytes()).hexdigest()==batch['source_file_sha256'];assert hashlib.sha256(metadata.read_bytes()).hexdigest()==batch['npc_metadata_sha256'];document=json.loads(source.read_text());npcs=json.loads(metadata.read_text())['npcs'];tree=batch['prior_runtime_git_tree'];lua=LuaRuntime(unpack_returned_tuples=True);addon=lua.table();old=lua.table();load=lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for n in ['Catalog.lua','Match.lua','Atlas.lua']:
 load((RUN/n).read_text(),addon);load(subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+n]).decode(),old)
new_ids={v['npc_id'] for v in batch['fields'] if old.npcs[v['npc_id']] is None};new_lines={(v['npc_id'],v['line_index']) for v in batch['fields']};checks=0
def preserve(a,b,path=()):
 global checks
 if lua_type(a)=='table':
  assert lua_type(b)=='table',path
  for k,v in a.items():preserve(v,b[k],path+(k,))
  for k in b.keys():
   if a[k] is None:assert path in [('glyphs',),('runs',)] or path==('npcs',) and k in new_ids or len(path)==3 and path[0]=='npcs' and path[2]=='lines' and (path[1],k) in new_lines,(path,k)
 elif lua_type(a)!='function':assert a==b,path
 checks+=1
for k,v in old.items():
 if lua_type(v)!='function':preserve(v,addon[k],(k,))
unchanged=0
for name,h in prior_manifest['runtime_manifest'].items():
 data=(ROOT/'src'/name).read_bytes()
 if name.endswith('/Catalog.lua') or name.endswith('/Atlas.lua'):
  before=subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+name.split('/',1)[1]]);assert data.startswith(before),name
 else:assert hashlib.sha256(data).hexdigest()==h,name;unchanged+=1
lua.execute('UnitName=function()return player_name end;UnitClass=function()return player_class, "DRUID"end;UnitRace=function()return player_race end;SECRET={};function issecretvalue(v)return v==SECRET end;function UnitGUID(unit) if input_guid then return input_guid end;local id=unit=="questnpc" and quest_id or input_id;if id then return "Creature-0-1-2-3-"..id.."-12345" end end;C_GossipInfo={GetOptions=function()return {}end}')
g=lua.globals();g.player_name='CloudTester';g.player_class='Druid';g.player_race='Night Elf';events=(RUN/'Events.lua').read_text();dialog=events[events.index('local function dialogTarget('):events.index('local function npcID()')];handler=events[events.index('local function readGossipOptions('):events.index('local function splitStepCount(')];wrapper='local addon=...;local english=true;local mode;local shown={};local function clear()shown.title=nil;shown.text=nil end;addon.ShowPage=function(title,text)shown.title=title;shown.text=text end;addon.Observe=function(...)end;'+dialog+handler+'\nreturn npcPage,shown,function(v)english=v end';page,shown,enabled=lua.execute(wrapper,addon);positive=negative=0;new_prose=0
for field in batch['fields']:
 n=field['npc_id'];text=field['english'];thai=field['thai'];assert field['source_record'] in document[field['field']]['npc:'+str(n)];assert npcs[str(n)]==field['npc_metadata_record'];assert npcs[str(n)]['name']==field['npc_name'];assert hashlib.sha256(text.encode()).hexdigest()==field['english_sha256'];assert hashlib.sha256(thai.encode()).hexdigest()==field['thai_sha256'];assert '$' not in text and '{' not in thai;assert old.TranslateNpc(old.npcs[n],text) is None
 if field['category']=='new_prose':
  new_prose+=1
  for _,entry in old.npcs.items():assert old.TranslateNpc(entry,text) is None
 for context in ['gossip','quest']:
  g.input_id=n;g.quest_id=None;g.input_guid=None;page(context,text);assert shown.title=='บทสนทนา';assert shown.text=='|cffffd987'+field['npc_name']+'|r\n\n'+thai;positive+=1
  for bad in [text+' changed',None,123,g.SECRET]:page(context,bad);assert shown.text is None;negative+=1
  g.input_id=999999999;page(context,text);assert shown.text is None;negative+=1
  g.input_id=n;g.input_guid='Player-1234-ABCD';page(context,text);assert shown.text is None;negative+=1;g.input_guid=None
  enabled(False);page(context,text);assert shown.text is None;negative+=1;enabled(True)
 # Exact literal remains identical for a different current player's class/race/name.
 g.player_name='AnotherTester';g.player_class='Mage';g.player_race='Human';g.input_id=n;page(field['field']=='greeting' and 'quest' or 'gossip',text);assert shown.text=='|cffffd987'+field['npc_name']+'|r\n\n'+thai;positive+=1
 g.player_name='CloudTester';g.player_class='Druid';g.player_race='Night Elf'
 # Real questnpc fallback is allowed only for quest context.
 g.input_id=None;g.quest_id=n;page('quest',text);assert shown.text=='|cffffd987'+field['npc_name']+'|r\n\n'+thai;positive+=1;page('gossip',text);assert shown.text is None;negative+=1;g.quest_id=None
 for run in re.findall(r'[\u0e00-\u0e7f]+',thai):assert addon.runs[run] is not None,run
assert new_prose==4
# Decode only new bitmap pages; all candidate07 pages were checked by byte hash above.
new_pages=[p for p in (RUN/'Fonts').glob('Thai*.tga') if 'ForeverThai/Fonts/'+p.name not in prior_manifest['runtime_manifest']]
for p in new_pages:
 with Image.open(p) as im:assert im.size==(1024,1024) and im.mode=='RGBA';assert im.getchannel('A').getextrema()==(0,255)
result=dict(status='passed',unique_source_cases=len(batch['fields']),parameterized_positive_executions=positive,negative_executions=negative,new_prose=4,exact_literal_source_variants=3,own_id_form_reuse=1,own_id_reuse_bindings=2,old_runtime_values_preserved=checks,candidate07_unchanged_component_hashes=unchanged,new_font_pages_decoded=[p.name for p in new_pages],prior_runtime_tree=tree,source_file_sha256=batch['source_file_sha256'],npc_metadata_sha256=batch['npc_metadata_sha256'],npc_handler_sha256=hashlib.sha256((dialog+handler).encode()).hexdigest(),scope='Actual existing npcPage/readGossipOptions/dialogTarget with mocked surrounding UI. Independent full English/Thai evidence; exact own-ID, changed body/type/secret/GUID/mode/fallback gates. No speech event additions, shared matcher changes, live game check, or rerun of Skills/NPC686.')
(ROOT/'evidence/npc-gossip-regression08.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
