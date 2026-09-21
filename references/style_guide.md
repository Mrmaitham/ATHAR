# BY ATHAR — Visual & Voice Style Guide

Shared, channel-wide reference. Reused for every episode. Update this file
only when a deliberate channel-wide style change is decided — not per
episode.

**⚠️ Superseded 2026-09-21**: the Roberto Baggio episode was built with
vector-illustration portraits (`recraft_v4_1`) and Dorktown/Secret Base as
the structure reference. After reviewing that episode, Maitham explicitly
decided, twice, to move the channel to the Tifo-only reference and the
duotone-photo portrait style locked below instead — including the
"photoreal recognizable person" risk that was the original reason for
choosing vector illustration (Maitham chose to accept that risk; the
Maldini test render below generated successfully with no refusal). The
full prior lock is preserved in
`episodes/roberto-baggio-the-man-who-died-standing/PRODUCTION_LOG.md` and
that episode's own `production/manifest.json` — it is not repeated here
since it no longer applies to new episodes.

---

## Reference channel — LOCKED: Tifo Football by The Athletic

Sole reference for **both** narrative structure and visual style (replaces
the previous split reference of Dorktown for structure + Tifo for visuals).

- Channel: https://www.youtube.com/channel/UCGYYNGmyhZ_kwBF_lqqXdAQ
- Reference episode analyzed frame-by-frame and word-by-word: "Xabi Alonso's
  Chelsea & Tactical Diversity" (7:24 runtime, published 2026-09-21).
- Publishing pattern (pulled via the channel's public RSS feed — direct
  YouTube access is blocked in this environment, RSS works):
  near-daily uploads, mixed formats (deep tactical explainers, a recurring
  "Who's on my head?" segment, live post-match reactions, historical
  rankings). The format BY ATHAR imitates specifically is the deep tactical
  explainer, voice-over only, no host on camera.

### Narrative structure (timestamps from the reference episode)
| Part | Timing | Function |
|---|---|---|
| Hook | 0:00–0:39 | A direct, intellectually complex question (not dramatic/emotional) |
| Historical context | 0:46–3:57 | Builds "why this matters now" cumulatively, event → consequence → next event |
| Core analysis | 3:58–7:06 | Breaks the question down with concrete, connected evidence |
| Outro | 7:07–7:24 | Channel/sponsor plug — BY ATHAR replaces this with its own bumper |

Rules extracted: (1) the hook is a thinking question, not a cliffhanger;
(2) never open on the subject directly — build why it matters first; (3)
cumulative build, no scattered trivia; (4) even pacing suited to a single
uninterrupted voice-over, no dialogue.

## Episode length — two approved formats (picked per episode, before writing the script)

- **7–10 minutes** — matches the reference episode's own runtime exactly;
  for narrower/lighter topics.
- **10–20 minutes** — the reference structure (hook → context → analysis)
  stretched with more material; for topics with enough historical/narrative
  depth (Maitham's decision, for the deeper storytelling the channel wants).

## Portrait scenes — LOCKED: duotone photographic cutout

Replaces the earlier vector-illustration lock below. Approved 2026-09-21
after a 3-variant test on Paolo Maldini (`gpt_image_2_5`); variant 1 chosen.

- **Model**: `gpt_image_2_5`
- **aspect_ratio**: `16:9`
- **Output format**: PNG

### Locked prompt template (portrait scenes)

```
Sports analysis broadcast graphic: a duotone black-and-white cutout photo
of [SUBJECT] in a highly dynamic mid-action pose ([SPECIFIC ACTION, e.g.
"a sliding tackle", "a driving run", "a mid-air header"]), isolated with
clean sharp edges, placed on a flat dark forest-green background fading to
black at the edges, subtle grain texture and faint scattered light dots.
Bottom-left corner has a bold black rectangular name-tag box with bold
white sans-serif text reading '[NAME]'. Minimalist tactical football
analysis video style, high contrast, cinematic documentary feel, no logos,
no watermark, 16:9 widescreen composition, empty negative space on the
right side for text overlay.
```

Vary only the subject, the specific action, and the name-tag text — every
other clause stays verbatim so all portraits share one house look.

### Approved reference render (Paolo Maldini test, variant 1)

https://d8j0ntlcm91z4.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/hf_20260921_215338_694c19c4-0c8b-4763-9a68-ee739ed504d5.png

## Data-graphic / tactical scenes — LOCKED: Tifo chalkboard style

Replaces the earlier Dorktown line-chart style below, to match the single
Tifo reference now used for both structure and visuals.

- **Model**: `gpt_image_2_5` (or best available for clean vector-like line art)
- **aspect_ratio**: `16:9`
- **Output format**: PNG

### Locked prompt template (tactical/data scenes)

```
Tactical football analysis chalkboard diagram, flat black background, a
hand-drawn-style white pitch outline, colored circles representing players
in [FORMATION/MOVEMENT BEING SHOWN], clean minimalist broadcast graphic
style matching a tactical analysis YouTube show, no real photos, no text,
no logos, no watermark
```

Keep every clause verbatim except the bracketed formation/movement
description, which varies per scene (a shape, a pressing trap, a passing
pattern, a statistical comparison rendered as simple bars/icons, etc).

## Voice (ElevenLabs via Higgsfield)

**LOCKED**: **Arthur** (male preset), chosen by ear from the built-in preview
sample after Higgsfield's daily generation grace-period limit blocked
generating a live narration test.

- **model**: `text2speech_v2`
- **variant**: `elevenlabs`
- **voice_type**: `preset`
- **voice_id**: `30fc8796-ceb6-4a66-b3a7-4a145ef7f346`
- **Preview used for selection**: https://d1xarpci4ikg0w.cloudfront.net/audio_voice_preset/preview/080fcbab-8be3-4d60-8156-3c3040421e0f.mp3
- **Confirmed live narration sample** (episode's actual cold-open lines):
  https://d8j0ntlcm91z4.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/hf_20260920_015020_bdbd7c40-ff55-4036-a5cd-44c411694598.mp3

## Arabic subtitles — sync target

Per-scene sync (one cue per scene, as done for the Baggio episode) is the
floor, not the goal. Target for new episodes: **phrase/sentence-level
sync** — each Arabic cue timed to match its corresponding English
phrase's actual timing window from the word-level Whisper transcript, not
just the outer scene boundary. Word-for-word timing is not attempted
(timing doesn't transfer 1:1 across languages), but cues should be finer
than "one block per scene" wherever a scene's narration has more than one
beat.

## Production pipeline note

The final FFmpeg assembly (concat, Ken Burns per scene, encode) for the
Baggio episode ran inside a **Higgsfield cloud sandbox** (`sandbox_exec`),
not this repo's local environment — local Bash/ffmpeg here cannot reach
the Higgsfield asset CDN or handle a render job at full-episode scale.
Use `sandbox_exec` for the real assembly step of every episode; local
`ffmpeg` here is only for small utility tasks (e.g. extracting audio from
a user-uploaded reference video for analysis).
