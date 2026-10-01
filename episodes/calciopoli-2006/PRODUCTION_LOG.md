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

## Known issues
- No background music. A licensed track is still needed.
- I0022: the captain's armband sits on #3.
- I0141/I0142: the Rome dome is visible from an office meant to be in Turin.
- I0952: the framed portrait doesn't look like Facchetti.
- Clip I0611: the Trezeguet kit number is not his real 2006 number.
