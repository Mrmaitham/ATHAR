"""تدفق كامل بدون إنترنت: Claude وهمي يستدعي الأدوات، وأوامر الفريق، والـ webhook."""
import copy
import hashlib
import hmac
import json
import os
from datetime import timedelta
from types import SimpleNamespace as NS

os.environ.update(DB_PATH=":memory:", ADMIN_NUMBER="96599999999", WORKER_NUMBERS="96588888888:1",
                  WHATSAPP_APP_SECRET="sec", WHATSAPP_VERIFY_TOKEN="vt", ANTHROPIC_API_KEY="x")

import app  # noqa: E402
from booking import now_kw  # noqa: E402

SENT: list[tuple[str, str]] = []
app.SEND = lambda to, text: SENT.append((to, text))
TOMORROW = (now_kw().date() + timedelta(days=1)).isoformat()
CAR = [{"vehicle": "saloon", "package": "bubbles", "addons": ["freshener"]}]


def tool(tool_name, /, **inp):
    return NS(type="tool_use", id=f"t-{tool_name}", name=tool_name, input=inp)


def fake_claude(script):
    calls = []

    def create(**kw):
        calls.append(copy.deepcopy(kw))
        step = script[len(calls) - 1]
        blocks = step if isinstance(step, list) else [NS(type="text", text=step)]
        stop = "tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn"
        return NS(stop_reason=stop, content=blocks)

    app.claude.beta.messages.create = create
    return calls


def msg(sender, text, mid):
    return {"from": sender, "id": mid, "type": "text", "text": {"body": text}}


def test_full_booking_flow_and_done_command():
    calls = fake_claude([
        [tool("check_availability", date=TOMORROW, area="السالمية", cars=CAR)],
        [tool("create_booking", name="أحمد", area="السالمية", date=TOMORROW, time="10:30", cars=CAR,
              notes="بيت، أحمد موجود")],
        "تم! ثبتت لك الحجز 🫧",
    ])
    app.handle_message(msg("96511111111", "ابي احجز بكرة 10:30 السالمية", "m1"), "أحمد")
    first = calls[0]
    assert first["model"] == "claude-opus-5-5" and first["fallbacks"] == "default"
    assert "الوقت الآن" in first["messages"][-1]["content"] and "عميل جديد" in first["messages"][-1]["content"]
    avail = json.loads(calls[1]["messages"][-1]["content"][0]["content"])
    assert "10:30 الصبح" in avail["available_times"] and avail["price"]["total"] == 5.0
    booked = json.loads(calls[2]["messages"][-1]["content"][0]["content"])
    assert booked["booking_id"] == 1 and booked["status"] == "confirmed"
    assert any(to == "96599999999" and "حجز #1" in t for to, t in SENT)        # تنبيه لميثم
    assert SENT[-1] == ("96511111111", "تم! ثبتت لك الحجز 🫧")

    SENT.clear()
    app.handle_message(msg("96588888888", "تم 1", "m2"))                       # العامل خلص
    assert any(to == "96511111111" and "5 د.ك" in t and "تلمع" in t for to, t in SENT)
    assert SENT[-1][0] == "96588888888" and "काम पूरा" in SENT[-1][1]   # رد العامل بالإنجليزي والهندي


def test_handoff_silences_bot_until_admin_returns_it():
    fake_claude([[tool("handoff_to_human", reason="شكوى", summary="خدش")], "حوّلتك للفريق"])
    app.handle_message(msg("96522222222", "في خدش بسيارتي!", "h1"))
    assert app.in_handoff("96522222222")
    SENT.clear()
    app.handle_message(msg("96522222222", "وينكم؟", "h2"))
    assert SENT == []                                                           # البوت ساكت
    app.handle_message(msg("96599999999", "/bot on 96522222222", "h3"))
    assert not app.in_handoff("96522222222")


def test_customer_cannot_run_staff_commands():
    fake_claude(["ما فهمت عليك 🫧"])
    app.handle_message(msg("96533333333", "تم 1", "c1"))
    assert app.store.get(1)["status"] == "done"  # من الاختبار الأول — ما تغيّر
    assert SENT[-1][0] == "96533333333"


def test_duplicate_webhook_message_processed_once():
    calls = fake_claude(["هلا 🫧", "هلا مرة ثانية"])
    app.handle_message(msg("96544444444", "هلا", "dup"))
    app.handle_message(msg("96544444444", "هلا", "dup"))
    assert len(calls) == 1


def test_webhook_signature_and_verify():
    from fastapi.testclient import TestClient
    c = TestClient(app.app)
    assert c.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "vt",
                                     "hub.challenge": "42"}).text == "42"
    body = json.dumps({"entry": []}).encode()
    sig = "sha256=" + hmac.new(b"sec", body, hashlib.sha256).hexdigest()
    assert c.post("/webhook", content=body, headers={"X-Hub-Signature-256": sig}).status_code == 200
    assert c.post("/webhook", content=body, headers={"X-Hub-Signature-256": "sha256=x"}).status_code == 401


def test_admin_commands_schedule_and_far_day():
    SENT.clear()
    app.handle_message(msg("96599999999", "جدول بكرة", "a1"))
    assert "#1" in SENT[-1][1]
    fake_claude([[tool("join_far_waitlist", name="سالم", area="صباح الأحمد", cars=CAR,
                       preferred_days="أي يوم")], "سجلتك 🫧"])
    app.handle_message(msg("96555555555", "انا بصباح الاحمد", "a2"))
    d = (now_kw().date() + timedelta(days=3)).strftime("%d/%m")
    app.handle_message(msg("96599999999", f"يوم بعيد {d} سيارة 2: صباح الأحمد", "a3"))
    assert any(to == "96555555555" and "صباح الأحمد" in t for to, t in SENT)
    assert "تبلّغ 1" in SENT[-1][1]


def test_send_package_posters_all_and_selected():
    posters = []
    app.SEND_POSTER = lambda to, path, caption: posters.append((to, path.name, caption))
    r = app.run_tool("96511111111", "send_package_posters", {})
    assert r["ok"] and [p[1] for p in posters] == ["1-basic.jpg", "2-super-bubbles.jpg",
                                                   "3-super-top-bubbles.jpg", "4-special-bubbles.jpg"]
    assert all((app.biz.POSTERS_DIR / p[1]).exists() for p in posters)
    posters.clear()
    r = app.run_tool("96511111111", "send_package_posters", {"packages": ["special", "bubbles"], "resend": True})
    assert [p[1] for p in posters] == ["1-basic.jpg", "4-special-bubbles.jpg"]


def test_send_package_posters_failure_falls_back_to_text():
    def boom(*a):
        raise OSError("no file")
    app.SEND_POSTER = boom
    r = app.run_tool("96511111112", "send_package_posters", {})
    assert not r["ok"]


def test_admin_alert_does_not_repeat_vehicle_label():
    assert app._car_text([{"vehicle": "saloon", "package": "bubbles", "description": "صالون"}]) == "صالون ببلز"
    assert app._car_text([{"vehicle": "jeep", "package": "super", "description": "كامري بيضا"}]) == "جيب كامري بيضا سوبر ببلز"


def test_posters_not_resent_unless_asked():
    posters = []
    app.SEND_POSTER = lambda to, path, caption: posters.append(path.name)
    phone = "96512121212"
    app.run_tool(phone, "send_package_posters", {})
    posters.clear()
    r = app.run_tool(phone, "send_package_posters", {"packages": ["super"]})
    assert posters == [] and r["already_sent"] == ["سوبر ببلز"]
    assert "بوسترات وصلته قبل" in app.turn_context(phone, "", False)
    app.run_tool(phone, "send_package_posters", {"packages": ["super"], "resend": True})
    assert posters == ["2-super-bubbles.jpg"]


def test_sticker_sent_once_for_new_customer():
    stickers = []
    app.SEND_STICKER = lambda to: stickers.append(to)
    fake_claude(["هلا", "تمام"])
    app.agent_reply("96513131313", "هلا", "هلا")
    app.agent_reply("96513131313", "شكرا", "شكرا")
    assert stickers == ["96513131313"]
    assert app.STICKER.exists() and app.STICKER.stat().st_size < 100_000
