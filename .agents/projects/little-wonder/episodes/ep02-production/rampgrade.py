# Grade a shot: first match full-frame colour to a reference frame (same framing), then scale
# uniformly so the sky band's red level hits a target (lighting ramp, e.g. 135 -> 142).
# usage: rampgrade.py src dst ref_video ref_time sky_target [first|last]
import subprocess, sys, numpy as np
src, dst, ref, rt, sky_t = sys.argv[1:6]; mode = sys.argv[6] if len(sys.argv) > 6 else "first"
def px(f, t=None, crop=False, sseof=False):
    vf = ("crop=iw:ih*0.25:0:0," if crop else "") + "scale=1:1,format=rgb24"
    a = ["ffmpeg", "-v", "error"] + (["-sseof", "-0.3"] if sseof else ["-ss", t]) + ["-i", f, "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-"]
    return np.frombuffer(subprocess.run(a, capture_output=True).stdout, np.uint8).astype(float)
last = mode == "last"
k = px(ref, rt) / px(src, "0", sseof=last) if not last else px(ref, rt) / px(src, sseof=True)
sky = px(src, "0", crop=True) * k if not last else px(src, crop=True, sseof=True) * k
k = k * (float(sky_t) / sky[0])
print(f"gain={k.round(4)} sky_after={(sky * float(sky_t) / sky[0]).round()}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                f"colorchannelmixer=rr={k[0]:.4f}:gg={k[1]:.4f}:bb={k[2]:.4f},format=yuv420p",
                "-c:v", "libx264", "-crf", "18", "-movflags", "+faststart", "-c:a", "copy", dst], check=True)
