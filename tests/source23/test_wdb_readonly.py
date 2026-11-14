"""Synthetic protocol structures only. No user cache, addon fixtures, game or network."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import struct
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('owned_wdb23', ROOT/'tools/source23_wdb_readonly.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
H = lambda b: hashlib.sha256(b).hexdigest()
# Independent wire fixture encoder: nine field widths from published layout, not parser constants.
WIDTHS = [9, 12, 12, 9, 10, 8, 10, 8, 11]
TEXTS = [b'Synthetic Quest', b'Gather two samples. $1oa', b'A synthetic description. $N $c',
         b'', b'', b'', b'', b'', b'Log completion only.']


def wire_header(strings):
    bits = ''.join(format(len(s), '0%db' % w) for s, w in zip(strings, WIDTHS)) + '0000000'
    return int(bits, 2).to_bytes(12, 'big')


def objective(oid=5000, effects=0, desc=b'obj'):
    b = bytearray(43 + 4*effects)
    struct.pack_into('<I', b, 0, oid)
    b[4] = 1
    struct.pack_into('<i', b, 9, 123)
    struct.pack_into('<i', b, 13, 2)
    struct.pack_into('<i', b, 33, effects)
    b[41+4*effects] = len(desc)
    return bytes(b) + desc


def payload(qid=116, strings=None, chain=None, gap=b''):
    strings = list(TEXTS if strings is None else strings)
    return (struct.pack('<I', qid) + b'\xff'*12 + (objective() if chain is None else chain)
            + wire_header(strings) + gap + b''.join(strings))


def snapshot(records=None, tail=b'\0'*8):
    records = [(116, payload())] if records is None else records
    data = b'TSQW' + struct.pack('<I', 70938) + b'SUne' + b'\0'*12
    data += b''.join(struct.pack('<II', q, len(p)) + p for q, p in records) + tail
    unique = dict(records)
    expected = dict(schema=1, expected_magic='TSQW', expected_build=70938, expected_locale='enUS',
                    source23_file_sha256=H(data),
                    expected_records=[dict(id=q, payload_bytes=len(p), payload_sha256=H(p)) for q,p in unique.items()],
                    expected_titles={str(q):dict(title_sha256=H(TEXTS[0])) for q in unique})
    return data, expected


class StrictWDB(unittest.TestCase):
    def rejected(self, data, expected, reason):
        with self.assertRaisesRegex(m.Rejected, '^'+reason+'$'):
            m.extract(data, expected)

    def held(self, p, reason):
        d,e = snapshot([(116,p)])
        report,decoded=m.extract(d,e)
        self.assertEqual(report['records'][0]['status'],reason)
        self.assertEqual(decoded,[])
        return report

    def test_fixed_bit_header_oracle(self):
        # Constant bytes independently calculated for [12,9,14,0,0,0,0,0,0], seven trailing flags0.
        raw=bytes.fromhex('060048070000000000000000')
        lengths,flags=m.lengths_at(raw,0)
        self.assertEqual(lengths,[12,9,14,0,0,0,0,0,0])
        self.assertEqual(flags,0)

    def test_valid_wire_structure_metadata_privacy_and_raw_macros(self):
        data,expected=snapshot()
        metadata,decoded=m.extract(data,expected)
        row=metadata['records'][0]
        self.assertEqual(row['status'],'unique_structure_raw_only_pending_review')
        self.assertTrue(row['title_match'])
        self.assertEqual(row['header_proof']['valid_objective_chain_candidates'],1)
        self.assertEqual(row['header_proof']['strings_end'],len(payload()))
        self.assertEqual(metadata['envelopes_validated'],1)
        fields={f['protocol_field']:f for f in row['fields']}
        self.assertEqual(fields['questDescription']['raw_macro_positions'],
                         [dict(byte_offset=25,marker='$N',semantic_role='unconfirmed'),
                          dict(byte_offset=28,marker='$c',semantic_role='unconfirmed')])
        self.assertEqual(fields['completionLog']['UI_phase_binding'],'held_not_reward_or_progress_dialogue')
        public=json.dumps(metadata)
        for raw in TEXTS:
            if raw:self.assertNotIn(raw.decode(),public)
        self.assertEqual(decoded[0]['raw_protocol_strings']['questDescription'],TEXTS[2].decode())
        self.assertFalse(row['quantities_substituted'])

    def test_utf8_length_is_bytes(self):
        texts=list(TEXTS);texts[2]='ข้อมูลจำลอง'.encode()
        d,e=snapshot([(116,payload(strings=texts))]);r,private=m.extract(d,e)
        self.assertEqual(r['records'][0]['status'],'unique_structure_raw_only_pending_review')
        field=r['records'][0]['fields'][2]
        self.assertEqual(field['raw_bytes'],len(texts[2]))
        self.assertEqual(private[0]['raw_protocol_strings']['questDescription'],'ข้อมูลจำลอง')

    def test_gap_between_header_and_tail_held(self):
        self.held(payload(gap=b'X'),'held_no_unique_known_title_header')

    def test_invalid_tail_utf8_held(self):
        texts=list(TEXTS);texts[2]=b'\xff'
        self.held(payload(strings=texts),'held_no_unique_known_title_header')

    def test_no_objective_chain_is_not_accepted(self):
        self.held(payload(chain=b'\xff'*43),'held_unconfirmed_objective_chain')

    def test_two_objective_binary_array_with_exact_suffix_accepted(self):
        d,e=snapshot([(116,payload(chain=objective(5000)+objective(5001)))])
        r,private=m.extract(d,e)
        row=r['records'][0]
        self.assertEqual(row['status'],'unique_structure_raw_only_pending_review')
        self.assertEqual(row['header_proof']['valid_objective_chain_candidates'],2)
        self.assertEqual(row['header_proof']['objective_chain']['objective_count'],2)
        self.assertEqual(row['header_proof']['other_candidates_proven_exact_suffixes'],1)
        self.assertFalse(row['quantities_substituted'])
        self.assertEqual(private[0]['raw_protocol_strings']['logDescription'],TEXTS[1].decode())

    def test_genuine_nonsuffix_chain_ambiguity_decision_boundary_negative(self):
        # Decision-boundary injected candidates, not claimed as an extra binary wire fixture.
        # Same end and compatible IDs still do not qualify if node boundaries cross.
        chains=[dict(start=16,end=110,objective_count=2,raw_sha256='a'*64,
                     _nodes=[(16,63,5000),(63,110,5001)]),
                dict(start=20,end=110,objective_count=2,raw_sha256='b'*64,
                     _nodes=[(20,70,5000),(70,110,5001)])]
        with patch.object(m,'objective_chains',return_value=chains):
            row,private=m.parse_record(116,payload(),dict(title_sha256=H(TEXTS[0])))
        self.assertEqual(row['status'],'held_ambiguous_objective_chain')
        self.assertIsNone(private)

    def test_unicode_before_name_macro_uses_utf8_byte_offset(self):
        texts=list(TEXTS);texts[2]='ไทย $N'.encode('utf-8')
        d,e=snapshot([(116,payload(strings=texts))]);r,private=m.extract(d,e)
        field=r['records'][0]['fields'][2]
        self.assertEqual(field['raw_macro_positions'],
                         [dict(byte_offset=10,marker='$N',semantic_role='unconfirmed')])
        self.assertEqual(private[0]['raw_protocol_strings']['questDescription'],'ไทย $N')

    def test_multiple_header_decision_rejects_instead_of_last_plausible(self):
        # Decision-boundary ambiguity injection; not claimed as a second wire fixture.
        with patch.object(m,'string_candidates',return_value=([{'offset':40},{'offset':55}],2)):
            r,private=m.parse_record(116,payload(),dict(title_sha256=H(TEXTS[0])))
        self.assertEqual(r['status'],'held_ambiguous_header')
        self.assertEqual(r['header_candidates'],2)
        self.assertIsNone(private)

    def test_known_title_hash_mismatch_held(self):
        d,e=snapshot();e['expected_titles']['116']['title_sha256']=H(b'Different Quest')
        r,private=m.extract(d,e)
        self.assertEqual(r['records'][0]['status'],'held_no_unique_known_title_header')
        self.assertEqual(private,[])

    def test_missing_or_conflicting_title_held(self):
        d,e=snapshot();e['expected_titles']['116']['title_sha256']=None
        r,private=m.extract(d,e)
        self.assertEqual(r['records'][0]['status'],'held_missing_or_conflicting_expected_title')
        self.assertEqual(private,[])

    def test_invalid_objective_utf8_held(self):
        self.held(payload(chain=objective(desc=b'\xff')),'held_unconfirmed_objective_chain')

    def test_unsupported_visual_effect_count_held(self):
        p=bytearray(objective());struct.pack_into('<i',p,33,9)
        self.held(payload(chain=bytes(p)),'held_unconfirmed_objective_chain')

    def test_nonzero_visual_effects_exact_bounds(self):
        d,e=snapshot([(116,payload(chain=objective(effects=2)))])
        r,_=m.extract(d,e)
        self.assertEqual(r['records'][0]['status'],'unique_structure_raw_only_pending_review')

    def test_one_mib_bound(self):
        self.rejected(b'X'*(1024*1024+1),{},'input_size_out_of_bounds')

    def test_snapshot_hash_binding(self):
        d,e=snapshot();self.rejected(d+b'X',e,'input_snapshot_sha256_mismatch')

    def test_header_magic_build_locale(self):
        for offset,value,reason in [(0,b'WDBC','invalid_wdb_magic'),(4,struct.pack('<I',70888),'unsupported_wdb_build'),(8,b'RF rf'[:4],'unsupported_wdb_locale')]:
            with self.subTest(reason=reason):
                d,e=snapshot();d=d[:offset]+value+d[offset+4:];e['source23_file_sha256']=H(d)
                self.rejected(d,e,reason)

    def test_missing_sentinel(self):
        d,e=snapshot(tail=b'');self.rejected(d,e,'missing_sentinel_or_records')

    def test_sentinel_must_be_exact_end(self):
        d,e=snapshot(tail=b'\0'*8+b'X');self.rejected(d,e,'trailing_data_after_sentinel')

    def test_duplicate_envelope_rejected(self):
        p=payload();d,e=snapshot([(116,p),(116,p)])
        self.rejected(d,e,'duplicate_or_unexpected_record_id')

    def test_payload_envelope_id_mismatch(self):
        d,e=snapshot([(116,payload(qid=117))]);self.rejected(d,e,'payload_envelope_id_mismatch')

    def test_envelope_overflow(self):
        d,e=snapshot();d=d[:28]+struct.pack('<I',65536)+d[32:];e['source23_file_sha256']=H(d)
        self.rejected(d,e,'invalid_record_bounds')

    def test_expected_title_schema(self):
        d,e=snapshot();e['expected_titles']['116']=[];self.rejected(d,e,'title_id_set_mismatch')

    def test_bounded_read_and_optional_private_output(self):
        with tempfile.TemporaryDirectory(prefix='source23-tests-') as td:
            root=Path(td);inputdir=root/'inputs';inputdir.mkdir();inp=inputdir/'snapshot.wdb';exp=inputdir/'expected.json';data,expected=snapshot();inp.write_bytes(data);exp.write_text(json.dumps(expected));original=inp.read_bytes()
            with self.assertRaisesRegex(m.Rejected,'input_size_out_of_bounds'):m.read_bounded(inp,10)
            _,decoded=m.extract(data,expected)
            with patch.object(m.tempfile,'gettempdir',return_value=str(root)):
                info=m.write_private(decoded,inp,exp)
            target=root/info['system_temp_subdirectory']/info['filename']
            self.assertEqual(json.loads(target.read_text())['records'][0]['qid'],116)
            self.assertEqual(inp.read_bytes(),original)
            self.assertEqual(target.stat().st_mode & 0o777,0o600)
            self.assertNotIn(str(root),json.dumps(info))

    def test_private_output_inside_input_parent_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with patch.object(m.tempfile,'gettempdir',return_value=str(root)):
                with self.assertRaisesRegex(m.Rejected,'private_temp_root_not_outside_protected_paths'):
                    m.write_private([],root/'snapshot.wdb',root/'expected.json')


if __name__=='__main__':
    unittest.main()
