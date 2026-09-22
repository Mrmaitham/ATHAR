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

**KITCHEN** — grey-wood shaker cabinets, white marble island with four white bar stools on wooden legs, three glass globe pendant lights, stainless hood and built-in ovens, brass Arabic dallah coffee pot on a tray, window with palm trees, blue Persian runner rug.

---

## ٤. الصوت وتحريك الشفايف (قرار ميثم)

الفيديو يتولد **مع الصوت** (`generate_audio: true`) عشان حركة الشفايف تطلع طبيعية مثل الأنمي الواقعي، مو رسمة ثابتة تتكلم.

قواعد لتقليل الأخطاء:
1. **متحدث واحد في كل لقطة**، ووجهه واضح للكاميرا. لقطتين فيهم كلام متبادل = لقطتين منفصلتين.
2. **الجملة مكتوبة حرفيًا بين علامتي تنصيص** في الطلب، مع اسم المتحدث:
   `NOONOO says in a warm Gulf Arabic child voice: "..."`
3. **جملة قصيرة لكل لقطة**: لقطة 4–6 ثواني = جملة أو جملتين قصيرتين بالكثير.
4. **ثبات الصوت بين اللقطات**: كل شخصية لها عينة صوت ثابتة (audio reference) تنرفق مع كل لقطة تتكلم فيها — Seedance 2.0 / Mini يقبلون `audio_references`. العينات تنسوى مرة وحدة قبل أول حلقة.
5. **خطة بديلة** إذا الصوت العربي المولّد طلع ضعيف: نولّد الفيديو، ونسجل الحوار بصوت ثابت، ونركّب الشفايف بـ **Sync Lipsync 3**.

> ملاحظة: جودة اللهجة الخليجية في الصوت المولّد مع الفيديو ما انختبرت بعد — تنقاس في تجربة المشهد الأول.

---

## ٥. ملاحظات مفتوحة

- شعارات الأحذية: النماذج أبقت شكل خطوط Adidas/Nike تقريبًا. ميثم وافق إنها تبقى أو تنشال — حاليًا باقية كخطوط بدون شعار واضح.
- صورتا HOUSE و GARDEN متقاربتين (كلها من قدام البيت). إذا احتجنا لقطة حديقة قريبة (المراجيح/الزحليقة)، نولّد صورة إضافية أقرب.
