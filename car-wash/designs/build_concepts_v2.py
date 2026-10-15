"""3 تصاميم جديدة لباقة ببلز: اسم BIG BUBBLES كبير، واللوقو بالوسط، وكل معلومات التواصل.
المقاس: 1080x1350 (إنستقرام بوست 4:5).
تشغيل: python3 car-wash/designs/build_concepts_v2.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "concepts"
LOGO = "../brand/logo/big-bubbles-logo-4096-transparent.png"
MASCOT = "../brand/mascot/big-bubbles-mascot-transparent.png"
PHONE, IG, TT = "98894114", "@big_bubbless", "TikTok: قريبًا"

FONTS = """
@font-face{font-family:Cairo;font-weight:700;src:url(../fonts/Cairo-700.woff2)}
@font-face{font-family:Cairo;font-weight:900;src:url(../fonts/Cairo-900.woff2)}
*{box-sizing:border-box;margin:0}
html,body{width:1080px;height:1350px;overflow:hidden;font-family:Cairo,'Inter',sans-serif;direction:rtl;position:relative}
:root{--navy:#0B1F4B;--blue:#1E5BD8;--gold:#FFC400;--white:#fff;--green:#25D366}
.big{font-family:Inter,'DejaVu Sans',sans-serif;font-weight:900;letter-spacing:-2px;line-height:.9}
.ltr{direction:ltr;unicode-bidi:isolate}
.ct{position:absolute;left:0;right:0;bottom:0;height:150px;display:flex;justify-content:space-around;align-items:center;padding:0 30px}
.ci{display:flex;align-items:center;gap:12px;font-size:34px;font-weight:900;direction:ltr}
.ci i{width:52px;height:52px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-style:normal;font-size:26px;font-weight:900}
"""

ICONS = lambda c: (f'<span class="ci"><i style="background:{c[0]};color:{c[1]}">{c[2]}</i>{c[3]}</span>')

def contacts(dark):
    fg = "#fff" if dark else "#0B1F4B"
    return (ICONS(("#25D366", "#fff", "✆", PHONE)) +
            ICONS(("#FFC400", "#0B1F4B", "◎", IG)) +
            ICONS(("#fff", "#0B1F4B", "♪", TT)))

D = FONTS + """
body{background:var(--blue)}
.top{position:absolute;top:0;left:0;right:0;height:300px;display:flex;justify-content:center;align-items:center}
.bigname{position:absolute;top:44px;left:0;right:0;text-align:center;color:var(--gold);font-size:150px;text-shadow:0 10px 0 var(--navy)}
.bigname span{color:var(--white)}
.logo{position:absolute;top:300px;left:50%;transform:translateX(-50%);width:520px}
.price{position:absolute;bottom:200px;left:60px;right:60px;display:flex;gap:20px}
.pb{flex:1;background:var(--white);color:var(--navy);border-radius:34px;text-align:center;padding:16px 0}
.pb.s{background:var(--navy);color:var(--white)}
.pb small{font-size:30px;font-weight:700;display:block}
.pb strong{font-size:110px;font-weight:900;line-height:1}
.pb em{font-style:normal;font-size:30px;font-weight:700}
.tg{position:absolute;bottom:430px;left:0;right:0;text-align:center;color:var(--white);font-size:34px;font-weight:900}
.ct{background:var(--navy);color:#fff}
"""

E = FONTS + """
body{background:var(--white)}
.side{position:absolute;top:0;bottom:0;left:0;width:260px;background:var(--blue)}
.vert{position:absolute;left:0;top:0;bottom:0;width:260px;display:flex;align-items:center;justify-content:center}
.vert div{transform:rotate(-90deg);white-space:nowrap;color:var(--gold);font-size:150px}
.vert div span{color:var(--white)}
.logo{position:absolute;top:70px;right:50px;width:250px}
.head{position:absolute;top:360px;right:60px;left:300px}
.head h1{font-size:150px;font-weight:900;color:var(--navy);line-height:1}
.head p{font-size:40px;font-weight:700;color:var(--blue);margin-top:14px}
.mascot{position:absolute;left:250px;bottom:250px;width:300px}
.box{position:absolute;right:60px;bottom:260px;width:480px;text-align:center;color:var(--white);background:var(--navy);border-radius:34px;padding:22px}
.box small{font-size:32px;font-weight:700;color:var(--gold);display:block}
.box strong{font-size:140px;font-weight:900;line-height:1}
.box em{font-style:normal;font-size:36px;font-weight:700}
.ct{background:var(--gold);color:var(--navy)}
"""

F = FONTS + """
body{background:linear-gradient(180deg,#0B1F4B 0%,#1E5BD8 100%)}
.card{position:absolute;top:70px;left:70px;right:70px;height:820px;background:var(--white);border-radius:50px;overflow:hidden}
.card .logo{position:absolute;top:30px;left:50%;transform:translateX(-50%);width:440px}
.nm{position:absolute;top:500px;left:0;right:0;text-align:center;color:var(--navy);font-size:132px;font-weight:900}
.nm span{color:var(--blue)}
.pr{position:absolute;top:655px;left:0;right:0;text-align:center}
.pr span{display:inline-block;background:var(--gold);color:var(--navy);font-size:58px;font-weight:900;padding:6px 36px;border-radius:999px;margin:0 8px}
.pr2{position:absolute;top:925px;left:0;right:0;text-align:center;color:var(--white);font-size:44px;font-weight:900}
.mascot{position:absolute;right:20px;bottom:150px;width:320px}
.lg{position:absolute;left:70px;bottom:270px;width:360px;color:var(--white);font-size:44px;font-weight:900;text-align:left;direction:rtl}
.ct{background:var(--navy);color:#fff}
"""

def page(css, body):
    return f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'

def build():
    d = page(D, f'''<div class="bigname big"><span>BIG </span>BUBBLES</div>
<img class="logo" src="{LOGO}">
<div class="tg">غسيل متنقل بالماي · نوصل لك وين ما كنت 🚐</div>
<div class="price"><div class="pb"><small>صالون</small><strong>5</strong><em>د.ك</em></div>
<div class="pb s"><small>جيب</small><strong>6</strong><em>د.ك</em></div></div>
<div class="ct">{contacts(True)}</div>''')
    e = page(E, f'''<div class="vert"><div class="big"><span>BIG</span> BUBBLES</div></div>
<img class="logo" src="{LOGO}">
<div class="head"><h1>ببلز</h1><p>غسيل خارجي + تنظيف داخلي</p></div>
<img class="mascot" src="{MASCOT}">
<div class="box"><small>صالون</small><strong>5</strong><em>د.ك</em></div>
<div class="ct">{contacts(False)}</div>''')
    f = page(F, f'''<div class="card"><img class="logo" src="{LOGO}">
<div class="nm big">BIG <span>BUBBLES</span></div>
<div class="pr"><span>ببلز 5 / 6 د.ك</span></div>
<div class="pr2">الماي معانا · الخدمة عند باب بيتك</div></div>
<img class="mascot" src="{MASCOT}">
<div class="lg">غسيل خارجي + تنظيف داخلي</div>
<div class="ct">{contacts(True)}</div>''')
    return {"D-bigname": d, "E-vertical": e, "F-card": f}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        for name, html in build().items():
            f = OUT / f"bubbles-{name}.html"
            f.write_text(html.replace('src="../brand', 'src="../../brand').replace("url(../fonts", "url(../fonts"), encoding="utf-8")
            pg.goto(f.resolve().as_uri(), wait_until="load"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / f"bubbles-{name}.png"), clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            print("ok", name)
        br.close()

if __name__ == "__main__":
    main()
