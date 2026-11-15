"""Read only the user's ForeverThaiObserved as literal data; never execute SavedVariables Lua."""
import pathlib,re,json,hashlib,sys,datetime
R=pathlib.Path(__file__).resolve().parent
assert len(sys.argv)<=2 and (len(sys.argv)==1 or sys.argv[1]=='latest')
suffix='-latest' if len(sys.argv)==2 else ''
class LiteralReader:
 def __init__(self,s,start):self.s=s;self.i=start
 def skip(self):
  while True:
   m=re.match(r'(?:\s+|--[^\r\n]*)',self.s[self.i:])
   if not m:return
   self.i+=m.end()
 def peek(self):self.skip();return self.s[self.i:self.i+1]
 def take(self,ch):
  self.skip();assert self.s.startswith(ch,self.i),'Expected data punctuation';self.i+=len(ch)
 def string(self):
  quote=self.s[self.i];self.i+=1;out=bytearray();esc={'a':7,'b':8,'f':12,'n':10,'r':13,'t':9,'v':11,'\\':92,'"':34,"'":39}
  while self.i<len(self.s):
   c=self.s[self.i];self.i+=1
   if c==quote:return out.decode('utf-8')
   if c!='\\':out.extend(c.encode('utf-8'));continue
   assert self.i<len(self.s);c=self.s[self.i];self.i+=1
   if c in esc:out.append(esc[c])
   elif c.isascii() and c.isdigit():
    digits=c
    while len(digits)<3 and self.i<len(self.s) and self.s[self.i].isascii() and self.s[self.i].isdigit():digits+=self.s[self.i];self.i+=1
    n=int(digits);assert n<=255;out.append(n)
   elif c=='\n':out.append(10)
   elif c=='\r':
    if self.s[self.i:self.i+1]=='\n':self.i+=1
    out.append(10)
   else:raise ValueError('Unsupported literal string escape')
  raise ValueError('Unterminated literal string')
 def value(self,depth=0):
  assert depth<24,'Literal nesting too deep';c=self.peek()
  if c in ['"',"'"]:return self.string()
  if c=='{':
   self.take('{');out={};idx=1
   while self.peek()!='}':
    if self.peek()=='[':self.take('[');key=self.value(depth+1);self.take(']');self.take('=');v=self.value(depth+1)
    else:
     self.skip();m=re.match(r'([A-Za-z_][A-Za-z_0-9]*)\s*=',self.s[self.i:])
     if m:key=m[1];self.i+=m.end();v=self.value(depth+1)
     else:key=idx;idx+=1;v=self.value(depth+1)
    assert key not in out,'Duplicate literal key';out[key]=v
    if self.peek() in [',',';']:self.i+=1
    else:assert self.peek()=='}','Expected literal separator'
   self.take('}');return out
  self.skip();m=re.match(r'-?(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)',self.s[self.i:])
  if m:
   self.i+=m.end();t=m[0];return int(t,16) if 'x' in t.lower() else float(t) if re.search('[.eE]',t) else int(t)
  for word,val in [('true',True),('false',False),('nil',None)]:
   if self.s.startswith(word,self.i) and not re.match(r'[A-Za-z_0-9]',self.s[self.i+len(word):self.i+len(word)+1]):self.i+=len(word);return val
  raise ValueError('Executable/nonliteral Lua rejected')
paths=json.loads((R/'main32-local-observed-paths-private.json').read_text(encoding='utf-8-sig'));paths=[paths] if isinstance(paths,dict) else paths
pins=[];seen=set();docs=[]
for index,f in enumerate(paths):
 path=pathlib.Path(f['path']);before=path.stat();b=path.read_bytes();after=path.stat();assert before.st_mtime_ns==after.st_mtime_ns and len(b)==after.st_size,'Source changed during this read';assert len(b)<32*1024*1024;sha=hashlib.sha256(b).hexdigest();pin=dict(source_index=index,file_sha256=sha,file_bytes=len(b),backup=f['backup'],last_write_utc=datetime.datetime.fromtimestamp(after.st_mtime,datetime.timezone.utc).isoformat());pins.append(pin)
 if sha in seen:pin['duplicate_skipped']=True;continue
 seen.add(sha);s=b.decode('utf-8-sig');m=re.search(r'(?m)^ForeverThaiObserved\s*=\s*',s);assert m
 d=LiteralReader(s,m.end()).value();assert isinstance(d,dict);docs.append(dict(pin=pin,observed=d))
(R/f'main32-local-observed{suffix}-decoded-private.json').write_text(json.dumps(docs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
summaries=[]
for doc in docs:
 d=doc['observed'];q=d.get('quests',{});rows=[]
 for qid,fields in q.items():
  if not isinstance(qid,int) or not isinstance(fields,dict):continue
  for phase,variants in fields.items():
   if isinstance(variants,dict):
    for ix,v in variants.items():
     if isinstance(v,dict) and isinstance(v.get('text'),str):rows.append(dict(quest_id=qid,field=phase,index=ix,chars=len(v['text']),build=v.get('build'),locale=v.get('locale'),identity_keys=sorted(k for k in ['player','class','race'] if k in v),has_context=bool(v.get('questContext'))))
 summaries.append(dict(source_index=doc['pin']['source_index'],schema=d.get('schema'),stored_count=d.get('count'),main_quest_ids=len(q),main_fields=len(rows),rows=rows))
report=dict(status='READ_ONLY_LOCAL_OBSERVED_LITERAL_DATA_PARSED',sources=pins,summaries=summaries,game_install_or_control=False,source_files_modified=False,raw_player_context_published=False,upstream_code_executed=False)
(R/f'main32-local-observed{suffix}-safe-inventory.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:v for k,v in report.items() if k!='summaries'}));print(json.dumps([{k:v for k,v in s.items() if k!='rows'} for s in summaries]))
