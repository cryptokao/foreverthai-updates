"""Bounded additive MAIN39 build:82 fields, reviewed cuts, exact old assets, no local AI/full font rebuild."""
import pathlib,sys,json,re,zipfile,hashlib,io,time,collections
R=pathlib.Path(__file__).resolve().parent;S=R.parent;PREV=S/'package-main25-26';O=R/'build-0.475.0'
if O.exists():assert not any(O.iterdir()),'Refuse overwrite'
else:O.mkdir(parents=True)
sys.path[:0]=[str(PREV/'font-deps'),str(PREV)]
from lupa.lua51 import LuaRuntime
from PIL import Image,ImageDraw
from font_shapes_bounded import initialize,render
t=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
base=S/'package-main38/build-0.474.0/ForeverThai-0.474.0-main38-PRIVATE-TEST.zip';assert sha(base.read_bytes())=='d6541f6daf107d54fd88564299cc480b52ebb3ed7203f417850b13ac1198fb95'
proposal=json.loads((S/'main39-reviewed-pairs.json').read_text(encoding='utf8'));fields=proposal['fields'];assert len(fields)==14 and len({r['quest_id'] for r in fields})==11
source_checks=json.loads((S/'main39-source-checks.json').read_text(encoding='utf8'));patch=(S/'main39-reviewed-overlay.lua').read_bytes();assert sha(patch)==source_checks['overlay_sha256']=='fd48cfa8a153301a92190487285447c6140f2e40ba2db62332915f131ceeec68'
z=zipfile.ZipFile(base);toc0=z.read('ForeverThai/ForeverThai.toc').decode();files0=[s.replace('\\','/') for s in toc0.splitlines() if s.strip() and not s.startswith('#')];assert len(files0)==37
catalog=[s for s in files0 if s=='Catalog.lua' or s.startswith('MainQuest')];atlas=[s for s in files0 if s=='Atlas.lua' or s.startswith('AtlasMain')]
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();loaded=[]
for n in catalog:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a);loaded.append(n)
l.execute(patch.decode(),'ForeverThai',a);loaded.append('MainQuest39.lua')
for n in ['Match.lua']+atlas:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a);loaded.append(n)
assert len(a.glyphs)==14591
assert z.read('ForeverThai/Fonts/Sarabun-Regular.ttf')==(PREV/'baseline-Sarabun-Regular.ttf').read_bytes();initialize(PREV/'baseline-Sarabun-Regular.ttf')
needs=json.loads((S/'main39-font-run-needs.json').read_text(encoding='utf8'));plans=[];words=[]
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
assert len(plans)==10 and 0<=len(words)<120
pg=104;x=y=2;masks=({pg:Image.new('L',(1024,1024))} if words else {});newids={};lines=['-- MAIN39 exact retained Sarabun shaping; additive reviewed word boundaries.','local _, addon = ...']
for ix,word in enumerate(words,start=14592):
 shape,left,advance=render(word);assert 0<shape.width<=1020 and advance>0 and shape.height==56
 if x+shape.width+2>=1024:x,y=2,y+60
 if y+58>=1024:pg+=1;x=y=2;masks[pg]=Image.new('L',(1024,1024))
 assert pg<108 and f'ForeverThai/Fonts/Thai{pg}.tga' not in z.namelist()
 masks[pg].paste(shape,(x,y));glyph=[pg,x,y,shape.width,left,advance];newids[word]=ix
 assert a.glyphs[ix] is None
 lines.extend([f'assert(addon.glyphs[{ix}] == nil, "MAIN39 glyph baseline changed")',f'addon.glyphs[{ix}] = {{ '+', '.join(str(v) for v in glyph)+' }']);x+=shape.width+4
pagefiles={}
for pg,mask in masks.items():
 im=Image.new('RGBA',mask.size,'white');im.putalpha(mask);buf=io.BytesIO();im.save(buf,format='TGA');raw=buf.getvalue();assert len(raw)==4194348;pagefiles[f'ForeverThai/Fonts/Thai{pg}.tga']=raw
for plan in plans:
 ids=[]
 for piece in plan['pieces']:
  if piece['kind']=='existing':assert [int(v) for _,v in a.runs[piece['text']].items()]==piece['glyphs'];ids.extend(piece['glyphs'])
  else:ids.append(newids[piece['text']])
 lines.extend(['assert(addon.runs['+json.dumps(plan['run'],ensure_ascii=False)+'] == nil, "MAIN39 run baseline changed")','addon.runs['+json.dumps(plan['run'],ensure_ascii=False)+'] = { '+', '.join(str(v) for v in ids)+' }']);plan['glyphs']=ids
atlas_patch=('\n'.join(lines)+'\n').encode();l.execute(atlas_patch.decode(),'ForeverThai',a);loaded.append('AtlasMain39.lua');l.execute(z.read('ForeverThai/Bitmap.lua').decode(),'ForeverThai',a);loaded.append('Bitmap.lua')
assert all(a.runs[span] is not None for r in fields for span in re.findall(r'[\u0e00-\u0e7f]+',r['thai']))
assert '## Version: 0.474.0' in toc0 and 'MainQuest39.lua' not in toc0 and 'AtlasMain39.lua' not in toc0
toc=toc0.replace('## Version: 0.474.0','## Version: 0.475.0').replace('MainQuest38.lua\n','MainQuest38.lua\nMainQuest39.lua\n').replace('AtlasMain38.lua\n','AtlasMain38.lua\nAtlasMain39.lua\n')
assert next(s for s in toc0.splitlines() if s.startswith('## SavedVariables:'))==next(s for s in toc.splitlines() if s.startswith('## SavedVariables:'))
sources=z.read('ForeverThai/SOURCES-TH.txt')+b'\nMAIN39:14new literal fields/11existingquestIDs,5newreviewedThai+9verbatimreviewedreuse,NOTcompletequests. Own-ID WowheadForever primary full NPC phase bodies;gamequesttext Blizzard Entertainment.86792literal6/4/2 objectives independentlycorroborated at wowhead.com/forever/quest=86792/thinning-their-forces;rawtemplate EG0f202e892f1a15c8192c232351824eccb99efd8a,blob307e74c62ee5d897d6d4c59363c919820992c5ac. EG attribution Efficient Games https://efficient.games CC BY4.0. SourcepageURLs/hashes in reviewmanifest.5untypednamefields held;no role/condition/count guesses.96602Progress NPCparagraph excludes renderer-only itemtable and reuses identical olddescription;olddescription unchanged. Old8918translatornote retained but notcopied into new84160NPCbody. All olddata/engines/aliases/settings/SavedVariables/70938fix/Quest/Tracker/Questie/NPC/Skill/Talent/Profession/Item/fonts exactpreserved. Private0.475only,nextnormalcustomer0.480. No actualWindows/MacM2gameplayacceptance.8315/84213multilineTrackerguard retained.\n'
changed={'ForeverThai/ForeverThai.toc':toc.encode(),'ForeverThai/SOURCES-TH.txt':sources};added={'ForeverThai/MainQuest39.lua':patch,'ForeverThai/AtlasMain39.lua':atlas_patch,**pagefiles}
manifest={};preserved=[];outzip=O/'ForeverThai-0.475.0-main39-PRIVATE-TEST.zip'
with zipfile.ZipFile(outzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as out:
 for n in z.namelist():
  assert '..' not in pathlib.PurePosixPath(n).parts and not pathlib.PurePosixPath(n).is_absolute()
  if n in changed:b=changed[n]
  else:b=z.read(n);preserved.append(n)
  out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
 for n,b in added.items():assert n not in manifest;out.writestr(n,b);manifest[n]=dict(bytes=len(b),sha256=sha(b))
with zipfile.ZipFile(outzip) as check:
 assert len(check.namelist())==len(set(check.namelist()))==164+len(added) and len(preserved)==162
 for n,m in manifest.items():b=check.read(n);assert len(b)==m['bytes'] and sha(b)==m['sha256']
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];oldfonts=[n for n in z.namelist() if '/Fonts/' in n];assert len(protected)==28 and len(oldfonts)==118
 for n in protected+oldfonts:assert n in preserved and check.read(n)==z.read(n)
 files=[s.replace('\\','/') for s in toc.splitlines() if s.strip() and not s.startswith('#')];assert len(files)==len(set(files))==39
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
  fn=f'MAIN39-bitmap-simulation-{page:02}.png';canvas.save(O/fn);previewfiles.append(fn)
z.close()
receipt=dict(status='PASSED_BOUNDED_COMBINED_PRIVATE0475_PACKAGE',version='0.475.0',new_supported_fields=14,new_Thai_fields=5,verbatim_reviewed_reuse=9,quest_ids=11,new_runtime_ids=0,new_field_slots=14,appended_variants=0,complete_quests_claimed=0,source_proposal_sha256=sha((S/'main39-reviewed-pairs.json').read_bytes()),zip=dict(path=outzip.name,bytes=outzip.stat().st_size,sha256=sha(outzip.read_bytes())),runtime_files=len(manifest),old_runtime_files_exact_bytes_preserved=len(preserved),metadata_changed=list(changed),added_runtime=list(added),protected_Skill_font_assets_preserved=len(protected),old_font_assets_preserved=len(oldfonts),new_word_glyphs=len(words),new_Thai_runs=len(plans),new_pages=len(pagefiles),actual_changed_data_order=loaded,all_TOC_Lua_compile=len(files),actual_BitmapLayer_Thai_draws=draws,Thai_live_font_fallbacks=0,glyph_crops_pixel_checked=len(crops),preview_files=previewfiles,source_checks_reference='MAIN39:168positives404negatives220wrongphase+4legalsamebodyroutes;not rerun here',engines_or_settings_changed=False,real_Windows_MacM2_acceptance=False,launcher_published=False,old_UI_Skill_NPC_full_suites_rerun=False,localAI_NLP_or_full_font_rebuild=False,elapsed_wall_seconds=time.perf_counter()-t,cpu_seconds=time.process_time()-cpu,limits=['14literal fields/11existingIDs,NOTcompletequests or enabledwholegamepercent','Current enabled inventory/per-row build unproven','5newuntypednamefields and earlieridentity/titleholds notguessed','8315/84213multilineTracker guard retained','No actualWindows/MacM2 acceptance'])
for n,v in [('receipt.json',receipt),('manifest.json',manifest),('font-plan.json',dict(new_words=words,plans=plans))]:(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for n,b in {**changed,**added}.items():
 p=O/'runtime-delta'/pathlib.PurePosixPath(n).relative_to('ForeverThai');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
print(json.dumps(receipt,indent=2))
