"""Parse only Harvest's [positiveInteger]="Lua string" literal rows.
This is a data parser, not a Lua interpreter. Calls/expressions/duplicate IDs fail.
"""
import re
ESCAPES={'a':'\a','b':'\b','f':'\f','n':'\n','r':'\r','t':'\t','v':'\v','\\':'\\','"':'"',"'":"'"}
def decode_string(literal):
 assert literal.startswith('"') and literal.endswith('"')
 s=literal[1:-1];out=bytearray();i=0
 while i<len(s):
  if s[i]!='\\':
   if s[i] in '\r\n':raise ValueError('Unescaped newline')
   out.extend(s[i].encode("utf8"));i+=1;continue
  i+=1
  if i==len(s):raise ValueError('Truncated escape')
  if s[i].isdigit() and s[i].isascii():
   m=re.match(r'[0-9]{1,3}',s[i:]);value=int(m[0],10)
   if value>255:raise ValueError('Byte escape out of range')
   out.append(value);i+=len(m[0])
  elif s[i] in ESCAPES:out.extend(ESCAPES[s[i]].encode('utf8'));i+=1
  else:raise ValueError('Unsupported escape')
 return out.decode('utf8')
ROW=re.compile(r'\s*\[([0-9]+)\]\s*=\s*("(?:\\.|[^"\\])*")\s*,?',re.S)
def parse_rows(body):
 rows={};pos=0
 while body[pos:].strip():
  match=ROW.match(body,pos)
  if not match:raise ValueError('Non-literal content in Harvest table at '+str(pos))
  q=int(match[1])
  if q<=0 or q in rows:raise ValueError('Invalid or duplicate quest ID')
  rows[q]=decode_string(match[2]);pos=match.end()
 return rows

def parse_harvest(source,kind):
 opener='lib:LoadQuests({' if kind=='core' else 'lib:LoadText("enUS", {'
 if source.count(opener)!=1:raise ValueError('Unexpected table envelope')
 before,body=source.split(opener)
 # The core's second argument is a literal column-name schema, not code.
 if kind=='core':
  if '\n}, ' not in body:raise ValueError('Missing literal core schema')
  body,schema=body.rsplit('\n}, ',1)
  literal=r'"(?:\\.|[^"\\])*"'
  if not re.fullmatch(r'\{\s*(?:'+literal+r'\s*,?\s*)+\}\)\s*',schema):raise ValueError('Nonliteral core schema')
  columns=[decode_string(v) for v in re.findall(literal,schema)]
  expected='requiredLevel questLevel zoneOrSort requiredRaces requiredClasses questFlags specialFlags startNpcs startObjects startItems endNpcs endObjects objNpcs objObjects objItems objRep objSpells explore preQuestSingle preQuestActive preQuestGroup exclusiveTo nextQuestInChain breadcrumbFor requiredSkill requiredMinRep requiredMaxRep suggestedPlayers hidden'.split()
  if columns!=expected:raise ValueError('Unexpected core schema columns')
  return parse_rows(body)
 if not body.rstrip().endswith('})'):raise ValueError('Unexpected trailing code')
 return parse_rows(body.rstrip()[:-2])
