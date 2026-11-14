# SOURCE23: bounded own WDB decoder for Root review

The dedicated Cloud worker wrote this standard-library helper. Cloud does **not** have the user's WDB and has not run it on that input. Root may review and perform the one authorized light local extraction; no third-party parser is imported or executed. No addon/runtime, game, model or network operation is in the helper.

Files:

- `tools/source23_wdb_readonly.py`: one-file reader, default metadata-only stdout.
- `source_inputs/source23-expected-title-hashes.json`: exact snapshot/envelope pins and title hashes for only the27 supplied IDs; no title/player text.
- `source_inputs/source23-local-cache-envelope-metadata.json`: Root's original safe metadata, preserved.
- `evidence/source23-public11-audit.json`: separate public historical input comparison, not local decode results.
- `tests/source23/test_wdb_readonly.py`: Cloud synthetic structure/selection/privacy tests only.

## One invocation after code review

Use a private temporary working folder outside the game and repository. `INPUT_WDB` below means the already-identified exact source file, not a directory. This is an instruction for the separately authorized Root fallback, not a claim that Cloud executed it.

```text
python -B source23_wdb_readonly.py INPUT_WDB --expected source23-expected-title-hashes.json
```

Default: read-only input, metadata JSON on stdout. It contains IDs, field names, byte lengths, SHA256s, raw macro **byte** positions, title-match and structural proof only; no raw English, title, player names, account paths or context. Capture metadata only in private Temp and screen it before sharing. Do not put raw input/cache into GitHub.

If selected raw fields will be needed for privacy review, add `--private-decoded` to that **same single invocation**, rather than running twice. This optional flag writes raw strings only into a fresh `foreverthai-source23-*` folder under the system temporary directory (directory0700/file0600 creation modes). It refuses a temporary root inside the input directory, detected Cache/client/game parent or repository. It accepts no arbitrary output path. The metadata reports only the random subdirectory/filename, not an account path. Windows access remains subject to the user's normal private Temp ACLs. Nothing is uploaded automatically. Inspect/redact locally; return only screened metadata or selected qualified text.

## Binding and qualification

- Exact input SHA256 `2c8412fd62dda79bafdb716ee425eafe38d84c94c3f0aead5a5d358460615554`; expected28512bytes,27record envelope lengths/IDs/hashes and terminal zero envelope. Maximum input1MiB, regular nonsymlink file; no directory recursion.
- TSQW,24-byte file header,70938,enUS. Other fixed header bytes are hashed and left uninterpreted.
- Expected title hashes come only from existing QuestieDB `4dbb82440a27856f8dccf57094a5d792cdc7cc9b` and EG `e0f8585914c134d9cb5d76756bd065b1e3e92ece`, scoped to these27IDs.26 have a unique known title;177 has conflicting title hashes and stays held. No source pull/title repair or inferred playability.
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

Public11 audit ran **once** against current Catalog43ec:33fields=32already supported exact+1held raw `$c` description92645;0ready literal/0newThai. No current inventory or per-record70938 claim for those historical records.

Cloud synthetic tests passed26 methods (including separately labelled candidate-selection decision-boundary injections, not26real cache records). The corrected two-objective binary fixture is positive; genuine crossing-chain decision boundary and multiple-header boundary are negative; Unicode-before-`$N` verifies byte offset10. No local WDB/addon/Skills/NPC/party/font suites or game execution occurred. See the exact helper/test/hash report in `evidence/source23-decoder-synthetic.json`.

Runtime remains the delivered0.466.0 MAIN21r1 set:141files, protected28, Catalog43ec,70938Core/Speech/Questie/settings. Books22 is still held and its removed payload is not restored. No font/version/ZIP/feed work in SOURCE23. Full GOAL remains unproven.
