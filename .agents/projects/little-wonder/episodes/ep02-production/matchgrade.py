# Grade a shot so its full-frame mean colour at a sample point (first|last) matches a reference
# colour taken from another shot's frame with the same framing. Constant gain, yuv420p output.
# usage: matchgrade.py src dst ref_video ref_time [first|last]
import subprocess, sys, numpy as np
src, dst, ref, rt = sys.argv[1:5]; mode = sys.argv[5] if len(sys.argv) > 5 else "last"
def mean_at(f, t, sseof=False):
    a = ["ffmpeg", "-v", "error"] + (["-sseof", "-0.3"] if sseof else ["-ss", t]) + ["-i", f, "-frames:v", "1",
         "-vf", "scale=1:1,format=rgb24", "-f", "rawvideo", "-"]
    return np.frombuffer(subprocess.run(a, capture_output=True).stdout, np.uint8).astype(float)
tgt = mean_at(ref, rt)
cur = mean_at(src, "0") if mode == "first" else mean_at(src, None, sseof=True)
k = tgt / cur
print(f"ref={tgt} cur={cur} gain={k.round(4)}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                f"colorchannelmixer=rr={k[0]:.4f}:gg={k[1]:.4f}:bb={k[2]:.4f},format=yuv420p",
                "-c:v", "libx264", "-crf", "18", "-movflags", "+faststart", "-c:a", "copy", dst], check=True)
