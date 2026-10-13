#!/usr/bin/env python3
# usage: whipaudio.py WHIP.mp4 A.mp4 B.mp4 B_start OUT.mp4
# Replace a whipjoin clip's audio with A audio (to A's video length) + B audio (from B_start, to the remaining length),
# 0.2s fade out/in at the seam -> audio length == video length, no drift for later clips.
import sys, subprocess
w, a, b, bs, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5]
dur = lambda f, s: float(subprocess.run(["ffprobe","-v","error","-select_streams",s,"-show_entries","stream=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout.split()[0])
W, A = dur(w,"v:0"), dur(a,"v:0"); B = W - A
fc = (f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{A},asetpts=PTS-STARTPTS,apad=whole_dur={A},afade=t=out:st={A-0.2}:d=0.2[x];"
      f"[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim={bs}:{bs+B},asetpts=PTS-STARTPTS,apad=whole_dur={B},afade=t=in:d=0.2[y];[x][y]concat=n=2:v=0:a=1[o]")
subprocess.run(["ffmpeg","-v","error","-y","-i",w,"-i",a,"-i",b,"-filter_complex",fc,"-map","0:v","-map","[o]","-c:v","copy","-c:a","aac","-b:a","192k",out],check=True)
print("ok", out, W, dur(out,"a:0"))
