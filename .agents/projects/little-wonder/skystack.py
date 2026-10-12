#!/usr/bin/env python3
# usage: skystack.py SKY_OUTPAINT.png BASE_TALL.png OUT.png  - SKY_OUTPAINT = outpaint of BASE's top (W x W*9/16) crop;
# stacks its extra sky above BASE (found by matching, 120px ramp) -> taller image so a day-card tilt clears all characters.
import sys, numpy as np
from PIL import Image
S = Image.open(sys.argv[1]).convert('RGB'); T = Image.open(sys.argv[2]).convert('RGB'); W = T.width; h = W * 9 // 16
top = T.crop((0, 0, W, h)); S = S.resize((W, int(round(S.height * W / S.width))))
ref = np.asarray(top.resize((224, 126))).astype(float); best = None
for oy in range(0, S.height - h + 1, 4):
    d = abs(np.asarray(S.crop((0, oy, W, oy + h)).resize((224, 126))).astype(float) - ref).mean()
    if best is None or d < best[0]: best = (d, oy)
d, oy = best; out = Image.new('RGB', (W, oy + T.height)); out.paste(S.crop((0, 0, W, oy + h)), (0, 0))
m = np.ones((T.height, W)); m[:120] = np.linspace(0, 1, 120)[:, None]
out.paste(T, (0, oy), Image.fromarray((m * 255).astype(np.uint8))); out.save(sys.argv[3]); print('offset', oy, 'diff', round(d, 1), out.size)
