"""Actual immutable artifact download-back;no game,Launcher execution or installation."""
import pathlib,json,urllib.request,zipfile,hashlib,shutil,time
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.474.0';t=time.perf_counter()
SOURCE='70f937a8c0c93630a64535a4fe3e05410322584e';TREE='4309643829a566b90045630663b0c2687ae516c7';ARTIFACT='541ebd47868a1ce13517c2cfa546ea5c467be164'
d=json.loads((O/'github-runtime-tree.json').read_text(encoding='utf8'));assert d['sha']==TREE and not d['truncated']
actual={v['path'][len('src/'):]:v['sha'] for v in d['tree'] if v['type']=='blob' and v['path'].startswith('src/ForeverThai/')}
receipt=json.loads((O/'receipt.json').read_text(encoding='utf8'))
with zipfile.ZipFile(O/receipt['zip']['path']) as z:
 expected={}
 for n in z.namelist():
  b=z.read(n);expected[n]=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert len(actual)==len(expected)==164 and actual==expected
source=dict(status='PASSED_ALL164_COMMITTED_RUNTIME_BLOBS_EQUAL_VERIFIED_ZIP',source_commit=SOURCE,source_tree=TREE,files=164,game_verified=False)
(O/'github-source-tree-check.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf8')
names=[receipt['zip']['path'],'INSTALL-0.474.0-TH.txt']+receipt['preview_files'];checks=[]
for n in names:
 with urllib.request.urlopen(f'https://raw.githubusercontent.com/cryptokao/foreverthai-updates/{ARTIFACT}/output/{n}',timeout=45) as response:b=response.read()
 assert b==(O/n).read_bytes();checks.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),download_back_exact_bytes=True))
assert checks[0]['bytes']==29967987 and checks[0]['sha256']=='d6541f6daf107d54fd88564299cc480b52ebb3ed7203f417850b13ac1198fb95'
delivery=dict(status='PRIVATE0474_MAIN38_DELIVERED_DOWNLOAD_BACK_VERIFIED',artifact_commit=ARTIFACT,source_commit=SOURCE,checks=checks,all164_source_runtime_blobs_equal_ZIP=True,protected_Skill_font_assets_preserved=28,old_fonts_preserved=117,new_word_bitmaps=79,new_Thai_fields=67,verbatim_reviewed_reuse=15,new_supported_fields=82,quest_ids=28,complete_quests_claimed=0,current_enabled_inventory_proven=False,real_Windows_MacM2_acceptance=False,launcher_published=False,elapsed_wall_seconds=time.perf_counter()-t)
(O/'delivery-receipt.json').write_text(json.dumps(delivery,indent=2)+'\n',encoding='utf8')
dst=pathlib.Path('C:/Users/Mos/Documents/ChatGPT/Alpha WoW/outputs/ForeverThai-0.474.0-PRIVATE-TEST');dst.mkdir(parents=True,exist_ok=True)
for n in names+['receipt.json','manifest.json','font-plan.json','github-source-tree-check.json','delivery-receipt.json']:shutil.copyfile(O/n,dst/n)
print(json.dumps(source));print(json.dumps(delivery,indent=2))
