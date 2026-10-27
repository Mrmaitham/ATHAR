"""يبني بوسترات الباقات (1080x1350) من نفس القالب ويصدّرها PNG.
الأسعار والأسماء من هنا فقط (مطابقة لـ business.py)؛ أي تغيير سعر لازم ينعكس هنا وفي الكود.
تشغيل: python3 car-wash/designs/build_posters.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
OUT = HERE / "posters"
LOGO = Path("../brand/logo/big-bubbles-logo-4096-transparent.png")
MASCOT = Path("../brand/mascot/big-bubbles-mascot-transparent.png")
PHONE = "98894114"
IG = "@big_bubbless"

# (ملف، اسم عربي، اسم إنجليزي، صالون، جيب، الخدمات، الجديد بالباقة، ملاحظة)
PACKAGES = [
    ("1-bubbles", "ببلز", "BUBBLES", 6, 7,
     ["غسيل خارجي", "تنظيف داخلي"], [],
     "الأساسية، لمن يبي غسيل نظيف وسريع"),
    ("2-double", "دبل ببلز", "DOUBLE BUBBLES", 9, 10,
     ["غسيل خارجي مع طبقة واكس", "تنظيف داخلي", "تلميع التابلوه", "تلميع الإطارات والرنقات"],
     ["طبقة واكس", "تلميع التابلوه", "تلميع الإطارات والرنقات"],
     "الخيار الأوسط، ينظف ويلمّع أكثر"),
    ("3-super", "سوبر ببلز", "SUPER BUBBLES", 15, 20,
     ["غسيل خارجي مع واكس", "تلميع داخلي كامل", "تلميع الأبواب والأرضيات", "تلميع ربلات السيارة"],
     ["تلميع داخلي كامل", "تلميع الأبواب والأرضيات", "تلميع ربلات السيارة"],
     "تلميع داخلي كامل من الداخل والخارج"),
    ("4-super-top", "سوبر توب ببلز", "SUPER TOP BUBBLES", 20, 25,
     ["كل سوبر ببلز", "غسيل الكشنات", "تنظيف فتحات التكييف", "🎁 معطر وكلينكس هدية"],
     ["غسيل الكشنات", "تنظيف فتحات التكييف", "🎁 معطر وكلينكس هدية"],
     "أكمل باقة للغسيل الشامل"),
]

CSS = """
@font-face{font-family:Cairo;font-weight:700;src:url(../fonts/Cairo-700.woff2)}
@font-face{font-family:Cairo;font-weight:900;src:url(../fonts/Cairo-900.woff2)}
*{box-sizing:border-box;margin:0}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:Cairo,'DejaVu Sans',sans-serif;direction:rtl;color:#0B1F4B;
  background:radial-gradient(circle at 80% 15%,#e6f2ff 0,#ffffff 55%),#fff;position:relative}
.band{position:absolute;inset:0 0 auto 0;height:330px;background:linear-gradient(135deg,#0B1F4B,#1E5BD8);border-radius:0 0 60px 60px}
.logo{position:absolute;top:28px;right:44px;width:200px}
.brand{position:absolute;top:58px;left:48px;color:#fff;text-align:left}
.brand b{display:block;font-size:44px;font-weight:900;color:#FFC400;line-height:1}
.brand span{font-size:26px;font-weight:700;opacity:.95;display:block}.brand em{display:block;font-style:normal;font-size:24px;color:#FFC400;margin-top:6px}
.title{position:absolute;top:350px;right:60px;left:60px;text-align:right}
.name{font-size:104px;font-weight:900;line-height:1.05;color:#0B1F4B}
.en{font-size:34px;font-weight:700;color:#1E5BD8;letter-spacing:2px;margin-top:6px}
.note{font-size:30px;font-weight:700;color:#4b5563;margin-top:10px}
.prices{position:absolute;top:640px;right:60px;left:60px;display:flex;gap:22px}
.pbox{flex:1;border-radius:28px;padding:14px 20px;background:#0B1F4B;color:#fff;text-align:center}
.pbox.j{background:#FFC400;color:#0B1F4B}
.pbox small{display:block;font-size:28px;font-weight:700;opacity:.9}
.pbox strong{display:block;font-size:84px;font-weight:900;line-height:1.05}
.pbox em{font-style:normal;font-size:30px;font-weight:700}
.list{position:absolute;top:860px;right:60px;left:400px;text-align:right}
.li{font-size:30px;font-weight:700;padding:8px 0;border-bottom:2px dashed #cfd8ea;display:flex;justify-content:space-between;align-items:center;gap:12px}
.new{font-size:22px;font-weight:900;background:#FFC400;color:#0B1F4B;border-radius:999px;padding:4px 14px;white-space:nowrap}
.mascot{position:absolute;left:-20px;bottom:120px;width:340px}
.foot{position:absolute;bottom:0;left:0;right:0;height:112px;background:#0B1F4B;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 44px;font-size:30px;font-weight:700}
.foot .ph{color:#FFC400;font-size:40px;font-weight:900;direction:ltr}
.tag{position:absolute;bottom:126px;right:60px;font-size:30px;font-weight:900;color:#1E5BD8}
"""

def html(p):
    key, ar, en, s, j, items, new, note = p
    rows = "".join(
        f'<div class="li"><span>{i}</span>{"<span class=new>جديد</span>" if i in new else ""}</div>'
        for i in items)
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
<div class="band"></div>
<img class="logo" src="{LOGO}" alt="Big Bubbles">
<div class="brand"><b>Big Bubbles</b><span>غسيل متنقل بالماي</span><em>نوصل لك وين ما كنت 🚐</em></div>
<div class="title"><div class="name">{ar}</div><div class="en">{en}</div><div class="note">{note}</div></div>
<div class="prices">
  <div class="pbox"><small>صالون</small><strong>{s}</strong><em>د.ك</em></div>
  <div class="pbox j"><small>جيب</small><strong>{j}</strong><em>د.ك</em></div>
</div>
<div class="list">{rows}</div>
<img class="mascot" src="{MASCOT}" alt="الفقاعة الكبيرة">
<div class="foot"><span class="ph">{PHONE}</span><span dir="ltr">{IG}</span></div>
</body></html>"""

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for p in PACKAGES:
            src = HERE / "posters" / f"{p[0]}.html"
            src.write_text(html(p).replace('src="../brand', 'src="../../brand').replace("url(../fonts", "url(../fonts"), encoding="utf-8")
            pg.goto(src.resolve().as_uri(), wait_until="load")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / f"{p[0]}.png"), clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            print("ok", p[0])
        b.close()

if __name__ == "__main__":
    main()
