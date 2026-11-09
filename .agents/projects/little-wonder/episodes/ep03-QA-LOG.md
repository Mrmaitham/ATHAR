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
