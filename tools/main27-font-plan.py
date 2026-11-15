"""Plan only new MAIN27 runs using reviewed manual word cuts; no NLP/model install."""
import pathlib,json,zipfile,re,hashlib,time
from lupa.lua51 import LuaRuntime
R=pathlib.Path(__file__).resolve().parent;O=R/'package-main27';O.mkdir(exist_ok=True);start=time.perf_counter()
base=R/'package-main25-26/build-0.468.0/ForeverThai-0.468.0-main25-26-PRIVATE-TEST.zip';assert hashlib.sha256(base.read_bytes()).hexdigest()=='90b85b81dc4f9dc4d94b4349ec7c64a90889deedf8340c8976806115fb5441df'
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table()
with zipfile.ZipFile(base) as z:
 for n in ['Atlas.lua','AtlasMain2526.lua']:l.execute(z.read('ForeverThai/'+n).decode(),'ForeverThai',a)
fields=json.loads((R/'main27-reviewed-pairs.json').read_text(encoding='utf-8'))['fields'];cuts=json.loads((R/'main27-thai-word-cuts.json').read_text(encoding='utf-8'));wordcuts={}
for f in fields:
 if f['translation_kind']!='new_reviewed_Thai':continue
 s=cuts[str(f['quest_id'])];assert s.replace('|','')==f['thai']
 for m in re.finditer(r'[\u0e00-\u0e7f]+(?:\|[\u0e00-\u0e7f]+)*',s):
  text=m[0];key=text.replace('|','');wordcuts.setdefault(key,text.split('|'))
need=sorted({s for f in fields for s in re.findall(r'[\u0e00-\u0e7f]+',f['thai']) if a.runs[s] is None});plans=[];newwords=set()
for run in need:
 assert run in wordcuts,('Unchanged reuse text lacks prior font run; manual review required',run)
 words=wordcuts[run];assert ''.join(words)==run;dp={len(words):(0,0,[])}
 for i in range(len(words)-1,-1,-1):
  choices=[]
  for j in range(i+1,len(words)+1):
   s=''.join(words[i:j]);known=a.runs[s]
   if known is not None and j in dp:
    cost,parts,chain=dp[j];choices.append((cost,parts+1,[dict(text=s,kind='existing run',glyphs=[int(known[ix]) for ix in range(1,len(known)+1)])]+chain))
  cost,parts,chain=dp[i+1];w=words[i];known=a.runs[w]
  choices.append((cost+(known is None),parts+1,[dict(text=w,kind='new shaped word' if known is None else 'existing run',glyphs=None if known is None else [int(known[ix]) for ix in range(1,len(known)+1)])]+chain))
  dp[i]=min(choices,key=lambda v:(v[0],v[1]))
 pieces=dp[0][2];assert ''.join(v['text'] for v in pieces)==run
 newwords.update(v['text'] for v in pieces if v['kind']=='new shaped word');plans.append(dict(run=run,pieces=pieces))
assert len(newwords)<=128,('New-word bound exceeded',len(newwords))
role_values=['นักรบ','พาลาดิน','พราน','โจร','นักบวช','ชาแมน','จอมเวท','วอร์ล็อก','ดรูอิด','คนแคระ','โนม','มนุษย์','ไนต์เอลฟ์','ออร์ค','สกายบอร์น','ทอเรน','โทรลล์','อันเดด','สกายบอร์นฝ่ายไฮออร์เดอร์','สกายบอร์นฝ่ายวินด์เชเปอร์']
assert all(a.runs[v] is not None for v in role_values),'Dynamic class/race Thai run missing'
report=dict(status='BOUNDED_FONT_PLAN_READY',baseline_version='0.468.0',old_glyph_slots=len(a.glyphs),old_run_count=sum(1 for _ in a.runs.items()),old_last_page=max(v[1] for _,v in a.glyphs.items()),missing_runs=len(need),new_word_glyphs=len(newwords),new_words=sorted(newwords),plans=plans,dynamic_class_race_values_already_ready=len(role_values),new_NLP_or_AI_dependency=False,manual_cuts_preserve_all7_original_Thai=True,elapsed_wall_seconds=time.perf_counter()-start)
(O/'font-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['plans']},ensure_ascii=False))
