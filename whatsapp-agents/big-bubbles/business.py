"""بيانات بيج ببلز الثابتة: الباقات، الأسعار، المواعيد، الزونات.

إعادة التسعير = تعديل PACKAGES / ADDONS هنا فقط (الموظف الآلي يقرأ منها مباشرة).
الزونات تنقرأ من zones.md (المصدر الوحيد للمناطق).
"""

import difflib
import json
import re
from pathlib import Path

BASE = Path(__file__).parent

# ---------------------------------------------------------------- الباقات والأسعار (د.ك)
# light = غسلة قصيرة (30–40 دقيقة) → سيارتين منها تنحجز بموعد واحد
PACKAGES = {
    "bubbles": {"name": "ببلز", "saloon": 6.0, "jeep": 7.0, "light": True,
                "includes": "غسيل خارجي + تنظيف داخلي"},
    "double": {"name": "دبل ببلز", "saloon": 9.0, "jeep": 10.0, "light": False,
               "includes": "غسيل خارجي مع طبقة واكس • تنظيف داخلي • تلميع التابلوه • "
                           "تلميع الإطارات والرنقات"},
    "super": {"name": "سوبر ببلز", "saloon": 15.0, "jeep": 20.0, "light": True,
              "includes": "غسيل خارجي مع طبقة واكس • غسيل داخلي مع تلميع كامل من الداخل • "
                          "تلميع الإطارات والرنقات والأبواب والأرضيات • تلميع جميع ربلات السيارة"},
    "super_top": {"name": "سوبر توب ببلز", "saloon": 20.0, "jeep": 25.0, "light": False,
                  "includes": "غسيل خارجي مع طبقة واكس • غسيل داخلي مع تلميع كامل من الداخل • "
                              "غسيل الكشنات والأبواب والأرضيات • تلميع الإطارات والرنقات والأبواب • "
                              "تلميع ربلات السيارة • تنظيف فتحات التكييف"},
    "special": {"name": "سيشل ببلز", "saloon": 35.0, "jeep": 40.0, "light": False,
                "includes": "بوليش مميز بعد غسيل السيارة بالكامل من الداخل والخارج"},
}
MOTORCYCLE_PRICE = 5.0


VEHICLES = {"saloon": "صالون", "jeep": "جيب", "large": "سيارة كبيرة (بيك أب/جيب كبير/فان/باص)",
            "motorcycle": "دراجة نارية"}

ADDONS = {
    "freshener": {"name": "معطر بيج ببلز", "price": 1.0, "free_with": {"super_top", "special"}},
    "tissues": {"name": "كلينكس بيج ببلز", "price": 0.25, "free_with": {"super_top", "special"}},
    "trunk": {"name": "تنظيف الدبة", "price": 0.5, "free_with": {"super", "super_top", "special"}},
}

# ---------------------------------------------------------------- المواعيد
SLOTS = ["09:00", "10:30", "12:00", "13:30", "15:00", "16:30", "18:00", "19:30"]
VANS = [1, 2]
MAX_CARS_PER_BOOKING = 4          # 5 وفوق → تحويل لميثم
FREE_CANCEL_HOURS = 2
STRIKES_FOR_PREPAY = 2
REMINDER_HOURS = 2
MIN_LEAD_MINUTES = 60             # حجز نفس اليوم: أقرب موعد بعد ساعة على الأقل
DELAY_NOTIFY_MINUTES = 15


def fmt_kd(amount: float) -> str:
    if amount < 1:
        return f"{round(amount * 1000)} فلس"
    if amount == int(amount):
        return f"{int(amount)} د.ك"
    return f"{amount:.3f} د.ك"


def fmt_time(hhmm: str) -> str:
    h, m = map(int, hhmm.split(":"))
    period = "الصبح" if h < 12 else ("الظهر" if h < 15 else ("العصر" if h < 17 else "المسا"))
    return f"{h if h <= 12 else h - 12}:{m:02d} {period}"


# ---------------------------------------------------------------- التسعير

class PricingError(ValueError):
    pass


def car_price(car: dict) -> tuple[float, list[str]]:
    """سعر سيارة وحدة + تفاصيلها. car = {vehicle, package, addons[]}"""
    vehicle = car.get("vehicle")
    if vehicle not in VEHICLES:
        raise PricingError(f"نوع مركبة غير معروف: {vehicle}")
    lines: list[str] = []
    if vehicle == "motorcycle":
        lines.append(f"غسيل دراجة نارية: {fmt_kd(MOTORCYCLE_PRICE)}")
        return MOTORCYCLE_PRICE, lines

    pkg_key = car.get("package")
    if pkg_key not in PACKAGES:
        raise PricingError(f"باقة غير معروفة: {pkg_key}")
    pkg = PACKAGES[pkg_key]
    price = pkg["saloon" if vehicle == "saloon" else "jeep"]
    lines.append(f"{pkg['name']} ({VEHICLES[vehicle]}): {fmt_kd(price)}")
    total = price
    for key in car.get("addons") or []:
        addon = ADDONS.get(key)
        if not addon:
            raise PricingError(f"إضافة غير معروفة: {key}")
        if pkg_key in addon["free_with"]:
            lines.append(f"{addon['name']}: مجاني 🎁")
        else:
            lines.append(f"{addon['name']}: {fmt_kd(addon['price'])}")
            total += addon["price"]
    return round(total, 3), lines


def quote(cars: list[dict]) -> dict:
    total, details = 0.0, []
    for i, car in enumerate(cars, 1):
        price, lines = car_price(car)
        total += price
        prefix = f"سيارة {i}: " if len(cars) > 1 else ""
        details.extend(prefix + line for line in lines)
    return {"total": round(total, 3), "total_text": fmt_kd(round(total, 3)), "details": details}


def is_light(car: dict) -> bool:
    return car.get("vehicle") == "motorcycle" or PACKAGES.get(car.get("package"), {}).get("light", False)


def slots_needed(cars: list[dict]) -> int:
    """سيارتين خفيفات = موعد واحد؛ لو وحدة منهم سوبر توب/سيشل = موعدين متتاليين."""
    if not cars:
        raise PricingError("لازم سيارة وحدة على الأقل")
    ordered = sorted(cars, key=is_light, reverse=True)  # نجمع الخفيفات مع بعض
    slots = 0
    for i in range(0, len(ordered), 2):
        pair = ordered[i:i + 2]
        slots += 1 if len(pair) == 1 or all(is_light(c) for c in pair) else 2
    return slots


# ---------------------------------------------------------------- الزونات

FAR_ZONE = 6


def normalize(text: str) -> str:
    text = re.sub(r"[ً-ْـ]", "", text.strip())   # تشكيل + تطويل
    text = re.sub("[أإآ]", "ا", text).replace("ة", "ه").replace("ى", "ي")
    words = [w[2:] if w.startswith("ال") and len(w) > 3 else w for w in text.split()]
    return " ".join(words)


def load_zones(path: Path = BASE / "zones.md"):
    area_zone: dict[str, int] = {}
    display: dict[str, str] = {}
    adjacent: dict[int, set[int]] = {}
    zone = None
    for line in path.read_text(encoding="utf-8").splitlines():
        header = re.match(r"^## Area (\d)", line)
        if header:
            zone = int(header.group(1))
            continue
        if line.startswith("## "):
            zone = None
            continue
        adj = re.match(r"^- Area (\d) ↔ (.+)$", line)
        if adj:
            adjacent[int(adj.group(1))] = {int(n) for n in re.findall(r"Area (\d)", adj.group(2))}
            continue
        if zone and line.strip() and not line.startswith(("-", ">", "#")):
            for item in re.split(r"[،,()]", line.replace("...", "")):
                name = item.strip()
                if name:
                    area_zone[normalize(name)] = zone
                    display[normalize(name)] = name
    return area_zone, display, adjacent


AREA_ZONE, AREA_DISPLAY, ADJACENT = load_zones()

# الأسماء الإنجليزية: للعمال، وعشان العميل يقدر يكتب المنطقة بالإنجليزي
_EN = json.loads((BASE / "area_names_en.json").read_text(encoding="utf-8"))
AREA_EN = {ar: names[0] for ar, names in _EN.items()}
_EN_INDEX = {re.sub(r"[^a-z]", "", n.lower()): normalize(ar) for ar, names in _EN.items() for n in names}


def area_en(arabic_name: str) -> str:
    return AREA_EN.get(arabic_name, "")


def find_area(name: str) -> dict:
    """يرجع {area, zone} أو {suggestions} لو ما انعرفت المنطقة."""
    key = normalize(name)
    if key in AREA_ZONE:
        return {"area": AREA_DISPLAY[key], "zone": AREA_ZONE[key]}
    latin = re.sub(r"[^a-z]", "", name.lower())
    if latin:
        hit = _EN_INDEX.get(latin) or next(iter(
            [_EN_INDEX[c] for c in difflib.get_close_matches(latin, _EN_INDEX, n=1, cutoff=0.85)]), None)
        if hit:
            return {"area": AREA_DISPLAY[hit], "zone": AREA_ZONE[hit]}
    # خطأ إملائي بسيط (مثل "الجهرا") ينقبل؛ غير كذا نقترح ونخلي العميل يأكد
    sure = difflib.get_close_matches(key, AREA_ZONE.keys(), n=2, cutoff=0.88)
    if len(sure) == 1:
        return {"area": AREA_DISPLAY[sure[0]], "zone": AREA_ZONE[sure[0]]}
    close = difflib.get_close_matches(key, AREA_ZONE.keys(), n=3, cutoff=0.6)
    return {"suggestions": [AREA_DISPLAY[c] for c in close]}


def zones_compatible(van_zone: int, zone: int) -> bool:
    return van_zone == zone or zone in ADJACENT.get(van_zone, set())


def price_table_text() -> str:
    lines = ["| الباقة | تشمل | صالون | جيب / سيارة كبيرة |", "|---|---|---|---|"]
    for p in PACKAGES.values():
        lines.append(f"| {p['name']} | {p['includes']} | {fmt_kd(p['saloon'])} | {fmt_kd(p['jeep'])} |")
    lines.append(f"| دراجة نارية | غسيل | {fmt_kd(MOTORCYCLE_PRICE)} | — |")
    lines.append("\nالإضافات:")
    for a in ADDONS.values():
        free = "، ".join(PACKAGES[k]["name"] for k in PACKAGES if k in a["free_with"])
        lines.append(f"- {a['name']}: {fmt_kd(a['price'])} — مجاني مع: {free}")
    lines.append("\nالمواعيد اليومية: " + " · ".join(fmt_time(s) for s in SLOTS))
    return "\n".join(lines)
