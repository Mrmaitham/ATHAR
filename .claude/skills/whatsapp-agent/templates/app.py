"""موظف خدمة عملاء على الواتساب — WhatsApp Cloud API + Claude.

تشغيل السيرفر:        uvicorn app:app --host 0.0.0.0 --port 8000
اختبار محلي بالطرفية:  python app.py --chat
"""

import hashlib
import hmac
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

import anthropic
import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

load_dotenv()
BASE = Path(__file__).parent

MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
EFFORT = os.getenv("CLAUDE_EFFORT", "medium")
WA_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WA_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WA_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
WA_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
GRAPH_VERSION = os.getenv("GRAPH_API_VERSION", "v23.0")
ADMIN_NUMBERS = {n.strip() for n in os.getenv("ADMIN_NUMBERS", "").split(",") if n.strip()}
HANDOFF_HOURS = float(os.getenv("HANDOFF_HOURS", "12"))
HISTORY_TURNS = int(os.getenv("HISTORY_TURNS", "20"))
DB_PATH = os.getenv("DB_PATH", str(BASE / "agent.db"))
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}/{WA_PHONE_ID}/messages"
MAX_WA_CHARS = 4000  # حد واتساب 4096 — نترك هامش

claude = anthropic.Anthropic()


def load_system_prompt() -> str:
    prompt = (BASE / "system_prompt.md").read_text(encoding="utf-8")
    kb = (BASE / "knowledge_base.md").read_text(encoding="utf-8")
    return prompt.replace("{{KNOWLEDGE_BASE}}", kb)


SYSTEM_PROMPT = load_system_prompt()

# ---------------------------------------------------------------- قاعدة البيانات

db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.executescript(
    """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY, phone TEXT, role TEXT, content TEXT, ts REAL);
    CREATE TABLE IF NOT EXISTS seen (wa_id TEXT PRIMARY KEY, ts REAL);
    CREATE TABLE IF NOT EXISTS handoffs (
        phone TEXT PRIMARY KEY, reason TEXT, summary TEXT, ts REAL);
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY, phone TEXT, kind TEXT, data TEXT, ts REAL);
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
    rows = db.execute(
        "SELECT role, content FROM messages WHERE phone = ? ORDER BY id DESC LIMIT ?",
        (phone, HISTORY_TURNS),
    ).fetchall()[::-1]
    history: list[dict] = []
    for role, content in rows:
        # Claude يتطلب تناوب الأدوار — ندمج الرسائل المتتالية من نفس الطرف
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


def end_handoff(phone: str) -> None:
    db.execute("DELETE FROM handoffs WHERE phone = ?", (phone,))
    db.commit()


# ---------------------------------------------------------------- الأدوات (Tools)
# عدّل/أضف أدوات حسب صلاحيات النشاط. handoff_to_human لازم تبقى دائمًا.

TOOLS = [
    {
        "name": "handoff_to_human",
        "description": "حوّل المحادثة لموظف بشري. استخدمها عند طلب العميل لموظف، "
                       "الشكاوى، طلبات الاسترجاع/التعويض، أو أي شيء خارج صلاحياتك.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "سبب التحويل باختصار"},
                "summary": {"type": "string", "description": "ملخص المحادثة وطلب العميل للموظف"},
            },
            "required": ["reason", "summary"],
        },
    },
    {
        "name": "create_order",
        "description": "سجّل طلبًا جديدًا بعد أن يؤكد العميل التفاصيل صراحةً.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "items": {"type": "array", "items": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "qty": {"type": "integer"}},
                    "required": ["name", "qty"]}},
                "address": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["customer_name", "items"],
        },
    },
]


def run_tool(phone: str, name: str, args: dict, notify) -> str:
    if name == "handoff_to_human":
        db.execute("INSERT OR REPLACE INTO handoffs VALUES (?, ?, ?, ?)",
                   (phone, args.get("reason", ""), args.get("summary", ""), time.time()))
        db.commit()
        alert = (f"🔔 *تحويل عميل*\nالرقم: +{phone}\nالسبب: {args.get('reason')}\n"
                 f"الملخص: {args.get('summary')}\n\nلإرجاع البوت: /bot on {phone}")
        for admin in ADMIN_NUMBERS:
            notify(admin, alert)
        return "تم التحويل وتنبيه الفريق."

    if name == "create_order":
        # TODO: اربطها بنظام النشاط الفعلي (Shopify / Google Sheets / API) إن وُجد
        cur = db.execute("INSERT INTO records (phone, kind, data, ts) VALUES (?, ?, ?, ?)",
                         (phone, "order", json.dumps(args, ensure_ascii=False), time.time()))
        db.commit()
        for admin in ADMIN_NUMBERS:
            notify(admin, f"🛒 *طلب جديد #{cur.lastrowid}*\nمن: +{phone}\n"
                          f"{json.dumps(args, ensure_ascii=False, indent=1)}")
        return f"تم تسجيل الطلب برقم {cur.lastrowid}."

    return f"أداة غير معروفة: {name}"


# ---------------------------------------------------------------- عقل الموظف (Claude)

def agent_reply(phone: str, user_text: str, notify) -> str:
    save_message(phone, "user", user_text)
    messages = load_history(phone)
    reply = ""

    for _ in range(5):  # حد أقصى لجولات الأدوات
        resp = claude.beta.messages.create(
            model=MODEL,
            max_tokens=8000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            thinking={"type": "adaptive"},
            output_config={"effort": EFFORT},
            system=[{"type": "text", "text": SYSTEM_PROMPT,
                     "cache_control": {"type": "ephemeral"}}],
            tools=TOOLS,
            messages=messages,
        )
        if resp.stop_reason == "refusal":
            break
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        if text:
            reply = text
        if resp.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": resp.content})
        results = [
            {"type": "tool_result", "tool_use_id": b.id,
             "content": run_tool(phone, b.name, b.input, notify)}
            for b in resp.content if b.type == "tool_use"
        ]
        messages.append({"role": "user", "content": results})

    reply = reply or "لحظات وأرجع لك 🙏"
    save_message(phone, "assistant", reply)
    return reply


# ---------------------------------------------------------------- واتساب

def split_message(text: str) -> list[str]:
    parts: list[str] = []
    while len(text) > MAX_WA_CHARS:
        cut = text.rfind("\n", 0, MAX_WA_CHARS)
        cut = cut if cut > 0 else MAX_WA_CHARS
        parts.append(text[:cut].strip())
        text = text[cut:]
    parts.append(text.strip())
    return [p for p in parts if p]


def wa_post(payload: dict) -> None:
    r = httpx.post(GRAPH_URL, json=payload, timeout=20,
                   headers={"Authorization": f"Bearer {WA_TOKEN}"})
    if r.status_code >= 400:
        print("WhatsApp API error:", r.status_code, r.text, file=sys.stderr)


def wa_send_text(to: str, text: str) -> None:
    for part in split_message(text):
        wa_post({"messaging_product": "whatsapp", "to": to, "type": "text",
                 "text": {"body": part, "preview_url": False}})


def wa_mark_read(message_id: str) -> None:
    wa_post({"messaging_product": "whatsapp", "status": "read", "message_id": message_id,
             "typing_indicator": {"type": "text"}})


def extract_text(msg: dict) -> str | None:
    t = msg.get("type")
    if t == "text":
        return msg["text"]["body"]
    if t == "interactive":
        i = msg["interactive"]
        return (i.get("button_reply") or i.get("list_reply") or {}).get("title")
    if t == "button":
        return msg["button"].get("text")
    if t == "location":
        loc = msg["location"]
        return f"[العميل أرسل موقعه: {loc.get('latitude')},{loc.get('longitude')} {loc.get('address', '')}]"
    if t in ("image", "video", "document"):
        caption = msg.get(t, {}).get("caption", "")
        return f"[العميل أرسل {t}] {caption}".strip()
    if t == "audio":
        return "[العميل أرسل رسالة صوتية — لا تستطيع سماعها، اطلب منه كتابتها بلطف]"
    return None  # reaction / sticker / unsupported → تجاهل


def handle_message(msg: dict) -> None:
    phone, wa_id = msg["from"], msg["id"]
    if already_seen(wa_id):
        return
    text = extract_text(msg)
    if not text:
        return

    # أوامر الإدارة: /bot on <رقم>  أو  /bot off <رقم>
    if phone in ADMIN_NUMBERS and text.startswith("/bot"):
        parts = text.split()
        if len(parts) == 3 and parts[1] in ("on", "off"):
            if parts[1] == "on":
                end_handoff(parts[2])
            else:
                db.execute("INSERT OR REPLACE INTO handoffs VALUES (?, 'admin', '', ?)",
                           (parts[2], time.time()))
                db.commit()
            wa_send_text(phone, f"✅ البوت {parts[1]} للرقم {parts[2]}")
        return

    if in_handoff(phone):
        save_message(phone, "user", text)  # نحفظها للموظف البشري، والبوت يسكت
        return

    wa_mark_read(wa_id)
    try:
        reply = agent_reply(phone, text, wa_send_text)
    except anthropic.APIError as e:
        print("Claude API error:", e, file=sys.stderr)
        reply = "عذرًا، صار عندنا خلل بسيط 🙏 حاول مرة ثانية بعد شوي."
    wa_send_text(phone, reply)


# ---------------------------------------------------------------- السيرفر

app = FastAPI()


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
    if not WA_APP_SECRET or not hmac.compare_digest(
            expected, request.headers.get("X-Hub-Signature-256", "")):
        raise HTTPException(status_code=401)

    data = json.loads(body)
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                background.add_task(handle_message, msg)
    return {"ok": True}  # نرد بسرعة على Meta والمعالجة بالخلفية


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}


# ---------------------------------------------------------------- اختبار محلي

def chat_cli() -> None:
    phone = "test-" + str(int(time.time()))
    ADMIN_NUMBERS.add("الإدارة")  # عشان تنبيهات التحويل/الطلبات تنطبع بالطرفية
    print(f"وضع الاختبار ({MODEL}) — اكتب رسالتك كأنك عميل. Ctrl+C للخروج.\n")

    def notify(to, text):
        print(f"\n[تنبيه للإدارة → {to}]\n{text}\n")

    while True:
        try:
            text = input("👤 العميل: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if in_handoff(phone):
            print("🤖 (البوت ساكت — المحادثة محوّلة لموظف بشري)\n")
            continue
        print(f"🤖 الموظف: {agent_reply(phone, text, notify)}\n")


if __name__ == "__main__":
    if "--chat" in sys.argv:
        chat_cli()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
