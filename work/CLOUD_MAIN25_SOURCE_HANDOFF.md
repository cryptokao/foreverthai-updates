# MAIN25 source checkpoint — 2026-11-15

Continue main quest coverage before old wording polish. Do not treat this checkpoint as a packaged release.

## Actual new translation work

Two reviewed literal fields for two quest IDs are saved in source_inputs/main25-reviewed-pairs.json, ordered by verified quest-query level: 94829.progress (40), then 94236.completion (60). Exact full English, Thai, source positions, hashes, matching signatures and source API attribution are included. This is not two complete quests.

source_inputs/main25-reviewed-overlay.lua is a candidate append-only data overlay, NOT loaded in the current TOC. It was evaluated once in isolated Lua 5.1 memory: 2 exact positives, 14 altered/wrong-ID/wrong-phase/empty/nil/secret negatives, and existing 94236 canonical/aliases preserved. See evidence/main25-source-review-receipt.json. No runtime or font asset was modified.

## Scope already checked; do not repeat

FVO issues 3488–3501: 14 actual decoded exports, 1760 total records (1150 gossip, 524 quest, 86 book). 475 unique MAIN forms, 49 duplicate occurrences. 364 exact supported, 95 diagnostic identity-substitution supported (not role proof), 12 token-held, 2 blank, 2 new literals above. Raw exports/private character context stay private.

Independent Efficient Games source ea970da071079b32e56f349e09648ff0e314b351 confirms three of the held normalized Hunter descriptions have fixed literal hunter, no identity macros, and are already supported for Druid and Hunter. Evidence main25-raw-literal3-proof.json: no new Thai counted. Remaining nine token forms require genuinely new literal/typed evidence; don't infer roles from normalized exports.

## Baseline to preserve

Cloud source head dfb0b202bc65ca1a125cf3a68901fdc206db09e7; combined PRIVATE 0.467.0 MAIN24 artifact bb7fbd96b5d078a2807bfffe87d2b5fe83806af1.
Catalog SHA256 9958d2edf3096a4cdffd39b5c99a58cc8a1bc3e1729e18b2d09c6f7e0e481118 (16968349 bytes).
Match SHA256 d3cf853e0e7c997652b589993f827e5f7794e2f789e59e484a4ab97e97b24b1d.
Combined ZIP SHA256 dca6283c1fdb7ee6d7abbee07f2f7f9b86ddbdf68e694dcd2b0074ed883d633e.

MAIN24 delivered 122 supported fields/57 IDs: 90 new Thai +31 reviewed verbatim reuse +1 proper-name passthrough, not 57 complete quests. All28 protected Skill/font assets and old runtime were retained. Preserve Skill, Talent, Profession, Item, font/bitmap assets, Tracker/Questie/options/SavedVariables, and exact 70938 fix in every package. Known existing 84213 objective newline guard leaves its Tracker English; don't claim it translated there.

## Next Cloud integration

Cloud desktop control became unavailable after the MAIN24 worker had finished; no healthy run was canceled. App read_thread cannot access that Work chat. Native window targeting did not safely identify Chrome; stopped without UI input or game control. GitHub connector recovered, allowing this authorized light serial source fallback. All translation reasoning used hosted OpenAI, no local AI/heavy builds/font generation.

When Cloud control is available, continue the existing checkout/terminal worker, inspect head first, and pull/cherry-pick these SOURCE files with a single writer. Add the two entries without replacing existing Catalog prefix/canonical/aliases. Generate only necessary additive bitmap coverage on Cloud, then affected panel/Tracker checks and a combined PRIVATE ZIP; inspect exact Skill/Talent/Profession/Item TOC/assets against 0.467.0. Do not publish this unbuilt overlay directly or bump version just for this checkpoint. Windows/Mac M2 in-game acceptance remains outstanding.

Launcher policy: every ten substantive versions with all translated modules; next normal planned milestone 0.470.0, subject to fresh live-feed verification and passing checks. Last historical verified feed 0.463.1 is not a fresh current feed claim. No customer publication was performed in MAIN25.

## Newly discovered next source delta

One fresh primary issue search after this checkpoint found 19 additional FVO captures 3502–3520, outside the above audit. Two short bodies 3506/3507 require their comments to obtain exports. Process only these new inputs as MAIN26, compare before translating, prioritize MAIN and low to high level, keep raw data private. Do not rerun the previous 524 fields, full 11144 EG scan, source23, old NPC/books/Skills/full fonts/tests.
