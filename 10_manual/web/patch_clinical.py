# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# Clinical-report restyle of the dashboard (index.html): hospital-blue header, patient strip, interpretation, zones, trend alert,
# measured/reference table, A4 print. Idempotent (skips when 'clinical-report' marker is present).
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
s = open('index.html', encoding='utf-8').read()
if 'clinical-report' in s:
    raise SystemExit('already patched')


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:60], s.count(a))
    s = s.replace(a, b)


CSS = r'''<style>
/* clinical-report: hospital-style look (white cards, clinical blue, standard traffic-light status colours) */
:root{--bg:#eef2f7;--card:#fff;--ink:#14263d;--mute:#586b82;--acc:#0b5cab;--line:#d3dce7;--ok:#1b8a4b;--warn:#b7791f;--bad:#c0392b;--soft:#f5f8fc;
  --disp:"IBM Plex Sans Thai","Chakra Petch",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0e1621;--card:#16222f;--ink:#e8eef5;--mute:#93a4b8;--acc:#5aa8f0;--line:#2a3a4c;--ok:#3ccf7b;--warn:#e0a63a;--bad:#ef6a5b;--soft:#1b2a3a}}
:root[data-theme=dark]{--bg:#0e1621;--card:#16222f;--ink:#e8eef5;--mute:#93a4b8;--acc:#5aa8f0;--line:#2a3a4c;--ok:#3ccf7b;--warn:#e0a63a;--bad:#ef6a5b;--soft:#1b2a3a}
body{padding:0!important;background:var(--bg)!important;background-image:none!important;font-family:"IBM Plex Sans Thai",system-ui,sans-serif;font-size:15px}
body>header{max-width:none;margin:0;background:#0b5cab;color:#fff;border-radius:0;box-shadow:none;padding:12px max(16px,calc((100% - 1040px)/2));gap:10px}
body>header h1{font:600 18px var(--disp);text-transform:none;letter-spacing:0;display:flex;align-items:center;gap:10px;color:#fff}
body>header h1::before{content:"";width:22px;height:22px;border:2px solid #fff;border-radius:6px;flex:none;
  background:linear-gradient(#fff,#fff) center/6px 70% no-repeat,linear-gradient(#fff,#fff) center/70% 6px no-repeat}
body>header button,body>header select{background:rgba(255,255,255,.14)!important;color:#fff!important;border:1px solid rgba(255,255,255,.45)!important;border-radius:6px!important;padding:6px 12px}
body>header option{color:#14263d}
main{max-width:1040px;margin:0 auto;padding:18px 16px 44px;background:transparent;box-shadow:none;border-radius:0;gap:16px}
.card,.grid .card{background:var(--card)!important;border:1px solid var(--line)!important;border-bottom:1px solid var(--line)!important;border-radius:8px!important;box-shadow:0 1px 2px rgba(20,38,61,.06)!important;padding:16px 18px}
.grid .card{border-left:4px solid var(--acc)!important;padding:12px 14px}
.k{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);font-weight:600}
.v{font:600 28px var(--disp);font-variant-numeric:tabular-nums}
button,select{border-radius:6px!important}
button{border:1px solid var(--line);background:var(--card)}
button.pri{background:var(--acc)!important;border-color:var(--acc)!important;color:#fff;text-transform:none;letter-spacing:0;font-weight:600}
input{border-radius:6px!important;border:1px solid var(--line);box-shadow:none!important}
th{font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);background:var(--soft);font-weight:600}
th,td{border-bottom:1px solid var(--line)!important;font-variant-numeric:tabular-nums}
.tag{border-radius:4px!important;padding:2px 9px;font-weight:600}
#rep{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:16px}
#rep .wide,#rep .rhead{grid-column:1/-1}
.rhead{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:6px 18px;padding-bottom:12px;border-bottom:2px solid var(--acc)}
.rhead b{display:block;font-size:15px}.rhead span{font-size:11.5px;color:var(--mute);text-transform:uppercase;letter-spacing:.05em}
.rtitle{grid-column:1/-1;font:600 20px var(--disp);color:var(--acc)}
.interp{border-left:5px solid var(--ok);background:var(--soft);padding:10px 14px;border-radius:0 6px 6px 0}
.interp.warn{border-color:var(--warn)}.interp.bad{border-color:var(--bad)}
.interp b{font-size:16px}.interp p{margin:4px 0 0;color:var(--mute);font-size:13.5px}
.zbar{position:relative;height:16px;border-radius:8px;overflow:hidden;display:flex;margin:12px 0 6px}
.zbar i{display:block;height:100%}.zbar .r{background:var(--bad);width:41.7%}.zbar .y{background:var(--warn);width:25%}.zbar .g{background:var(--ok);flex:1}
.zmark{position:relative;height:0}.zmark u{position:absolute;top:-30px;width:3px;height:22px;background:var(--ink);text-decoration:none;transform:translateX(-1px)}
.zleg{display:flex;justify-content:space-between;font-size:11px;color:var(--mute)}
.big{font:600 34px var(--disp);font-variant-numeric:tabular-nums}
.alertbox{padding:8px 12px;border-radius:6px;background:var(--soft);border:1px solid var(--line);font-size:13.5px;margin-top:8px}
.alertbox.warn{border-color:var(--warn)}.alertbox.bad{border-color:var(--bad)}
#printTitle{display:none}
@media print{
  @page{size:A4;margin:14mm}
  body{background:#fff!important;color:#000}
  body>header,#cfg,#ble,#overviewCard,.noprint,#demoNote{display:none!important}
  main{padding:0;max-width:none}
  .card,.grid .card{box-shadow:none!important;break-inside:avoid;border-color:#999!important}
  .grid{grid-template-columns:repeat(4,1fr)}
  #printTitle{display:block}
  canvas{height:200px}
}
</style>
'''
rep('</head>', CSS + '<meta name="theme-color" content="#0b5cab">\n<link rel="manifest" href="manifest.webmanifest">\n<link rel="icon" href="icon-192.png">\n</head>')

# header title
rep('<h1 id="t_title">Spiro Dashboard</h1>', '<h1 id="t_title">Spiro Dashboard</h1>')

# patient fields in settings
rep('''    <label>Predicted FEV1 (L) — personal ref<input id="c_pred" type="number" step="0.1" placeholder="3.5"></label>''',
    '''    <label>Predicted FEV1 (L) — personal ref<input id="c_pred" type="number" step="0.1" placeholder="3.5"></label>
    <label>ชื่อ / HN (แสดงในรายงาน เก็บในเบราว์เซอร์นี้เท่านั้น)<input id="c_name" placeholder="HN 000000"></label>
    <label>อายุ (ปี)<input id="c_age" type="number" min="3" max="110"></label>
    <label>เพศ<select id="c_sex"><option value="">–</option><option value="M">ชาย / M</option><option value="F">หญิง / F</option></select></label>
    <label>ส่วนสูง (ซม.)<input id="c_ht" type="number" min="90" max="220"></label>''')

# report section after KPI grid
rep('<div class="grid" id="kpis"></div>', '''<div class="grid" id="kpis"></div>
  <section class="card" id="rep" hidden>
    <div class="rtitle" id="printTitle">รายงานสไปโรเมทรี / Spirometry report</div>
    <div class="rhead" id="repHead"></div>
    <div class="rb" id="repInterp"></div>
    <div class="rb" id="repZone"></div>
    <div class="rb" id="repTrend"></div>
    <div class="rb wide" id="repTbl"></div>
  </section>''')
rep('<p><button id="csv">CSV</button>', '<p class="noprint"><button id="csv">CSV</button> <button id="print" class="pri">พิมพ์รายงาน / Print</button>')

# JS: report renderer, called from render()
JS = r'''
/* ---------- clinical report (rule-based screening text; fixed-ratio 0.70 and GOLD %pred bands) ---------- */
function L(th,en){return lang==='th'?th:en}
function mean(a){return a.reduce((x,y)=>x+y,0)/a.length}
function renderReport(l,best){
  const p=+cfg.pred||0,pb=Math.max(...rows.map(r=>r.pef)),sx={M:L('ชาย','Male'),F:L('หญิง','Female')}[cfg.sex]||'–';
  $('rep').hidden=false;
  $('repHead').innerHTML=[[L('ผู้ป่วย / HN','Patient / HN'),cfg.name||'–'],[L('อายุ / เพศ','Age / sex'),(cfg.age?cfg.age+L(' ปี',' y'):'–')+' · '+sx],
    [L('ส่วนสูง','Height'),cfg.ht?cfg.ht+' cm':'–'],[L('เครื่อง','Device'),$('devSel').value||'–'],[L('ทดสอบล่าสุด','Last test'),new Date(l.ts).toLocaleString(lang==='th'?'th-TH':'en-GB')],
    [L('จำนวนครั้ง','Tests'),rows.length]].map(([a,b])=>`<div><span>${a}</span><b>${b}</b></div>`).join('');
  // interpretation
  let lvl='ok',title,sub;const ppc=p?100*l.fev1/p:0;
  if(l.ratio<70){
    if(p){const sev=ppc>=80?L('เล็กน้อย','mild'):ppc>=50?L('ปานกลาง','moderate'):ppc>=30?L('รุนแรง','severe'):L('รุนแรงมาก','very severe');lvl=ppc>=80?'warn':'bad';
      title=L('สงสัยรูปแบบการอุดกั้นทางเดินหายใจ ('+sev+')','Possible obstructive pattern ('+sev+')');sub=L(`FEV1/FVC ${l.ratio.toFixed(0)}% (< 70%) และ FEV1 ${ppc.toFixed(0)}% ของค่าที่กรอก แบ่งระดับตามแนว GOLD`,`FEV1/FVC ${l.ratio.toFixed(0)}% (< 70%), FEV1 ${ppc.toFixed(0)}% of entered reference; severity bands as GOLD`)}
    else{lvl=l.ratio<50?'bad':'warn';title=L('สงสัยรูปแบบการอุดกั้นทางเดินหายใจ','Possible obstructive pattern');sub=L(`FEV1/FVC ${l.ratio.toFixed(0)}% (< 70%) ใส่ค่า FEV1 คาดการณ์ในการตั้งค่า ⚙ เพื่อประเมินระดับ`,`FEV1/FVC ${l.ratio.toFixed(0)}% (< 70%). Enter a predicted FEV1 in ⚙ to grade severity`)}
  }else{
    title=L('ไม่พบรูปแบบการอุดกั้น','No obstructive pattern');
    sub=p&&ppc<80?L(`FEV1/FVC ${l.ratio.toFixed(0)}% ปกติ แต่ FEV1 ต่ำกว่า 80% ของค่าที่กรอก อาจเข้าได้กับปริมาตรปอดลดลง ต้องยืนยันด้วยการตรวจปอดเต็มรูปแบบ`,`Ratio normal but FEV1 below 80% of the entered reference; a restrictive process cannot be excluded — confirm with full PFT`):
      L(`FEV1/FVC ${l.ratio.toFixed(0)}% (≥ 70%) เครื่องนี้ประเมินภาวะปอดจำกัดการขยายตัวไม่ได้`,`FEV1/FVC ${l.ratio.toFixed(0)}% (≥ 70%). This device cannot assess restriction`);
    if(p&&ppc<80)lvl='warn'}
  $('repInterp').innerHTML=`<div class="k">${L('สรุปผลเบื้องต้น (คัดกรอง)','Preliminary interpretation (screening)')}</div><div class="interp ${lvl==='ok'?'':lvl}" style="margin-top:8px"><b>${title}</b><p>${sub}</p></div>`+
    (l.mp>=20?`<div class="alertbox warn">⚠ ${L('ที่เป่าใช้ครบ 20 ครั้ง ควรเปลี่ยนก่อนเป่าครั้งต่อไป','Mouthpiece reached 20 blows — replace before the next test')}</div>`:'');
  // personal-best zones
  const z=100*l.fev1/best,zc=z>=80?'ok':z>=50?'warn':'bad',zt=z>=80?L('โซนเขียว','Green zone'):z>=50?L('โซนเหลือง','Yellow zone'):L('โซนแดง','Red zone'),pz=100*l.pef/pb;
  $('repZone').innerHTML=`<div class="k">${L('เทียบค่าดีที่สุดของตัวเอง','Versus personal best')}</div>
    <div class="big" style="color:var(--${zc})">${z.toFixed(0)}% <small style="font:600 14px var(--disp)">${zt}</small></div>
    <div class="zbar"><i class="r"></i><i class="y"></i><i class="g"></i></div><div class="zmark"><u style="left:${Math.min(100,z/120*100)}%"></u></div>
    <div class="zleg"><span>0</span><span>50%</span><span>80%</span><span>120%</span></div>
    <p class="note">${L('FEV1 ล่าสุดเทียบกับ FEV1 สูงสุดที่เคยวัดได้ ('+best.toFixed(2)+' L) · PEF ล่าสุด '+pz.toFixed(0)+'% ของ PEF สูงสุด','Latest FEV1 vs best ever ('+best.toFixed(2)+' L) · latest PEF '+pz.toFixed(0)+'% of best PEF')}</p>`;
  // trend alert
  let tr;
  if(rows.length>=6){const a=mean(rows.slice(-3).map(r=>r.fev1)),b=mean(rows.slice(-6,-3).map(r=>r.fev1)),ch=100*(a-b)/b;
    tr=ch<=-10?['warn',L(`FEV1 เฉลี่ย 3 ครั้งล่าสุดลดลง ${Math.abs(ch).toFixed(0)}% จาก 3 ครั้งก่อนหน้า ควรติดตามและปรึกษาแพทย์ถ้ามีอาการ`,`Mean FEV1 of the last 3 tests fell ${Math.abs(ch).toFixed(0)}% vs the previous 3`)]:
       ch>=10?['ok',L(`FEV1 เฉลี่ยดีขึ้น ${ch.toFixed(0)}% จาก 3 ครั้งก่อนหน้า`,`Mean FEV1 improved ${ch.toFixed(0)}% vs the previous 3`)]:['ok',L(`FEV1 คงที่ (เปลี่ยน ${ch>0?'+':''}${ch.toFixed(0)}%)`,`FEV1 stable (${ch>0?'+':''}${ch.toFixed(0)}%)`)]}
  else tr=['',L('ต้องมีอย่างน้อย 6 ครั้งจึงจะประเมินแนวโน้ม','At least 6 tests are needed for a trend')];
  $('repTrend').innerHTML=`<div class="k">${L('แนวโน้ม','Trend')}</div><div class="alertbox ${tr[0]==='ok'?'':tr[0]}" style="margin-top:8px">${tr[1]}</div>
    <p class="note">${L('เกณฑ์เปลี่ยนแปลง ±10% เป็นค่าตั้งต้นของโครงงาน ยังไม่ใช่เกณฑ์ทางคลินิกที่รับรอง','The ±10% change threshold is a project default, not a validated clinical rule')}</p>`;
  // measured / reference table
  $('repTbl').innerHTML=`<table><tr><th>${L('พารามิเตอร์','Parameter')}</th><th>${L('ค่าที่วัด','Measured')}</th><th>${L('ค่าอ้างอิง','Reference')}</th><th>${L('ผล','Result')}</th></tr>
   <tr><td>FEV1 (L)</td><td>${l.fev1.toFixed(2)}</td><td>${p?p.toFixed(2)+L(' (ผู้ใช้กรอก)',' (entered)'):'–'}</td><td>${p?ppc.toFixed(0)+'%':'–'}</td></tr>
   <tr><td>FVC (L)</td><td>${l.fvc.toFixed(2)}</td><td>–</td><td>–</td></tr>
   <tr><td>FEV1/FVC (%)</td><td>${l.ratio.toFixed(0)}</td><td>≥ 70</td><td>${stat(l)}</td></tr>
   <tr><td>PEF (L/s)</td><td>${l.pef.toFixed(1)}</td><td>–</td><td>–</td></tr></table>
   <p class="note">${L('ไม่ใช่เครื่องมือแพทย์ที่ผ่านการรับรอง ผลใช้คัดกรองเบื้องต้นเท่านั้น ต้องยืนยันด้วยสไปโรเมทรีมาตรฐานและการประเมินของแพทย์','Not a certified medical device. Screening only — confirm with standard spirometry and clinical assessment.')}</p>`}
'''
rep("function kpi(k,v,u){", JS + "function kpi(k,v,u){")
rep("  $('tbl').innerHTML=h;draw()}", "  $('tbl').innerHTML=h;renderReport(l,best);draw()}")
rep("if(!rows.length){k.innerHTML='';$('tbl').innerHTML='';", "if(!rows.length){k.innerHTML='';$('tbl').innerHTML='';$('rep').hidden=true;")
# patient fields save/load
rep("auth:$('c_auth').value.trim(),pred:$('c_pred').value};",
    "auth:$('c_auth').value.trim(),pred:$('c_pred').value,name:$('c_name').value.trim(),age:$('c_age').value,sex:$('c_sex').value,ht:$('c_ht').value};")
rep("$('c_pred').value=cfg.pred||'';", "$('c_pred').value=cfg.pred||'';$('c_name').value=cfg.name||'';$('c_age').value=cfg.age||'';$('c_sex').value=cfg.sex||'';$('c_ht').value=cfg.ht||'';\n$('print').onclick=()=>window.print();\nif('serviceWorker' in navigator&&location.protocol.startsWith('http'))navigator.serviceWorker.register('sw.js').catch(()=>{});")
open('index.html', 'w', encoding='utf-8').write(s)
print('patched index.html')
