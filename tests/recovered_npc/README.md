# Recovered historical NPC speech replay

`check_speech_v04230.py` was read as text from the original quest work folder and transferred for Cloud porting. Original disk SHA-256: `bdcf2ff10c973ab90cd372cfbd8f9416805f1fb0167be0d3e2d8a08193977b58`. Verify the recovered bytes before claiming byte identity. No local tests or local AI were run during recovery.

Do not execute this historical wrapper unchanged. It imports `forever_speech_source`, reads the old work folder/source corpus and Blizzard UI archives, and selects old version-specific Catalog delta helpers. Those dependencies are not supplied here. The current combined candidate retains version 0.462.0 but has new append-only Catalog/Atlas data; comparing it as an untouched old author ZIP would be wrong.

Port the actual Lua fixture and its positive/negative event assertions, setting/deduplication/timer/bounded-history/opt-in-capture/secret-value gates and real bitmap checks to the current Cloud candidate. Keep the original reference intact. First inspect source/evidence records already present in the verified 0.462.0 author ZIP (Dev/NPCSpeech-* plus related source/review documents). Build an independent explicit replay corpus from reviewed English/Thai/NPC/event records, not expected outputs read back from runtime SpeechData. Record exact row counts and missing source/dependency evidence rather than asserting all historical 686 forms by assumption.

Preserve fixed NPC-to-NPC names (Ringo/Torta) and typed player-name restrictions. Do not generalize untyped escort lines. Existing Cloud baseline preservation and pixel-shape checks can cover historical comparison wrappers where applicable; report their scope separately. If Blizzard UI API archives are unavailable, the runtime simulation may run without claiming the missing API-documentation proof was freshly verified. Keep all in-game Windows/Mac M2 flags unverified.

Run the port on Cloud after the current main-quest batch is committed. This reference adds test recovery only and does not count as translated quest content or authorize changing the customer feed.
