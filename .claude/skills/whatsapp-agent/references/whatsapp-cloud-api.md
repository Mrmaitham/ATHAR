# WhatsApp Cloud API — مرجع سريع

> الأرقام والحدود تتغير — تحقق من التوثيق الرسمي وقت التنفيذ:
> https://developers.facebook.com/docs/whatsapp/cloud-api
> نسخة الـ Graph API في القالب قابلة للتغيير عبر `GRAPH_API_VERSION`.

## الإعداد (يسويه صاحب النشاط)

1. **Meta for Developers** → Create App → نوع Business → أضف منتج **WhatsApp**.
2. من **WhatsApp → API Setup**: تحصل على `Phone number ID` و `WhatsApp Business
   Account ID` ورقم تجريبي تقدر تختبر عليه لحد 5 أرقام مستلمين.
3. **إضافة رقم حقيقي**: الرقم يتحقق برسالة SMS/مكالمة. الرقم المربوط بالـ API
   ما يشتغل على تطبيق الواتساب العادي في نفس الوقت (إلا بميزة Coexistence لو متاحة
   للحساب — تسمح باستخدام WhatsApp Business App والـ API معًا).
4. **Permanent Token**: Business Settings → Users → **System Users** → أنشئ
   System User (Admin) → Add Assets (التطبيق + حساب الواتساب) → Generate Token
   بصلاحيات `whatsapp_business_messaging` و `whatsapp_business_management`.
5. **App Secret**: App Settings → Basic → App Secret (للتحقق من توقيع الـ webhook).
6. **Webhook**: WhatsApp → Configuration → Callback URL = `https://<دومينك>/webhook`
   و Verify Token = نفس `WHATSAPP_VERIFY_TOKEN` → Verify and Save → اشترك في حقل
   **messages**.
7. **Business Verification** لرفع حدود المحادثات اليومية وعرض اسم النشاط.

## التحقق من الـ Webhook (GET)

Meta ترسل: `hub.mode=subscribe&hub.verify_token=...&hub.challenge=...`
→ لو التوكن مطابق، رجّع قيمة `hub.challenge` كنص خام بحالة 200.

## استقبال الرسائل (POST)

- تحقق من الهيدر `X-Hub-Signature-256` = `sha256=` + HMAC-SHA256(App Secret, body الخام).
- **رجّع 200 بسرعة** (خلال ثواني) وعالج بالخلفية — وإلا Meta تعيد الإرسال
  وتتكرر الرسائل. وخزّن `message.id` لمنع المعالجة المكررة.
- البنية: `entry[].changes[].value.messages[]` (رسائل) أو
  `value.statuses[]` (حالات التسليم/القراءة — تجاهلها أو سجّلها).
- أنواع `message.type`: `text`، `image`، `audio`، `video`، `document`،
  `location`، `interactive` (ردود الأزرار/القوائم)، `button`، `reaction`، `sticker`.
- اسم العميل: `value.contacts[0].profile.name`. رقمه: `message.from`.

## إرسال رسالة نصية

```
POST https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages
Authorization: Bearer {TOKEN}
{
  "messaging_product": "whatsapp",
  "to": "9665XXXXXXXX",
  "type": "text",
  "text": { "body": "النص", "preview_url": false }
}
```

- حد النص: **4096 حرف** للرسالة (القالب يقسّم تلقائيًا).
- علامة "تمت القراءة" + مؤشر الكتابة:
  `{"messaging_product":"whatsapp","status":"read","message_id":"<id>","typing_indicator":{"type":"text"}}`

## رسائل تفاعلية (أزرار / قوائم)

أزرار (حتى 3):
```json
{"messaging_product":"whatsapp","to":"...","type":"interactive",
 "interactive":{"type":"button","body":{"text":"تبي تكمل الطلب؟"},
  "action":{"buttons":[
   {"type":"reply","reply":{"id":"confirm","title":"أكّد"}},
   {"type":"reply","reply":{"id":"cancel","title":"إلغاء"}}]}}}
```
الرد يجي كـ `type: interactive` → `interactive.button_reply.id/title`.
قائمة (حتى 10 خيارات): `"type":"list"` مع `sections[].rows[]`.

## الوسائط (صور، صوت)

1. `message.image.id` / `message.audio.id` → `GET /{VERSION}/{MEDIA_ID}` يرجع `url`.
2. حمّل الـ `url` بنفس هيدر الـ Authorization.
3. **صور** → أرسلها لـ Claude كـ image content block (base64) — Claude يفهم الصور مباشرة.
4. **صوت** (ogg/opus) → يحتاج تحويل لنص (Speech-to-Text) بخدمة خارجية قبل Claude؛
   لو ما فيه خدمة مفعّلة، الموظف يرد بلطف: "ما أقدر أسمع الرسائل الصوتية حاليًا،
   تقدر تكتبها لي؟".

## نافذة الـ 24 ساعة والقوالب (Templates)

- خلال **24 ساعة** من آخر رسالة من العميل: ترسل أي رد حر (Service conversation).
- بعدها: ممنوع رسالة حرة — لازم **Message Template** معتمد من Meta
  (فئات: Utility / Marketing / Authentication).
- إنشاء القوالب: WhatsApp Manager → Message Templates، أو عبر API. الاعتماد
  ياخذ من دقائق لساعات.
- إرسال قالب:
```json
{"messaging_product":"whatsapp","to":"...","type":"template",
 "template":{"name":"order_update","language":{"code":"ar"},
  "components":[{"type":"body","parameters":[{"type":"text","text":"#1234"}]}]}}
```
- الرسائل التسويقية تحتاج **موافقة مسبقة (opt-in)** من العميل.

## التسعير (عام)

Meta تحاسب حسب نوع الرسالة/المحادثة والدولة؛ ردود خدمة العملاء داخل نافذة
الـ 24 ساعة غالبًا مجانية أو أرخص بكثير من التسويقية. راجع صفحة التسعير
الرسمية للدولة المستهدفة قبل التقدير لميثم.

## أخطاء شائعة

| الخطأ | السبب |
|-------|-------|
| `131047` Re-engagement message | انتهت نافذة الـ 24 ساعة → استخدم Template |
| `190` / 401 | التوكن منتهي (غالبًا التوكن المؤقت) → استخدم System User token |
| `131030` Recipient not in allowed list | الرقم التجريبي يرسل فقط للأرقام المضافة يدويًا |
| الـ webhook ما يوصل | ما اشتركت في حقل `messages`، أو الرابط مو HTTPS |
| رسائل مكررة | السيرفر بطيء بالرد بـ 200 أو ما فيه dedup على `message.id` |
