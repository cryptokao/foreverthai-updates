# Exact bounded 0.468.0 build snapshot

This is the actual successful build script, not a generic release pipeline. It created four translated fields with one small new font page (19 word glyphs,19 run mappings); retained all old runtime engines, all28 protected Skill/font files and112 old font files; verified all148 ZIP files. Wall5.365s, CPU5.078s on one serial local fallback job. Hosted OpenAI translated; no local AI or full font/test suite was run.

The first attempt stopped before writing a ZIP because an existing provenance file is named SOURCES-TH.txt rather than SOURCES.txt. That path was corrected; the successful script here refuses to overwrite a nonempty output directory.

Do not rerun this build merely to reconfirm unchanged output. Receipt and whole-archive SHA bind the existing verified ZIP. If reproducing for an actual changed input, use a private temporary layout (never a game folder):
- parent/: main25-reviewed-pairs.json,main26-reviewed-pairs.json and both reviewed-overlay.lua files, copied from source_inputs/
- parent/package-main25-26/: this snapshot's build_private_0468.py,font_shapes_bounded.py,run-reuse-proposal.json,existing-run-chains.json
- same package directory: ForeverThai-0.467.0-baseline.zip, the immutable combined artifact bb7fbd96b5d078a2807bfffe87d2b5fe83806af1, SHA dca6283c1fdb7ee6d7abbee07f2f7f9b86ddbdf68e694dcd2b0074ed883d633e
- baseline-Sarabun-Regular.ttf must be extracted unchanged from that ZIP's ForeverThai/Fonts/Sarabun-Regular.ttf
- font-deps/: temporary wheel libraries freetype-py2.5.1 and uharfbuzz0.57.0 (platform-correct wheels), with existing Pillow and lupa.lua51; no models/NLP package required
- build-0.468.0/ must not already contain output.

19 word boundaries and exact existing-run chains were reviewed as data. The retained shaping implementation uses the original 34px Sarabun/HarfBuzz metrics and56px cell height. All19 new glyph crops and89 reused glyph crops were pixel/bounds checked; all four actual BitmapLayer draws had zero Thai live-font fallback. The PNG is a simulation, not game evidence.

The separate TOC check compiled all26 listed Lua files and executed the actual changed data order Catalog -> MainQuest2526 -> Match -> Atlas -> AtlasMain2526 -> Bitmap; all4 source pairs matched. No full UI/old Skill suite was rerun. Real Windows/Mac M2 acceptance, current enabled quest inventory and customer publication remain unproven.
