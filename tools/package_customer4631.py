"""Complete customer0.463.1; only approved exact build gates and TOC metadata change."""
import hashlib,json,pathlib,re,subprocess,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1];RUN=ROOT/'src/ForeverThai';OUT=ROOT/'work/customer4631';OUT.mkdir(exist_ok=True);base=json.loads((ROOT/'evidence/private-package-manifest15.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();manifest={str(p.relative_to(ROOT/'src')):sha(p.read_bytes()) for p in sorted(RUN.rglob('*')) if p.is_file()};assert len(manifest)==138 and set(manifest)==set(base['runtime_manifest']);changed=sorted(n for n,h in manifest.items() if h!=base['runtime_manifest'][n]);assert changed==['ForeverThai/ForeverThai.toc','ForeverThai/Skills/Core.lua','ForeverThai/Speech.lua']
for name in changed:
 old=subprocess.check_output(['git','-C',str(ROOT),'show',base['runtime_git_tree']+':'+name.split('/',1)[1]]);expected=old.replace(b'## Version: 0.462.0',b'## Version: 0.463.1') if name.endswith('.toc') else old.replace(b'(build == "70862" or build == "70888")',b'(build == "70862" or build == "70888" or build == "70938")');assert (ROOT/'src'/name).read_bytes()==expected
artifact='ForeverThai-0.463.1.zip';path=OUT/artifact
with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in manifest:
  info=zipfile.ZipInfo(name,date_time=(2026,11,13,0,0,0));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(ROOT/'src'/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
m=dict(artifact=artifact,version='0.463.1',schema=1,sha256=sha(path.read_bytes()),bytes=path.stat().st_size,files=138,runtime_manifest=manifest,changed_from_candidate15=changed,unchanged_candidate15_files=135,approved_protected_delta='Skills/Core.lua exact70938allowlist addition; all27other protected assets unchanged',new_translations=0,includes_main13_and15=True,customer_feed_switched=False,public_download_url='https://foreverthai-download.yukimikulovelove2.chatgpt.site/ForeverThai-0.463.1.zip')
(OUT/'package-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({k:v for k,v in m.items() if k!='runtime_manifest'},indent=2))
