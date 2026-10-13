#!/usr/bin/env python3
# Depth-based background blur (Depth-Anything-V2 small, ONNX). Library + CLI test.
# usage (test on stills): bgblur.py IN.png OUT.png [far_pct=0.35] [sigma=14]
import sys, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
MODEL = '/home/user/lw_tools/models/depth_v2_small.onnx'
_sess = None
def depth(img):                      # img: PIL RGB -> relative inverse depth (higher = closer), same size as img
    global _sess
    if _sess is None: _sess = ort.InferenceSession(MODEL, providers=['CPUExecutionProvider'])
    w, h = 518, 294
    x = np.asarray(img.resize((w, h), Image.BICUBIC), np.float32)/255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    d = _sess.run(None, {'pixel_values': x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    d = (d - d.min()) / max(1e-6, d.max() - d.min())
    return np.asarray(Image.fromarray((d*255).astype(np.uint8)).resize(img.size, Image.BICUBIC), np.float32)/255
def blur_bg(img, d, far_pct=0.35, sigma=14, soft=0.12):
    # far = lowest-depth pixels; threshold at the far_pct quantile, soft ramp, feathered mask
    t = np.quantile(d, far_pct)
    m = np.clip((t + soft - d) / soft, 0, 1)                      # 1 = far (blur), 0 = near (keep)
    m = np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), np.float32)[..., None]/255
    b = np.asarray(img.filter(ImageFilter.GaussianBlur(sigma)), np.float32)
    a = np.asarray(img, np.float32)
    return Image.fromarray(np.clip(a*(1-m) + b*m, 0, 255).astype(np.uint8)), m[..., 0]
if __name__ == '__main__':
    im = Image.open(sys.argv[1]).convert('RGB'); fp = float(sys.argv[3]) if len(sys.argv) > 3 else 0.35; sg = float(sys.argv[4]) if len(sys.argv) > 4 else 14
    d = depth(im); o, m = blur_bg(im, d, fp, sg); o.save(sys.argv[2])
    Image.fromarray((m*255).astype(np.uint8)).save(sys.argv[2].replace('.png', '_mask.png'))
