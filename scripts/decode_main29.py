"""Decode only newly supplied MAIN29 issue data; never execute upstream code."""
import json,pathlib,re,zlib,base64,hashlib,collections
R=pathlib.Path(__file__).resolve().parent
inputs=json.loads((R/'main29-fvo-new-issues-private.json').read_text(encoding='utf-8'))
docs=[];missing=[]
for v in inputs:
 matches=re.findall(r'FVO1:([A-Za-z0-9+/=]+)',v['body'])
 if not matches:missing.append(v['issue']);continue
 assert len(matches)==1
 raw=zlib.decompress(base64.b64decode(matches[0]),bufsize=1024*1024)
 assert len(raw)<16*1024*1024
 d=json.loads(raw);assert isinstance(d,dict) and isinstance(d['lines'],list)
 docs.append(dict(issue=v['issue'],url=v['url'],source_kind=v['source_kind'],comment_id=v.get('comment_id'),doc=d,raw_sha256=hashlib.sha256(raw).hexdigest(),body_sha256=hashlib.sha256(v['body'].encode()).hexdigest()))
(R/'main29-fvo-decoded-private.json').write_text(json.dumps(docs,ensure_ascii=False),encoding='utf-8')
print(json.dumps(dict(actual_exports=len(docs),actual_records=sum(len(d['doc']['lines']) for d in docs),missing_payload_issues=missing,exports=[dict(issue=d['issue'],records=len(d['doc']['lines']),build=d['doc'].get('build'),locale=d['doc'].get('locale'),kinds=dict(collections.Counter(v.get('k') for v in d['doc']['lines']))) for d in docs]),ensure_ascii=False))
