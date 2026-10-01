#!/bin/bash
# Join all scene files, add the BY ATHAR badge, normalise loudness, export 1080p.
set -e
cd "$(dirname "$0")"
python3 -c "
import json
ids=[s['id'] for s in json.load(open('scenes.json'))]
open('scenes_list.txt','w').write(''.join(f\"file 'scenes_mp4/{i}.mp4'\n\" for i in ids))"
ffmpeg -y -v error -f concat -safe 0 -i scenes_list.txt -c copy joined.mp4
ffmpeg -y -v error -i joined.mp4 -loop 1 -i overlays/badge.png \
  -filter_complex "[1:v]format=rgba[b];[0:v][b]overlay=0:0:shortest=1:format=auto[v];[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart calciopoli_2006_final.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 calciopoli_2006_final.mp4
