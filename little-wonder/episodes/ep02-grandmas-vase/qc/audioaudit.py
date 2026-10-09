#!/usr/bin/env python3
# audioaudit.py — every shot: whisper (medium.en) transcript vs SCRIPT.md line → flags extra/missing words
import re,os,sys,json,difflib
from faster_whisper import WhisperModel
rows={}
for l in open('SCRIPT.md'):
    m=re.match(r'^\| *(\d+[a-z]?) *\|',l)
    if not m or m.group(1) in rows: continue
    q=re.findall(r'"([^"]+)"',l); rows[m.group(1)]=' '.join(q)
ids=sorted([f[4:-4] for f in os.listdir('shots') if re.match(r'^shot\d+[a-z]?\.mp4$',f)],key=lambda s:(int(re.match(r'\d+',s).group()),s))
if len(sys.argv)>1: ids=[i for i in ids if i in sys.argv[1:]]
m=WhisperModel('medium.en',compute_type='int8')
norm=lambda s:re.sub(r"[^a-z' ]",' ',s.lower().replace('…',' ').replace('—',' ')).split()
out={}
for n in ids:
    f=f'shots_graded/shot{n}.mp4' if os.path.exists(f'shots_graded/shot{n}.mp4') else f'shots/shot{n}.mp4'
    segs,_=m.transcribe(f,word_timestamps=True,condition_on_previous_text=False,temperature=0,no_speech_threshold=0.3,vad_filter=False)
    words=[(w.word.strip(),round(w.start,2),round(w.probability,2)) for s in segs for w in s.words]
    exp=norm(rows.get(n,'')); got=norm(' '.join(w[0] for w in words))
    sm=difflib.SequenceMatcher(None,exp,got)
    extra=[got[j] for t,i1,i2,j1,j2 in sm.get_opcodes() if t in('insert','replace') for j in range(j1,j2)]
    miss=[exp[i] for t,i1,i2,j1,j2 in sm.get_opcodes() if t in('delete','replace') for i in range(i1,i2)]
    out[n]=dict(expected=rows.get(n,''),heard=words,extra=extra,missing=miss)
    print(f"{n:4s} EXP: {rows.get(n,'')[:70]}\n     GOT: {' '.join(f'{w[0]}@{w[1]}' for w in words)}\n     EXTRA:{extra} MISS:{miss}",flush=True)
json.dump(out,open('qc/audioaudit.json','w'),ensure_ascii=False,indent=1)
