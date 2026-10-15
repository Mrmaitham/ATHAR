"""رسائل الفريق: جدول الصبح، التنبيهات، أوامر إنجليزي/هندي."""
import os
from datetime import timedelta

os.environ.setdefault("DB_PATH", ":memory:")
os.environ.setdefault("ADMIN_NUMBER", "96599999999")
os.environ.setdefault("WORKER_NUMBERS", "96588888888:1")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")

import app  # noqa: E402
import workers  # noqa: E402
from booking import now_kw  # noqa: E402

CAR = [{"vehicle": "jeep", "package": "super", "addons": ["trunk"], "description": "Land Cruiser white"}]


def setup_module():
    app.WORKERS.update({"96588888888": 1, "96577777777": 1, "96566666666": 2})
    app.crew.numbers = app.WORKERS


def collect():
    sent = []
    app.SEND = lambda to, text: sent.append((to, text))
    return sent


def test_parse_commands_all_languages():
    assert workers.parse_command("done 12") == ("done", ("12",))
    assert workers.parse_command("हो गया 12") == ("done", ("12",))
    assert workers.parse_command("Late 20")[0] == "late"
    assert workers.parse_command("देरी 20 5") == ("late", ("20", "5"))
    assert workers.parse_command("no show 3")[0] == "noshow"
    assert workers.parse_command("आज")[0] == "schedule"
    assert workers.parse_command("hello") is None


def test_booking_today_notifies_both_crew_of_that_van_only():
    sent = collect()
    later = now_kw() + timedelta(hours=3)
    day = now_kw().date() if later.date() == now_kw().date() and later.hour < 19 else now_kw().date() + timedelta(days=1)
    avail = app.store.availability(day, "حولي", CAR)
    time = [t for t in avail["available_times"]][0]
    hhmm = app.biz.SLOTS[[app.biz.fmt_time(x) for x in app.biz.SLOTS].index(time)]
    out = app.run_tool("96512121212", "create_booking", {
        "name": "Ahmed", "area": "حولي", "date": day.isoformat(), "time": hhmm, "cars": CAR,
        "notes": "سرداب", "worker_notes": "Basement, guard allows entry"})
    van = out["van"]
    crew_msgs = [(to, t) for to, t in sent if to in app.WORKERS]
    assert {to for to, _ in crew_msgs} == {n for n, v in app.WORKERS.items() if v == van}
    text = crew_msgs[0][1]
    assert "New job" in text and "नया काम" in text and "Basement" in text
    assert "Super Bubbles" in text and "Trunk cleaning" in text and "डिक्की" in text
    assert "20 KD" in text


def test_worker_commands_reply_bilingual_and_send_next():
    sent = collect()
    bid = app.store.day_schedule(now_kw().date()) or app.store.day_schedule(now_kw().date() + timedelta(days=1))
    bid = bid[0]["id"]
    app.handle_message({"from": "96588888888", "id": "w-done", "type": "text", "text": {"body": f"done {bid}"}})
    replies = [t for to, t in sent if to == "96588888888"]
    assert any("काम पूरा" in t for t in replies)
    assert any("तلمع" in t or "تلمع" in t for to, t in sent if to == "96512121212")
    sent.clear()
    app.handle_message({"from": "96588888888", "id": "w-bad", "type": "text", "text": {"body": "مرحبا"}})
    assert "Unknown command" in sent[-1][1]
    app.handle_message({"from": "96588888888", "id": "w-voice", "type": "audio", "audio": {"id": "x"}})
    assert "Commands" in sent[-1][1]  # فويس من العامل ما يروح لموظف العملاء


def test_daily_schedule_sent_once_per_day():
    sent = collect()
    app.store.kv_set("daily_sent", "")
    real_hour = workers.DAILY_HOUR
    workers.DAILY_HOUR = 0
    try:
        app.send_daily_schedules()
        app.send_daily_schedules()
    finally:
        workers.DAILY_HOUR = real_hour
    van1 = [t for to, t in sent if to == "96588888888"]
    assert len(van1) == 1 and "Van 1" in van1[0] and "गाड़ी 1" in van1[0]
    assert any(to == "96566666666" for to, _ in sent)
