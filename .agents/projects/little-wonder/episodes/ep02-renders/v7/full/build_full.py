import subprocess, os
V='/home/user/ATHAR/.agents/projects/little-wonder/episodes/ep02-renders/v7/ep02_v7_'
S='/home/user/lw_edit/intro_song.mp4'
def sh(n): return V+'shot%s.mp4'%(n if isinstance(n,str) else '%02d'%n)
def card(n): return V+'card_day%d.mp4'%n
D1={1:.15,2:.2,3:.3,4:.3}
def run(name, items):
    # items: (file,label,dissolve_after)
    a=[name+'.mp4']
    labs=[]
    for i,(f,l,d) in enumerate(items):
        a.append(f); labs.append(l)
        if i<len(items)-1: a.append(str(d))
    a+=['--num','--labels='+','.join(labs)]
    subprocess.run(['python3','/home/user/lw_tools/cut.py']+a,check=True)
A=[('hook_a.mp4','H',.4),(V+'shot40.mp4','H',.4),(S,'',.4)]
for n in range(1,36):
    d=D1.get(n,.25)
    if n==10: d=.3
    A.append((sh(n),str(n),d))
    if n==10: A.append((sh('10b_bridge'),'10b',.3))
A[-1]=(A[-1][0],A[-1][1],0)
B=[(card(2),'',.3),(sh(36),'36',.25),(sh(37),'37',.3),(card(3),'',.3),(sh(38),'38',.3),(sh('38b_bridge'),'38b',.3),
   (card(4),'',.3),(sh(39),'39',.25),(sh(40),'40',.25),(sh(41),'41',.3),(sh('41b_bridge'),'41b',.3),(card(5),'',.3)]
B+=[(sh(n),str(n),.25) for n in range(42,60)]+[(sh(60),'60',0)]
C=[(sh(61),'61',.2),(sh('61b_bridge'),'61b',.3)]+[(sh(n),str(n),.25) for n in range(62,70)]+[(sh(70),'70',.3)]
import sys
which=sys.argv[1]
run(which,{'A':A,'B':B,'C':C}[which])
