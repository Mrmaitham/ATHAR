"""الفقاعة الكبيرة 🫧 — موظف خدمة عملاء بيج ببلز على الواتساب.

WhatsApp Cloud API + Claude + محرك حجوزات (booking.py).

تشغيل السيرفر:         uvicorn app:app --host 0.0.0.0 --port 8000
اختبار محلي بالطرفية:   python app.py --chat
"""

import base64
import hashlib
import hmac
import json
import os
import re
import sqlite3
import sys
import threading
import time
from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path

import anthropic
import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

import business as biz
import telegram
import workers
from booking import WEEKDAYS, BookingError, Store, now_kw, parse_date

load_dotenv()
BASE = Path(__file__).parent

MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
EFFORT = os.getenv("CLAUDE_EFFORT", "medium")
WA_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WA_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WA_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
WA_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
GRAPH = f"https://graph.facebook.com/{os.getenv('GRAPH_API_VERSION', 'v23.0')}"
ADMIN = os.getenv("ADMIN_NUMBER", "").strip()
# "96550000000:1,96560000000:2" — رقم العامل : رقم سيارة الغسيل
WORKERS = {p.split(":")[0].strip(): int(p.split(":")[1]) for p in
           os.getenv("WORKER_NUMBERS", "").split(",") if ":" in p}
PAYMENT_LINK = os.getenv("PAYMENT_LINK", "").strip()
STT_KEY = os.getenv("ELEVENLABS_API_KEY", "")
HANDOFF_HOURS = float(os.getenv("HANDOFF_HOURS", "12"))
HISTORY_TURNS = int(os.getenv("HISTORY_TURNS", "30"))
DB_PATH = os.getenv("DB_PATH", str(BASE / "bigbubbles.db"))
tg = telegram.Telegram(os.getenv("TELEGRAM_BOT_TOKEN", ""), os.getenv("TELEGRAM_ADMIN_CHAT_ID", ""))
ADMIN_DIGESTS = os.getenv("ADMIN_DIGESTS", "1") != "0"   # ملخص 8 الصبح + 9 بالليل
MAX_WA_CHARS = 4000

# BB_ANTHROPIC_KEY أولًا: جلسات Claude Code تحجب ANTHROPIC_API_KEY من البيئة
claude = anthropic.Anthropic(api_key=os.getenv("BB_ANTHROPIC_KEY") or os.getenv("ANTHROPIC_API_KEY"))
store = Store(DB_PATH)


def build_system_prompt() -> str:
    kb = (BASE / "knowledge_base.md").read_text(encoding="utf-8")
    kb = kb.replace("{{PAYMENT_LINK}}", PAYMENT_LINK or "لسا ما انضاف — الدفع كي نت مع الشباب، أو الفريق يرسل الرابط")
    prompt = (BASE / "system_prompt.md").read_text(encoding="utf-8")
    return prompt.replace("{{PRICE_TABLE}}", biz.price_table_text()).replace("{{KNOWLEDGE_BASE}}", kb)


SYSTEM_PROMPT = build_system_prompt()

# ---------------------------------------------------------------- المحادثات

db = store.db
db.executescript(
    """
    CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, phone TEXT, role TEXT, content TEXT, ts REAL);
    CREATE TABLE IF NOT EXISTS seen (wa_id TEXT PRIMARY KEY, ts REAL);
    CREATE TABLE IF NOT EXISTS handoffs (phone TEXT PRIMARY KEY, reason TEXT, ts REAL);
    CREATE TABLE IF NOT EXISTS last_media (phone TEXT PRIMARY KEY, kind TEXT, media_id TEXT, ts REAL);
    CREATE TABLE IF NOT EXISTS locations (phone TEXT PRIMARY KEY, text TEXT, ts REAL);
    """
)


def already_seen(wa_id: str) -> bool:
    try:
        db.execute("INSERT INTO seen VALUES (?, ?)", (wa_id, time.time()))
        db.commit()
        return False
    except sqlite3.IntegrityError:
        return True


def save_message(phone: str, role: str, content: str) -> None:
    db.execute("INSERT INTO messages (phone, role, content, ts) VALUES (?, ?, ?, ?)",
               (phone, role, content, time.time()))
    db.commit()


def load_history(phone: str) -> list[dict]:
    rows = db.execute("SELECT role, content FROM messages WHERE phone = ? ORDER BY id DESC LIMIT ?",
                      (phone, HISTORY_TURNS)).fetchall()[::-1]
    history: list[dict] = []
    for role, content in rows:
        if history and history[-1]["role"] == role:
            history[-1]["content"] += "\n" + content
        else:
            history.append({"role": role, "content": content})
    while history and history[0]["role"] != "user":
        history.pop(0)
    return history


def in_handoff(phone: str) -> bool:
    row = db.execute("SELECT ts FROM handoffs WHERE phone = ?", (phone,)).fetchone()
    return bool(row) and time.time() - row[0] < HANDOFF_HOURS * 3600


def set_handoff(phone: str, on: bool, reason: str = "") -> None:
    if on:
        db.execute("INSERT OR REPLACE INTO handoffs VALUES (?, ?, ?)", (phone, reason, time.time()))
    else:
        db.execute("DELETE FROM handoffs WHERE phone = ?", (phone,))
    db.commit()


def working_hours() -> bool:
    return 8 <= now_kw().hour < 20


# ---------------------------------------------------------------- الإرسال (واتساب أو الطرفية)

def split_message(text: str) -> list[str]:
    parts = []
    while len(text) > MAX_WA_CHARS:
        cut = text.rfind("\n", 0, MAX_WA_CHARS)
        cut = cut if cut > 0 else MAX_WA_CHARS
        parts.append(text[:cut].strip())
        text = text[cut:]
    parts.append(text.strip())
    return [p for p in parts if p]


def wa_post(payload: dict) -> dict:
    r = httpx.post(f"{GRAPH}/{WA_PHONE_ID}/messages", json=payload, timeout=20,
                   headers={"Authorization": f"Bearer {WA_TOKEN}"})
    if r.status_code >= 400:
        print("WhatsApp API error:", r.status_code, r.text, file=sys.stderr)
    return r.json() if r.content else {}


def wa_send_text(to: str, text: str) -> None:
    for part in split_message(text):
        wa_post({"messaging_product": "whatsapp", "to": to, "type": "text",
                 "text": {"body": part, "preview_url": False}})


def wa_send_image(to: str, media_id: str, caption: str) -> None:
    wa_post({"messaging_product": "whatsapp", "to": to, "type": "image",
             "image": {"id": media_id, "caption": caption[:1000]}})


def wa_download(media_id: str) -> tuple[bytes, str]:
    auth = {"Authorization": f"Bearer {WA_TOKEN}"}
    meta = httpx.get(f"{GRAPH}/{media_id}", headers=auth, timeout=20).json()
    data = httpx.get(meta["url"], headers=auth, timeout=60).content
    return data, meta.get("mime_type", "application/octet-stream")


def wa_upload(data: bytes, mime: str) -> str:
    r = httpx.post(f"{GRAPH}/{WA_PHONE_ID}/media", headers={"Authorization": f"Bearer {WA_TOKEN}"},
                   data={"messaging_product": "whatsapp", "type": mime},
                   files={"file": ("file", data, mime)}, timeout=60)
    return r.json().get("id", "")


_poster_ids: dict[str, tuple[str, float]] = {}   # ملف → (media_id, وقت الرفع)


def wa_send_poster(to: str, path: Path, caption: str) -> None:
    """يرفع البوستر مرة وحدة ويعيد استخدامه (ميديا واتساب تنتهي بعد 30 يوم — نجدد كل أسبوع)."""
    media_id, ts = _poster_ids.get(path.name, ("", 0.0))
    if not media_id or time.time() - ts > 7 * 86400:
        media_id = wa_upload(path.read_bytes(), "image/jpeg")
        if not media_id:
            raise httpx.HTTPError("upload failed")
        _poster_ids[path.name] = (media_id, time.time())
    wa_send_image(to, media_id, caption)


def wa_mark_read(message_id: str) -> None:
    wa_post({"messaging_product": "whatsapp", "status": "read", "message_id": message_id,
             "typing_indicator": {"type": "text"}})


# تقدر تستبدلها (وضع الاختبار يطبع بالطرفية بدل الإرسال)
SEND = wa_send_text
SEND_POSTER = wa_send_poster
crew = workers.Crew(store, WORKERS, lambda to, text: SEND(to, text))


def tell_customer(phone: str, text: str) -> None:
    """رسالة من الموظف للعميل خارج دورة المحادثة — تنحفظ عشان يتذكرها."""
    save_message(phone, "assistant", text)
    SEND(phone, text)


def tell_admin(text: str, buttons: list[list[tuple[str, str]]] | None = None) -> None:
    """التنبيهات لميثم: على تليقرام لو مفعّل، وإلا على واتساب."""
    if tg.ready and SEND is wa_send_text:
        tg.send(text, buttons)
    elif ADMIN:
        SEND(ADMIN, text)


# ---------------------------------------------------------------- تحويل الفويس لنص

def transcribe(audio: bytes, mime: str) -> str | None:
    """ElevenLabs Speech-to-Text. يرجع None لو الخدمة مو مفعّلة أو ما انفهم الصوت."""
    if not STT_KEY:
        return None
    try:
        r = httpx.post("https://api.elevenlabs.io/v1/speech-to-text", headers={"xi-api-key": STT_KEY},
                       data={"model_id": os.getenv("STT_MODEL", "scribe_v1"), "language_code": "ara"},
                       files={"file": ("voice.ogg", audio, mime)}, timeout=60)
        r.raise_for_status()
        text = (r.json().get("text") or "").strip()
        return text or None
    except (httpx.HTTPError, ValueError) as e:
        print("STT error:", e, file=sys.stderr)
        return None


# ---------------------------------------------------------------- الأدوات (Tools)

CAR_SCHEMA = {
    "type": "object",
    "properties": {
        "vehicle": {"type": "string", "enum": list(biz.VEHICLES),
                    "description": "saloon=صالون، jeep=جيب، large=سيارة كبيرة (بيك أب/جيب كبير/فان/باص)، motorcycle=دراجة نارية"},
        "package": {"type": "string", "enum": list(biz.PACKAGES),
                    "description": "bubbles=ببلز، super=سوبر ببلز، super_top=سوبر توب ببلز، special=سيشل ببلز (لا تحتاجها للدراجة)"},
        "addons": {"type": "array", "items": {"type": "string", "enum": list(biz.ADDONS)},
                   "description": "freshener=معطر، tissues=كلينكس، trunk=تنظيف الدبة"},
        "description": {"type": "string", "description": "الموديل واللون، مثل: كامري بيضاء"},
    },
    "required": ["vehicle"],
}
CARS = {"type": "array", "items": CAR_SCHEMA, "minItems": 1}
DATE = {"type": "string", "description": "التاريخ بصيغة YYYY-MM-DD"}

TOOLS = [
    {"name": "get_price", "description": "يحسب السعر الدقيق لسيارة أو أكثر مع الإضافات. استخدمها لأي سؤال عن السعر.",
     "input_schema": {"type": "object", "properties": {"cars": CARS}, "required": ["cars"]}},
    {"name": "check_availability",
     "description": "يرجع المواعيد المتاحة لمنطقة العميل بيوم معين، مع السعر. لازم قبل أي حجز. "
                    "area = اسم المنطقة بالعربي (مثل السالمية، خيطان).",
     "input_schema": {"type": "object", "properties": {"date": DATE, "area": {"type": "string"}, "cars": CARS},
                      "required": ["date", "area", "cars"]}},
    {"name": "create_booking",
     "description": "يثبت الحجز. استخدمها فقط بعد ما تلخص الحجز للعميل ويأكد صراحةً.",
     "input_schema": {"type": "object", "properties": {
         "name": {"type": "string"}, "area": {"type": "string"}, "date": DATE,
         "time": {"type": "string", "description": "الموعد بصيغة HH:MM من المواعيد المتاحة، مثل 10:30 أو 13:30"},
         "cars": CARS,
         "notes": {"type": "string", "description": "تفاصيل المكان: عمارة/سرداب/بيت، رقم البيت أو الشقة، "
                                                   "مين يسلم المفتاح، توفر كهرباء"},
         "worker_notes": {"type": "string", "description": "نفس الملاحظات بالإنجليزي البسيط للعمال "
                                                          "(مثال: Basement parking, guard allows entry, "
                                                          "son will give keys, power socket available)"}},
         "required": ["name", "area", "date", "time", "cars"]}},
    {"name": "my_bookings", "description": "حجوزات العميل الجاية.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "cancel_booking", "description": "يلغي حجز للعميل (بعد ما يأكد).",
     "input_schema": {"type": "object", "properties": {"booking_id": {"type": "integer"}},
                      "required": ["booking_id"]}},
    {"name": "reschedule_booking", "description": "يأجل حجز لموعد جديد متاح (بعد ما يأكد).",
     "input_schema": {"type": "object", "properties": {"booking_id": {"type": "integer"}, "date": DATE,
                                                       "time": {"type": "string"}},
                      "required": ["booking_id", "date", "time"]}},
    {"name": "join_far_waitlist",
     "description": "يسجل عميل منطقة بعيدة بقائمة الانتظار لين يتحدد يوم لمنطقته.",
     "input_schema": {"type": "object", "properties": {
         "name": {"type": "string"}, "area": {"type": "string"}, "cars": CARS,
         "preferred_days": {"type": "string", "description": "الأيام/الأوقات اللي تناسبه"}},
         "required": ["name", "area", "cars"]}},
    {"name": "send_package_posters",
     "description": "يرسل للعميل صور بوسترات الباقات (كل بوستر فيه محتوى الباقة وسعرها للصالون والجيب). "
                    "استخدمها لما يسأل عن الأسعار بشكل عام أو الفرق بين الباقات. "
                    "packages فاضية = كل الباقات من الأرخص للأغلى.",
     "input_schema": {"type": "object", "properties": {
         "packages": {"type": "array", "items": {"type": "string", "enum": list(biz.POSTERS)}}}}},
    {"name": "handoff_to_human",
     "description": "يحوّل المحادثة لميثم (موظف بشري) ويوقف المساعد الآلي لهالعميل.",
     "input_schema": {"type": "object", "properties": {
         "reason": {"type": "string"}, "summary": {"type": "string", "description": "ملخص الطلب والمحادثة"}},
         "required": ["reason", "summary"]}},
]


def _car_text(cars: list[dict]) -> str:
    out = []
    for c in cars:
        pkg = biz.PACKAGES.get(c.get("package"), {}).get("name", "")
        out.append(" ".join(x for x in [biz.VEHICLES.get(c.get("vehicle"), ""), c.get("description", ""), pkg] if x))
    return "، ".join(out)


def run_tool(phone: str, name: str, args: dict) -> dict:
    try:
        if name == "get_price":
            return biz.quote(args["cars"])

        if name == "send_package_posters":
            keys = [k for k in biz.POSTERS if k in (args.get("packages") or biz.POSTERS)]
            sent = []
            for k in keys:
                try:
                    SEND_POSTER(phone, biz.POSTERS_DIR / biz.POSTERS[k], biz.PACKAGES[k]["name"])
                    sent.append(biz.PACKAGES[k]["name"])
                except (httpx.HTTPError, OSError) as e:
                    print("poster error:", e, file=sys.stderr)
            if not sent:
                return {"ok": False, "error": "ما قدرت أرسل الصور — اكتب له الباقات والأسعار نصًا"}
            return {"ok": True, "sent": sent, "note": "الصور وصلت العميل قبل ردك — لا تكرر كل محتواها نصًا"}

        if name == "check_availability":
            result = store.availability(date.fromisoformat(args["date"]), args["area"], args["cars"])
            result.pop("_slot_van", None)
            result["customer_needs_prepay"] = store.strikes(phone) >= biz.STRIKES_FOR_PREPAY
            if result.get("ok") and not result["available_times"] and not result.get("far_zone"):
                result["hint"] = "ما فيه مواعيد هاليوم — اعرض يوم ثاني"
            return result

        if name == "create_booking":
            loc = db.execute("SELECT text FROM locations WHERE phone = ?", (phone,)).fetchone()
            b = store.create(phone, args["name"], args["area"], date.fromisoformat(args["date"]),
                             args["time"], args["cars"], loc[0] if loc else "", args.get("notes", ""),
                             worker_notes=args.get("worker_notes", ""))
            b.pop("cars", None)
            crew.notify(store.get(b["booking_id"]), "new")
            if b["prepay_required"]:
                b["payment_link"] = PAYMENT_LINK or "مو متوفر — قل إن الفريق بيرسل الرابط"
            tell_admin(f"🆕 *حجز #{b['booking_id']}*{' (دفع مسبق ⏳)' if b['prepay_required'] else ''}\n"
                       f"{b['weekday']} {b['date']} — {b['time']} — سيارة غسيل {b['van']}\n"
                       f"{args['name']} • +{phone} • {b['area']}\n{_car_text(args['cars'])}\n"
                       f"الإجمالي: {b['total']}\n{args.get('notes', '')}\n"
                       f"{('📍 ' + loc[0]) if loc else '📍 لسا ما أرسل اللوكيشن'}",
                       [[("✅ وصل الدفع", f"مدفوع {b['booking_id']}")]] if b["prepay_required"] else None)
            return b

        if name == "my_bookings":
            return {"bookings": store.upcoming_for(phone)}

        if name == "cancel_booking":
            r = store.cancel(args["booking_id"], phone)
            crew.notify(store.get(args["booking_id"]), "cancel")
            tell_admin(f"❌ العميل +{phone} ألغى الحجز #{args['booking_id']}"
                       f"{' (إلغاء متأخر — ينحسب)' if r['late'] else ''}")
            return r

        if name == "reschedule_booking":
            b = store.reschedule(args["booking_id"], phone, date.fromisoformat(args["date"]), args["time"])
            b.pop("cars", None)
            crew.notify(store.get(args["booking_id"]), "cancel")
            crew.notify(store.get(b["booking_id"]), "moved")
            tell_admin(f"🔁 العميل +{phone} أجّل الحجز #{args['booking_id']} → #{b['booking_id']} "
                       f"{b['date']} {b['time']} (سيارة {b['van']})")
            return b

        if name == "join_far_waitlist":
            r = store.join_waitlist(phone, args["name"], args["area"], args["cars"],
                                    args.get("preferred_days", ""))
            tell_admin(f"📋 قائمة انتظار {r['area']}: صار فيها {r['waiting_in_area']} طلب\n"
                       f"آخرهم: {args['name']} • +{phone} • {_car_text(args['cars'])}\n"
                       f"يناسبه: {args.get('preferred_days', '-')}")
            return r

        if name == "handoff_to_human":
            set_handoff(phone, True, args.get("reason", ""))
            tell_admin(f"🔔 *تحويل عميل*\nالرقم: +{phone}\nالسبب: {args.get('reason')}\n"
                       f"الملخص: {args.get('summary')}\n\nلإرجاع البوت: /bot on {phone}",
                       [[("↩️ رجّع البوت للعميل", f"/bot on {phone}")]])
            forward_last_media(phone)
            return {"ok": True, "working_hours": working_hours()}

        return {"error": f"أداة غير معروفة: {name}"}
    except BookingError as e:
        return {"ok": False, "error": str(e)}
    except (ValueError, KeyError, biz.PricingError) as e:
        return {"ok": False, "error": f"بيانات غير صحيحة: {e}"}


def forward_last_media(phone: str) -> None:
    row = db.execute("SELECT kind, media_id, ts FROM last_media WHERE phone = ?", (phone,)).fetchone()
    if not row or time.time() - row[2] > 1800 or SEND is not wa_send_text:
        return
    try:
        data, mime = wa_download(row[1])
        if tg.ready:
            tg.send_photo(data, f"📎 آخر صورة من العميل +{phone}")
            return
        if not ADMIN:
            return
        new_id = wa_upload(data, mime)
        if new_id:
            wa_send_image(ADMIN, new_id, f"📎 آخر صورة من العميل +{phone}")
    except (httpx.HTTPError, KeyError) as e:
        print("forward media error:", e, file=sys.stderr)


# ---------------------------------------------------------------- عقل الموظف (Claude)

def turn_context(phone: str, profile_name: str, is_new: bool) -> str:
    n = now_kw()
    ctx = f"[الوقت الآن: {WEEKDAYS[n.weekday()]} {n:%Y-%m-%d %H:%M} بتوقيت الكويت"
    if profile_name:
        ctx += f" • اسم العميل بالواتساب: {profile_name}"
    if is_new:
        ctx += " • عميل جديد: أول رسالة منه"
    if store.strikes(phone) >= biz.STRIKES_FOR_PREPAY:
        ctx += " • هالعميل حجوزاته بدفع مسبق"
    return ctx + "]\n"


def agent_reply(phone: str, user_content: str | list, history_text: str, profile_name: str = "") -> str:
    is_new = not load_history(phone)
    save_message(phone, "user", history_text)
    messages = load_history(phone)
    ctx = turn_context(phone, profile_name, is_new)
    last = messages[-1]["content"]
    if isinstance(user_content, list):          # صورة + نص
        messages[-1]["content"] = [{"type": "text", "text": ctx + last}] + user_content
    else:
        messages[-1]["content"] = ctx + last

    reply = ""
    for _ in range(8):
        resp = claude.beta.messages.create(
            model=MODEL, max_tokens=8000,
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            thinking={"type": "adaptive"}, output_config={"effort": EFFORT},
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            tools=TOOLS, messages=messages,
        )
        if resp.stop_reason == "refusal":
            set_handoff(phone, True, "refusal")
            tell_admin(f"⚠️ المساعد ما قدر يرد على العميل +{phone} — تحتاج ترد بنفسك.")
            reply = "السموحة 🙏 بحوّلك لأحد من الفريق يفيدك أكثر."
            break
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        if text:
            reply = text
        if resp.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                out = run_tool(phone, b.name, b.input)
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": json.dumps(out, ensure_ascii=False, default=str),
                                "is_error": out.get("ok") is False and "error" in out})
        messages.append({"role": "user", "content": results})

    reply = reply or "لحظات وأرجع لك 🫧"
    save_message(phone, "assistant", reply)
    return reply


# ---------------------------------------------------------------- أوامر الفريق

HELP = """🫧 أوامر الفريق:
*العمال* (بالإنجليزي/الهندي، يوصلهم جدول اليوم 8 الصبح تلقائيًا):
• done 12 • late 20 • noshow 12 • schedule • tomorrow • next
*ميثم* (هنا بتليقرام):
• تم 12 / تأخير 20 12 / غياب 12
• جدول / جدول بكرة / جدول 20/10
• حجز 20/10 10:30 سيارة 1 السالمية ← حجز من برا الواتساب
• إلغاء حجز 12 ← إلغاء بدون ما ينحسب على العميل
• إلغاء سيارة 1 اليوم ← نعتذر لكل عملاء السيارة
• مدفوع 12 ← تأكيد الدفع المسبق
• يوم بعيد 20/10 سيارة 2: صباح الأحمد، جنوب صباح الأحمد
• انتظار ← قوائم انتظار المناطق البعيدة
• /bot on 965xxxxxxxx ← رجّع البوت لعميل محوّل"""


def job_done(booking_id: int):
    b = store.set_status(booking_id, "done")
    pay = f"\nأو من الرابط: {PAYMENT_LINK}" if PAYMENT_LINK else ""
    if b["phone"] != "manual":
        tell_customer(b["phone"], f"سيارتك صارت تلمع ✨\nالمبلغ: *{biz.fmt_kd(b['total'])}*\n"
                                  f"تقدر تدفع كي نت مع الشباب{pay}\n"
                                  "ننطرك المرة الجاية، الفقاعة الكبيرة في الخدمة 🫧")
    return b


def job_late(minutes: int, booking_id: int | None, van: int | None):
    """يرجع (الحجز، هل تبلّغ العميل)."""
    b = store.get(booking_id) if booking_id else (store.next_for_van(van) if van else None)
    if not b or minutes < biz.DELAY_NOTIFY_MINUTES or b["phone"] == "manual":
        return b, False
    tell_customer(b["phone"], f"نعتذر منك 🙏 فريقنا بيتأخر عليك تقريبًا {minutes} دقيقة "
                              "بسبب الزحمة، ونوصلك بأقرب وقت بإذن الله 🫧")
    return b, True


def job_noshow(booking_id: int):
    b = store.set_status(booking_id, "no_show")
    if b["phone"] != "manual":
        tell_customer(b["phone"], "حاول فريقنا يوصل لك بموعدك وانتظرك 10 دقايق، بس للأسف ما قدرنا 🙏\n"
                                  "تقدر تحجز موعد جديد متى ما تبي 🫧")
        tell_admin(f"🚫 غياب بالحجز #{b['id']} (+{b['phone']}) — صار عنده {store.strikes(b['phone'])} من 2")
    return b


def handle_worker_command(van: int, text: str) -> str:
    """رد العمال دايمًا بالإنجليزي والهندي."""
    cmd = workers.parse_command(text)
    if not cmd:
        return "❓ Unknown command | कमांड समझ नहीं आई\n\n" + workers.HELP
    kind, groups = cmd
    try:
        if kind == "done":
            b = job_done(int(groups[0]))
            crew.send_next(b["van"])
            return f"✅ #{b['id']} done — customer informed | काम पूरा — ग्राहक को बता दिया"
        if kind == "late":
            b, told = job_late(int(groups[0]), int(groups[1]) if groups[1] else None, van)
            if not b:
                return "No next job found — send: late 20 <job no.> | अगला काम नहीं मिला"
            if not told:
                return "Under 15 min is normal — customer not informed | 15 मिनट से कम — ग्राहक को नहीं बताया"
            return f"✅ Customer #{b['id']} informed about delay | ग्राहक को देरी बता दी"
        if kind == "noshow":
            b = job_noshow(int(groups[0]))
            crew.send_next(b["van"])
            return f"✅ #{b['id']} marked no-show | ग्राहक नहीं मिला — दर्ज किया"
        if kind == "schedule":
            return workers.schedule_text(store, van, now_kw().date())
        if kind == "tomorrow":
            return workers.schedule_text(store, van, now_kw().date() + timedelta(days=1))
        if kind == "next":
            r = store.next_for_van(van)
            return ("➡️ Next job | अगला काम\n\n" + workers.job_text(r)) if r else \
                "✅ No more jobs today | आज और कोई काम नहीं"
        return workers.HELP
    except BookingError:
        return "⚠️ Job number not found | यह काम नंबर नहीं मिला"


def handle_staff_command(sender: str, text: str) -> str | None:
    """يرجع رد للفريق، أو None لو الرسالة مو أمر."""
    if sender in WORKERS and sender != ADMIN:
        return handle_worker_command(WORKERS[sender], text)
    if sender != ADMIN:
        return None
    return handle_admin_command(text)


def admin_schedule(day: date, title: str = "") -> str:
    rows = store.day_schedule(day)
    head = f"{title}📅 *{WEEKDAYS[day.weekday()]} {day:%d/%m}*"
    if not rows:
        return head + "\nما فيه حجوزات."
    lines = [head]
    for van in biz.VANS:
        mine = [r for r in rows if r["van"] == van]
        far = store.far_day(day, van=van)
        lines.append(f"\n🚐 سيارة {van} — {len(mine)}/{len(biz.SLOTS)} مواعيد"
                     + (" — يوم بعيد: " + "، ".join(json.loads(far["areas"])) if far else ""))
        for r in mine:
            lines.append(f"• {biz.fmt_time(biz.SLOTS[r['slot']])} #{r['id']} {r['name']} • {r['area']} • "
                         f"{biz.fmt_kd(r['total'])}"
                         f"{' ✅' if r['status'] == 'done' else (' ⏳' if r['status'] == 'pending_payment' else '')}")
    total = sum(r["total"] for r in rows)
    lines.append(f"\n💰 المتوقع: {biz.fmt_kd(total)} • {len(rows)} حجز")
    return "\n".join(lines)


def handle_admin_command(text: str) -> str | None:
    t = text.strip()
    try:
        if t in ("مساعدة", "اوامر", "أوامر", "help"):
            return HELP

        m = re.fullmatch(r"تم\s*#?(\d+)", t)
        if m:
            b = job_done(int(m.group(1)))
            crew.send_next(b["van"])
            return f"✅ الحجز #{b['id']} خلص وانرسل للعميل."

        m = re.fullmatch(r"تأخير\s+(\d+)\s+#?(\d+)", t)
        if m:
            b, told = job_late(int(m.group(1)), int(m.group(2)), None)
            return (f"✅ بلّغت عميل الحجز #{b['id']} بالتأخير." if told else
                    "ما بلغت العميل (التأخير أقل من 15 دقيقة أو الحجز مو موجود).")

        m = re.fullmatch(r"غياب\s*#?(\d+)", t)
        if m:
            b = job_noshow(int(m.group(1)))
            return f"✅ انحسب غياب للحجز #{b['id']}."

        m = re.fullmatch(r"جدول(?:\s+(.+))?", t)
        if m:
            return admin_schedule(parse_date(m.group(1) or "اليوم"))

        m = re.fullmatch(r"حجز\s+(\S+)\s+(\S+)\s+سيارة\s*(\d)\s+(.+)", t)
        if m:
            bid = store.manual_block(parse_date(m.group(1)), m.group(2), int(m.group(3)), m.group(4))
            crew.notify(store.get(bid), "new")
            return f"✅ انحجز الموعد يدويًا (#{bid})."

        m = re.fullmatch(r"إلغاء حجز\s*#?(\d+)", t)
        if m:
            b = store.set_status(int(m.group(1)), "cancelled")
            crew.notify(b, "cancel")
            return f"✅ انلغى الحجز #{b['id']} بدون ما ينحسب على العميل."

        m = re.fullmatch(r"إلغاء سيارة\s*(\d)\s*(.*)", t)
        if m:
            day = parse_date(m.group(2) or "اليوم")
            rows = store.cancel_van_day(int(m.group(1)), day)
            crew.to_van(int(m.group(1)), f"❌ All jobs on {day:%d/%m} cancelled | "
                                         f"{day:%d/%m} के सारे काम रद्द — {len(rows)}")
            for r in rows:
                if r["phone"] != "manual":
                    tell_customer(r["phone"], "نعتذر منك 🙏 صار عندنا ظرف طارئ واضطرينا نلغي موعدك "
                                              f"({biz.fmt_time(biz.SLOTS[r['slot']])}). لك الأولوية بأقرب "
                                              "موعد — رد علي وأحجز لك على طول 🫧")
            return f"✅ انلغت {len(rows)} مواعيد لسيارة {m.group(1)} يوم {day} وتبلّغ العملاء."

        m = re.fullmatch(r"مدفوع\s*#?(\d+)", t)
        if m:
            b = store.set_status(int(m.group(1)), "confirmed")
            set_handoff(b["phone"], False)
            crew.notify(b, "new")
            tell_customer(b["phone"], f"تم! وصلنا الدفع وثبتت لك الحجز 🫧\n"
                                      f"{b['day']} — {biz.fmt_time(biz.SLOTS[b['slot']])}")
            return f"✅ الحجز #{b['id']} تثبت."

        m = re.fullmatch(r"يوم بعيد\s+(\S+)\s+سيارة\s*(\d)\s*[:：]\s*(.+)", t)
        if m:
            day = parse_date(m.group(1))
            areas = [a.strip() for a in re.split(r"[،,]", m.group(3)) if a.strip()]
            waiting = store.announce_far_day(day, int(m.group(2)), areas)
            for w in waiting:
                tell_customer(w["phone"], f"بشارة 🫧 بنكون متواجدين في {w['area']} يوم "
                                          f"{WEEKDAYS[day.weekday()]} {day}. تبي أحجز لك موعد؟")
            return f"✅ انعلن اليوم، وتبلّغ {len(waiting)} من قائمة الانتظار."

        if t == "انتظار":
            rows = store.waitlist_summary()
            return "\n".join(f"• {a}: {n}" for a, n in rows) or "قوائم الانتظار فاضية."

        m = re.fullmatch(r"/bot (on|off) (\d+)", t)
        if m:
            set_handoff(m.group(2), m.group(1) == "off", "admin")
            return f"✅ البوت {m.group(1)} للرقم {m.group(2)}"
    except BookingError as e:
        return f"⚠️ {e}"
    except ValueError as e:
        return f"⚠️ صيغة غير صحيحة: {e}\nاكتب: مساعدة"
    return None


# ---------------------------------------------------------------- استقبال الرسائل

def handle_message(msg: dict, profile_name: str = "") -> None:
    phone, wa_id, kind = msg["from"], msg["id"], msg.get("type")
    if already_seen(wa_id):
        return

    if (phone == ADMIN or phone in WORKERS) and kind == "text":
        answer = handle_staff_command(phone, msg["text"]["body"])
        if answer:
            SEND(phone, answer)
            return
    if phone in WORKERS and phone != ADMIN:  # الفريق ما يكلم موظف العملاء
        SEND(phone, workers.HELP)
        return

    user_content: str | list = ""
    history_text = ""
    if kind == "text":
        history_text = user_content = msg["text"]["body"]
    elif kind == "interactive":
        i = msg["interactive"]
        history_text = user_content = (i.get("button_reply") or i.get("list_reply") or {}).get("title", "")
    elif kind == "location":
        loc = msg["location"]
        text = f"https://maps.google.com/?q={loc.get('latitude')},{loc.get('longitude')} {loc.get('address', '')}"
        db.execute("INSERT OR REPLACE INTO locations VALUES (?, ?, ?)", (phone, text.strip(), time.time()))
        db.commit()
        history_text = user_content = "[العميل أرسل اللوكيشن ✅ — انحفظ مع الحجز]"
    elif kind == "image":
        media_id = msg["image"]["id"]
        caption = msg["image"].get("caption", "")
        db.execute("INSERT OR REPLACE INTO last_media VALUES (?, 'image', ?, ?)", (phone, media_id, time.time()))
        db.commit()
        history_text = f"[العميل أرسل صورة] {caption}".strip()
        try:
            data, mime = wa_download(media_id)
            user_content = [{"type": "image", "source": {"type": "base64", "media_type": mime,
                                                         "data": base64.b64encode(data).decode()}}]
        except (httpx.HTTPError, KeyError):
            user_content = history_text
    elif kind == "audio":
        try:
            data, mime = wa_download(msg["audio"]["id"])
            text = transcribe(data, mime)
        except (httpx.HTTPError, KeyError):
            text = None
        history_text = user_content = (f"🎤 (فويس): {text}" if text else
                                       "[العميل أرسل فويس وما انفهم — اطلب منه بلطف يكتبه]")
    else:
        return  # ستيكر / رياكشن / غيره

    if in_handoff(phone):
        save_message(phone, "user", history_text)
        return

    if SEND is wa_send_text:
        wa_mark_read(wa_id)
    try:
        reply = agent_reply(phone, user_content, history_text, profile_name)
    except anthropic.APIError as e:
        print("Claude API error:", e, file=sys.stderr)
        reply = "السموحة صار عندنا خلل بسيط 🙏 حاول مرة ثانية بعد شوي."
    SEND(phone, reply)


# ---------------------------------------------------------------- التذكير قبل الموعد

def send_reminders() -> None:
    for r in store.due_reminders():
        store.mark_reminded(r["id"])
        tell_customer(r["phone"], f"تذكير 🫧 موعد غسيل سيارتك اليوم الساعة "
                                  f"*{biz.fmt_time(biz.SLOTS[r['slot']])}* في {r['area']}.\n"
                                  "تأكد إن فيه أحد يسلّم الشباب المفتاح وإن الدخول للموقع مسموح.\n"
                                  "إذا ما تقدر، رد علي وأأجله لك 🙏")


def send_daily_schedules() -> None:
    today = now_kw().date().isoformat()
    if now_kw().hour >= workers.DAILY_HOUR and store.kv_get("daily_sent") != today:
        store.kv_set("daily_sent", today)
        crew.daily()


def send_admin_digests() -> None:
    if not ADMIN_DIGESTS:
        return
    n = now_kw()
    today = n.date().isoformat()
    if n.hour >= 8 and store.kv_get("admin_morning") != today:
        store.kv_set("admin_morning", today)
        waiting = store.waitlist_summary()
        extra = ("\n\n📋 ينتظرون بالمناطق البعيدة: " + "، ".join(f"{a} ({c})" for a, c in waiting)) if waiting else ""
        tell_admin(admin_schedule(n.date(), "☀️ صباح الخير — ") + extra)
    if n.hour >= 21 and store.kv_get("admin_night") != today:
        store.kv_set("admin_night", today)
        tell_admin(admin_schedule(n.date() + timedelta(days=1), "🌙 جدول بكرة — "))


def reminder_loop() -> None:
    while True:
        try:
            send_reminders()
            send_daily_schedules()
            send_admin_digests()
        except Exception as e:  # noqa: BLE001 — اللوب لازم ما يوقف
            print("reminder error:", e, file=sys.stderr)
        time.sleep(60)


# ---------------------------------------------------------------- السيرفر

@asynccontextmanager
async def lifespan(_app):
    threading.Thread(target=reminder_loop, daemon=True).start()
    tg.start(handle_admin_command)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/webhook")
def verify(request: Request):
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and q.get("hub.verify_token") == WA_VERIFY_TOKEN:
        return PlainTextResponse(q.get("hub.challenge", ""))
    raise HTTPException(status_code=403)


@app.post("/webhook")
async def receive(request: Request, background: BackgroundTasks):
    body = await request.body()
    expected = "sha256=" + hmac.new(WA_APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not WA_APP_SECRET or not hmac.compare_digest(expected, request.headers.get("X-Hub-Signature-256", "")):
        raise HTTPException(status_code=401)
    data = json.loads(body)
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            names = {c.get("wa_id"): c.get("profile", {}).get("name", "") for c in value.get("contacts", [])}
            for msg in value.get("messages", []):
                background.add_task(handle_message, msg, names.get(msg.get("from"), ""))
    return {"ok": True}


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}


# ---------------------------------------------------------------- اختبار محلي بالطرفية

def chat_cli() -> None:
    global SEND, SEND_POSTER, ADMIN
    ADMIN = ADMIN or "admin"
    for n, v in (("worker1", 1), ("helper1", 1), ("worker2", 2), ("helper2", 2)):
        WORKERS.setdefault(n, v)
    customer = f"test{int(time.time())}"

    def show(to: str, text: str) -> None:
        who = "🫧 للعميل" if to.startswith("test") else (f"👷 لـ{to}" if to in WORKERS else "📲 لميثم")
        print(f"\n{who}:\n{text}\n")

    SEND = show
    SEND_POSTER = lambda to, path, caption: print(f"\n🖼️ للعميل: [صورة {path.name}] — {caption}\n")
    print(f"وضع الاختبار ({MODEL}). اكتب كعميل. أوامر خاصة:\n"
          "  !ادمن <أمر>     ← رسالة من ميثم (مثل: !ادمن جدول بكرة)\n"
          "  !عامل1 <أمر>    ← رسالة من سواق سيارة 1 (مثل: !عامل1 done 1)\n"
          "  !صبح            ← إرسال جدول اليوم للفريق الحين\n"
          "  !موقع           ← العميل يرسل لوكيشن\n"
          "  !عميل جديد      ← عميل ثاني\n"
          "  Ctrl+C للخروج\n")
    n = 0
    while True:
        try:
            line = input("👤 ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        n += 1
        sender, msg = customer, {"type": "text", "text": {"body": line}}
        if line.startswith("!ادمن "):
            sender, msg["text"]["body"] = ADMIN, line[len("!ادمن "):]
        elif m := re.match(r"!عامل(\d) (.+)", line):
            sender, msg["text"]["body"] = f"worker{m.group(1)}", m.group(2)
        elif line == "!موقع":
            msg = {"type": "location", "location": {"latitude": 29.3375, "longitude": 48.0746,
                                                    "address": "السالمية، قطعة 10"}}
        elif line == "!صبح":
            crew.daily()
            continue
        elif line == "!عميل جديد":
            customer = f"test{int(time.time())}"
            print("— عميل جديد —")
            continue
        msg.update({"from": sender, "id": f"cli-{n}-{time.time()}"})
        handle_message(msg, "عميل تجربة")
        send_reminders()


if __name__ == "__main__":
    if "--chat" in sys.argv:
        chat_cli()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
