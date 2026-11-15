# MAIN26 source checkpoint — 2026-11-15

This follows MAIN25 source-only work on codex/main25-source-fallback-20261115. Neither overlay is loaded in the current TOC or packaged.

## Actual new coverage

Two new reviewed Thai progress fields / two IDs: 92457 (Starving Arcane, verified query level33) and 78270 (Goblin Lockpicks, level not established; do not invent it).
source_inputs/main26-reviewed-pairs.json contains full source/Thai, hashes, own-ID/phase source positions and meaning review.
source_inputs/main26-reviewed-overlay.lua adds missing 92457.progress and appends an exact variant for 78270.progress, preserving its old canonical/aliases.

One serial isolated Lua5.1 memory verification passed: 2 exact positives,14 changed/wrongID/wrongphase/empty/nil/secret negatives; old78270 canonical/aliases retained; MAIN25 overlay retained. No Lua OS/io/package/require/debug access, local AI, game control, fonts, runtime writes or build. See evidence/main26-source-review-receipt.json.

Across MAIN25+MAIN26: **4 new Thai fields /4 quest IDs**, not four complete quests. They still need Cloud bitmap/combined package integration before any release.

## Exact new-source scope — do not repeat

Fresh GitHub primary issue search found FVO3502–3520,19 issue bodies. Actual17 exported payloads decode to1974 records =1091gossip+805quest+78book. 3506/3507 contain only a new-issue URL; comments are empty. Their title counts306+70 are NOT captured data and were not counted.

MAIN805 occurrences reduce to642 unique forms with163 duplicate occurrences:
447 exact supported,178 diagnostic identity-substitution supported (NOT roleproof),4 blank,9 token-held,4 literal candidates needing full review.
Full read found two literal candidates257.completion/258.description contain unproven player-name fragments. Their original raw strings remain PRIVATE; do not publish a fixed named variant or count them translated. The other two literals above are fully reviewed, no exact existing full-body Thai reuse, now source translated.
Do not infer tokens from normalized exports or overwrite old translations to fit these captures.
NonMAIN gossip/books have not been fulltext audited or translated in this pass.

Efficient Games primary query ea970da071079b32e56f349e09648ff0e314b351 corroborates92457 ownID/title/level, but has no78270 entry in the two inspected caches. The FVO producer contract in MAIN25 ties capture q/e/t/x to the same GetQuestID/GetTitleText and quest phase event (GetProgressText here). Header70938/enUS does not prove per-row version/current enabled use. No whole-game denominator.

## Cloud next step

Read work/CLOUD_MAIN25_SOURCE_HANDOFF.md. Baseline Catalog/Match and combined PRIVATE0.467.0 are unchanged. Preserve Quest/Tracker/optionalQuestie/NPC, Skill/Talent/Profession/Item, all fonts/bitmap assets, options/SavedVariables and exact70938 compatibility fix in every package.

Once the existing Cloud worker can be controlled safely, inspect its head; import these reviewed SOURCE files with one writer. Integrate MAIN25 then MAIN26 overlays append-only, build only additive Thai bitmap coverage on Cloud, check affected fields and combined assets, then produce a real combined PRIVATE ZIP/Thai guide. No version was minted merely for source checkpoints; no Launcher upload has occurred here. Windows/MacM2 in-game acceptance still absent. A previous user-facing preliminary count901 was corrected to actual805.

Next MAIN source work must use genuinely new input/proof: remaining role-held forms only with independent typed/literal source evidence, or new primary issue/cache delta after this bounded set. Do not rerun old524/805, full11144 EG scan, source23decoder, old NPC/books/Skills/fullfont/fulltest suites without a real changed input or error. MAIN24 finite122literal queue is already delivered; don't retranslate it.

No healthy Cloud run was canceled. GitHub source checkpoint is durable even while Cloud desktop control is unavailable. Do not switch or control the user's running game.
