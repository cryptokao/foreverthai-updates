"""One new exact quest progress field; privacy review and full-source Thai reuse only."""
import pathlib,json,hashlib,zipfile,re,sys
from lupa.lua51 import LuaRuntime,lua_type
sys.stdout.reconfigure(encoding='utf-8');R=pathlib.Path(__file__).resolve().parent
vs=json.loads((R/'main33-fvo-unmatched-private.json').read_text(encoding='utf-8'));f=next(x for x in vs if x['quest_id']==97928 and x['field']=='progress')
en=f['english'];assert en=='Yes, I can teach you.' and len(en.encode())==21 and not re.search(r'[$|{}<>]',en)
assert hashlib.sha256(en.encode()).hexdigest()==f['english_sha256']=='a30043e0d1efeade80eb35d6f08217fcdeca46af4bab10645e044bbd28f6127a'
b=en.encode();x=y=0
for c in b:x=(x*257+c)%2147483647;y=(y*131+c)%2147483629
sig=f'{len(b)}:{x}:{y}'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(R/'package-main28/build-0.470.0/ForeverThai-0.470.0-main28-COMBINED.zip') as z:
 for n in ['Catalog.lua','MainQuest2526.lua','MainQuest27.lua','MainQuest28.lua','Match.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
assert a.quests[97928] is not None and a.quests[97928].progress is None
reuse=[]
def walk(e,q,field,path):
 if lua_type(e)!='table':return
 ss=[e[1]] if isinstance(e[1],str) else [v for _,v in e[1].items()] if lua_type(e[1])=='table' else []
 if sig in ss and isinstance(e[2],str):reuse.append(dict(quest_id=q,field=field,path=path,thai=e[2],thai_sha256=hashlib.sha256(e[2].encode()).hexdigest()))
 if e.variants:
  for i,v in e.variants.items():walk(v,q,field,path+f'.variants[{i}]')
 if e.amount:walk(e.amount,q,field,path+'.amount')
for q,e in a.quests.items():
 for field in ['title','objective','description','progress','completion']:walk(e[field],int(q),field,field)
doc=json.loads((R/'main33-fvo-decoded-private.json').read_text(encoding='utf-8'));d=next(x for x in doc if x['issue']==3522);record=d['doc']['lines'][58]
assert record.get('q')==97928 and record.get('e')=='progress' and record.get('x')==en
meta=dict(batch='MAIN33',quest_id=97928,field='progress',title='Camping 101: Blacksmithing',level=6,english=en,english_sha256=f['english_sha256'],expected_dynamic_signature=sig,source_ref=dict(repository='quinn-dougherty/forever-vo',issue=3522,url='https://github.com/quinn-dougherty/forever-vo/issues/3522',line_index=58,phase='progress',payload_container_sha256=d['body_sha256'],decoded_sha256=d['raw_sha256']),corroborating_metadata=dict(repository='Questie/QuestieDB',pin='4dbb82440a27856f8dccf57094a5d792cdc7cc9b',path='src/corrections/Forever/traces/foreverQuestTraces.lua',blob='b458cb4e2f262c7fa84826beea463942b8ffb160',purpose='own-ID title/level,not a second progress-text source'),privacy_review=dict(full21ASCIIbytes_read=True,no_player_name_or_partial_name=True,no_dynamic_role_or_number=True,no_gender_condition_inferred=True),meaning_review='Yes/affirmation,first-person speaker is able to teach the addressee;no subject/skill/race/class/eligibility added.',reuse_candidates=reuse,source_NPC_name=record.get('n'),source_header_build=d['doc'].get('build'),per_row_build_or_current_enabled_inventory_proven=False,existing_canonical_progress_absent=True,complete_quests_claimed=0)
(R/'main33-literal-review-private.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in meta.items() if k!='source_NPC_name'},ensure_ascii=False,indent=2));print(json.dumps({'source_NPC_name':record.get('n')},ensure_ascii=False))
