"""Only approved122 render paths + append-only Atlas/page preservation; no old runtime suites."""
import ast,json,pathlib,hashlib,re,zipfile
from lupa.lua51 import LuaRuntime
from PIL import Image
R=pathlib.Path(__file__).resolve().parents[1];RUN=R/'src/ForeverThai';BASE=R/'work/private-main21-r1/ForeverThai-0.466.0-cloud-main21-r1-PRIVATE-TEST.zip';sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(BASE.read_bytes())=='279efca27ec2b9a96743cfc39a8512d846ac9e055b527e53fb9dc2371ce157d5'
with zipfile.ZipFile(BASE) as z:
 prior=z.read('ForeverThai/Atlas.lua');assert (RUN/'Atlas.lua').read_bytes().startswith(prior);fonts=[n for n in z.namelist() if '/Fonts/' in n];assert len(fonts)==108
 for n in fonts:assert (R/'src'/n).read_bytes()==z.read(n),n
 protected=[n for n in z.namelist() if '/Skills/' in n or '/Fonts/Skills' in n or n.endswith('/Sarabun-Regular.ttf')];assert len(protected)==28
 for n in protected+['ForeverThai/Speech.lua','ForeverThai/Tracker.lua','ForeverThai/Match.lua']:assert (R/'src'/n).read_bytes()==z.read(n),n
 newpages=sorted(p for p in (RUN/'Fonts').glob('Thai*.tga') if 'ForeverThai/Fonts/'+p.name not in z.namelist())
assert [p.name for p in newpages]==['Thai94.tga','Thai95.tga','Thai96.tga','Thai97.tga']
fixturepath=R/'tests/recovered_npc/check_speech_v04230.py';assert sha(fixturepath.read_bytes())=='bdcf2ff10c973ab90cd372cfbd8f9416805f1fb0167be0d3e2d8a08193977b58';parsed=ast.parse(fixturepath.read_text());fixture=next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fixture' for t in n.targets));l=LuaRuntime(unpack_returned_tuples=True);l.execute(fixture);a=l.table();old=l.table();l.execute(prior.decode(),'ForeverThai',old)
for n in ['Atlas','Bitmap']:l.execute((RUN/f'{n}.lua').read_text(),'ForeverThai',a)
fields=[f for n in [1,2,3] for f in json.loads((R/f'evidence/main24-proposal0{n}.json').read_text())['fields']];assert len(fields)==122
missing_before={s for f in fields for s in re.findall(r'[\u0e00-\u0e7f]+',f['thai']) if old.runs[s] is None};images={}
for p in newpages:
 im=Image.open(p);im.load();assert im.mode=='RGBA' and im.size==(1024,1024) and im.getchannel('A').getextrema()==(0,255);images[int(re.search(r'\d+',p.name)[0])]=im
for s in missing_before:
 assert a.runs[s] is not None
 for _,idx in a.runs[s].items():
  g=a.glyphs[idx];pg,x,y,w=int(g[1]),int(g[2]),int(g[3]),int(g[4]);h=int(g[7] or 56);assert pg in images and min(x,y)>=0 and x+w<=1024 and y+h<=1024;assert images[pg].getchannel('A').crop((x,y,x+w,y+h)).getbbox() is not None
for key,v in old.runs.items():assert [x for _,x in v.items()]==[x for _,x in a.runs[key].items()],key
for key,v in old.glyphs.items():assert [x for _,x in v.items()]==[x for _,x in a.glyphs[key].items()],key
painted=latin=0
for f in fields:
 text=f['thai'];runs=re.findall(r'[\u0e00-\u0e7f]+',text)
 for s in runs:assert a.runs[s] is not None,s
 layer,draw=a.BitmapLayer(l.globals().UIParent,'TOPLEFT',0,0,484,18);assert draw(text,1,1,1)>0 and layer.visible
 for _,label in layer.labels.items():
  if label.visible:assert not re.search(r'[\u0e00-\u0e7f]',label.text or ''),'Thai livefont fallback'
 painted+=1;latin+=not bool(runs)
r=dict(status='PASSED_AFFECTED122_BITMAP_AND_FONT_PRESERVATION',baseline_artifact='d9208f6710ef3867d3dd728c1db52055185fd009',baseline_zip_sha256=sha(BASE.read_bytes()),old_Atlas_prefix_sha256=sha(prior),old_font_assets_exact_bytes_preserved=len(fonts),protected_assets_exact_bytes_preserved=len(protected),old_runs_preserved=sum(1 for _ in old.runs.items()),old_glyph_slots_preserved=len(old.glyphs),new_Thai_runs=len(missing_before),new_glyph_slots=len(a.glyphs)-len(old.glyphs),new_font_pages=[dict(path='Fonts/'+p.name,bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in newpages],actual_BitmapLayer_field_draws=painted,Thai_rendered_fields=painted-latin,propername_Latin_passthrough_fields=latin,Thai_font_fallbacks=0,font_ready=True,Catalog_sha256=sha((RUN/'Catalog.lua').read_bytes()),Atlas_sha256=sha((RUN/'Atlas.lua').read_bytes()),font_helper_sha256=sha((R/'tools/append_fonts.py').read_bytes()),runtime_engine_changed=False,old_NPC_Skill_party_suites_rerun=False,real_game_verified=False)
(R/'evidence/font-readiness24.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
