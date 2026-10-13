#!/bin/bash
# usage: houselamps.sh CLIP(without .mp4) x y r [x y r ...]  -> CLIP_l.mp4 with those lamps switched off.
# Lamp positions are in CLIP's LAST frame (find them with findlamps.py); camtrack follows the camera from there.
cd /home/user/lw_v3; C=$1; shift
N=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $C.mp4)
python3 /home/user/lw_tools/camtrack.py $C.mp4 $((N-1)) 480 40 1240 300 > /dev/null
TRACK=$C.mp4.track.npy python3 /home/user/lw_tools/pathlamp.py $C.mp4 ${C}_l.mp4 "$@"
