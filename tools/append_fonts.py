"""Append only missing Thai runs. Never rewrite existing glyphs, runs or pages."""
import json,pathlib,re,sys
from lupa.lua51 import LuaRuntime
from PIL import Image
from font_shapes import initialize,thai_words,render
root=pathlib.Path(__file__).resolve().parents[1];runtime=root/'src/ForeverThai';lua=LuaRuntime();addon=lua.table();lua.eval('function(s,a) assert(loadstring(s))("ForeverThai",a) end')((runtime/'Atlas.lua').read_text(),addon)
report=json.loads((root/(sys.argv[1] if len(sys.argv)>1 else 'evidence/main-objectives-01.json')).read_text());runs=sorted({s for f in report['fields'] for s in re.findall(r'[\u0e00-\u0e7f]+',f['thai']) if addon.runs[s] is None});chunks={s:thai_words(s) for s in runs};words=sorted({w for ws in chunks.values() for w in ws});initialize(runtime/'Fonts/Sarabun-Regular.ttf')
page=max(v[1] for _,v in addon.glyphs.items());start_page=page;index={};rows=[];im=Image.new('L',(1024,1024));x=y=2

def save():
 rgba=Image.new('RGBA',im.size,'white');rgba.putalpha(im);p=runtime/f'Fonts/Thai{page}.tga';assert not p.exists();rgba.save(p)
if words:page+=1
for word in words:
 shape,left,advance=render(word);assert 0<shape.width<=1020 and advance>0
 if x+shape.width+2>=1024:x,y=2,y+60
 if y+shape.height+2>=1024:
  save();page+=1;im=Image.new('L',(1024,1024));x=y=2
 im.paste(shape,(x,y));index[word]=len(addon.glyphs)+len(rows)+1;rows.append(f'addon.glyphs[{index[word]}] = {{ {page}, {x}, {y}, {shape.width}, {left}, {advance} }}');x+=shape.width+4
if words:save()
if not words:
 print('No missing Thai runs; no files changed');sys.exit(0)
lines=['\n-- Append-only Cloud batch; original atlas entries retained.']+rows
for run,ws in chunks.items():
 assert ''.join(ws)==run
 lines.append('addon.runs['+json.dumps(run,ensure_ascii=False)+'] = { '+', '.join(str(index[w]) for w in ws)+' }')
with (runtime/'Atlas.lua').open('ab') as f:f.write(('\n'.join(lines)+'\n').encode())
print('Added',len(runs),'runs,',len(words),'glyphs,',page-start_page,'pages; see cloud-regression.json for cumulative totals')
