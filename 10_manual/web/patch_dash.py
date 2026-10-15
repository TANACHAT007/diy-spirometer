# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
import re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
CSS = '''<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Sans+Thai:wght@400;500;600&display=swap">
<style>
/* lab-grid look shared with the product page: grey ruled grid, orange accent, squared type */
:root{--bg:#e6e6e6;--card:#f4f4f4;--ink:#161616;--mute:#5d5d5d;--acc:#f25c00;--line:#bdbdbd;--pop:none;--disp:"Chakra Petch","IBM Plex Sans Thai",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#161616;--card:#232323;--ink:#f0f0f0;--mute:#a0a0a0;--acc:#ff7a1a;--line:#3a3a3a;--pop:none}}
:root[data-theme=dark]{--bg:#161616;--card:#232323;--ink:#f0f0f0;--mute:#a0a0a0;--acc:#ff7a1a;--line:#3a3a3a;--pop:none}
body{font-family:"IBM Plex Sans Thai","Chakra Petch",system-ui,sans-serif;background:var(--bg);background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:96px 96px}
h1{text-transform:uppercase;letter-spacing:.02em}
header,main{background:var(--bg);box-shadow:0 0 0 1px var(--line);padding-inline:clamp(12px,2.5vw,28px)}
button,input,select,.card,.tag{box-shadow:none!important}
button,select,.tag{border-radius:99px!important}
input{border-radius:16px!important}
.card,.grid .card{border-radius:24px!important}
header,main{border-radius:30px}
button,select{border:1px solid var(--ink);background:var(--card)}
button.pri{background:var(--acc)!important;color:#fff;border-color:var(--acc);text-transform:uppercase;letter-spacing:.05em}
.card,.grid .card{background:var(--card)!important;border:1px solid var(--line);border-bottom:4px solid var(--acc)}
.v{font-family:var(--disp)} .k{text-transform:uppercase;letter-spacing:.08em}
.tag{padding:2px 10px}
#ble{display:grid;gap:10px}
#ble canvas{height:170px;border:1px solid var(--line);background:var(--bg)}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
</style>'''
LIVEHTML = '''
  <section class="card" id="overviewCard" hidden><div class="k" id="t_over">ภาพรวมทุกเครื่อง (ครู-แพทย์)</div><div style="overflow:auto"><table id="over"></table></div></section>
  <section class="card" id="ble"><div class="row"><div class="k" style="margin-right:auto" id="t_ble">เป่าสดผ่านบลูทูธ (Bluetooth)</div><button id="bleBtn" class="pri">เชื่อมต่อเครื่อง</button></div>
    <canvas id="bleCv" width="900" height="170"></canvas><p class="note" id="bleMsg">ต้องใช้เบราว์เซอร์ที่รองรับ Web Bluetooth (Chrome/Edge บนคอม/Android) และเปิดหน้านี้จากเว็บที่โฮสต์เอง ไม่ใช่ในกรอบพรีวิว ยังไม่ได้ทดสอบกับเครื่องจริง</p>
    <div class="row"><span class="k">FVC</span><b id="bFvc">–</b><span class="k">FEV1</span><b id="bFev">–</b><span class="k">PEF</span><b id="bPef">–</b></div></section>'''
NEWLOAD = '''async function load(){
  if(demo){byDev={'demo-01':makeDemo(),'demo-02':makeDemo().map(r=>({...r,fev1:+(r.fev1*.72).toFixed(2),ratio:+(r.ratio*.78).toFixed(1)}))};
    $('status').textContent='demo';$('demoNote').hidden=false;fillSel();return}
  $('demoNote').hidden=true;
  const ids=devList();
  if(!cfg.db||!ids.length){$('status').textContent=tt('nodata');$('cfg').style.display='grid';return}
  try{const out={};
    for(const id of ids){const u=`${cfg.db.replace(/\\/$/,'')}/devices/${encodeURIComponent(id)}/sessions.json`+(cfg.auth?`?auth=${cfg.auth}`:'');
      const j=await (await fetch(u)).json();
      out[id]=Object.values(j||{}).filter(r=>r&&typeof r.fev1==='number').sort((a,b)=>a.ts-b.ts)}
    byDev=out;$('status').textContent=new Date().toLocaleTimeString()+' ✔';fillSel();
  }catch(e){$('status').textContent='offline: '+e.message;render()}
}'''
JS = '''
/* ---------- multi-device + doctor overview ---------- */
let byDev={};
function devList(){return (cfg.dev||'').split(',').map(s=>s.trim()).filter(Boolean)}
function renderOverview(){
  const card=$('overviewCard'),doc=$('role').value==='doctor';card.hidden=!doc;if(!doc)return;
  let h='<tr><th>Device</th><th>#</th><th>FEV1</th><th>FEV1/FVC %</th><th>PEF</th><th></th></tr>';
  for(const id of Object.keys(byDev)){const a=byDev[id],l=a[a.length-1];
    h+=l?`<tr data-dev="${id}" style="cursor:pointer"><td>${id}</td><td>${a.length}</td><td>${l.fev1.toFixed(2)}</td><td>${l.ratio.toFixed(0)}</td><td>${l.pef.toFixed(1)}</td><td>${stat(l)}</td></tr>`
      :`<tr><td>${id}</td><td>0</td><td colspan="4">–</td></tr>`}
  $('over').innerHTML=h;
  $('over').querySelectorAll('tr[data-dev]').forEach(tr=>tr.onclick=()=>{$('devSel').value=tr.dataset.dev;pickDev()})}
function pickDev(){rows=byDev[$('devSel').value]||[];render()}
function fillSel(){const s=$('devSel'),ids=Object.keys(byDev),cur=s.value;
  s.innerHTML=ids.map(i=>`<option>${i}</option>`).join('');if(ids.includes(cur))s.value=cur;s.hidden=ids.length<2;pickDev();renderOverview()}
/* ---------- Web Bluetooth live view (UUIDs match the firmware) ---------- */
const NUS='6e400001-b5a3-f393-e0a9-e50e24dcca9e',LIVE_C='6e400002-b5a3-f393-e0a9-e50e24dcca9e',RES_C='6e400003-b5a3-f393-e0a9-e50e24dcca9e';
let bl=[];
function bleDraw(){const c=$('bleCv'),g=c.getContext('2d'),w=c.width,h=c.height;g.clearRect(0,0,w,h);
  const css=getComputedStyle(document.documentElement);g.strokeStyle=css.getPropertyValue('--line');g.fillStyle=css.getPropertyValue('--mute');g.font='12px sans-serif';
  for(let f=0;f<=10;f+=2){const y=h-14-(h-24)*f/10;g.beginPath();g.moveTo(30,y);g.lineTo(w-6,y);g.stroke();g.fillText(f,6,y+4)}
  if(!bl.length)return;g.strokeStyle=css.getPropertyValue('--acc');g.lineWidth=2.5;g.beginPath();
  const mt=Math.max(6000,bl[bl.length-1][0]);bl.forEach((p,i)=>{const x=30+(w-36)*p[0]/mt,y=h-14-(h-24)*Math.min(10,p[1])/10;i?g.lineTo(x,y):g.moveTo(x,y)});g.stroke()}
$('bleBtn').onclick=async()=>{
  const m=$('bleMsg');
  if(!navigator.bluetooth){m.textContent='เบราว์เซอร์นี้ไม่รองรับ Web Bluetooth หรือถูกบล็อกในหน้านี้';return}
  try{
    const d=await navigator.bluetooth.requestDevice({filters:[{services:[NUS]}]});
    const s=await (await d.gatt.connect()).getPrimaryService(NUS);
    const cl=await s.getCharacteristic(LIVE_C),cr=await s.getCharacteristic(RES_C),dec=new TextDecoder();
    cl.addEventListener('characteristicvaluechanged',e=>{const p=dec.decode(e.target.value).split(',').map(Number);if(p.length>=3){bl.push([p[0],p[1],p[2]]);bleDraw();$('bFvc').textContent=p[2].toFixed(2)+' L'}});
    cr.addEventListener('characteristicvaluechanged',e=>{const p=dec.decode(e.target.value).split(',');if(p[0]==='R'){$('bFvc').textContent=(+p[1]).toFixed(2)+' L';$('bFev').textContent=(+p[2]).toFixed(2)+' L';$('bPef').textContent=(+p[4]).toFixed(1)+' L/s'}});
    await cl.startNotifications();await cr.startNotifications();bl=[];bleDraw();
    m.textContent='เชื่อมต่อแล้ว: '+d.name+' — กดปุ่มที่เครื่องแล้วเป่า';$('bleBtn').textContent='เชื่อมต่อแล้ว';
  }catch(e){m.textContent='เชื่อมต่อไม่สำเร็จ: '+e.message}};
bleDraw();
'''
for fn in ('index.html', 'dashboard_artifact.html'):
    s = open(fn, encoding='utf-8').read()
    if 'overviewCard' in s:
        continue
    s = s.replace('</style>', '</style>\n' + CSS, 1)
    s = s.replace('<div class="grid" id="kpis"></div>', LIVEHTML + '\n  <div class="grid" id="kpis"></div>', 1)
    s = s.replace('<select id="role">', '<select id="devSel" hidden></select> <select id="role">', 1)
    a = s.index('async function load(){')
    b = s.index('render()}', s.index('catch(e)', a)) + len('render()}')
    s = s[:a] + NEWLOAD + s[b:]
    old = "$('role').onchange=()=>{$('gear').style.display=$('role').value==='doctor'?'':'none'};"
    assert old in s, 'role handler'
    s = s.replace(old, "$('role').onchange=()=>{$('gear').style.display=$('role').value==='doctor'?'':'none';renderOverview()};")
    s = s.replace("$('role').onchange();applyText();load();", JS + "\n$('devSel').onchange=pickDev;$('role').onchange();applyText();load();")
    s = s.replace('<label>Device ID<input', '<label>Device ID (คั่นหลายเครื่องด้วย ,)<input')
    open(fn, 'w', encoding='utf-8').write(s)
    print(fn, len(s))
