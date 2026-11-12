# Project instructions

- Prefer Codex Cloud for project execution. The user's latest clarification allows Codex Local on their computer as a fallback when Cloud is genuinely blocked. Before switching, inspect and preserve the Cloud task's current work and coordinate a single writer; do not cancel healthy Cloud work just to move it locally. The existing 0.462.0 ZIP transfer is complete.
- Use hosted OpenAI models for reasoning and translation. Do not automatically install or launch Ollama, LM Studio, local model servers, or local AI inference. Keep local commands light and run one local job at a time; prefer Cloud for full font generation and other CPU/GPU-heavy work. Do not repeat unchanged builds or tests without a reason.
- Use the saved `foreverthai-updates` Cloud environment for development. A task started in `Default environment` must remain read-only: verify the transfer and report the dedicated environment requirement rather than starting a second translation worker.
- Read `CLOUD_HANDOFF.md` before modifying addon files. Obtain the two named 0.462.0 release assets; the generated repository source ZIP is not the addon.
- Preserve both transferred packages. The author ZIP omits Skills; the combined PRIVATE-TEST ZIP contains the complete 126-file runtime. Always retain Quest, Tracker, NPC speech, Skill, Talent, Profession, Item, fonts, Questie integration and SavedVariables compatibility together.
- Prioritize corroborated main quest text from low levels upward before stylistic cleanup. Preserve reviewed translations. Do not guess missing English source or placeholder roles, and do not claim full-game completion from a partial inventory.
- Preserve runtime-only matching aliases; do not regenerate Catalog.lua solely from incomplete source generators. Shared matcher changes require meaningful full regression. Report missing historical test harnesses honestly.
- The old local draft 0.463.0 was not transferred or verified. Under the authorized local fallback it may be inspected, but do not merge it or claim it is included or passed without independent checks.
- Do not install into or control the user's game. Distinguish technical simulation from real Windows/Mac M2 in-game testing.
- Customer publication is a separate action from this source transfer. Preserve all package components and validate any release against the standing ten-version publication policy in the handoff.
- Keep credentials, private player captures and unrelated local files out of this public repository.
