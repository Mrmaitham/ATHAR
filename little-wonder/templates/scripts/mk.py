import subprocess,sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F="../op/fonts/Baloo.ttf"; G="../build/g3/"
def card(text,col,fname,maxw=1000,size=104):
    while True:
        f=ImageFont.truetype(F,size); f.set_variation_by_name("ExtraBold")
        b=ImageDraw.Draw(Image.new("RGBA",(10,10))).textbbox((0,0),text,font=f)
        if b[2]-b[0]+40<=maxw or size<50: break
        size-=4
    w,h=b[2]-b[0],b[3]-b[1]; W,H=w+40,h+60
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img); x,y=20-b[0],30-b[1]
    d.text((x,y),text,font=f,fill=col+(255,),stroke_width=10,stroke_fill=(255,255,255,255))
    sh=Image.new("RGBA",img.size,(0,0,0,0)); ImageDraw.Draw(sh).text((x,y+6),text,font=f,fill=(0,0,0,120),stroke_width=10,stroke_fill=(0,0,0,120))
    Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)),img).save(fname)
def build(name,files,title,col,logo=True):
    FPS=24;D=6
    N=[int(subprocess.run(["ffprobe","-v","error","-count_packets","-select_streams","v","-show_entries","stream=nb_read_packets","-of","csv=p=0",f],capture_output=True,text=True).stdout) for f in files]
    fc=[];args=[]
    for i,f in enumerate(files):
        args+=["-i",f]; a=D//2 if i else 0; b=D//2 if i<len(files)-1 else 0
        fc.append(f"[{i}:v]fps={FPS},settb=1/{FPS},format=yuv420p,tpad=start={a}:start_mode=clone:stop={b}:stop_mode=clone,setpts=PTS-STARTPTS[p{i}]")
    P=[N[i]+(D//2 if i else 0)+(D//2 if i<len(files)-1 else 0) for i in range(len(files))]
    acc=0;prev="p0"
    for i in range(len(files)-1):
        acc+=P[i]; fc.append(f"[{prev}][p{i+1}]xfade=transition=fade:duration={D/FPS}:offset={(acc-i*D-D)/FPS:.6f}[x{i}]"); prev=f"x{i}"
    fc.append("".join(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{N[i]/FPS:.6f},asetpts=PTS-STARTPTS[a{i}];" for i in range(len(files)))+"".join(f"[a{i}]" for i in range(len(files)))+f"concat=n={len(files)}:v=0:a=1[aout]")
    subprocess.run(["ffmpeg","-v","error","-y"]+args+["-filter_complex",";".join(fc),"-map",f"[{prev}]","-map","[aout]","-c:v","libx264","-crf","16","-preset","medium","-c:a","aac","-b:a","192k",f"h_{name}.mp4"],check=True)
    Dur=sum(N)/FPS; card(title,col,f"cap_{name}.png")
    lg="[1:v]format=rgba[lg];[v1][lg]overlay=(W-w)/2:170[v2]" if logo else "[v1]null[v2]"
    s=Dur-4
    flt=(f"[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.08:saturation=1.2[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2:shortest=1[v1];{lg};"
         f"[2:v]format=rgba,fade=t=in:st=0.3:d=0.4:alpha=1[c1];[v2][c1]overlay=(W-w)/2:1300[v3];"
         f"[3:v]format=rgba,fade=t=in:st={s:.2f}:d=0.5:alpha=1[c2];[v3][c2]overlay=(W-w)/2:1480:enable='gte(t,{s:.2f})'[v]")
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"h_{name}.mp4","-loop","1","-framerate","24","-t",f"{Dur:.3f}","-i","logo820.png","-loop","1","-framerate","24","-t",f"{Dur:.3f}","-i",f"cap_{name}.png","-loop","1","-framerate","24","-t",f"{Dur:.3f}","-i","cap2.png","-filter_complex",flt,"-map","[v]","-map","0:a","-c:v","libx264","-crf","20","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart","-r","24",f"EP01_short_{name}.mp4"],check=True)
    print(name,round(Dur,1))
g=lambda *n:[G+f"{i:03d}.mp4" for i in n]
S={
 "meet_the_family":(["../op/intro_named2.mp4"],"Meet the Little Wonder Family!",(227,93,151),False),
 "my_turn":(g(11,12,14,15),"My Turn! No, MINE!",(236,98,150),True),
 "oh_no":(g(27,28,29,30,31),"Oh No... The Swing!",(58,128,210),True),
 "hoors_rose":(g(35,36,37,38,39,40),"Hoor's Little Rose",(240,110,165),True),
 "grandmas_question":(g(49,50,51,52,53),"Grandma's Big Question",(140,90,185),True),
 "count_to_ten":(g(59,60,61,62,63),"Count to Ten... Your Turn!",(214,160,50),True),
 "im_flying":(g(65,66,67),"I'm Flying!",(58,128,210),True),
 "big_wonders":(g(71,72,73,74),"Little Hearts, BIG WONDERS!",(227,93,151),True),
}
for k in sys.argv[1:] or S: build(k,*S[k])
