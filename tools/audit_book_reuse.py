"""Compare full book bodies against every prior title/page/variant, not names alone."""
import pathlib,json,hashlib,subprocess
from lupa.lua51 import LuaRuntime,lua_type
ROOT=pathlib.Path(__file__).resolve().parents[1];proof=json.loads((ROOT/'evidence/npc-cloud-replay05.json').read_text());tree=proof['runtime_git_tree'];batch=json.loads((ROOT/'evidence/books-labels-07.json').read_text());l=LuaRuntime(unpack_returned_tuples=True);a=l.table();load=l.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for name in ['Catalog.lua','Match.lua']:
 data=subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+name]);expected=json.loads((ROOT/'evidence/private-package-manifest05.json').read_text())['runtime_manifest']['ForeverThai/'+name];assert hashlib.sha256(data).hexdigest()==expected;load(data.decode(),a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
rows=[];bindings=[(title,page,entry) for title,book in a.books.items() for page,entry in book.items() if isinstance(page,(int,float)) and lua_type(entry)=='table']
for field in batch['fields']:
 matches=[]
 for title,page,entry in bindings:
  thai=a.Translate(entry,field['english'])
  if thai is not None:matches.append(dict(title=title,page=page,thai=thai))
 rows.append(dict(title=field['book_title'],page=field['page'],english_sha256=field['english_sha256'],prior_full_body_matches=matches))
report=dict(prior_runtime_tree=tree,prior_catalog_sha256=json.loads((ROOT/'evidence/private-package-manifest05.json').read_text())['runtime_manifest']['ForeverThai/Catalog.lua'],prior_title_bindings=sum(1 for _ in a.books.items()),prior_numeric_page_bindings=len(bindings),comparison='Real prior Translate, including signature lists/variants/amount forms, tested against each full incoming English body for every existing title alias and page.',matched_bodies=sum(bool(v['prior_full_body_matches']) for v in rows),unmatched_bodies=sum(not v['prior_full_body_matches'] for v in rows),records=rows)
(ROOT/'evidence/book-reuse-audit07.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
