"""MAIN35 bounded combined private0.472:4literal objectives,only3wordbitmaps,existing engines/assets preserved."""
import pathlib,sys,json,re,zipfile,hashlib,io,time,collections
R=pathlib.Path(__file__).resolve().parent;S=R.parent;PREV=S/'package-main25-26';O=R/'build-0.472.0'
if O.exists():assert not any(O.iterdir()),'Refuse to overwrite prior build'
else:O.mkdir(parents=True)
sys.path[:0]=[str(PREV/'font-deps'),str(PREV)]
from lupa.lua51 import LuaRuntime
from PIL import Image,ImageDraw
from font_shapes_bounded import initialize,render
start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
base=S/'package-main33/build-0.471.0/ForeverThai-0.471.0-main33-PRIVATE-TEST.zip';assert sha(base.read_bytes())=='54eef1b1fb33379332d8bfe5621d166e9bc77f9fe5931cdf510efbfd782b5077'
proposal=json.loads((S/'main35-reviewed-pairs.json').read_text(encoding='utf8'));fields=proposal['fields'];assert len(fields)==4 and {f['quest_id'] for f in fields}=={96075,96087,96088,99217}
quest_patch=(S/'main35-reviewed-overlay.lua').read_bytes();assert sha(quest_patch)=='1501b8e638c8c1245e80bdc915b22763cd56f9dd9fdb84fcd9f6c910be9b1258'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();z=zipfile.ZipFile(base);loaded=[]
order=['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','MainQuest35.lua','Match.lua','Atlas.lua','AtlasMain2526.lua','AtlasMain27.lua','AtlasMain28.lua']
for n in order:l.execute((quest_patch if n=='MainQuest35.lua' else z.read('ForeverThai/'+n)).decode(),'ForeverThai',a);loaded.append(n)
assert len(a.glyphs)==14476
font=z.read('ForeverThai/Fonts/Sarabun-Regular.ttf');assert font==(PREV/'baseline-Sarabun-Regular.ttf').read_bytes();initialize(PREV/'baseline-Sarabun-Regular.ttf')
needs=json.loads((S/'main35-font-run-needs.json').read_text(encoding='utf8'));plans=[];new_words=[]
for row in needs:
 if row['existing_full_run']:assert a.runs[row['run']] is not None;continue
 assert a.runs[row['run']] is None and ''.join(row['words'])==row['run'];pieces=[]
 for word in row['words']:
  run=a.runs[word]
  if run is not None:pieces.append(dict(kind='existing run',text=word,glyphs=[int(run[i]) for i in range(1,len(run)+1)]))
  else:
   pieces.append(dict(kind='new word',text=word))
   if word not in new_words:new_words.append(word)
 plans.append(dict(run=row['run'],pieces=pieces))
assert len(plans)==2 and set(new_words)=={'หุ้มเกราะ','พาหนะ','มหากาพย์'}
page=101;assert f'ForeverThai/Fonts/Thai{page}.tga' not in z.namelist()
mask=Image.new('L',(1024,1024));x=2;y=2;newwordids={};lines=['-- MAIN35 additive bitmap data;exact retained Sarabun shaping and reviewed word boundaries.','local _, addon = ...']
for ix,word in enumerate(new_words,start=14477):
 shape,left,advance=render(word);assert 0<shape.width<=1020 and advance>0 and shape.height==56
 if x+shape.width+2>=1024:x,y=2,y+60
 assert y+58<1024
 mask.paste(shape,(x,y));g=[page,x,y,shape.width,left,advance];newwordids[word]=ix
 assert a.glyphs[ix] is None
 lines += [f'assert(addon.glyphs[{ix}] == nil, "MAIN35 glyph baseline changed")',f'addon.glyphs[{ix}] = {{ '+', '.join(str(v) for v in g)+' }'];x+=shape.width+4
im=Image.new('RGBA',mask.size,'white');im.putalpha(mask);buf=io.BytesIO();im.save(buf,format='TGA');pagebytes=buf.getvalue();assert len(pagebytes)==4194348
provenance=[]
for row in plans:
 ids=[]
 for piece in row['pieces']:
  if piece['kind']=='existing run':
   r=a.runs[piece['text']];assert [int(r[i]) for i in range(1,len(r)+1)]==piece['glyphs'];ids.extend(piece['glyphs'])
  else:ids.append(newwordids[piece['text']])
 lines += ['assert(addon.runs['+json.dumps(row['run'],ensure_ascii=False)+'] == nil, "MAIN35 run baseline changed")','addon.runs['+json.dumps(row['run'],ensure_ascii=False)+'] = { '+', '.join(str(v) for v in ids)+' }'];provenance.append(dict(row,glyphs=ids))
atlas_patch=('\n'.join(lines)+'\n').encode();l.execute(atlas_patch.decode(),'ForeverThai',a);loaded.append('AtlasMain35.lua');l.execute(z.read('ForeverThai/Bitmap.lua').decode(),'ForeverThai',a);loaded.append('Bitmap.lua')
assert all(a.runs[s] is not None for f in fields for s in re.findall(r'[\u0e00-\u0e7f]+',f['thai']))
toc0=z.read('ForeverThai/ForeverThai.toc').decode();assert '## Version: 0.471.0' in toc0 and 'MainQuest35.lua' not in toc0
toc=toc0.replace('## Version: 0.471.0','## Version: 0.472.0').replace('MainQuest33.lua\n','MainQuest33.lua\nMainQuest35.lua\n').replace('AtlasMain28.lua\n','AtlasMain28.lua\nAtlasMain35.lua\n')
assert next(x for x in toc.splitlines() if x.startswith('## SavedVariables:'))==next(x for x in toc0.splitlines() if x.startswith('## SavedVariables:'))
sources=z.read('ForeverThai/SOURCES-TH.txt')+b'\nMAIN35: four new reviewed literal objective fields,existing quests96075/96087/96088/99217,L60;not four complete quests. Full own-ID objectivesText from EG ea970da071079b32e56f349e09648ff0e314b351,data/wowf/1.60.1.70938/quests.enUS.json,blob138d862da0402cee616647b0f7de1d5aa885c8c6. Data from Efficient Games https://efficient.games CC BY4.0;Thai translations added. Headerbuild does not prove per-row current enabled inventory. No player/quantity/condition role guessed. All old data/engines/settings/SavedVariables/70938fix and Skill/Talent/Profession/Item/fonts retained. Only3new Thai wordbitmaps/2newruns. No Windows/MacM2 in-game acceptance or customer Launcher publication for this private package. Old8315/84213multilineTracker limits remain.\n'
changed={'ForeverThai/ForeverThai.toc':toc.encode(),'ForeverThai/SOURCES-TH.txt':sources}
added={'ForeverThai/MainQuest35.lua':quest_patch,'ForeverThai/AtlasMain35.lua':atlas_patch,'ForeverThai/Fonts/Thai101.tga':pagebytes}
outzip=O/'ForeverThai-0.472.0-main35-PRIVATE-TEST.zip';manifest={};preserved=[]
with zipfile.ZipFile(outzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as out:
 for n in z.namelist():
  assert '..' not in pathlib.PurePosixPath(n).parts and not pathlib.PurePosixPath(n).is_absolute()
  b=changed.get(n)
  if b is None:b=z.read(n);preserved.append(n)
  out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
 for n,b in added.items():out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
with zipfile.ZipFile(outzip) as check:
 assert len(check.namelist())==len(set(check.namelist()))==158 and len(preserved)==153
 for n,m in manifest.items():
  b=check.read(n);assert len(b)==m['bytes'] and sha(b)==m['sha256']
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];oldfonts=[n for n in z.namelist() if '/Fonts/' in n]
 assert len(protected)==28 and len(oldfonts)==115
 assert all(n in preserved and check.read(n)==z.read(n) for n in protected+oldfonts)
 for n in ['Catalog.lua','Atlas.lua','Match.lua','Bitmap.lua','Tracker.lua','Events.lua','Panel.lua','Speech.lua','Observe.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','AtlasMain2526.lua','AtlasMain27.lua','AtlasMain28.lua']:assert 'ForeverThai/'+n in preserved
 files=[s.replace('\\','/') for s in toc.splitlines() if s and not s.startswith('#')];assert len(files)==len(set(files))==33
 syntax=l.eval('function(s)local f,e=loadstring(s);return f~=nil,e end')
 for n in files:
  assert 'ForeverThai/'+n in manifest;ok,err=syntax(check.read('ForeverThai/'+n).decode());assert ok,(n,err)
 l.execute((S/'package-main27/bitmap_fixture.lua').read_text(encoding='utf8'));l.execute('UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
 draws=0;coords=set();preview=[]
 for name,cl,cid,race in [('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('MageReader','Mage','MAGE','Human'),('PriestReader','Priest','PRIEST','Windshaper Skyborne')]:
  g=l.globals();g.sampleName=name;g.sampleClass=cl;g.sampleClassID=cid;g.sampleRace=race
  for f in fields:
   actual=a.Translate(a.quests[f['quest_id']].objective,f['english']);assert actual==f['thai'];before=len(g.created);layer,draw=a.BitmapLayer(g.UIParent,'TOPLEFT',0,0,484,18);height=draw(actual,1,1,1);assert height>0 and layer.visible
   objects=[g.created[i] for i in range(before+1,len(g.created)+1)];assert any(o.kind=='texture' and o.visible for o in objects);assert all(not re.search(r'[\u0e00-\u0e7f]',o.text or '') for o in objects if o.kind=='label' and o.visible),'Thai live-font fallback'
   for o in objects:
    if o.kind=='texture' and o.visible:
     pg=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;gx,gy,xe,ye=[round(uv[i]*1024) for i in [1,3,2,4]];coords.add((pg,gx,gy,xe-gx,ye-gy))
   if name=='CloudTester':preview.append((f,height,objects))
   draws+=1
 crops={};bypage=collections.defaultdict(list)
 for key in coords:bypage[key[0]].append(key)
 for pg,keys in bypage.items():
  raw=pagebytes if pg==101 else check.read(f'ForeverThai/Fonts/Thai{pg}.tga');img=Image.open(io.BytesIO(raw));img.load();assert img.mode=='RGBA' and img.size==(1024,1024)
  for key in keys:
   _,gx,gy,w,h=key;assert min(gx,gy)>=0 and gx+w<=1024 and gy+h<=1024;crop=img.crop((gx,gy,gx+w,gy+h));assert crop.getchannel('A').getbbox();crops[key]=crop
 canvas=Image.new('RGB',(760,int(sum(h for _,h,_ in preview)+len(preview)*65)+30),(22,28,35));d=ImageDraw.Draw(canvas);top=15
 for f,height,objects in preview:
  d.text((20,top),f"Quest {f['quest_id']} / objective - actual BitmapLayer simulation, NOT in-game",fill=(240,195,80));top+=30
  for o in objects:
   if not o.visible:continue
   if o.kind=='texture':
    pg=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;gx,gy,xe,ye=[round(uv[i]*1024) for i in [1,3,2,4]];img=crops[(pg,gx,gy,xe-gx,ye-gy)].resize((max(1,round(o.width)),max(1,round(o.height))),Image.Resampling.LANCZOS);pt=o.point;canvas.paste(img,(20+round(pt[4]),top-round(pt[5])),img)
   elif o.kind=='label':pt=o.point;d.text((20+round(pt[4]),top-round(pt[5])-9),o.text or '',fill='white')
  top+=int(height)+35
 canvas.save(O/'MAIN35-bitmap-simulation.png')
z.close()
receipt=dict(status='PASSED_BOUNDED_COMBINED_PRIVATE0472_PACKAGE',version='0.472.0',new_supported_fields=4,new_Thai_fields=4,quest_ids=4,complete_quests_claimed=0,source_proposal_sha256=sha((S/'main35-reviewed-pairs.json').read_bytes()),zip=dict(path=outzip.name,bytes=outzip.stat().st_size,sha256=sha(outzip.read_bytes())),runtime_files=158,old_runtime_files_exact_bytes_preserved=153,metadata_changed=list(changed),added_runtime=list(added),protected_Skill_font_assets_preserved=28,old_font_assets_preserved=115,new_word_glyphs=3,new_Thai_runs=2,new_pages=1,actual_data_order=loaded,all_TOC_Lua_compile=33,actual_BitmapLayer_Thai_draws=draws,Thai_live_font_fallbacks=0,glyph_crops_pixel_checked=len(crops),source_checks_reference='MAIN35:32positives96negatives32wrongroutes,not rerun here',engines_or_settings_changed=False,real_Windows_MacM2_acceptance=False,launcher_published=False,old_UI_Skill_NPC_full_suites_rerun=False,localAI_NLP_or_full_font_rebuild=False,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limits=['4newobjective fields,not4completequests or whole-game percentage','Current enabled inventory/per-row build unproven','8315/84213existing multilineTracker guard retained','No real Windows/MacM2 acceptance'])
for n,v in [('receipt.json',receipt),('manifest.json',manifest),('font-plan.json',dict(new_words=new_words,plans=provenance))]:(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for n,b in changed.items()|added.items():
 p=O/'runtime-delta'/pathlib.PurePosixPath(n).relative_to('ForeverThai');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
print(json.dumps(receipt,indent=2))
