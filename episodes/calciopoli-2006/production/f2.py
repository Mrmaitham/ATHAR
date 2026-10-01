import sys,subprocess
B="https://d8j0ntlcm91z4.cloudfront.net/user_3GPnMIBf9MTKG0k3nXluooyuyoI/hf_20261001_"
lines=[l.split() for l in sys.stdin.read().strip().split('\n') if l.strip()]
txt=",".join('{"index":%s,"job_id":"x","status":"completed","type":"image","model":"m","result_url":"%s%s_%s.png"}'%(i,B,t,j) for i,t,j in lines)
subprocess.run(["python3","fetch_imgs.py",sys.argv[1]],input=txt,text=True)
