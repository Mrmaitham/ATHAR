"""3 أفكار تيشيرت لعمال Big Bubbles (تصميم الصدر/الظهر، PNG شفاف 2400px)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE
LOGO = "../brand/logo/big-bubbles-logo-4096-transparent.png"
MASCOT = "../brand/mascot/big-bubbles-mascot-transparent.png"
FONTS = """
@font-face{font-family:Cairo;font-weight:900;src:url(../fonts/Cairo-900.woff2)}
*{box-sizing:border-box;margin:0}
html,body{width:1200px;height:1200px;overflow:hidden;background:transparent;font-family:Cairo,'Inter',sans-serif;direction:rtl}
:root{--navy:#0B1F4B;--blue:#1E5BD8;--gold:#FFC400;--white:#fff}
.big{font-family:Inter,'DejaVu Sans',sans-serif;font-weight:900;letter-spacing:-2px}
"""
A = FONTS + """
body{background:#fff;position:relative}
.shirt{position:absolute;inset:0;background:var(--navy);border-radius:60px 60px 40px 40px}
.logo{position:absolute;top:150px;left:150px;width:160px}
.mascot{position:absolute;left:50%;transform:translateX(-50%);top:330px;width:560px}
.name{position:absolute;bottom:170px;left:0;right:0;text-align:center;color:var(--gold);font-size:120px}
.name span{color:var(--white)}
.tag{position:absolute;bottom:90px;left:0;right:0;text-align:center;color:var(--white);font-size:44px;font-weight:900}
"""
B = FONTS + """
body{background:#fff;position:relative}
.shirt{position:absolute;inset:0;background:var(--blue);border-radius:60px 60px 40px 40px}
.wave{position:absolute;left:-40px;right:-40px;bottom:-60px;height:340px;background:var(--navy);border-radius:50% 50% 0 0/100% 100% 0 0;opacity:.9}
.bub{position:absolute;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff 0,rgba(255,255,255,.2) 45%,rgba(255,255,255,.05) 70%);border:3px solid rgba(255,255,255,.6)}
.logo{position:absolute;top:120px;left:50%;transform:translateX(-50%);width:200px}
.name{position:absolute;top:350px;left:0;right:0;text-align:center;color:var(--gold);font-size:150px;text-shadow:0 8px 0 var(--navy)}
.sub{position:absolute;top:530px;left:0;right:0;text-align:center;color:var(--white);font-size:52px;font-weight:900}
.mascot{position:absolute;left:50%;transform:translateX(-50%);bottom:150px;width:420px}
"""
C = FONTS + """
body{background:#fff;position:relative}
.shirt{position:absolute;inset:0;background:#fff;border-radius:60px 60px 40px 40px;border:6px solid var(--navy)}
.band{position:absolute;top:0;left:0;right:0;height:300px;background:var(--navy);border-radius:60px 60px 0 0}
.logo{position:absolute;top:70px;left:50%;transform:translateX(-50%);width:200px}
.big2{position:absolute;top:340px;left:0;right:0;text-align:center;color:var(--navy);font-size:130px;line-height:.95}
.big2 span{color:var(--blue)}
.mascot{position:absolute;left:50%;transform:translateX(-50%);bottom:90px;width:360px}
.bubbles{position:absolute;right:90px;bottom:260px;width:200px;height:200px}
.tag{position:absolute;bottom:40px;left:0;right:0;text-align:center;color:var(--gold);background:var(--navy);font-size:40px;font-weight:900;padding:14px 0;margin:0 40px;border-radius:999px}
"""
def page(css, body): return f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'
def build():
    a = page(A, f'''<div class="shirt"></div>
<img class="logo" src="{LOGO}"><img class="mascot" src="{MASCOT}">
<div class="name big">BIG <span>BUBBLES</span></div><div class="tag">نوصل لك وين ما كنت 🚐</div>''')
    b = page(B, f'''<div class="shirt"></div><div class="wave"></div>
<div class="bub" style="left:120px;top:700px;width:70px;height:70px"></div>
<div class="bub" style="left:960px;top:620px;width:90px;height:90px"></div>
<div class="bub" style="left:880px;top:820px;width:50px;height:50px"></div>
<img class="logo" src="{LOGO}">
<div class="name big">BIG BUBBLES</div><div class="sub">غسيل متنقل بالماي</div>
<img class="mascot" src="{MASCOT}">''')
    c = page(C, f'''<div class="shirt"></div><div class="band"></div>
<img class="logo" src="{LOGO}">
<div class="big2 big">BIG<br><span>BUBBLES</span></div>
<img class="mascot" src="{MASCOT}">
<div class="tag">نوصل لك وين ما كنت 🚐</div>''')
    return {"T1-chest-mascot": a, "T2-blue-wave": b, "T3-white-stack": c}
def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": 1200, "height": 1200})
        for name, html in build().items():
            f = OUT / f"{name}.html"
            f.write_text(html.replace('src="../brand', 'src="../../brand').replace("url(../fonts", "url(../fonts"), encoding="utf-8")
            pg.goto(f.resolve().as_uri(), wait_until="load"); pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"{name}.png"), clip={"x":0,"y":0,"width":1200,"height":1200}, omit_background=True)
            print("ok", name)
        br.close()
if __name__=="__main__": main()
