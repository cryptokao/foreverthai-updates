# Recovered Skill UI fixtures for Cloud

These are copies of existing local test sources, recovered because the Cloud transfer lacked the historical Skill UI harness. No test, addon code, local AI model, or font generation was executed on the user's computer to create this transfer. Only four text files were copied and hashed.

`manifest.json` records the copied bytes. Verify it after extraction on Cloud. Keep the originals unchanged and place any portable Cloud runner separately. These current source snapshots are not, by themselves, evidence that a historical test result has been reproduced.

The three `tests/` modules depend on Python's standard library, `lupa.lua51`, and each other. They model the UI without operating a real game. Their default `ROOT` expects `addon/ForeverThai`; adapt or patch it to a temporary stage containing the current complete runtime. Do not run every test indiscriminately: some unrelated tests expect author-only capture files omitted from the runtime package.

Recover and run the nine named cases originally selected by the combined-package check:

- RecipePanelTests.test_all_compiled_reviewed_recipe_names_obey_exact_lookup_gates
- RecipePanelTests.test_recipe_list_hover_matches_current_rank_and_clears_on_recycling
- RecipePanelTests.test_toc_loads_name_data_and_companion_in_dependency_order
- ItemTooltipTests.test_real_compiled_effect_through_tooltip_callback
- ItemTooltipTests.test_wrong_kind_wrong_item_and_replaced_live_text_fall_back
- ItemTooltipTests.test_reviewed_base_casts_require_full_native_text_and_preserve_visible_values
- SpellbookMetadataTests.test_profession_helper_titles_require_the_current_native_player_spellbook_entry
- SpellbookMetadataTests.test_combat_reader_translates_only_exact_native_action_cards
- SpellbookMetadataTests.test_completed_talent_reads_visible_requirements_and_preserves_native_tooltip

`reference/check_combined_launcher.py` is an unchanged reference for the complete TOC startup replay, the nine selected tests, and specific Stoneform / Devotion Aura rank 2 / Perception regressions. Its original packaging helper and two-archive/receipt wrapper are not bundled. Do not run it unmodified or substitute an old author ZIP for the current modified addon. Port the checks to current source and current candidate ZIP, preserving their assertions rather than weakening them to obtain a pass.

Important details in that reference:

- Use the real complete TOC and one namespace; retain quest translation, Questie settings, saved variables, Skills startup, and both slash commands.
- Stoneform must draw the Thai texture atlas even when SetFont reports success, covering the previously reported boxes.
- Devotion Aura rank 2 must retain 160 armor / 30 yards and preserve the original native tooltip.
- Perception must show its reviewed Thai on builds 70862 and 70888, clear when needed, reject changed source words, and retain unsupported-build/locale gates.
- Some standalone recipe mocks intentionally use explicit font mode. The old runner patches their LuaRuntime factory to set ForeverThaiDisplayMode="font"; preserve that fixture intent, while testing the actual bitmap path separately.

Run on Cloud, record exact source/candidate hashes and the tests actually executed, and report failures honestly. This transfer contains no NPC-speech harness and does not prove the historical 686-speech suite or real Windows/Mac M2 game behavior. It is a development-only input, never an addon module or customer Launcher payload.
