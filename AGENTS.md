# Project instructions

- Run project commands, scripts, builds and tests exclusively on Codex Cloud. Do not use the user's Windows/Mac, another local chat, or a connected desktop device for execution. The user authorized uploading the existing 0.462.0 ZIPs through the browser; that transfer is complete.
- Use the saved `foreverthai-updates` Cloud environment for development. A task started in `Default environment` must remain read-only: verify the transfer and report the dedicated environment requirement rather than starting a second translation worker.
- Read `CLOUD_HANDOFF.md` before modifying addon files. Obtain the two named 0.462.0 release assets; the generated repository source ZIP is not the addon.
- Preserve both transferred packages. The author ZIP omits Skills; the combined PRIVATE-TEST ZIP contains the complete 126-file runtime. Always retain Quest, Tracker, NPC speech, Skill, Talent, Profession, Item, fonts, Questie integration and SavedVariables compatibility together.
- Prioritize corroborated main quest text from low levels upward before stylistic cleanup. Preserve reviewed translations. Do not guess missing English source or placeholder roles, and do not claim full-game completion from a partial inventory.
- Preserve runtime-only matching aliases; do not regenerate Catalog.lua solely from incomplete source generators. Shared matcher changes require meaningful full regression. Report missing historical test harnesses honestly.
- Local draft 0.463.0 was not transferred or verified. Do not claim it is included or retrieve it from the user's computer.
- Do not install into or control the user's game. Distinguish technical simulation from real Windows/Mac M2 in-game testing.
- Customer publication is a separate action from this source transfer. Preserve all package components and validate any release against the standing ten-version publication policy in the handoff.
- Keep credentials, private player captures and unrelated local files out of this public repository.
