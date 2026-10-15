# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for fn in ('index.html', 'dashboard_artifact.html'):
    s = open(fn, encoding='utf-8').read()
    if 'localRows' in s:
        continue
    # 1) local history helpers + merge into fillSel
    s = s.replace("let byDev={};", """let byDev={};
function localRows(){try{return JSON.parse(localStorage.localSessions||'[]')}catch(e){return []}}
function saveLocal(r){try{const a=localRows();a.push(r);localStorage.localSessions=JSON.stringify(a.slice(-500))}catch(e){}}""", 1)
    s = s.replace("function fillSel(){const s=$('devSel')", "function fillSel(){const L=localRows();if(L.length&&!demo)byDev={...byDev,'local-ble':L};const s=$('devSel')", 1)
    # 2) no cloud configured -> still show local history instead of an empty page
    s = s.replace("if(!cfg.db||!ids.length){$('status').textContent=tt('nodata');$('cfg').style.display='grid';return}",
                  "if(!cfg.db||!ids.length){byDev={};$('status').textContent='local';fillSel();if(!localRows().length){$('status').textContent=tt('nodata')}return}", 1)
    # 3) save every BLE result locally
    s = s.replace("$('bPef').textContent=(+p[4]).toFixed(1)+' L/s'}});",
                  "$('bPef').textContent=(+p[4]).toFixed(1)+' L/s';saveLocal({ts:Date.now(),fvc:+p[1],fev1:+p[2],ratio:+p[3],pef:+p[4]});if(!cfg.db)load()}});", 1)
    # 4) CSV: real download (works on the hosted site), clipboard fallback
    a = s.index("$('csv').onclick="); b = s.index("copy blocked'}};", a) + len("copy blocked'}};")
    s = s[:a] + """$('csv').onclick=async()=>{const t='time,fev1_L,fvc_L,ratio_pct,pef_Lps,bat\\n'+rows.map(r=>[new Date(r.ts).toISOString(),r.fev1,r.fvc,r.ratio,r.pef,r.bat??''].join(',')).join('\\n');
  try{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/csv'}));a.download='spirometer.csv';a.click();$('status').textContent='CSV'}
  catch(e){try{await navigator.clipboard.writeText(t);$('status').textContent='copied CSV'}catch(e2){$('status').textContent='copy blocked'}}};""" + s[b:]
    s = s.replace('Copy CSV', 'CSV')
    s = s.replace('ยังไม่ได้ทดสอบกับเครื่องจริง</p>', 'ผลการเป่าที่รับผ่านบลูทูธจะถูกบันทึกในเบราว์เซอร์นี้ (ไม่ต้องมีฐานข้อมูล) ยังไม่ได้ทดสอบกับเครื่องจริง</p>', 1)
    open(fn, 'w', encoding='utf-8').write(s)
    print('patched', fn)
