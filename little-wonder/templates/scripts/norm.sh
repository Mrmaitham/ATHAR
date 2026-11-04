#!/bin/bash
# norm in out [extra vf] [trim]
in=$1; out=$2; vfx=$3; tr=$4
has=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$in")
VF="scale=1280:720,fps=24,format=yuv420p${vfx:+,$vfx}"
T=${tr:+-t $tr}
if [ -n "$has" ]; then
ffmpeg -v error -y -i "$in" $T -vf "$VF" -af "aresample=48000,aformat=channel_layouts=stereo${AFX:+,$AFX}" -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest "$out"
else
ffmpeg -v error -y -i "$in" -f lavfi -i anullsrc=r=48000:cl=stereo $T -vf "$VF" -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k -shortest "$out"
fi
