# BY ATHAR — Visual & Voice Style Guide

Shared, channel-wide reference. Written once (per the "Step 0" one-time setup in
`.claude/skills/youtube-studio/SKILL.md`) and reused for every episode. Update
this file only when a deliberate channel-wide style change is decided — not
per episode.

---

## Portrait scenes — LOCKED: Tifo-style clean vector illustration

Source of truth: test batch generated 2026-09-20 for the Roberto Baggio
episode. Version B (vector) was chosen as the channel standard over the
softer "standard" cel-shaded look (Version A) and the semi-realistic
painterly look (Version C) — closest match to Tifo Football's crisp,
flat-color illustrated portraits.

- **Model**: `recraft_v4_1`
- **model_type**: `vector`
- **resolution**: `2k`
- **aspect_ratio**: match the shot (`3:4` for single chest-up portraits,
  `16:9` for wider narrative scenes)
- **Output format**: SVG (scalable — good for crisp export at any size)

### Locked prompt template (portrait scenes)

Reusable skeleton — fill in the bracketed identity/wardrobe block per
subject and per episode, keep every other clause verbatim so all portraits
share one consistent house style:

```
Clean vector editorial sports illustration portrait, flat color football
tactics show style, [SUBJECT AGE/BUILD], [FACE: jaw, nose, eyes, cheekbones,
skin tone], [HAIR: color, style, part], calm focused expression looking
slightly off-camera, wearing [ERA-ACCURATE KIT/OUTFIT], chest-up portrait
(or full-body for wide shots), muted [TEAM COLOR] and cream flat background,
bold clean outlines, minimal flat shading, consistent vector illustration
style, no photorealistic texture, no text, no watermark, no logos
```

### Roberto Baggio — locked identity block (reuse across all his scenes)

```
Italian footballer, defined angular jaw, straight prominent nose, deep-set
brown eyes, high cheekbones, olive skin tone, dark brown hair centrally
parted and pulled back into a long ponytail
```

Vary only: age (teens at Vicenza → mid-20s at Juventus → late 30s at
Brescia), kit/team color per era:
- Vicenza: red-and-white
- Fiorentina: purple, number 10
- Juventus: black-and-white stripes, number 10
- Italy national team: blue, number 18 (1994) / number 10 (1998)
- AC Milan: red-and-black
- Bologna: red-and-blue
- Inter Milan: black-and-blue
- Brescia: blue-and-white

Editorial-illustration framing note: this is a hand-drawn/vector likeness
for documentary commentary (same practice as Tifo Football drawing real
managers/players), not a photoreal reproduction — keep it in this stylized
vector form for every real person the channel covers, both for house style
consistency and to stay clear of the "photoreal recognizable person" issue
that Higgsfield's dedicated character-sheet workflow explicitly disallows.

### Approved reference render (Baggio, Fiorentina era)

- Job ID: `cd082625-4661-4f59-9583-3f16e79e82bf`
- URL: https://d8j0ntlcm91z4.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/hf_20260920_005937_cd082625-4661-4f59-9583-3f16e79e82bf.svg

---

## Data-graphic scenes — Dorktown-style

**LOCKED**: Version C from the 2026-09-20 test batch — `gpt_image_2_5`.

- **Model**: `gpt_image_2_5`
- **aspect_ratio**: `16:9`
- **Output format**: PNG

### Locked prompt template (data-graphic scenes)

```
Sports documentary data visualization frame, Dorktown Secret Base YouTube
essay style, dark navy background, glowing red animated-looking line graph
charting [WHAT IS BEING TRACKED, e.g. "a career trajectory across years" /
"a match scoreline building over 90 minutes" / "a transfer fee climbing to
a new record"], small abstract silhouette icons marking key moments (not
real faces or photographs), retro Google-Sheets-chart-meets-map aesthetic,
clean flat design with subtle grain texture, no text, no logos, no real
photos
```

Keep every clause verbatim except the bracketed tracked-metric description
— this is what varies per scene (goals, transfer fees, timelines, match
scorelines, career progression, etc).

### Approved reference render

- Job ID: `9d3de4f8-37d4-4960-981f-d5fcbbbdddd5`
- URL: https://d8j0ntlcm91z4.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/hf_20260920_015035_9d3de4f8-37d4-4960-981f-d5fcbbbdddd5.png

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

## Narrative/structure reference

Secret Base — Dorktown series (e.g. "The History of the Atlanta Falcons").
Used for pacing, chapter structure, hook style, and target runtime
(20–30 minutes). Content/subject matter is not used as a source — American
football, unrelated to BY ATHAR's sports coverage.
