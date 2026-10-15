"""لوحة ميثم على تليقرام: الصلاحيات، الأزرار، الملخصات."""
import os

os.environ.setdefault("DB_PATH", ":memory:")
os.environ.setdefault("ADMIN_NUMBER", "96599999999")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")

import app  # noqa: E402
import telegram  # noqa: E402


class FakeTG(telegram.Telegram):
    def __init__(self):
        super().__init__("token", "111")
        self.calls = []

    def _call(self, method, **kw):
        self.calls.append((method, kw.get("json") or kw.get("data")))
        return {"ok": True, "result": []}

    def texts(self):
        return [(p["chat_id"], p["text"]) for m, p in self.calls if m == "sendMessage"]


def test_only_admin_chat_can_run_commands():
    tg = FakeTG()
    ran = []
    tg._dispatch({"message": {"chat": {"id": 222}, "text": "جدول"}}, lambda t: ran.append(t))
    assert ran == [] and tg.texts() == []                     # غريب: تجاهل
    tg._dispatch({"message": {"chat": {"id": 222}, "text": "/start"}}, lambda t: ran.append(t))
    assert tg.texts()[-1][0] == "222" and "222" in tg.texts()[-1][1] and ran == []
    tg._dispatch({"message": {"chat": {"id": 111}, "text": "📅 جدول بكرة"}}, lambda t: ran.append(t) or "ok")
    assert ran == ["جدول بكرة"] and tg.texts()[-1] == ("111", "ok")


def test_button_press_runs_command():
    tg = FakeTG()
    ran = []
    tg._dispatch({"callback_query": {"id": "q", "data": "/bot on 965123", "message": {"chat": {"id": 111}}}},
                 lambda t: ran.append(t) or "done")
    assert ran == ["/bot on 965123"] and ("answerCallbackQuery", {"callback_query_id": "q"}) in tg.calls


def test_buttons_and_formatting():
    tg = FakeTG()
    tg.send("*حجز #5*", [[("✅ وصل الدفع", "مدفوع 5")]])
    payload = tg.calls[-1][1]
    assert payload["text"] == "حجز #5"
    assert payload["reply_markup"]["inline_keyboard"][0][0]["callback_data"] == "مدفوع 5"


def test_admin_digest_sent_once_morning_and_night(monkeypatch):
    sent = []
    app.SEND = lambda to, text: sent.append((to, text))
    from datetime import datetime
    from booking import KW
    monkeypatch.setattr(app, "now_kw", lambda: datetime(2026, 10, 20, 21, 30, tzinfo=KW))
    app.send_admin_digests()
    app.send_admin_digests()
    admin = [t for to, t in sent if to == app.ADMIN]
    assert len(admin) == 2 and "صباح الخير" in admin[0] and "جدول بكرة" in admin[1]
