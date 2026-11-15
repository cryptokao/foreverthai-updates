"""Verify immutable committed runtime and actual downloadable private artifact;no game/Launcher installation."""
import pathlib,json,urllib.request,zipfile,hashlib,shutil
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.472.0'
SOURCE='fb0d057adc39d1432ecc77919ad97ea027f39b8a';TREE='7a86b614529eebb31b0fee5e20127c41533ae48b';ARTIFACT='7f6a1e6b04d0ea95fc99bd8ab39878d13e8ddfae'
with urllib.request.urlopen(f'https://api.github.com/repos/cryptokao/foreverthai-updates/git/trees/{TREE}?recursive=1',timeout=30) as response:d=json.load(response)
assert not d['truncated']
actual={v['path'][len('src/'):]:v['sha'] for v in d['tree'] if v['type']=='blob' and v['path'].startswith('src/ForeverThai/')}
with zipfile.ZipFile(O/'ForeverThai-0.472.0-main35-PRIVATE-TEST.zip') as z:
 expected={}
 for n in z.namelist():
  b=z.read(n);expected[n]=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert len(actual)==len(expected)==158 and actual==expected
source=dict(status='PASSED_ALL158_COMMITTED_RUNTIME_BLOBS_EQUAL_VERIFIED_ZIP',source_commit=SOURCE,source_tree=TREE,files=158,game_verified=False)
(O/'github-source-tree-check.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf8')
names=['ForeverThai-0.472.0-main35-PRIVATE-TEST.zip','INSTALL-0.472.0-TH.txt','MAIN35-bitmap-simulation.png'];checks=[]
for n in names:
 with urllib.request.urlopen(f'https://raw.githubusercontent.com/cryptokao/foreverthai-updates/{ARTIFACT}/output/{n}',timeout=45) as response:b=response.read()
 assert b==(O/n).read_bytes();checks.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),download_back_exact_bytes=True))
assert checks[0]['sha256']=='3b6f10f8519c625f4897840e17aabdd908ef6ab1ae753f3ab01daddd52f0cebc' and checks[0]['bytes']==29776055
receipt=dict(status='PRIVATE0472_MAIN35_DELIVERED_DOWNLOAD_BACK_VERIFIED',artifact_commit=ARTIFACT,source_commit=SOURCE,checks=checks,all158_source_runtime_blobs_equal_ZIP=True,protected_Skill_font_assets_preserved=28,old_fonts_preserved=115,new_word_bitmaps=3,new_Thai_fields=4,new_supported_fields=4,complete_quests_claimed=0,real_Windows_MacM2_acceptance=False,launcher_published=False)
(O/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
dst=pathlib.Path('C:/Users/Mos/Documents/ChatGPT/Alpha WoW/outputs/ForeverThai-0.472.0-PRIVATE-TEST');dst.mkdir(parents=True,exist_ok=True)
for n in names+['receipt.json','manifest.json','font-plan.json','github-source-tree-check.json','delivery-receipt.json']:shutil.copyfile(O/n,dst/n)
print(json.dumps(source));print(json.dumps(receipt,indent=2))
