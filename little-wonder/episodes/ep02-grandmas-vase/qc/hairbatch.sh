#!/bin/bash
# hairbatch.sh — run hoorhair_track.py on every shot in hoorhair_keypoints.txt → qc/hair_tmp/shotNN.mp4 (+ qc sheet)
cd "$(dirname "$0")/.."
grep -v '^#' qc/hoorhair_keypoints.txt | while read n rest; do
  [ -z "$n" ] && continue
  src=shots_graded/shot$n.mp4; [ -f $src ] || src=shots/shot$n.mp4
  kp=$(python3 -c "import sys;print(','.join(f'{float(t)}:{float(x)*1280/480:.0f}:{float(y)*720/270:.0f}' for t,x,y in (p.split(':') for p in sys.argv[1:])))" $rest)
  r=$(python3 qc/hoorhair_track.py $src qc/hair_tmp/shot$n.mp4 "$kp" </dev/null 2>&1 | grep -E '^frames')
  python3 qc/hairqc.py $src qc/hair_tmp/shot$n.mp4 qc/hair_tmp/q$n.png </dev/null
  echo "$n $src $r"
done
