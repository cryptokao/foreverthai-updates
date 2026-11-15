import pathlib,urllib.request,json,hashlib,shutil
R=pathlib.Path(__file__).resolve().parent;O=R/'build-0.471.0';commit='648d283e9a1f571c68c7d6421b3b209c8f370e38';root=f'https://raw.githubusercontent.com/cryptokao/foreverthai-updates/{commit}/output/'
names=['ForeverThai-0.471.0-main33-PRIVATE-TEST.zip','INSTALL-0.471.0-TH.txt','MAIN33-bitmap-simulation.png'];checks=[]
for n in names:
 with urllib.request.urlopen(root+n,timeout=45) as response:b=response.read()
 assert b==(O/n).read_bytes();checks.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),download_back_exact_bytes=True))
assert checks[0]['sha256']=='54eef1b1fb33379332d8bfe5621d166e9bc77f9fe5931cdf510efbfd782b5077'
receipt=dict(status='PRIVATE-TEST0471_MAIN33_DELIVERED_AND_DOWNLOAD_BACK_VERIFIED',artifact_commit=commit,source_commit='c994dda2b977252a1d6f46cac23722ee30d4023e',checks=checks,all155_committed_runtime_blobs_equal_ZIP=True,protected_Skill_font_assets_preserved=28,old_fonts_preserved=115,real_Windows_Mac_M2_acceptance=False,launcher_published=False)
(O/'delivery-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
dst=pathlib.Path('C:/Users/Mos/Documents/ChatGPT/Alpha WoW/outputs/ForeverThai-0.471.0-PRIVATE-TEST');dst.mkdir(exist_ok=True)
for n in names+['receipt.json','manifest.json','delivery-receipt.json','github-source-tree-check.json']:shutil.copyfile(O/n,dst/n)
print(json.dumps(receipt,indent=2))
