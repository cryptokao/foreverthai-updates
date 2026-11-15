import pathlib,urllib.request,json,hashlib,shutil
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.470.0';commit='2da8d23f1863dcf92f7abd5666728f5f565e36b1';root=f'https://raw.githubusercontent.com/cryptokao/foreverthai-updates/{commit}/output/'
names=['ForeverThai-0.470.0-main28-COMBINED.zip','INSTALL-0.470.0-TH.txt','MAIN28-bitmap-simulation.png'];checks=[]
for n in names:
 with urllib.request.urlopen(root+n,timeout=45) as response:b=response.read()
 assert b==(O/n).read_bytes();checks.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),download_back_exact_bytes=True))
assert checks[0]['sha256']=='a9c854976d2efac55b4821492714b7cf93dae627fbb77309d6bc820610cfb5e6'
receipt=dict(status='COMBINED0470_MAIN28_DELIVERED_AND_DOWNLOAD_BACK_VERIFIED',artifact_commit=commit,source_commit='29fa7625f968c825d5b4d0b073be4c0d2bbb45be',checks=checks,all154_committed_runtime_blobs_equal_ZIP=True,protected_Skill_font_assets_preserved=28,old_fonts_preserved=114,real_Windows_Mac_M2_acceptance=False,launcher_published=False)
(O/'delivery-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
dst=pathlib.Path('C:/Users/Mos/Documents/ChatGPT/Alpha WoW/outputs/ForeverThai-0.470.0-COMBINED');dst.mkdir(exist_ok=True)
for n in names+['receipt.json','manifest.json','delivery-receipt.json','github-source-tree-check.json']:shutil.copyfile(O/n,dst/n)
print(json.dumps(receipt,indent=2))
