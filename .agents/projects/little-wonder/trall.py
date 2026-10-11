import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8")
for n in range(1,74):
    f = "s05t.mp4" if n==5 else f"s{n:02d}.mp4"
    raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout
    a = np.frombuffer(raw,np.int16).astype(np.float32)/32768
    segs,_ = m.transcribe(a, vad_filter=False, condition_on_previous_text=False, language="en")
    print(n, "|", " ".join(s.text.strip() for s in segs), flush=True)
