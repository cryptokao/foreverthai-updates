"""Full recovered NPC686 plus independent finite group-name event regression.
Run against a ZIP whose every byte matches current src; never relabel ZIP10.
"""
import argparse,collections,contextlib,hashlib,json,pathlib,re,zipfile
from lupa.lua51 import LuaRuntime
from npc_replay import verify_corpus,replay
ROOT=pathlib.Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=pathlib.Path,nargs='?');parser.add_argument('--source-debug',action='store_true');args=parser.parse_args();assert args.source_debug or args.archive;audit=json.loads((ROOT/'evidence/party-source-audit12.json').read_text());cases=json.loads((ROOT/'tests/speech-party-cases11.json').read_text())+json.loads((ROOT/'tests/speech-party-extra-cases12.json').read_text());assert len(cases)==16;corpus=json.loads((ROOT/'tests/npc_corpus/reviewed-0462.json').read_text());verify_corpus(corpus)
for row,case in zip(audit['qualified_templates'],cases):
 assert case['npc_id']==row['npc_id'] and case['event']==row['event'];assert case['english'].replace('Maelin','$N')==row['english'];assert case['thai'].replace('Maelin','{name}')==row['thai']
result=dict(candidate='current-src-debug' if args.source_debug else args.archive.name,candidate_sha256=None if args.source_debug else sha(args.archive.read_bytes()),qualified_unique_source_templates=16,qualified_npcs=7,additional_static_cases=8,independent_static_rendered_cases=len(cases),party_source_audit_sha256=sha((ROOT/'evidence/party-source-audit12.json').read_bytes()),base_independent_cases_sha256=sha((ROOT/'tests/speech-party-cases11.json').read_bytes()),additional_independent_cases_sha256=sha((ROOT/'tests/speech-party-extra-cases12.json').read_bytes()),in_game_verified=False)
class SourceSnapshot:
 def namelist(self):return [str(p.relative_to(ROOT/'src')) for p in (ROOT/'src/ForeverThai').rglob('*') if p.is_file()]
 def read(self,name):return (ROOT/'src'/name).read_bytes()
 def testzip(self):return None
with (contextlib.nullcontext(SourceSnapshot()) if args.source_debug else zipfile.ZipFile(args.archive)) as z:
 assert z.testzip() is None;source={str(p.relative_to(ROOT/'src')):p.read_bytes() for p in (ROOT/'src/ForeverThai').rglob('*') if p.is_file()};assert set(source)==set(z.namelist())
 for n,b in source.items():assert b==z.read(n),n
 manifest=json.loads((ROOT/'evidence/private-package-manifest11.json').read_text());changed=[]
 for n,h in manifest['runtime_manifest'].items():
  if sha(z.read(n))!=h:changed.append(n)
 assert changed==['ForeverThai/Catalog.lua','ForeverThai/Speech.lua'],changed
 assert sha(z.read('ForeverThai/Catalog.lua'))==json.loads((ROOT/'evidence/npc-reuse-regression12.json').read_text())['catalog_sha256']
 before=__import__('subprocess').check_output(['git','-C',str(ROOT),'show',manifest['runtime_git_tree']+':Speech.lua']).decode();after=z.read('ForeverThai/Speech.lua').decode();strip=lambda text:text.split('local playerSpeechTargets =',1)[0]+text.split('local function secret',1)[1];assert strip(before).replace('party-source-audit11.json','party-source-audit12.json')==strip(after),'Reviewed11algorithm changed beyond qualification table/source comment'
 def payload(name):return z.read('ForeverThai/'+name)
 # Exact original Lua fixture/event/settings/timers/capture/bitmap assertions retained.
 lua,a=replay(payload,corpus);g=lua.globals();popup=g.frames.ForeverThaiSpeechReader
 chunk=payload('Speech.lua').decode().split('local playerSpeechTargets =',1)[1].split('local function secret',1)[0];qualified_table=lua.execute('local playerSpeechTargets ='+chunk+'return playerSpeechTargets');actual={(int(n),sig,(value[1],value[2])) for n,entries in qualified_table.items() for sig,value in entries.items()};expected={(v['npc_id'],v['signature'],(v['prefix'],v['suffix'])) for v in audit['qualified_templates']};assert actual==expected
 # Install independently controlled current player units, NOT chat arg5.
 lua.execute('''
 roster={};guidReads={};interface=16001
 function GetBuildInfo()return version,build,"",interface end
 function UnitExists(unit)local u=roster[unit];if u then return u.exists end;return false end
 function UnitIsPlayer(unit)local u=roster[unit];if u then return u.player end;return false end
 function UnitInParty(unit)local u=roster[unit];if u then return u.party end;return false end
 function UnitInRaid(unit)local u=roster[unit];if u then return u.raid end end
 function UnitGUID(unit)
  if unit=="player" then return "Player-1-0001" end
  local u=roster[unit];guidReads[unit]=(guidReads[unit] or 0)+1
  if u then if u.changeGuid and guidReads[unit]>=2 then return "Player-1-CHANGED" end;return u.guid end
 end
 function UnitName(unit)
  if unit=="player" then return playerName end
  local u=roster[unit];if u then return u.name,u.realm end
 end
 function groupEvent(kind,text,id,arg5,guid)
  local f=frames.ForeverThaiSpeechEvents;guidReads={}
  f.scripts.OnEvent(f,kind,text,"Speaker","Common","",arg5,"",0,0,"",0,123,guid or ("Creature-0-1-2-3-"..id.."-012ABC"))
 end
 ''')
 counters=collections.Counter();g.playerName='Aeri';g.version='1.60.1';g.locale='enUS';g.ForeverThaiSpeech=lua.table();g.ForeverThaiObserved=None
 def member(name='Maelin',realm='',guid='Player-1-0002',**kw):
  values=dict(name=name,realm=realm,guid=guid,exists=True,player=True,party=True);values.update(kw);return lua.table_from(values)
 def roster(**units):g.roster=lua.table_from(units)
 def fire(c,text=None,expected=None,arg5='arbitrary',event=None,id=None,guid=None,category='negative'):
  a.SpeechCommand('speech hide');before=len(g.draws);g.groupEvent(event or c['event'],text if text is not None else c['english'],id if id is not None else c['npc_id'],arg5,guid)
  if expected is None:assert not popup.IsShown(popup) and len(g.draws)==before,(category,c['npc_id'],text)
  else:
   assert popup.IsShown(popup) and g.draws[len(g.draws)]=='|cffffd987'+a.speech[c['npc_id']].name+'|r\n'+expected,(category,c['npc_id'],g.draws[len(g.draws)] if len(g.draws)>before else 'not shown')
   for run in re.findall(r'[\u0e00-\u0e7f]+',expected):assert a.runs[run] is not None,run
  counters[category]+=1
 for build in ['70862','70888']:
  g.build=build
  for c in cases:
   roster(party1=member());fire(c,expected=c['thai'],category='party_positive');fire(c,expected=c['thai'],arg5=g.SECRET,category='secret_arg5_ignored_positive')
   roster(raid40=member(party=False,raid=40));fire(c,expected=c['thai'],category='raid_positive')
   roster(party1=member(),raid2=member(party=False,raid=2));fire(c,expected=c['thai'],category='same_guid_alias_positive')
   roster(party1=member('Maëlin'));fire(c,c['english'].replace('Maelin','Maëlin'),c['thai'].replace('Maelin','Maëlin'),category='unicode_positive')
   roster(party1=member());fire(c,c['english'].replace('Maelin','Outsider'),arg5='Maelin',category='nonparty_arg5_rejection');fire(c,c['english']+' changed',category='changed_body_rejection');fire(c,arg5='Maelin',event='CHAT_MSG_MONSTER_YELL',category='wrong_event_rejection');fire(c,id=999999999,category='wrong_npc_rejection');fire(c,guid='Player-1-0002',category='noncreature_speaker_rejection');fire(c,g.SECRET,category='secret_text_rejection');fire(c,guid=g.SECRET,category='secret_speaker_guid_rejection')
   roster();fire(c,arg5='Maelin',category='removed_member_rejection')
   for field,value in [('exists',False),('player',False),('party',False),('guid','Creature-0-1-2-3-999-01'),('guid',None),('name','|cff00ff00Maelin'),('name','Maelin Other'),('realm','Realm One'),('changeGuid',True),('raid',0),('raid',41)]:
    kw={field:value}
    if field=='raid':kw['party']=False
    roster(party1=member(**kw));fire(c,category='invalid_identity_rejection')
   for field in ['exists','player','party','raid','guid','name','realm']:
    roster(party1=member(**{field:g.SECRET}));fire(c,category='secret_identity_rejection')
   # An NPC or pet must never gain identity merely by occupying a fixture unit.
   roster(party1=member(player=False,guid='Pet-0-1-2-3-9-01'));fire(c,category='nonplayer_party_unit_rejection')
   roster(party1=member(party=False));fire(c,category='nonmember_unit_rejection')
   # Same base name on distinct realms is ambiguous; full names stay exact.
   roster(party1=member(realm='RealmOne'),party2=member(realm='RealmTwo',guid='Player-2-0003'))
   fire(c,category='duplicate_base_name_rejection');fire(c,c['english'].replace('Maelin','Maelin-RealmOne'),c['thai'].replace('Maelin','Maelin-RealmOne'),category='qualified_realm_positive');fire(c,c['english'].replace('Maelin','Maelin-RealmTwo'),c['thai'].replace('Maelin','Maelin-RealmTwo'),category='qualified_realm_positive');fire(c,c['english'].replace('Maelin','Maelin-OtherRealm'),category='wrong_realm_rejection')
   roster(party1=member(),party2=member(guid='Player-2-0003'));fire(c,category='duplicate_unqualified_rejection')
   # Group matching must not leak into generic quest/gossip/Tracker Translate.
   for row in corpus['entries']:
    if row['npc_id']==c['npc_id'] and row['english'].replace('$N','Maelin')==c['english']:
     # Entry matching remains current-player only even though event fallback works.
     for _,entry in a.speech[c['npc_id']][c['event']].items():
      if entry[1]==next(v['signature'] for v in audit['qualified_templates'] if v['english']==row['english']):assert a.Translate(entry,c['english']) is None;counters['shared_translate_remains_current_player_only']+=1
   roster(party1=member());g.ForeverThaiSpeech=lua.table_from(dict(enabled=False));fire(c,category='setting_off_rejection');g.ForeverThaiSpeech=lua.table_from(dict(enabled=False,capture=True));fire(c,category='capture_only_no_popup');g.ForeverThaiSpeech=lua.table()
  # Preserve every independent old source with a real party roster active too.
  roster(party1=member());g.ForeverThaiSpeech=lua.table()
  for row in corpus['entries']:
   raw=row['english'].replace('$N','Aeri').replace('$C','druid').replace('$R','night elf');expected=row['thai'].replace('{name}','Aeri').replace('{class}','ดรูอิด').replace('{race}','ไนต์เอลฟ์');c=dict(npc_id=row['npc_id'],event=row['event']);fire(c,raw,expected,category='legacy_active_group_positive');fire(c,raw+' changed',category='legacy_active_group_changed_body_rejection')
  c=cases[0];roster(party1=member());fire(c,expected=c['thai'],category='party_timer_positive');before=len(g.draws);g.groupEvent(c['event'],c['english'],c['npc_id'],'ignored',None);assert len(g.draws)==before;counters['party_dedup_checks']+=1;g.tick(0.6);g.groupEvent(c['event'],c['english'],c['npc_id'],'ignored',None);assert len(g.draws)==before+1;counters['party_timed_redisplay_checks']+=1;g.tick(15.1);assert not popup.IsShown(popup);counters['party_expiry_checks']+=1
  # Unknown group-like names remain opt-in captures; known translations do not.
  g.ForeverThaiSpeech=lua.table_from(dict(enabled=False,capture=True));g.ForeverThaiObserved=None;fire(c,category='party_capture_only_rejection');assert g.ForeverThaiObserved is None;fire(c,c['english'].replace('Maelin','Outsider'),category='party_unknown_capture_no_popup');assert g.ForeverThaiObserved.speechCount==1;g.ForeverThaiSpeech=lua.table()
  # UnitName is an existing core Match dependency, not a removable group-only API.
  for api in ['UnitExists','UnitIsPlayer','UnitInParty','UnitInRaid','UnitGUID']:
   saved=g[api];g[api]=None;fire(c,category='missing_group_api_rejection');g[api]=saved
  # Runtime supported/version/locale gates on a party-positive line.
  c=cases[0];roster(party1=member())
  for attr,value in [('locale','deDE'),('build','99999'),('version','1.15.8'),('interface',15000)]:
   saved=g[attr];g[attr]=value;fire(c,category='unsupported_client_rejection');g[attr]=saved
  g.locale='enGB';fire(c,expected=c['thai'],category='enGB_positive');g.locale='enUS'
  # Fixed NPC names and unqualified templates remain negative with a valid roster.
  roster(party1=member('Maelin'))
  for row in corpus['entries']:
   if re.search(r'\b(Ringo|Torta)\b',row['english']):
    for fixed in ['Ringo','Torta']:
     if fixed in row['english']:fire(dict(npc_id=row['npc_id'],event=row['event']),row['english'].replace(fixed,'Maelin').replace('$N','Aeri'),category='fixed_npc_name_rejection')
  # Other N templates may not gain party matching just because they look similar.
  qualified={(v['npc_id'],v['event'],v['english']) for v in audit['qualified_templates']}
  for row in corpus['entries']:
   if '$N' in row['english'] and (row['npc_id'],row['event'],row['english']) not in qualified:fire(dict(npc_id=row['npc_id'],event=row['event']),row['english'].replace('$N','Maelin').replace('$C','druid').replace('$R','night elf'),category='unqualified_name_template_rejection')
 result.update(status='passed',changed_runtime_files=changed,unchanged_candidate11_files=len(manifest['runtime_manifest'])-2,reviewed11_algorithm_retained=True,kristof_catalog_hash_verified=True,legacy_unique_forms=len(corpus['entries']),legacy_positive_event_executions=2*len(corpus['entries']),legacy_base_negative_event_executions=12*len(corpus['entries']),legacy_wrong_player_name_executions=2*sum('$N' in row['english'] for row in corpus['entries']),legacy_wrong_race_executions=2*sum('$R' in row['english'] for row in corpus['entries']),legacy_fixture_assertions_retained=True,legacy_additional_active_group_positive_executions=counters['legacy_active_group_positive'],legacy_additional_active_group_negative_executions=counters['legacy_active_group_changed_body_rejection'],legacy_bitmap_settings_timers_capture_gates_passed=True,party_executions=dict(counters),party_positive_executions=sum(v for k,v in counters.items() if k.endswith('positive') and k!='legacy_active_group_positive'),party_negative_event_executions=sum(v for k,v in counters.items() if (k.endswith('rejection') or k.endswith('no_popup')) and k!='legacy_active_group_changed_body_rejection'),party_timer_control_assertions=sum(counters[k] for k in ['party_dedup_checks','party_timed_redisplay_checks','party_expiry_checks']),shared_translate_identity_checks=counters['shared_translate_remains_current_player_only'],runtime_speech_sha256=sha(payload('Speech.lua')),scope=('Source-only debug; no ZIP assertion. ' if args.source_debug else 'Exact ZIP/current src on Cloud. ')+' Full independent686 Dev corpus with retained original runtime assertions + finite sixteen-template group tests. Actual BitmapLayer mock UI, API-source proof separate; not live Windows/Mac. Candidate11 immutable. Only enumerated whitelist/source comment in Speech.lua and reviewed Kristof binding in Catalog.lua differ; all other134files preserved.')
(ROOT/('work/party-debug12.json' if args.source_debug else 'evidence/party-speech-regression12.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
