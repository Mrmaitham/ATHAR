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
