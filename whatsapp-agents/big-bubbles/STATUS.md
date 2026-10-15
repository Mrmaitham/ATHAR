# حالة مشروع "الفقاعة الكبيرة" 🫧 — نقطة الاستئناف

> لأي جلسة جديدة: اقرأ هذا الملف + BUSINESS_BRIEF.md أولًا. الفرع: `ccr-f0f14017-ul3vxp`.

## ✅ خلص
- جمع كل معلومات النشاط (BUSINESS_BRIEF.md) والزونات (zones.md) والشخصية والماسكوت.
- البناء: business.py، booking.py، workers.py (رسائل الفريق إنجليزي/هندي)، telegram.py
  (لوحة ميثم)، app.py. 28 اختبار offline ناجحة (`python -m pytest -q`).
- ميثم سوّى: بوت تليقرام (التوكن محفوظ عنده) + حساب Claude (رصيد 10$، Auto-reload مقفول)
  + مفتاح API بدون انتهاء.

## ⏭️ الخطوة الجاية
1. ميثم يضيف المفتاح في Environment variables باسم **`BB_ANTHROPIC_KEY`** (مو ANTHROPIC_API_KEY —
   جلسات Claude Code تحجب هالاسم) ويفتح جلسة جديدة. app.py يقرا BB_ANTHROPIC_KEY أولًا.
2. اختبار حي مع Claude الحقيقي: `cd whatsapp-agents/big-bubbles && python app.py --chat`
   ومرّر السيناريوهات في tests/conversations.md (ميثم يلعب دور العميل). صلّح الردود.
3. Meta (واتساب) + Railway + ربط التليقرام — الخطوات في SETUP.md.

## ⏳ ناقص من ميثم
- رابط الدفع الثابت • اسم المواد • مواعيد رمضان • أرقام العمال (لـ WORKER_NUMBERS)
- عينات فويس كويتي (لاختبار ElevenLabs STT — طريقة الربط غير مجرّبة بعد)
