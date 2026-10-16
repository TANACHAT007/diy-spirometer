# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# Adds login guard + roles (doctor / patient; admin has its own page) to clinic.html. Reads clinic_pre_roles.bak -> writes clinic.html.
s = open('clinic_pre_roles.bak', encoding='utf-8').read()


def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)


# 1 script -> module + core.js
rep('<script>\nconst $=id=>document.getElementById(id);', '<script src="core.js"></script>\n<script type="module">\nconst $=id=>document.getElementById(id);')

# 2 header chip + logout
rep('<button class="tbtn" id="lang">TH/EN</button>', '<span class="pill on" id="who" style="display:none"><i></i><span id="whoT"></span></span><button class="tbtn" id="lang">TH/EN</button>')
rep('<button class="tbtn" id="theme">◐</button>\n</div></header>', '<button class="tbtn" id="theme">◐</button><button class="tbtn" id="logout" style="display:none"></button>\n</div></header>')

# 3 doctor-code box + patient profile tab
rep('<section class="tab" id="tab-patients">\n', '<section class="tab" id="tab-patients">\n  <div class="alert" id="docCode" style="margin-bottom:14px;display:none"></div>\n')
rep('<!-- ============ DEVICE ============ -->', '<!-- ============ MY PROFILE (patient) ============ -->\n<section class="tab" id="tab-me"><div id="meBox"></div></section>\n\n<!-- ============ DEVICE ============ -->')

# 4 state with per-user keys + role boot
OLD = "let patients=load('sp_patients',[]),tests=load('sp_tests',[]),activeP=localStorage.sp_active||'',cfg=load('sp_cfg',{});"
rep(OLD, r"""const DEMO_Q=/[?&]demo/.test(location.search);
const ME=DEMO_Q?{id:'demo',role:'doctor',name:'Example',status:'active',code:'DR-DEMO',meta:{}}:await SP.Auth.require(['doctor','patient']);
if(!DEMO_Q&&ME.status!=='active'){document.body.innerHTML='<p style="padding:48px 20px;text-align:center;font:16px sans-serif">บัญชียังไม่ได้รับอนุมัติจากผู้ดูแลระบบ · Account awaiting admin approval<br><br><a href="login.html">login</a></p>';throw new Error('pending')}
const ROLE=ME.role,NS='_'+ME.id,PK='sp_patients'+NS,TK='sp_tests'+NS,AK='sp_active'+NS,CK='sp_cfg'+NS;
let patients=load(PK,[]),tests=load(TK,[]),activeP=localStorage[AK]||'',cfg=load(CK,{});""")
rep("const fmt=(v,d=2)=>v==null||isNaN(v)?'–':(+v).toFixed(d);", r"""const fmt=(v,d=2)=>v==null||isNaN(v)?'–':(+v).toFixed(d);
/* accounts: a patient account is a "linked" patient record; its tests live in the shared store (SP.Tests) */
const recOf=(u,hn)=>{const m=u.meta||{};return{id:u.id,hn:hn,name:u.name,sex:m.sex||'M',age:m.age||'',ht:m.ht||'',wt:m.wt||'',smk:m.smk||'0',pf:m.pf||'',pv:m.pv||'',note:m.note||'',linked:true}};
const persistTests=()=>save(TK,tests.filter(x=>!x.linked));
if(!DEMO_Q){
  if(ROLE==='patient'){patients=[recOf(ME,'')];patients[0].self=true;activeP=ME.id;tests=(await SP.Tests.forPatient(ME.id)).map(x=>({...x,pid:ME.id,linked:true}))}
  else{const us=(await SP.Users.list()).filter(u=>u.role==='patient'&&u.doctorId===ME.id),ids=us.map(u=>u.id);
    patients=patients.concat(us.map(u=>recOf(u,L0('บัญชี','Acct'))));tests=tests.concat((await SP.Tests.forDoctor(ME.id)).filter(x=>ids.includes(x.patientUid)).map(x=>({...x,pid:x.patientUid,linked:true})))}
}""")
rep("let lang=localStorage.sp_lang||'th';const t=k=>D[lang][k]??k;", "let lang=localStorage.sp_lang||'th';const t=k=>D[lang][k]??k;const L0=(a,b)=>lang==='th'?a:b;")
rep("let cur={pid:'',trials:[],checks:[],comment:''};", "let cur={pid:ROLE==='patient'?ME.id:'',trials:[],checks:[],comment:''};")

# 5 key replacements
s = s.replace('localStorage.sp_active', 'localStorage[AK]')
s = s.replace("save('sp_patients',patients)", "save(PK,patients.filter(p=>!p.linked))")
s = s.replace("save('sp_tests',tests)", "persistTests()")
s = s.replace("save('sp_cfg',cfg)", "save(CK,cfg)")
rep("  Object.assign(p,{hn:g('p_hn'),name:g('p_name'),sex:g('p_sex'),age:+g('p_age')||'',ht:+g('p_ht')||'',wt:+g('p_wt')||'',smk:g('p_smk'),pf:+g('p_pf')||'',pv:+g('p_pv')||'',note:g('p_note')});",
    "  Object.assign(p,{hn:g('p_hn'),name:g('p_name'),sex:g('p_sex'),age:+g('p_age')||'',ht:+g('p_ht')||'',wt:+g('p_wt')||'',smk:g('p_smk'),pf:+g('p_pf')||'',pv:+g('p_pv')||'',note:g('p_note')});\n  if(p.linked&&!DEMO)SP.Users.get(p.id).then(u=>SP.Users.update(u.id,{meta:{...u.meta,sex:p.sex,age:p.age,ht:p.ht,wt:p.wt,smk:p.smk,pf:p.pf,pv:p.pv,note:p.note}}));")
rep("$('delP').onclick=()=>{if(!confirm(t('confirmDel')))return;", "$('delP').onclick=()=>{if(!confirm(t('confirmDel')))return;{const q=P(activeP);if(q&&q.linked&&!DEMO)SP.Users.update(q.id,{doctorId:''})}")
rep("  $('delP').style.display=$('startP').style.display=p.id?'':'none';", "  $('delP').style.display=$('startP').style.display=p.id?'':'none';\n  ['p_hn','p_name'].forEach(k=>$(k).disabled=!!p.linked);")

# 6 saveTest / delete test aware of the shared store
a = s.index('function saveTest(){')
b = s.index('function addTrial(r){')
s = s[:a] + r"""async function saveTest(){
  const s=summarize(cur.trials),id=uid(),p=P(cur.pid);
  const rec={id,pid:cur.pid,ts:Date.now(),trials:cur.trials.map(x=>({...x,curve:x.curve?x.curve.filter((_,i)=>i%2===0):undefined})),best:s.best,rep:s.rep,comment:cur.comment,fw:live.name||''};
  if(p&&p.linked&&!DEMO){rec.patientUid=p.id;rec.doctorUid=ROLE==='doctor'?ME.id:((await SP.Users.get(ME.id)).doctorId||'');rec.src=ROLE==='patient'?'self':'clinic';
    if(cur.trials.some(x=>x.src==='sim'))rec.demo=true;await SP.Tests.add(rec);tests.push({...rec,linked:true})}
  else{tests.push(rec);persistTests()}
  repSel=id;const pid=cur.pid;cur={pid,trials:[],checks:[],comment:''};setTab('reports')}
""" + s[b:]
rep("$('delT').onclick=()=>{if(confirm(t('confirmDel'))){tests=tests.filter(z=>z.id!==x.id);persistTests();repSel='';renderReports()}};",
    "$('delT').onclick=async()=>{if(confirm(t('confirmDel'))){if(x.linked&&!DEMO)await SP.Tests.remove(x.id);tests=tests.filter(z=>z.id!==x.id);persistTests();repSel='';renderReports()}};")
rep("if($('saveT'))$('saveT').onclick=saveTest;", "if($('saveT'))$('saveT').onclick=()=>saveTest();")

# 7 patient-mode UI tweaks in the test tab
rep("""<button class="b" id="chgP">← ${t('tabs').patients}</button></div>`""", """${ROLE==='patient'?'':`<button class="b" id="chgP">← ${t('tabs').patients}</button>`}</div>`""")
rep("  $('chgP').onclick=()=>setTab('patients');", "  if($('chgP'))$('chgP').onclick=()=>setTab('patients');")
rep("""      <label style="margin-top:12px"><span>${t('doctor')}</span><textarea id="cmt" rows="2">${esc(cur.comment)}</textarea></label>""",
    """      ${ROLE==='patient'?'<p class="note" style="margin-top:10px">'+L('ผลนี้เป็นการคัดกรองเบื้องต้น ถ้าผิดปกติหรือมีอาการ ให้ปรึกษาแพทย์','Screening only. If abnormal or you have symptoms, see a doctor')+'</p>':`<label style="margin-top:12px"><span>${t('doctor')}</span><textarea id="cmt" rows="2">${esc(cur.comment)}</textarea></label>`}""")
rep("  ['manual','sim'].forEach(k=>$(k).disabled=!p||cur.trials.length>=8);", "  ['manual','sim'].forEach(k=>$(k).disabled=!p||cur.trials.length>=8);$('manual').style.display=ROLE==='patient'?'none':'';")

# 8 nav + text + render map
rep("function buildNav(){$('nav').innerHTML=['test','patients','reports','device'].map(k=>`<button data-t=\"${k}\">${t('tabs')[k]}</button>`).join('');",
    "const tabName=k=>ROLE==='patient'?({test:L('เป่าวัดปอด','Blow test'),reports:L('ประวัติของฉัน','My history'),me:L('ข้อมูลของฉัน','My profile'),device:t('tabs').device})[k]:t('tabs')[k];\nfunction buildNav(){$('nav').innerHTML=(ROLE==='patient'?['test','reports','me','device']:['test','patients','reports','device']).map(k=>`<button data-t=\"${k}\">${tabName(k)}</button>`).join('');")
rep("$('appName').textContent=t('app');", "$('appName').textContent=ROLE==='patient'?'Spiro · '+L0('ผู้ป่วย','Patient'):t('app');")
rep("function render(){pill();({test:renderTest,patients:renderPatients,reports:renderReports,device:renderDevice})[tab]()}", "function render(){pill();({test:renderTest,patients:renderPatients,reports:renderReports,device:renderDevice,me:renderMe})[tab]()}")

# 9 profile tab (patient), account chip, doctor code
ME_JS = open('roles_me.js', encoding='utf-8').read()
rep("/* ---------- boot ---------- */", ME_JS + "\n/* ---------- boot ---------- */")
rep("setTab(tab);applyText();pullCloud();", r"""if(!DEMO_Q){$('who').style.display='';$('whoT').textContent=ME.name+' · '+({doctor:'แพทย์',patient:'ผู้ป่วย'}[ROLE]);$('logout').style.display='';$('logout').textContent=L0('ออก','Sign out');
  $('logout').onclick=async()=>{await SP.Auth.logout();location.href='login.html'};
  if(ROLE==='doctor'){$('docCode').style.display='';$('docCode').innerHTML=L0('รหัสแพทย์ของคุณ','Your doctor code')+': <b style="font-size:17px">'+esc(ME.code||'')+'</b> · '+L0('ให้ผู้ป่วยกรอกตอนสมัครหรือในแท็บ "ข้อมูลของฉัน" ผลการเป่าของเขาจะแสดงในรายชื่อผู้ป่วยและรายงาน','patients enter it at sign-up or in "My profile"; their results then appear in your patient list and reports')}}
setTab(tab);applyText();pullCloud();""")
rep("$('lang').onclick=()=>{lang=lang==='th'?'en':'th';localStorage.sp_lang=lang;applyText()};", "$('lang').onclick=()=>{lang=lang==='th'?'en':'th';localStorage.sp_lang=lang;applyText();if(!DEMO_Q)$('logout').textContent=L0('ออก','Sign out')};")
open('clinic.html', 'w', encoding='utf-8').write(s)
print('ok', len(s))
