"""Bounded MAIN25/26 package fallback: 4 fields, <=32 new word glyphs, one page. No game/AI/full suites."""
import pathlib,json,sys,re,hashlib,zipfile,time,unicodedata,io,copy
R=pathlib.Path(__file__).resolve().parent;S=R.parent
sys.path.insert(0,str(R/'font-deps'))
from lupa.lua51 import LuaRuntime
from PIL import Image,ImageDraw,ImageFont
from font_shapes_bounded import initialize,render
start=time.perf_counter();cpu=time.process_time();sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/'build-0.468.0'
if OUT.exists():assert not any(OUT.iterdir()),'Refuse to overwrite a prior build'
else:OUT.mkdir()
base=R/'ForeverThai-0.467.0-baseline.zip';assert sha(base.read_bytes())=='dca6283c1fdb7ee6d7abbee07f2f7f9b86ddbdf68e694dcd2b0074ed883d633e'
pairs=[v for n in [25,26] for v in json.loads((S/f'main{n}-reviewed-pairs.json').read_text(encoding='utf-8'))['pairs']];assert len(pairs)==4
cuts=json.loads((R/'run-reuse-proposal.json').read_text(encoding='utf-8'));chains={v['run']:v for v in json.loads((R/'existing-run-chains.json').read_text(encoding='utf-8'))}
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
z=zipfile.ZipFile(base)
for n,want in [('Catalog.lua','9958d2edf3096a4cdffd39b5c99a58cc8a1bc3e1729e18b2d09c6f7e0e481118'),('Atlas.lua','c41c4f3494cdf38dc159528ee714da97ecf76c4822b1be5445a55630a8f7819a'),('Match.lua','d3cf853e0e7c997652b589993f827e5f7794e2f789e59e484a4ab97e97b24b1d')]:
 b=z.read('ForeverThai/'+n);assert sha(b)==want;l.execute(b.decode(),'ForeverThai',a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end;issecretvalue=function(v)return v=="SECRET_SENTINEL"end')
old_slots=len(a.glyphs);assert old_slots==14333 and max(v[1] for _,v in a.glyphs.items())==97
old_runs=sum(1 for _ in a.runs.items());assert old_runs==102898
serialize=l.eval('function(v) local function s(x) if type(x)~="table" then return type(x)..":"..tostring(x) end local t={} for k,v in pairs(x) do t[#t+1]=s(k).."="..s(v) end table.sort(t) return "{"..table.concat(t,",").."}" end return s(v) end')
old_canon={q:serialize(a.quests[q][f]) for q,f in [(94236,'completion'),(78270,'progress')]}
quest_lines=['-- Reviewed MAIN25/26 literal additions; retain canonical text and all prior aliases.','local _, addon = ...']
for n in [25,26]:
 lines=(S/f'main{n}-reviewed-overlay.lua').read_text(encoding='utf-8').splitlines();assert lines[1]=='local _, addon = ...';quest_lines.extend(lines[2:])
quest_patch=('\n'.join(quest_lines)+'\n').encode();l.execute(quest_patch.decode(),'ForeverThai',a)
for q,f in [(94236,'completion'),(78270,'progress')]:
 e=a.quests[q][f];vs=e.variants;ix=len(vs);saved=vs[ix];vs[ix]=None
 if ix==1:e.variants=None
 assert serialize(e)==old_canon[q]
 e.variants=vs;vs[ix]=saved
missing={s for f in pairs for s in re.findall(r'[\u0e00-\u0e7f]+',f['thai']) if a.runs[s] is None};assert missing=={v['run'] for v in cuts} and len(missing)==19
initialize(R/'baseline-Sarabun-Regular.ttf')
page=98;mask=Image.new('L',(1024,1024));x=y=2;nextid=old_slots+1;new_word_ids={};new_glyphs={};atlaslines=['-- MAIN25/26 additive run aliases and bounded shaped words. Existing Atlas is unchanged.','local _, addon = ...'];provenance=[]
for row in cuts:
 run=row['run'];assert a.runs[run] is None;chain=chains[run];pieces=chain['existing_runs'] if chain['covered'] else row['words'];assert ''.join(pieces)==run
 ids=[];parts=[]
 for word in pieces:
  assert word and not unicodedata.category(word[0]).startswith('M') and word[0]!='\u0e33'
  known=a.runs[word]
  if known is not None:
   seq=[int(known[i]) for i in range(1,len(known)+1)];ids.extend(seq);parts.append(dict(text=word,kind='existing exact shaped run',glyphs=seq));continue
  if word not in new_word_ids:
   shape,left,advance=render(word);assert 0<shape.width<=1020 and advance>0 and shape.height==56
   if x+shape.width+2>=1024:x,y=2,y+60
   assert y+shape.height+2<1024,'Bounded one-page font budget exceeded'
   mask.paste(shape,(x,y));g=[page,x,y,shape.width,left,advance];new_word_ids[word]=nextid;new_glyphs[nextid]=g
   atlaslines.append(f'assert(addon.glyphs[{nextid}] == nil, "MAIN25/26 Atlas baseline mismatch")')
   atlaslines.append(f'addon.glyphs[{nextid}] = {{ '+', '.join(str(v) for v in g)+' }');x+=shape.width+4;nextid+=1
  idx=new_word_ids[word];ids.append(idx);parts.append(dict(text=word,kind='new HarfBuzz shaped word',glyphs=[idx]))
 atlaslines.append('assert(addon.runs['+json.dumps(run,ensure_ascii=False)+'] == nil, "MAIN25/26 run baseline mismatch")')
 atlaslines.append('addon.runs['+json.dumps(run,ensure_ascii=False)+'] = { '+', '.join(str(i) for i in ids)+' }');provenance.append(dict(run=run,parts=parts,glyphs=ids))
assert 0<len(new_glyphs)<=32
atlas_patch=('\n'.join(atlaslines)+'\n').encode();l.execute(atlas_patch.decode(),'ForeverThai',a)
rgba=Image.new('RGBA',mask.size,'white');rgba.putalpha(mask);buf=io.BytesIO();rgba.save(buf,format='TGA');tga=buf.getvalue();assert len(tga)==4194348
toc=z.read('ForeverThai/ForeverThai.toc').decode();assert '## Version: 0.467.0' in toc and 'MainQuest2526.lua' not in toc
toc=toc.replace('## Version: 0.467.0','## Version: 0.468.0').replace('Catalog.lua\n','Catalog.lua\nMainQuest2526.lua\n').replace('Atlas.lua\n','Atlas.lua\nAtlasMain2526.lua\n')
sources=z.read('ForeverThai/SOURCES-TH.txt')+b'\nMAIN25/26 reviewed literal additions (4 fields /4 IDs), 2026-11-15.\nFVO primary captures: https://github.com/quinn-dougherty/forever-vo/issues/3493 ; /issues/3511 ; /issues/3519 .\nSource checkpoint: cryptokao/foreverthai-updates 1b7e5922a30ff482c79351be2bc00df8714ef233 .\nNo whole-game coverage or in-game Windows/Mac M2 acceptance claim.\n'
changed={'ForeverThai/ForeverThai.toc':toc.encode(),'ForeverThai/SOURCES-TH.txt':sources}
added={'ForeverThai/MainQuest2526.lua':quest_patch,'ForeverThai/AtlasMain2526.lua':atlas_patch,'ForeverThai/Fonts/Thai98.tga':tga}
outzip=OUT/'ForeverThai-0.468.0-main25-26-PRIVATE-TEST.zip';manifest={};baseline_manifest={};preserved=[]
with zipfile.ZipFile(outzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as dest:
 for info in z.infolist():
  name=info.filename;assert not pathlib.PurePosixPath(name).is_absolute() and '..' not in pathlib.PurePosixPath(name).parts and not info.is_dir()
  b=z.read(name);baseline_manifest[name]=dict(bytes=len(b),sha256=sha(b));out=changed.get(name,b)
  if name not in changed:preserved.append(name)
  dest.writestr(name,out);manifest[name]=dict(bytes=len(out),sha256=sha(out))
 for name,b in added.items():dest.writestr(name,b);manifest[name]=dict(bytes=len(b),sha256=sha(b))
# Read back every actual packaged file once. No old functional suite rerun.
with zipfile.ZipFile(outzip) as check:
 assert len(check.infolist())==len(set(check.namelist()))==148 and set(check.namelist())==set(manifest)
 for name,meta in manifest.items():
  b=check.read(name);assert len(b)==meta['bytes'] and sha(b)==meta['sha256'],name
 for name in preserved:assert manifest[name]==baseline_manifest[name]
 for line in toc.splitlines():
  if line and not line.startswith('#'):assert 'ForeverThai/'+line.replace('\\','/') in manifest,line
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28 and all(n in preserved for n in protected)
 oldfonts=[n for n in z.namelist() if '/Fonts/' in n];assert len(oldfonts)==112 and all(n in preserved for n in oldfonts)
 for n in ['Catalog.lua','Atlas.lua','Match.lua','Observe.lua','Panel.lua','Speech.lua','Tracker.lua','Events.lua','Bitmap.lua']:assert 'ForeverThai/'+n in preserved
 images={98:rgba}
 def pageimage(pg):
  if pg not in images:
   im=Image.open(io.BytesIO(z.read(f'ForeverThai/Fonts/Thai{pg}.tga')));im.load();images[pg]=im
  return images[pg]
 used=set()
 for v in provenance:
  assert a.runs[v['run']] is not None
  for idx in v['glyphs']:
   if idx in used:continue
   used.add(idx);g=a.glyphs[idx];pg,gx,gy,w=int(g[1]),int(g[2]),int(g[3]),int(g[4]);h=int(g[7] or 56);im=pageimage(pg)
   assert im.mode=='RGBA' and im.size==(1024,1024) and min(gx,gy)>=0 and gx+w<=1024 and gy+h<=1024
   assert im.getchannel('A').crop((gx,gy,gx+w,gy+h)).getbbox() is not None
 l.execute('''
 created={}; UIParent={}; STANDARD_TEXT_FONT='fixture-english-only'
 local methods={}
 function methods:SetPoint(...) self.point={...} end
 function methods:SetSize(w,h) self.width=w;self.height=h end
 function methods:SetWidth(w) self.width=w end
 function methods:SetHeight(h) self.height=h end
 function methods:Show() self.visible=true end
 function methods:Hide() self.visible=false end
 function methods:SetTexture(v) self.texture=v end
 function methods:SetTexCoord(...) self.uv={...} end
 function methods:SetText(v) self.text=v end
 function methods:GetStringWidth() return #(self.text or '')*8 end
 function methods:ClearAllPoints() self.point=nil end
 function methods:SetFont(...) end
 function methods:SetTextColor(...) end
 function methods:SetVertexColor(...) end
 local function object(kind) local o=setmetatable({kind=kind,visible=false},{__index=methods}); created[#created+1]=o; return o end
 function methods:CreateTexture(...) return object('texture') end
 function methods:CreateFontString(...) return object('label') end
 function CreateFrame(...) return object('frame') end
 ''');l.execute(z.read('ForeverThai/Bitmap.lua').decode(),'ForeverThai',a)
 positives=negatives=draws=0;preview_rows=[]
 for v in pairs:
  q,f,en=v['quest_id'],v['field'],v['english'];entry=a.quests[q][f];th=a.Translate(entry,en);assert th==v['thai'];positives+=1
  for wrong in [en+' Changed.',en[:-1],None,'','SECRET_SENTINEL']:
   assert a.Translate(entry,wrong) is None;negatives+=1
  other=next(w for w in pairs if w['quest_id']!=q);assert a.Translate(a.quests[other['quest_id']][f],en) is None;negatives+=1
  wrongphase='completion' if f=='progress' else 'progress';assert a.Translate(a.quests[q][wrongphase],en) is None;negatives+=1
  before=len(l.globals().created);layer,draw=a.BitmapLayer(l.globals().UIParent,'TOPLEFT',0,0,484,18);height=draw(th,1,1,1);assert height>0 and layer.visible
  objects=[l.globals().created[i] for i in range(before+1,len(l.globals().created)+1)]
  assert any(o.kind=='texture' and o.visible for o in objects)
  assert all(not re.search(r'[\u0e00-\u0e7f]',o.text or '') for o in objects if o.kind=='label' and o.visible),'Thai live-font fallback'
  preview_rows.append((v,height,objects));draws+=1
 canvas=Image.new('RGB',(1060,int(sum(h for _,h,_ in preview_rows)+len(preview_rows)*65)+30),(22,28,35));d=ImageDraw.Draw(canvas);top=15
 for v,height,objects in preview_rows:
  d.text((20,top),f"Quest {v['quest_id']} / {v['field']} - BitmapLayer simulation, NOT in-game",fill=(240,195,80));top+=30
  for o in objects:
   if not o.visible or o.kind!='texture':continue
   pg=int(re.search(r'Thai([0-9]+)\.tga$',o.texture)[1]);uv=o.uv;im=pageimage(pg);crop=im.crop(tuple(round(uv[i]*1024) for i in [1,3,2,4]));crop=crop.resize((max(1,round(o.width)),max(1,round(o.height))),Image.Resampling.LANCZOS);pt=o.point;canvas.paste(crop,(20+round(pt[4]),top-round(pt[5])),crop)
  # Latin remains live text in-game; include its actual fixture positions too.
  for o in objects:
   if o.visible and o.kind=='label':
    pt=o.point;d.text((20+round(pt[4]),top-round(pt[5])-9),o.text or '',fill='white')
  top+=int(height)+35
 canvas.save(OUT/'MAIN25-26-bitmap-simulation.png')
z.close()
receipt=dict(status='PASSED_BOUNDED_PRIVATE_0468_PACKAGE_VERIFICATION',version='0.468.0',translation_counts=dict(new_thai_fields=4,quest_ids=4,complete_quests_claimed=0),baseline_sha256=sha(base.read_bytes()),zip=dict(path=outzip.name,bytes=outzip.stat().st_size,sha256=sha(outzip.read_bytes())),runtime_files=148,old_runtime_files_exact_bytes_preserved=len(preserved),authorized_metadata_changed=list(changed),new_runtime_files=list(added),protected_Skill_font_assets_preserved=len(protected),old_font_assets_preserved=len(oldfonts),Catalog_Atlas_unchanged=True,new_runs=19,new_word_glyphs=len(new_glyphs),new_pages=1,affected_glyphs_pixel_checked=len(used),positive_exact_matches=positives,negative_checks=negatives,actual_BitmapLayer_Thai_draws=draws,Thai_live_font_fallbacks=0,engine_files_changed=False,old_functional_suites_rerun=False,local_scope='One serial bounded fallback package with <=32 new word glyphs. No local AI, full font rebuild, full test suite or game control.',elapsed_wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,limitations=['Real Windows/Mac M2 game acceptance remains unverified','No whole-game enabled quest inventory or whole-game percent','Existing84213 objective multiline Tracker English fallback unchanged','No customer Launcher publication in this private build'])
for name,data in [('manifest.json',manifest),('receipt.json',receipt),('run-provenance.json',provenance)]:(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name,b in added.items():
 p=OUT/'runtime-delta'/pathlib.PurePosixPath(name).relative_to('ForeverThai');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
(OUT/'runtime-delta/ForeverThai.toc').write_bytes(changed['ForeverThai/ForeverThai.toc']);(OUT/'runtime-delta/SOURCES-TH.txt').write_bytes(sources)
print(json.dumps(receipt,ensure_ascii=False,indent=2))
