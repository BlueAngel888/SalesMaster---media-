# Sales Master clip engine

- `lux.py` — black & white luxury backgrounds + word-by-word captions (exact spoken words, timed from ElevenLabs word timings).
- `cta_gold.py` → `cta_gold.png` — gold 3D CTA overlay; usage: python3 cta_gold.py "LINE 1" "LINE 2" out.png (default "BUY NOW · $199"). Variants: cta_gold_199.png, cta_gold_free.png.
- `words_dayNN.py` — word timings per clip (original 1.0x voice; clips use the voice at 1.25x).
- `pinned.py` — the pinned "what's inside" clip (product shots + luxury shots).
- `house.py` — simple original house loop (not used by default).
- Voice: ElevenLabs "Adam - Dominant, Firm" (eGSd0uV8dNQnZuEEX9lu), model eleven_v4, 1 take, sped up 1.25x.
