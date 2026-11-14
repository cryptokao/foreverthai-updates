"""Two typed broadcast source templates; independent full rendered class oracles."""
import hashlib,json,pathlib,re,subprocess
from lupa.lua51 import LuaRuntime,lua_type
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';batch=json.loads((ROOT/'evidence/npc-templates-09.json').read_text());cases=json.loads((ROOT/'tests/npc-template-cases09.json').read_text());tree=batch['prior_runtime_git_tree'];source=ROOT/'work/eg/data/wowf/1.60.1.70888/texts.enUS.json';meta=ROOT/'work/eg/data/wowf/1.60.1.70888/npcs.json';assert hashlib.sha256(source.read_bytes()).hexdigest()==batch['source_file_sha256'];assert hashlib.sha256(meta.read_bytes()).hexdigest()==batch['npc_metadata_sha256'];doc=json.loads(source.read_text());npcs=json.loads(meta.read_text())['npcs'];lua=LuaRuntime(unpack_returned_tuples=True);a=lua.table();old=lua.table();load=lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for n in ['Catalog.lua','Match.lua','Atlas.lua']:
 load((RUN/n).read_text(),a);load(subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+n]).decode(),old)
later=json.loads((ROOT/'evidence/public-literals-10.json').read_text())['fields'] if (ROOT/'evidence/public-literals-10.json').exists() else [];allowed=batch['fields']+[v for v in later if v['kind']=='npc'];later_books={v['book_title'] for v in later if v['kind']=='book'};newids={v['npc_id'] for v in allowed if old.npcs[v['npc_id']] is None};newlines={(v['npc_id'],v['line_index']) for v in allowed};checks=0
def preserve(before,after,path=()):
 global checks
 if lua_type(before)=='table':
  assert lua_type(after)=='table',path
  for k,v in before.items():preserve(v,after[k],path+(k,))
  for k in after.keys():
   if before[k] is None:assert path in [('runs',),('glyphs',)] or path==('npcs',) and k in newids or path==('books',) and k in later_books or len(path)==3 and path[0]=='npcs' and path[2]=='lines' and (path[1],k) in newlines,(path,k)
 elif lua_type(before)!='function':assert before==after,path
 checks+=1
for k,v in old.items():
 if lua_type(v)!='function':preserve(v,a[k],(k,))
oldnames=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',tree],text=True).splitlines();unchanged=0
for name in oldnames:
 before=subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+name]);after=(RUN/name).read_bytes()
 if name in ['Catalog.lua','Atlas.lua']:assert after.startswith(before)
 else:assert after==before,name;unchanged+=1
lua.execute('UnitName=function()return player_name end;UnitClass=function()return player_class,player_class_id end;UnitRace=function()return player_race end;SECRET={};function issecretvalue(v)return v==SECRET end;function UnitGUID(unit)if unit=="npc" then return "Creature-0-1-2-3-"..input_id.."-12345" end end;C_GossipInfo={GetOptions=function()return {}end}')
g=lua.globals();g.player_name='CloudTester';g.player_race='Night Elf';events=(RUN/'Events.lua').read_text();dialog=events[events.index('local function dialogTarget('):events.index('local function npcID()')];handler=events[events.index('local function readGossipOptions('):events.index('local function splitStepCount(')];page,shown=lua.execute('local addon=...;local english=true;local mode;local shown={};local function clear()shown.text=nil;shown.title=nil end;addon.Observe=function()end;addon.ShowPage=function(title,text)shown.title=title;shown.text=text end;'+dialog+handler+'\nreturn npcPage,shown',a)
for f in batch['fields']:
 assert f['source_record'] in doc['gossip']['npc:'+str(f['npc_id'])];assert f['npc_metadata_record']==npcs[str(f['npc_id'])];assert f['source_record']['template']=='broadcastText';assert f['source_record']['broadcastTextIds'];assert f['english'].count('$c')==1 and f['english'].count('$')==1
 assert hashlib.sha256(f['english'].encode()).hexdigest()==f['english_sha256'];assert hashlib.sha256(f['thai'].encode()).hexdigest()==f['thai_sha256']
positive=negative=0
for c in cases:
 field=next(f for f in batch['fields'] if f['npc_id']==c['npc_id']);assert c['english'].replace(c['class'],'$c')==field['english'];g.player_class=c['class'];g.player_class_id=c['class_id'];g.input_id=c['npc_id'];assert old.TranslateNpc(old.npcs[c['npc_id']],c['english']) is None
 for context in ['gossip','quest']:
  page(context,c['english']);assert shown.title=='บทสนทนา' and shown.text=='|cffffd987'+field['npc_name']+'|r\n\n'+c['thai'];positive+=1
  for bad in [c['english']+' changed',field['english'],c['english'].replace(c['class'],'CloudTester'),c['english'].replace(c['class'],'Night Elf'),None,123,g.SECRET]:page(context,bad);assert shown.text is None;negative+=1
  # Source belongs to another current class, even if its words are otherwise exact.
  g.player_class='Priest';g.player_class_id='PRIEST';page(context,c['english']);assert shown.text is None;negative+=1;g.player_class=c['class'];g.player_class_id=c['class_id']
  g.input_id=999999999;page(context,c['english']);assert shown.text is None;negative+=1;g.input_id=c['npc_id']
 for run in re.findall(r'[\u0e00-\u0e7f]+',c['thai']):assert a.runs[run] is not None,run
for path in RUN.rglob('*.lua'):assert lua.eval('function(s)return loadstring(s)~=nil end')(path.read_text())
toc=(RUN/'ForeverThai.toc').read_text();paths=[v.strip().replace('\\','/') for v in toc.splitlines() if v.strip() and not v.startswith('#')];assert all((RUN/v).is_file() for v in paths)
newpages=[p for p in (RUN/'Fonts').glob('Thai*.tga') if 'Fonts/'+p.name not in oldnames]
for p in newpages:
 with Image.open(p) as im:assert im.size==(1024,1024) and im.mode=='RGBA';assert im.getchannel('A').getextrema()==(0,255)
result=dict(status='passed',unique_source_templates=2,independent_rendered_cases=len(cases),parameterized_positive_executions=positive,negative_executions=negative,old_runtime_values_preserved=checks,previous_unchanged_component_bytes=unchanged,new_font_pages_decoded=[p.name for p in newpages],lua_files_compiled=len(list(RUN.rglob('*.lua'))),toc_paths=len(paths),prior_runtime_tree=tree,source_file_sha256=batch['source_file_sha256'],independent_cases_sha256=hashlib.sha256((ROOT/'tests/npc-template-cases09.json').read_bytes()).hexdigest(),scope='Actual existing npcPage handler and matcher; source template tagged broadcastText with own-ID and broadcastTextIds. Static complete rendered English/Thai oracles for three player classes. No guessed normalized identities, shared matcher edits, live game proof, or rerun of unchanged Skills/NPC686/main/book suites.')
(ROOT/'evidence/npc-template-regression09.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
