"""Exact current public NPC/book captures; independent Thai before package review.
No player-name literal is accepted; fonts may remain pending Root wording review.
"""
import hashlib,json,pathlib,re,subprocess
from lupa.lua51 import LuaRuntime,lua_type
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';batch=json.loads((ROOT/'evidence/public-literals-10.json').read_text());tree=batch['prior_runtime_git_tree'];lua=LuaRuntime(unpack_returned_tuples=True);a=lua.table();old=lua.table();load=lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for name in ['Catalog.lua','Match.lua','Atlas.lua']:
 load((RUN/name).read_text(),a);load(subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+name]).decode(),old)
newids={v['npc_id'] for v in batch['fields'] if v['kind']=='npc' and old.npcs[v['npc_id']] is None};newlines={(v['npc_id'],v['line_index']) for v in batch['fields'] if v['kind']=='npc'};newtitles={v['book_title'] for v in batch['fields'] if v['kind']=='book'};checks=0
for key,pin in batch['source_pins'].items():
 raw=(ROOT/f'work/issue-{key}.json').read_bytes();decoded=(ROOT/f'work/issue-{key}-decoded.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==pin['issue_json_sha256'];assert hashlib.sha256(json.loads(raw)['body'].encode()).hexdigest()==pin['body_sha256'];assert hashlib.sha256(decoded).hexdigest()==pin['decoded_sha256'];assert json.loads(decoded)['build']=='70888'
def preserve(before,after,path=()):
 global checks
 if lua_type(before)=='table':
  assert lua_type(after)=='table',path
  for k,v in before.items():preserve(v,after[k],path+(k,))
  for k in after.keys():
   if before[k] is None:assert path in [('runs',),('glyphs',)] or path==('npcs',) and k in newids or path==('books',) and k in newtitles or len(path)==3 and path[0]=='npcs' and path[2]=='lines' and (path[1],k) in newlines,(path,k)
 elif lua_type(before)!='function':assert before==after,path
 checks+=1
for k,v in old.items():
 if lua_type(v)!='function':preserve(v,a[k],(k,))
oldnames=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',tree],text=True).splitlines();unchanged=0
for name in oldnames:
 before=subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+name]);after=(RUN/name).read_bytes()
 if name in ['Catalog.lua','Atlas.lua']:assert after.startswith(before)
 else:assert after==before,name;unchanged+=1
lua.execute('UnitName=function()return player_name end;UnitClass=function()return player_class,player_class_id end;UnitRace=function()return player_race end;SECRET={};function issecretvalue(v)return v==SECRET end;function UnitGUID(unit) if input_guid then return input_guid end;local id=unit=="questnpc" and quest_id or input_id;if id then return "Creature-0-1-2-3-"..id.."-12345" end end;C_GossipInfo={GetOptions=function()return {}end}')
g=lua.globals();g.player_name='CloudTester';g.player_class='Druid';g.player_class_id='DRUID';g.player_race='Night Elf';events=(RUN/'Events.lua').read_text();dialog=events[events.index('local function dialogTarget('):events.index('local function npcID()')];handler=events[events.index('local function readGossipOptions('):events.index('local function splitStepCount(')];page,shown,enabled=lua.execute('local addon=...;local english=true;local mode;local shown={};local function clear()shown.text=nil;shown.title=nil end;addon.Observe=function()end;addon.ShowPage=function(title,text)shown.title=title;shown.text=text end;'+dialog+handler+'\nreturn npcPage,shown,function(v)english=v end',a);np=nn=bp=bn=0;missing=set()
for f in batch['fields']:
 source=json.loads((ROOT/f"work/issue-{f['issue']}-decoded.json").read_text());record=source['lines'][f['source_line_index']];assert record==f['source_record'] and record['x']==f['english'];assert hashlib.sha256(f['english'].encode()).hexdigest()==f['english_sha256'];assert hashlib.sha256(f['thai'].encode()).hexdigest()==f['thai_sha256'];assert '$' not in f['english'] and '{' not in f['thai']
 if f['kind']=='book':continue
 n=f['npc_id'];text=f['english'];thai=f['thai'];assert record['n']==str(n) and record['s']==f['npc_name'];assert source['npcs'][str(n)]==f['npc_metadata_record'];assert old.TranslateNpc(old.npcs[n],text) is None
 for reuse in f['full_body_reuse_matches']:assert old.TranslateNpc(old.npcs[reuse['npc_id']],text)==reuse['thai']
 if f['previous_translation']:
  p=f['previous_translation']
  if p.get('line_index'):assert old.npcs[p['npc_id']].lines[p['line_index']][2]==thai
  else:assert old.TranslateNpc(old.npcs[p['npc_id']],text)==thai
 else:
  for _,npc in old.npcs.items():assert old.TranslateNpc(npc,text) is None
 for context in ['gossip','quest']:
  g.input_id=n;g.quest_id=None;g.input_guid=None;page(context,text);assert shown.title=='บทสนทนา' and shown.text=='|cffffd987'+f['npc_name']+'|r\n\n'+thai;np+=1
  for bad in [text+' changed',None,123,g.SECRET]:page(context,bad);assert shown.text is None;nn+=1
  g.input_id=999999999;page(context,text);assert shown.text is None;nn+=1;g.input_id=n;g.input_guid='Player-1234-ABCD';page(context,text);assert shown.text is None;nn+=1;g.input_guid=None;enabled(False);page(context,text);assert shown.text is None;nn+=1;enabled(True)
 g.player_name='AnotherTester';g.player_class='Mage';g.player_class_id='MAGE';g.player_race='Human';page('gossip',text);assert shown.text=='|cffffd987'+f['npc_name']+'|r\n\n'+thai;np+=1;g.player_name='CloudTester';g.player_class='Druid';g.player_class_id='DRUID';g.player_race='Night Elf';g.input_id=None;g.quest_id=n;page('quest',text);assert shown.text=='|cffffd987'+f['npc_name']+'|r\n\n'+thai;np+=1;page('gossip',text);assert shown.text is None;nn+=1;g.quest_id=None
# Book fixture keeps actual readBook, with independent title/page/full-body pairs.
lua.execute('ItemTextGetItem=function()return input_title end;ItemTextGetPage=function()return input_page end;ItemTextGetText=function()return input_text end');bookhandler=events[events.index('local function readBook()'):events.index('\nlocal handlers =',events.index('local function readBook()'))];readbook,shown,enabled=lua.execute('local addon=...;local english=true;local mode;local shown={};local function clear()shown.text=nil;shown.title=nil end;addon.ShowPage=function(title,text)shown.title=title;shown.text=text end;'+bookhandler+'\nreturn readBook,shown,function(v)english=v end',a)
for f in batch['fields']:
 if f['kind']!='book':continue
 assert f['source_record']['t']==f['book_title'] and f['source_record']['p']==f['page'];assert old.books[f['book_title']] is None;assert not f['whole_book_total_proven'] and f['total_pages'] is None
 for _,book in old.books.items():
  for p,e in book.items():
   if isinstance(p,(int,float)) and lua_type(e)=='table':assert old.Translate(e,f['english']) is None
 g.input_title=f['book_title'];g.input_page=f['page'];g.input_text=f['english'];readbook();assert shown.title=='เอกสาร · หน้า '+str(f['page']);assert shown.text=='|cffffd987'+f['thai_title']+'|r\n\n'+f['thai'];bp+=1
 for title,page,text in [(f['book_title']+' changed',f['page'],f['english']),(f['book_title'],f['page']+1,f['english']),(f['book_title'],0,f['english']),(f['book_title'],f['page'],f['english']+' changed'),(f['book_title'],f['page'],g.SECRET)]:
  g.input_title=title;g.input_page=page;g.input_text=text;readbook();assert shown.text is None;bn+=1
for f in batch['fields']:
 for text in [f['thai']]+([f['thai_title']] if f['kind']=='book' else []):
  for run in re.findall(r'[\u0e00-\u0e7f]+',text):
   if a.runs[run] is None:missing.add(run)
for p in RUN.rglob('*.lua'):assert lua.eval('function(s)return loadstring(s)~=nil end')(p.read_text())
report=dict(status='text_and_preservation_passed',unique_npc_source_cases=14,npc_positive_executions=np,npc_negative_executions=nn,unique_book_source_cases=2,book_positive_executions=bp,book_negative_executions=bn,old_runtime_values_preserved=checks,unchanged_component_bytes=unchanged,prior_runtime_tree=tree,font_ready=not missing,font_runs_pending_review=len(missing),pending_thai_runs=sorted(missing),whole_book_total_proven=False,scope='Actual unchanged NPC/book event handlers with mocked UI. Independent full source/Thai evidence and public issue hashes/index lineage. No hardcoded player-name translation. Text-only review stage: missing font runs explicitly reported, not a packaged/bitmap-ready or in-game claim. No rerun of unchanged Skills/NPC686/main suites.')
(ROOT/'evidence/public-literal-regression10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='pending_thai_runs'},indent=2))
