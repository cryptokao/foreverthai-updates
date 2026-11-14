"""Build a complete private review ZIP; keep feed and runtime version unchanged."""
import hashlib,json,pathlib,sys,zipfile
root=pathlib.Path(__file__).resolve().parents[1];out=pathlib.Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);runtime=root/'src/ForeverThai';files=sorted(p for p in runtime.rglob('*') if p.is_file());assert len(files)>=126
manifest={str(p.relative_to(runtime.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};label=sys.argv[2] if len(sys.argv)>2 else 'batch05';assert label.replace('-','').isalnum();name=f'ForeverThai-0.462.0-cloud-through-{label}-PRIVATE-TEST.zip'
def write_zip(path,entries):
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for label,p in entries:
   info=zipfile.ZipInfo(label,date_time=(2026,11,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
write_zip(out/name,[(str(p.relative_to(runtime.parent)),p) for p in files])
with zipfile.ZipFile(out/name) as z:
 assert z.testzip() is None
 assert not any('/Dev/' in n or n.endswith(('/Capture.lua','/Discovery.lua')) for n in z.namelist())
 toc=z.read('ForeverThai/ForeverThai.toc').decode()
 paths=[v.strip().replace('\\','/') for v in toc.splitlines() if v.strip() and not v.startswith('#')]
 assert all('ForeverThai/'+v in z.namelist() for v in paths)
 assert set(z.namelist())==set(manifest)
 for label,digest in manifest.items():assert hashlib.sha256(z.read(label)).hexdigest()==digest
result={'artifact':name,'files':len(files),'bytes':(out/name).stat().st_size,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest(),'runtime_manifest':manifest,'private_review_only':True,'runtime_version':'0.462.0','customer_feed_changed':False}
(out/'package-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='runtime_manifest'},indent=2))
