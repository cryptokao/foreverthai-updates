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
