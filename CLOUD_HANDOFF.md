# Alphaverse THAI SUB — Codex Cloud continuation

The user requests continued reviewed Thai translation of all WoW Forever quests and NPC quest dialogue. Main quest coverage takes priority, low level to high level, before polishing old wording. The user's explicit instruction is that all builds, scripts, tests and development execution run on Codex Cloud, never their local PC. Browser upload of the existing files was separately authorized and completed.

## Verified transfer

Repository: cryptokao/foreverthai-updates. The main tree originally contained only README.md. The actual packages are **release assets**, not the automatically generated source-code ZIP for the tag.

Transfer release: https://github.com/cryptokao/foreverthai-updates/releases/tag/v0.462.0-cloud-source

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| ForeverThai-0.462.0-Windows-Mac.zip | 25948703 | 9eb4084c1f6c90d5cc05486b1ecb41951d6e3543cde9fb78b97686df73f81881 |
| ForeverThai-0.462.0-Quest-Skills-PRIVATE-TEST.zip | 17109177 | d36621b9357a33e909777f31fdc5745ddf96aa579add740364ac60011f30cb62 |

The GitHub asset API independently reports these exact digests and uploaded state. Download both named assets from the release, verify hashes again on Cloud, inspect paths for safe extraction, then inspect their contents and development metadata before deciding which tools are present.

The author ZIP and combined runtime ZIP serve different purposes. Preserve the combined package's complete Quest/Tracker/Skill/Talent/Profession/Item/font set when preparing any later build. The combined 0.462.0 baseline had 126 runtime files and 28 protected Skill/font assets; validate the actual manifest and TOC rather than treating those counts alone as proof.

## Known verified baseline, not new Cloud test results

Private 0.462.0 passed technical simulation before transfer: 686 reviewed speech forms on two pinned client UI builds (70862 and 70888); nine Skill/Talent fixtures; preservation of 102301 previous Thai font runs; combined package/126 installed files; isolated Windows Launcher 0.5 update fixture 0.461.0 to 0.462.0. These are historical checks, not proof of real game behavior or a Cloud rerun.

0.462.0 added eight typed current-player-name speech templates for Volcor (quest995 L20), Shakes O'Breen (quest670 L40), Captured Arko'narin (5203 L55), Arei (4261 L56) and Ranshalla (4901 L59). Existing Thai text must be retained. It did not add new main quest fields.

Private 0.461.0 added eleven historically corroborated continuation pages for three books. Current Forever full-book page ordering remains unproven; don't label these complete current-client books.

Draft 0.463.0 exists only on the user's local disk, is untested, and is NOT included. Do not claim it was transferred, passed, or released. Do not access the user's machine to retrieve or execute it. Continue from the verified 0.462.0 transfer and keep any reconstructed work separately identified.

## First concrete Cloud work

1. Clone this repository on Cloud, read its instructions and inspect the transfer packages. Record SHA-256, file lists, TOC load paths, font references, Skill/Talent/Profession/Item assets and any source/test harness gaps. Do not run project commands on a connected local device.
2. Establish an editable Cloud checkout from the transferred source without deleting runtime-only matching aliases. Recover/prepare meaningful automated checks in Cloud from the actual available sources. Preserve the prior combined runtime assets byte-for-byte unless a reviewed change requires replacing them.
3. Prioritize new corroborated English main quest fields from current Forever sources, then corresponding Thai translation. Preserve reviewed wording. No guessed quest prose, placeholder types, class/race roles or fake completion percentages. If a source phase is missing, identify it precisely and keep existing English fallback.
4. Optional pending functional gap after main-source work: NPC lines addressing a different party member. The user plays Alliance Night Elf Druid with a Hunter partner on Mac M2. Existing identity matching is current-player only. Any group-name implementation must be speech-specific, independently qualify exact Player-target templates, validate current party/raid player unit identity, and leave quest/gossip/Tracker identity matching unchanged. Never generalize fixed NPC names Ringo/Torta, arbitrary chat argument5 (playerName2), or unproven race/class slots. Shared matcher edits require full regression.
5. Produce a reviewable branch/PR or Cloud artifacts with an honest technical report. Keep progressing on substantive translation coverage and source gaps; do not substitute a version bump or setup-only report for completed translation work.

## Source leads and remaining scope

Latest pre-transfer check at 2026-11-12T10:38:42Z found:
- https://github.com/quinn-dougherty/forever-vo : latest issue3418, last20 export payloads unchanged.
- Questie/QuestieDB commit4605a11cf1fe4f47aef1ab398b0e55e32ae5c685.
- JIVESCORP/eg-link-output-wowf commit3067c6919046428152f2152fa551f44a8c215d79.

These are leads, not a claim they remain current. Recheck from Cloud. Retained current source words and exact historical primary callers are different kinds of evidence; don't claim historical caller code proves the current private server implementation.

Last known inventory was 6150 quest IDs, 6149 usable source/Thai IDs, 5011 complete main-source records and 1138 partial records. This does not establish current whole-game completeness. Current Forever inventory, missing phases/typed slots, readable pages, custom NPC dialogue, and actual Windows/Mac M2 in-game acceptance remain open. Main quest completions6076/5642/5643 had changed current bodies whose slot types were not independently corroborated; do not infer them from similar old text.

## Distribution and naming

- Product: Alphaverse THAI SUB, free, separate addon from Alphaverse XP.
- Runtime folder/SavedVariables compatibility: ForeverThai; optional Questie integration; preserve settings.
- Every package must include Quest, Tracker, Skill, Talent, Profession, Item, Thai fonts and existing NPC speech together. Repeated missing Skill assets have broken customer updates.
- Customer Cloud feed remained 0.460.0, next standing publication milestone0.470.0, every ten versions. This transfer is a pre-release and does not change customer feeds.
- Cloud feed: https://foreverthai-download.yukimikulovelove2.chatgpt.site/latest.json
- Public460 combined ZIP: https://foreverthai-download.yukimikulovelove2.chatgpt.site/ForeverThai-0.460.0.zip ; 17095554 bytes ; SHA-256 f907b9f51fe8d285bb3d1398c787141a096eb62aca18b00ea268a9241185a397.
- The legacy GitHub latest release remains0.359.0. Never mistake that legacy feed for the newer Cloud feed.
- Do not alter Alphaverse XP CurseForge project1797869. A later visible browser tab identified Thai Sub project1798317, but no further CurseForge update is requested here.
- Do not install over the user's game, control their game or other local computer, expose credentials/private captures, or claim in-game testing without actual evidence.
- Do not promise absolute anti-copy protection.
