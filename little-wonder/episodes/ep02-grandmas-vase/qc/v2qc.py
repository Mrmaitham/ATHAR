#!/usr/bin/env python3
"""QC for one v2 shot: python3 qc/v2qc.py <id> <prev_last.png> <raw.mp4> <outdir>
Writes contact sheet + last frame, prints start diff, background drift, Lab light and transcripts."""
import sys, glob, os, subprocess
import numpy as np, cv2
from faster_whisper import WhisperModel

sid, prev, raw, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
fd = os.path.join(out, f'f{sid}')
os.makedirs(fd, exist_ok=True)
for f in glob.glob(fd + '/*.png'):
    os.remove(f)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-vf', 'fps=3,scale=480:-1,tile=4x4', '-frames:v', '1', f'{out}/cs{sid}.png'])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-vsync', '0', f'{fd}/%03d.png'])
fs = sorted(glob.glob(fd + '/*.png'))
A = cv2.resize(cv2.imread(prev), (1280, 720)).astype(float)
print('frames', len(fs))
print('start diff', [round(np.abs(cv2.imread(fs[i]).astype(float) - A).mean(), 1) for i in (0, 1, 3)])
f0 = cv2.imread(fs[0]).astype(float)
print('drift L-top', [round(np.abs(cv2.imread(f).astype(float)[:300, :300] - f0[:300, :300]).mean(), 1) for f in fs[::12]])
print('drift R-top', [round(np.abs(cv2.imread(f).astype(float)[:300, -300:] - f0[:300, -300:]).mean(), 1) for f in fs[::12]])
def lab(img):
    l = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(float)
    return [round(l[..., 0].mean(), 1), round(l[..., 1].mean() - 128, 1), round(l[..., 2].mean() - 128, 1)]
print('lab prev_last', lab(A), 'first', lab(cv2.imread(fs[0])), 'last', lab(cv2.imread(fs[-1])))
cv2.imwrite(f'{out}/{sid}_last.png', cv2.imread(fs[-1]))
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
for vad in (True, False):
    s, _ = m.transcribe(raw, vad_filter=vad)
    print('vad' if vad else 'raw', [(round(x.start, 2), round(x.end, 2), x.text) for x in s])
e = subprocess.run(['ffmpeg', '-nostats', '-i', raw, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
import re
print('LUFS', re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1:], 'peak', re.findall(r'Peak:\s+(-?[\d.]+) dBFS', e)[-1:])
