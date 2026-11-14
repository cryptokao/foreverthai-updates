"""Exact book event/title/page/body checks and own-ID historical label aliases."""
import hashlib,json,pathlib,re
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';batch=json.loads((ROOT/'evidence/books-labels-07.json').read_text());source=ROOT/'work/eg/data/wowf/1.60.1.70888/texts.enUS.json';raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==batch['source_file_sha256'];document=json.loads(raw)
lua=LuaRuntime(unpack_returned_tuples=True);addon=lua.table();load=lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for n in ['Catalog','Match','Atlas']:load((RUN/f'{n}.lua').read_text(),addon)
lua.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end;SECRET={};function issecretvalue(v)return v==SECRET end;function ItemTextGetItem()return input_title end;function ItemTextGetPage()return input_page end;function ItemTextGetText()return input_text end')
events=(RUN/'Events.lua').read_text();handler=events[events.index('local function readBook()'):events.index('\nlocal handlers =',events.index('local function readBook()'))]
# Keep the actual readBook function; replace only its surrounding UI state.
wrapper='local addon=...;local english=true;local mode;local shown={};local function clear(kind) shown.title=nil;shown.text=nil;shown.cleared=kind end;addon.ShowPage=function(title,text)shown.title=title;shown.text=text end;'+handler+'\nreturn readBook,shown,function(value)english=value end'
read_book,shown,enabled=lua.execute(wrapper,addon);g=lua.globals();positive=negative=0
for field in batch['fields']:
 record=document['books'][field['item']][str(field['page'])];assert record==field['source_record'];assert record['title']==field['book_title'] and record['texts'][0]['text']==field['english'];assert hashlib.sha256(field['english'].encode()).hexdigest()==field['english_sha256'];assert hashlib.sha256(field['thai'].encode()).hexdigest()==field['thai_sha256']
 g.input_title=field['book_title'];g.input_page=field['page'];g.input_text=field['english'];read_book()
 assert shown.title=='เอกสาร · หน้า '+str(field['page']);assert shown.text=='|cffffd987'+addon.books[field['book_title']].title+'|r\n\n'+field['thai'];positive+=1
 for title,page,text in [(field['book_title']+' changed',field['page'],field['english']),(field['book_title'],field['page']+1,field['english']),(field['book_title'],0,field['english']),(field['book_title'],field['page'],field['english']+' changed')]:
  g.input_title=title;g.input_page=page;g.input_text=text;read_book();assert shown.text is None,(field['book_title'],field['page'],title,page);negative+=1
 for text in [field['thai'],addon.books[field['book_title']].title]:
  for run in re.findall(r'[\u0e00-\u0e7f]+',text):assert addon.runs[run] is not None,run
# Secret/type/mode gates use a valid body but may not leave the old page visible.
sample=batch['fields'][0];g.input_title=sample['book_title'];g.input_page=sample['page'];g.input_text=sample['english']
for key,value in [('input_title',g.SECRET),('input_page',g.SECRET),('input_text',g.SECRET),('input_title',123),('input_page','1')]:
 old=g[key];g[key]=value;read_book();assert shown.text is None;g[key]=old;negative+=1
old=g.ItemTextGetItem;g.ItemTextGetItem=None;read_book();assert shown.text is None;g.ItemTextGetItem=old;negative+=1
enabled(False);read_book();assert shown.text is None;enabled(True);negative+=1
alias_positive=alias_negative=0
for field in batch['historical_label_aliases']:
 entry=addon.quests[field['quest_id']].steps[field['step_index']]
 assert addon.Translate(entry,field['english'])==field['thai'];alias_positive+=1
 assert addon.Translate(entry,field['corrected_existing_english'])==field['corrected_existing_thai'];alias_positive+=1
 assert addon.Translate(entry,field['english']+' changed') is None;alias_negative+=1
 if field['quest_id']==92679:
  assert 'ไม่บังคับ' in field['thai']
  assert addon.Translate(entry,field['corrected_existing_english']+' (Required)') is None;alias_negative+=1
 for run in re.findall(r'[\u0e00-\u0e7f]+',field['thai']):assert addon.runs[run] is not None,run
result=dict(status='passed',new_book_page_cases=len(batch['fields']),book_positive_executions=positive,book_negative_executions=negative,source_file_sha256=batch['source_file_sha256'],read_book_handler_sha256=hashlib.sha256(handler.encode()).hexdigest(),historical_alias_cases=len(batch['historical_label_aliases']),alias_positive_executions=alias_positive,alias_negative_executions=alias_negative,whole_book_total_proven=False,scope='Real existing Events.readBook function in mocked UI; exact source title/page/fullbody. No game interaction, optional-flag inference, global suffix stripping, new identity binding or complete-book assertion.')
(ROOT/'evidence/book-regression07.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
