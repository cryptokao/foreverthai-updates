import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools'))
from harvest_literals import parse_rows,decode_string
class HarvestLiteralTests(unittest.TestCase):
 def test_lua_decimal_separator_and_escaped_text(self):
  self.assertEqual(decode_string(r'"\226\128\153"'),'’')
  self.assertEqual(decode_string(r'"Title\031\031Summary\nline"'),'Title\x1f\x1fSummary\nline')
  self.assertEqual(parse_rows(r'[7]="A \\" B"'.replace(r'\\"',r'\"'))[7],'A " B')
 def test_calls_expressions_and_trailing_code_are_rejected(self):
  for source in ['[1]=os.execute("x")','[1]="x" .. "y"','[1]="x", function() end','[1]="x", [2]=LibStub("x")']:
   with self.subTest(source=source):
    with self.assertRaises(ValueError):parse_rows(source)
 def test_duplicate_ids_and_unsupported_escapes_are_rejected(self):
  for source in [r'[1]="a",[1]="b"',r'[1]="\999"',r'[1]="\z"']:
   with self.subTest(source=source):
    with self.assertRaises(ValueError):parse_rows(source)
if __name__=='__main__':unittest.main()
