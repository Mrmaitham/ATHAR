"""3 تصاميم لببلز: خلفيات مولّدة بهيغسفيلد (بدون نص)، والنص والشعار والفقاعة تنركّب بالكود.
تشغيل: python3 car-wash/designs/build_hf.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "concepts"
BG = HERE / "backgrounds"
LOGO = "../brand/logo/big-bubbles-logo-4096-transparent.png"
MASCOT = "../brand/mascot/big-bubbles-mascot-transparent.png"
PHONE, IG = "98894114", "@big_bubbless"

BASE = """
@font-face{font-family:Cairo;font-weight:700;src:url(../fonts/Cairo-700.woff2)}
@font-face{font-family:Cairo;font-weight:900;src:url(../fonts/Cairo-900.woff2)}
*{box-sizing:border-box;margin:0}
html,body{width:1080px;height:1350px;overflow:hidden;font-family:Cairo,'Inter',sans-serif;direction:rtl;position:relative}
body{background-size:cover;background-position:center}
.big{font-family:Inter,'DejaVu Sans',sans-serif;font-weight:900;letter-spacing:-3px;line-height:.85}
.ftr{position:absolute;left:0;right:0;bottom:0;height:120px;display:flex;align-items:center;justify-content:center;gap:50px;font-size:38px;font-weight:900}
.ftr span{direction:ltr;unicode-bidi:isolate}
"""

H1 = BASE + """
body{background-image:url(../backgrounds/bg-A-bubble.png);color:#fff}
.name{position:absolute;top:60px;left:0;right:0;text-align:center;font-size:124px;color:#fff;text-shadow:0 10px 30px rgba(0,0,0,.35)}
.name span{color:#FFC400}
.logo{position:absolute;top:230px;left:50%;transform:translateX(-50%);width:340px;filter:drop-shadow(0 20px 40px rgba(0,0,0,.35))}
.pkg{position:absolute;top:585px;left:0;right:0;text-align:center;font-size:100px;font-weight:900;color:#FFC400}
.sub{position:absolute;top:718px;left:0;right:0;text-align:center;font-size:40px;font-weight:700}
.prices{position:absolute;top:820px;left:70px;right:70px;display:flex;gap:24px}
.pb{flex:1;background:rgba(255,255,255,.95);color:#0B1F4B;border-radius:40px;text-align:center;padding:22px 0}
.pb small{display:block;font-size:34px;font-weight:700}
.pb strong{display:block;font-size:120px;font-weight:900;line-height:1}
.pb em{font-style:normal;font-size:32px;font-weight:700}
.ftr{background:rgba(11,31,75,.92);color:#fff}
.ftr b{color:#FFC400}
"""

H2 = BASE + """
body{background-image:url(../backgrounds/bg-B-waves.png);color:#0B1F4B}
.logo{position:absolute;top:40px;left:50px;width:220px}
.name{position:absolute;top:300px;right:60px;left:60px;text-align:right;font-size:150px;color:#0B1F4B}
.name span{color:#1E5BD8}
.pkg{position:absolute;top:500px;right:60px;font-size:96px;font-weight:900;color:#0B1F4B}
.sub{position:absolute;top:650px;right:60px;font-size:44px;font-weight:700;color:#1E5BD8}
.mascot{position:absolute;left:40px;bottom:170px;width:420px}
.box{position:absolute;right:60px;bottom:170px;width:420px;background:#0B1F4B;color:#fff;border-radius:40px;padding:28px 30px;text-align:center}
.box small{display:block;font-size:34px;font-weight:700;color:#FFC400}
.box strong{display:block;font-size:150px;font-weight:900;line-height:1}
.box em{font-style:normal;font-size:34px;font-weight:700}
.ftr{background:#FFC400;color:#0B1F4B}
"""

H3 = BASE + """
body{background-image:url(../backgrounds/bg-C-night.png);color:#fff}
.logo{position:absolute;top:40px;right:50px;width:200px}
.name{position:absolute;top:260px;left:60px;right:60px;text-align:center;font-size:140px;color:#fff}
.name span{color:#FFC400}
.pkg{position:absolute;top:470px;left:0;right:0;text-align:center;font-size:110px;font-weight:900;color:#FFC400}
.mascot{position:absolute;left:-10px;bottom:140px;width:300px}
.pts{position:absolute;right:50px;bottom:150px;width:480px;text-align:right}
.pts div{font-size:44px;font-weight:900;margin:12px 0}
.pts div:before{content:"💧";margin-left:12px}
.prices{position:absolute;top:700px;left:60px;right:60px;display:flex;gap:24px}
.pb{flex:1;border:4px solid #FFC400;border-radius:40px;text-align:center;padding:20px 0;background:rgba(11,31,75,.6)}
.pb small{display:block;font-size:34px;font-weight:700;color:#cfe3ff}
.pb strong{display:block;font-size:150px;font-weight:900;line-height:1;color:#FFC400}
.pb em{font-style:normal;font-size:32px;font-weight:700}
.ftr{background:#1E5BD8}
"""

def page(css, body):
    return f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'

def ftr():
    return f'<div class="ftr"><b>{PHONE}</b><span>{IG}</span></div>'

def build():
    h1 = page(H1, f'''<div class="name big">BIG <span>BUBBLES</span></div>
<img class="logo" src="{LOGO}">
<div class="pkg">ببلز</div>
<div class="sub">غسيل خارجي + تنظيف داخلي · نوصل لك وين ما كنت</div>
<div class="prices"><div class="pb"><small>صالون</small><strong>5</strong><em>د.ك</em></div>
<div class="pb"><small>جيب</small><strong>6</strong><em>د.ك</em></div></div>
{ftr()}''')
    h2 = page(H2, f'''<img class="logo" src="{LOGO}">
<div class="name big">BIG <span>BUBBLES</span></div>
<div class="pkg">ببلز</div>
<div class="sub">غسيل خارجي + تنظيف داخلي</div>
<img class="mascot" src="{MASCOT}">
<div class="box"><small>صالون</small><strong>5</strong><em>د.ك</em></div>
{ftr()}''')
    h3 = page(H3, f'''<img class="logo" src="{LOGO}">
<div class="name big">BIG <span>BUBBLES</span></div>
<div class="pkg">ببلز</div>
<div class="prices"><div class="pb"><small>صالون</small><strong>5</strong><em>د.ك</em></div>
<div class="pb"><small>جيب</small><strong>6</strong><em>د.ك</em></div></div>
<img class="mascot" src="{MASCOT}">
<div class="pts"><div>الماي معانا</div><div>ما تحتاج توفر شي</div></div>
{ftr()}''')
    return {"H1-bubble": h1, "H2-waves": h2, "H3-night": h3}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        for name, html in build().items():
            f = OUT / f"bubbles-{name}.html"
            f.write_text(html.replace('src="../brand', 'src="../../brand').replace("url(../fonts", "url(../fonts").replace("url(../backgrounds", "url(../backgrounds"), encoding="utf-8")
            pg.goto(f.resolve().as_uri(), wait_until="load"); pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"bubbles-{name}.png"), clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            print("ok", name)
        br.close()

if __name__ == "__main__":
    main()
