# سجل الفحص (qa.py يضيف سطر لكل فحص)

| اللقطة | المحاولة | الملف | النتيجة الآلية | التوقيع | الحكم |
|---|---|---|---|---|---|
| S011 | attempt 1 | S011_n1a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | attempt 2 | S011_n2a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | attempt 2 | S011_n2b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | attempt 3 | S011_n3a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | attempt 3 | S011_n3b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | attempt 1 | S011_c1b.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S011 | attempt 1 | S011_c1a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | cycle2 attempt 1 (c1b) | S011_c1b.mp4 | auto-pass (all automatic checks incl. name "Afnan!" exact) | identity signoff: NO - Afnan height ~52-60% of Grandma vs 46 spec (inherited from approved S009/S010) | NOT SENT: waiting Maitham decision |
| S011 | cycle2 attempt 1 (c1a) | S011_c1a.mp4 | FAIL (name heard "Oh") | NO | NOT SENDABLE |
| S011 | cycle2 attempt 1 (c1b) | S011_c1b.mp4 | auto-pass | identity signoff: YES (Afnan height 55% accepted by Maitham) | OK to send |
| S011 | cycle2 | S011_c1b.mp4 | ما كان لازم يتوقّع | - | تصحيح: الحكم السابق "OK to send" غلط. افنان تختفي وجدة تنسحب بآخر المشهد؛ ما انتبهت قبل الإرسال. |
| S011 | redo attempt 1 | no-end-frame a | FAIL (door closed, Grandma+Afnan gone at end) | NO | NOT SENDABLE |
| S011 | redo attempt 1 | no-end-frame b | FAIL (Afnan absent at end, Noonoo points instead of Hoor, ribbon not taut) | NO | NOT SENDABLE |
| S011 | attempt 1 | b.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S011 | attempt 1 | a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | shy attempt 1 | a | FAIL (name Asman) | NO | NOT SENDABLE |
| S011 | shy attempt 1 | b | auto-pass (name exact in 1 of 2 ASR models), Afnan fully hidden at last frame | NO | HELD |
| S011 | shy attempt 2 | a+b | FAIL (door closed, Grandma+Afnan gone at last frame) | NO | NOT SENDABLE |
| S011 | attempt 2 | b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | attempt 2 | a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | attempt 1 | b.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S011 | attempt 1 | a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | attempt 1 | b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | walkdown attempt 1 | a | FAIL (join 0.08 wide-shot jump, brightness, saturation) | NO | NOT SENDABLE |
| S011 | walkdown attempt 1 | b | FAIL auto: brightness +23% vs S010 (95 vs 77); pass: join 0.80, line exact x2 | NO | HELD for Maitham decision |
| S011 | walkdown b | - | رفض من ميثم: البنات والمكان السابق اختفوا | - | REJECTED. خطأ فحصي: cast=Grandma,Afnan فقط |
| S011 | attempt 1 | a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | wide fixed attempt 1 | a | auto: join 0.06 + brightness vs S010 (both consequences of the cut Maitham approved; substitutes: vs intended S009 start frame 0.61, brightness vs S009 95 vs 94); line exact x2; cast 6/6 + bucket + ribbon + open door verified by eye on every 0.5s frame | identity: eye-checked | SENT to Maitham with disclosure |
| S012 | attempt 1 | b.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S012 | attempt 1 | a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S012 | attempt 1 | a (fixed) | FAIL: name "Afna! Afna!"; also invented metal pole at left holding the ribbon | NO | NOT SENDABLE |
| S012 | attempt 1 | b (push-in) | auto-pass incl. name "Afnan! Afnan!" exact x2, but invented metal pole (new object not in S011) | NO | NOT SENDABLE (pole) |
| S012 | attempt 2 | a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S012 | attempt 2 | b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S012 | attempt 2 | a | audio exact x2; join aligned 0.49; invented red stanchion pole at left | NO | NOT SENDABLE |
| S012 | attempt 2 | b | audio exact x2; join aligned 0.56; invented wooden post; push-in crops Grandma and Zoozoo | NO | NOT SENDABLE |
| S012 | attempt 3 | b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S012 | attempt 3 | b | audio exact in 1 of 2 models; join aligned 0.20; invented wooden post again | NO | NOT SENDABLE |
| S012 | attempt 3 | a | job b493bdf5 still running after 20+ min | - | PENDING |
| S011 | attempt 1 | b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S011 | option-A redo | a (Noonoo holds end) | end still hidden behind Noonoo/Hoor at frame edge | NO | REJECTED |
| S011 | option-A redo | b (Hoor holds end) | end still hidden behind Hoor hair | NO | REJECTED |
| S012 | attempt 4 | a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S012 | attempt 4 | b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S012 | attempt 4 | a_matched.mp4 | FAIL | identity signoff: eye-checked 12 frames: 6/6 cast, bucket, open door, ribbon on ground, no pole | NOT SENDABLE: automatic FAIL |
| S012 | attempt 4 (approved by Maitham "solve it and generate") | b (ribbon bundled) | audio exact in 1 of 2; join 0.30 | NO | not used |
| S012 | attempt 4 | a + framing match (v8a) | join 0.59 (limit 0.60) after 1.5s affine match to S011 last frame; audio exact x2; brightness/saturation pass; eye: 6/6 cast, bucket, open door, ribbon on ground, no pole | signed | SENT with disclosure, PENDING |
| S013 | attempt 1 | a.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S013 | attempt 1 | b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S013 | attempt 1 | a_matched.mp4 | auto-pass | identity signoff: eye-checked 12 frames | OK to send (only if the eye review above also passed) |
| S013 | attempt 1 | a + framing match | join raw 0.39 -> 0.62 after 1.5s affine match; audio: "Who/Whoo! You came!"; brightness/saturation pass; eye: hug, ribbon on ground, bucket, cast partly cropped by push-in | signed | SENT with disclosure, PENDING |
| S013 | attempt 1 | b | join 0.54; extra laughter in audio | NO | not used |
| S013 | v1a | - | رفض ميثم: "Hoo" قالتها حور وليس افنان. خطأ فحصي: التفريغ الصوتي ما يحدد مين المتكلم، وأنا ما راجعت حركة الفم | - | REJECTED |
| S013 | attempt 2 | a_matched.mp4 | auto-pass | identity signoff: eye-checked 24 frames at 4fps: one Hoor, Afnan says Hoo (mouth open 0.7-1.4s, Hoor closed), Hoor says You came (2.6-4.0s) | OK to send (only if the eye review above also passed) |
| S013 | attempt 2 | a + framing match | speakers verified by eye (Afnan mouth open during "Who?" 0-1.46s, Hoor mouth open during "You came!" 2.4-4.36s); one Hoor; audio ok | signed | SENT, PENDING |
| S013 | attempt 2 | b | duplicated Hoor in first frames | NO | REJECTED |
| S013 | attempt 3 | a_matched.mp4 | FAIL | identity signoff: eye-checked 24 frames at 4fps: one Hoor, Afnan mouth open 0.3-1.0s saying Hoor, Hoor mouth open 1.8-2.7s saying You came | NOT SENDABLE: automatic FAIL |
| S013 | attempt 3 (Afnan says Hoor) | a + framing match | ASR both models: "Whore!" 0-1.06s then "You came!" 1.8-2.7s; speakers verified by mouth frames; one Hoor | signed | SENT, PENDING |
S014 attempt 1 (v1a): REJECTED by director review — invented extra girl (long brown hair, white top) + duplicate Nadyah (two blue-vest girls). Not sent.
S014 attempt 1 (v1b): REJECTED by director review — extra short-bob girl in pink top (duplicate Noonoo) next to real Noonoo. Not sent.
| S014 | attempt 2 | S014_v2b.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S014 | attempt 2 | S014_v2b_matched.mp4 | FAIL | identity signoff: NO | NOT SENDABLE: automatic FAIL |
| S014 | attempt 2 | S014_v2b_matched.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S014 | attempt 2 | S014_v2b_matched.mp4 | auto-pass | identity signoff: eye-checked first/mid/last 2026-11-16: exactly 6 characters no duplicates; Hoor puffs+bows pink vest/shorts; Afnan bob green tulle bangles; Noonoo long wavy hair butterfly tee cargo white sneakers; Nadyah ponytail blue vest; Zoozoo white hijab cream coat (belt not visible, ruffle collar yes); Grandma black; Afnan ~53% of Grandma; door open; bucket+ribbon on grass; speakers verified by mouth frames: Zoozoo 1.9-3.8s, Noonoo 4.3-4.9s; nobody looks at lens | OK to send (only if the eye review above also passed) |
S014 attempt 2 (v2b + homography framing match, join SSIM 0.84): QA OK, eye review OK, speakers verified by mouth frames. Sent to Maitham, pending approval. Note: Zoozoo coat belt not visible.
S015 attempt 1 (v1b): REJECTED — first frame not S014 last frame, other characters absent from start (vanished) instead of cropped by zoom. Not sent.
| S015 | attempt 1 | S015_v1a_matched.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S015 | attempt 1 | S015_v1a_matched.mp4 | auto-pass | identity signoff: eye-checked 2026-11-16: first frame = S014 last (join 0.97), others remain in place cropped by zoom (Grandma abaya, Noonoo visible), Nadyah ponytail blue vest white sneakers speaks 0-2s verified by mouth frames, Afnan bob green tulle bangles smiles at end, no duplicates, nobody looks at lens; Nadyah face leaves frame after ~3s by tight push-in | OK to send (only if the eye review above also passed) |
S015 attempt 1 (v1a + homography match, join 0.97): QA OK, eye review OK, speaker Nadyah verified. Sent, pending approval.
S015 v1a: REJECTED by Maitham — Afnan grabbing Nadyah's raised foot looked wrong. Script changed: no shoe touching/leg raising.
| S015 | attempt 2 | S015_v2a_matched.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
S015 attempt 2: v2b REJECTED (unscripted speech before line); v2a clean visually but all 3 ASR hear 'zoozy/zoosy' not 'zoomy' -> held, attempt 3 requested with stronger pronunciation.
S015 attempt 3: v3a REJECTED (extra woman + cat in start frame, word heard 'Zumimi').
S015 attempt 3: v3b REJECTED (unscripted speech 'What is castful! My shoes are speedy. I want to be...', start frame lost Grandma/bucket). 3-attempt cap reached; held v2a (clean visuals, join 0.97, speaker OK, but word heard zoozy/zoosy by 3 ASR). Reported to Maitham without video.
S015 line changed by Maitham to 'My shoes are super fast!' (zoomy mispronounced).
S015 new line attempt: v4b REJECTED (camera tilts down to feet, extra speech 'Nadia, we are super fast' before line).
| S015 | attempt 4 | S015_v4a_matched.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S015 | attempt 4 | S015_v4a_matched.mp4 | auto-pass | identity signoff: eye-checked 2026-11-16: first frame=S014 last (join 0.97); others stay in place cropped by push-in (Grandma abaya, Zoozoo coat, Noonoo visible at edges); Nadyah ponytail blue vest speaks 3.7-5.3s verified by mouth frames, 3 ASR models hear exactly 'My shoes are super fast', no extra speech; Afnan bob green tulle smiles at end; no duplicates, no animals, no foot lifting/shoe touching; nobody looks at lens | OK to send (only if the eye review above also passed) |
S015 v4a (line: My shoes are super fast!): QA OK, eye review OK, speaker Nadyah verified, 3 ASR exact. Sent, pending approval.
| S015 | attempt 5 | S015_v5a_matched.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S015 | attempt 5 | S015_v5a_matched.mp4 | auto-pass | identity signoff: eye-checked 2026-11-16: all 6 characters present in every frame (Hoor puffs+bows pink vest, Noonoo long wavy hair butterfly tee, Nadyah ponytail blue vest, Afnan bob green tulle, Zoozoo white hijab cream coat, Grandma black); first frame = S014 last (join 0.96); bucket+ribbon visible at start; Nadyah speaks 2.1-5.0s (mouth open at 3.1/4.2), 3 ASR exact line; Afnan smiles at end; no shoe touching/leg lift, no extra speech, no duplicates; nobody looks at lens | OK to send (only if the eye review above also passed) |
S015 v5a (new line): QA OK, eye review OK, speaker Nadyah verified, 3 ASR exact, all 6 present. Sent, pending approval.
S016 attempt 1 (v1b): REJECTED — Afnan/Hoor pink sneakers (should be white sandals/black sneakers), Hoor long pink trousers instead of shorts. Audio 'New friend?' clean. Not sent.
S016 attempt 1 (v1a): REJECTED — Afnan brown sandals (should be white bow sandals), Nadyah blue sneakers (should be white). Camera tilted to ground reveals invented shoes. Attempt 2 will spell out shoes + lineup ref.
| S016 | attempt 2 | S016_v2a_matched.mp4 | auto-pass | identity signoff: NO | NOT SENDABLE: identity checklist not signed off (--identity-signoff) |
| S016 | attempt 2 | S016_v2a_matched.mp4 | auto-pass | identity signoff: eye-checked 2026-11-16 first/mid/last: shoes correct (Afnan white bow sandals, Nadyah white sneakers, Hoor black velcro sneakers + pink shorts, Zoozoo beige flats); Mishoo matches turnaround (grey tabby white chest gold bell collar); join 0.95; Mishoo enters from right with reason (curious about new girl); others stay in place, heads cropped by tilt only; 3 ASR hear exactly 'New friend?'; Mishoo mouth open at speech times, Afnan mouth closed; Afnan pats head and laughs; nobody looks at lens; saturation 79 vs 92 borderline | OK to send (only if the eye review above also passed) |
S016 attempt 2 (v2a + homography, join 0.95): QA OK, eye review OK, Mishoo speaks 'New friend?' 3 ASR exact. Pending Maitham approval (sent with S017).
S017 attempt 1 (v1a,v1b): both REJECTED — camera pull-back invented a different house (arched doorway, lantern, lavender) and Afnan looks/walks at the camera at the end. Audio lines OK in both. Attempt 2: no pull-back, tilt up only, house reference image.
S017 attempt 2: v2a REJECTED (Grandma says unscripted 'Missy,' before line; house/door OK). v2b HELD (line clean, but door not visible, Mishoo cropped at bottom, arm skin blotches). Attempt 3 requested.
| S017 | attempt 3 | S017_v3a_matched.mp4 | FAIL | identity signoff: eye-checked 2026-11-16 first/mid/last: approved house kept (stone pillars, open dark wood door, brick sides); all 6 + Grandma + Mishoo (Mishoo partly visible low in frame mid-shot, below frame at end due to tilt-up); Grandma black hijab abaya speaks 3.6-4.9s; Afnan mouth open 5.7-5.85s saying Run (base/medium/small ASR hear run); no extra speech; nobody looks at lens; camera tilt only no pull-back; known artifact: mottled skin patches on arms (Hoor/Afnan), model texture issue | NOT SENDABLE: automatic FAIL |
| S016 | attempt 2 | S016_v2a_matched_graded.mp4 | auto-pass | identity signoff: same eye review as S016 v2a (saturation graded x1.1 to sit between S015 92 and S017 92) | OK to send (only if the eye review above also passed) |
| S017 | attempt 3 | S017_v3a_matched.mp4 | auto-pass | identity signoff: eye-checked 2026-11-16 first/mid/last: approved house kept (stone pillars, open dark wood door, brick sides); all 6 + Grandma + Mishoo (Mishoo partly visible low in frame mid-shot, below frame at end due to tilt-up); Grandma speaks 3.6-4.9s; Afnan mouth open 5.7-5.85s saying Run (ASR hears run); no extra speech; nobody looks at lens; camera tilt only no pull-back; known artifact: mottled skin patches on arms (Hoor/Afnan) | OK to send (only if the eye review above also passed) |
S016 v2a(+grade sat x1.1) and S017 v3a(+match): QA OK, eye review OK. S017 took 3 attempts (pull-back invented a different house; 'Missy' extra word; 'Hey, get Grandmama' extra speech). Known artifact: mottled arm skin. Sent merged S015+S016+S017, pending approval.
Script change by Maitham 2026-11-16: race postponed to next sunny morning (S018a-S018g new). Not generated yet.
S018a attempt 1 (v1a): REJECTED — Noonoo/Nadyah/Afnan/Hoor stare into the lens in the last 2 s with sad faces. Audio exact (3 ASR), house OK, 6 present. Not sent. Attempt 2 (single version) requested.
| S018a | attempt 2 | S018a_v2a_matched.mp4 | auto-pass | identity signoff: eye-checked 2026-11-16: approved house kept (stone pillars, open dark door); all 6 present; Zoozoo speaks (hand on cheek then line) 1.2-4.1s, 3 ASR exact; others react looking toward Zoozoo, gaze crops checked not at lens; no pull-back; known artifact mottled arm skin | OK to send (only if the eye review above also passed) |
S018a attempt 2 (v2a + match, join 0.64): QA OK, eye review OK. Sent S017+S018a, pending approval.
S018b attempt 1 (v1a): REJECTED — wrong speaker: Grandma's mouth open for 'Tomorrow, little sister!' (Zoozoo's closed). Audio exact (3 ASR), Afnan says 'Run?' ok, faces of Hoor/Afnan faithful. Attempt 2 requested with Grandma frozen/quiet.
S018b attempt 2 (v2a): REJECTED — audio exact (3 ASR) but Zoozoo's mouth closed during 'Tomorrow, little sister!', Grandma leans in with open lips (speaker mismatch). Attempt 3: tight two-shot Afnan+Zoozoo, Grandma cropped out by framing.
S018b attempt 3 (v3a): visually/audio good — tight two-shot, Zoozoo's mouth moves for 'Tomorrow, little sister!', Afnan 'Run?', 3 ASR exact, faces faithful, Hoor only in first 2s (script has Afnan+Zoozoo only). BUT visible mottled skin blotches on Afnan's cheek (model artifact). 3-attempt cap reached; held, NOT sent; asked Maitham to decide.
| S018b | attempt 3 | S018b_v3a_matched.mp4 | FAIL | identity signoff: eye-checked 2026-11-16: tight two-shot Afnan+Zoozoo, others cropped by push-in; Afnan face faithful to turnaround; Zoozoo mouth moves for her line, Afnan for Run?; 3 ASR exact; house kept; known artifact: skin blotches on Afnan cheek/shoulder; sent at Maitham request | NOT SENDABLE: automatic FAIL |
S018b v3a sent to Maitham on request despite fails: join SSIM 0.20 (start frame leaked from S014 reference image), saturation 85 vs 101, cheek skin blotches. Proposed attempt 4 without house reference.
S018b attempt 4 (v4a, no house ref): join fixed (raw 0.63), audio exact, Zoozoo speaks; BUT heavy skin blotches on Afnan cheek/arms and Nadyah arm, Zoozoo's face oversized/distorted at end. REJECTED, not sent. Blotches look cumulative since S016.
S018b v4a APPROVED by Maitham 2026-11-17 despite disclosed defects (skin blotches, Zoozoo face distortion in last 2s).
