#!/bin/bash
# finalize.sh NN — grade → abaya to reference black → last frame (+orange juice) for the next start
N=$1
python3 qc/grade.py $N >/dev/null && python3 qc/abayatone.py shots_graded/shot$N.mp4 shots_graded/shot${N}_t.mp4 820 60 1140 640 2>/dev/null && mv shots_graded/shot${N}_t.mp4 shots_graded/shot$N.mp4
rm -f qc/shot${N}_last.png; ffmpeg -y -v error -sseof -0.6 -i shots_graded/shot$N.mp4 -an -update 1 qc/shot${N}_last.png; [ -s qc/shot${N}_last.png ] || { echo "LAST FRAME FAILED $N"; exit 1; }
python3 qc/juicefix.py qc/shot${N}_last.png qc/shot${N}_last.png
echo done $N
