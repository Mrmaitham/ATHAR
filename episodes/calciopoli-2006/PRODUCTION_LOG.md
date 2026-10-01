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

## Known issues
- No background music. A licensed track is still needed.
- Real people are drawn by signature features, not exact likeness.
