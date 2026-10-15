"""محرك الحجوزات: المواعيد، الزونات، المناطق البعيدة، الإلغاء والعدّاد.

كل الحسابات هنا (مو عند Claude) عشان المواعيد والأسعار تكون دقيقة دايمًا.
"""

import json
import sqlite3
import threading
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import business as biz

KW = ZoneInfo("Asia/Kuwait")


def now_kw() -> datetime:
    return datetime.now(KW)


def slot_start(day: date, slot_index: int) -> datetime:
    h, m = map(int, biz.SLOTS[slot_index].split(":"))
    return datetime(day.year, day.month, day.day, h, m, tzinfo=KW)


def parse_date(text: str, today: date | None = None) -> date:
    today = today or now_kw().date()
    t = text.strip()
    if t in ("اليوم", "today"):
        return today
    if t in ("بكرة", "باجر", "بكره", "tomorrow"):
        return today + timedelta(days=1)
    if "/" in t:
        parts = [int(p) for p in t.split("/")]
        d, m = parts[0], parts[1]
        y = parts[2] if len(parts) > 2 else today.year
        result = date(y if y > 100 else 2000 + y, m, d)
        if len(parts) == 2 and result < today:
            result = date(result.year + 1, m, d)
        return result
    return date.fromisoformat(t)


def parse_slot(text: str) -> int:
    t = text.strip().replace("٫", ":").replace(".", ":")
    if ":" not in t:
        t += ":00"
    h, m = map(int, t.split(":")[:2])
    for i, s in enumerate(biz.SLOTS):
        sh, sm = map(int, s.split(":"))
        if (sh, sm) == (h, m) or (sh - 12, sm) == (h, m):  # "1:30" = 13:30
            return i
    raise ValueError(f"الوقت {text} مو من المواعيد المتاحة")


class BookingError(ValueError):
    pass


class Store:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY, phone TEXT, name TEXT, area TEXT, zone INTEGER,
                van INTEGER, day TEXT, slot INTEGER, slots INTEGER, cars TEXT,
                total REAL, location TEXT, notes TEXT,
                status TEXT,            -- confirmed / pending_payment / done / cancelled /
                                        -- late_cancel / no_show / cancelled_by_us
                reminder_sent INTEGER DEFAULT 0, created_at TEXT);
            CREATE TABLE IF NOT EXISTS far_days (
                id INTEGER PRIMARY KEY, day TEXT, van INTEGER, areas TEXT);
            CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT);
            CREATE TABLE IF NOT EXISTS waitlist (
                id INTEGER PRIMARY KEY, phone TEXT, name TEXT, area TEXT, cars TEXT,
                preferred TEXT, created_at TEXT, notified INTEGER DEFAULT 0);
            """
        )
        cols = {r[1] for r in self.db.execute("PRAGMA table_info(bookings)")}
        if "worker_notes" not in cols:  # ترقية قاعدة بيانات قديمة
            self.db.execute("ALTER TABLE bookings ADD COLUMN worker_notes TEXT DEFAULT ''")
            self.db.commit()

    def kv_get(self, k: str) -> str | None:
        row = self.db.execute("SELECT v FROM kv WHERE k = ?", (k,)).fetchone()
        return row[0] if row else None

    def kv_set(self, k: str, v: str) -> None:
        self.db.execute("INSERT OR REPLACE INTO kv VALUES (?, ?)", (k, v))
        self.db.commit()

    # ------------------------------------------------------------ قراءة

    ACTIVE = ("confirmed", "pending_payment", "done")

    def _day_bookings(self, day: date, van: int | None = None) -> list[sqlite3.Row]:
        q = f"SELECT * FROM bookings WHERE day = ? AND status IN {self.ACTIVE}"
        args: list = [day.isoformat()]
        if van is not None:
            q += " AND van = ?"
            args.append(van)
        return self.db.execute(q + " ORDER BY id", args).fetchall()

    def far_day(self, day: date, van: int | None = None, area: str | None = None):
        rows = self.db.execute("SELECT * FROM far_days WHERE day = ?", (day.isoformat(),)).fetchall()
        for r in rows:
            areas = json.loads(r["areas"])
            if van is not None and r["van"] != van:
                continue
            if area is not None and biz.normalize(area) not in {biz.normalize(a) for a in areas}:
                continue
            return r
        return None

    def strikes(self, phone: str) -> int:
        return self.db.execute(
            "SELECT COUNT(*) FROM bookings WHERE phone = ? AND status IN ('late_cancel', 'no_show')",
            (phone,)).fetchone()[0]

    def get(self, booking_id: int):
        return self.db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()

    def upcoming_for(self, phone: str, now: datetime | None = None) -> list[dict]:
        now = now or now_kw()
        rows = self.db.execute(
            "SELECT * FROM bookings WHERE phone = ? AND status IN ('confirmed','pending_payment') "
            "AND day >= ? ORDER BY day, slot", (phone, now.date().isoformat())).fetchall()
        return [self.describe(r) for r in rows if slot_start(date.fromisoformat(r["day"]), r["slot"]) > now]

    def describe(self, r) -> dict:
        d = date.fromisoformat(r["day"])
        return {"booking_id": r["id"], "date": r["day"], "weekday": WEEKDAYS[d.weekday()],
                "time": biz.fmt_time(biz.SLOTS[r["slot"]]), "area": r["area"], "status": r["status"],
                "total": biz.fmt_kd(r["total"]), "cars": json.loads(r["cars"])}

    # ------------------------------------------------------------ التوفر

    def _free_starts(self, day: date, van: int, n: int, now: datetime) -> list[int]:
        taken: set[int] = set()
        for b in self._day_bookings(day, van):
            taken.update(range(b["slot"], b["slot"] + b["slots"]))
        earliest = now + timedelta(minutes=biz.MIN_LEAD_MINUTES)
        starts = []
        for i in range(len(biz.SLOTS) - n + 1):
            if any(j in taken for j in range(i, i + n)):
                continue
            if slot_start(day, i) < earliest:
                continue
            starts.append(i)
        return starts

    def _van_zone(self, day: date, van: int) -> int | None:
        for b in self._day_bookings(day, van):
            if b["zone"]:  # الحجز اليدوي بمنطقة غير معروفة ما يحدد الزون
                return b["zone"]
        return None

    def candidate_vans(self, day: date, zone: int, area: str) -> list[int]:
        """السيارات اللي تقدر تخدم المنطقة هاليوم — المفتوحة على زون قريب أولًا."""
        if zone == biz.FAR_ZONE:
            fd = self.far_day(day, area=area)
            return [fd["van"]] if fd else []
        matching, empty = [], []
        for van in biz.VANS:
            if self.far_day(day, van=van):
                continue  # السيارة محجوزة ليوم منطقة بعيدة
            vz = self._van_zone(day, van)
            if vz is None:
                empty.append(van)
            elif vz != biz.FAR_ZONE and biz.zones_compatible(vz, zone):
                matching.append(van)
        return matching + empty

    def availability(self, day: date, area: str, cars: list[dict], now: datetime | None = None) -> dict:
        now = now or now_kw()
        found = biz.find_area(area)
        if "zone" not in found:
            return {"ok": False, "reason": "unknown_area", "suggestions": found["suggestions"]}
        if len(cars) > biz.MAX_CARS_PER_BOOKING:
            return {"ok": False, "reason": "too_many_cars_handoff"}
        n = biz.slots_needed(cars)
        if day < now.date():
            return {"ok": False, "reason": "date_in_past"}
        result = {"area": found["area"], "zone": found["zone"],
                  "far_zone": found["zone"] == biz.FAR_ZONE, "slots_needed": n,
                  "price": biz.quote(cars)}
        times: dict[int, int] = {}
        for van in self.candidate_vans(day, found["zone"], found["area"]):
            for s in self._free_starts(day, van, n, now):
                times.setdefault(s, van)
        result["ok"] = True
        result["available_times"] = [biz.fmt_time(biz.SLOTS[s]) for s in sorted(times)]
        result["_slot_van"] = times
        if result["far_zone"] and not self.far_day(day, area=found["area"]):
            result["far_day_announced"] = False
            result["upcoming_far_days"] = self.upcoming_far_days(found["area"], now)
        return result

    def upcoming_far_days(self, area: str, now: datetime | None = None) -> list[str]:
        now = now or now_kw()
        rows = self.db.execute("SELECT * FROM far_days WHERE day >= ? ORDER BY day",
                               (now.date().isoformat(),)).fetchall()
        out = []
        for r in rows:
            if biz.normalize(area) in {biz.normalize(a) for a in json.loads(r["areas"])}:
                d = date.fromisoformat(r["day"])
                out.append(f"{WEEKDAYS[d.weekday()]} {r['day']}")
        return out

    # ------------------------------------------------------------ الحجز

    def create(self, phone: str, name: str, area: str, day: date, time_text: str, cars: list[dict],
               location: str = "", notes: str = "", now: datetime | None = None,
               worker_notes: str = "") -> dict:
        now = now or now_kw()
        with self.lock:
            avail = self.availability(day, area, cars, now)
            if not avail["ok"]:
                raise BookingError(avail["reason"])
            slot = parse_slot(time_text)
            van = avail["_slot_van"].get(slot)
            if van is None:
                raise BookingError("slot_not_available")
            prepay = self.strikes(phone) >= biz.STRIKES_FOR_PREPAY
            status = "pending_payment" if prepay else "confirmed"
            cur = self.db.execute(
                "INSERT INTO bookings (phone, name, area, zone, van, day, slot, slots, cars, total, "
                "location, notes, status, created_at, worker_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (phone, name, avail["area"], avail["zone"], van, day.isoformat(), slot,
                 avail["slots_needed"], json.dumps(cars, ensure_ascii=False), avail["price"]["total"],
                 location, notes, status, now.isoformat(), worker_notes))
            self.db.commit()
            out = self.describe(self.get(cur.lastrowid))
            out.update(van=van, prepay_required=prepay, price=avail["price"])
            return out

    def cancel(self, booking_id: int, phone: str, now: datetime | None = None) -> dict:
        now = now or now_kw()
        with self.lock:
            r = self.get(booking_id)
            if not r or r["phone"] != phone or r["status"] not in ("confirmed", "pending_payment"):
                raise BookingError("booking_not_found")
            start = slot_start(date.fromisoformat(r["day"]), r["slot"])
            late = start - now < timedelta(hours=biz.FREE_CANCEL_HOURS)
            status = "late_cancel" if late else "cancelled"
            self.db.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
            self.db.commit()
            strikes = self.strikes(phone)
            return {"booking_id": booking_id, "late": late, "strikes": strikes,
                    "next_booking_prepaid": strikes >= biz.STRIKES_FOR_PREPAY}

    def add_addons(self, booking_id: int, phone: str, addons: list[str],
                   car_numbers: list[int] | None = None, now: datetime | None = None) -> dict:
        """يضيف معطر/كلينكس لحجز قائم (ما يغير الموعد) ويعيد حساب الإجمالي."""
        now = now or now_kw()
        with self.lock:
            r = self.get(booking_id)
            if not r or r["phone"] != phone or r["status"] not in ("confirmed", "pending_payment") \
                    or slot_start(date.fromisoformat(r["day"]), r["slot"]) <= now:
                raise BookingError("booking_not_found")
            cars = json.loads(r["cars"])
            targets = car_numbers or list(range(1, len(cars) + 1))
            for i in targets:
                if not 1 <= i <= len(cars):
                    raise BookingError("bad_car_number")
                car = cars[i - 1]
                car["addons"] = list(dict.fromkeys((car.get("addons") or []) + list(addons)))
            price = biz.quote(cars)
            self.db.execute("UPDATE bookings SET cars = ?, total = ? WHERE id = ?",
                            (json.dumps(cars, ensure_ascii=False), price["total"], booking_id))
            self.db.commit()
            out = self.describe(self.get(booking_id))
            out["price"] = price
            return out

    def reschedule(self, booking_id: int, phone: str, new_day: date, new_time: str,
                   now: datetime | None = None) -> dict:
        with self.lock:
            r = self.get(booking_id)
            if not r or r["phone"] != phone or r["status"] not in ("confirmed", "pending_payment"):
                raise BookingError("booking_not_found")
            cars = json.loads(r["cars"])
            # نتأكد إن الموعد الجديد متاح قبل لا نلغي القديم
            self.db.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
            try:
                new = self.create(phone, r["name"], r["area"], new_day, new_time, cars,
                                  r["location"], r["notes"], now, r["worker_notes"])
            except (BookingError, ValueError):
                self.db.execute("UPDATE bookings SET status = ? WHERE id = ?", (r["status"], booking_id))
                self.db.commit()
                raise
            # التأجيل المتأخر ينحسب مثل الإلغاء المتأخر
            now = now or now_kw()
            late = slot_start(date.fromisoformat(r["day"]), r["slot"]) - now < timedelta(
                hours=biz.FREE_CANCEL_HOURS)
            if late:
                self.db.execute("UPDATE bookings SET status = 'late_cancel' WHERE id = ?", (booking_id,))
            self.db.commit()
            new["late_reschedule"] = late
            return new

    def set_status(self, booking_id: int, status: str) -> sqlite3.Row:
        with self.lock:
            if not self.get(booking_id):
                raise BookingError("booking_not_found")
            self.db.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
            self.db.commit()
            return self.get(booking_id)

    def manual_block(self, day: date, time_text: str, van: int, area: str, note: str = "") -> int:
        """حجز من برا الواتساب (اتصال/انستقرام) — يحجز الموعد عشان ما يصير تعارض."""
        with self.lock:
            slot = parse_slot(time_text)
            taken = {s for b in self._day_bookings(day, van) for s in range(b["slot"], b["slot"] + b["slots"])}
            if slot in taken:
                raise BookingError("slot_not_available")
            found = biz.find_area(area)
            cur = self.db.execute(
                "INSERT INTO bookings (phone, name, area, zone, van, day, slot, slots, cars, total, "
                "location, notes, status, created_at) VALUES ('manual','حجز يدوي',?,?,?,?,?,1,'[]',0,'',?,"
                "'confirmed',?)",
                (found.get("area", area), found.get("zone", 0), van, day.isoformat(), slot, note,
                 now_kw().isoformat()))
            self.db.commit()
            return cur.lastrowid

    def cancel_van_day(self, van: int, day: date) -> list[sqlite3.Row]:
        with self.lock:
            rows = [r for r in self._day_bookings(day, van) if r["status"] != "done"]
            for r in rows:
                self.db.execute("UPDATE bookings SET status = 'cancelled_by_us' WHERE id = ?", (r["id"],))
            self.db.commit()
            return rows

    def next_for_van(self, van: int, now: datetime | None = None):
        now = now or now_kw()
        for r in self.db.execute(
                "SELECT * FROM bookings WHERE van = ? AND day = ? AND status = 'confirmed' ORDER BY slot",
                (van, now.date().isoformat())):
            if slot_start(now.date(), r["slot"]) + timedelta(minutes=30) >= now:
                return r
        return None

    def day_schedule(self, day: date) -> list[sqlite3.Row]:
        return self.db.execute(
            "SELECT * FROM bookings WHERE day = ? AND status IN ('confirmed','pending_payment','done') "
            "ORDER BY van, slot", (day.isoformat(),)).fetchall()

    # ------------------------------------------------------------ المناطق البعيدة

    def announce_far_day(self, day: date, van: int, areas: list[str]) -> list[sqlite3.Row]:
        with self.lock:
            if self._day_bookings(day, van):
                raise BookingError("van_has_bookings")
            names = []
            for a in areas:
                found = biz.find_area(a)
                if found.get("zone") != biz.FAR_ZONE:
                    raise BookingError(f"not_far_area:{a}")
                names.append(found["area"])
            self.db.execute("INSERT INTO far_days (day, van, areas) VALUES (?,?,?)",
                            (day.isoformat(), van, json.dumps(names, ensure_ascii=False)))
            keys = {biz.normalize(n) for n in names}
            waiting = [w for w in self.db.execute("SELECT * FROM waitlist WHERE notified = 0")
                       if biz.normalize(w["area"]) in keys]
            for w in waiting:
                self.db.execute("UPDATE waitlist SET notified = 1 WHERE id = ?", (w["id"],))
            self.db.commit()
            return waiting

    def join_waitlist(self, phone: str, name: str, area: str, cars: list[dict], preferred: str) -> dict:
        found = biz.find_area(area)
        if found.get("zone") != biz.FAR_ZONE:
            raise BookingError("not_far_area")
        with self.lock:
            self.db.execute(
                "INSERT INTO waitlist (phone, name, area, cars, preferred, created_at) VALUES (?,?,?,?,?,?)",
                (phone, name, found["area"], json.dumps(cars, ensure_ascii=False), preferred,
                 now_kw().isoformat()))
            self.db.commit()
            count = self.db.execute("SELECT COUNT(*) FROM waitlist WHERE area = ? AND notified = 0",
                                    (found["area"],)).fetchone()[0]
        return {"area": found["area"], "waiting_in_area": count}

    def waitlist_summary(self) -> list[tuple[str, int]]:
        return self.db.execute("SELECT area, COUNT(*) FROM waitlist WHERE notified = 0 "
                               "GROUP BY area ORDER BY 2 DESC").fetchall()

    # ------------------------------------------------------------ التذكير

    def due_reminders(self, now: datetime | None = None) -> list[sqlite3.Row]:
        now = now or now_kw()
        due = []
        for r in self.db.execute("SELECT * FROM bookings WHERE status = 'confirmed' AND reminder_sent = 0 "
                                 "AND phone != 'manual' AND day <= ?",
                                 ((now + timedelta(hours=biz.REMINDER_HOURS)).date().isoformat(),)):
            start = slot_start(date.fromisoformat(r["day"]), r["slot"])
            if now < start <= now + timedelta(hours=biz.REMINDER_HOURS):
                due.append(r)
        return due

    def mark_reminded(self, booking_id: int) -> None:
        self.db.execute("UPDATE bookings SET reminder_sent = 1 WHERE id = ?", (booking_id,))
        self.db.commit()


WEEKDAYS = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
