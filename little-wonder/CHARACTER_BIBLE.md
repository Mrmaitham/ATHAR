# Little Wonder — المرجع الثابت (Character & Location Bible)

هذا الملف هو المرجع الوحيد لكل توليد صور أو فيديو في مشروع Little Wonder.
أي طلب توليد لازم ينسخ **الوصف الإنجليزي الثابت** للشخصية كما هو، ويرفق **صورتها المرجعية بدون أسماء**.

الأسلوب البصري: **3D animated feature film style (soft stylized 3D render, Pixar-like)**.

---

## ١. القاعدة الذهبية: كيف نربط الاسم بالشخصية

الصور المرجعية اللي نعطيها نماذج الفيديو **ما فيها أي كتابة**، لأن النموذج ما "يقرأ" الاسم كهوية، وممكن ينسخ الكتابة داخل المشهد.

الربط يصير **في نص الطلب نفسه** بهالشكل:

```
Reference image 1 = NOONOO: 8-year-old girl, very long wavy black hair, oversized pink t-shirt with lilac butterfly print ...
Reference image 2 = HOOR: 2-year-old toddler girl, curly dark hair in two small buns with cream polka-dot bows ...
```

قواعد:
1. نرفق **فقط** الشخصيات الموجودة في اللقطة (مو كل الست).
2. كل شخصية ترفق **صورتها الفردية** (`char_*.png`)، وترتيب الصور في الطلب = ترتيب ذكرها في النص.
3. ننسخ الوصف الإنجليزي الثابت من الجدول تحت **حرفيًا** — ما نختصره ولا نغير كلماته.
4. نذكر الطول النسبي إذا فيه أكثر من شخصية: `height order: GRANDMA KHADIJA > ZOOZOO > NOONOO > NADYAH > HOOR`.
5. الصور اللي فيها أسماء (`*_labeled.png`) **لنا فقط** للمراجعة — ما تنرفق لنماذج الفيديو أبدًا.

---

## ١ب. قاعدة عدد الشخصيات في اللقطة (مهمة جدًا)

> **شخصيتين بالكثير في اللقطة الوحدة.**

**السبب:** نموذج الفيديو يولّد كل إطار لحاله. لما تتحرك أكثر من شخصيتين متشابهتين ويتقاطعون، يفقد النموذج هوية كل وحدة، فتصير:
- الشخصية تتكرر مرتين في نفس الكادر
- الملامح تنتقل من شخصية لأخرى
- عدد الأشخاص يتغير أثناء اللقطة

**القواعد العملية:**

| الحالة | المسموح |
|---|---|
| لقطة عادية | شخصية أو شخصيتين |
| شخصيتين في الكادر | يوقفون **متباعدين**، وما يتقاطعون ولا يمرّون قدام بعض |
| لازم يطلعون كلهم | إمّا **ظهورهم للكاميرا** (ما نشوف وجوه = ما فيه خطأ)، أو **واقفين ثابتين** في صف بمسافات واضحة |
| ❌ ممنوع | ثلاث شخصيات أو أكثر يتحركون ويتقاطعون ويدورون |

**في الطلب نكتب صراحة:**
`EXACTLY TWO children and nobody else in frame ... they never cross in front of each other and never touch`

ولو اللقطة من الخلف:
`seen ENTIRELY FROM BEHIND, NO FACES ARE EVER VISIBLE, they never turn around`

**البديل لأي مشهد جماعي:** نقسمه لقطتين أو ثلاث قصيرة، كل وحدة فيها شخصية أو شخصيتين. القص السريع يعطي طاقة أعلى من لقطة وحدة طويلة، والخطأ شبه معدوم.

---

## ٢. الشخصيات

ترتيب الطول (من الأطول): **تيتة خديجة ← زوزو ← نونو ← نادية ← حور**، وميشو القطة.

| الاسم | العمر | الصورة المرجعية | Higgsfield ID |
|---|---|---|---|
| GRANDMA KHADIJA (تيتة خديجة) | كبيرة بالسن | `references/char_grandma_khadija.png` | `bd131c30-0bce-4959-aca0-c6cb18f9d334` |
| ZOOZOO (زوزو) | 10 سنوات | `references/char_zoozoo.png` | `52eef1d0-b121-4079-8a58-defa724d605a` |
| NOONOO (نونو) | 8 سنوات | `references/char_noonoo.png` | `f9fc0ef6-f12c-42f4-aa2f-cef873e525ff` |
| NADYAH (نادية) | 4 سنوات | `references/char_nadyah.png` | `2b6af15e-480c-49a9-9c75-9d586e3c4925` |
| HOOR (حور) | سنتين | `references/char_hoor.png` | `7b03ec43-189c-46bf-a4d0-84f2a80b7e49` |
| MISHOO (ميشو) | قطة | `references/char_mishoo.png` | `26b2cb7e-aca1-4e59-9b39-ec9bd477d288` |

الصورة الجماعية بدون أسماء: `references/characters_lineup_clean.png` — ID `3a9b7c34-43b1-49df-bc00-8f283e942ca6`
(تُستخدم فقط للقطات اللي فيها الجميع مع بعض.)

### الوصف الإنجليزي الثابت (انسخه حرفيًا)

**GRANDMA KHADIJA**
> elderly grandmother, the tallest, warm smile with wrinkles, brown eyes, black hijab wrapped around head and neck, long loose black abaya with subtle black embroidery down the front and on the wide sleeves, black shoes

**ZOOZOO**
> 10-year-old girl, second tallest, white hijab, cream lace long coat with ruffled collar, lace cuffs and pearl buttons, white wide trousers, gold coin pendant necklace, cream flat shoes with small bows

**NOONOO**
> 8-year-old girl, very long wavy black hair, brown eyes, oversized pink t-shirt with a lilac butterfly print, gold coin necklace, small earrings, black cargo pants with side pockets, white sneakers with a black side stripe

**NADYAH**
> 4-year-old girl, dark hair in a low ponytail with loose strands, big brown eyes, blue sleeveless collarless long vest with pockets, white top, blue cuffed shorts, gold heart necklace, white velcro sneakers with three black side stripes

**HOOR**
> 2-year-old toddler girl, the smallest, curly dark hair in two small buns with cream polka-dot bows, big brown eyes, pink sleeveless blazer vest, white top, pink cuffed shorts, gold heart necklace, black velcro sneakers with white side stripes

**MISHOO**
> chubby fluffy grey tabby cat with darker grey stripes, white chest, muzzle and paws, pink nose and inner ears, big amber eyes, happy open-mouth smile, gold collar with a gold bell

---

## ٣. الأماكن

| المكان | الصورة المرجعية | Higgsfield ID |
|---|---|---|
| HOUSE (البيت من الخارج) | `references/loc_house.png` | `9431068b-a5c2-4447-99fd-fc8e7f3d3ae4` |
| GARDEN (الحديقة) | `references/loc_garden.png` | `4beeb51b-09d5-4884-aa73-8677839cc8cd` |
| LIVING ROOM (الصالة) | `references/loc_living_room.png` | `fb50fa92-a45d-4a03-990c-71796a548e04` |
| KITCHEN (المطبخ) | `references/loc_kitchen.png` | `33e5f6bc-bf6c-44ef-b317-8942f512b573` |

**HOUSE** — modern three-storey beige stone villa, vertical wooden slat screens, glass balconies with plants, central glass stairwell with chandelier, dark wooden front door, palm trees, black metal front gates with lit pillars.

**GARDEN** — stone walkway with bollard lights, green lawn, pink flower beds, outdoor sofa set with wooden coffee table, wall waterfall, wooden swing set (red and blue swings), wooden playhouse with green roof and blue slide, palm trees.

**LIVING ROOM** — double-height room, white L-shaped sofa with orange and green patterned cushions and green throw, carved dark wood coffee table with pink roses and brass pots, orange-cream Persian rug, white armchairs, tall garden windows, glass pendant lanterns, carved wooden wall art, dining table and kitchen behind.

### الإكسسوارات الثابتة (Props)

| البروب | الصورة المرجعية | Higgsfield ID |
|---|---|---|
| THE SWING (المرجيحة) | `references/prop_swing.png` | `18515f28-acef-4426-8c80-1696ed7b6515` |

**THE SWING** — ⚠️ **ترفق صورتها المرجعية في كل لقطة تظهر فيها المرجيحة**، وإلا شكلها يتغير من لقطة لأخرى.

> the garden's original children's swing set: a sturdy warm natural wood A-frame with a wooden top beam, carrying TWO hanging swing seats on metal chains — one bright RED seat on the left and one bright BLUE seat on the right, both moulded curved plastic seats. Same wood tone and chains as the garden reference.

> **قصة الحلقة الأولى تدور على المقعد الأحمر** (الأيسر). المقعد الأزرق موجود في الكادر بس ما يُستخدم.

---

**KITCHEN** — grey-wood shaker cabinets, white marble island with four white bar stools on wooden legs, three glass globe pendant lights, stainless hood and built-in ovens, brass Arabic dallah coffee pot on a tray, window with palm trees, blue Persian runner rug.

---

## ٤. الصوت وتحريك الشفايف (قرار ميثم)

- **اللغة: إنجليزي.**
- **الصوت يتولد من نموذج الفيديو نفسه** (`generate_audio: true`) — بدون تسجيل صوت منفصل — عشان حركة الشفايف تطلع طبيعية مثل الأنمي الواقعي، مو رسمة ثابتة تتكلم.

قواعد لتقليل الأخطاء:
1. **متحدث واحد في كل لقطة**، ووجهه واضح للكاميرا. لقطتين فيهم كلام متبادل = لقطتين منفصلتين.
2. **الجملة مكتوبة حرفيًا بين علامتي تنصيص** في الطلب، مع اسم المتحدث ووصف صوته الثابت:
   `NOONOO speaks in English, <voice description>: "..."`
3. **جملة قصيرة لكل لقطة**: لقطة 4–6 ثواني = جملة أو جملتين قصيرتين بالكثير.
4. **ثبات الصوت بين اللقطات** على مرحلتين:
   - المرحلة ١: وصف صوت ثابت لكل شخصية (تحت) ينسخ حرفيًا في كل لقطة.
   - المرحلة ٢: بعد التجربة الأولى، نختار أفضل لقطة لكل شخصية ونستخدم صوتها كـ `audio_references` في كل اللقطات الجاية — يعني الصوت نفسه مصدره التوليد، بس يصير ثابت.
5. **خطة بديلة** لو لقطة طلعت الشفايف فيها مو متطابقة: إعادة توليدها بس (مو المشهد كله).

### وصف الصوت الثابت (معتمد من ميثم)

| الشخصية | Voice description |
|---|---|
| GRANDMA KHADIJA | warm, gentle, slightly husky elderly woman voice, slow calm pace, loving tone |
| ZOOZOO | clear, soft-spoken 10-year-old girl voice, calm and polite, the "big sister" tone |
| NOONOO | bright, energetic 8-year-old girl voice, expressive and playful |
| NADYAH | sweet, high-pitched 4-year-old girl voice, curious, slightly lisping |
| HOOR | tiny, clear 2-year-old toddler voice, short simple words, spoken clearly — no babbling |
| MISHOO | playful, goofy cartoon cat voice, slightly raspy, funny comic timing, ends with a cheeky giggle |

### دور ميشو (الكوميديا)

- ميشو **عادةً** يصدر أصوات قطة بس (مواء، خرخرة).
- في **مواقف مختارة** يتكلم — وهذي لحظات الإثارة والضحك للطفل: يعلّق بجملة مضحكة، أو يسوي شي غبي (يطيح، يلحق ذيله، يتورط بشي) ثم يضحك على نفسه.
- عشان تبقى مميزة: **مرة إلى ثلاث مرات بالحلقة** بالكثير، وجملته قصيرة جدًا.
- في الطلب: `MISHOO the cat talks in English, <voice description>: "..."` مع وصف الحركة الكوميدية.

---

## ٥. التكلفة الحقيقية (Higgsfield, مقاسة بـ get_cost)

| النموذج | لقطة 5 ثواني مع الصوت |
|---|---|
| **Seedance 2.0 Mini — 720p** | **5 كريدت** (≈ 1 كريدت/ثانية) |
| Seedance 2.0 Mini — 480p | 2.5 كريدت |
| Seedance 2.0 fast — 720p | 12.5 كريدت |
| Seedance 2.0 std — 720p | 22.5 كريدت |
| Seedance 2.5 — 720p | 35 كريدت |

صورة GPT Image 2.5 (high, 2k) = 2.75 كريدت.

---

## ٦. ملاحظات مفتوحة

- شعارات الأحذية: النماذج أبقت شكل خطوط Adidas/Nike تقريبًا. ميثم وافق إنها تبقى أو تنشال — حاليًا باقية كخطوط بدون شعار واضح.
- صورتا HOUSE و GARDEN متقاربتين (كلها من قدام البيت). إذا احتجنا لقطة حديقة قريبة (المراجيح/الزحليقة)، نولّد صورة إضافية أقرب.
