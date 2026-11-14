"""Incremental new-issue audit only; no unchanged full inventory/Harvest/test rerun."""
import collections,datetime,hashlib,json,pathlib,re,subprocess
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();lua=LuaRuntime(unpack_returned_tuples=True);a=lua.table();load=lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
# Freeze the comparison to verified candidate11, so a later own-ID reuse addition
# does not silently change this source-audit snapshot.
manifest=json.loads((ROOT/'evidence/private-package-manifest11.json').read_text());tree=manifest['runtime_git_tree']
for n in ['Catalog','Match']:
 data=subprocess.check_output(['git','-C',str(ROOT),'show',tree+':'+n+'.lua']);assert sha(data)==manifest['runtime_manifest']['ForeverThai/'+n+'.lua'];load(data.decode(),a)
lua.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end');query=json.loads((ROOT/'work/eg/data/wowf/1.60.1.70888/quests.enUS.json').read_text())['quests'];seen=set();counts=collections.Counter();records=[];pins=[]
for no in [3426,3427,3428]:
 path=ROOT/f'work/issue-{no}.json';raw=path.read_bytes();issue=json.loads(raw);decoded=(ROOT/f'work/issue-{no}-decoded.json').read_bytes();doc=json.loads(decoded);assert doc['build']=='70888' and doc['locale']=='enUS';pins.append(dict(issue=no,url=f'https://github.com/quinn-dougherty/forever-vo/issues/{no}',created_at=issue['created_at'],updated_at=issue['updated_at'],issue_json_sha256=sha(raw),body_sha256=sha(issue['body'].encode()),decoded_sha256=sha(decoded),build=doc['build'],locale=doc['locale'],lines=len(doc['lines'])))
 for index,v in enumerate(doc['lines']):
  kind=v.get('k');text=v['x'];key=(kind,v.get('q'),v.get('n'),v.get('t'),v.get('p'),v.get('e'),text)
  if key in seen:continue
  seen.add(key);field=None;info={}
  if kind=='quest':
   field={'accept':'description','complete':'completion','progress':'progress'}[v['e']];quest=a.quests[v['q']];entry=quest[field] if quest else None;translate=lambda s:a.Translate(entry,s);info=query.get(str(v['q']),{});canonical=entry is not None
  elif kind=='gossip':
   nid=int(v['n']);npc=(a.objects if nid<0 else a.npcs)[abs(nid)];translate=lambda s:a.TranslateNpc(npc,s);canonical=npc is not None
  elif kind=='book':
   book=a.books[v['t']];entry=book[v['p']] if book else None;translate=lambda s:a.Translate(entry,s);canonical=entry is not None
  else:raise AssertionError(kind)
  if not text.strip():status='blank_no_prose'
  elif translate(text) is not None:status='exact_supported'
  elif '$' in text:
   rendered=text
   for t,z in [('N','CloudTester'),('n','CloudTester'),('C','Druid'),('c','Druid'),('R','Night Elf'),('r','Night Elf')]:rendered=rendered.replace('$'+t,z)
   status='normalized_diagnostic_supported' if translate(rendered) is not None else 'held_unproven_typed_source_variant'
  else:status='literal_reuse_review'
  counts[kind+':'+status]+=1
  if status in ['held_unproven_typed_source_variant','literal_reuse_review']:
   row=dict(issue=no,source_line_index=index,kind=kind,field=field,quest_id=v.get('q'),npc_id=v.get('n'),book_title=v.get('t') if kind=='book' else None,page=v.get('p'),level=info.get('level'),title=info.get('title'),english=text,english_sha256=sha(text.encode()),status=status,runtime_canonical_or_npc_present=canonical,source_record=v)
   if status=='literal_reuse_review':
    matches=[]
    for nid,npc in a.npcs.items():
     thai=a.TranslateNpc(npc,text)
     if thai:matches.append(dict(npc_id=int(nid),npc_name=npc.name,thai=thai))
    row['full_body_reuse_matches']=sorted(matches,key=lambda x:x['npc_id']);row['new_prose']=False if matches else None;row['next_action']='Reuse an independently reviewed full-body translation for exact own-ID binding; add focused tests, no font rebuild if existing runs.'
   else:row['next_action']='Need exact current own-ID/title/page full body plus independently typed name/class/race binding. Do not infer from uploader identity or similar old wording; preserve existing canonical.'
   records.append(row)
result=dict(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),compared_runtime_tree=tree,source_heads=dict(EG='164bd1e2d89579ada4ee5e2de7e5fd4db684a9f1',ForeverVO='d562be626b9970fa8575170950ff61076dc47df0',QuestieDB='a444a6418113ae0fce5d30c897674132e756ba1d',additional_forever_quests='9f4c5aac2d077854d7f4a2bdc2f8eceb8d7b23af'),source_heads_unchanged=True,source_pins=pins,input_records=sum(v['lines'] for v in pins),unique_records=len(seen),counts=dict(counts),literal_source_ready_records=sum(v['status']=='literal_reuse_review' for v in records),new_prose_ready=0,held_new_source_variants=sum(v['status']=='held_unproven_typed_source_variant' for v in records),scope='Only new public issues3426–3428 since3425, not a playable/full-game denominator. Diagnostic rendering does not establish typed binding or new coverage; canonical support and held source variants are distinct.',records=records)
(ROOT/'evidence/new-capture-audit12.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['records','source_pins']},indent=2))
