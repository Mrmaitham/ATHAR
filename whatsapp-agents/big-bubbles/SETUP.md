# تشغيل "الفقاعة الكبيرة" 🫧 على واتساب بيج ببلز

> الخطوات اللي عليها ⚠️ لازم تسويها أنت بنفسك (حسابات ودفع). لا ترسل أي مفتاح أو توكن
> في المحادثة — تنحط مباشرة في إعدادات الاستضافة.

## 1. مفتاح Claude
1. ادخل https://platform.claude.com ← سجل حساب ← Billing ← اشحن رصيد (يكفي 10$ للبداية).
2. API Keys ← Create Key ← احفظه (هذا `ANTHROPIC_API_KEY`).

## 2. حساب واتساب للأعمال (Meta) ⚠️
1. ادخل https://developers.facebook.com ← My Apps ← Create App ← نوع **Business**.
2. أضف منتج **WhatsApp** ← API Setup.
3. **الرقم**: أضف رقم بيج ببلز وأكده بـ SMS.
   - ⚠️ الرقم المربوط ما يشتغل على تطبيق الواتساب العادي بنفس الوقت (إلا لو ميزة
     Coexistence متاحة لحسابك — تخليك تستخدم تطبيق WhatsApp Business والـ API مع بعض).
   - نصيحة: جرّب أول على الرقم التجريبي اللي تعطيك Meta، وبعدين انقل للرقم الحقيقي.
4. احفظ **Phone number ID** (هذا `WHATSAPP_PHONE_NUMBER_ID`).
5. **توكن دائم**: business.facebook.com ← Settings ← Users ← **System Users** ← Add (Admin)
   ← Add Assets (التطبيق + حساب الواتساب) ← Generate Token بصلاحيات
   `whatsapp_business_messaging` و `whatsapp_business_management` (هذا `WHATSAPP_TOKEN`).
6. **App Secret**: App Settings ← Basic ← App Secret (هذا `WHATSAPP_APP_SECRET`).
7. صورة البروفايل: حط **الفقاعة الكبيرة** (`assets/mascot/concept-1-sponge-wave.png`).

## 3. الاستضافة (Railway — الأسهل) ⚠️
1. https://railway.app ← سجل بحساب GitHub ← New Project ← Deploy from GitHub repo ← اختر
   `mrmaitham/athar`، ومجلد الخدمة (Root Directory): `whatsapp-agents/big-bubbles`.
2. **مهم جدًا**: أضف **Volume** واربطه على `/data`، وحط `DB_PATH=/data/bigbubbles.db`.
   بدون هالخطوة الحجوزات تنمسح كل ما السيرفر يعيد التشغيل.
3. Variables: انسخ كل المتغيرات من `.env.example` وعبّيها:
   - `ADMIN_NUMBER` = رقمك (965xxxxxxxx بدون +)
   - `WORKER_NUMBERS` = رقم عامل سيارة 1:1,رقم عامل سيارة 2:2
   - `WHATSAPP_VERIFY_TOKEN` = أي كلمة سر تختارها
   - `PAYMENT_LINK` = خله فاضي لين يجهز الرابط
   - `ELEVENLABS_API_KEY` = للفويس (من elevenlabs.io ← API Keys) — اختياري بالبداية
4. Settings ← Networking ← Generate Domain ← بيطلع لك رابط مثل `https://bigbubbles.up.railway.app`.
5. تأكد يشتغل: افتح `https://<الرابط>/health` ← لازم يطلع `{"ok": true}`.

## 4. ربط الواتساب بالسيرفر
1. Meta ← WhatsApp ← Configuration ← Webhook ← Edit:
   - Callback URL: `https://<الرابط>/webhook`
   - Verify Token: نفس `WHATSAPP_VERIFY_TOKEN`
2. Verify and Save ← Webhook fields ← اشترك في **messages**.

## 5. التجربة قبل الإعلان
1. من جوالك الشخصي راسل رقم بيج ببلز: "هلا" ← لازم يرد الترحيب.
2. مرّر كل السيناريوهات في `tests/conversations.md`.
3. جرّب أوامر الفريق من رقمك ورقم العامل (تحت).
4. جرّب فويس بلهجة كويتية.

## 6. توثيق النشاط (Business Verification)
business.facebook.com ← Security Center ← Start Verification — يرفع حدود الرسائل اليومية
ويظهر اسم بيج ببلز للعملاء.

## 7. قوالب الرسائل (Templates) — للتذكير ورسائل المناطق البعيدة
واتساب يسمح بالرد الحر خلال **24 ساعة** من آخر رسالة للعميل بس. إذا العميل حجز قبل
أكثر من يوم، التذكير أو "بشارة اليوم البعيد" يحتاج **قالب معتمد**:
WhatsApp Manager ← Message Templates ← Create ← فئة **Utility** ← مثال:
> تذكير 🫧 موعد غسيل سيارتك اليوم الساعة {{1}} في {{2}}. إذا ما تقدر رد علينا ونأجله لك.

(نضيف إرسال القوالب للكود بعد ما تنعتمد.)

---

## أوامر الفريق (ترسلها للرقم نفسه من الواتساب)
**العمال** (من أرقام `WORKER_NUMBERS`):
- `تم 12` ← الغسيل خلص → العميل يوصله المبلغ وطريقة الدفع
- `تأخير 20` ← تأخير 20 دقيقة على الموعد الجاي (أو `تأخير 20 12`)
- `غياب 12` ← العميل مو موجود بعد 10 دقايق (ينحسب عليه)

**ميثم** (من `ADMIN_NUMBER`):
- `جدول` / `جدول بكرة` / `جدول 20/10`
- `حجز 20/10 10:30 سيارة 1 السالمية` ← حجز جاكم من برا الواتساب (اتصال/انستقرام)
- `إلغاء حجز 12` ← إلغاء بدون ما ينحسب على العميل
- `إلغاء سيارة 1 اليوم` ← عطل/ظرف → يعتذر لكل عملاء السيارة
- `مدفوع 12` ← تأكيد الدفع المسبق
- `يوم بعيد 20/10 سيارة 2: صباح الأحمد، جنوب صباح الأحمد` ← يعلن اليوم ويبلّغ قائمة الانتظار
- `انتظار` ← كم طلب ينتظر بكل منطقة بعيدة
- `/bot on 965xxxxxxxx` ← رجّع البوت لعميل بعد ما خلصت معه
- `مساعدة` ← قائمة الأوامر

## تعديل الأسعار أو المعلومات
- **الأسعار والباقات**: `business.py` (القسم الأول — PACKAGES و ADDONS).
- **المعلومات والسياسات**: `knowledge_base.md`.
- **المناطق والزونات**: `zones.md`.
- **شخصية الموظف**: `system_prompt.md`.
بعد أي تعديل: commit + push، و Railway يعيد النشر تلقائيًا. (أو قول لي وأعدّلها لك.)

## التكلفة المتوقعة (تقريبية)
- الاستضافة: ~5$ بالشهر.
- Claude (Opus 5.5): تقريبًا سنتات قليلة لكل محادثة حجز كاملة (تعليمات النظام تنحفظ بالكاش
  فتصير أرخص). لو تبي أرخص: `CLAUDE_MODEL=claude-sonnet-5-5`.
- الفويس: أقل من سنت للدقيقة تقريبًا.
- Meta: ردود خدمة العملاء خلال 24 ساعة غالبًا مجانية؛ القوالب برسوم بسيطة حسب الدولة.
