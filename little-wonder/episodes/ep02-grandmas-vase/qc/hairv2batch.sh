#!/bin/bash
# hairv2batch.sh — Hoor hair v2 (flicker-free) on every Hoor shot, always from the untouched originals in shots/_hair_old/
cd "$(dirname "$0")/.."
orig(){ [ -f shots/_hair_old/shot${1}_graded.mp4 ] && echo shots/_hair_old/shot${1}_graded.mp4 || echo shots/_hair_old/shot$1.mp4; }
{
grep -v '^#' qc/hoorhair_keypoints.txt | while read n rest; do
  [ -z "$n" ] && continue; grep -q "^$n " qc/hoorhair_strict.txt && continue
  kp=$(python3 -c "import sys;print(','.join(f'{float(t)}:{float(x)*1280/480:.0f}:{float(y)*720/270:.0f}' for t,x,y in (p.split(':') for p in sys.argv[1:])))" $rest)
  echo "$n|$kp|320|0"; done
grep -v '^#' qc/hoorhair_strict.txt | while read n R B rest; do [ -z "$n" ] && continue; echo "$n|$(echo $rest | tr ' ' ',')|$B|$R"; done
} | while IFS='|' read n kp B R; do
  src=$(orig $n)
  r=$(python3 qc/hoorhair_v2.py $src qc/hair_tmp/shot$n.mp4 "$kp" $B $R </dev/null 2>&1 | grep -E '^frames')
  f=$(python3 qc/flickqc.py $src qc/hair_tmp/shot$n.mp4 qc/hair_tmp/f$n.png </dev/null 2>&1 | tail -1)
  python3 qc/hairqc.py $src qc/hair_tmp/shot$n.mp4 qc/hair_tmp/q$n.png </dev/null
  echo "$n $r | $f"
done
