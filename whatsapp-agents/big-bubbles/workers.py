"""رسائل الفريق الميداني (السواق + العامل) بالإنجليزي والهندي.

- جدول اليوم لكل سيارة غسيل كل صبح.
- تنبيه فوري بأي حجز جديد / إلغاء / تأجيل لليوم أو بكرة.
- أوامر: done / late / noshow / schedule / tomorrow / next (وبالهندي والعربي).
"""

import json
import re
from datetime import date, timedelta

import business as biz
from booking import now_kw

DAILY_HOUR = 8

PKG_EN = {"bubbles": "Bubbles", "super": "Super Bubbles", "super_top": "Super Top Bubbles"}
VEHICLE = {"saloon": ("Sedan", "सेडान"), "jeep": ("Jeep", "जीप"),
           "large": ("Big vehicle", "बड़ी गाड़ी"), "motorcycle": ("Motorcycle", "मोटरसाइकिल")}
ADDON = {"freshener": ("Air freshener", "एयर फ्रेशनर"), "tissues": ("Tissues", "टिशू"),
         "trunk": ("Trunk cleaning", "डिक्की की सफ़ाई")}

HELP = """🫧 Commands | कमांड:
• done 12 — job finished | काम पूरा (हो गया 12)
• late 20 — 20 min late for next job | अगले काम में 20 मिनट देर (देरी 20)
• noshow 12 — customer not there after 10 min | ग्राहक नहीं मिला (नहीं मिला 12)
• schedule — today's jobs | आज का शेड्यूल (आज)
• tomorrow — tomorrow's jobs | कल का शेड्यूल (कल)
• next — next job + location | अगला काम (अगला)"""

# أمر العامل → (نوع الأمر، يحتاج رقم؟)
_COMMANDS = [
    (r"(?:done|finished|हो गया|पूरा|تم)\s*#?(\d+)", "done"),
    (r"(?:late|delay|देरी|देर|تأخير)\s+(\d+)(?:\s+#?(\d+))?", "late"),
    (r"(?:no ?show|नहीं मिला|غياب)\s*#?(\d+)", "noshow"),
    (r"(?:schedule|today|my jobs|आज|शेड्यूल|جدولي|جدول)", "schedule"),
    (r"(?:tomorrow|कल|بكرة)", "tomorrow"),
    (r"(?:next|अगला|الجاي)", "next"),
    (r"(?:help|मदद|مساعدة)", "help"),
]


def parse_command(text: str) -> tuple[str, tuple] | None:
    t = text.strip().lower()
    for pattern, kind in _COMMANDS:
        m = re.fullmatch(pattern, t)
        if m:
            return kind, m.groups()
    return None


def time_en(hhmm: str) -> str:
    h, m = map(int, hhmm.split(":"))
    return f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"


def _cars_lines(cars: list[dict]) -> str:
    lines = []
    for c in cars:
        en, hi = VEHICLE.get(c.get("vehicle"), ("Car", "गाड़ी"))
        pkg = PKG_EN.get(c.get("package"), "") if c.get("vehicle") != "motorcycle" else ""
        extras = [ADDON[a] for a in c.get("addons") or [] if a in ADDON]
        desc = f" ({c['description']})" if c.get("description") else ""
        en_line = " · ".join(x for x in [en + desc, pkg] if x)
        hi_line = " · ".join(x for x in [hi, pkg] if x)
        if extras:
            en_line += " + " + ", ".join(e[0] for e in extras)
            hi_line += " + " + ", ".join(e[1] for e in extras)
        lines.append(f"🚗 {en_line}\n    {hi_line}")
    return "\n".join(lines)


def job_text(r) -> str:
    cars = json.loads(r["cars"])
    out = [f"⏰ *{time_en(biz.SLOTS[r['slot']])}*"
           + (f" → {time_en(biz.SLOTS[r['slot'] + r['slots'] - 1])} (2 slots | 2 स्लॉट)" if r["slots"] > 1 else "")
           + f" — #{r['id']}"]
    en = biz.area_en(r["area"])
    out.append(f"📍 {en + ' | ' if en else ''}{r['area']} (Area {r['zone']})")
    if r["location"]:
        out.append(f"🗺️ {r['location'].split()[0]}")
    if r["phone"] == "manual":
        out.append("📞 Manual booking — ask Maitham | मैनुअल बुकिंग — मैथम से पूछें")
    else:
        out.append(f"👤 {r['name']} — +{r['phone']}")
    if cars:
        out.append(_cars_lines(cars))
    if r["total"]:
        out.append(f"💰 {biz.fmt_kd(r['total']).replace('د.ك', 'KD').replace('فلس', 'fils')} — "
                   "collect after wash (KNET) | धुलाई के बाद पेमेंट लें")
    notes = r["worker_notes"] if "worker_notes" in r.keys() and r["worker_notes"] else ""
    if notes:
        out.append(f"📝 {notes}")
    if r["status"] == "pending_payment":
        out.append("⏳ Waiting prepayment — don't go yet | पेमेंट का इंतज़ार — अभी मत जाइए")
    return "\n".join(out)


def schedule_text(store, van: int, day: date) -> str:
    label = "Today | आज" if day == now_kw().date() else (
        "Tomorrow | कल" if day == now_kw().date() + timedelta(days=1) else day.isoformat())
    rows = [r for r in store.day_schedule(day) if r["van"] == van and r["status"] != "done"]
    head = f"🚐 *Van {van} | गाड़ी {van}* — {label} {day:%d/%m}"
    far = store.far_day(day, van=van)
    if far:
        head += "\n🏜️ Far-area day | दूर के इलाके का दिन: " + ", ".join(
            biz.area_en(a) or a for a in json.loads(far["areas"]))
    if not rows:
        return head + "\nNo jobs | कोई काम नहीं"
    return head + f" — {len(rows)} jobs | काम\n\n" + "\n\n".join(
        f"{i}) " + job_text(r) for i, r in enumerate(rows, 1))


class Crew:
    """يربط أرقام الفريق بسيارات الغسيل ويرسل لهم."""

    def __init__(self, store, numbers: dict[str, int], send):
        self.store, self.numbers, self.send = store, numbers, send

    def members(self, van: int) -> list[str]:
        return [n for n, v in self.numbers.items() if v == van]

    def to_van(self, van: int, text: str) -> None:
        for n in self.members(van):
            self.send(n, text)

    def notify(self, r, event: str) -> None:
        """تنبيه فوري للفريق — بس لحجوزات اليوم وبكرة (الباقي يجي بالجدول الصبح)."""
        day = date.fromisoformat(r["day"])
        today = now_kw().date()
        if day not in (today, today + timedelta(days=1)):
            return
        when = "TODAY | आज" if day == today else "TOMORROW | कल"
        title = {"new": "🆕 New job | नया काम", "cancel": "❌ Cancelled | रद्द",
                 "moved": "🔁 Time changed | समय बदला",
                 "extras": "➕ Extras added | अतिरिक्त सामान जोड़ा"}[event]
        self.to_van(r["van"], f"{title} — {when}\n\n{job_text(r)}")

    def send_next(self, van: int) -> None:
        r = self.store.next_for_van(van)
        if r:
            self.to_van(van, "➡️ Next job | अगला काम\n\n" + job_text(r))
        else:
            self.to_van(van, "✅ No more jobs today | आज और कोई काम नहीं 🫧")

    def daily(self) -> None:
        today = now_kw().date()
        for van in biz.VANS:
            if self.members(van):
                self.to_van(van, schedule_text(self.store, van, today))
