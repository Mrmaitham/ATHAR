import subprocess, sys, numpy as np
# prints per-frame mean abs diff (0-255) for the first N seconds
f=sys.argv[1]; secs=float(sys.argv[2]) if len(sys.argv)>2 else 1.5
w,h=160,90
raw=subprocess.run(["ffmpeg","-v","error","-i",f,"-t",str(secs),"-vf",f"scale={w}:{h},format=gray","-f","rawvideo","-"],capture_output=True).stdout
a=np.frombuffer(raw,np.uint8).reshape(-1,h,w).astype(float)
d=np.abs(np.diff(a,axis=0)).mean(axis=(1,2))
print(" ".join(f"{x:.2f}" for x in d))
