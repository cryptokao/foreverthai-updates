"""One exact new own-ID binding; preserve every candidate11 value/component."""
import hashlib,json,pathlib,re,subprocess
from lupa.lua51 import LuaRuntime,lua_type
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';doc=json.loads((ROOT/'evidence/npc-reuse-12.json').read_text());f=doc['fields'][0];tree=doc['prior_runtime_tree'];l=LuaRuntime(unpack_returned_tuples=True);a=l.table();old=l.table();load=l.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for n in ['Catalog.lua','Match.lua','Atlas.lua']:
 load((RUN/n).read_text(),a);load(subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+n]).decode(),old)
checks=0
def preserve(before,after,path=()):
 global checks
 if lua_type(before)=='table':
  assert lua_type(after)=='table',path
  for k,v in before.items():preserve(v,after[k],path+(k,))
  for k in after.keys():
   if before[k] is None:assert path==('npcs',251001,'lines') and k==f['line_index'],(path,k)
 elif lua_type(before)!='function':assert before==after,path
 checks+=1
for k,v in old.items():
 if lua_type(v)!='function':preserve(v,a[k],(k,))
manifest=json.loads((ROOT/'evidence/private-package-manifest11.json').read_text());unchanged=0
for name,h in manifest['runtime_manifest'].items():
 p=ROOT/'src'/name
 if name=='ForeverThai/Catalog.lua':assert p.read_bytes().startswith(subprocess.check_output(['git','-C',str(ROOT),'show',tree+':Catalog.lua']))
 else:assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name;unchanged+=1
audit=json.loads((ROOT/'evidence/new-capture-audit12.json').read_text());pin=next(v for v in audit['source_pins'] if v['issue']==f['issue']);source_raw=(ROOT/f"work/issue-{f['issue']}-decoded.json").read_bytes();assert hashlib.sha256(source_raw).hexdigest()==pin['decoded_sha256'];source=json.loads(source_raw);assert source['lines'][f['source_line_index']]==f['source_record'];assert source['npcs']['251001']==f['npc_metadata_record'];assert f['source_record']['x']==f['english'];assert hashlib.sha256(f['english'].encode()).hexdigest()==f['english_sha256'];assert hashlib.sha256(f['thai'].encode()).hexdigest()==f['thai_sha256']
l.execute('UnitName=function()return player_name end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end;SECRET={};issecretvalue=function(v)return v==SECRET end;function UnitGUID(unit)if input_guid then return input_guid end;if unit=="npc" and input_id then return "Creature-0-1-2-3-"..input_id.."-12345" end;if unit=="questnpc" and quest_id then return "Creature-0-1-2-3-"..quest_id.."-12345" end end;C_GossipInfo={GetOptions=function()return {}end}')
g=l.globals();g.player_name='CloudTester';assert old.TranslateNpc(old.npcs[251001],f['english']) is None
for reuse in f['all_full_body_reuse_matches']:assert old.TranslateNpc(old.npcs[reuse['npc_id']],f['english'])==reuse['thai']
e=(RUN/'Events.lua').read_text();dialog=e[e.index('local function dialogTarget('):e.index('local function npcID()')];handler=e[e.index('local function readGossipOptions('):e.index('local function splitStepCount(')];page,shown,enabled=l.execute('local addon=...;local english=true;local mode;local shown={};local function clear()shown.text=nil;shown.title=nil end;addon.Observe=function()end;addon.ShowPage=function(title,text)shown.title=title;shown.text=text end;'+dialog+handler+'\nreturn npcPage,shown,function(v)english=v end',a);positive=negative=0;expected='|cffffd987Deathguard Kristof|r\n\n'+f['thai']
for context in ['gossip','quest']:
 g.input_id=251001;g.quest_id=None;g.input_guid=None;page(context,f['english']);assert shown.title=='บทสนทนา' and shown.text==expected;positive+=1
 for text in [f['english']+' changed',None,123,g.SECRET]:page(context,text);assert shown.text is None;negative+=1
 g.input_id=999999999;page(context,f['english']);assert shown.text is None;negative+=1;g.input_id=251001;g.input_guid='Player-1-0002';page(context,f['english']);assert shown.text is None;negative+=1;g.input_guid=None;enabled(False);page(context,f['english']);assert shown.text is None;negative+=1;enabled(True)
g.player_name='AnotherTester';page('gossip',f['english']);assert shown.text==expected;positive+=1;g.input_id=None;g.quest_id=251001;page('quest',f['english']);assert shown.text==expected;positive+=1;page('gossip',f['english']);assert shown.text is None;negative+=1
for run in re.findall(r'[\u0e00-\u0e7f]+',f['thai']):assert a.runs[run] is not None,run
report=dict(status='passed',unique_source_cases=1,new_prose=0,new_thai_texts=0,new_own_id_reuse_bindings=1,parameterized_positive_executions=positive,negative_executions=negative,independent_prior_full_body_reuse_matches=len(f['all_full_body_reuse_matches']),old_runtime_values_preserved=checks,unchanged_candidate11_files=unchanged,catalog_sha256=hashlib.sha256((RUN/'Catalog.lua').read_bytes()).hexdigest(),prior_runtime_tree=tree,font_changes=False,scope='Actual existing NPC page handler, exact current public own-ID/body and retained Thai from independent prior candidate11 records. All prior values/135otherfile bytes retained including Speech.lua/Match/Atlas/protected assets. Existing Thai runs present; no font rebuild or unchanged686/party/Skills/main suite rerun. Not in immutable ZIP11 or game proof.')
(ROOT/'evidence/npc-reuse-regression12.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
