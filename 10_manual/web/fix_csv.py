# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
import os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
p = open('patch_dash.py', encoding='utf-8').read()
p = p.replace("b = s.index('\\n}', s.index('catch(e)', a)) + 2", "b = s.index('render()}', s.index('catch(e)', a)) + len('render()}')")
open('patch_dash.py', 'w', encoding='utf-8').write(p)
GOOD = ("$('csv').onclick=async()=>{const t='time,fev1_L,fvc_L,ratio_pct,pef_Lps,bat\\n'+rows.map(r=>[new Date(r.ts).toISOString(),r.fev1,r.fvc,r.ratio,r.pef,r.bat??''].join(',')).join('\\n');\n"
        "  try{await navigator.clipboard.writeText(t);$('status').textContent='copied CSV'}catch(e){$('status').textContent='copy blocked'}};")
for fn in ('index.html', 'dashboard_artifact.html'):
    s = open(fn, encoding='utf-8').read()
    a = s.index("$('csv').onclick=")
    b = s.index("copy blocked'}};", a) + len("copy blocked'}};")
    s = s[:a] + GOOD + s[b:]
    open(fn, 'w', encoding='utf-8').write(s)
print('ok')
