# littlewonder-agent memory (Little Wonder فقط)

- Little Wonder (2026-10-09): **مو 4 خوات.** زوزو ونونو خوات، نادية وحور خوات، تيتة خديجة جدتهم. بالإنجليزي: "two pairs of sisters" أو "the girls" — لا "four sisters" ولا "the sisters" عن الأربع.
- Little Wonder: ميثم يرفع الفيديوهات على Google Drive (مجلد مشارك "Anyone with the link")، وأنزلها بـ gdown. رفع Higgsfield من جهته ما زبط.
- 2026-10-09: تيك توك يبقى حساب **شخصي** (Business طلب رخصة تجارية، ما عند ميثم). ما فيه خيار ربط يوتيوب → اسم القناة بالبايو. الرابط بعد 1,000 متابع.
- 2026-10-09: ميثم يبي خطوات النشر **وحدة وحدة** وبالعربي (لهجة خليجية)، والكابشنات بالإنجليزي جاهزة للنسخ.
- 2026-10-09: شورتسات الحلقة 1 (4) تنزل خلال يومين، مقطعين باليوم، وبعدها شورتسات الحلقة 2. أول مقطع (Meet the Family) نزل إنستقرام + تيك توك.
- الحلقة 2 تأخرت (كانت مفروض الجمعة 9 الصبح). إعلانها ينزل بعد نزولها بيوتيوب، مو قبل.
- whisper (faster-whisper small) يفرّغ حوار الحلقات بدقة كافية — مفيد لاختيار لحظات الشورتس.
- 2026-10-09: **ميشو ذكر** (he/his/him) — تأكيد ميثم. صحّحت كابشنات خطة الإطلاق ("She means well" ← "He means well").
- 2026-10-09: سكريبت الحلقة 2 (Grandma's Old Vase — الصدق) بـ `.agents/projects/little-wonder/episodes/ep02-grandmas-old-vase-script.md` — مراجعة 2: زوزو تطلع قبل التحقيق (ما تسكت وميشو ينعاقب)، "Golden paint" بدل "Real gold"، غرا بالإصلاح. ميثم يعتمد السكريبت لقطة لقطة ويحب القرارات مكتوبة جنب اللقطة ("قرار ميثم").
- 2026-10-09: الحلقة 1 كاملة بـ Drive `1VjMxXHpFVcP4tDNlWgeqX9KVL2tFFyll` (gdown بالـ ID). صوتها −21.7 LUFS (واطي) → الحلقات الجاية −14 LUFS. زوزو = البنت اللي بالحجاب (مؤكد من الحلقة).
- 2026-10-09: ميثم **لغى سكريبت الفازة** — الحلقة 2 تنكتب من الصفر. الأفكار الثلاث بـ episodes/ep02-ideas.md. المرجيحة الملتفة بالحلقة 1 جزء من القصة، مو خطأ.
- 2026-10-09: **درس:** فلتر VAD بـ faster-whisper حذف جمل كثيرة من الحلقة 1 (منها الختام). فرّغ دايمًا بـ vad_filter=False + condition_on_previous_text=False، وافحص آخر 30 ث صورة بصورة. ختام كل حلقة: "Little hearts, big wonders!" + رفع الإيدين.
- 2026-10-09: ميثم اختار فكرة **The Little Seed (الصبر)** للحلقة 2. الخطوة الجاية: المخطط (beats) ثم السكريبت لقطة لقطة.
- 2026-10-09: الحلقة 2 أزواج الزراعة (قرار ميثم): زوزو + حور (كبيرة وصغيرة، أصيص Baby، صابرين) · نونو + نادية (متقاربين، أصيص Sprouty، مستعجلين). ميثم يحب الأزواج: كبير مع صغير + اثنين متقاربين.
- 2026-10-09: صور مرجع الحلقة 2 (1–10) معتمدة بـ episodes/ep02-refs/ (≈33 كريدت). Higgsfield job IDs: زاوية 7cd09641 · أصيصين 423119cf · أدوات f127785c · Day5 c184b23a · Day7 e24b1516 · لوحة فاضية 86693aa6 · 6 نجوم bc276e00 · نونو 252962b5 · نادية 5f79237f · حور b6a89a52. زوزو/تيتة/ميشو: الصور الأصلية (media 2e1e9118 / f7f818c8 / dd84ad18 — رفع 07:06 قد ينتهي). موديل الفيديو: seedance_2_0_mini (720p، 1 كريدت/ث).
- 2026-10-09: مشهد التجربة (20–24b) نجح. عينات الأصوات من الحلقة 1 (Higgsfield audio): نونو 4de3fa9f (v2 — الأولى 33df6e08 فيها 'I want to fly so high' وانرفضت ip_detected) · نادية 53593716 · زوزو 780a10f3 · حور ab035a53 · تيتة a582f3fb. زوزو صورة a221b97a. Higgsfield يقترح preset 'IN THE DARK' ويرفض الإرسال → حط declined_preset_id 24bae836-2c4a-48e0-89b6-49fcc0b21612. ip_detected ينرد الكريدت.
- 2026-10-09: **درس كبير:** ميثم رفض الفصل الأول (انتقالات غلط، أغراض تختفي). القاعدة الآن: كل لقطة 5–8 ث بالكثير، وبداية كل لقطة = آخر إطار من اللي قبلها (start_image)، واللقطات القريبة بحركة كاميرا مو قطع. يوم جديد يبدأ من Anchor ثابت + كرت Day. أفحص الانتقال (آخر إطار ↔ أول إطار) مو بس اللقطة لحالها، وأولّد السلسلة لقطة لقطة.

## Ep2 production lessons (2026-10-09)
- Returning from a close-up to the wide set: pass the last accepted WIDE end frame as image_reference (not A1/A2 anchors) — anchors cause hard cuts / set collapse when composition differs.
- Close-ups without a set ref drift to a generic suburban yellow house; add the wide frame as ref.
- Never pass pots_named ref before the signs exist (signs appear early); never write "plain wooden sign" (signs vanish).
- Name signs tend to grow a fake sprout at the stick base — say "absolutely no sprout/leaf/green".
- Duplicate toddlers happen on pans to a bench — say "ONLY ONE toddler", prefer pull-back to wide.
- Grandma/Zoozoo crouch unless told "STANDING upright the whole time, never crouching".
- lastframe.sh now auto-detects hard cuts (scene>0.3); trim before the cut if the line is complete.
- ip_detected is refunded; rewording ("3D animated" instead of "Pixar-style") passes.
- Ep1 intro song = 0:00–0:33.8; outro = 413.5s→end; chant backup audio at 407.3–413.1s.

## قاعدة العمل مع ميثم (2026-10-09) — إلزامية
- لقطة وحدة بس كل مرة: أسويها، أعرضها، وأنتظر اعتماد أو رفض صريح من ميثم.
- ممنوع أي خطوة تصرف كريدت أو تغير شي (توليد فيديو، صورة، تصليح، إعادة) بدون موافقة صريحة قبلها.
- خطة إعادة الحلقة 2 من البداية: صورة العائلة الأساسية (مطابقة للمراجع) كمرجع لكل لقطة • مراجع كل الشخصيات بالكادر • تصليح آخر صورة من كل لقطة على المرجع قبل اللقطة اللي بعدها — كل خطوة بموافقة.
- اسم البنت الصغيرة بالعربي: **حور** (بالحاء) — مو "هور". بالإنجليزي Hoor.
- **قبل إرسال أي فيديو لميثم:** فحص الأشكال إلزامي — قص كل شخصية من أول/نص/آخر صورة وقارنها بصورة المرجع (الشعر، اللون، الملابس، الإكسسوارات). أي فرق أذكره بوضوح قبل ما أرسل.
- نادية (المرجع): شعر أسود غامق، فرق بالنص، مسحوب لورا **ذيل حصان واحد واطي ورا الراس**، بدون غرة وبدون ضفيرتين. الموقع يميل يحولها لشعر بني بغرة وضفيرتين — لازم أكتبها صريح بكل لقطة.
- حور (المرجع): كعكتين مجعدة وعلى كل وحدة **فيونكة كريمي بنقط سودا صغيرة** — مو مشابك لؤلؤ ذهبية (وصفي القديم كان غلط).
- Rule (user, Ep2 v2): every finished shot is sent MERGED with the previous approved shot (prev + new) so the user can follow continuity. Also keep morning light/sun time constant within a scene (use empty-garden ref 7e9f45d5 for light lock).
- Seeds must be drawn plain brown with NO green tip; nothing sprouts on planting day.
- Lighting ramp (user, Ep2 v2 shot 23+): sky band red level = 135 at shot 23, then raise gradually each shot (~+1.5) back up to 142 and hold. Tool: lw_tools/rampgrade.py (full-frame match to previous shot + uniform scale to sky target). Plain sky-only grading breaks on camera moves.
- Never describe a "plant drawing/doodle" on props: the video model turns it into a real seedling. Use a red heart on a flat wooden label.
- User rule: no push-ins that drop characters out of frame - in group scenes keep a LOCKED WIDE camera so everyone stays visible.
- KEY LESSON (shot 25): never write "no sprout / no seedling / nothing green" - negatives make the video model ADD the plant. Describe soil positively only: "filled to the rim with smooth, flat, dark brown soil with a plain even surface, like freshly patted earth". This fixed it first try.
- Look drift fix (Ep2 shots 26-31): ALWAYS attach every on-screen girl's reference + full character block in the prompt (Noonoo = very dark BLACK long wavy hair, WHITE sneakers; drifted to brown curly + pink shoes when her ref was omitted). If drift already in start frame, fix it with a gpt_image_2_5 edit of the start frame first.
- Nadyah outfit (ref 09): SOFT LIGHT CORNFLOWER-BLUE smooth cotton vest + matching shorts. "denim" → denim vest drift; "royal blue" → too dark (Ep2 16v3 rejected). Approved wording in Ep2 l16.
- Before any batch redo: inspect existing shots per character vs refs and report first (user: "افحص قبل الاعاده").
- Handoff lesson (Ep2 22): a handoff to a girl standing BEHIND/beyond another girl lands between them and the model duplicates the prop (both hold one). Only hand props to the ADJACENT person. Small props tend to vanish late in a shot → trim the shot where props are still clearly held. Speech stutter in one take can be fixed by swapping in the clean audio from another take with the same timing (adelay to align).
- Prop morph lesson (Ep2 24): a girl holding pen + plain stick → model turns the stick into a clipboard/board. Give the pen only right before drawing, in the same shot as the drawing.
- DRIFT lesson (Ep2 v2, user caught at 29): chaining end frames accumulates look drift (Noonoo/Nadyah/Hoor hair black→brown from shot 19, faces rounder, warmer light). QA must compare every shot to the MASTER family ref (12_master_family_v1, media 62a561c2), not just to the previous shot. Fix: gpt_image_2_5 edit of the start frame with master + individual refs ("JET-BLACK hair", bright morning), then attach master ref to the video gen.
- Do NOT attach the master family image as a video image_reference: it caused a hard cut into the master group pose at ~4.8s (Ep2 26). Use master only for the start-frame image edit; videos get individual refs.
- Repeat lesson (Ep2 29/31): the model often repeats a short line twice in a 7s shot. Write the line once and keep 5s duration for short lines, or trim / replace the repeat with ambience.
