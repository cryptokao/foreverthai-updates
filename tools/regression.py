"""Cloud regression against the independently hash-verified 0.462.0 runtime ZIP."""
import hashlib,io,json,pathlib,re,zipfile
from lupa.lua51 import LuaRuntime,lua_type
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai'
BASE=pathlib.Path('/workspace/foreverthai-dev/downloads/ForeverThai-0.462.0-Quest-Skills-PRIVATE-TEST.zip')
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='d36621b9357a33e909777f31fdc5745ddf96aa579add740364ac60011f30cb62'
z=zipfile.ZipFile(BASE);names=[n for n in z.namelist() if not n.endswith('/')];assert len(names)==126
lua=LuaRuntime(unpack_returned_tuples=True);load=lua.eval('function(s,a) local f,e=loadstring(s); assert(f,e); if a then f("ForeverThai",a) end end')
base=lua.table();addon=lua.table()
for n in ['Catalog.lua','Match.lua','SpeechData.lua','Atlas.lua']:
 load(z.read('ForeverThai/'+n).decode(),base);load((RUN/n).read_text(),addon)
lua.execute('UnitName=function() return "CloudTester" end; UnitClass=function() return "Druid", "DRUID" end; UnitRace=function() return "Night Elf" end')
report=json.loads((ROOT/'evidence/main-objectives-01.json').read_text());added={(x['quest_id'],x['field']) for x in report['fields']};assert len(added)==34
# Every original table key/value (including all runtime-only aliases) remains identical.
checks=0
def equal(a,b,path=()):
 global checks
 if lua_type(a)=='table':
  assert lua_type(b)=='table',path
  for k,v in a.items():equal(v,b[k],path+(k,))
  for k,v in b.items():
   if a[k] is None:assert path in [('runs',),('glyphs',)] or (len(path)==2 and path[0]=='quests' and (path[1],k) in added),(path,k)
 else:assert a==b,(path,a,b)
 checks+=1
for k,v in base.items():
 if lua_type(v)!='function':equal(v,addon[k],(k,))
# Only Catalog and append-only Atlas may differ among original runtime files.
for n in names:
 p=ROOT/'src'/n;assert p.is_file(),n
 if n.endswith('/Catalog.lua'):continue
 if n.endswith('/Atlas.lua'):assert p.read_bytes().startswith(z.read(n));continue
 assert p.read_bytes()==z.read(n),n
for p in RUN.rglob('*.lua'):load(p.read_text(),None)
toc=(RUN/'ForeverThai.toc').read_text();paths=[x.strip().replace('\\','/') for x in toc.splitlines() if x.strip() and not x.startswith('#')];assert all((RUN/x).is_file() for x in paths)
assert '## OptionalDeps: Questie' in toc and 'AlphaWoWSkillsDB' in toc
positives=negatives=0
for f in report['fields']:
 q=f['quest_id'];entry=addon.quests[q][f['field']];assert base.quests[q][f['field']] is None
 assert hashlib.sha256(f['english'].encode()).hexdigest()==f['english_sha256']
 assert hashlib.sha256(f['thai'].encode()).hexdigest()==f['thai_sha256']
 for count in ['1','12','1,234','999999']:
  source=f['english'];target=f['thai']
  for token in re.findall(r'\$(\d+)oa',source):source=source.replace('$'+token+'oa',count);target=target.replace('{world'+token+'}',count)
  assert addon.Translate(entry,source)==target,(q,source);positives+=1
  assert addon.Translate(entry,'UNRELATED '+source) is None;negatives+=1
  assert addon.Translate(entry,source+' incorrect') is None;negatives+=1
  assert addon.Translate(entry,source.replace('1,234','1,23')) is None if '1,234' in source else True
 for run in re.findall(r'[\u0e00-\u0e7f]+',f['thai']):
  assert addon.runs[run] is not None,(q,run)
  for _,idx in addon.runs[run].items():
   glyph=addon.glyphs[idx];assert glyph and glyph[4]>0 and glyph[6]>0
# Decode all font pages and ensure every glyph rectangle is within a real atlas.
images={}
for p in (RUN/'Fonts').glob('*.tga'):
 with Image.open(p) as im:im.load();images[p.name]=im.size
for _,g in addon.glyphs.items():
 w,h=images[f'Thai{g[1]}.tga'];assert 0<=g[2] and g[2]+g[4]<=w and 0<=g[3] and g[3]+56<=h
result=dict(baseline_components_retained=126,byte_identical_baseline_files=124,new_objective_fields=len(added),unchanged_data_values_checked=checks,positive_matches=positives,negative_matches=negatives,lua_files_compiled=len(list(RUN.rglob('*.lua'))),toc_paths=len(paths),font_pages_decoded=len(images),old_glyphs=len(base.glyphs),old_runs=sum(1 for _ in base.runs.items()),new_glyphs=len(addon.glyphs)-len(base.glyphs),new_runs=sum(1 for k,_ in addon.runs.items() if base.runs[k] is None),scope='New Cloud technical checks; not historical 686 speech/9 Skills harness and not in-game verification')
(ROOT/'evidence/cloud-regression.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
