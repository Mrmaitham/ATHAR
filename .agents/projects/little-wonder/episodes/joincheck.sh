#!/bin/bash
# usage: joincheck.sh prev.mp4 next.mp4  -> SSIM between last frame of prev and first frame of next (1.0 = identical)
a=$(mktemp --suffix=.png); b=$(mktemp --suffix=.png)
ffmpeg -v error -y -sseof -0.3 -i "$1" -update 1 -frames:v 1 -vf scale=640:360 "$a"
ffmpeg -v error -y -i "$2" -frames:v 1 -vf scale=640:360 "$b"
ffmpeg -i "$a" -i "$b" -lavfi ssim -f null - 2>&1 | grep -o "All:[0-9.]*"
rm -f "$a" "$b"
