"""Lossless atlas consolidation for actual customer0.5 512MiB extraction limit; no shaping or local AI."""
import pathlib,json,zipfile,hashlib,io,time,re,collections,math,sys
from lupa.lua51 import LuaRuntime,lua_type
from PIL import Image,ImageDraw
R=pathlib.Path(__file__).resolve().parent;S=R.parent;I=R/'build-0.480.0';O=R/'build-0.480.0-compact'
assert not O.exists() or not any(O.iterdir());O.mkdir(exist_ok=True);sys.stdout.reconfigure(encoding='utf8');t=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
z=zipfile.ZipFile(I/'ForeverThai-0.480.0-main44-COMBINED.zip');assert sha(pathlib.Path(z.filename).read_bytes())=='6f2bc563da3e78e3a52abd7645c95e7a5bc9546a6be88400b9cda28a401f400f'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();toc=z.read('ForeverThai/ForeverThai.toc').decode();tocfiles=[s.replace('\\','/') for s in toc.splitlines() if s.strip() and not s.startswith('#')]
loaded=[]
for n in tocfiles:
 if n=='Catalog.lua' or n.startswith('MainQuest') or n=='Match.lua' or n=='Atlas.lua' or n.startswith('AtlasMain'):
  l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a);loaded.append(n)
glyphs={int(i):[g[j] for j in range(1,7)] for i,g in a.glyphs.items()};assert len(glyphs)==15994
old={i:g for i,g in glyphs.items() if i<=15331};area=collections.Counter();bottom=collections.defaultdict(int)
for g in old.values():p,x,y,w,left,adv=map(int,g);area[p]+=w*56;bottom[p]=max(bottom[p],y+56)
ordered=sorted(area,key=lambda p:(area[p],p));retire=set(ordered[:12]);dest=ordered[12:24];images={};modified={};empty=Image.new('RGBA',(1,1),(255,255,255,0));buf=io.BytesIO();empty.save(buf,format='TGA');emptybytes=buf.getvalue();assert len(emptybytes)==48
def originalpage(p):
 if p not in images:
  im=Image.open(io.BytesIO(z.read(f'ForeverThai/Fonts/Thai{p}.tga')));im.load();assert im.mode=='RGBA' and im.size==(1024,1024);images[p]=im
 return images[p]
def cropof(g):p,x,y,w,left,adv=map(int,g);return originalpage(p).crop((x,y,x+w,y+56))
positions={p:[2,math.ceil((bottom[p]+2)/60)*60+2] for p in dest};relocations=[];move=[i for i,g in glyphs.items() if int(g[0]) in retire or i>15331];move.sort(key=lambda i:(-int(glyphs[i][3]),i))
for i in move:
 oldg=glyphs[i];w=int(oldg[3]);found=None
 for p in dest:
  x,y=positions[p]
  if x+w+2>=1024:x,y=2,y+60
  if y+58>=1024:continue
  found=(p,x,y);positions[p]=[x+w+4,y];break
 assert found is not None,('not enough existing transparent atlas tails',i,w)
 p,x,y=found
 if p not in modified:modified[p]=originalpage(p).copy()
 target=modified[p].crop((x,y,x+w,y+56));assert target.getchannel('A').getbbox() is None
 pix=cropof(oldg);assert pix.getchannel('A').getbbox();modified[p].paste(pix,(x,y));newg=[p,x,y,oldg[3],oldg[4],oldg[5]];relocations.append(dict(glyph=i,old=oldg,new=newg,pixel_sha256=sha(pix.tobytes())))
lines=['-- MAIN44 lossless texture consolidation: actual Launcher0.5 caps expanded ZIP at512MiB.','-- All glyph dimensions,advance,bearing,run sequences and RGBA pixels preserved.','-- No typography rerender;only relocation into previously transparent texture tails.']
for row in relocations:
 i=row['glyph'];og=row['old'];ng=row['new'];lines.extend([f'assert(addon.glyphs[{i}] and '+ ' and '.join(f'addon.glyphs[{i}][{j+1}] == {v}' for j,v in enumerate(og))+', "MAIN44 relocation baseline changed")',f'addon.glyphs[{i}] = {{ '+', '.join(str(v) for v in ng)+' }'])
reloclua=('\n'.join(lines)+'\n').encode();atlas0=z.read('ForeverThai/AtlasMain44.lua');atlas=atlas0+b'\n'+reloclua;l.execute(atlas.decode().split('\n',2)[0] if False else ('local _, addon = ...\n'+reloclua.decode()),'ForeverThai',a)
pagebytes={}
for p,im in modified.items():b=io.BytesIO();im.save(b,format='TGA');pagebytes[f'ForeverThai/Fonts/Thai{p}.tga']=b.getvalue()
for p in retire:pagebytes[f'ForeverThai/Fonts/Thai{p}.tga']=emptybytes
removed={f'ForeverThai/Fonts/Thai{p}.tga' for p in range(111,115)};changed={'ForeverThai/AtlasMain44.lua':atlas,**pagebytes};changed['ForeverThai/SOURCES-TH.txt']=z.read('ForeverThai/SOURCES-TH.txt')+b'\nMAIN44CUSTOMER05SIZEFIX: initial uncompressed atlas candidate exceeded original Launcher0.5 512MiB safety limit and WAS NOT PUBLISHED. Losslessly relocate glyph rectangles from12sparse questfont pages and4newpages into transparent tails of existing questfont pages; retain12retirednames asunused1x1transparentTGAs,omit4unpublishednewpagefiles. No oldglyph pixels/bearings/advances/runsequences or Skill/Talent/Profession/Item assets changed. All15994 glyph RGBA crops checked including15331old;744newdraws and22PNG bytes mustmatch initial inspected previews. No localAI/no fullfontshaping.\n'
outzip=O/'ForeverThai-0.480.0-main44-COMBINED.zip';manifest={}
with zipfile.ZipFile(outzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as out:
 for n in z.namelist():
  if n in removed:continue
  b=changed.get(n,z.read(n));out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
with zipfile.ZipFile(outzip) as check:
 assert len(check.namelist())==183 and sum(v.file_size for v in check.infolist())<512*1024*1024
 for n,v in manifest.items():assert sha(check.read(n))==v['sha256']
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28 and all(check.read(n)==z.read(n) for n in protected)
 currentpages={}
 for i,og in glyphs.items():
  ng=[a.glyphs[i][j] for j in range(1,7)];assert ng[3:]==og[3:]
  p,x,y,w,left,adv=map(int,ng);assert p not in retire and p<=110
  if p not in currentpages:im=Image.open(io.BytesIO(check.read(f'ForeverThai/Fonts/Thai{p}.tga')));im.load();assert im.size==(1024,1024);currentpages[p]=im
  assert currentpages[p].crop((x,y,x+w,y+56)).tobytes()==cropof(og).tobytes(),('glyph pixels changed',i)
  if i not in move:assert ng==og
 syntax=l.eval('function(s)local f,e=loadstring(s);return f~=nil,e end')
 for n in tocfiles:ok,e=syntax(check.read('ForeverThai/'+n).decode());assert ok,(n,e)
 # Re-execute exactly the consolidated runtime atlas from actual package,not an in-memory substitute.
 l2=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l2.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a2=l2.table()
 for n in loaded:l2.execute(check.read('ForeverThai/'+n).decode(),'ForeverThai',a2)
 assert len(a2.glyphs)==len(a.glyphs) and len(a2.runs)==len(a.runs)
 for run,ids in a.runs.items():assert [a2.runs[run][j] for j in range(1,len(ids)+1)]==[ids[j] for j in range(1,len(ids)+1)]
 l=l2;a=a2;l.execute(check.read('ForeverThai/Bitmap.lua').decode(),'ForeverThai',a);l.execute((S/'package-main27/bitmap_fixture.lua').read_text(encoding='utf8'));l.execute('UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
 fields=json.loads((S/'main44-reviewed-pairs.json').read_text(encoding='utf8'))['fields'];draws=0;coords=set();previews=collections.defaultdict(list);questorder=list(dict.fromkeys(r['quest_id'] for r in fields))
 for name,cl,cid,race in [('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('MageReader','Mage','MAGE','Human'),('PriestReader','Priest','PRIEST','Windshaper Skyborne')]:
  g=l.globals();g.sampleName=name;g.sampleClass=cl;g.sampleClassID=cid;g.sampleRace=race
  for r in fields:
   actual=a.Translate(a.quests[r['quest_id']][r['field']],re.sub(r'\$[Bb]','\n',r['english']));assert actual==r['thai'];before=len(g.created);layer,draw=a.BitmapLayer(g.UIParent,'TOPLEFT',0,0,484,18);height=draw(actual,1,1,1);assert height>0 and layer.visible;objects=[g.created[i] for i in range(before+1,len(g.created)+1)];assert any(o.kind=='texture' and o.visible for o in objects);assert all(not re.search(r'[\u0e00-\u0e7f]',o.text or '') for o in objects if o.kind=='label' and o.visible)
   for o in objects:
    if o.kind=='texture' and o.visible:page=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;gx,gy,xe,ye=[round(uv[i]*1024) for i in [1,3,2,4]];coords.add((page,gx,gy,xe-gx,ye-gy))
   if name=='CloudTester':previews[questorder.index(r['quest_id'])//6+1].append((r,height,objects))
   draws+=1
 crops={}
 for key in coords:
  page,gx,gy,w,h=key;img=currentpages[page];crop=img.crop((gx,gy,gx+w,gy+h));assert crop.getchannel('A').getbbox();crops[key]=crop
 previewfiles=[]
 for page,preview in previews.items():
  canvas=Image.new('RGB',(760,int(sum(h for _,h,_ in preview)+len(preview)*65)+30),(22,28,35));d=ImageDraw.Draw(canvas);top=15
  for r,height,objects in preview:
   d.text((20,top),f"Quest {r['quest_id']} / {r['field']} - actual BitmapLayer, NOT in-game",fill=(240,195,80));top+=30
   for o in objects:
    if not o.visible:continue
    if o.kind=='texture':
     pg=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;gx,gy,xe,ye=[round(uv[i]*1024) for i in [1,3,2,4]];im=crops[(pg,gx,gy,xe-gx,ye-gy)].resize((max(1,round(o.width)),max(1,round(o.height))),Image.Resampling.LANCZOS);pt=o.point;canvas.paste(im,(20+round(pt[4]),top-round(pt[5])),im)
    elif o.kind=='label':pt=o.point;d.text((20+round(pt[4]),top-round(pt[5])-9),o.text or '',fill='white')
   top+=int(height)+35
  fn=f'MAIN44-bitmap-simulation-{page:02}.png';canvas.save(O/fn);assert (O/fn).read_bytes()==(I/fn).read_bytes(),('preview pixels changed',fn);previewfiles.append(fn)
receipt=json.loads((I/'receipt.json').read_text());receipt.update(status='PASSED_LOSSLESS_COMPACT_COMBINED0480_PACKAGE',zip=dict(path=outzip.name,bytes=outzip.stat().st_size,sha256=sha(outzip.read_bytes())),runtime_files=183,expanded_bytes=sum(v['bytes'] for v in manifest.values()),launcher05_limit_bytes=512*1024*1024,old_runtime_files_exact_bytes_preserved=sum(n in manifest and sha(z.read(n))==manifest[n]['sha256'] for n in z.namelist()),old_font_assets_exact_preserved=sum(n in manifest and sha(z.read(n))==manifest[n]['sha256'] for n in z.namelist() if '/Fonts/' in n and n not in removed),old_font_assets_preserved='pixel-equivalent, see consolidation; not all old font file bytes unchanged',new_pages=0,retired_unused_quest_pages=sorted(retire),quest_font_destination_pages=sorted(modified),relocated_old_glyphs=sum(row['glyph']<=15331 for row in relocations),relocated_new_glyphs=sum(row['glyph']>15331 for row in relocations),all_old_glyph_pixels_exact=15331,all_glyph_pixels_exact=15994,all_run_sequences_exact=sum(1 for _ in a.runs.items()),actual_BitmapLayer_Thai_draws=draws,glyph_crops_pixel_checked=len(crops),preview_files=previewfiles,all22_preview_files_byte_identical_to_inspected_initial=True,consolidation_wall_seconds=time.perf_counter()-t,consolidation_cpu_seconds=time.process_time()-cpu,launcher_published=False,initial_unpublished_oversize_candidate='6f2bc563da3e78e3a52abd7645c95e7a5bc9546a6be88400b9cda28a401f400f',metadata_changed=['ForeverThai/SOURCES-TH.txt'],added_runtime=['ForeverThai/MainQuest44.lua','ForeverThai/AtlasMain44.lua'])
for n,v in [('receipt.json',receipt),('manifest.json',manifest),('atlas-consolidation.json',dict(retired_pages=sorted(retire),destination_pages=sorted(modified),relocations=relocations,original_old_glyph_pixels_exact=15331,all_glyph_pixels_exact=15994,no_font_shaping=True,no_engine_edits=True))]:(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for n,b in changed.items():p=O/'runtime-delta'/pathlib.PurePosixPath(n).relative_to('ForeverThai');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
for n in ['ForeverThai.toc','MainQuest44.lua']:(O/'runtime-delta'/n).write_bytes(z.read('ForeverThai/'+n))
print(json.dumps(receipt,indent=2))
