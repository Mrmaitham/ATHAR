import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8")
for f in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout
    a = np.frombuffer(raw,np.int16).astype(np.float32)/32768
    segs,_ = m.transcribe(a, vad_filter=False, condition_on_previous_text=False, language="en")
    print(f, "|", " ".join(f"[{s.start:.1f}] {s.text.strip()}" for s in segs))
