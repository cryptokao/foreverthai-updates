"""All154 committed runtime Git blobs must equal the already-verified current ZIP."""
import pathlib,urllib.request,json,zipfile,hashlib
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.470.0'
with urllib.request.urlopen('https://api.github.com/repos/cryptokao/foreverthai-updates/git/trees/ba79809c2ff5df21d083adf9d785894e093d32e7?recursive=1',timeout=30) as r:d=json.load(r)
assert not d['truncated'];actual={v['path'][len('src/'):]:v['sha'] for v in d['tree'] if v['type']=='blob' and v['path'].startswith('src/ForeverThai/')}
with zipfile.ZipFile(O/'ForeverThai-0.470.0-main28-COMBINED.zip') as z:
 expected={}
 for n in z.namelist():
  b=z.read(n);expected[n]=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert len(actual)==len(expected)==154 and actual==expected
r=dict(status='PASSED_ALL154_COMMITTED_RUNTIME_BLOBS_EQUAL_VERIFIED_ZIP',source_commit='29fa7625f968c825d5b4d0b073be4c0d2bbb45be',source_tree='ba79809c2ff5df21d083adf9d785894e093d32e7',files=154,game_verified=False)
(O/'github-source-tree-check.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(r))
