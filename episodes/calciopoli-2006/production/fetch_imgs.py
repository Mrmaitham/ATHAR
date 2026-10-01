import json,sys,subprocess,os,re,concurrent.futures as cf
from PIL import Image, ImageDraw, ImageFont
urls=json.load(open('img_urls.json')) if os.path.exists('img_urls.json') else {}
txt=sys.stdin.read()
pairs=re.findall(r'"index":(\d+),"job_id":"[^"]+","status":"completed","type":"image","model":"[^"]+","result_url":"([^"]+)"',txt)
for i,u in pairs: urls[i]=u
json.dump(urls,open('img_urls.json','w'),indent=0)
def dl(p):
    i,u=p; out=f"images/I{int(i):04d}.png"
    if not os.path.exists(out): subprocess.run(["curl","-sS","-f","-o",out,u])
    return out
with cf.ThreadPoolExecutor(8) as ex: files=list(ex.map(dl,pairs))
if files:
    W,H=480,270; cols=4; rows=(len(files)+cols-1)//cols
    sheet=Image.new("RGB",(cols*W,rows*(H+24)),(15,15,20)); d=ImageDraw.Draw(sheet)
    f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
    for k,(p,fn) in enumerate(zip(pairs,files)):
        im=Image.open(fn).convert("RGB").resize((W,H)); x=(k%cols)*W; y=(k//cols)*(H+24)
        sheet.paste(im,(x,y+24)); d.text((x+6,y+2),f"I{int(p[0]):04d}",fill=(232,163,23),font=f)
    sheet.save(sys.argv[1],quality=80)
print(len(pairs),"fetched; total",len(urls))
