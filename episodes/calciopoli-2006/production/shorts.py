"""Cut 5 vertical Shorts (1080x1920) from the rendered scene files.

Layout: blurred full-bleed background + the 16:9 film centred, hook title
on top, big burned-in English captions, BY ATHAR end line.
"""
import json, os, re, subprocess

PAD = 0.5
sc = json.load(open("scenes.json")); ids = [s["id"] for s in sc]; by = {s["id"]: s for s in sc}
SHORTS = {
    "01_the_key": ("S020", "S025", "He locked the referee in… and took the key"),
    "02_trezeguet": ("S055", "S061", "The World Cup final's cruellest twist"),
    "03_del_piero": ("S079", "S082", "Why Del Piero stayed in Serie B"),
    "04_milan": ("S083", "S086", "Punished… then champions of Europe"),
    "05_the_verdict": ("S088", "S093", "The verdict that came too late"),
}
os.makedirs("../shorts", exist_ok=True)


def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


def chunks(text, maxc=30):
    words, out, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > maxc: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out


def ass(sel, title, total, fn):
    hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,2,2,60,60,520,1
Style: Hook,Playfair Display,72,&H0017A3E8,&H0017A3E8,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,4,0,8,70,70,170,1
Style: End,Montserrat,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,4,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 0,{ts(0)},{ts(total-3)},Hook,,0,0,0,,{title}"]
    t = 0.0
    for sid in sel:
        s = by[sid]; dur = s["dur"] + PAD
        if s["narration"] and os.path.exists(f"audio/{sid}.mp3"):
            cs = chunks(s["narration"]); tot = sum(len(c) for c in cs); st = t
            for c in cs:
                d = s["dur"] * len(c) / tot
                ev.append(f"Dialogue: 0,{ts(st)},{ts(st+d)},Cap,,0,0,0,,{c}"); st += d
        t += dur
    ev.append(f"Dialogue: 0,{ts(total-3)},{ts(total)},End,,0,0,0,,Full story: CALCIOPOLI\\N{{\\c&H17A3E8&}}BY ATHAR")
    open(fn, "w").write(hdr + "\n".join(ev) + "\n")


for name, (a, b, title) in SHORTS.items():
    sel = ids[ids.index(a):ids.index(b) + 1]
    lst = f"segs/short_{name}.txt"
    open(lst, "w").write("".join(f"file '../scenes_mp4/{i}.mp4'\n" for i in sel))
    joined = f"segs/short_{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined], check=True)
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", joined],
                                 capture_output=True, text=True).stdout) + 3.0
    af = f"segs/short_{name}.ass"; ass(sel, title, total, af)
    fc = ("[0:v]tpad=stop_mode=clone:stop_duration=3,split[a][b];"
          "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.25[bg];"
          "[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2,"
          f"subtitles={af}:fontsdir=/home/user/ATHAR/assets/fonts[v];"
          "[0:a]apad=pad_dur=3,loudnorm=I=-14:TP=-1.5[aout]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[aout]", "-t", f"{total:.2f}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
                    f"../shorts/{name}.mp4"], check=True)
    print(name, round(total, 1), "s", flush=True)
