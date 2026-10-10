# Grade a shot so the mean colour of its top sky band equals a target (default 142,119,110).
# One constant gain per shot (from the mean over sampled frames) so motion never flickers.
import subprocess, sys, numpy as np
src, dst = sys.argv[1], sys.argv[2]
tgt = np.array([float(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "142,119,110").split(",")])
w, h = 64, 36
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps=4,scale={w}:{h},format=rgb24",
                      "-f", "rawvideo", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(float)
band = a[:, : h // 4].reshape(len(a), -1, 3)
first, last, mean = band[0].mean(0), band[-1].mean(0), band.mean((0, 1))
k = tgt / mean
print(f"sky first={first.round()} last={last.round()} mean={mean.round()} gain={k.round(4)}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                f"colorchannelmixer=rr={k[0]:.4f}:gg={k[1]:.4f}:bb={k[2]:.4f}",
                "-c:v", "libx264", "-crf", "18", "-c:a", "copy", dst], check=True)
