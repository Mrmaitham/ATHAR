# Production Log — Is Hansi Flick Really the Man to Finally Give Barcelona Their Champions League?

## Final video (v3 — current)
Local: `final_video.mp4`
Hosted: https://d2ol7oe51mr4n9.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/137e7baf-69e7-49e2-aa5c-815345ec17ae.mp4
(v2, superseded: https://d2ol7oe51mr4n9.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/b99a3525-628e-4c26-9537-ecd4b6797254.mp4 —
 v1, superseded: https://d2ol7oe51mr4n9.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/b298f61f-0f77-4074-9546-ef20816193f6.mp4)

- 1920x1080, h264/aac, **8:47.7 runtime** (527.68s) — unchanged since v1; only the visual treatment inside scenes has changed across versions, so the original subtitle timing stayed valid throughout and was never regenerated.
- 16 narrated scenes + 1 outro bumper (17 total), each scene's video length equals its narration clip's exact duration — scene/audio sync is exact by construction.
- Voice: Arthur (ElevenLabs via Higgsfield `text2speech_v2`, locked in `references/style_guide.md` at repo root).
- Visuals: duotone photographic cutout portraits (8 scenes, one consistent identity — see below) + Tifo-style static data-graphic scenes (5) + progressive multi-state chalkboard diagrams (3), all `gpt_image_2_5`.
- Built with FFmpeg (Ken Burns zoompan per scene/sub-state, concat, final encode) inside a Higgsfield cloud sandbox (`sandbox_exec`) — this repo's local environment cannot handle a render/upload of this size, per the lesson from the Baggio episode.

### v1 → v2 fixes (per Maitham's review of v1)
1. **Ken Burns motion bug (root cause of "looks like one frozen image")**: v1's zoom formula (`min(zoom+0.0012,1.12)`) saturated at its 1.12x cap within a few seconds for any scene longer than ~8s, then held perfectly still for the rest — most scenes are 15-58s, so the majority of v1 was genuinely a frozen frame. v2 uses a linear zoom (`1 + (on/total_frames)*0.18`) that only reaches its target at the scene's *last* frame, plus a diagonal pan, so motion runs continuously for the scene's full duration. No content was regenerated for this fix — same images, corrected math.
2. **Real tactical pitch video inserted, not just diagrams**: the three `chalkboard` scenes (8, 12, 15) opened with an 18-20s AI-generated broadcast-style tactical-camera video (`seedance_2_5`, 35 credits each) before cutting to the annotated diagram for the rest of the scene. **Superseded in v3 — see below, this approach did not work.**
3. **Hansi Flick likeness accuracy**: raised as a harder constraint — a real press photo cannot be used as a generation input since that would mean deriving the output from copyrighted photography (holds even when Maitham supplies the photo directly — the source's copyright status doesn't depend on who fetched it). **Partially addressed in v3 — see below.**

### v2 → v3 fixes (per Maitham's review of v2)
1. **The 3 AI-generated tactical videos were reviewed frame-by-frame and found broken, not just "generic":** scene 8's video was a vague mass of player markers with no clear shape; scene 12's was a nonsensical single-file line of ~20 players plus a glowing laser-beam effect; scene 15's was an abstract grid of dots forming two diamond shapes, not a football formation at all. Current video-generation models cannot reliably follow precise tactical choreography instructions. **Decision: dropped all 3 tactical videos entirely.**
2. **Replaced with progressive multi-state chalkboard diagrams** (Maitham's request — "كأن مدرب قاعد يأشر على ورقة تكتيكية ... الدوائر والخطوط تتغير حسب الشرح"): each of scenes 8, 12, and 15 is now built from 4-5 separately generated diagram images (an empty pitch → defensive line appears → attackers/space highlighted → final state), cut at the exact sentence-boundary timestamps already computed for the subtitles (same char-proportional allocation), each with its own short Ken Burns move. This reads as a coach building up the explanation live, stays fully accurate to the narration (unlike the AI video), and cost only 14 extra image generations (~14 credits) instead of more video credits.
3. **Hansi Flick identity consistency fixed**: Maitham supplied 3 real photos of Flick; using them as generation *inputs* was still declined (same copyright reasoning as v1/v2 — applies regardless of who supplies the photo). Instead, those photos were used only for visual reference to correct the *text* description — Flick has short grey receding hair, not a shaved bald head, and is rarely shown wearing glasses, both wrong in v1/v2's prompts. A new master portrait was generated from the corrected description, approved by Maitham, then reused as an `image_references` input across the other 7 portrait scenes (all originally-generated images, no copyrighted source), which produced one consistent face across all 8 portrait scenes instead of 8 different-looking men. Likeness to the real Hansi Flick is closer but still an approximation — that ceiling from v1/v2 still applies; what's fixed is *consistency*, not perfect real-world accuracy.

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
