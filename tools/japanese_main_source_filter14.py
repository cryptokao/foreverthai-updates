"""Bounded source qualification of the previously discovered365 absent-canonical rows.
Reads English only. No addon/game suite, library code or Japanese translation runs.
"""
import collections,hashlib,json,pathlib,re,runpy,subprocess
from lupa.lua51 import LuaRuntime
from source_classification import classify_title
ROOT=pathlib.Path(__file__).resolve().parents[1];REF='76fc4f2d32f90af96c2a382d7e6c4723d5902e3b';REPO=ROOT/'work/forever-japanese';TREE='f85a68ca9c2ade231310620e693765cd99eebfc1'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args])
sig=runpy.run_path('/workspace/foreverthai-dev/combined/ForeverThai/Dev/Signature.py')['signature']
prior=json.loads((ROOT/'work/new-main-sources/japanese-unmatched.json').read_text());rows=[r for r in prior if not r['canonical_present']];assert len(rows)==365
eligible=[r for r in rows if r['source'].startswith('wdb@1.60.1.') or r['source'].startswith(('collector@1.60.1.','forever-vo@'))];assert len(eligible)==52
files={};lineages={};titles={}
for path in git('ls-tree','-r','--name-only',REF,'data/english/quest').decode().splitlines():
 if not path.endswith('.jsonl'):continue
 raw=git('show',REF+':'+path);files[path]=dict(bytes=len(raw),sha256=sha(raw))
 for i,line in enumerate(raw.decode().splitlines(),1):
  r=json.loads(line);f={'objectives':'objective'}.get(r['field'],r['field']);lineages[r['id'],f,r['en']]=dict(path=path,line=i,source=r['src'],upstream_hash=r['hash'])
  if f=='title':titles[r['id']]=r['en']
served=git('show',REF+':pipeline/served/quest.tsv');served_index={}
for line in served.decode().splitlines():
 if line.startswith('#'):continue
 q,first,last=line.split('\t');served_index[int(q)]=dict(first_build=first,last_build=last)
lua=LuaRuntime();a=lua.table();lua.eval('function(s,a)assert(loadstring(s))("ForeverThai",a)end')((ROOT/'src/ForeverThai/Catalog.lua').read_text(),a)
index=collections.defaultdict(list)
# Cross-ID signature lookup includes every explicit canonical and nested runtime alias.
index=collections.defaultdict(list)
def collect(e,q,f):
 if e is None:return
 signatures=e[1];signatures=[signatures] if isinstance(signatures,str) else [v for _,v in signatures.items()]
 for s in signatures:index[s].append(dict(quest_id=q,field=f))
 for _,v in (e.variants.items() if e.variants is not None else []):collect(v,q,f)
for q,qe in a.quests.items():
 for f in ['title','objective','description','progress','completion']:collect(qe[f],q,f)
manual_test={5101:'Description explicitly calls this a Test Quest and objective jokes about running.',8274:'Objective explicitly asks return to the test character.',7681:'Exact title Hunter test quest and internal feed-pet script instruction.',7682:'Exact title Hunter test quest2 and internal feed-pet script instruction.',8230:"Exact title Collin's Test Quest; no playable/source phase proof.",8270:'Exact title test copy quest.',92534:'Exact title jktestquest1a; no playable/source phase proof.'}
qualified=[]
for r in eligible:
 q=r['quest_id'];f=r['field'];title=titles.get(q,'');source=lineages[q,f,r['english']];assert source['source']==r['source'];e=a.quests[q];canonical=e[f] if e is not None else None;assert canonical is None
 marker=classify_title(title,q)
 if marker:status='held_explicit_disabled_or_developer';proof_gap=marker+'; query/cache presence does not establish enabled playability.'
 elif q in manual_test:status='held_explicit_test_context';proof_gap=manual_test[q]
 elif r['english'] in ['Description','Log'] or r['english'].startswith('[PH]'):status='held_placeholder_not_prose';proof_gap='Need actual own-ID full '+f+' source; placeholder is not quest prose.'
 elif f=='title':status='held_title_only_usage_unconfirmed';proof_gap='Only this title is absent; no new main prose in this subset. Need current enabled own-ID/phase evidence; historical cache/served-ID is insufficient.'
 else:status='needs_manual_source_review';proof_gap='No approval from metadata alone.'
 hits=index.get(sig(r['english']),[])
 qualified.append(dict(quest_id=q,level=r['level'],field=f,title=title,source_kind=r['source'],english_sha256=sha(r['english'].encode()),source_record=source,upstream_served_id_observation=served_index.get(q),runtime_canonical_present=False,matching_existing_signatures=hits,status=status,proof_gap=proof_gap))
qualified.sort(key=lambda r:(r['level'] if r['level'] is not None and r['level']>0 else 999,r['quest_id'],r['field']))
assert not any(r['status']=='needs_manual_source_review' for r in qualified)
manifest=json.loads((ROOT/'evidence/private-package-manifest13.json').read_text())['runtime_manifest'];assert all(sha((ROOT/'src'/p).read_bytes())==h for p,h in manifest.items())
excluded=[dict(quest_id=r['quest_id'],field=r['field'],source_kind=r['source'],english_sha256=sha(r['english'].encode()),reason='Classic Era WDB/pfQuest/VMangos only; not current Forever prose proof.') for r in rows if r not in eligible]
report=dict(scope='Only previously discovered365 English fields lacking an own-ID runtime canonical; not365 quests or whole-game gap count. Source filtering and alias comparison only, no regression suite.',upstream=dict(repository='zyaga/wow-forever-japanese',commit=REF,served_ledger_sha256=sha(served),source_files=files,limitation='src labels and served-ID ledger are upstream provenance assertions. No full original70862 cache is transferred. Additive English retains old/disabled records; ledger does not prove playability. Upstream collector class/race normalization is not used as typed proof.'),actual_runtime_tree=TREE,counts=dict(prior_absent_canonical_fields=365,excluded_classic_reference_fields=len(excluded),excluded_by_source=dict(collections.Counter(r['source_kind'] for r in excluded)),forever_wdb_candidate_fields=len(qualified),forever_candidate_unique_ids=len({r['quest_id'] for r in qualified}),forever_player_capture_absent_canonical_fields=0,statuses=dict(collections.Counter(r['status'] for r in qualified)),existing_cross_id_alias_signature_matches=sum(bool(r['matching_existing_signatures']) for r in qualified),writ_named_records_in_filtered_subset=sum('writ' in r['title'].lower() for r in qualified),source_ready_new_main_fields=0,new_thai_fields=0,new_aliases=0),records=qualified,excluded_records=excluded,decision='Stop this bounded source queue: no corroborated enabled new main prose. Preserve candidate13; do not switch NPC/book/party or rerun unchanged tests.',runtime_files_unchanged=len(manifest),japanese_translation_imported=False)
(ROOT/'evidence/japanese-main-source-filter14.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['counts'],indent=2))
