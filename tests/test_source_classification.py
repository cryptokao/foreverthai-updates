"""Audit-label regressions; no runtime, font, NPC or Skill replay is required."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools'))
from source_classification import classify_title,classify_titles
class SourceClassificationTests(unittest.TestCase):
 def test_real_titles_and_substrings_are_not_developer_markers(self):
  for title in ['Testing the Wells','Contest','The Greatest Race of Hunters','A Test of Faith','Test of Endurance','The Test of Righteousness','Prove Your Worth']:
   with self.subTest(title=title):self.assertIsNone(classify_title(title))
 def test_explicit_markers_from_sources_are_excluded(self):
  for title in ['<UNUSED>','[UNUSED]','[DNT] Holiday Quests Tracker','[PH] Collect frogs','<nyi> <TXT>The Centaur Hoofprints','[Never used]','REUSE ME','(UNUSED) The Rusty Gadget','zzOLD UNUSED Cult Ambush','test quest - do not use']:
   with self.subTest(title=title):self.assertIn(classify_title(title),['developer_marker','developer_exact_label'])
 def test_disabled_annotation_and_known_ids_require_matching_evidence(self):
  self.assertEqual(classify_title('Violent Winds (Temp Disabled)',94898),'disabled_marker')
  self.assertIsNone(classify_title('Testing the Wells',94898))
  self.assertEqual(classify_title('The "Chow" Quest (123)aa',1),'known_developer_id')
  self.assertIsNone(classify_title('A Test of Faith',1))
 def test_historical_label_cannot_hide_current_or_conflicting_title(self):
  self.assertIsNone(classify_titles(['[UNUSED]','Testing the Wells'],current_title='Testing the Wells'))
  self.assertIsNone(classify_titles(['[UNUSED]','Testing the Wells']))
  self.assertEqual(classify_titles(['[UNUSED]','[DNT] Old Quest']),'developer_marker')
if __name__=='__main__':unittest.main()
