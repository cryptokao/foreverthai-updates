"""Combined MAIN33 package:one source-backed progress slot,no font rebuild or old functional-suite rerun."""
import pathlib,json,zipfile,hashlib,time,re,io,collections
from lupa.lua51 import LuaRuntime
from PIL import Image,ImageDraw
R=pathlib.Path(__file__).resolve().parent;S=R.parent;O=R/'build-0.471.0';start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
if O.exists():assert not any(O.iterdir()),'Refuse to overwrite prior build'
else:O.mkdir(parents=True)
base=S/'package-main28/build-0.470.0/ForeverThai-0.470.0-main28-COMBINED.zip';assert sha(base.read_bytes())=='a9c854976d2efac55b4821492714b7cf93dae627fbb77309d6bc820610cfb5e6'
p=json.loads((S/'main33-reviewed-pairs.json').read_text(encoding='utf-8'));assert p['counts']['new_supported_fields']==1;f=p['fields'][0];assert f['quest_id']==97928 and f['field']=='progress' and f['translation_kind']=='verbatim_reviewed_reuse'
overlay=(S/'main33-reviewed-overlay.lua').read_bytes();assert sha(overlay)=='3691a574261943bb9392aeac5c5c99cb5503ac2396b1350939c240e041109d67'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();z=zipfile.ZipFile(base);loaded=[]
order=['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','MainQuest33.lua','Match.lua','Atlas.lua','AtlasMain2526.lua','AtlasMain27.lua','AtlasMain28.lua','Bitmap.lua']
for n in order:l.execute((overlay if n=='MainQuest33.lua' else z.read('ForeverThai/'+n)).decode(),'ForeverThai',a);loaded.append(n)
assert a.quests[97928].progress[2]==a.quests[97927].progress[2]==f['thai'];assert all(a.runs[s] is not None for s in re.findall(r'[\u0e00-\u0e7f]+',f['thai'])),'Missing reuse font run'
toc0=z.read('ForeverThai/ForeverThai.toc').decode();assert '## Version: 0.470.0' in toc0 and 'MainQuest33.lua' not in toc0
toc=toc0.replace('## Version: 0.470.0','## Version: 0.471.0').replace('MainQuest28.lua\n','MainQuest28.lua\nMainQuest33.lua\n')
assert next(x for x in toc.splitlines() if x.startswith('## SavedVariables:'))==next(x for x in toc0.splitlines() if x.startswith('## SavedVariables:'))
sources=z.read('ForeverThai/SOURCES-TH.txt')+b'\nMAIN33: one newly supported quest progress field,97928 Camping101:Blacksmithing,L6. Exact English from https://github.com/quinn-dougherty/forever-vo/issues/3522 line58(progress);export header70938 is not individual-row build proof.\nReviewed full-source Thai reused verbatim from existing97927.progress;0newThai prose,1new supported field,not1completequest. QuestieDB4dbb82440a27856f8dccf57094a5d792cdc7cc9b corroborates own-ID title/level only.\nPrior95772completion variant remains held:third-party race role unproven,canonical untouched. All Quest/Tracker/optionalQuestie/NPC/Skill/Talent/Profession/Item/fonts/settings/70938fix retained. No real Windows/Mac M2 verification or customer publication in this private package.\n'
changed={'ForeverThai/ForeverThai.toc':toc.encode(),'ForeverThai/SOURCES-TH.txt':sources};added={'ForeverThai/MainQuest33.lua':overlay};manifest={};preserved=[];outzip=O/'ForeverThai-0.471.0-main33-PRIVATE-TEST.zip'
with zipfile.ZipFile(outzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as out:
 for n in z.namelist():
  assert not pathlib.PurePosixPath(n).is_absolute() and '..' not in pathlib.PurePosixPath(n).parts
  b=changed.get(n)
  if b is None:b=z.read(n);preserved.append(n)
  out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
 for n,b in added.items():out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
with zipfile.ZipFile(outzip) as check:
 assert len(check.namelist())==len(set(check.namelist()))==155
 for n,m in manifest.items():
  b=check.read(n);assert len(b)==m['bytes'] and sha(b)==m['sha256']
 assert len(preserved)==152
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];fonts=[n for n in z.namelist() if '/Fonts/' in n];assert len(protected)==28 and len(fonts)==115
 assert all(n in preserved and check.read(n)==z.read(n) for n in protected+fonts)
 files=[s.replace('\\','/') for s in toc.splitlines() if s and not s.startswith('#')];assert len(files)==len(set(files))==31
 syntax=l.eval('function(s)local f,e=loadstring(s);return f~=nil,e end')
 for n in files:
  assert 'ForeverThai/'+n in manifest;ok,err=syntax(check.read('ForeverThai/'+n).decode());assert ok,(n,err)
 for n in ['Catalog.lua','Atlas.lua','Match.lua','Tracker.lua','Events.lua','Panel.lua','Speech.lua','Observe.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','AtlasMain2526.lua','AtlasMain27.lua','AtlasMain28.lua']:assert 'ForeverThai/'+n in preserved
 l.execute((S/'package-main27/bitmap_fixture.lua').read_text(encoding='utf-8'));l.execute('UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
 draws=0;preview=[];coords=set()
 for name,cl,cid,race in [('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('MageReader','Mage','MAGE','Human'),('PriestReader','Priest','PRIEST','Windshaper Skyborne')]:
  g=l.globals();g.sampleName=name;g.sampleClass=cl;g.sampleClassID=cid;g.sampleRace=race;actual=a.Translate(a.quests[97928].progress,f['english']);assert actual==f['thai'];before=len(g.created)
  layer,draw=a.BitmapLayer(g.UIParent,'TOPLEFT',0,0,680,20);height=draw(actual,1,1,1);assert layer.visible and height>0
  objects=[g.created[i] for i in range(before+1,len(g.created)+1)];assert any(o.kind=='texture' and o.visible for o in objects)
  assert all(not re.search(r'[\u0e00-\u0e7f]',o.text or '') for o in objects if o.kind=='label' and o.visible),'Thai font fallback'
  for o in objects:
   if o.kind=='texture' and o.visible:
    pg=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;gx,gy,xend,yend=[round(uv[i]*1024) for i in [1,3,2,4]];coords.add((pg,gx,gy,xend-gx,yend-gy))
  if draws==0:preview=objects
  draws+=1
 bypage=collections.defaultdict(list)
 for key in coords:bypage[key[0]].append(key)
 crops={}
 for pg,keys in bypage.items():
  im=Image.open(io.BytesIO(check.read(f'ForeverThai/Fonts/Thai{pg}.tga')));im.load();assert im.mode=='RGBA' and im.size==(1024,1024)
  for key in keys:
   _,x,y,w,h=key;assert min(x,y)>=0 and x+w<=1024 and y+h<=1024;crop=im.crop((x,y,x+w,y+h));assert crop.getchannel('A').getbbox();crops[key]=crop
 canvas=Image.new('RGB',(860,130),(22,28,35));d=ImageDraw.Draw(canvas);d.text((20,12),'Quest97928 / progress - actual BitmapLayer simulation, NOT in-game',fill=(240,195,80));top=55
 for o in preview:
  if not o.visible:continue
  if o.kind=='texture':
   pg=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;x,y,xe,ye=[round(uv[i]*1024) for i in [1,3,2,4]];im=crops[(pg,x,y,xe-x,ye-y)].resize((max(1,round(o.width)),max(1,round(o.height))),Image.Resampling.LANCZOS);pt=o.point;canvas.paste(im,(20+round(pt[4]),top-round(pt[5])),im)
  elif o.kind=='label':pt=o.point;d.text((20+round(pt[4]),top-round(pt[5])-9),o.text or '',fill='white')
 canvas.save(O/'MAIN33-bitmap-simulation.png')
z.close()
receipt=dict(status='PASSED_BOUNDED_COMBINED_PRIVATE_0471_PACKAGE',version='0.471.0',new_supported_fields=1,quest_ids=1,new_Thai_fields=0,verbatim_reviewed_reuse_fields=1,complete_quests_claimed=0,source_proposal_sha256=sha((S/'main33-reviewed-pairs.json').read_bytes()),zip=dict(path=outzip.name,bytes=outzip.stat().st_size,sha256=sha(outzip.read_bytes())),runtime_files=155,old_runtime_files_exact_bytes_preserved=152,changed_metadata=list(changed),added_runtime=list(added),protected_Skill_font_assets_preserved=28,old_font_assets_preserved=115,new_fonts_glyphs_runs=0,all_TOC_Lua_compile=31,actual_data_order=loaded,positive_matches=4,actual_BitmapLayer_Thai_draws=draws,Thai_live_font_fallbacks=0,affected_glyph_crops_checked=len(crops),source_checks_reference='main33-source-checks.json:4positive40negative8route;not rerun here',matcher_Tracker_NPC_Skill_engines_changed=False,real_game_verified=False,launcher_published=False,old_UI_Skill_NPC_full_suites_rerun=False,local_AI_or_full_font_build=False,elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limits=['Only1progress slot,not a complete quest or whole-game claim','95772third-party race role held;oldcanonical retained','8315/84213existing multiline Tracker limitation retained','Windows/Mac M2 real game acceptance absent'])
for n,v in [('manifest.json',manifest),('receipt.json',receipt)]: (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for n,b in changed.items()|added.items():
 path=O/'runtime-delta'/pathlib.PurePosixPath(n).relative_to('ForeverThai');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
print(json.dumps(receipt,indent=2))
