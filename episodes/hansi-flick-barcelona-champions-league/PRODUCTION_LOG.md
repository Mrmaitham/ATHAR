# Production Log — Is Hansi Flick Really the Man to Finally Give Barcelona Their Champions League?

## Final video
Local: `final_video.mp4`
Hosted: https://d2ol7oe51mr4n9.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/b298f61f-0f77-4074-9546-ef20816193f6.mp4

- 1920x1080, h264/aac, **8:47.7 runtime** (527.7s).
- 16 narrated scenes + 1 outro bumper (17 total), each scene's video length equals its narration clip's exact duration — scene/audio sync is exact by construction.
- Voice: Arthur (ElevenLabs via Higgsfield `text2speech_v2`, locked in `references/style_guide.md` at repo root).
- Visuals: duotone photographic cutout portraits (9 scenes) + Tifo-style chalkboard/data-graphic scenes (7 scenes), all `gpt_image_2_5`, per the style guide locked this session.
- Built with FFmpeg (Ken Burns zoompan per scene, concat, final encode) inside a Higgsfield cloud sandbox (`sandbox_exec`) — this repo's local environment cannot handle a render/upload of this size, per the lesson from the Baggio episode.

## ⚠️ Runtime came in short of the 10-15 min target
Script was written and word-counted to land at an estimated ~10.5-11.5 min based on the reference's ~130-140 wpm pacing. The actual ElevenLabs TTS delivery came in faster than that estimate — same gap flagged in the Baggio production log ("natural TTS pacing came in faster than the script's estimated word-per-minute rate"). Not fixed in this pass; flagging per QC policy rather than padding the script artificially. Options for next time: measure actual TTS pace from a short test clip before finalizing scene-duration budgets, or write toward the *top* of the target range to leave margin.

## Captions
- `subtitles_en.srt` and `subtitles_ar.srt` — **61 cues each**, phrase/sentence-level (not per-scene, not word-level), timed by allocating each scene's exact known duration proportionally across its sentence groups by character length. This is a step up from the Baggio episode's per-scene-only Arabic timing, per this session's style-guide update, though it is a proportional estimate rather than true per-word ASR timing (word-level ASR timing was captured via Whisper on the full mix for validation, but sentence-level text was substituted for the raw ASR transcript to avoid the proper-noun misspellings Whisper produced — "Flix" for "Flick", "Adayemi" for "Adeyemi" — the same class of error corrected by hand in the Baggio episode).
- Both are **soft subtitle files, not burned into the video.**

## Known gaps vs. the full SKILL.md checklist (not yet done)
- **No background music bed** — same Higgsfield limitation noted in the Baggio log (its music model is restricted to the game-generation pipeline). Not sourced from elsewhere this pass.
- **Thumbnail concept, title, description, tags, and 3 Shorts are planned in `metadata.md` but not yet rendered/cut.**
- **Formal end-to-end QC pass**: spot-checked (audio not silent — confirmed via `volumedetect`, mean level -14.8dB, no clipping; correct 1920x1080 h264/aac stream layout; 5 of 16 scene images visually reviewed for style-guide adherence) rather than reviewed frame-by-frame across the full 8:48.

## Visual identity note
This episode uses the **duotone photographic** portrait style (dark green-to-black background, dynamic-pose cutout, bold name-tag box) approved this session on a Paolo Maldini test — a deliberate change from the Baggio episode's locked vector-illustration style. See `references/style_guide.md` at repo root for the full rationale and the "photoreal recognizable person" risk Maitham chose to accept.
