"""All155 committed runtime Git blobs must equal the already-verified current ZIP."""
import pathlib,urllib.request,json,zipfile,hashlib
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.471.0'
with urllib.request.urlopen('https://api.github.com/repos/cryptokao/foreverthai-updates/git/trees/e802163b5a18507cfb5de9f913eab01351a6cf85?recursive=1',timeout=30) as r:d=json.load(r)
assert not d['truncated'];actual={v['path'][len('src/'):]:v['sha'] for v in d['tree'] if v['type']=='blob' and v['path'].startswith('src/ForeverThai/')}
with zipfile.ZipFile(O/'ForeverThai-0.471.0-main33-PRIVATE-TEST.zip') as z:
 expected={}
 for n in z.namelist():
  b=z.read(n);expected[n]=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert len(actual)==len(expected)==155 and actual==expected
r=dict(status='PASSED_ALL155_COMMITTED_RUNTIME_BLOBS_EQUAL_VERIFIED_ZIP',source_commit='c994dda2b977252a1d6f46cac23722ee30d4023e',source_tree='e802163b5a18507cfb5de9f913eab01351a6cf85',files=155,game_verified=False)
(O/'github-source-tree-check.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(r))
