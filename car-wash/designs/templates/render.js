// usage: node render.js <data.json> <out.png>
const fs=require('fs'),path=require('path');const {chromium}=require('playwright');
(async()=>{
 const d=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 let h=fs.readFileSync(path.join(__dirname,'package.html'),'utf8');
 const li=a=>a.map(x=>`<li>${x}</li>`).join('');
 const tier=`<span>المستوى</span>`+[1,2,3,4,5].map(i=>`<i class="${i<=d.tier?'on':''}"></i>`).join('');
 h=h.replace('{{AR_NAME}}',d.ar_name).replace('{{EN_NAME}}',d.en_name).replace('{{TIER}}',tier)
    .replace('{{AR_ITEMS}}',li(d.ar_items)).replace('{{EN_ITEMS}}',li(d.en_items)).replace('{{P1}}',d.saloon).replace('{{P2}}',d.suv);
 const tmp=path.join(__dirname,'_render.html');fs.writeFileSync(tmp,h);
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1080},deviceScaleFactor:2});
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
 await p.screenshot({path:process.argv[3]});await b.close();fs.unlinkSync(tmp);
})();
