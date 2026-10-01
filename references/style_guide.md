# BY ATHAR — Visual & Voice Style Guide

Shared, channel-wide reference. Written once (per the "Step 0" one-time setup in
`.claude/skills/youtube-studio/SKILL.md`) and reused for every episode. Update
this file only when a deliberate channel-wide style change is decided — not
per episode.

---

## ⚠️ Channel visual standard changed — 2026-10-01

The channel moved to the cinematic-documentary format documented in
`references/documentary_format.md` (copied from the Wake Island reference
film). The sections below marked **ARCHIVED** (Tifo vector portraits,
Dorktown data-graphics) were the standard for the Roberto Baggio episode only
and are kept for reference — do not use them for new episodes.

## Narrative scenes — painterly cinematic — LOCKED 2026-10-01

Chosen by Maitham from a 3-model test (Calciopoli episode,
`episodes/calciopoli-2006/style_test/comparison.jpg`):

- **Model**: `gpt_image_2_5`, `quality: high`, `resolution: 2k`, `aspect_ratio: 16:9`
- **Cost**: 2.75 credits / image (Oct 2026)
- Rejected: Nano Banana (digital poster look, letterboxing, false NSFW
  refusals), Cinema Studio 2.5 (too photographic).

### Real people — "signature features" rule (decided 2026-10-01)
GPT Image will not copy a real person's exact face from a reference photo
(it turns the subject away). So real people are drawn by **signature
features** + an on-screen name tag, never by face-matching:
hairstyle, glasses, build, kit number, armband, props (cigar, phone),
clothing. Write the features from verified photos; keep one identity block
per person per episode and reuse it verbatim.

Example (Luciano Moggi, from photos supplied by Maitham):
`heavyset Italian football executive in his late sixties: bald crown with
short dark hair at the sides, thin rimless glasses, tanned face, a cigar in
his mouth, dark suit and tie` (later years: camel overcoat with sheepskin
collar).

### Prompt rules learned on the first episode
- Never write "alternate composition / closer framing on faces, hands and
  details" — the model returns a **collage**. Use: `Single continuous image,
  not a collage: a close-up shot of …` and end every prompt with
  `single image, no panels, no text, no logos, not photorealistic`.
- Name the country of courtrooms/offices and say `Italian tricolour flag
  only` (otherwise US flags appear).
- State kit numbers explicitly (Grosso #3, Cannavaro #5, Del Piero #7 Italy /
  #10 Juventus).
- Short tail keeps style consistent: `Muted teal-amber palette, cinematic
  light, painterly brushstrokes, period detail`.

### Climax clips (Tier B)
- **Model**: `kling3_0`, `mode: std`, `sound: off`, 5 s, image-to-video from
  the scene's own painting (`start_image` = image job id), prompt ends with
  `keep the oil painting style`. Cost 7.5 credits / clip.
- If Higgsfield answers with a preset recommendation instead of a job, resend
  with `declined_preset_id`.

### Prompt template (narrative scenes)

```
Cinematic digital oil painting, historical documentary still, [SCENE: who,
where, what is happening], [ERA: year, place, era-accurate clothing, kits,
stadium, equipment, vehicles], dramatic [LIGHT: dawn / golden hour /
floodlights / firelight / overcast], muted teal and amber palette, visible
painterly brushstrokes, rich detail, [SHOT: wide establishing / medium group
/ close-up face], 16:9, no text, no logos, no watermark, not photorealistic
```

Optional per-episode art direction (from the Brief), appended verbatim, e.g.
`in the style of Rembrandt chiaroscuro lighting`.

### Prompt template (antique maps)

```
Antique parchment map, aged paper texture, hand-drawn coastlines and
borders, watercolor teal sea, ornate compass rose and decorative cartouche
frames, [REGION / CITY / STADIUM LAYOUT], [optional: red arrows showing
MOVEMENT], vintage cartography style, 16:9, no modern text, no logos
```

Place labels are added in FFmpeg as overlays, not generated in the image.

### Overlay system (rendered as PNG with PIL, composited in FFmpeg)

| Token | Value (initial — confirm on first episode) |
|---|---|
| Navy (cards background) | `#1F2A3A` |
| Gold (accents, numbers, subtitles) | `#E8A317` |
| Black (name boxes) | `#111111` |
| White (titles, names) | `#FFFFFF` |
| Title / quote font | Playfair Display (serif; italic for quotes) |
| Name / number font | Montserrat Bold |

Elements and layout: see `documentary_format.md` §4.

### Thumbnail

Cinematic semi-realistic climax image + two words, each in its own box
(top-left): word 1 black text on orange/gold box, word 2 white text on black
box with orange border. Two variants per episode.

## Portrait scenes — ARCHIVED (Baggio episode): Tifo-style clean vector illustration

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

## Data-graphic scenes — ARCHIVED (Baggio episode): Dorktown-style

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

Current: `references/documentary_format.md` (cold open → 6–8 chapters →
"The Price/Legacy"; ~137 wpm). Secret Base / Dorktown remains a tonal
reference for sports storytelling and a source to search for outliers.
Used for pacing, chapter structure, hook style, and target runtime
(20–30 minutes). Content/subject matter is not used as a source — American
football, unrelated to BY ATHAR's sports coverage.
