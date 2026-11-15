"""Bounded additive MAIN40 build:82 fields, reviewed cuts, exact old assets, no local AI/full font rebuild."""
import pathlib,sys,json,re,zipfile,hashlib,io,time,collections
R=pathlib.Path(__file__).resolve().parent;S=R.parent;PREV=S/'package-main25-26';O=R/'build-0.476.0'
if O.exists():assert not any(O.iterdir()),'Refuse overwrite'
else:O.mkdir(parents=True)
sys.path[:0]=[str(PREV/'font-deps'),str(PREV)]
from lupa.lua51 import LuaRuntime
from PIL import Image,ImageDraw
from font_shapes_bounded import initialize,render
t=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
base=S/'package-main39/build-0.475.0/ForeverThai-0.475.0-main39-PRIVATE-TEST.zip';assert sha(base.read_bytes())=='a9ec2fd4de80f353bd56ad47775555608c00812e98f8289a3a1212d39147298e'
proposal=json.loads((S/'main40-reviewed-pairs.json').read_text(encoding='utf8'));fields=proposal['fields'];assert len(fields)==2 and len({r['quest_id'] for r in fields})==2
source_checks=json.loads((S/'main40-source-checks.json').read_text(encoding='utf8'));patch=(S/'main40-reviewed-overlay.lua').read_bytes();assert sha(patch)==source_checks['overlay_sha256']=='4e5d4db0f448413105c0e3cc13c928d46527c7653c9d84ccf6a1ee7a428c8f2a'
z=zipfile.ZipFile(base);toc0=z.read('ForeverThai/ForeverThai.toc').decode();files0=[s.replace('\\','/') for s in toc0.splitlines() if s.strip() and not s.startswith('#')];assert len(files0)==39
catalog=[s for s in files0 if s=='Catalog.lua' or s.startswith('MainQuest')];atlas=[s for s in files0 if s=='Atlas.lua' or s.startswith('AtlasMain')]
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();loaded=[]
for n in catalog:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a);loaded.append(n)
l.execute(patch.decode(),'ForeverThai',a);loaded.append('MainQuest40.lua')
for n in ['Match.lua']+atlas:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a);loaded.append(n)
assert len(a.glyphs)==14599
assert z.read('ForeverThai/Fonts/Sarabun-Regular.ttf')==(PREV/'baseline-Sarabun-Regular.ttf').read_bytes();initialize(PREV/'baseline-Sarabun-Regular.ttf')
needs=json.loads((S/'main40-font-run-needs.json').read_text(encoding='utf8'));plans=[];words=[]
for row in needs:
 if row['existing_full_run']:assert a.runs[row['run']] is not None;continue
 assert a.runs[row['run']] is None and ''.join(row['words'])==row['run'];pieces=[]
 for word in row['words']:
  run=a.runs[word]
  if run is not None:pieces.append(dict(kind='existing',text=word,glyphs=[int(run[i]) for i in range(1,len(run)+1)]))
  else:
   pieces.append(dict(kind='new',text=word))
   if word not in words:words.append(word)
 plans.append(dict(run=row['run'],pieces=pieces))
assert len(plans)==12 and 0<=len(words)<120
pg=105;x=y=2;masks=({pg:Image.new('L',(1024,1024))} if words else {});newids={};lines=['-- MAIN40 exact retained Sarabun shaping; additive reviewed word boundaries.','local _, addon = ...']
for ix,word in enumerate(words,start=14600):
 shape,left,advance=render(word);assert 0<shape.width<=1020 and advance>0 and shape.height==56
 if x+shape.width+2>=1024:x,y=2,y+60
 if y+58>=1024:pg+=1;x=y=2;masks[pg]=Image.new('L',(1024,1024))
 assert pg<108 and f'ForeverThai/Fonts/Thai{pg}.tga' not in z.namelist()
 masks[pg].paste(shape,(x,y));glyph=[pg,x,y,shape.width,left,advance];newids[word]=ix
 assert a.glyphs[ix] is None
 lines.extend([f'assert(addon.glyphs[{ix}] == nil, "MAIN40 glyph baseline changed")',f'addon.glyphs[{ix}] = {{ '+', '.join(str(v) for v in glyph)+' }']);x+=shape.width+4
pagefiles={}
for pg,mask in masks.items():
 im=Image.new('RGBA',mask.size,'white');im.putalpha(mask);buf=io.BytesIO();im.save(buf,format='TGA');raw=buf.getvalue();assert len(raw)==4194348;pagefiles[f'ForeverThai/Fonts/Thai{pg}.tga']=raw
for plan in plans:
 ids=[]
 for piece in plan['pieces']:
  if piece['kind']=='existing':assert [int(v) for _,v in a.runs[piece['text']].items()]==piece['glyphs'];ids.extend(piece['glyphs'])
  else:ids.append(newids[piece['text']])
 lines.extend(['assert(addon.runs['+json.dumps(plan['run'],ensure_ascii=False)+'] == nil, "MAIN40 run baseline changed")','addon.runs['+json.dumps(plan['run'],ensure_ascii=False)+'] = { '+', '.join(str(v) for v in ids)+' }']);plan['glyphs']=ids
atlas_patch=('\n'.join(lines)+'\n').encode();l.execute(atlas_patch.decode(),'ForeverThai',a);loaded.append('AtlasMain40.lua');l.execute(z.read('ForeverThai/Bitmap.lua').decode(),'ForeverThai',a);loaded.append('Bitmap.lua')
assert all(a.runs[span] is not None for r in fields for span in re.findall(r'[\u0e00-\u0e7f]+',r['thai']))
assert '## Version: 0.475.0' in toc0 and 'MainQuest40.lua' not in toc0 and 'AtlasMain40.lua' not in toc0
toc=toc0.replace('## Version: 0.475.0','## Version: 0.476.0').replace('MainQuest39.lua\n','MainQuest39.lua\nMainQuest40.lua\n').replace('AtlasMain39.lua\n','AtlasMain39.lua\nAtlasMain40.lua\n')
assert next(s for s in toc0.splitlines() if s.startswith('## SavedVariables:'))==next(s for s in toc.splitlines() if s.startswith('## SavedVariables:'))
sources=z.read('ForeverThai/SOURCES-TH.txt')+b'\nMAIN40:2new literal fields/2existingquestIDs;1newreviewedThai+1verbatimreviewedreuse,NOTcompletequests. PrimaryIcyVeinsForever own-ID phase transcriptions https://db.icy-veins.com/wow-forever/quests/93362 and /93601. Questtext BlizzardEntertainment;IcyVeins earlyaccess database reports Added1.60.1.70532,not current per-row eligibility.93362progress exactreviewedreuse5102progress.93601completion literalNightElf only,fullstatic sourceguard,no UnitRace/playercondition/identity dispatch;Human/Orc/macrorace forms rejected.93362completion nameplaceholder held. Allold Quest/Tracker/Questie/NPC/Skill/Talent/Profession/Item/fonts/aliases/settings/SavedVariables/70938fix exactpreserved. Private0.476only,nextnormalcustomer0.480. NoactualWindows/MacM2gameplayacceptance.8315/84213multilineTrackerguard retained.\n'
changed={'ForeverThai/ForeverThai.toc':toc.encode(),'ForeverThai/SOURCES-TH.txt':sources};added={'ForeverThai/MainQuest40.lua':patch,'ForeverThai/AtlasMain40.lua':atlas_patch,**pagefiles}
manifest={};preserved=[];outzip=O/'ForeverThai-0.476.0-main40-PRIVATE-TEST.zip'
with zipfile.ZipFile(outzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as out:
 for n in z.namelist():
  assert '..' not in pathlib.PurePosixPath(n).parts and not pathlib.PurePosixPath(n).is_absolute()
  if n in changed:b=changed[n]
  else:b=z.read(n);preserved.append(n)
  out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
 for n,b in added.items():assert n not in manifest;out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
with zipfile.ZipFile(outzip) as check:
 assert len(check.namelist())==len(set(check.namelist()))==167+len(added) and len(preserved)==165
 for n,m in manifest.items():b=check.read(n);assert len(b)==m['bytes'] and sha(b)==m['sha256']
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];oldfonts=[n for n in z.namelist() if '/Fonts/' in n];assert len(protected)==28 and len(oldfonts)==119
 for n in protected+oldfonts:assert n in preserved and check.read(n)==z.read(n)
 files=[s.replace('\\','/') for s in toc.splitlines() if s.strip() and not s.startswith('#')];assert len(files)==len(set(files))==41
 syntax=l.eval('function(s)local f,e=loadstring(s);return f~=nil,e end')
 for n in files:assert 'ForeverThai/'+n in manifest;ok,err=syntax(check.read('ForeverThai/'+n).decode());assert ok,(n,err)
 l.execute((S/'package-main27/bitmap_fixture.lua').read_text(encoding='utf8'));l.execute('UnitName=function()return sampleName end;UnitClass=function()return sampleClass,sampleClassID end;UnitRace=function()return sampleRace end')
 draws=0;coords=set();previews=collections.defaultdict(list);questorder=list(dict.fromkeys(r['quest_id'] for r in fields))
 for name,cl,cid,race in [('CloudTester','Druid','DRUID','Night Elf'),('NewHunter','Hunter','HUNTER','Night Elf'),('MageReader','Mage','MAGE','Human'),('PriestReader','Priest','PRIEST','Windshaper Skyborne')]:
  g=l.globals();g.sampleName=name;g.sampleClass=cl;g.sampleClassID=cid;g.sampleRace=race
  for r in fields:
   actual=a.Translate(a.quests[r['quest_id']][r['field']],re.sub(r'\$[Bb]','\n',r['english']));assert actual==r['thai'];before=len(g.created);layer,draw=a.BitmapLayer(g.UIParent,'TOPLEFT',0,0,484,18);height=draw(actual,1,1,1);assert height>0 and layer.visible
   objects=[g.created[i] for i in range(before+1,len(g.created)+1)];assert any(o.kind=='texture' and o.visible for o in objects)
   assert all(not re.search(r'[\u0e00-\u0e7f]',o.text or '') for o in objects if o.kind=='label' and o.visible),'Thai live-font fallback'
   for o in objects:
    if o.kind=='texture' and o.visible:
     page=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;gx,gy,xe,ye=[round(uv[i]*1024) for i in [1,3,2,4]];coords.add((page,gx,gy,xe-gx,ye-gy))
   if name=='CloudTester':previews[questorder.index(r['quest_id'])//6+1].append((r,height,objects))
   draws+=1
 crops={};bypage=collections.defaultdict(list)
 for key in coords:bypage[key[0]].append(key)
 for page,keys in bypage.items():
  fn=f'ForeverThai/Fonts/Thai{page}.tga';raw=pagefiles[fn] if fn in pagefiles else check.read(fn);img=Image.open(io.BytesIO(raw));img.load();assert img.mode=='RGBA' and img.size==(1024,1024)
  for key in keys:
   _,gx,gy,w,h=key;assert min(gx,gy)>=0 and gx+w<=1024 and gy+h<=1024;crop=img.crop((gx,gy,gx+w,gy+h));assert crop.getchannel('A').getbbox();crops[key]=crop
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
  fn=f'MAIN40-bitmap-simulation-{page:02}.png';canvas.save(O/fn);previewfiles.append(fn)
z.close()
receipt=dict(status='PASSED_BOUNDED_COMBINED_PRIVATE0476_PACKAGE',version='0.476.0',new_supported_fields=2,new_Thai_fields=1,verbatim_reviewed_reuse=1,quest_ids=2,new_runtime_ids=0,new_field_slots=2,appended_variants=0,complete_quests_claimed=0,source_proposal_sha256=sha((S/'main40-reviewed-pairs.json').read_bytes()),zip=dict(path=outzip.name,bytes=outzip.stat().st_size,sha256=sha(outzip.read_bytes())),runtime_files=len(manifest),old_runtime_files_exact_bytes_preserved=len(preserved),metadata_changed=list(changed),added_runtime=list(added),protected_Skill_font_assets_preserved=len(protected),old_font_assets_preserved=len(oldfonts),new_word_glyphs=len(words),new_Thai_runs=len(plans),new_pages=len(pagefiles),actual_changed_data_order=loaded,all_TOC_Lua_compile=len(files),actual_BitmapLayer_Thai_draws=draws,Thai_live_font_fallbacks=0,glyph_crops_pixel_checked=len(crops),preview_files=previewfiles,source_checks_reference='MAIN40:24positives78negatives32wrongphase+0legalsamebodyroutes;not rerun here',engines_or_settings_changed=False,real_Windows_MacM2_acceptance=False,launcher_published=False,old_UI_Skill_NPC_full_suites_rerun=False,localAI_NLP_or_full_font_rebuild=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu,limits=['2literal fields/2existingIDs,NOTcompletequests or enabledwholegamepercent','Current enabled inventory/per-row build unproven','93362completion untypedname and earlieridentity/titleholds notguessed','8315/84213multilineTracker guard retained','No actualWindows/MacM2 acceptance'])
for n,v in [('receipt.json',receipt),('manifest.json',manifest),('font-plan.json',dict(new_words=words,plans=plans))]:(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for n,b in {**changed,**added}.items():
 p=O/'runtime-delta'/pathlib.PurePosixPath(n).relative_to('ForeverThai');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
print(json.dumps(receipt,indent=2))
