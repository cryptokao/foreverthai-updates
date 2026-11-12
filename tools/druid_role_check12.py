"""Bounded two-hold corroboration: historical raw roles vs current Forever words.
Read literal SQL/Lua data without executing it; never manufacture a C template.
"""
import argparse,hashlib,json,pathlib,re,subprocess,urllib.request
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();pins=json.loads((ROOT/'tests/source_inputs/druid-role-pins12.json').read_text());parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--download',action='store_true');args=parser.parse_args();data=[]
for i,p in enumerate(pins):
 path=ROOT/f'work/druid-primary-exact-{i}.txt'
 if args.download:path.write_bytes(urllib.request.urlopen(p['raw_url']).read())
 raw=path.read_bytes();assert len(raw)==p['bytes'] and sha(raw)==p['sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==p['git_blob'];data.append(raw.decode())
sql=data[0];line=next(v for v in sql.splitlines() if v.startswith("('4721',"));body=re.match(r"\('4721','((?:\\.|[^'])*)'",line)[1].replace('$B','\n');assert '$c' not in body.lower() and 'young druid.' in body
for exact in ['UPDATE creature_template set gossip_menu_id=3882 WHERE entry=11956;',"('3882','0','0','What do you represent, spirit?','1','1','3881'","('3881','4721','0','0')"]:assert exact in sql
mail={}
for line in data[1].splitlines():
 match=re.match(r'\s*\{ (\d+), ("(?:\\.|[^"\\])*") \}',line)
 if match and match[1] in ['112','116']:mail[int(match[1])]=json.loads(match[2])
assert len(mail)==2 and 'Mathrengyl Bearwalker' in mail[112] and 'young druid!' in mail[112] and '$c' not in mail[112].lower()
new=json.loads((ROOT/'evidence/new-capture-audit12.json').read_text());npc=next(v for v in new['records'] if v.get('npc_id')=='11956');book=next(v for v in new['records'] if v.get('book_title')=='Plain Letter');normal=lambda s:re.sub(r'[ \t\r\n\f\v]+',' ',s).strip();assert normal(body)==normal(npc['english'].replace('$c','druid'));assert normal(mail[112])==normal(book['english'].replace('$c','druid'));assert normal(mail[116])!=normal(mail[112])
# A prior literal Forever body exists independently of the Classic raw table.
path=ROOT/'work/forever-vo/tools/data/capture.json';capture=json.loads(path.read_text());key='11956|2c9200b5';old=capture['gossip'][key];assert old['build']=='70790' and old['npc']=='11956' and '$' not in old['text'];assert normal(old['text'])==normal(body)
manifest=json.loads((ROOT/'evidence/private-package-manifest11.json').read_text());tree=manifest['runtime_git_tree'];lua=LuaRuntime();a=lua.table()
for name in ['Catalog','Match']:
 raw=subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+name+'.lua']);assert sha(raw)==manifest['runtime_manifest']['ForeverThai/'+name+'.lua'];lua.execute(raw.decode(),'ForeverThai',a)
positive=negative=0
for klass,cid in [('Druid','DRUID'),('Mage','MAGE')]:
 lua.globals().klass=klass;lua.globals().cid=cid;lua.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return klass,cid end;UnitRace=function()return "Night Elf"end')
 assert a.TranslateNpc(a.npcs[11956],old['text']) is not None;positive+=1
 assert a.Translate(a.books['Plain Letter'][1],mail[112]) is not None;positive+=1
 assert a.TranslateNpc(a.npcs[11956],old['text'].replace('young druid.','young mage.')) is None;negative+=1
 assert a.Translate(a.books['Plain Letter'][1],mail[112].replace('young druid!','young mage!')) is None;negative+=1
report=dict(scope='Only11956andPlainLetterpage1 fresh holds; no runtime/Thai/font changes and no Classic words imported into Forever catalog.',primary_sources=pins,historical_npc_role=dict(npc_id=11956,gossip_entry=3882,option_target_menu=3881,npc_text_id=4721,role='literal druid, not a dynamic class token',full_body_sha256=sha(body.encode()),explicit_npc_menu_text_association=True,normalized_body_equal_if_capture_token_replaced_by_fixed_literal_for_comparison=True,current_server_role_proven=False),historical_letter_role=dict(table='MailTemplate',id=112,role='literal druid, no dynamic class token',full_body_sha256=sha(mail[112].encode()),author='Mathrengyl Bearwalker',location='Cenarion Enclave of Darnassus',level=14,normalized_body_equal_if_capture_token_replaced_by_fixed_literal_for_comparison=True,raw_source_title_page_item_association_proven=False,current_server_role_proven=False,distinct_same_family_record=116),current_forever_words=dict(new_source_refs=[dict(issue=v['issue'],line_index=v['source_line_index'],english_sha256=v['english_sha256'],build='70888') for v in [npc,book]],prior_literal_npc=dict(repository='quinn-dougherty/forever-vo',commit='d562be626b9970fa8575170950ff61076dc47df0',path=str(path.relative_to(ROOT/'work/forever-vo')),file_sha256=sha(path.read_bytes()),record_key=key,origin=old['origin'],build=old['build'],english_sha256=sha(old['text'].encode())),new_capture_tokens_are_role_proof=False,uploader_class_race_used_to_infer_role=False),existing_canonical_probe=dict(runtime_tree=tree,literal_positive_executions=positive,changed_class_word_negative_executions=negative,classes=['Druid','Mage'],interpretation='Both existing literal-druid bodies are already supported independently of current player class. NPC uses prior literal Forever70790 words; letter test uses historical raw body only to confirm an existing literal alias, NOT current70888 coverage or a new English source.'),decision='Keep both normalized70888$c role holds; no C/class expansion or invented literal current source. Historical raw records are fixed druid, and letter primary raw lacks current title/page/item association. Existing literal canonical translations stay intact.',new_prose=0,new_thai=0,runtime_changes=False,unchanged_suites_rerun=False)
(ROOT/'evidence/druid-role-check12.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Two historical raw literal-druid records verified; existing literals4positive/4negative. Both current normalized$c role holds retained; no runtime change.')
