"""Read only pinned JSON snapshots; never execute third-party pullers/converters."""
import collections,csv,hashlib,json,pathlib,subprocess,re
from lupa.lua51 import LuaRuntime
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT/'work/forever-quests';PIN='9f4c5aac2d077854d7f4a2bdc2f8eceb8d7b23af';OUT=ROOT/'evidence';sha=lambda b:hashlib.sha256(b).hexdigest();show=lambda p:subprocess.check_output(['git','-C',str(REPO),'show',PIN+':'+p])
manifest=json.loads(show('manifest.json'));raw=show('data/quests.json');entry=next(v for v in manifest['files'] if v['path']=='data/quests.json');assert len(raw)==entry['bytes'] and sha(raw)==entry['sha256'];main=json.loads(raw)
fdbraw=show('foreverdb/data/quests.json');fdb=json.loads(fdbraw);meta=json.loads(show('foreverdb/data/meta.json'));assert len(main)==manifest['questCount']==4630 and len(fdb)==meta['quest_count']==3862
lua=LuaRuntime(unpack_returned_tuples=True);addon=lua.table();load=lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')
for n in ['Catalog','Match']:load((ROOT/'src/ForeverThai'/f'{n}.lua').read_text(),addon)
lua.execute('UnitName=function()return "CloudTester"end;UnitClass=function()return "Druid","DRUID"end;UnitRace=function()return "Night Elf"end')
runtime={int(q) for q,_ in addon.quests.items()};union={int(x['quest_id']) for x in csv.DictReader((OUT/'source-id-union.csv').open())};query=json.loads((ROOT/'work/eg/data/wowf/1.60.1.70888/quests.enUS.json').read_text())['quests'];rows=[];counts=collections.Counter()
for q,v in main.items():
 for field,k,native_key in [('title','name','title'),('objective','objectivesText','objectivesText')]:
  text=v.get(k)
  if not text:continue
  text='\n'.join(text) if isinstance(text,list) else text
  if not text.strip():continue
  native=query.get(q,{});current=native.get(native_key);e=addon.quests[int(q)][field] if int(q) in runtime else None
  if text.strip().lower() in ['null','description','log']:status='hold_placeholder_not_quest_prose'
  elif current is None:status='hold_no_current_own_id_field'
  elif ' '.join(text.split())!=' '.join(current.split()):status='hold_differs_from_current_own_id_text'
  else:status='same_as_current_own_id_text'
  counts[status]+=1
  if e is None or status!='same_as_current_own_id_text':rows.append(dict(quest_id=int(q),level=v.get('questLevel'),field=field,source_text_sha256=sha(text.encode()),current_text_sha256=sha(current.encode()) if current else None,runtime_field_present=e is not None,status=status,source_name=v.get('name'),current_name=native.get('title'),current_query_path='data/wowf/1.60.1.70888/quests.enUS.json'))
summary=dict(source_repository='https://github.com/tyler3497/forever-quests',source_commit=PIN,main=dict(records=len(main),sha256=sha(raw),license='GPL-3.0',objectives_field_records=sum(bool(v.get('objectivesText')) for v in main.values()),outside_catalog=sorted(set(map(int,main))-runtime),outside_prior_union=sorted(set(map(int,main))-union),live_verification=False),foreverdb=dict(records=len(fdb),sha256=sha(fdbraw),build=meta['api_meta']['build'],meta_quest_count=meta['api_meta']['quests'],credit='Data from ForeverDB.net',credit_url='https://foreverdb.net',source_kinds=dict(collections.Counter(v.get('source') for v in fdb.values())),outside_catalog=sorted(set(map(int,fdb))-runtime),outside_prior_union=sorted(set(map(int,fdb))-union),full_quest_prose_fields=sum(any(k in v for k in ['description','details','objectivesText','progress','completion']) for v in fdb.values()),coverage='3862 list records are not meta6614 or a whole-game denominator; knownInForever/classic fallback flags are not live proof.'),comparison_counts=dict(counts),missing_runtime_fields=[x for x in rows if not x['runtime_field_present']],conclusion='No new IDs outside Catalog or previous union from either snapshot. Historical missing-objective candidates5641/5679 have renamed current query records (Chastise/Dark Sacrifice), no current objective and questType0; do not copy obsolete priest travel text. Four null objectives are placeholders, not translations. Other differences remain pinned historical-vs-current source comparisons, not automatic aliases.',new_translations=0,new_current_playable_ids_proven=0,network_policy_changed=False,third_party_scripts_executed=False)
(OUT/'additional-source-audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');(OUT/'additional-source-field-differences.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(OUT/'third-party/forever-quests-GPL-3.0.txt').write_bytes(show('LICENSE.md'));(OUT/'third-party/SOURCE-CREDITS.txt').write_text('Audit inputs only; no snapshot is merged into runtime.\nMain data: tyler3497/forever-quests, pin '+PIN+', GPL-3.0.\nDerived from QuestieDB, TrinityCore Forever and NorgannonDB as described in upstream README/manifest.\nSeparate ForeverDB snapshot: Data from ForeverDB.net (https://foreverdb.net), build1.60.1.70707, 3862 listed IDs; API meta6614 is not coverage.\nHistorical/emulation records and Classic fallbacks do not prove current Forever text or playability.\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
