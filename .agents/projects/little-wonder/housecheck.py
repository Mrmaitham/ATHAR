#!/usr/bin/env python3
# usage: housecheck.py CLIP.mp4 REF.png  -> house-band difference per 0.25s (top 28% of frame, robust median of abs diff)
# Low, flat values = house unchanged; a rising trend or jump = the house/background is changing.
import sys, subprocess, numpy as np
from PIL import Image
c, r = sys.argv[1], sys.argv[2]
ref = np.asarray(Image.open(r).convert('RGB').resize((640, 360)), np.float32)
raw = subprocess.run(['ffmpeg','-v','error','-i',c,'-vf','scale=640:360,fps=4','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, 360, 640, 3).astype(np.float32)
v = [float(np.median(np.abs(f[:100] - ref[:100]).mean(2))) for f in F]
print('house median diff:', ' '.join('%.0f' % x for x in v), '| max %.0f' % max(v))
