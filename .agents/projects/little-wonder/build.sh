#!/bin/bash
# Ep02 v3 full episode: hook -> intro song -> shots 1-79 -> outro. Segments split at plain cuts.
cd /home/user/lw_v3; C=/home/user/lw_tools/cut.py; O=full/ep; S=/home/user/lw_edit/intro_song.mp4
MODE=$1   # clean | num
seg(){ out=$1; lab=$2; shift 2; if [ "$MODE" = num ]; then python3 $C $O/${MODE}_$out.mp4 "$@" --num --labels=$lab; else python3 $C $O/${MODE}_$out.mp4 "$@"; fi; }
seg A "H,H,,1,2,3,4,5,6,7,8,9,10,11,12,13,,14,15" v27d_s.mp4 0.4 v37_v.mp4 0.4 $S 0.4 v01.mp4 0 v02_f2_k.mp4 0 v03_f2_k.mp4 0.5 v04_u_k.mp4 0 v05_u_k.mp4 0.3 v06_u_k.mp4 0 v07_u_k.mp4 0 v08_u_k.mp4 0 v09_s_k.mp4 0 v10_u_k.mp4 0 v11_u.mp4 0 v12_u.mp4 0 v13_s.mp4 0 trans13.mp4 0 v14_v.mp4 0 v15b_k.mp4 &
seg B "16,17,18,19,20,21,22,23,24,25" v16_k.mp4 0 v17d_s.mp4 0.5 v18e_k.mp4 0 v19_k.mp4 0 v20d_k.mp4 0.5 v21_k.mp4 0 v22_k.mp4 0 v23_a.mp4 0 v24b_s.mp4 0 v25b_s.mp4 &
seg C "26,27,28,29,30,31,32,33,34,35,36,37,38,39,40" v26b_u.mp4 0 v27d_s.mp4 0 v28_k.mp4 0 v29_k.mp4 0 v30_u.mp4 0 v31_u.mp4 0 v32b_v.mp4 0 v33_k.mp4 0 v34_s.mp4 0 v35b_s.mp4 0 v36_s.mp4 0 v37_v.mp4 0 v38_k.mp4 0 v39b_k.mp4 0 v40b_v.mp4 &
wait
seg D "41,,42,43,,44,,45,46,47,,48,49,50" v41_k.mp4 0 transD2c.mp4 0 v42b_k.mp4 0 v43_u.mp4 0 transD3b.mp4 0 v44c_u.mp4 0 transD4b.mp4 0 v45f_u.mp4 0 v46d_u.mp4 0 v47c_k.mp4 0 transD5d.mp4 0 v48c_u.mp4 0.4 v49c_k.mp4 0 v50_u.mp4 &
seg E "51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,,67,,68,69,70,71-72,,73,74,75,76,77,78,79,80" v51d_u.mp4 0 v52b_k.mp4 0 v53d_k.mp4 0 v54b_k.mp4 0 v55a_k.mp4 0 v56h_s.mp4 0 v57d_s.mp4 0 v58d_k.mp4 0 v59b_k.mp4 0.4 v60p_k.mp4 0.4 v61b_k.mp4 0.4 v62b_k.mp4 0.4 v63g_k.mp4 0.4 v64b_k.mp4 0.4 v65d_k.mp4 0.4 v66a_k.mp4 0.4 transD2g.mp4 0.4 v67c_k.mp4 0.4 transD4g.mp4 0.4 v68b_k.mp4 0.4 v69c_k.mp4 0.4 v70Ab_h.mp4 0.4 v7172W_a.mp4 0.4 transD7g.mp4 0.4 v73d_k.mp4 0.4 v74b_k.mp4 0.4 v75d_k.mp4 0.4 v76b_k.mp4 0.4 v77a_k.mp4 0.4 v78d_k.mp4 0.4 v79b_s.mp4 0.4 v80O_a.mp4 &
wait
printf "file '%s'\n" ${MODE}_A.mp4 ${MODE}_B.mp4 ${MODE}_C.mp4 ${MODE}_D.mp4 ${MODE}_E.mp4 > $O/${MODE}_list.txt
ffmpeg -v error -y -f concat -safe 0 -i $O/${MODE}_list.txt -c copy -movflags +faststart $O/ep02_v3_${MODE}.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 $O/ep02_v3_${MODE}.mp4
