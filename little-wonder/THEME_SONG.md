# Little Wonder — أغنية البداية (Opening Theme)

- **اللغة:** إنجليزي. **تنعاد كما هي في بداية كل حلقة.**
- **المدة المستهدفة:** 30–45 ثانية.
- **النسخة الأولى (62.6 ثانية):** https://suno.com/s/sNn4T4ypI4ddaTR9 — طويلة، اتقصّرت أدناه.

---

## النسخة المختصرة — المعتمدة للتوليد (هدف ~40 ثانية)

نفس الأسلوب ونفس القافية ونفس الترتيب، بس بدون التكرار.

```
[Intro]
Hey hey, come and play!
Little Wonder starts today!

[Verse]
ZooZo's kind, she leads the way,
NooNo's got ideas to play,
Nadiah asks a hundred whys,
Little Hoor waves up so high!

[Bridge]
Grandma Khadija, warm and wise,
Mishoo the cat with big round eyes!

[Chorus]
Little Wonder, Little Wonder,
Every day's a brand new wonder!
```

**اللي انشال ووين راح معناه:**

| انشال | ليش ما ضاع المعنى |
|---|---|
| الـ Chorus الأول (كان ينعاد مرتين) | باقي مرة وحدة في النهاية، وهي أقوى مكان له |
| "Come along, let's go together!" | معناها (تعال معنا) موجود أصلاً في "Hey hey, come and play!" |
| الـ Outro "Little Wonder... starts today!" | نفس السطر موجود في الـ Intro |

**الباقي كامل:** الترحيب، والبنات الأربع كل وحدة بسطرها، وتيتة، وميشو، واللازمة.

---

## نسخة أقصر احتياطية (هدف ~30 ثانية)

لو النسخة فوق طلعت أطول من 45 ثانية:

```
[Intro]
Hey hey, come and play!

[Verse]
ZooZo's kind, she leads the way,
NooNo's got ideas to play,
Nadiah asks a hundred whys,
Little Hoor waves up so high!
Grandma Khadija, warm and wise,
Mishoo the cat with big round eyes!

[Chorus]
Little Wonder, Little Wonder —
Every day's a brand new wonder!
```

---

## نصائح للتحكم بالمدة في Suno

1. **قلّل الوسوم (tags).** كل `[Intro]` و `[Bridge]` يخلي Suno يضيف موسيقى بدون غناء. النسخة الاحتياطية فيها 3 وسوم بس.
2. **لا تكتب `[Outro]`** — هو اللي يطوّل النهاية بموسيقى زايدة.
3. **ضيف للـ style prompt:** `short intro, no long instrumental outro, ends quickly`.
4. لو Suno يعطي خيار مدة أو `Custom Mode`، حدد ~40 ثانية.

---

## Prompt الموسيقى

> Upbeat cheerful preschool kids TV theme song, 110 BPM, major key, bright ukulele, glockenspiel and hand claps, light bouncy drums, warm female lead vocal with a small children's choir on the chorus, playful spoken parts, a cat meow sound effect at the start, catchy sing-along hook, short intro, no long instrumental outro, ends quickly.

---

## تقطيع المشاهد (Storyboard) — مبني على النسخة المختصرة

10 لقطات. **الثواني تقديرية** لين يوصل ملف الصوت ونقيس التوقيت الحقيقي.

| # | المقطع | المشهد | المكان |
|---|---|---|---|
| 1 | "Hey hey, come and play!" | البوابة تنفتح، الكاميرا تدخل على الممر، ميشو يطل ويموء | HOUSE |
| 2 | "Little Wonder starts today!" | الكاميرا ترفع على البيت وقت الغروب، **عنوان Little Wonder يظهر** | HOUSE |
| 3 | "ZooZo's kind, she leads the way" | زوزو تمسك يد حور وتمشي فيها بهدوء | GARDEN |
| 4 | "NooNo's got ideas to play" | نونو تطلع فكرة، تشير بيدها بحماس | GARDEN |
| 5 | "Nadiah asks a hundred whys" | نادية ترفع يدها وتسأل بفضول، علامات استفهام تطير حولها | GARDEN |
| 6 | "Little Hoor waves up so high!" | حور تلوّح للكاميرا بيدها الصغيرة وهي تضحك | GARDEN |
| 7 | "Grandma Khadija, warm and wise" | تيتة على درج البيت تفتح يديها، البنات يركضون لحضنها | HOUSE |
| 8 | "Mishoo the cat with big round eyes!" | لقطة قريبة لميشو، عيونه الكبيرة، يميل راسه ويموء | LIVING ROOM |
| 9 | "Little Wonder, Little Wonder" | الكل يرقص في الحديقة، ميشو يطيح من المرجيحة ويضحك | GARDEN |
| 10 | "Every day's a brand new wonder!" | الكل ينظرون للكاميرا ويبتسمون، **العنوان يظهر ويثبت** | GARDEN |

**التكلفة:** 10 لقطات × 5 ثواني بـ Seedance Mini بدون صوت ≈ **50 كريدت**. تنسوى مرة وحدة وتنعاد في كل حلقة.

---

## طريقة الإنتاج

1. نولّد الأغنية المختصرة في Suno.
2. نولّد الـ 10 لقطات **بدون صوت** (`generate_audio: false` — أرخص، والأغنية بتغطي المقدمة كلها).
3. نركّب اللقطات على الأغنية في المونتاج، والقص على ضربات الإيقاع.

### الناقص

- [ ] **ملف الأغنية MP3** — Suno يمنع التحميل من برّا، فلازم ميثم ينزّله ويرفعه هنا. منه نطلع التوقيت الحقيقي لكل سطر.

---

## المعنى بالعربي

| السطر | المعنى |
|---|---|
| Hey hey, come and play! | هيه هيه، تعال نلعب! |
| Little Wonder starts today! | Little Wonder يبدأ اليوم! |
| ZooZo's kind, she leads the way | زوزو طيبة وهي اللي تقود الطريق |
| NooNo's got ideas to play | نونو عندها أفكار للّعب |
| Nadiah asks a hundred whys | نادية تسأل مية "ليش" |
| Little Hoor waves up so high! | وحور الصغيرة تلوّح عالي! |
| Grandma Khadija, warm and wise | تيتة خديجة، دافية وحكيمة |
| Mishoo the cat with big round eyes | وميشو القطو بعيونه الكبيرة |
| Every day's a brand new wonder! | كل يوم فيه عجب جديد! |

> ⚠️ **إملاء:** كلمات Suno تكتب `ZooZo / NooNo / Nadiah`، والمعتمد في المشروع `ZOOZOO / NOONOO / NADYAH`. الفرق ما يأثر على الغناء، بس نستخدم المعتمد في أي كتابة تظهر على الشاشة أو في وصف الفيديو.
