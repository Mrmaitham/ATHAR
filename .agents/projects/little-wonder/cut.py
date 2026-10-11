#!/usr/bin/env python3
# usage: cut.py OUT.mp4 clip1 [d] clip2 [d] clip3 ...   (d = dissolve seconds before next clip, 0 = cut)
# optional --num : burn shot numbers top-left. Single-pass graph, yuv420p, 48k aac, loudnorm.
import sys, subprocess
a = sys.argv[1:]; num = "--num" in a; a = [x for x in a if x != "--num"]
out, rest = a[0], a[1:]
clips, ds = [], []
for x in rest:
    if x.endswith(".mp4"): clips.append(x)
    else: ds.append(float(x))
while len(ds) < len(clips)-1: ds.append(0.0)
dur = lambda f: float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout)
D = [dur(c) for c in clips]
inp = sum([["-i", c] for c in clips], [])
f = []
for i in range(len(clips)):
    lab = f",drawtext=text='{i+1}':x=20:y=16:fontsize=40:fontcolor=white:borderw=3:bordercolor=black" if num else ""
    f.append(f"[{i}:v]scale=1280:720,fps=24,setsar=1,format=yuv420p,settb=AVTB{lab}[v{i}];[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
v, au, t = "v0", "a0", D[0]
for i in range(1, len(clips)):
    d = ds[i-1]
    if d > 0:
        f.append(f"[{v}][v{i}]xfade=transition=fade:duration={d}:offset={t-d:.3f}[vx{i}];[{au}][a{i}]acrossfade=d={d}[ax{i}]"); t = t-d+D[i]
    else:
        f.append(f"[{v}][{au}][v{i}][a{i}]concat=n=2:v=1:a=1[vx{i}][ax{i}]"); t = t+D[i]
    v, au = f"vx{i}", f"ax{i}"
f.append(f"[{au}]loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[aout]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(f),"-map",f"[{v}]","-map","[aout]","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-b:a","192k","-ar","48000",out],check=True)
print("ok", out, round(t, 2), "s")
