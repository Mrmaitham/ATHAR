#!/bin/bash
# usage: qc/chars.sh NN — side-by-side of the lineup reference and shot NN's last frame (for a by-eye costume/hair check)
S=/tmp/claude-0/-home-user-ATHAR/808f4051-f44a-5338-a794-9ee8e53308d1/scratchpad
python3 -c "
from PIL import Image
r=Image.open('../../references/characters_lineup_clean.png').convert('RGB').resize((1280,724))
f=Image.open('qc/shot$1_last.png').convert('RGB').resize((1280,720))
o=Image.new('RGB',(1280,1444));o.paste(r,(0,0));o.paste(f,(0,724));o.save('$S/chars_$1.png')"
echo $S/chars_$1.png
