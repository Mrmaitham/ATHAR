#!/usr/bin/env python3
"""Little Wonder shot QA.  usage:
  qa.py VIDEO --shot S007 --cast Noonoo,Nadyah,Hoor,Zoozoo [--prev PREV.mp4] [--lines "Hoor: I'll win"] [--no-audio] [--out DIR]
         [--attempt N] [--identity-signoff "نعم: فحصت كل بنود الهوية بإطار البداية والوسط والنهاية"]
Exit 0 = automatic checks pass AND identity checklist signed off. 1 = at least one FAIL. 2 = identity checklist NOT signed off (video is NOT sendable).
Rules: episodes/ep03-QA-RULES.md (updated 2026-11-08)."""
import argparse, json, os, re, subprocess, sys
import cv2, numpy as np

# ---- thresholds (from episodes/ep03-DIRECTOR-RULES.md) ----
JOIN_MIN = 0.60; LUM_MIN = 133; SAT_MIN = 133; CAM_MAX_SHIFT = 3.0
BAD_NAMES = {"zuzu": "ZOO-zoo", "miss shoe": "MISH-oo", "fanuda": "AF-nahn", "fanoona": "AF-nahn", "nunu": "NOO-noo",
             "afnan": None}  # None = fine, listed only to document spelling variants
# characters whose colours are distinctive enough for automatic presence detection
REL_TOL = 0.15  # brightness / saturation must stay within 15% of the previous approved shot
# identity checklist per character, from ep-refs-APPROVED/TURNAROUNDS_3D (tick EVERY item at first / middle / last frame)
IDENTITY = {
 "Zoozoo": "white hijab; cream coat with ruffle collar + belt; cream trousers; gold pendant; beige shoes",
 "Noonoo": "long black wavy hair; pink butterfly t-shirt; black cargo pants; gold pendant; plain WHITE sneakers (never pink)",
 "Nadyah": "dark ponytail; blue sleeveless vest over white top; blue shorts; gold heart necklace; WHITE velcro sneakers (never pink/blue)",
 "Hoor": "TWO curly puffs with cream polka-dot bows; pink sleeveless blazer vest over white top; PINK SHORTS (not trousers); gold heart necklace; BLACK velcro sneakers with white soles",
 "Afnan": "short dark brown bob, side part, NO bow/clip; pale green tulle dress with pastel butterflies; gold heart necklace + gold bangles; WHITE bow sandals; height ~46% of Grandma",
 "Grandma": "black hijab; black abaya; kind elderly face; black shoes",
 "Mishoo": "grey tabby cat with gold collar",
}
AUTO = {"Grandma", "Nadyah", "Afnan", "Hoor", "Noonoo"}
EYE_ONLY = {"Zoozoo", "Mishoo"}  # cream/grey collide with house cladding, path and grass

def frames(path, fps=2):
    cap = cv2.VideoCapture(path); n = cap.get(cv2.CAP_PROP_FRAME_COUNT); r = cap.get(cv2.CAP_PROP_FPS) or 24
    step = max(1, int(round(r / fps))); out = []; i = 0
    while True:
        ok, f = cap.read()
        if not ok: break
        if i % step == 0: out.append(f)
        last = f; i += 1
    if out and last is not None: out.append(last)
    return out, r

def ssim(a, b):
    a = cv2.cvtColor(cv2.resize(a, (320, 180)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    b = cv2.cvtColor(cv2.resize(b, (320, 180)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    C1, C2 = 6.5025, 58.5225; g = lambda x: cv2.GaussianBlur(x, (11, 11), 1.5)
    ma, mb = g(a), g(b); sa = g(a * a) - ma * ma; sb = g(b * b) - mb * mb; sab = g(a * b) - ma * mb
    return float((((2 * ma * mb + C1) * (2 * sab + C2)) / ((ma * ma + mb * mb + C1) * (sa + sb + C2))).mean())

def aligned_ssim(a, b):
    """best SSIM after rescaling b around its centre (handles a small re-frame between shots). returns (best, scale)"""
    best, bs = ssim(a, b), 1.0
    h, w = b.shape[:2]
    for sc in (0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.05, 1.1, 1.15, 1.2, 1.3, 1.4):
        r = cv2.resize(b, None, fx=sc, fy=sc)
        if sc > 1: y0, x0 = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2; r = r[y0:y0 + h, x0:x0 + w]
        else:
            canvas = np.zeros_like(b); y0, x0 = (h - r.shape[0]) // 2, (w - r.shape[1]) // 2; canvas[y0:y0 + r.shape[0], x0:x0 + r.shape[1]] = r; r = canvas
        v = ssim(a, r)
        if v > best: best, bs = v, sc
    return best, bs

def color(f):
    rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB).astype(np.float32)
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).mean()
    sat = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)[..., 1].mean()
    return float(lum), float(sat), float(rgb[..., 0].mean() / max(rgb[..., 2].mean(), 1))

def camera_shift(fs):
    g = [cv2.cvtColor(cv2.resize(f, (480, 270)), cv2.COLOR_BGR2GRAY).astype(np.float32)[:80] for f in fs]
    win = cv2.createHanningWindow((480, 80), cv2.CV_32F)
    return max(abs(np.hypot(*cv2.phaseCorrelate(g[0], x, win)[0])) for x in g[1:]) if len(g) > 1 else 0.0

def masks(f):
    f = cv2.resize(f, (640, 360)); h = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); H, S, V = h[..., 0], h[..., 1], h[..., 2]
    return {"Nadyah": (H >= 100) & (H <= 125) & (S > 120) & (V > 120),
            "Afnan": (H >= 38) & (H <= 75) & (S > 40) & (V > 120) & (S < 150),
            "Hoor": ((H >= 170) | (H <= 4)) & (S > 35) & (S < 130) & (V > 190),
            "Noonoo": (H >= 145) & (H < 170) & (S > 35) & (S < 150) & (V > 170),
            "Grandma": (V < 55)}

def present(f, min_frac=0.0015):
    res = {}
    for k, m in masks(f).items():
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, _, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(m, np.ones((15, 15), np.uint8)))
        areas = [st[i, cv2.CC_STAT_AREA] for i in range(1, n)]
        res[k] = (m.mean() >= min_frac, sum(a > 1500 for a in areas))
    return res

def transcript(path, model="medium.en"):
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segs, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(a, vad_filter=False, condition_on_previous_text=False, language="en")
    return " ".join(s.text.strip() for s in segs)

def name_heard(text, name):
    """exact -> 'exact'; close phonetic variants (afna, afman, afnaan...) -> 'near' (WARN, not a pass); else None"""
    toks = norm(text)
    if name in toks: return "exact"
    import difflib
    if any(difflib.SequenceMatcher(None, name, t).ratio() >= 0.7 for t in toks if len(t) >= 3): return "near"
    return None

def norm(t): return re.sub(r"[^a-z0-9 ]", "", t.lower().replace("-", " ")).split()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--shot", default="shot"); ap.add_argument("--cast", default="")
    ap.add_argument("--prev"); ap.add_argument("--lines", default=""); ap.add_argument("--no-audio", action="store_true"); ap.add_argument("--out", default="qa_out")
    ap.add_argument("--attempt", type=int, default=1); ap.add_argument("--identity-signoff", default="")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); rep = {"shot": a.shot, "checks": [], "eye": []}
    def add(name, ok, detail, soft=False): rep["checks"].append({"check": name, "result": "PASS" if ok else ("WARN" if soft else "FAIL"), "detail": detail})
    fs, fps = frames(a.video); cast = [c for c in a.cast.split(",") if c]
    if a.prev:
        pf, _ = frames(a.prev); s = ssim(pf[-1], fs[0]); sa, sc = aligned_ssim(pf[-1], fs[0])
        add("join SSIM(prev last, first)", max(s, sa) >= JOIN_MIN, f"raw {s:.2f} / aligned {sa:.2f} at scale x{sc:.2f} (min {JOIN_MIN}); first frame is {'WIDER' if sc < 0.95 else 'TIGHTER' if sc > 1.05 else 'the same framing'} than prev last - confirm it matches the script")
        prev_cs = [color(f) for f in pf]; prev_lum, prev_sat = (float(np.mean([c[i] for c in prev_cs])) for i in range(2))
    else: rep["eye"].append("no --prev given: join not checked"); prev_lum = prev_sat = None
    cs = [color(f) for f in fs]; lum, sat, rb = (float(np.mean([c[i] for c in cs])) for i in range(3))
    if prev_lum is not None:
        add("brightness vs previous approved shot", abs(lum - prev_lum) <= REL_TOL * prev_lum, f"{lum:.0f} vs {prev_lum:.0f} (+-{REL_TOL:.0%})")
        add("saturation vs previous approved shot", abs(sat - prev_sat) <= REL_TOL * prev_sat, f"{sat:.0f} vs {prev_sat:.0f} (+-{REL_TOL:.0%})")
    else:
        add("brightness (absolute, no prev given)", lum >= LUM_MIN, f"{lum:.0f} (min {LUM_MIN}); the pale house always reads low", soft=True)
        add("saturation (absolute, no prev given)", sat >= SAT_MIN, f"{sat:.0f} (min {SAT_MIN}); the pale house always reads low", soft=True)
    add("cool light R/B (flag only)", True, f"{rb:.2f} (target 1.5-2.0{'' if 1.5 <= rb <= 2.0 else ' - OUT OF RANGE, look at it'})")
    sh = camera_shift(fs); add("camera movement (advisory, moving camera allowed)", sh <= CAM_MAX_SHIFT, f"max background shift {sh:.1f}px - check by eye that it matches the script", soft=True)
    pres = [present(f) for f in fs]
    for c in cast:
        if c in AUTO:
            frac = np.mean([p[c][0] for p in pres]); add(f"{c} colour present (advisory)", frac >= 0.6, f"seen in {frac:.0%} of frames", soft=True)
        else: rep["eye"].append(f"{c}: cream/grey colours collide with the scene, confirm by eye")
    for c in AUTO - set(cast):
        frac = np.mean([p[c][0] for p in pres]); add(f"{c} colour absent (advisory)", frac < 0.3, f"seen in {frac:.0%} of frames - grass/shadows can trigger Afnan/Grandma", soft=True)
    rep["eye"] += ["character count per frame (no duplicates/missing)", "identity vs turnaround sheets (outfit, hair, jewellery)",
                   "heights vs table (Grandma=100 Zoozoo 90 Noonoo 84 Nadyah 55 Hoor 49 Afnan 46 Mishoo seated 23): MEASURE head-to-feet at the same depth and write the numbers", "nobody looks at camera / walks toward it", "state of objects vs shot sheet (door open/closed, ribbon, props)", "each exit has a reason", "last frame passes the identity checklist (it is the next shot's start)"]
    rep["identity_checklist"] = {c: IDENTITY.get(c, "(no checklist)") for c in cast}
    if not a.no_audio:
        t = transcript(a.video); ts = [t]
        try: ts.append(transcript(a.video, "small.en"))
        except Exception as e: rep["eye"].append(f"second ASR model unavailable: {e}")
        rep["transcript"] = " || ".join(ts); low = " ".join(ts).lower()
        bad = [k for k, v in BAD_NAMES.items() if v and k in low]; add("name pronunciation", not bad, "wrong variants heard: " + ", ".join(bad) if bad else "ok")
        if a.lines:
            exp = norm(a.lines); got = set(w for x in ts for w in norm(x)); miss = [w for w in exp if w not in got]
            add("dialogue matches script", len(miss) <= max(1, len(exp) // 6), f"missing words: {miss}")
            for nm in ("afnan", "zoozoo", "noonoo", "nadyah", "hoor", "mishoo"):
                if nm in exp:
                    hs = [name_heard(x, nm) for x in ts]
                    ok = "exact" in hs
                    add(f"name '{nm}' spoken clearly", ok, f"heard: {hs} (a near variant such as 'afna/afman' is NOT a pass - listen / regenerate)")
    idx = np.linspace(0, len(fs) - 1, min(12, len(fs))).astype(int); th = [cv2.resize(fs[i], (480, 270)) for i in idx]
    while len(th) % 4: th.append(np.zeros_like(th[0]))
    cv2.imwrite(f"{a.out}/{a.shot}_sheet.jpg", np.vstack([np.hstack(th[i:i + 4]) for i in range(0, len(th), 4)]))
    json.dump(rep, open(f"{a.out}/{a.shot}_report.json", "w"), ensure_ascii=False, indent=1)
    for c in rep["checks"]: print(f"[{c['result']}] {c['check']}: {c['detail']}")
    print("EYE REVIEW:", *rep["eye"], sep="\n  - ")
    print("IDENTITY CHECKLIST (tick every item at first / middle / last frame):"); [print(f"  - {k}: {v}") for k, v in rep["identity_checklist"].items()]
    fail = any(c["result"] == "FAIL" for c in rep["checks"]); signed = bool(a.identity_signoff)
    verdict = "NOT SENDABLE: automatic FAIL" if fail else ("NOT SENDABLE: identity checklist not signed off (--identity-signoff)" if not signed else "OK to send (only if the eye review above also passed)")
    print("VERDICT:", verdict)
    log = os.environ.get("QA_LOG", "/home/user/ATHAR/.agents/projects/little-wonder/episodes/ep03-QA-LOG.md")
    try:
        with open(log, "a", encoding="utf-8") as lf: lf.write(f"| {a.shot} | attempt {a.attempt} | {os.path.basename(a.video)} | {'FAIL' if fail else 'auto-pass'} | identity signoff: {a.identity_signoff or 'NO'} | {verdict} |\n")
    except OSError: pass
    sys.exit(1 if fail else (0 if signed else 2))

if __name__ == "__main__": main()
