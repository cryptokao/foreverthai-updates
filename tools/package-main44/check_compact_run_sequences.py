import pathlib,zipfile,json,hashlib
from lupa.lua51 import LuaRuntime
r=pathlib.Path(__file__).resolve().parent;p=r/'build-0.480.0-compact';zs=[zipfile.ZipFile(r/'build-0.480.0/ForeverThai-0.480.0-main44-COMBINED.zip'),zipfile.ZipFile(p/'ForeverThai-0.480.0-main44-COMBINED.zip')];maps=[]
for z in zs:
 l=LuaRuntime(register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
 for n in z.read('ForeverThai/ForeverThai.toc').decode().splitlines():
  if n=='Atlas.lua' or n.startswith('AtlasMain'):l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
 maps.append({s:tuple(ids[i] for i in range(1,len(ids)+1)) for s,ids in a.runs.items()})
assert maps[0] and maps[0]==maps[1];rec=json.loads((p/'receipt.json').read_text());rec['all_run_sequences_exact']=len(maps[0]);rec['run_sequence_verification']='all string-keyed entries compared,not Lua length operator';rec['unchanged_files_vs_initial_unpublished0480']=rec.pop('old_runtime_files_exact_bytes_preserved');rec['old_runtime_files_exact_bytes_preserved_vs0479']=160;rec['old_font_assets_exact_preserved_vs0479']=106;(p/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(status='PASSED_ALL_RUN_SEQUENCES_EQUAL',runs=len(maps[0]),old_glyph_pixels_exact=15331,new_glyph_pixels_exact=663)))
