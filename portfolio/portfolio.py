#!/usr/bin/env python3
"""محاسب المحفظة: حساب واحد باسم طيبة، والأسهم داخله مقسّمة على خمسة أشخاص.

يقرأ:
  ledger.csv     كل عمليات الشراء والبيع والتعديل لكل شخص
  dividends.csv  التوزيعات النقدية والمنحة (حسب تاريخ الاستحقاق ex_date)

ويطلع REPORT.md: عدد أسهم كل شخص، متوسط تكلفته، ونصيبه من كل توزيعة.

الاستخدام:
  python3 portfolio/portfolio.py            # يطبع التقرير ويكتب REPORT.md
  python3 portfolio/portfolio.py --date 2026-12-31   # الوضع كما كان بتاريخ معيّن
"""
import argparse
import csv
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
PEOPLE = ["ميثم", "طيبة", "نادية", "حور", "محمد"]
ALIASES = {"طيبه": "طيبة", "ناديه": "نادية"}
TRADE_TYPES = {"buy", "sell", "adjust"}
FILS = Decimal("0.001")


class LedgerError(Exception):
    pass


def person_of(raw, where):
    name = ALIASES.get(raw.strip(), raw.strip())
    if name not in PEOPLE:
        raise LedgerError(f"{where}: اسم غير معروف '{raw}' (المسموح: {'، '.join(PEOPLE)})")
    return name


def dec(raw, where, field, default=None):
    raw = (raw or "").strip()
    if not raw:
        if default is None:
            raise LedgerError(f"{where}: الحقل {field} فاضي")
        return Decimal(default)
    try:
        return Decimal(raw)
    except Exception:
        raise LedgerError(f"{where}: قيمة غير صالحة في {field}: '{raw}'")


def day(raw, where):
    try:
        return date.fromisoformat(raw.strip())
    except Exception:
        raise LedgerError(f"{where}: تاريخ غير صالح '{raw}' (الصيغة YYYY-MM-DD)")


def read_csv(name):
    with open(HERE / name, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]


def load_events():
    events = []
    for i, r in enumerate(read_csv("ledger.csv"), start=2):
        where = f"ledger.csv سطر {i}"
        kind = r["type"].strip().lower()
        if kind not in TRADE_TYPES:
            raise LedgerError(f"{where}: نوع غير معروف '{r['type']}' (buy/sell/adjust)")
        qty = dec(r["qty"], where, "qty")
        if kind != "adjust" and qty <= 0:
            raise LedgerError(f"{where}: الكمية لازم تكون موجبة")
        if qty != qty.to_integral_value():
            raise LedgerError(f"{where}: الكمية لازم تكون عدد صحيح")
        events.append({
            "date": day(r["date"], where), "order": 1, "where": where, "kind": kind,
            "person": person_of(r["person"], where), "symbol": r["symbol"].strip().upper(),
            "qty": int(qty),
            "price": dec(r["price_kwd"], where, "price_kwd", "0"),
            "fees": dec(r["fees_kwd"], where, "fees_kwd", "0"),
        })
    for i, r in enumerate(read_csv("dividends.csv"), start=2):
        where = f"dividends.csv سطر {i}"
        kind = r["type"].strip().lower()
        if kind not in {"cash", "bonus"}:
            raise LedgerError(f"{where}: نوع التوزيعة لازم cash أو bonus")
        received = (r.get("total_received") or "").strip()
        events.append({
            # التوزيعة تنحسب قبل عمليات نفس اليوم: اللي يشتري يوم ex_date ما يستحق
            "date": day(r["ex_date"], where), "order": 0, "where": where, "kind": kind,
            "symbol": r["symbol"].strip().upper(),
            "fils": dec(r["fils_per_share"], where, "fils_per_share", "0"),
            "pct": dec(r["bonus_pct"], where, "bonus_pct", "0"),
            "received": int(received) if received else None,
            "note": (r.get("note") or "").strip(),
        })
    events.sort(key=lambda e: (e["date"], e["order"]))
    return events


def split_bonus(holders, pct, received):
    """يوزّع أسهم المنحة اللي استلمها الحساب على الأشخاص بطريقة أكبر باقي،
    عشان مجموع حصصهم يساوي بالضبط اللي نزل في حساب طيبة."""
    total = sum(holders.values())
    exact = {p: Decimal(q) * pct / 100 for p, q in holders.items()}
    if received is None:
        received = int((Decimal(total) * pct / 100).to_integral_value(ROUND_FLOOR))
    base = {p: int(v.to_integral_value(ROUND_FLOOR)) for p, v in exact.items()}
    left = received - sum(base.values())
    if left < 0 or left > len(holders):
        raise LedgerError(
            f"total_received={received} بعيد عن المتوقع ({sum(exact.values()):.2f}) — راجع الرقم")
    by_remainder = sorted(holders, key=lambda p: (-(exact[p] - base[p]), PEOPLE.index(p)))
    for p in by_remainder[:left]:
        base[p] += 1
    return base, exact, received


def run(as_of=None):
    qty = defaultdict(int)             # (person, symbol) -> shares
    cost = defaultdict(Decimal)        # (person, symbol) -> cost basis KWD
    realized = defaultdict(Decimal)    # person -> realized P/L KWD
    cash_divs = defaultdict(Decimal)   # person -> cash dividends KWD
    distributions = []

    for e in load_events():
        if as_of and e["date"] > as_of:
            break
        sym = e["symbol"]
        if e["kind"] in TRADE_TYPES:
            key = (e["person"], sym)
            if e["kind"] == "buy":
                qty[key] += e["qty"]
                cost[key] += e["qty"] * e["price"] + e["fees"]
            elif e["kind"] == "sell":
                if e["qty"] > qty[key]:
                    raise LedgerError(
                        f"{e['where']}: بيع {e['qty']} {sym} من رصيد {e['person']} والموجود بس {qty[key]}")
                avg = cost[key] / qty[key]
                realized[e["person"]] += e["qty"] * e["price"] - e["fees"] - avg * e["qty"]
                cost[key] -= avg * e["qty"]
                qty[key] -= e["qty"]
            else:  # adjust: تصحيح يدوي (تخفيض رأس مال، تحويل...) بدون تغيير التكلفة
                if qty[key] + e["qty"] < 0:
                    raise LedgerError(f"{e['where']}: التعديل يخلي رصيد {e['person']} سالب")
                qty[key] += e["qty"]
                if qty[key] == 0:
                    cost[key] = Decimal(0)
            continue

        holders = {p: qty[(p, sym)] for p in PEOPLE if qty[(p, sym)] > 0}
        if not holders:
            raise LedgerError(f"{e['where']}: ما في أحد يملك {sym} قبل {e['date']}")
        row = {"date": e["date"], "symbol": sym, "kind": e["kind"], "note": e["note"],
               "holders": holders, "shares": {}}
        if e["kind"] == "cash":
            row["fils"] = e["fils"]
            for p, q in holders.items():
                amount = (Decimal(q) * e["fils"] / 1000).quantize(FILS, ROUND_HALF_UP)
                row["shares"][p] = amount
                cash_divs[p] += amount
        else:
            got, exact, received = split_bonus(holders, e["pct"], e["received"])
            row.update(pct=e["pct"], exact=exact, received=received)
            for p, n in got.items():
                row["shares"][p] = n
                qty[(p, sym)] += n
        distributions.append(row)

    return qty, cost, realized, cash_divs, distributions


def kwd(x):
    return f"{Decimal(x).quantize(FILS, ROUND_HALF_UP):,.3f}"


def render(qty, cost, realized, cash_divs, distributions, as_of):
    symbols = sorted({s for (_, s), q in qty.items() if q > 0})
    out = [f"# تقرير المحفظة — حساب طيبة", "",
           f"الوضع بتاريخ: **{as_of or 'آخر عملية مسجلة'}** — الأسعار بالدينار الكويتي.", ""]

    out += ["## عدد الأسهم لكل شخص", ""]
    if symbols:
        out += ["| السهم | " + " | ".join(PEOPLE) + " | **إجمالي الحساب** |",
                "|---|" + "---:|" * (len(PEOPLE) + 1)]
        for s in symbols:
            cells = [f"{qty[(p, s)]:,}" if qty[(p, s)] else "—" for p in PEOPLE]
            total = sum(qty[(p, s)] for p in PEOPLE)
            out.append(f"| {s} | " + " | ".join(cells) + f" | **{total:,}** |")
        out += ["", "> عمود **إجمالي الحساب** لازم يطابق كشف الوسيط لحساب طيبة.", ""]
    else:
        out += ["ما في أسهم مسجلة لحد الحين.", ""]

    out += ["## تفاصيل كل شخص", ""]
    for p in PEOPLE:
        mine = [s for s in symbols if qty[(p, s)] > 0]
        out.append(f"### {p}")
        if not mine:
            out += ["ما في أسهم حاليًا.", ""]
        else:
            out += ["| السهم | العدد | متوسط التكلفة | إجمالي التكلفة |", "|---|---:|---:|---:|"]
            for s in mine:
                k = (p, s)
                out.append(f"| {s} | {qty[k]:,} | {kwd(cost[k] / qty[k])} | {kwd(cost[k])} |")
            out.append("")
        out += [f"- التوزيعات النقدية المستلمة: **{kwd(cash_divs[p])} د.ك**",
                f"- ربح/خسارة محققة من البيع: **{kwd(realized[p])} د.ك**", ""]

    out += ["## التوزيعات", ""]
    if not distributions:
        out += ["ما في توزيعات مسجلة لحد الحين.", ""]
    for d in reversed(distributions):
        if d["kind"] == "cash":
            title = f"### {d['symbol']} — نقدي {d['fils']} فلس للسهم (ex: {d['date']})"
            out += [title, "", "| الشخص | الأسهم المستحقة | النصيب (د.ك) |", "|---|---:|---:|"]
            for p in PEOPLE:
                if p in d["holders"]:
                    out.append(f"| {p} | {d['holders'][p]:,} | {kwd(d['shares'][p])} |")
            out.append(f"| **المجموع** | **{sum(d['holders'].values()):,}** | "
                       f"**{kwd(sum(d['shares'].values()))}** |")
        else:
            title = f"### {d['symbol']} — منحة {d['pct']}% (ex: {d['date']})"
            out += [title, "", "| الشخص | الأسهم المستحقة | الحصة الدقيقة | أسهم المنحة |",
                    "|---|---:|---:|---:|"]
            for p in PEOPLE:
                if p in d["holders"]:
                    out.append(f"| {p} | {d['holders'][p]:,} | {d['exact'][p]:.2f} | "
                               f"{d['shares'][p]:,} |")
            out.append(f"| **المجموع** | **{sum(d['holders'].values()):,}** | "
                       f"**{sum(d['exact'].values()):.2f}** | **{d['received']:,}** |")
        if d["note"]:
            out += ["", f"ملاحظة: {d['note']}"]
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", type=date.fromisoformat, help="احسب الوضع لغاية هذا التاريخ")
    ap.add_argument("--no-write", action="store_true", help="اطبع بس بدون كتابة REPORT.md")
    args = ap.parse_args()
    try:
        report = render(*run(args.date), args.date)
    except LedgerError as err:
        print(f"خطأ: {err}", file=sys.stderr)
        return 1
    print(report)
    if not args.no_write and not args.date:
        (HERE / "REPORT.md").write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
