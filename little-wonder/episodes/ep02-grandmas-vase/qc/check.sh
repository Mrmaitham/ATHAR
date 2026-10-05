#!/bin/bash
# usage: qc/check.sh NN PREV URL  — download, QC, face/tail crops, transcript
S=/tmp/claude-0/-home-user-ATHAR/808f4051-f44a-5338-a794-9ee8e53308d1/scratchpad
N=$1; P=$2; U=$3
[ -n "$U" ] && curl -sS -o shots/shot$N.mp4 "$U"
bash qc/qc.sh $N $P 2>&1 | tail -6 | grep -v rms
ffmpeg -loglevel error -y -i shots/shot$N.mp4 -vf "fps=8,crop=300:70:740:130,scale=200:-1,tile=8x5" -frames:v 1 $S/f.png
ffmpeg -loglevel error -y -i shots/shot$N.mp4 -vf "fps=2,crop=500:300:780:340,scale=320:-1,tile=5x2" -frames:v 1 $S/t.png
python3 -c "
from faster_whisper import WhisperModel
m=WhisperModel('medium.en',compute_type='int8')
s,_=m.transcribe('shots/shot$N.mp4',word_timestamps=True)
print([(w.word,round(w.start,2),round(w.end,2)) for x in s for w in x.words])
" 2>/dev/null
