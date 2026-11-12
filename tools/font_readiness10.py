"""Affected bitmap checks after reviewed batch10 append; no unchanged UI suites."""
import ast,hashlib,json,pathlib,re,subprocess,zipfile
from lupa.lua51 import LuaRuntime
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';tree='d2562e61bec8ab0be3c5bd5e2f645d755eb55238' # Actual pre-font runtime used by the reviewed candidate10 check; never moving HEAD;prior=subprocess.check_output(['git','-C',str(ROOT),'show',tree+':Atlas.lua']);assert (RUN/'Atlas.lua').read_bytes().startswith(prior)
oldnames=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',tree],text=True).splitlines();unchanged=0
for name in oldnames:
 if name=='Atlas.lua':continue
 assert (RUN/name).read_bytes()==subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+name]),name;unchanged+=1
z=zipfile.ZipFile('/workspace/foreverthai-dev/downloads/ForeverThai-0.462.0-Quest-Skills-PRIVATE-TEST.zip');protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
for n in protected:assert (ROOT/'src'/n).read_bytes()==z.read(n),n
reference=ROOT/'tests/recovered_npc/check_speech_v04230.py';assert hashlib.sha256(reference.read_bytes()).hexdigest()=='bdcf2ff10c973ab90cd372cfbd8f9416805f1fb0167be0d3e2d8a08193977b58';parsed=ast.parse(reference.read_text());fixture=next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fixture' for t in n.targets));lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(fixture);a=lua.table();old=lua.table();load=lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end');load(prior.decode(),old)
for n in ['Atlas','Bitmap']:load((RUN/f'{n}.lua').read_text(),a)
texts=[]
for path in ['npc-gossip-08.json','npc-templates-09.json','public-literals-10.json']:
 doc=json.loads((ROOT/'evidence'/path).read_text());texts.extend(v['thai'] for v in doc['fields']);texts.extend(doc.get('font_texts',[]))
texts.extend(v['thai'] for v in json.loads((ROOT/'tests/npc-template-cases09.json').read_text()));addedruns={s for text in texts for s in re.findall(r'[\u0e00-\u0e7f]+',text) if old.runs[s] is None};assert len(addedruns)==38
newpages=[p for p in (RUN/'Fonts').glob('Thai*.tga') if 'Fonts/'+p.name not in oldnames];assert [p.name for p in newpages]==['Thai88.tga'];images={}
for p in newpages:
 im=Image.open(p);im.load();assert im.size==(1024,1024) and im.mode=='RGBA';assert im.getchannel('A').getextrema()==(0,255);images[int(re.search(r'\d+',p.name)[0])]=im
for run in addedruns:
 assert a.runs[run] is not None
 for _,idx in a.runs[run].items():
  glyph=a.glyphs[idx];page,x,y,w=int(glyph[1]),int(glyph[2]),int(glyph[3]),int(glyph[4]);height=int(glyph[7] or 56);assert page in images and x>=0 and y>=0 and x+w<=1024 and y+height<=1024;assert images[page].getchannel('A').crop((x,y,x+w,y+height)).getbbox() is not None
painted=0
for text in texts:
 for run in re.findall(r'[\u0e00-\u0e7f]+',text):assert a.runs[run] is not None,run
 layer,draw=a.BitmapLayer(lua.globals().UIParent,'TOPLEFT',0,0,484,18);height=draw(text,1,1,1);assert height>0 and layer.visible
 for _,label in layer.labels.items():
  if label.visible:assert not re.search(r'[\u0e00-\u0e7f]',label.text or ''),'Thai fell back to live font'
 painted+=1
report=dict(status='passed',prior_runtime_tree=tree,old_other_component_bytes_preserved=unchanged,protected_skill_font_assets_preserved=len(protected),old_atlas_prefix_sha256=hashlib.sha256(prior).hexdigest(),new_thai_runs=38,new_glyphs=len(a.glyphs)-len(old.glyphs),new_font_pages=[p.name for p in newpages],actual_bitmap_text_draws=painted,font_ready=True,scope='Append-only batch10 after Root wording review. Existing runtime bytes except Atlas unchanged; old Atlas prefix and all old pages retained. New glyph bounds/alpha, all08–10Thai runs/titles/class oracles and actual unchanged BitmapLayer draw checked. No unchanged Skill/NPC686 suite rerun or game proof.')
(ROOT/'evidence/font-readiness10.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
