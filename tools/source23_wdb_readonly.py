#!/usr/bin/env python3
"""Owned strict SOURCE23 WDB intake (stdlib only, read-only input, metadata stdout).

Layout facts: Stein-N/WoW-Quest-Database@8153cf7536636208c91bc88e34082d1dc1bdeac0
etl/questcache.py blob ab70d8f1aee3bc44538e6cbba9012855d9555bbc;
etl/import_questcache.py blob 117409395ec79782b60a7efc6cc912d5f4418a67.
Independent implementation, not an import/execution of that heuristic parser.
No last-plausible/length-only fallback, amount expansion or macro-role inference.
Require one string header and one maximal objective chain whose every other
candidate is an exact boundary/ID suffix. Crossing chains or objective-free
unconfirmed records are HELD.
A unique structure is raw protocol evidence, NOT dialogue/UI-phase/live-game proof.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import sys
import tempfile

MAX_INPUT = 1024 * 1024
MAX_EXPECTED = 256 * 1024
MAX_PAYLOAD = 65536
MAX_RECORDS = 64
FIELDS = (
    ('title', 9), ('logDescription', 12), ('questDescription', 12),
    ('areaDescription', 9), ('portraitGiverText', 10), ('portraitGiverName', 8),
    ('portraitTurnInText', 10), ('portraitTurnInName', 8), ('completionLog', 11),
)
HEADER_LEN = 12
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
MACRO = re.compile(rb'\$(?:[0-9]{1,8}[A-Za-z]{1,3}|[A-Za-z])')


class Rejected(ValueError):
    """Only fixed reason codes: never interpolate input strings, paths or names."""


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise Rejected(reason)


def valid_text(s):
    return all(ord(c) >= 32 or c in '\t\r\n' for c in s) and '\x7f' not in s


def lengths_at(payload, pos):
    value = int.from_bytes(payload[pos:pos + HEADER_LEN], 'big')
    shift = HEADER_LEN * 8
    lengths = []
    for _, width in FIELDS:
        shift -= width
        lengths.append((value >> shift) & ((1 << width) - 1))
    return lengths, value & ((1 << shift) - 1)


def string_candidates(payload, expected_title_hash):
    """Only exact-end, adjacent-header/tail, strict UTF8, known-title candidates."""
    found = []
    plausible_titles = 0
    for pos in range(4, len(payload) - HEADER_LEN):
        lengths, flags = lengths_at(payload, pos)
        if not lengths[0] or not lengths[1] or pos + HEADER_LEN + sum(lengths) != len(payload):
            continue
        offset = pos + HEADER_LEN
        strings, raws = {}, {}
        try:
            for (field, _), size in zip(FIELDS, lengths):
                raw = payload[offset:offset + size]
                text = raw.decode('utf-8', errors='strict')
                if not valid_text(text):
                    raise UnicodeError
                strings[field], raws[field] = text, raw
                offset += size
        except UnicodeError:
            continue
        title = strings['title']
        if not (0 < len(title) <= 120 and title == title.strip() and '\n' not in title
                and '\r' not in title and '\t' not in title and not title[0].islower()):
            continue
        plausible_titles += 1
        if digest(raws['title']) != expected_title_hash:
            continue
        found.append(dict(offset=pos, lengths=lengths, flags=flags, strings=strings, raws=raws))
    return found, plausible_titles


def objective_step(payload, pos, stop):
    """Conservative published structural checks, not a complete enum/quantity schema."""
    if pos < 4 or pos + 43 > stop:
        return None
    objective_id = struct.unpack_from('<I', payload, pos)[0]
    amount = struct.unpack_from('<i', payload, pos + 13)[0]
    effects = struct.unpack_from('<i', payload, pos + 33)[0]
    if objective_id < 1000 or payload[pos + 4] > 30 or not 0 < amount < 10000 or not 0 <= effects <= 8:
        return None
    description_length_at = pos + 41 + 4 * effects
    description_at = pos + 43 + 4 * effects
    if description_at > stop:
        return None
    end = description_at + payload[description_length_at]
    if end > stop:
        return None
    try:
        text = payload[description_at:end].decode('utf-8', errors='strict')
    except UnicodeError:
        return None
    if not valid_text(text):
        return None
    return end, objective_id


def objective_chains(payload, stop):
    """Enumerate chains with node boundary/ID proofs; do not rank by length alone."""
    chains = []
    for start in range(4, stop - 42):
        pos = start
        ids = []
        nodes = []
        while len(ids) < 12:
            step = objective_step(payload, pos, stop)
            if step is None:
                break
            end, identifier = step
            if ids and not 0 < identifier - ids[-1] < 64:
                break
            ids.append(identifier)
            nodes.append((pos, end, identifier))
            pos = end
            if pos == stop:
                chains.append(dict(start=start, end=stop, objective_count=len(ids),
                                   raw_sha256=digest(payload[start:stop]), _nodes=nodes))
                break
    return chains


def unique_maximal_chain(chains):
    """A maximal array must contain ALL candidates as exact node/ID suffixes.

    Never select a merely longer chain over a crossing or different-ID chain.
    Comparing each (start,end,id) tuple proves both boundaries and sequence.
    """
    qualifying = []
    for candidate in chains:
        nodes = candidate['_nodes']
        if all(other['_nodes'] and len(other['_nodes']) <= len(nodes)
               and nodes[-len(other['_nodes']):] == other['_nodes']
               and other['end'] == candidate['end'] for other in chains):
            qualifying.append(candidate)
    return qualifying[0] if len(qualifying) == 1 else None


def macro_positions(raw):
    out = []
    for m in re.finditer(rb'\$', raw):
        token = MACRO.match(raw, m.start())
        out.append(dict(byte_offset=m.start(), marker=token[0].decode('ascii') if token else '$',
                        semantic_role='unconfirmed'))
    return out


def parse_record(qid, payload, expected_title):
    base = dict(qid=qid, payload_bytes=len(payload), payload_sha256=digest(payload))
    title_hash = expected_title.get('title_sha256')
    if not isinstance(title_hash, str) or not HEX64.fullmatch(title_hash):
        return dict(base, status='held_missing_or_conflicting_expected_title', title_match=False), None
    candidates, plausible = string_candidates(payload, title_hash)
    base.update(header_candidates=len(candidates), exact_bound_utf8_plausible_titles=plausible)
    if len(candidates) != 1:
        return dict(base, status='held_ambiguous_header' if candidates else 'held_no_unique_known_title_header',
                    title_match=bool(candidates)), None
    c = candidates[0]
    chains = objective_chains(payload, c['offset'])
    proof = dict(bit_header_payload_offset=c['offset'], bit_header_bytes=12,
                 bit_header_sha256=digest(payload[c['offset']:c['offset'] + 12]),
                 length_bits=[w for _, w in FIELDS], lengths=c['lengths'],
                 uninterpreted_trailing_flags=c['flags'],
                 strings_start=c['offset'] + 12, strings_end=len(payload),
                 exact_header_plus_lengths_to_record_end=True, strict_utf8=True,
                 valid_objective_chain_candidates=len(chains),
                 chain_selection_policy='unique_maximal_only_if_all_others_are_exact_boundary_ID_suffixes; crossing/non-suffix_held',
                 fixed_prefix_schema='uninterpreted; not proof of complete record/enum/objective-count schema')
    base.update(title_match=True, expected_title_sha256=title_hash, header_proof=proof)
    maximal = unique_maximal_chain(chains)
    if maximal is None:
        return dict(base, status='held_ambiguous_objective_chain' if chains else 'held_unconfirmed_objective_chain'), None
    proof['objective_chain'] = {k: v for k, v in maximal.items() if k != '_nodes'}
    proof['other_candidates_proven_exact_suffixes'] = len(chains) - 1
    fields = []
    for name, _ in FIELDS:
        raw = c['raws'][name]
        fields.append(dict(protocol_field=name, raw_bytes=len(raw), raw_sha256=digest(raw),
                           raw_macro_positions=macro_positions(raw),
                           UI_phase_binding='held_not_reward_or_progress_dialogue' if name not in
                           ('title', 'logDescription', 'questDescription') else 'raw_protocol_only_pending_source_review'))
    return dict(base, status='unique_structure_raw_only_pending_review', fields=fields,
                roles_inferred=False, quantities_substituted=False), dict(qid=qid, raw_protocol_strings=c['strings'],
                status='PRIVATE_RAW_ONLY_NOT_APPROVED_TRANSLATION_SOURCE', roles_inferred=False)


def extract(data, expected):
    """Pure bounded byte parsing; metadata plus optional private raw strings, no I/O."""
    require(isinstance(data, bytes) and 32 <= len(data) <= MAX_INPUT, 'input_size_out_of_bounds')
    require(isinstance(expected, dict), 'invalid_expected_json_schema')
    require(type(expected.get('schema')) is int and expected.get('schema') == 1 and expected.get('expected_magic') == 'TSQW'
            and expected.get('expected_build') == 70938 and expected.get('expected_locale') == 'enUS',
            'unsupported_expectation_schema')
    require(digest(data) == expected.get('source23_file_sha256'), 'input_snapshot_sha256_mismatch')
    require(data[:4] == b'TSQW', 'invalid_wdb_magic')
    require(struct.unpack_from('<I', data, 4)[0] == 70938, 'unsupported_wdb_build')
    require(data[8:12] == b'SUne', 'unsupported_wdb_locale')
    envelopes = expected.get('expected_records')
    require(isinstance(envelopes, list) and 0 < len(envelopes) <= MAX_RECORDS, 'invalid_expected_envelopes')
    known = {}
    for v in envelopes:
        require(isinstance(v, dict) and type(v.get('id')) is int and v['id'] > 0
                and v['id'] not in known and type(v.get('payload_bytes')) is int
                and 4 <= v['payload_bytes'] <= MAX_PAYLOAD
                and isinstance(v.get('payload_sha256'), str) and HEX64.fullmatch(v['payload_sha256']),
                'invalid_expected_envelope_entry')
        known[v['id']] = v
    titles = expected.get('expected_titles')
    require(isinstance(titles, dict) and set(titles) == {str(q) for q in known}
            and all(isinstance(v, dict) for v in titles.values()), 'title_id_set_mismatch')
    pos = 24
    seen = set()
    rows, decoded = [], []
    sentinel = False
    while pos < len(data):
        require(pos + 8 <= len(data), 'truncated_envelope')
        qid, size = struct.unpack_from('<II', data, pos)
        pos += 8
        if qid == size == 0:
            require(pos == len(data), 'trailing_data_after_sentinel')
            sentinel = True
            break
        require(qid > 0 and 4 <= size <= MAX_PAYLOAD and pos + size <= len(data), 'invalid_record_bounds')
        require(qid not in seen and qid in known, 'duplicate_or_unexpected_record_id')
        require(len(rows) < MAX_RECORDS, 'record_count_out_of_bounds')
        payload = data[pos:pos + size]
        require(struct.unpack_from('<I', payload, 0)[0] == qid, 'payload_envelope_id_mismatch')
        require(size == known[qid]['payload_bytes'] and digest(payload) == known[qid]['payload_sha256'],
                'record_snapshot_mismatch')
        row, private = parse_record(qid, payload, expected['expected_titles'][str(qid)])
        row['record_payload_file_offset'] = pos
        rows.append(row)
        if private:
            decoded.append(private)
        seen.add(qid)
        pos += size
    require(sentinel and seen == set(known), 'missing_sentinel_or_records')
    counts = {}
    for row in rows:
        counts[row['status']] = counts.get(row['status'], 0) + 1
    metadata = dict(schema=1, status='bounded_raw_structure_intake_only', input_bytes=len(data),
                    input_sha256=digest(data), header=dict(magic='TSQW', build=70938, locale='enUS',
                    bytes=24, raw_sha256=digest(data[:24]), remaining_fixed_header_fields='uninterpreted'),
                    envelopes_validated=len(rows), terminal_zero_envelope_exact_end=True, counts=counts,
                    records=rows, privacy='No raw text, titles, names, paths or player context in metadata.',
                    limits='Raw cache protocol fields only. completionLog/endText/portrait/area are NOT dialogue phase proof. No macro roles/amount substitution/current enabled/wholegame claims.')
    return metadata, decoded


def read_bounded(path, limit):
    require(not path.is_symlink(), 'symlink_input_not_supported')
    with path.open('rb') as handle:
        require(stat.S_ISREG(os.fstat(handle.fileno()).st_mode), 'input_not_regular_file')
        raw = handle.read(limit + 1)
    require(len(raw) <= limit, 'input_size_out_of_bounds')
    return raw


def is_under(path, parent):
    return path == parent or parent in path.parents


def write_private(decoded, input_path, expected_path):
    """Fresh system-temp directory only; never accept arbitrary output paths."""
    temp_root = Path(tempfile.gettempdir()).resolve()
    inp = input_path.resolve()
    forbidden = {inp.parent, expected_path.resolve().parent}
    for ancestor in inp.parents:
        if ancestor.name.lower() == 'cache':
            # Protect the client root and its game-installation parent too.
            forbidden.add(ancestor.parent)
            forbidden.add(ancestor.parent.parent)
    # Ancestor checks only (no recursive file scan); protect repo/code roots.
    for start in [Path(__file__).resolve().parent, Path.cwd().resolve()]:
        for ancestor in [start, *start.parents]:
            if (ancestor / '.git').exists() or (ancestor / 'src' / 'ForeverThai').is_dir():
                forbidden.add(ancestor)
    require(not any(is_under(temp_root, v) for v in forbidden), 'private_temp_root_not_outside_protected_paths')
    folder = Path(tempfile.mkdtemp(prefix='foreverthai-source23-', dir=temp_root))
    os.chmod(folder, 0o700)
    target = folder / 'decoded-private.json'
    raw = (json.dumps(dict(status='PRIVATE_UNREVIEWED_RAW_PROTOCOL_ONLY', records=decoded),
                      ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(raw)
    return dict(created=True, system_temp_subdirectory=folder.name, filename=target.name,
                automatic_upload=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path, help='One exact snapshot file, opened rb only; never a directory.')
    ap.add_argument('--expected', type=Path, required=True, help='Reviewed27-ID hash/envelope manifest.')
    ap.add_argument('--private-decoded', action='store_true', help='Optional raw strings ONLY in fresh protected system-temp folder; no stdout text.')
    args = ap.parse_args()
    try:
        expected = json.loads(read_bounded(args.expected, MAX_EXPECTED))
        require(isinstance(expected, dict), 'invalid_expected_json_schema')
        raw = read_bounded(args.input, MAX_INPUT)
        metadata, decoded = extract(raw, expected)
        if args.private_decoded:
            metadata['private_output'] = write_private(decoded, args.input, args.expected)
        print(json.dumps(metadata, ensure_ascii=True, indent=2))
        return 0
    except Rejected as error:
        print(json.dumps(dict(status='REJECTED_NO_TEXT_OUTPUT', reason=error.args[0])))
        return 2
    except (OSError, ValueError, TypeError, KeyError, struct.error):
        print(json.dumps(dict(status='REJECTED_NO_TEXT_OUTPUT', reason='input_io_or_schema_error')))
        return 2


if __name__ == '__main__':
    sys.exit(main())
