# SOURCE23 v2: frozen217-record input, first extraction still pending

**v1 (28512bytes/27records) was superseded before ANY actual decoder execution. Do not run the old27-ID config.** Raw v2 bytes are frozen in private system Temp; use that frozen copy, never the changing live game cache. Old v1 metadata/config/report are preserved unchanged as historical inputs.

The dedicated Cloud worker wrote this standard-library helper. Cloud does **not** have the user's WDB and has not run it on that input. Root may review and perform the one authorized light local extraction; no third-party parser is imported or executed. No addon/runtime, game, model or network operation is in the helper.

Files:

- `tools/source23_wdb_readonly.py`: one-file reader, default metadata-only stdout.
- `source_inputs/source23-v2-expected-title-hashes.json`: exact frozenv2 snapshot/envelope pins and title hashes for all217 supplied IDs; no title/player text. The old `source23-expected-title-hashes.json` is UNUSED/SUPERSEDED v1.
- `source_inputs/source23-local-cache-v2-envelope-metadata.json`: Root's safe v2 metadata. Original27-record metadata is preserved for history only.
- `evidence/source23-public11-audit.json`: separate public historical input comparison, not local decode results.
- `tests/source23/test_wdb_readonly.py`: Cloud synthetic structure/selection/privacy tests only.

## One invocation after code review

Use a private temporary working folder outside the game and repository. `INPUT_WDB` below means the already-identified exact source file, not a directory. This is an instruction for the separately authorized Root fallback, not a claim that Cloud executed it.

```text
python -B source23_wdb_readonly.py INPUT_WDB --expected source23-v2-expected-title-hashes.json
```

Default: read-only input, metadata JSON on stdout. It contains IDs, field names, byte lengths, SHA256s, raw macro **byte** positions, title-match and structural proof only; no raw English, title, player names, account paths or context. Capture metadata only in private Temp and screen it before sharing. Do not put raw input/cache into GitHub.

If selected raw fields will be needed for privacy review, add `--private-decoded` to that **same single invocation**, rather than running twice. This optional flag writes raw strings only into a fresh `foreverthai-source23-*` folder under the system temporary directory (directory0700/file0600 creation modes). It refuses a temporary root inside the input directory, detected Cache/client/game parent or repository. It accepts no arbitrary output path. The metadata reports only the random subdirectory/filename, not an account path. Windows access remains subject to the user's normal private Temp ACLs. Nothing is uploaded automatically. Inspect/redact locally; return only screened metadata or selected qualified text.

## Binding and qualification

- Exact input SHA256 `26612489c7f5015c7958b84703b295760b7096c058a00c3c170ff3ae6a6baf00`; expected228447bytes,217record envelope lengths/IDs/hashes and terminal zero envelope. Maximum input1MiB, record ceiling217 plus exact manifest ID/payload set, regular nonsymlink file; no directory recursion. New compact manifest158581bytes fits unchanged MAX_EXPECTED262144bytes.
- TSQW,24-byte file header,70938,enUS. Other fixed header bytes are hashed and left uninterpreted.
- Expected title hashes come only from existing QuestieDB `4dbb82440a27856f8dccf57094a5d792cdc7cc9b` and EG `e0f8585914c134d9cb5d76756bd065b1e3e92ece`, scoped to these217IDs.209 have a unique known title;167/169/174/177/180/181/275/305 lack a unique supported title binding and stay held. No source pull/title repair or inferred playability.
- Require one known-title/strict-UTF8 bitheader with **header offset+12+sum(nine lengths)=exact payload end**, strings immediately adjacent to the header. Never choose a last-plausible header.
- Enumerate bounded objective chains. Accept a **unique maximal** chain only when every other candidate is an exact suffix with the same `(start,end,id)` nodes/end. Ordinary multi-objective full-chain/suffix pairs are accepted; crossing/different-ID/non-suffix competitors are held. No merely longest or best-looking candidate is chosen.
- Zero/unconfirmed chains and unsupported structures remain held. Unknown fixed-prefix/complete enum/count schemas are not claimed verified by this structural check. Raw protocol fields are pending review, not automatic translation approval.
- Never expand `$1oa` or any quantity, bind `$N/$c/$R`, normalize text or use reader identity. Macro offsets refer to original UTF8 **bytes**. The binary objective amount is not used to replace source placeholders.
- Raw field order/widths: title9,logDescription12,questDescription12,areaDescription9,portraitGiverText10,portraitGiverName8,portraitTurnInText10,portraitTurnInName8,completionLog11 (7 remaining bits uninterpreted). These are facts read from the pinned primary layout, not positional guessing from prose.
- In particular, completionLog/endText is **not** GetRewardText completion dialogue. No accept/progress/completion/portrait dialogue mapping is invented. Area/portrait/completionLog fields remain UI-phase-unconfirmed; even title/logDescription/questDescription require raw source/privacy review before any runtime use.

## Primary references and current results

Stein-N/WoW-Quest-Database `8153cf7536636208c91bc88e34082d1dc1bdeac0`:

- `etl/questcache.py` blob `ab70d8f1aee3bc44538e6cbba9012855d9555bbc` (layout facts; heuristic fallback deliberately not used).
- `etl/import_questcache.py` blob `117409395ec79782b60a7efc6cc912d5f4418a67` (objective-chain/title validation; not executed).
- `etl/corrections/questcache/forever/enUS.json` blob `f5ec184d900446ab8303c5b073b0b3fccb3da937`:11IDs at historical build70124. Source mapping name→title, objectivesText→log objective, details→description only.
- Pinned README/LICENSE identify GPL-3.0 for the repository. Collector/code licensing is not represented as blanket permission for underlying game text. No upstream code is vendored/executed in this owned helper.

Historical public11 audit ran **once** (not rerun for v2) against current Catalog43ec:33fields=32already supported exact+1held raw `$c` description92645;0ready literal/0newThai. No current inventory or per-record70938 claim for those historical records.

V2 Cloud synthetic tests passed27 methods (the affected26 plus one217/218-record/manifest-size boundary check) (including separately labelled candidate-selection decision-boundary injections, not217real cache records). The corrected two-objective binary fixture is positive; genuine crossing-chain decision boundary and multiple-header boundary are negative; Unicode-before-`$N` verifies byte offset10. No local WDB/addon/Skills/NPC/party/font suites or game execution occurred. See the exact helper/test/hash report in `evidence/source23-v2-decoder-synthetic.json` (old v1 report retained as history).

Runtime remains the delivered0.466.0 MAIN21r1 set:141files, protected28, Catalog43ec,70938Core/Speech/Questie/settings. Books22 is still held and its removed payload is not restored. No font/version/ZIP/feed work in SOURCE23. Full GOAL remains unproven.
