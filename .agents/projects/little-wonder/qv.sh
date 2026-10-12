#!/bin/bash
# usage: qv.sh NAME URL PREV_LAST KEYEND  -> qa4 + contact sheet scratch/tNAME.jpg
bash /home/user/lw_tools/qa4.sh "$@"
cd /home/user/lw_v3; ffmpeg -v error -y -i ${1}_k.mp4 -vf "fps=2,scale=426:-1,tile=4x4" -frames:v 1 /tmp/claude-0/-home-user-ATHAR/bf9b7122-c083-55f7-8a76-f3452131c4d4/scratchpad/t$1.jpg
