#!/bin/bash
cd "$(dirname "$0")/.."
grep -v '^#' qc/hoorhair_strict.txt | while read n R B rest; do
  [ -z "$n" ] && continue
  src=shots_graded/shot$n.mp4; [ -f $src ] || src=shots/shot$n.mp4
  kp=$(echo $rest | tr ' ' ',')

  r=$(python3 qc/hoorhair_track.py $src qc/hair_tmp/shot$n.mp4 "$kp" $B $R </dev/null 2>&1 | grep -E '^frames')
  python3 qc/hairqc.py $src qc/hair_tmp/shot$n.mp4 qc/hair_tmp/q$n.png </dev/null
  echo "$n $r"
done
