"""Only the17 new book sources: actual full Events registration, static reviewed-or-pending Thai oracles.
No font/old NPC/Skill/party suites. Source raw is read privately for lineage, never printed.
"""
import pathlib,json,hashlib,subprocess
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parents[1];run=R/'src/ForeverThai';batch=json.loads((R/'evidence/books22-pairs.json').read_text());audit=json.loads((R/'evidence/nonmain22-literal-audit.json').read_text());BASE=batch['prior_source'];sha=lambda b:hashlib.sha256(b).hexdigest()
def before(name):return subprocess.check_output(['git','-C',str(R),'show',BASE+':src/ForeverThai/'+name])
base=before('Catalog.lua');now=(run/'Catalog.lua').read_bytes();assert sha(base)==batch['prior_catalog_sha256'];assert now.startswith(base)
paths=subprocess.check_output(['git','-C',str(R),'ls-tree','-r','--name-only',BASE+':src/ForeverThai'],text=True).splitlines();assert len(paths)==141
unchanged=[]
for name in paths:
 if name!='Catalog.lua':assert (run/name).read_bytes()==before(name),name;unchanged.append(name)
assert sorted(p.relative_to(run).as_posix() for p in run.rglob('*') if p.is_file())==sorted(paths)
l=LuaRuntime(unpack_returned_tuples=True);a=l.table();old=l.table()
for n in ['Catalog','Match']:
 l.execute((run/f'{n}.lua').read_text(),'ForeverThai',a);l.execute(before(n+'.lua').decode(),'ForeverThai',old)
l.execute('''UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end;SECRET={};issecretvalue=function(v)return v==SECRET end;GetLocale=function()return "enUS"end;SlashCmdList={};function CreateFrame()return {RegisterEvent=function(self,e)registered[e]=true end,SetScript=function(self,k,f)event_handler=f end}end;registered={};ItemTextGetItem=function()return input_title end;ItemTextGetPage=function()return input_page end;ItemTextGetText=function()return input_text end''')
l.execute('local a=...;a.panel={Hide=function()shown_text=nil;shown_title=nil end};a.ShowPage=function(t,x)shown_title=t;shown_text=x end;a.Observe=function()end',a)
l.execute((run/'Events.lua').read_text(),'ForeverThai',a);g=l.globals();assert g.registered['ITEM_TEXT_READY'];positive=negative=0;final=[]
for pin in audit['source_parts']:
 b=(R/f"work/issue-{pin['issue']}-decoded.json").read_bytes();assert sha(b)==pin['decoded_sha256']
for f in batch['fields']:
 p=f['page'];title=f['book_title'];x=f['english'];thai=f['thai'];pos=f['source_position'];v=json.loads((R/f"work/issue-{pos['issue']}-decoded.json").read_text())['lines'][pos['line_index']]
 assert (v['k'],v['e'],v['t'],v['p'],v['x'])==('book','page',title,p,x);assert sha(x.encode())==f['english_sha256'];assert sha(thai.encode())==f['thai_sha256'];assert old.books[title] is None
 assert a.books[title][p][1]==f['signature'];assert a.books[title].title==f['thai_title']
 g.input_title=title;g.input_page=p;g.input_text=x;g.event_handler(None,'ITEM_TEXT_READY');assert g.shown_title=='เอกสาร · หน้า '+str(p);assert g.shown_text=='|cffffd987'+f['thai_title']+'|r\n\n'+thai;positive+=1
 for bt,bp,bx in [(title+' changed',p,x),(title,p+1,x),(title,0,x),(title,p,x+' changed'),(title,p,g.SECRET),(title,p,None)]:
  g.input_title=bt;g.input_page=bp;g.input_text=bx;g.event_handler(None,'ITEM_TEXT_READY');assert g.shown_text is None,(p,bp);negative+=1
 final.append(dict(page=p,english_sha256=f['english_sha256'],thai_sha256=f['thai_sha256']))
assert len(batch['fields'])==17 and positive==17 and negative==102
report=dict(status='passed_text_routes_pending_Root_wording_review',unique_book_source_cases=17,positive_executions=positive,negative_executions=negative,negative_kinds=['wrong exact title','wrong page','page zero','changed fullbody','secret fullbody','nil fullbody'],actual_hook='full unchanged Events.lua registered ITEM_TEXT_READY, real Catalog/Match; mocked UI sink, not bitmap or livegame',baseline_source=BASE,baseline_catalog_sha256=sha(base),final_catalog_sha256=sha(now),old_catalog_exact_prefix_preserved=True,unchanged_runtime_files=len(unchanged),runtime_files=141,protected28_Core_Speech70938_preserved='all140 non-Catalog files byte-equal to approved f2 source; no gates/settings/Questie/font change',approved_MAIN21_preserved=True,final_text_hashes=final,new_main_fields=0,new_thai_book_pages=17,thai_reuse_pages=0,fonts_build_version_package_feed='unchanged; not tested/claimed ready',whole_book_total_proven=False,old_suites_rerun=False)
(R/'evidence/books22-regression.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='final_text_hashes'},ensure_ascii=False,indent=2))
