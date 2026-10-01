"""Build EN + AR SRT from scene timings (scene start = sum of previous scene durations)."""
import json, re
PAD=0.5; CARD={"S010":5.0,"S107":5.0}
sc=json.load(open('scenes.json')); ar=json.load(open('narration_ar.json'))
import os
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s-int(s))*1000))%1000:03d}"
def chunks(text, maxc):
    sents=re.split(r'(?<=[.?!…"”])\s+', text.strip()); out=[]; cur=""
    for s in sents:
        if len(cur)+len(s)+1<=maxc: cur=(cur+" "+s).strip()
        else:
            if cur: out.append(cur)
            while len(s)>maxc:
                cut=s.rfind(" ",0,maxc); out.append(s[:cut]); s=s[cut+1:]
            cur=s
    if cur: out.append(cur)
    return out
def build(lang, fn, maxc):
    t=0.0; n=1; lines=[]
    for s in sc:
        has=os.path.exists(f"audio/{s['id']}.mp3")
        dur=(s['dur']+PAD) if has else CARD.get(s['id'],4.0)
        text = s['narration'] if lang=='en' else ar.get(s['id'],'')
        if text and has:
            cs=chunks(text,maxc); tot=sum(len(c) for c in cs); st=t
            for c in cs:
                d=s['dur']*len(c)/tot
                lines.append(f"{n}\n{ts(st)} --> {ts(st+d-0.05)}\n{c}\n"); n+=1; st+=d
        t+=dur
    open(fn,'w').write("\n".join(lines))
    return t
total=build('en','../subtitles_en.srt',84); build('ar','../subtitles_ar.srt',70)
print("total",round(total,1),"s =",round(total/60,2),"min")
