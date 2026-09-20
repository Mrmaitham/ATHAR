# Production Log — Roberto Baggio: The Man Who Died Standing

## Final video
**https://d2ol7oe51mr4n9.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/8cee0e9b-c355-46a9-bf87-770759c2860d.mp4**

- 1920x1080, 30fps, h264/aac, 15:29 runtime.
- 34 scenes (33 generated illustrated/data-graphic scenes + title card), each scene's video length equals its narration clip's exact duration — scene/audio sync is exact by construction, not approximated.
- Voice: Arthur (ElevenLabs via Higgsfield, locked in `references/style_guide.md`).
- Visuals: Recraft vector (portraits) + GPT Image (data-graphics), per the locked style guide.
- Built with FFmpeg (Ken Burns zoompan per scene, concat, final encode) inside a Higgsfield cloud sandbox (`sandbox_exec`), not locally — this repo's local environment cannot reach the asset CDN or run a job this size.

## Bug found and fixed during production
The first assembled cut (`.../cbe09c38-....mp4`, sent earlier in this session) was **silent** — the title-card clip was the first item in the FFmpeg concat list and had no audio stream, which made `ffmpeg`'s concat demuxer drop audio from the entire output. Fixed by giving the title card a matching silent audio track before concatenating, then re-encoding and re-uploading. **The link above is the corrected version; the earlier link should be discarded.**

## Captions
- `subtitles_en.srt` — real word-level timestamps from a Whisper transcription of the final mix (accurate sync), with proper-noun ASR errors corrected by hand (e.g. "Badgio"→"Baggio", "Nietzschean"→"Nichiren", "Tafferell"→"Taffarel", "Trapertoni"→"Trapattoni", "Ballon Door"→"Ballon d'Or").
- `subtitles_ar.srt` — Arabic translation, timed per-scene (34 cues) using the exact scene boundaries from the build, not word-level (word-level parallel timing doesn't transfer across languages).
- Both are **soft subtitle files, not burned into the video.**

## Known gaps vs. the full SKILL.md checklist (not yet done)
- **No background music bed** — Higgsfield's music model is restricted to its game-generation pipeline; no royalty-free track was sourced for this pass. Flagging rather than guessing at a workaround.
- **No thumbnail, title/description/tags, or 3 Shorts yet** (Skill step 6).
- **Runtime is 15:29**, short of the 20–30 min target — natural TTS pacing came in faster than the script's estimated word-per-minute rate. Options: pad with slower graphic holds, or extend the script.
- Formal QC pass (Skill step 7) not yet run end-to-end on the corrected file.
