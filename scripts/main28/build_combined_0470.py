"""MAIN28 bounded combined package. No local AI/NLP, full font rebuild or old functional suites."""
import pathlib,sys,json,re,zipfile,hashlib,io,time,collections
R=pathlib.Path(__file__).resolve().parent;S=R.parent;PREV=S/'package-main25-26';O=R/'build-0.470.0'
if O.exists():assert not any(O.iterdir()),'Refuse to overwrite a prior build'
else:O.mkdir()
sys.path[:0]=[str(PREV/'font-deps'),str(PREV)]
from lupa.lua51 import LuaRuntime
from PIL import Image,ImageDraw
from font_shapes_bounded import initialize,render
start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
base=S/'package-main27/build-0.469.0/ForeverThai-0.469.0-main27-PRIVATE-TEST.zip';assert sha(base.read_bytes())=='4fb985134c382d87744214a4ab290e5d3a3caf81a2cc0e47eaa17559dbd90021'
proposal=json.loads((S/'main28-reviewed-pairs.json').read_text(encoding='utf-8'));fields=proposal['fields'];plan=json.loads((R/'font-plan.json').read_text(encoding='utf-8'));assert len(fields)==17 and len(plan['new_words'])==79
quest_patch=(S/'main28-reviewed-overlay.lua').read_bytes();assert sha(quest_patch)=='6de314c7424a19a26fc892aacc4cef9b71803806f066f5d7d3c4df194d48435d'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();z=zipfile.ZipFile(base)
loaded=[]
for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','Match.lua','Atlas.lua','AtlasMain2526.lua','AtlasMain27.lua']:
 b=quest_patch if n=='MainQuest28.lua' else z.read('ForeverThai/'+n);l.execute(b.decode(),'ForeverThai',a);loaded.append(n)
assert len(a.glyphs)==14397 and sum(1 for _ in a.runs.items())==102986
font=z.read('ForeverThai/Fonts/Sarabun-Regular.ttf');assert font==(PREV/'baseline-Sarabun-Regular.ttf').read_bytes();initialize(PREV/'baseline-Sarabun-Regular.ttf')
page=100;mask=Image.new('L',(1024,1024));x=y=2;newwordids={};glyphrows={};pages={};lines=['-- MAIN28 additive bitmap data; reviewed manual word boundaries.','local _, addon = ...']
def savepage():
 im=Image.new('RGBA',mask.size,'white');im.putalpha(mask);buf=io.BytesIO();im.save(buf,format='TGA');pages[page]=buf.getvalue();assert len(pages[page])==4194348
for ix,word in enumerate(plan['new_words'],start=14398):
 shape,left,advance=render(word);assert 0<shape.width<=1020 and advance>0 and shape.height==56
 if x+shape.width+2>=1024:x,y=2,y+60
 if y+shape.height+2>=1024:
  savepage();page+=1;assert page<=101,'More than two additive pages requires review';mask=Image.new('L',(1024,1024));x=y=2
 mask.paste(shape,(x,y));g=[page,x,y,shape.width,left,advance];glyphrows[ix]=g;newwordids[word]=ix
 lines += [f'assert(addon.glyphs[{ix}] == nil, "MAIN28 glyph baseline changed")',f'addon.glyphs[{ix}] = {{ '+', '.join(str(v) for v in g)+' }'];x+=shape.width+4
savepage();provenance=[]
for row in plan['plans']:
 run=row['run'];assert a.runs[run] is None;ids=[]
 for p in row['pieces']:
  if p['kind']=='existing run':
   actual=a.runs[p['text']];assert [int(actual[i]) for i in range(1,len(actual)+1)]==p['glyphs'];ids.extend(p['glyphs'])
  else:ids.append(newwordids[p['text']])
 lines += ['assert(addon.runs['+json.dumps(run,ensure_ascii=False)+'] == nil, "MAIN28 run baseline changed")','addon.runs['+json.dumps(run,ensure_ascii=False)+'] = { '+', '.join(str(v) for v in ids)+' }'];provenance.append(dict(row,glyphs=ids))
atlas_patch=('\n'.join(lines)+'\n').encode();l.execute(atlas_patch.decode(),'ForeverThai',a);loaded.append('AtlasMain28.lua');l.execute(z.read('ForeverThai/Bitmap.lua').decode(),'ForeverThai',a);loaded.append('Bitmap.lua')
assert loaded==['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','Match.lua','Atlas.lua','AtlasMain2526.lua','AtlasMain27.lua','AtlasMain28.lua','Bitmap.lua']
toc0=z.read('ForeverThai/ForeverThai.toc').decode();assert '## Version: 0.469.0' in toc0 and 'MainQuest28.lua' not in toc0
toc=toc0.replace('## Version: 0.469.0','## Version: 0.470.0').replace('MainQuest27.lua\n','MainQuest27.lua\nMainQuest28.lua\n').replace('AtlasMain27.lua\n','AtlasMain27.lua\nAtlasMain28.lua\n')
assert next(x for x in toc0.splitlines() if x.startswith('## SavedVariables:'))==next(x for x in toc.splitlines() if x.startswith('## SavedVariables:'))
sources=z.read('ForeverThai/SOURCES-TH.txt')+b'\nMAIN28: 17 newly supported literal conditional-description variants/13existing quest fields/13IDs =8 new reviewed Thai variants+9 reviewed verbatim reuse; not17 complete quests.\nEnglish: https://github.com/JIVESCORP/eg-link-output-wowf/blob/ea970da071079b32e56f349e09648ff0e314b351/data/wowf/1.60.1.70938/quests.enUS.json ; conditionalDescriptions full own-ID source, no condition/creature eligibility guessed.\n98391uppercaseG and91754basepipe5grammar remain held independently of translated literal conditions. Existing8315/84213multi-line objective Tracker English guards retained. Real Windows/Mac M2 and whole-game completion not verified.\n'
changed={'ForeverThai/ForeverThai.toc':toc.encode(),'ForeverThai/SOURCES-TH.txt':sources};added={'ForeverThai/MainQuest28.lua':quest_patch,'ForeverThai/AtlasMain28.lua':atlas_patch}|{f'ForeverThai/Fonts/Thai{pg}.tga':b for pg,b in pages.items()}
outzip=O/'ForeverThai-0.470.0-main28-COMBINED.zip';manifest={};preserved=[]
with zipfile.ZipFile(outzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as dest:
 for info in z.infolist():
  n=info.filename;assert not info.is_dir() and '..' not in pathlib.PurePosixPath(n).parts and not pathlib.PurePosixPath(n).is_absolute();b=changed.get(n)
  if b is None:b=z.read(n);preserved.append(n)
  dest.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
 for n,b in added.items():dest.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
with zipfile.ZipFile(outzip) as check:
 assert len(check.infolist())==len(set(check.namelist()))==151+len(added)
 for n,m in manifest.items():
  b=check.read(n);assert len(b)==m['bytes'] and sha(b)==m['sha256']
 for n in preserved:assert manifest[n]['sha256']==sha(z.read(n))
 files=[s.replace('\\','/') for s in toc.splitlines() if s and not s.startswith('#')];assert len(files)==len(set(files))==30
 compilecheck=l.eval('function(s) local f,e=loadstring(s);return f~=nil,e end')
 for n in files:
  assert 'ForeverThai/'+n in manifest;ok,error=compilecheck(check.read('ForeverThai/'+n).decode());assert ok,(n,error)
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];oldfonts=[n for n in z.namelist() if '/Fonts/' in n]
 assert len(protected)==28 and len(oldfonts)==114 and all(n in preserved for n in protected+oldfonts)
 for n in ['Catalog.lua','Atlas.lua','MainQuest2526.lua','AtlasMain2526.lua','Match.lua','Bitmap.lua','Observe.lua','Panel.lua','Speech.lua','Tracker.lua','Events.lua']:assert 'ForeverThai/'+n in preserved
 l.execute((R/'bitmap_fixture.lua').read_text(encoding='utf-8'));l.execute('testName="CloudTester";testClass="Druid";testClassID="DRUID";testRace="Night Elf";UnitName=function()return testName end;UnitClass=function()return testClass,testClassID end;UnitRace=function()return testRace end')
 profiles=[('CloudTester','Druid','DRUID','Night Elf','ดรูอิด','ไนต์เอลฟ์'),('NewHunter','Hunter','HUNTER','Night Elf','พราน','ไนต์เอลฟ์'),('Arielle','Mage','MAGE','Human','จอมเวท','มนุษย์'),('Skywarden','Shaman','SHAMAN','High Order Skyborne','ชาแมน','สกายบอร์นฝ่ายไฮออร์เดอร์')]
 positive=draws=0;previewrows=[];glyphcoords=set()
 for pi,(name,cl,cid,race,thcl,thrace) in enumerate(profiles):
  g=l.globals();g.testName=name;g.testClass=cl;g.testClassID=cid;g.testRace=race
  for f in fields:
   ui=re.sub(r'\$([nNcCrR])',lambda m:{'n':name,'c':cl,'r':race}[m[1].lower()],re.sub(r'\$[Bb]','\n',f['english']));expected=f['thai'].replace('{name}',name).replace('{class}',thcl).replace('{race}',thrace)
   actual=a.Translate(a.quests[f['quest_id']][f['field']],ui);assert actual==expected;positive+=1
   before=len(g.created);layer,draw=a.BitmapLayer(g.UIParent,'TOPLEFT',0,0,484,18);height=draw(actual,1,1,1);assert height>0 and layer.visible
   objects=[g.created[i] for i in range(before+1,len(g.created)+1)]
   assert any(o.kind=='texture' and o.visible for o in objects);assert all(not re.search(r'[\u0e00-\u0e7f]',o.text or '') for o in objects if o.kind=='label' and o.visible),'Thai live-font fallback';draws+=1
   for o in objects:
    if o.kind=='texture' and o.visible:
     pg=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;gx,gy,xend,yend=[round(uv[i]*1024) for i in [1,3,2,4]];glyphcoords.add((pg,gx,gy,xend-gx,yend-gy))
   if pi==0 and f['translation_kind']=='new_reviewed_Thai':previewrows.append((f,height,objects))
 for row in provenance:
  for idx in row['glyphs']:
   gl=a.glyphs[idx];glyphcoords.add((int(gl[1]),int(gl[2]),int(gl[3]),int(gl[4]),int(gl[7] or 56)))
 bypage=collections.defaultdict(list)
 for key in glyphcoords:bypage[key[0]].append(key)
 crops={}
 for pg,keys in bypage.items():
  raw=pages[pg] if pg in pages else z.read(f'ForeverThai/Fonts/Thai{pg}.tga');im=Image.open(io.BytesIO(raw));im.load();assert im.mode=='RGBA' and im.size==(1024,1024)
  for key in keys:
   _,gx,gy,w,h=key;assert min(gx,gy)>=0 and gx+w<=1024 and gy+h<=1024;crop=im.crop((gx,gy,gx+w,gy+h));assert crop.getchannel('A').getbbox() is not None;crops[key]=crop
 canvas=Image.new('RGB',(1060,int(sum(h for _,h,_ in previewrows)+len(previewrows)*65)+30),(22,28,35));d=ImageDraw.Draw(canvas);top=15
 for f,height,objects in previewrows:
  d.text((20,top),f"Quest {f['quest_id']} / {f['field']} - BitmapLayer simulation, NOT in-game",fill=(240,195,80));top+=30
  for o in objects:
   if not o.visible:continue
   if o.kind=='texture':
    pg=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;gx,gy,xend,yend=[round(uv[i]*1024) for i in [1,3,2,4]];im=crops[(pg,gx,gy,xend-gx,yend-gy)];im=im.resize((max(1,round(o.width)),max(1,round(o.height))),Image.Resampling.LANCZOS);pt=o.point;canvas.paste(im,(20+round(pt[4]),top-round(pt[5])),im)
   elif o.kind=='label':pt=o.point;d.text((20+round(pt[4]),top-round(pt[5])-9),o.text or '',fill='white')
  top+=int(height)+35
 canvas.save(O/'MAIN28-bitmap-simulation.png')
z.close()
receipt=dict(status='PASSED_BOUNDED_COMBINED_0470_PACKAGE',version='0.470.0',source_proposal_sha256=sha((S/'main28-reviewed-pairs.json').read_bytes()),new_supported_variants=17,quest_ids=13,existing_description_fields_extended=13,new_Thai_variants=8,verbatim_reviewed_reuse_variants=9,complete_quests_claimed=0,baseline_zip_sha256=sha(base.read_bytes()),zip=dict(path=outzip.name,bytes=outzip.stat().st_size,sha256=sha(outzip.read_bytes())),runtime_files=len(manifest),old_runtime_files_exact_bytes_preserved=len(preserved),metadata_changed=list(changed),new_runtime_files=list(added),protected_Skill_font_assets_preserved=28,old_font_assets_preserved=114,new_Thai_runs=len(plan['plans']),new_word_glyphs=len(newwordids),new_pages=len(pages),actual_changed_data_order=loaded,all_TOC_Lua_files_compile=30,positive_matches=positive,actual_BitmapLayer_Thai_draws=draws,Thai_live_font_fallbacks=0,affected_glyph_crops_pixel_checked=len(crops),matcher_Tracker_engine_changed=False,source_template_checks_reference='evidence/main28-variant-checks.json;68positive,680template/136route negatives; not rerun here',real_game_verified=False,launcher_published=False,whole_game_inventory_or_percent=False,old_UI_Skill_NPC_full_suites_rerun=False,local_AI_NLP_or_full_font_rebuild=False,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limitations=['Windows/Mac M2 in-game acceptance absent','8315new typed objective alias retains old multi-line Thai; unchanged Tracker newline English guard expected','98391uppercaseG/91754basepipe5/95318basepipe5grammarheld','Source/query/class fixtures are not an enabled whole-game inventory'])
for name,data in [('manifest.json',manifest),('receipt.json',receipt),('run-provenance.json',provenance)]:
 (O/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for n,b in changed.items()|added.items():
 p=O/'runtime-delta'/pathlib.PurePosixPath(n).relative_to('ForeverThai');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
print(json.dumps(receipt,ensure_ascii=False,indent=2))
