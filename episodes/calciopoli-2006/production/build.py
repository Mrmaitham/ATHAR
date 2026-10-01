"""Assemble Calciopoli 2006 with FFmpeg.

Per scene: Ken Burns on each image (split evenly over the narration),
overlay PNG faded in, narration + pad. All scene files share codecs so
they can be joined with the concat demuxer. Every scene file carries an
audio track (silent when needed) — see the Baggio silent-audio bug.
"""
import json, os, glob, subprocess, sys, concurrent.futures as cf

FPS = 30
PAD = 0.5            # breath after each narration line
CARD_DUR = {"S010": 5.0, "S107": 5.0}
sc = json.load(open("scenes.json"))
os.makedirs("segs", exist_ok=True); os.makedirs("scenes_mp4", exist_ok=True)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(cmd[:6]) + "\n" + r.stderr[-1500:])


def kb(img, out, dur, mode):
    F = max(2, round(dur * FPS))
    z = {0: f"1+0.10*on/{F}", 1: f"1.10-0.10*on/{F}", 2: "1.10", 3: "1.10"}[mode]
    x = {0: "iw/2-(iw/zoom/2)", 1: "iw/2-(iw/zoom/2)",
         2: f"(iw-iw/zoom)*on/{F}", 3: f"(iw-iw/zoom)*(1-on/{F})"}[mode]
    y = "ih/2-(ih/zoom/2)"
    vf = (f"scale=2880:1620:force_original_aspect_ratio=increase,crop=2880:1620,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={F}:s=1920x1080:fps={FPS},format=yuv420p")
    run(["ffmpeg", "-y", "-v", "error", "-i", img, "-vf", vf, "-frames:v", str(F),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), out])


def scene_images(s):
    i = int(s["id"][1:])
    return [p for k in range(1, 5) for p in glob.glob(f"images/I{i*10+k:04d}.png")]


def build_scene(s):
    sid = s["id"]; i = int(sid[1:]); out = f"scenes_mp4/{sid}.mp4"
    if os.path.exists(out): return sid
    aud = f"audio/{sid}.mp3"
    has_aud = os.path.exists(aud)
    dur = (s["dur"] + PAD) if has_aud else CARD_DUR.get(sid, 4.0)
    # video track
    if s["type"] == "CARD":
        imgs, modes = [f"cards/{sid}.png"], [0]
    else:
        imgs = scene_images(s)
        modes = [(i + k) % 4 for k in range(len(imgs))]
    seg_d = dur / len(imgs); segs = []
    for k, (im, m) in enumerate(zip(imgs, modes)):
        sp = f"segs/{sid}_{k}.mp4"
        clip = "clips/" + os.path.basename(im).replace(".png", ".mp4")
        if os.path.exists(clip):
            src = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                        "-of", "csv=p=0", clip], capture_output=True, text=True).stdout)
            slow = min(2.0, max(1.0, seg_d / src))
            run(["ffmpeg", "-y", "-v", "error", "-i", clip, "-vf",
                 f"setpts={slow:.3f}*PTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
                 f"fps={FPS},tpad=stop_mode=clone:stop_duration={seg_d:.3f},format=yuv420p",
                 "-an", "-t", f"{seg_d:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", sp])
        else:
            kb(im, sp, seg_d, m)
        segs.append(sp)
    lst = f"segs/{sid}.txt"
    open(lst, "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in segs))
    vid = f"segs/{sid}_v.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
    # overlay + audio
    ov = f"overlays/{sid}.png"
    inputs = ["-i", vid]
    fc = "[0:v]null[v0]"
    if os.path.exists(ov) and s["type"] != "CARD":
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", ov]
        fc = (f"[1:v]format=rgba,fade=in:st=0.4:d=0.5:alpha=1,"
              f"fade=out:st={max(0.9, dur-0.6):.3f}:d=0.5:alpha=1[o];[0:v][o]overlay=0:0:format=auto[v0]")
    ai = len([x for x in inputs if x == "-i"])
    if has_aud:
        inputs += ["-i", aud]
        fc += f";[{ai}:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={dur:.3f}[a0]"
    else:
        inputs += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        fc += f";[{ai}:a]anull[a0]"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc,
         "-map", "[v0]", "-map", "[a0]", "-t", f"{dur:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out])
    return sid


if __name__ == "__main__":
    only = sys.argv[1:]
    todo = [s for s in sc if not only or s["id"] in only]
    with cf.ThreadPoolExecutor(4) as ex:
        for sid in ex.map(build_scene, todo): print(sid, flush=True)
