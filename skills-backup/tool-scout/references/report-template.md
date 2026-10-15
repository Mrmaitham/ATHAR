# Report template

Keep the same order every time; the user learns where to look. Write it in the user's language and dialect. Keep each section short, and cut a section to one line when there's nothing to say rather than padding it.

## Single tool

```markdown
## <اسم الأداة> — <الحكم: ✅ ركّبها | ⚠️ بشرط | ❌ لا>
<جملة وحدة: وش هي بالضبط ومن صنعها>

### وش تسوي؟
<٢–٤ نقاط: الوظيفة الحقيقية كما في الكود، مب كما في الإعلان>

### هل المدح في محله؟
<صريح: وش الصحيح ووش المبالغة، مع الدليل (ملف/تاريخ/رقم)>

### الجودة والأمان
| | التقييم | الدليل |
|---|---|---|
| الجودة | 🟢/🟡/🔴 | <آخر تحديث، توثيق، اختبارات> |
| الأمان | 🟢/🟡/🔴 | <وين تروح البيانات، مفاتيح، تتبع> |

### تفيدك أنت؟
| المشروع/الاستخدام | الفايدة | ليش |
|---|---|---|
| <مشروع ١ من ملف التعريف> | ⭐⭐⭐/⭐⭐/⭐/❌ | <سطر> |
| <مشروع ٢> | ... | ... |

**تشتغل من جهازك (<الجهاز>)؟** <نعم/لا/جزئيًا + السبب>
**التكلفة:** <مجاني / مفتاح خاص / سعر الاستخدام>

### الخلاصة
<٢–٣ أسطر: الحكم وسببه، والشرط إذا ⚠️، والبديل إذا ❌>

### طريقة التركيب (إذا ✅ أو ⚠️)
<خطوات مرقّمة مفصّلة على جهازه هو>
```

## Several tools in one request

Vet each one with a shorter version of the template above (what it is, verdict, fit), then close with:

```markdown
## المقارنة
| الأداة | وش تسوي | تشتغل من جهازك؟ | الحكم |
|---|---|---|---|
| ... | ... | ✅/⚠️/❌ | ✅/⚠️/❌ |

**توصيتي:** <إذا بتختار وحدة، أي وحدة وليش>
```

## Search request ("دوّر لي أداة تسوي كذا")

```markdown
## نتيجة البحث: <الحاجة>
**كيف دوّرت:** <المصادر في سطر، وتنبيه إن الأدوات الجديدة جدًا ممكن ما تكون مفهرسة>

### أفضل ٢–٣ (فحص كامل)
<template مختصر لكل وحدة>

### مرشحين ثانيين (سطر لكل وحدة)
- <اسم> — <ليش ما وصلت للقائمة الأولى>

**توصيتي:** ...
```

### When nothing new beats what they already have

That's a valid and useful answer, and often the right one. Say it first, then show the work briefly:

```markdown
## نتيجة البحث: <الحاجة>
**الخلاصة:** ما لقيت شي جديد يستاهل التركيب. اللي عندك أصلًا يغطي الحاجة: <الأداة الموجودة> لـ <كذا>.

**كيف تسويها باللي عندك:** <٢–٤ خطوات عملية>

**وش فحصت وليش ما نفع:**
- <اسم> — <سبب الاستبعاد في سطر>
```

## Tone

- Plain words first. When a technical term is unavoidable, explain it once in a few words: "MCP (سيرفر يعطي Claude أدوات جديدة)".
- Don't over-hedge. If the evidence is clear, say it plainly.
- Respect the person who forwarded the tool. "ممتازة للمبرمجين، بس مب لك" beats "this is useless".
