"""Reproduce the bounded107-input baseline lookup through full registered Events hooks.
Pinned pre-books22 source; raw outputs remain work/private. Not a corpus/source refresh.
Run only when this classification needs reproduction; not part of book regression.
"""
raise SystemExit("HELD: books22 source not user-provided; historical107-input reproduction disabled. Do not consume held payloads.")

import pathlib,json,re,collections,hashlib,subprocess
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];BASE="f2a469dbff82a2b68d569bbb2b16ad2041a74ba4";l=LuaRuntime(unpack_returned_tuples=True);a=l.table()
for n in ['Catalog','Match']:l.execute(subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+n+'.lua']).decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end; GetLocale=function()return "enUS"end; SlashCmdList={}; function CreateFrame()return {RegisterEvent=function()end,SetScript=function(self,k,f) event_handler=f end}end; function UnitGUID()return input_guid end; C_GossipInfo={GetText=function()return input_text end,GetOptions=function()return {}end};GetGreetingText=function()return input_text end;ItemTextGetItem=function()return input_title end;ItemTextGetPage=function()return input_page end;ItemTextGetText=function()return input_text end')
l.execute('local a=...;a.panel={Hide=function()shown_text=nil;shown_title=nil end};a.ShowPage=function(t,x)shown_title=t;shown_text=x end;a.Observe=function()end',a)
l.execute(subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/Events.lua']).decode(),'ForeverThai',a)
g=l.globals();out=[];seen=set();cnt=collections.Counter();pins=json.loads((R/'evidence/main22-sixpart-audit.json').read_text())['source_parts']
for no in range(3482,3488):
 raw=(R/f'work/issue-{no}-decoded.json').read_bytes();pin=next(p for p in pins if p['issue']==no);assert hashlib.sha256(raw).hexdigest()==pin['decoded_sha256'];d=json.loads(raw)
 for i,v in enumerate(d['lines']):
  k=v.get('k');x=v['x'];key=(k,v.get('n'),v.get('t'),v.get('p'),v.get('e'),x)
  if k not in ['gossip','book'] or key in seen:continue
  seen.add(key)
  if re.search(r'\$|<(?:name|player|race|class|unknown)[^>]*>|\{[^}]*\}',x,re.I):continue
  g.input_text=x;g.input_title=v.get('t');g.input_page=v.get('p');g.shown_text=None;g.shown_title=None
  if k=='gossip':
   n=int(v['n']);g.input_guid=f'{"Creature" if n>0 else "GameObject"}-0-1-2-3-{abs(n)}-12345';event={'gossip':'GOSSIP_SHOW','greeting':'QUEST_GREETING'}.get(v['e']);assert event,v
  else:event='ITEM_TEXT_READY'
  g.event_handler(None,event)
  status='supported' if g.shown_text else 'unmatched';cnt[k+'_'+status]+=1
  out.append(dict(issue=no,index=i,kind=k,status=status,record=v,thai_output=g.shown_text,event=event))
assert len(out)==107
(R/'work/nonmain22-scan-private.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(cnt)
