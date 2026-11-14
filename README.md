# foreverthai-updates

Public Alphaverse THAI SUB / ForeverThai packages. Launcher source is maintained separately.

## Codex Cloud development

[0.462.0 source and combined packages](https://github.com/cryptokao/foreverthai-updates/releases/tag/v0.462.0-cloud-source) are available as named release assets. Read [CLOUD_HANDOFF.md](CLOUD_HANDOFF.md) for hashes, setup, preserved components, known gaps and continuation priorities. The tag's automatically generated source-code archive contains repository documentation, not the addon packages.

Use the combined `ForeverThai-0.462.0-Quest-Skills-PRIVATE-TEST.zip` when preserving Skill, Talent, Profession, Item and font assets. The separate Windows-Mac author package contains development evidence and omits Skills. Keep both original packages intact.

Prefer Codex Cloud for development, builds and tests. The user allows Codex Local as a fallback when Cloud is blocked: use hosted OpenAI reasoning, avoid local AI inference and CPU/GPU-heavy jobs, and coordinate current Cloud changes before switching. Read [GOAL.md](GOAL.md) and [AGENTS.md](AGENTS.md) for the current scope and constraints. The transfer is a pre-release; it does not change customer Launcher manifests. Translation coverage and Windows/Mac M2 in-game verification remain incomplete.

## Cloud editable runtime

`src/ForeverThai` preserves the complete verified PRIVATE-TEST 0.462.0 runtime,
including Skills, Talent, Profession, Item and fonts. The import commit is
`231f4a7`; subsequent translation changes can be reviewed against that commit.

Cloud batch 01 adds 34 missing quest objective fields from pinned Forever build
70888 query text. Read `DEVELOPMENT-TH.txt` and `evidence/` for exact sources,
remaining source gaps and new Cloud regression results. This is private review
work, with no customer-feed update and no claim of full-game or in-game coverage.

Read [BATCHES.md](BATCHES.md) for batches 02–12, independent unequal-counter regression, recovered nine-case Skill UI results, exact private candidate hashes and the remaining source queue. The original 34 fields are retained and are not counted again.

NPC replay is recovered: the current combined12 exact-ZIP result is in `evidence/party-speech-regression12.json` (686 independent forms on builds70862/70888 and16qualified party templates across7NPCs). Relevant pinned Chat/Unit API proofs are recorded separately; full UI archives are not a live-game test. See `evidence/candidate12-delivery.json` for immutable ZIP/Thai guide/manifest links and byte readback. Earlier candidate reports remain scoped to their own hashes.

## Current handoff after combined candidate12

Candidate12 retains all136runtime files,28protected Skill/font assets,TOC24paths,SavedVariables and Questie compatibility. Compared with11 only the reviewed Kristof Catalog binding and private Speech whitelist16 differ;134other files are unchanged. Batch12 adds0Thai/prose:1exact reuse binding and8additional existing Player-target qualifications. No PCdraft runtime was merged; customer feed/runtime version is unchanged.

Remaining evidence is in [current-missing-inputs12.json](evidence/current-missing-inputs12.json):73main field/source variants (59alreadyhavecanonical,14placeholders/repurposed historical fields),5new supporting role holds, and older exact queue references. These are not73untranslated quests or a whole-game denominator. Both Druid literal canonicals already work; normalized$c roles remain held after bounded primary-role corroboration.

The user has no further source/maintainer link currently (`evidence/user-source-availability.json`). Real Windows/MacM2 tests are **not yet tested/unverified**, not failed (`evidence/user-game-test-status.json`). Do not repeat the same question, unchanged searches/Harvest audits or suites to hide the gap, or claim GOAL.md is complete. Use existing collectors only; privately review/minimize relevant SavedVariables before any public evidence, never automatically publish raw player names.
