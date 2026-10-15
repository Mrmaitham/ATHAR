"""3 تصاميم مختلفة لباقة ببلز فقط، بألوان الشعار (أزرق ملكي، أصفر، أبيض، ولمسة حمرا من السيارة).
تشغيل: python3 car-wash/designs/build_concepts.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "concepts"
LOGO = "../brand/logo/big-bubbles-logo-4096-transparent.png"
MASCOT = "../brand/mascot/big-bubbles-mascot-transparent.png"
DATA = dict(ar="ببلز", en="BUBBLES", s=5, j=6,
            items=["غسيل خارجي", "تنظيف داخلي"],
            note="الغسلة الأساسية، نظيفة وسريعة",
            phone="98894114", ig="@big_bubbless")

FONTS = """
@font-face{font-family:Cairo;font-weight:700;src:url(../fonts/Cairo-700.woff2)}
@font-face{font-family:Cairo;font-weight:900;src:url(../fonts/Cairo-900.woff2)}
*{box-sizing:border-box;margin:0}
html,body{width:1080px;height:1350px;overflow:hidden;font-family:Cairo,'DejaVu Sans',sans-serif;direction:rtl}
:root{--navy:#0B1F4B;--blue:#1E5BD8;--gold:#FFC400;--red:#D7261E;--white:#FFFFFF}
.ltr{direction:ltr;unicode-bidi:isolate}
"""

A = FONTS + """
body{background:var(--blue);position:relative}
.bgc{position:absolute;left:50%;top:400px;width:820px;height:820px;transform:translateX(-50%);border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#ffffff 0,#cfe6ff 45%,#6fb2ff 100%);opacity:.95}
.logo{position:absolute;top:20px;left:50%;transform:translateX(-50%);width:190px}
.name{position:absolute;top:165px;width:100%;text-align:center;color:var(--gold);font-size:130px;font-weight:900;
  text-shadow:0 8px 0 var(--navy)}
.en{position:absolute;top:330px;width:100%;text-align:center;color:var(--white);font-size:38px;font-weight:700;letter-spacing:4px}
.mascot{position:absolute;left:50%;transform:translateX(-50%);top:440px;width:460px}
.prices{position:absolute;top:900px;left:70px;right:70px;display:flex;gap:24px}
.pb{flex:1;text-align:center;border-radius:36px;padding:20px 0;background:var(--navy);color:var(--white);box-shadow:0 10px 0 #05112a}
.pb.j{background:var(--gold);color:var(--navy);box-shadow:0 10px 0 #b38600}
.pb small{font-size:30px;font-weight:700;display:block}
.pb strong{font-size:124px;font-weight:900;line-height:1}
.pb em{font-style:normal;font-size:32px;font-weight:700}
.chips{position:absolute;top:1108px;left:0;right:0;display:flex;justify-content:center;gap:16px;flex-wrap:wrap}
.chip{background:var(--white);color:var(--navy);font-size:34px;font-weight:900;border-radius:999px;padding:10px 26px}
.foot{position:absolute;bottom:0;left:0;right:0;height:96px;background:var(--navy);color:var(--white);display:flex;justify-content:center;align-items:center;gap:40px;font-size:32px;font-weight:700}
.foot b{color:var(--gold);font-size:40px;font-weight:900}
"""

B = FONTS + """
body{background:var(--white)}
.top{position:absolute;top:0;left:0;right:0;height:250px;background:var(--navy);display:flex;align-items:center;justify-content:space-between;padding:0 60px}
.top img{width:190px}
.top .tt{color:var(--gold);font-size:30px;font-weight:700;text-align:left}
.top .tt b{display:block;color:var(--white);font-size:44px;font-weight:900}
.ticket{position:absolute;top:300px;left:60px;right:60px;bottom:140px;border:4px solid var(--navy);border-radius:28px;padding:40px 50px;background:#f4f8ff}
.ticket:before,.ticket:after{content:"";position:absolute;top:50%;width:46px;height:46px;border-radius:50%;background:var(--white);border:4px solid var(--navy);transform:translateY(-50%)}
.ticket:before{left:-27px}.ticket:after{right:-27px}
.name{font-size:140px;font-weight:900;color:var(--navy);line-height:1}
.en{font-size:34px;font-weight:700;color:var(--blue);letter-spacing:3px}
.line{height:4px;background:var(--navy);margin:26px 0 30px;border-radius:4px}
.row{display:flex;justify-content:space-between;align-items:center;font-size:40px;font-weight:700;color:var(--navy);padding:10px 0;border-bottom:2px dashed #9fb3d9}
.row strong{font-size:58px;font-weight:900}
.row.g strong{color:var(--red)}
.inc{margin-top:14px;font-size:36px;font-weight:900;color:var(--navy)}
.inc div{padding:6px 0;font-size:36px;font-weight:700}
.inc div:before{content:"✔";color:var(--blue);margin-left:14px;font-weight:900}
.mascot{position:absolute;left:40px;bottom:150px;width:230px;transform:rotate(-6deg)}
.foot{position:absolute;bottom:0;left:0;right:0;height:120px;background:var(--gold);color:var(--navy);display:flex;justify-content:space-between;align-items:center;padding:0 50px;font-size:34px;font-weight:900}
"""

C = FONTS + """
body{background:var(--navy);color:var(--white)}
.clip{position:absolute;inset:0;overflow:hidden}.wave{position:absolute;left:-200px;right:-200px;height:520px;border-radius:50%}
.w1{top:-260px;background:var(--blue);opacity:.9}
.w2{top:-300px;background:#2f6fe6;opacity:.55;height:600px}
.logo{position:absolute;top:44px;right:50px;width:200px}
.head{position:absolute;top:300px;left:60px;right:60px}
.head .k{display:inline-block;background:var(--gold);color:var(--navy);font-size:34px;font-weight:900;padding:8px 26px;border-radius:999px}
.name{font-size:170px;font-weight:900;line-height:1;margin-top:16px;color:var(--white)}
.name span{color:var(--gold)}
.en{font-size:36px;font-weight:700;color:#9cc3ff;letter-spacing:4px}
.bigp{position:absolute;top:650px;left:60px;right:60px;display:flex;gap:30px}
.bigp div{flex:1;background:rgba(255,255,255,.07);border:3px solid var(--blue);border-radius:30px;padding:24px;text-align:center}
.bigp small{font-size:32px;font-weight:700;color:#9cc3ff;display:block}
.bigp strong{font-size:150px;font-weight:900;color:var(--gold);line-height:1}
.bigp em{font-style:normal;font-size:34px;font-weight:700}
.mascot{position:absolute;left:10px;bottom:110px;width:340px}
.pts{position:absolute;right:60px;bottom:170px;width:460px;text-align:right}
.pts div{font-size:44px;font-weight:900;margin:14px 0}
.pts div:before{content:"💧";margin-left:12px}
.foot{position:absolute;bottom:0;left:0;right:0;height:110px;background:var(--red);display:flex;justify-content:space-between;align-items:center;padding:0 50px;font-size:36px;font-weight:900;color:var(--white)}
.foot b{font-size:46px;color:var(--gold)}
"""

def page(css, body):
    return f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'

def build(d):
    ar, en, s, j = d["ar"], d["en"], d["s"], d["j"]
    phone, ig = d["phone"], d["ig"]
    chips = "".join(f'<span class="chip">{i}</span>' for i in d["items"])
    a = page(A, f'''<div class="bgc"></div>
<img class="logo" src="{LOGO}">
<div class="name">{ar}</div><div class="en">{en}</div>
<img class="mascot" src="{MASCOT}">
<div class="prices"><div class="pb"><small>صالون</small><strong>{s}</strong><em>د.ك</em></div>
<div class="pb j"><small>جيب</small><strong>{j}</strong><em>د.ك</em></div></div>
<div class="chips">{chips}</div>
<div class="foot"><b class="ltr">{phone}</b><span class="ltr">{ig}</span></div>''')
    rows = "".join(f'<div class="inc"><div>{i}</div></div>' for i in d["items"])
    b = page(B, f'''<div class="top"><div class="tt"><b>{ar}</b>{d["note"]}</div><img src="{LOGO}"></div>
<div class="ticket"><div class="name">{ar}</div><div class="en">{en}</div><div class="line"></div>
<div class="row"><span>صالون</span><strong>{s} د.ك</strong></div>
<div class="row g"><span>جيب</span><strong>{j} د.ك</strong></div>
<div class="inc">{rows}</div></div>
<img class="mascot" src="{MASCOT}">
<div class="foot"><span class="ltr">{ig}</span><span class="ltr">{phone}</span></div>''')
    c = page(C, f'''<div class="clip"><div class="wave w2"></div><div class="wave w1"></div></div>
<img class="logo" src="{LOGO}">
<div class="head"><span class="k">نوصل لك وين ما كنت 🚐</span>
<div class="name">{ar}</div><div class="en">{en} · MOBILE WASH</div></div>
<div class="bigp"><div><small>صالون</small><strong>{s}</strong><em>د.ك</em></div>
<div><small>جيب</small><strong>{j}</strong><em>د.ك</em></div></div>
<img class="mascot" src="{MASCOT}">
<div class="pts"><div>الماي معانا</div><div>ما تحتاج توفر شي</div></div>
<div class="foot"><b class="ltr">{phone}</b><span class="ltr">{ig}</span></div>''')
    return {"A-hero": a, "B-ticket": b, "C-splash": c}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        for name, html in build(DATA).items():
            f = OUT / f"bubbles-{name}.html"
            f.write_text(html.replace('src="../brand', 'src="../../brand').replace("url(../fonts", "url(../fonts"), encoding="utf-8")
            pg.goto(f.resolve().as_uri(), wait_until="load")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / f"bubbles-{name}.png"), clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            print("ok", name)
        br.close()

if __name__ == "__main__":
    main()
