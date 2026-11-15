"""Actual immutable artifact download-back;no game,Launcher execution or installation."""
import pathlib,json,urllib.request,zipfile,hashlib,shutil,time
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.475.0';t=time.perf_counter()
SOURCE='04f0ee8af33bae3af44d5dc8d9f1425ec720c60f';TREE='46843cedc75d6e54b277b2348cb311263cf710d2';ARTIFACT='a3ead232d7faf1cdb29f9b82a2775bd1e2430e28'
d=json.loads((O/'github-runtime-tree.json').read_text(encoding='utf8'));assert d['sha']==TREE and not d['truncated']
actual={v['path'][len('src/'):]:v['sha'] for v in d['tree'] if v['type']=='blob' and v['path'].startswith('src/ForeverThai/')}
receipt=json.loads((O/'receipt.json').read_text(encoding='utf8'))
with zipfile.ZipFile(O/receipt['zip']['path']) as z:
 expected={}
 for n in z.namelist():
  b=z.read(n);expected[n]=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert len(actual)==len(expected)==167 and actual==expected
source=dict(status='PASSED_ALL167_COMMITTED_RUNTIME_BLOBS_EQUAL_VERIFIED_ZIP',source_commit=SOURCE,source_tree=TREE,files=167,game_verified=False)
(O/'github-source-tree-check.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf8')
names=[receipt['zip']['path'],'INSTALL-0.475.0-TH.txt']+receipt['preview_files'];checks=[]
for n in names:
 with urllib.request.urlopen(f'https://raw.githubusercontent.com/cryptokao/foreverthai-updates/{ARTIFACT}/output/{n}',timeout=45) as response:b=response.read()
 assert b==(O/n).read_bytes();checks.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),download_back_exact_bytes=True))
assert checks[0]['bytes']==30002225 and checks[0]['sha256']=='a9ec2fd4de80f353bd56ad47775555608c00812e98f8289a3a1212d39147298e'
delivery=dict(status='PRIVATE0475_MAIN39_DELIVERED_DOWNLOAD_BACK_VERIFIED',artifact_commit=ARTIFACT,source_commit=SOURCE,checks=checks,all167_source_runtime_blobs_equal_ZIP=True,protected_Skill_font_assets_preserved=28,old_fonts_preserved=118,new_word_bitmaps=8,new_Thai_fields=5,verbatim_reviewed_reuse=9,new_supported_fields=14,quest_ids=11,complete_quests_claimed=0,current_enabled_inventory_proven=False,real_Windows_MacM2_acceptance=False,launcher_published=False,elapsed_wall_seconds=time.perf_counter()-t)
(O/'delivery-receipt.json').write_text(json.dumps(delivery,indent=2)+'\n',encoding='utf8')
dst=pathlib.Path.cwd()/'outputs/ForeverThai-0.475.0-PRIVATE-TEST';dst.mkdir(parents=True,exist_ok=True)
for n in names+['receipt.json','manifest.json','font-plan.json','github-source-tree-check.json','delivery-receipt.json']:shutil.copyfile(O/n,dst/n)
print(json.dumps(source));print(json.dumps(delivery,indent=2))
