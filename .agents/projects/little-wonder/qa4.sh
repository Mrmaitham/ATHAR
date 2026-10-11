#!/bin/bash
# usage: qa4.sh NAME URL PREV_LAST KEY_END   -> qa3 + skyfix (NAME_k.mp4) + whisper + lamp strip lNAME.jpg
cd /home/user/lw_v3
python3 /home/user/lw_tools/qa3.py $1 "$2" $3 $3 $4 | cut -c1-160
python3 /home/user/lw_tools/skyfix.py ${1}_g.mp4 ${1}_k.mp4 seams/v01_a.png
python3 /tmp/claude-0/-home-user-ATHAR/bf9b7122-c083-55f7-8a76-f3452131c4d4/scratchpad/wt.py ${1}_k.mp4 2>&1 | grep -o "('[^']*', np.float64([0-9.]*)" | sed -E "s/\('([^']*)', np.float64\(([0-9.]*)/\1@\2/" | tr '\n' ' '; echo
ffmpeg -y -loglevel error -i ${1}_k.mp4 -vf "crop=640:300:640:0,fps=1,scale=320:-1,tile=4x2" l$1.jpg
ffmpeg -y -loglevel error -sseof -0.3 -i ${1}_k.mp4 -frames:v 1 -update 1 ${1}_klast.png
