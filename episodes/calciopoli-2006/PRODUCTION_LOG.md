# Production log — Calciopoli 2006

## Pipeline
1. Topic chosen from outlier research (`research/outliers_2026-10-01.md`).
2. Arabic script approved → merged additions (intercepts + reactions), Pessotto removed.
3. English narration script: `script_en.md` (107 scenes). Fact check: `fact_check.md` (56 claims).
4. Voice: Higgsfield `text2speech_v2` (ElevenLabs preset "Arthur"), one clip per scene → `production/audio/`.
5. Images: GPT Image 2.5, 2k, 16:9, oil-painting style (see `style_guide.md` LOCKED section) → `production/images/`.
   Real people: signature features + name tags (no exact likeness).
6. Motion: 12 Kling 3.0 clips (5 s, std, no sound) from the key images → `production/clips/`.
7. Overlays and cards: `overlays.py`. Scene assembly: `build.py`. Final: `final.sh`. Shorts: `shorts.py`. Subtitles: `subs.py`.

## Rebuild from scratch
```
cd production
python3 overlays.py
python3 build.py            # all scenes (skips existing)
./final.sh                  # → calciopoli_2006_final.mp4
python3 shorts.py           # → ../shorts/*.mp4
```
Media is gitignored; re-download it from the URLs in `img_urls.json`, `audio_manifest.json` and `clip_jobs.txt`.

## Credits
- Starting balance 6,579.8 → 5,857.35 after production: **~722 credits**.
- Images ~180 × 2.75 · TTS ~98 × 0.45 · Kling 12 × 7.5 · tests and regenerations make up the rest.

## QC pass (1 Oct 2026)
Reviewed all 162 images against the script and facts.
- Regenerated: I0141, I0142 (Moggi's office showed Rome's dome — now Turin with the Mole Antonelliana), I0381 (TV studio showed a Berlusconi-like face), I0861, I0862 (Milan wore their all-white away kit in the 2007 Athens final, not red and black). New Kling clip for I0861.
- Dropped (moved to `production/images_excluded/`): I0022 (captain's armband on #3), I0231, I0243 (Florence skyline in Rome scenes), I0431 (Inter-coloured pennant in Galliani's office), I0601 + clip (Trezeguet wore #20, not #12), I0802 (wrong Juventus shirt numbers), I0952 (portrait didn't look like Facchetti), I0982 (Moggi drawn with full hair).
- Text: S047 on-screen quote now matches the narration ("They have killed my soul.").
- Fix cost: 5 images × 2.75 + 1 clip × 7.5 = 21.25 credits.

## Character pass (from Maitham's reference photos)
Signature features written from the photos; approved tests first, then the rest.
- Del Piero: I0801, I0812, I0821, I0822, I0851 (+ new clip), I0852.
- Lippi (glasses, silver hair, cigar, blue Italy polo): I0541, I0542, I0631, I0632, I0633.
- Cannavaro (buzz cut, forearm tattoos, wide smile): I0041 (+ new clip), I0791, I0792.
- Old versions kept in `production/images_excluded/old_characters/` and `clips_excluded/old_characters/`.
- Cost: 14 images × 2.75 + 2 clips × 7.5 = 53.5 credits.
- Moggi was already done from his photos in the first pass.

## Character pass 2 (reference links from Maitham)
- Bergamo (bald, white sides, rimless glasses, striped shirt): I0181, I0182, I0421, I0422.
- Pairetto (only a 1980s refereeing photo — aged to 53): I0181, I0182, I0421.
- Bettega (white hair swept back, camel coat): I0151, I0152.
- Buffon (slicked-back dark hair, grey 2006 kit): I0552.
- Giraudo: no photo available, kept as a generic grey-haired executive.
- Cost: 7 images × 2.75 = 19.25 credits (including 3 tests).

## Known issues
- No background music. A licensed track is still needed.
- Real people are drawn by signature features, not exact likeness.
