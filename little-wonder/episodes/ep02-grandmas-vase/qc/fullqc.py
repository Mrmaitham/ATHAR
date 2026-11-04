#!/usr/bin/env python3
"""Full-episode QC for EP02 shots 01-60: specs, loudness, dialogue vs script,
cut continuity, lighting drift. Writes qc/FULL_QC.json and qc/FULL_QC.txt."""
import json, os, re, subprocess, sys
import numpy as np, cv2
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ids = sorted([f[4:-4] for f in os.listdir('shots') if re.fullmatch(r'shot\d+[a-z]?\.mp4', f)],
             key=lambda s: (int(re.sub(r'[a-z]', '', s)), s))
ids = [s for s in ids if int(re.sub(r'[a-z]', '', s)) <= 60]

def src(s):
    if s == '44':
        return 'qc/hoor_redo/shot44_v1_raw.mp4'
    g = f'shots_graded/shot{s}.mp4'
    return g if os.path.exists(g) else f'shots/shot{s}.mp4'

# expected dialogue from SCRIPT.md table rows
script = {}
for line in open('SCRIPT.md', encoding='utf-8'):
    m = re.match(r'\|\s*(\d+[a-z]?)\s*\|', line)
    if not m:
        continue
    k = m.group(1).zfill(2) if m.group(1).isdigit() else m.group(1).zfill(3)
    lines = re.findall(r'\*\*([A-Z]+):\*\*\s*"([^"]+)"', line)
    script[k] = lines

def norm(t):
    return re.findall(r"[a-z']+", t.lower().replace('…', ' '))

def probe(p):
    o = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', p],
                                  capture_output=True, text=True).stdout)
    v = [x for x in o['streams'] if x['codec_type'] == 'video'][0]
    a = [x for x in o['streams'] if x['codec_type'] == 'audio']
    return dict(w=v['width'], h=v['height'], fps=v['r_frame_rate'], dur=float(o['format']['duration']),
                audio=bool(a), ar=a[0].get('sample_rate') if a else None)

def loud(p):
    e = subprocess.run(['ffmpeg', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    I = re.findall(r'I:\s+(-?[\d.]+) LUFS', e)
    P = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', e)
    return (float(I[-1]) if I else None, float(P[-1]) if P else None)

def frame(p, last=False):
    args = ['ffmpeg', '-v', 'error']
    if last:
        args += ['-sseof', '-0.15']
    args += ['-i', p, '-frames:v', '1', '-vf', 'scale=320:180', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    b = subprocess.run(args, capture_output=True).stdout
    if len(b) < 320 * 180 * 3:
        return None
    return np.frombuffer(b[:320 * 180 * 3], np.uint8).reshape(180, 320, 3)

def light(f):
    lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(float)
    return dict(L=round(lab[..., 0].mean(), 1), a=round(lab[..., 1].mean() - 128, 1), b=round(lab[..., 2].mean() - 128, 1))

model = WhisperModel('medium.en', device='cpu', compute_type='int8')
rows = []
prev_last = None
for s in ids:
    p = src(s)
    r = dict(id=s, src=p, **probe(p))
    r['lufs'], r['peak'] = loud(p)
    segs, _ = model.transcribe(p, vad_filter=True, word_timestamps=False)
    r['heard'] = ' '.join(x.text.strip() for x in segs)
    segs2, _ = model.transcribe(p, vad_filter=False)
    r['heard_novad'] = ' '.join(x.text.strip() for x in segs2)
    key = s.zfill(2) if s.isdigit() else s.zfill(3)
    exp = script.get(key, [])
    r['expected'] = [f'{a}: {b}' for a, b in exp]
    ew = [w for _, b in exp for w in norm(b)]
    hw = norm(r['heard'])
    r['missing'] = [w for w in ew if w not in hw]
    r['extra'] = [w for w in hw if w not in ew]
    f0, f1 = frame(p), frame(p, last=True)
    r['light_first'] = light(f0) if f0 is not None else None
    r['light_last'] = light(f1) if f1 is not None else None
    r['cut_diff'] = round(float(np.abs(f0.astype(float) - prev_last.astype(float)).mean()), 1) if (prev_last is not None and f0 is not None) else None
    prev_last = f1
    rows.append(r)
    print(s, r['dur'], r['lufs'], r['cut_diff'], '|', r['heard'], '| exp:', r['expected'], flush=True)

json.dump(rows, open('qc/FULL_QC.json', 'w'), ensure_ascii=False, indent=1)
with open('qc/FULL_QC.txt', 'w') as o:
    for r in rows:
        o.write(f"{r['id']:>4} {r['w']}x{r['h']} {r['fps']} {r['dur']:.2f}s audio={r['audio']} LUFS={r['lufs']} peak={r['peak']} cut={r['cut_diff']} light_first={r['light_first']} light_last={r['light_last']}\n")
        o.write(f"     EXP: {r['expected']}\n     HEARD(vad): {r['heard']}\n     HEARD(raw): {r['heard_novad']}\n     MISS: {r['missing']} EXTRA: {r['extra']}\n")
print('done')
