"""Bounded current public capture queue; pin indexes/hashes, omit player bodies."""
import collections,hashlib,json,pathlib
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];l=LuaRuntime(unpack_returned_tuples=True);a=l.table();load=l.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for name in ['Catalog','Match']:load((ROOT/f'src/ForeverThai/{name}.lua').read_text(),a)
l.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
batch=json.loads((ROOT/'evidence/public-literals-10.json').read_text());held={(v['issue'],v['line_index']) for v in batch['held_current_source_slots']};seen=set();counts=collections.Counter();remaining=[];pins={}
for number in range(3419,3426):
 raw=(ROOT/f'work/issue-{number}-decoded.json').read_bytes();doc=json.loads(raw);assert doc['build']=='70888';pins[str(number)]=dict(url=f'https://github.com/quinn-dougherty/forever-vo/issues/{number}',decoded_sha256=hashlib.sha256(raw).hexdigest())
 for index,record in enumerate(doc['lines']):
  kind=record.get('k');text=record.get('x','')
  if kind not in ['gossip','book']:continue
  key=(kind,record.get('n'),record.get('t'),record.get('p'),text)
  if key in seen:continue
  seen.add(key);identity=dict(issue=number,line_index=index,kind=kind,npc_id=record.get('n'),book_title=record.get('t') if kind=='book' else None,page=record.get('p'),english_sha256=hashlib.sha256(text.encode()).hexdigest())
  if not text.strip():status='blank_no_prose';action='Do not translate whitespace.'
  elif (number,index) in held:status='held_literal_player_name';action='Need exact typed source template or independently qualified player-name binding for this own-ID/title/page. Player body intentionally omitted.'
  elif '$' in text:
   status='normalized_tokens_need_typed_or_literal_current_source';action='Do not replace token by uploader class/race/name. Match to own-ID explicit source template or get unredacted literal/full body plus independent binding evidence.'
  elif kind=='gossip':
   try:n=int(record.get('n',''))
   except ValueError:n=0
   entry=(a.objects if n<0 else a.npcs)[abs(n)];supported=a.TranslateNpc(entry,text) is not None;status='supported_exact_literal' if supported else 'unmatched_literal_review';action='Preserve exact body/own-ID binding.' if supported else 'Review actual source and reuse before translation.'
  else:
   book=a.books[record.get('t')];entry=book[record.get('p')] if book else None;supported=a.Translate(entry,text) is not None;status='supported_exact_literal' if supported else 'unmatched_literal_review';action='Preserve exact title/page/body.' if supported else 'Compare full body across title/page aliases before translation.'
  counts[status]+=1
  if status not in ['supported_exact_literal','blank_no_prose']:remaining.append(dict(**identity,status=status,next_action=action))
result=dict(scope='Unique supporting text records only in pinned public issues3419–3425, build70888. Normalized-token records are NOT asserted untranslated: some canonical forms already work. Not whole-game/playable denominator or game proof.',source_pins=pins,unique_source_records=len(seen),counts=dict(counts),literal_remaining_actionable=sum(v['status']=='unmatched_literal_review' for v in remaining),records=remaining)
(ROOT/'evidence/public-supporting-remaining10.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['records','source_pins']},indent=2))
