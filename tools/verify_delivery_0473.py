"""Verify immutable committed runtime and actual downloadable private artifact;no game/Launcher installation."""
import pathlib,json,urllib.request,zipfile,hashlib,shutil
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.473.0'
SOURCE='26d2af8a7944ba7d2b4e9b984e93e005fd242629';TREE='20b6a7d5032c44530d6bc974ea16ac1ad575fde0';ARTIFACT='65d7757dfced38ef66fcc37ca959a423d1aca851'
d=json.loads((O/'github-runtime-tree.json').read_text(encoding='utf8'))
assert d['sha']==TREE
assert not d['truncated']
actual={v['path'][len('src/'):]:v['sha'] for v in d['tree'] if v['type']=='blob' and v['path'].startswith('src/ForeverThai/')}
with zipfile.ZipFile(O/'ForeverThai-0.473.0-main36-PRIVATE-TEST.zip') as z:
 expected={}
 for n in z.namelist():
  b=z.read(n);expected[n]=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert len(actual)==len(expected)==161 and actual==expected
source=dict(status='PASSED_ALL161_COMMITTED_RUNTIME_BLOBS_EQUAL_VERIFIED_ZIP',source_commit=SOURCE,source_tree=TREE,files=161,game_verified=False)
(O/'github-source-tree-check.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf8')
names=['ForeverThai-0.473.0-main36-PRIVATE-TEST.zip','INSTALL-0.473.0-TH.txt','MAIN36-bitmap-simulation.png'];checks=[]
for n in names:
 with urllib.request.urlopen(f'https://raw.githubusercontent.com/cryptokao/foreverthai-updates/{ARTIFACT}/output/{n}',timeout=45) as response:b=response.read()
 assert b==(O/n).read_bytes();checks.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),download_back_exact_bytes=True))
assert checks[0]['sha256']=='a606548c0b8877ca29fcee2bbca8919dba085ab166d87484e885982b27cb7add' and checks[0]['bytes']==29843848
receipt=dict(status='PRIVATE0473_MAIN36_DELIVERED_DOWNLOAD_BACK_VERIFIED',artifact_commit=ARTIFACT,source_commit=SOURCE,checks=checks,all161_source_runtime_blobs_equal_ZIP=True,protected_Skill_font_assets_preserved=28,old_fonts_preserved=116,new_word_bitmaps=33,new_Thai_fields=10,verbatim_reviewed_reuse=3,new_supported_fields_or_variants=13,quest_ids=8,complete_quests_claimed=0,real_Windows_MacM2_acceptance=False,launcher_published=False)
(O/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
dst=pathlib.Path('C:/Users/Mos/Documents/ChatGPT/Alpha WoW/outputs/ForeverThai-0.473.0-PRIVATE-TEST');dst.mkdir(parents=True,exist_ok=True)
for n in names+['receipt.json','manifest.json','font-plan.json','github-source-tree-check.json','delivery-receipt.json']:shutil.copyfile(O/n,dst/n)
print(json.dumps(source));print(json.dumps(receipt,indent=2))
