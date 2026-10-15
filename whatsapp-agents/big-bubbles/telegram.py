"""لوحة ميثم على تليقرام: كل التنبيهات + الأوامر بأزرار.

- ما فيه حد 24 ساعة ولا تكلفة.
- يقبل أوامر من TELEGRAM_ADMIN_CHAT_ID فقط. لو مو محدد، يرد على /start برقم المحادثة
  عشان ميثم يحطه بالإعدادات (وما ينفذ أي أمر).
"""

import sys
import threading

import httpx

MENU = {"📅 جدول اليوم": "جدول", "📅 جدول بكرة": "جدول بكرة",
        "📋 انتظار": "انتظار", "❓ مساعدة": "مساعدة"}
KEYBOARD = {"keyboard": [["📅 جدول اليوم", "📅 جدول بكرة"], ["📋 انتظار", "❓ مساعدة"]],
            "resize_keyboard": True, "is_persistent": True}
MAX_CHARS = 4000


class Telegram:
    def __init__(self, token: str, admin_chat_id: str):
        self.token, self.admin = token, admin_chat_id.strip()
        self.api = f"https://api.telegram.org/bot{token}"

    @property
    def ready(self) -> bool:
        return bool(self.token and self.admin)

    def _call(self, method: str, **kw) -> dict:
        try:
            r = httpx.post(f"{self.api}/{method}", timeout=kw.pop("_timeout", 20), **kw)
            data = r.json()
            if not data.get("ok"):
                print("Telegram error:", method, data, file=sys.stderr)
            return data
        except (httpx.HTTPError, ValueError) as e:
            print("Telegram error:", method, e, file=sys.stderr)
            return {}

    def send(self, text: str, buttons: list[list[tuple[str, str]]] | None = None,
             chat_id: str | None = None) -> None:
        """buttons = [[(النص، الأمر)], ...] — الضغط على الزر ينفذ الأمر."""
        text = text.replace("*", "")  # تنسيق واتساب ما يلزم هنا
        chunks = [text[i:i + MAX_CHARS] for i in range(0, len(text), MAX_CHARS)] or [""]
        for i, chunk in enumerate(chunks):
            payload = {"chat_id": chat_id or self.admin, "text": chunk, "disable_web_page_preview": True}
            if buttons and i == len(chunks) - 1:
                payload["reply_markup"] = {"inline_keyboard": [
                    [{"text": label, "callback_data": cmd[:64]} for label, cmd in row] for row in buttons]}
            elif i == 0 and not buttons:
                payload["reply_markup"] = KEYBOARD
            self._call("sendMessage", json=payload)

    def send_photo(self, data: bytes, caption: str) -> None:
        self._call("sendPhoto", data={"chat_id": self.admin, "caption": caption[:1000]},
                   files={"photo": ("photo.jpg", data)}, _timeout=60)

    def poll_forever(self, handle_command) -> None:
        """يستقبل رسائل وأزرار ميثم (long polling — ما يحتاج webhook)."""
        offset = 0
        while True:
            data = self._call("getUpdates", json={"offset": offset, "timeout": 50,
                                                  "allowed_updates": ["message", "callback_query"]},
                              _timeout=70)
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                try:
                    self._dispatch(upd, handle_command)
                except Exception as e:  # noqa: BLE001 — اللوب لازم ما يوقف
                    print("Telegram handler error:", e, file=sys.stderr)

    def _dispatch(self, upd: dict, handle_command) -> None:
        if "callback_query" in upd:
            q = upd["callback_query"]
            chat = str(q["message"]["chat"]["id"])
            self._call("answerCallbackQuery", json={"callback_query_id": q["id"]})
            if chat == self.admin:
                self.send(handle_command(q.get("data", "")) or "❓")
            return
        msg = upd.get("message") or {}
        chat, text = str(msg.get("chat", {}).get("id", "")), (msg.get("text") or "").strip()
        if not chat or not text:
            return
        if chat != self.admin:
            if text.startswith("/start"):
                self.send(f"رقم المحادثة: {chat}\nحطه في TELEGRAM_ADMIN_CHAT_ID بإعدادات الاستضافة "
                          "وبعدين أعد التشغيل 🫧", chat_id=chat)
            return
        if text.startswith("/start"):
            self.send("هلا ميثم 🫧 هنا توصلك كل تنبيهات بيج ببلز. استخدم الأزرار تحت أو اكتب أي أمر.")
            return
        self.send(handle_command(MENU.get(text, text)) or "❓ أمر غير معروف — اضغط ❓ مساعدة")

    def start(self, handle_command) -> None:
        if self.token:
            threading.Thread(target=self.poll_forever, args=(handle_command,), daemon=True).start()
