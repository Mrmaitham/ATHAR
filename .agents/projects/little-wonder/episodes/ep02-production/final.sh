#!/bin/bash
# Assemble Little Wonder Ep2 final
C=/home/user/lw_chain; E=/home/user/lw_edit
L=()
L+=($C/s36.mp4 $C/s35.mp4)            # hook
L+=($E/intro_song.mp4)
L+=($C/s01.mp4 $C/s02.mp4 $C/s03.mp4 $C/s04.mp4 $C/s05t.mp4)
for n in $(seq 6 35); do L+=($(printf "$C/s%02d.mp4" $n)); done
L+=($E/card_day2.mp4 $C/s36.mp4 $C/s37.mp4 $E/card_day3.mp4 $C/s38.mp4 $E/card_day4.mp4 $C/s39.mp4 $C/s40.mp4 $C/s41.mp4)
L+=($E/card_day5.mp4); for n in $(seq 42 60); do L+=($C/s$n.mp4); done
L+=($E/card_next.mp4 $C/s61.mp4 $E/card_few.mp4); for n in $(seq 62 66); do L+=($C/s$n.mp4); done
L+=($E/card_week.mp4); for n in $(seq 67 73); do L+=($C/s$n.mp4); done
L+=($E/outro.mp4)
echo "${#L[@]} clips"
/home/user/lw_tools/join.sh "$1" "${L[@]}"
