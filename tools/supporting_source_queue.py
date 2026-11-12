"""Freeze the remaining current EG book/dialogue records against candidate07.
This is a bounded source queue, never a whole-game denominator or live proof.
"""
import hashlib,json,pathlib,subprocess,collections,re
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'work/eg/data/wowf/1.60.1.70888/texts.enUS.json';batch=json.loads((ROOT/'evidence/npc-gossip-08.json').read_text());assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==batch['source_file_sha256'];doc=json.loads(SOURCE.read_text());tree=batch['prior_runtime_git_tree'];l=LuaRuntime(unpack_returned_tuples=True);a=l.table();load=l.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for name in ['Catalog.lua','Match.lua']:load(subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+name]).decode(),a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
rows=[];ready={(v['npc_id'],v['field'],v['english']) for v in batch['fields']}
for kind in ['gossip','greeting','books']:
 for key,value in doc[kind].items():
  records=[(int(page),record['title'],text['text'],record) for page,record in value.items() for text in record['texts']] if kind=='books' else [(None,None,v['text'],v) for v in value]
  for page,title,text,record in records:
   oid=int(key.split(':')[1]);rendered=text.replace('$B','\n');entry=a.books[title] if kind=='books' else (a.npcs if key.startswith('npc:') else a.objects)[oid];entry=entry[page] if kind=='books' and entry else entry
   translate=(lambda: a.Translate(entry,rendered)) if kind=='books' else (lambda: a.TranslateNpc(entry,rendered))
   if not text.strip():status='blank_no_prose';action='Do not translate whitespace.'
   elif '$' in rendered:
    status='needs_exact_rendered_or_typed_formatter_evidence';action='Need own-ID exact rendered full body and independent binding/formatter evidence. Do not infer fixed troll/trainer/race references from normalized tokens.'
    if kind!='books' and record.get('template')=='broadcastText' and record.get('broadcastTextIds'):
     # Explicit typed source template, not normalized uploader tokens. Rendering
     # here is diagnostic matching only; no runtime entry or expected Thai generated.
     samples=[]
     for sex in [0,1]:
      sample=re.sub(r'\$g([^:;]*):([^;]*);',lambda m:m[sex+1],rendered)
      for token,value in {'n':'CloudTester','c':'Druid','r':'Night Elf'}.items():sample=sample.replace('$'+token,value)
      samples.append(sample)
     if all('$' not in sample and a.TranslateNpc(entry,sample) is not None for sample in samples):
      status='already_supported_explicit_broadcast_template';action='Both gender samples match existing own-ID translation after explicit token rendering. Diagnostic simulation, not live rendered-body proof; preserve.'
     else:status='actionable_explicit_broadcast_template_review';action='Review independent Thai and typed placeholder association from the exact broadcastText ID/template; compare old full bodies before adding.'
   elif translate() is not None:status='already_supported_literal';action='Preserve; no added translation.'
   elif (oid,kind,text) in ready:status='batch08_ready_literal';action='See independent English/Thai/reuse evidence and focused handler tests in npc-gossip-08.'
   else:status='unmatched_literal_next';action='Compare full body across all title/NPC aliases and review own-ID source before translation.'
   rows.append(dict(kind=kind,own_id=key,title=title,page=page,english=text,status=status,next_action=action,source_record=record))
result=dict(source_commit=batch['source_commit'],source_build=batch['source_build'],source_file_sha256=batch['source_file_sha256'],compared_runtime_tree=tree,counts=dict(collections.Counter(v['status'] for v in rows)),scope='All book/gossip/greeting records in this pinned current EG texts file only. Literal/$B checks are distinct from token rendering, no playable/full-game denominator. Existing supported raw normalized tokens are deliberately not counted as current rendered coverage.',records=rows)
(ROOT/'evidence/supporting-source-queue08.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['counts'],indent=2))
