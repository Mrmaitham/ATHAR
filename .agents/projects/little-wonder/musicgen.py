#!/usr/bin/env python3
# usage: musicgen.py STYLE OUT.wav [seconds]   STYLE = uke | piano | pizz | musicbox
# Small procedural composer for Little Wonder underscore: original melodies, synthesized instruments
# (Karplus-Strong plucks, additive mallets/piano, filtered-saw strings), simple stereo reverb.
import sys, numpy as np, wave
SR = 44100
style, out = sys.argv[1], sys.argv[2]; DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 24
rng = np.random.default_rng(7)
def midi(n): return 440*2**((n-69)/12)
NOTE = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def nm(s):  # 'C5', 'F#4', 'Bb3'
    b = NOTE[s[0]]; i = 1
    if s[i] == '#': b += 1; i += 1
    elif s[i] == 'b': b -= 1; i += 1
    return 12*(int(s[i:])+1)+b
buf = np.zeros((int(SR*(DUR+4)), 2))
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t*SR); n = min(len(sig), len(buf)-i)
    if n <= 0: return
    l, r = np.cos((pan+1)*np.pi/4), np.sin((pan+1)*np.pi/4)
    buf[i:i+n, 0] += sig[:n]*gain*l; buf[i:i+n, 1] += sig[:n]*gain*r
def env(n, a=0.005, d=1.0):
    t = np.arange(n)/SR; e = np.exp(-t/d); k = int(a*SR); e[:k] *= np.linspace(0, 1, k) if k else 1; return e
def pluck(f, dur=1.5, bright=0.5, decay=0.996):           # Karplus-Strong
    N = int(SR/f); n = int(dur*SR); y = np.zeros(n); b = rng.uniform(-1, 1, N)
    b = np.convolve(b, [bright, 1-bright], 'same')
    for i in range(n):
        y[i] = b[i % N]; b[i % N] = decay*0.5*(b[i % N] + b[(i+1) % N])
    return y*np.exp(-np.arange(n)/SR/ (dur*0.6))
def mallet(f, dur=1.2, partials=((1,1),(2.76,0.35),(5.4,0.12)), d=0.5):
    t = np.arange(int(dur*SR))/SR
    return sum(a*np.sin(2*np.pi*f*p*t)*np.exp(-t/(d/p**0.5)) for p, a in partials)*env(len(t), 0.002, 10)
def piano(f, dur=2.5):
    t = np.arange(int(dur*SR))/SR
    s = sum((0.6**k)*np.sin(2*np.pi*f*(k+1)*t*(1+0.0004*k*k))*np.exp(-t*(0.9+0.6*k)) for k in range(7))
    return s*env(len(t), 0.004, 10)
def strings(f, dur):
    t = np.arange(int(dur*SR))/SR; s = np.zeros_like(t)
    for det in (-0.004, 0, 0.005):
        ph = (f*(1+det)*t) % 1.0; s += 2*ph-1
    y = np.zeros_like(s); a = 0.035
    for i in range(1, len(s)): y[i] = y[i-1]+a*(s[i]-y[i-1])
    e = np.minimum(1, t/0.6)*np.minimum(1, (dur-t)/0.5).clip(0); return y*e*0.5
def wood(dur=0.08, f=1800):
    n = int(dur*SR); x = rng.normal(0, 1, n)*np.exp(-np.arange(n)/SR/0.012)
    t = np.arange(n)/SR; return x*0.3 + np.sin(2*np.pi*f*t)*np.exp(-t/0.02)
CH = {'C':['C4','E4','G4'], 'G':['B3','D4','G4'], 'Am':['C4','E4','A4'], 'F':['C4','F4','A4'], 'Em':['B3','E4','G4'], 'Dm':['D4','F4','A4']}
BASS = {'C':'C3','G':'G2','Am':'A2','F':'F2','Em':'E2','Dm':'D2'}
if style == 'uke':          # 1: ukulele strum + glockenspiel melody, bright and happy (~100 bpm)
    bpm = 100; b = 60/bpm; prog = ['C','G','Am','F']*4
    mel = ['E5','G5','A5','G5','E5','D5','C5','D5','E5','G5','A5','C6','B5','G5','A5','G5']
    for bar, c in enumerate(prog):
        t0 = bar*4*b
        if t0 > DUR: break
        for beat, (dly, vol) in enumerate([(0,1),(1,0.6),(1.5,0.7),(2,0.9),(3,0.6),(3.5,0.7)]):
            for k, n in enumerate(CH[c]+[CH[c][0][:-1]+str(int(CH[c][0][-1])+1)]):
                add(pluck(midi(nm(n)), 1.2, 0.6), t0+dly*b+k*0.012, 0.16*vol, -0.3)
        add(pluck(midi(nm(BASS[c])), 1.8, 0.3, 0.998), t0, 0.35, 0)
        add(pluck(midi(nm(BASS[c])), 1.8, 0.3, 0.998), t0+2*b, 0.25, 0)
        if bar % 4 >= 0:
            for j in range(4):
                n = mel[(bar*4+j) % len(mel)]
                add(mallet(midi(nm(n)), 1.0), t0+j*b, 0.18, 0.35)
elif style == 'piano':      # 2: soft piano arpeggios + string pad, warm (~72 bpm)
    bpm = 72; b = 60/bpm; prog = ['C','Am','F','G']*4
    mel = ['E5','D5','C5','G4','A4','C5','D5','E5','F5','E5','D5','C5','D5','C5','B4','C5']
    for bar, c in enumerate(prog):
        t0 = bar*4*b
        if t0 > DUR: break
        notes = [BASS[c]]+CH[c]+[CH[c][1][:-1]+str(int(CH[c][1][-1])+1)]
        for j, n in enumerate(notes+notes[1:4][::-1]):
            add(piano(midi(nm(n))), t0+j*b/2, 0.13, -0.2+0.1*j/len(notes))
        for n in CH[c]: add(strings(midi(nm(n)), 4*b+0.6), t0, 0.05, 0.3)
        add(piano(midi(nm(mel[(bar*2) % len(mel)]))), t0, 0.16, 0.1)
        add(piano(midi(nm(mel[(bar*2+1) % len(mel)]))), t0+2*b, 0.14, 0.1)
elif style == 'pizz':       # 3: pizzicato + marimba + tick-tock woodblock, playful "waiting" (~110 bpm)
    bpm = 110; b = 60/bpm; prog = ['C','C','G','G','Am','F','G','C']*2
    mel = ['C5','E5','G5','E5','D5','F5','A5','F5','E5','G5','C6','G5','D5','B4','G4','B4']
    for bar, c in enumerate(prog):
        t0 = bar*4*b
        if t0 > DUR: break
        for j in range(4):
            add(wood(0.06, 2000 if j % 2 == 0 else 1500), t0+j*b, 0.10, 0.5 if j % 2 == 0 else -0.5)
            n = CH[c][j % 3] if j else BASS[c]
            add(pluck(midi(nm(n)), 0.5, 0.25, 0.990), t0+j*b, 0.28, -0.2)
        for j in range(4):
            if (bar+j) % 2 == 0 or j == 0:
                add(mallet(midi(nm(mel[(bar*4+j) % len(mel)])), 0.9, ((1,1),(4,0.25),(9.8,0.05)), 0.35), t0+j*b+b/2*(j % 2), 0.20, 0.25)
elif style == 'musicbox':   # 4: Little Wonder chorus motif on music box/celesta + soft pad (~84 bpm)
    bpm = 84; b = 60/bpm
    # melody approximated from the theme song chorus ("Little wonder, little wonder, every day's a brand-new wonder")
    phrase = [('B5',1),('A5',1),('G5',2),('B5',1),('A5',1),('G5',1),('E5',1),('G5',1),('A5',1),('B5',1),('C6',1),('B5',1),('A5',1),('G5',2)]
    prog = ['G','Em','C','D']*4
    CH['D'] = ['A3','D4','F#4']; BASS['D'] = 'D3'; CH['G'] = ['B3','D4','G4']; BASS['G'] = 'G2'
    t = 0.0; reps = 0
    while t < DUR:
        for n, l in phrase:
            add(mallet(midi(nm(n)), 1.6, ((1,1),(3.0,0.18),(6.1,0.05)), 0.9), t, 0.20, 0.2)
            t += l*b
        t += 2*b; reps += 1
    for bar, c in enumerate(prog):
        t0 = bar*4*b
        if t0 > DUR: break
        for n in CH[c]: add(strings(midi(nm(n)), 4*b+0.6), t0, 0.04, -0.3)
        add(mallet(midi(nm(BASS[c]))*1, 2.0, ((1,1),(2,0.2)), 1.2), t0, 0.10, -0.1)
# reverb (feedback combs + allpass), master
def reverb(x, mix=0.22):
    y = np.zeros_like(x)
    for d, g in [(1557,0.84),(1617,0.83),(1491,0.82),(1422,0.81)]:
        c = np.zeros_like(x)
        for i in range(d, len(x)): c[i] = x[i] + g*c[i-d]
        y += c
    for d in (225, 556):
        z = np.zeros_like(y)
        for i in range(d, len(y)): z[i] = -0.5*y[i] + y[i-d] + 0.5*z[i-d]
        y = z
    return x*(1-mix) + y*mix/4
L = reverb(buf[:, 0]); R = reverb(buf[:, 1])
mix = np.stack([L, R], 1)[:int(SR*DUR)]
fade = int(SR*1.5); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]; mix[:int(SR*0.05)] *= np.linspace(0, 1, int(SR*0.05))[:, None]
mix /= max(1e-9, np.abs(mix).max())/0.85
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print("ok", out, DUR)
