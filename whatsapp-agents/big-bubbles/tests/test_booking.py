from datetime import date, datetime, timedelta

import pytest

import business as biz
from booking import KW, BookingError, Store, now_kw, parse_date, parse_slot

DAY = date(2026, 10, 20)
NOW = datetime(2026, 10, 19, 12, 0, tzinfo=KW)
LIGHT = {"vehicle": "saloon", "package": "bubbles"}
HEAVY = {"vehicle": "jeep", "package": "special"}


@pytest.fixture
def store():
    return Store(":memory:")


def book(store, phone, area, time, cars=None, day=DAY, now=NOW):
    return store.create(phone, "عميل", area, day, time, cars or [LIGHT], now=now)


def test_pricing_addons_and_free_items():
    q = biz.quote([{"vehicle": "saloon", "package": "bubbles", "addons": ["freshener", "tissues", "trunk"]}])
    assert q["total"] == 6.75  # ببلز 5 + معطر 1 + كلينكس 0.25 + دبة 0.5
    q = biz.quote([{"vehicle": "large", "package": "super_top", "addons": ["freshener", "tissues", "trunk"]}])
    assert q["total"] == 25.0  # سعر الجيب، والإضافات مجانية
    assert biz.quote([{"vehicle": "jeep", "package": "super", "addons": ["trunk", "freshener"]}])["total"] == 21.0
    assert biz.quote([{"vehicle": "motorcycle"}])["total"] == 5.0


def test_slots_needed_rules():
    assert biz.slots_needed([LIGHT]) == 1
    assert biz.slots_needed([HEAVY]) == 1
    assert biz.slots_needed([LIGHT, LIGHT]) == 1
    assert biz.slots_needed([LIGHT, HEAVY]) == 2
    assert biz.slots_needed([LIGHT, LIGHT, HEAVY]) == 2


def test_area_lookup_variants():
    assert biz.find_area("السالميه")["zone"] == 2
    assert biz.find_area("جابر العلي")["zone"] == 4
    assert biz.find_area("صباح الاحمد")["zone"] == biz.FAR_ZONE
    assert "suggestions" in biz.find_area("مدينة وهمية")
    assert biz.find_area("الجهرا")["zone"] == biz.FAR_ZONE
    assert biz.find_area("Salmiya") == {"area": "السالمية", "zone": 2}
    assert biz.find_area("salmiyah")["zone"] == 2 and biz.find_area("Fahaheel")["zone"] == 5
    assert biz.find_area("Mangaff")["area"] == "المنقف"          # خطأ إملائي بسيط
    assert biz.area_en("جليب الشيوخ") == "Jleeb Al-Shuyoukh"


def test_parse_helpers():
    assert parse_slot("1:30") == 3 and parse_slot("13:30") == 3 and parse_slot("9") == 0
    with pytest.raises(ValueError):
        parse_slot("8:00")
    assert parse_date("بكرة", DAY) == DAY + timedelta(days=1)
    assert parse_date("20/10", date(2026, 10, 1)) == DAY


def test_zone_clustering(store):
    b1 = book(store, "1", "حولي", "9:00")          # يفتح سيارة على زون 2
    b2 = book(store, "2", "الأحمدي", "9:00")        # زون 5 مو قريب → السيارة الثانية
    assert b1["van"] != b2["van"]
    b3 = book(store, "3", "السالمية", "10:30")      # زون 2 → نفس سيارة حولي
    assert b3["van"] == b1["van"]
    # زون 1 قريب من 2، بس 9:00 مأخوذ بالسيارتين
    avail = store.availability(DAY, "الشامية", [LIGHT], NOW)
    assert "9:00 الصبح" not in avail["available_times"]
    assert "12:00 الظهر" in avail["available_times"]
    # زون 3 مو قريب من 5 ولا... قريب من 2 → متاح على سيارة حولي فقط
    b4 = book(store, "4", "خيطان", "12:00")
    assert b4["van"] == b1["van"]


def test_full_day_and_two_slot_booking(store):
    for i, t in enumerate(["9:00", "10:30", "12:00", "1:30", "3:00", "4:30", "6:00"]):
        book(store, f"a{i}", "حولي", t)
    # 7:30 فاضي بسيارة 1 بس الحجز الثقيل لسيارتين يحتاج موعدين متتاليين
    avail = store.availability(DAY, "حولي", [LIGHT, HEAVY], NOW)
    assert avail["slots_needed"] == 2
    b = book(store, "x", "حولي", "9:00", [LIGHT, HEAVY])
    assert b["van"] == 2


def test_same_day_lead_time(store):
    now = datetime(2026, 10, 20, 10, 0, tzinfo=KW)
    avail = store.availability(DAY, "حولي", [LIGHT], now)
    assert avail["available_times"][0] == "12:00 الظهر"  # 10:30 أقل من ساعة


def test_far_zone_requires_announced_day(store):
    avail = store.availability(DAY, "صباح الأحمد", [LIGHT], NOW)
    assert avail["available_times"] == [] and avail["far_day_announced"] is False
    store.join_waitlist("w1", "عميل", "صباح الاحمد", [LIGHT], "أي يوم")
    waiting = store.announce_far_day(DAY, 2, ["صباح الأحمد", "جنوب صباح الأحمد"])
    assert [w["phone"] for w in waiting] == ["w1"]
    b = book(store, "f1", "جنوب صباح الأحمد", "9:00")
    assert b["van"] == 2
    # سيارة 2 محجوزة لليوم البعيد → حولي تروح لسيارة 1
    assert book(store, "h", "حولي", "9:00")["van"] == 1
    with pytest.raises(BookingError):
        store.announce_far_day(DAY, 1, ["الجهراء"])  # السيارة فيها حجوزات


def test_cancel_strikes_and_prepay(store):
    late_now = datetime(2026, 10, 20, 8, 0, tzinfo=KW)
    b1 = book(store, "p", "حولي", "9:00")
    assert store.cancel(b1["booking_id"], "p", late_now)["late"] is True
    b2 = book(store, "p", "حولي", "10:30")
    store.set_status(b2["booking_id"], "no_show")
    b3 = book(store, "p", "حولي", "12:00")
    assert b3["prepay_required"] is True and b3["status"] == "pending_payment"
    # إلغاء مبكر ما ينحسب
    b4 = book(store, "q", "حولي", "1:30")
    assert store.cancel(b4["booking_id"], "q", NOW)["late"] is False
    assert store.strikes("q") == 0


def test_cancel_only_own_booking(store):
    b = book(store, "owner", "حولي", "9:00")
    with pytest.raises(BookingError):
        store.cancel(b["booking_id"], "someone-else", NOW)


def test_reschedule_keeps_old_if_new_unavailable(store):
    b = book(store, "r", "حولي", "9:00")
    book(store, "o1", "حولي", "10:30")
    book(store, "o2", "حولي", "10:30")
    with pytest.raises(BookingError):
        store.reschedule(b["booking_id"], "r", DAY, "10:30", NOW)
    assert store.get(b["booking_id"])["status"] == "confirmed"
    new = store.reschedule(b["booking_id"], "r", DAY, "12:00", NOW)
    assert new["time"] == "12:00 الظهر" and store.get(b["booking_id"])["status"] == "cancelled"


def test_manual_block_prevents_double_booking(store):
    store.manual_block(DAY, "9:00", 1, "حولي")
    store.manual_block(DAY, "9:00", 2, "الأحمدي")
    assert "9:00 الصبح" not in store.availability(DAY, "حولي", [LIGHT], NOW)["available_times"]


def test_reminders_window(store):
    b = book(store, "rem", "حولي", "12:00")
    assert store.due_reminders(datetime(2026, 10, 20, 9, 0, tzinfo=KW)) == []
    due = store.due_reminders(datetime(2026, 10, 20, 10, 5, tzinfo=KW))
    assert [r["id"] for r in due] == [b["booking_id"]]
    store.mark_reminded(b["booking_id"])
    assert store.due_reminders(datetime(2026, 10, 20, 10, 5, tzinfo=KW)) == []


def test_too_many_cars(store):
    assert store.availability(DAY, "حولي", [LIGHT] * 5, NOW)["reason"] == "too_many_cars_handoff"


def test_add_addons_after_booking(store):
    day = now_kw().date() + timedelta(days=1)
    cars = [{"vehicle": "jeep", "package": "super"}, {"vehicle": "saloon", "package": "super_top"}]
    b = store.create("965500", "علي", "السالمية", day, "10:30", cars)
    out = store.add_addons(b["booking_id"], "965500", ["freshener", "tissues"], [1])
    assert out["price"]["total"] == 20 + 1 + 0.25 + 20
    out = store.add_addons(b["booking_id"], "965500", ["freshener"])          # مكرر + هدية للسيارة 2
    assert out["price"]["total"] == 41.25
    with pytest.raises(BookingError):
        store.add_addons(b["booking_id"], "965999", ["freshener"])            # مو حجزه


def test_double_bubbles_price_and_slot():
    assert biz.quote([{"vehicle": "saloon", "package": "double"}])["total"] == 7
    assert biz.quote([{"vehicle": "jeep", "package": "double"}])["total"] == 9
    assert "دبل ببلز" in biz.price_table_text()
    assert biz.slots_needed([{"vehicle": "saloon", "package": "double"}]) == 1
