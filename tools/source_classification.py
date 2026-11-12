"""Conservative source-label classification, never a playability classifier."""
import re
DEVELOPER_MARKERS=re.compile(r'\[(?:UNUSED|DNT|DND|PH|TEST|NEVER USED)\]|<(?:UNUSED|DNT|DND|PH|TEST|NYI|TXT)>|\((?:UNUSED|DNT|PH|TEST)\)',re.I)
DISABLED_MARKERS=re.compile(r'\((?:TEMP(?:ORARILY)?\s+)?DISABLED\)|\[(?:DISABLED|OBSOLETE)\]|<(?:DISABLED|OBSOLETE)>',re.I)
EXACT_DEVELOPER_LABELS={'REUSE','REUSE ME','REUSEME','UNUSED'}
# Reviewed against current pinned EG quest1/9065 records, whose prose is an
# explicit Kobold development test, not a quest title containing the word Test.
KNOWN_DEVELOPER_IDS={1:'The "Chow" Quest (123)aa',9065:'The "Chow" Quest (123)aa'}
KNOWN_DISABLED_IDS={94898:'Violent Winds (Temp Disabled)'}
def classify_title(title,quest_id=None):
 title=title or ''
 if quest_id in KNOWN_DISABLED_IDS and title==KNOWN_DISABLED_IDS[quest_id]:return 'disabled_marker'
 if DISABLED_MARKERS.search(title):return 'disabled_marker'
 if quest_id in KNOWN_DEVELOPER_IDS and title==KNOWN_DEVELOPER_IDS[quest_id]:return 'known_developer_id'
 if DEVELOPER_MARKERS.search(title):return 'developer_marker'
 if re.search(r'^zzOLD\s+UNUSED\b|[-:]\s*do not use\s*$',title,re.I):return 'developer_marker'
 if ' '.join(title.upper().split()) in EXACT_DEVELOPER_LABELS:return 'developer_exact_label'
 return None

def classify_titles(titles,quest_id=None,current_title=None):
 # An old metadata label must not hide a conflicting current query title.
 if current_title:return classify_title(current_title,quest_id)
 kinds=[classify_title(t,quest_id) for t in titles if t]
 if not kinds or any(k is None for k in kinds):return None
 return 'disabled_marker' if all(k=='disabled_marker' for k in kinds) else 'developer_marker'
