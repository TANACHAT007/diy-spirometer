document.body.classList.add('role-'+(DEMO_Q?'demo':ROLE));   // lets calm.css give patients the friendlier look
/* ---------- count gauges ---------- */
function ringSvg(done,total,size,label){const R=size/2-9,C=2*Math.PI*R,f=total?Math.min(1,done/total):0;
  return '<svg viewBox="0 0 '+size+' '+size+'" width="'+size+'" height="'+size+'" role="img" aria-label="'+done+'/'+total+'"><circle cx="'+size/2+'" cy="'+size/2+'" r="'+R+'" fill="none" stroke="#cfe3f5" stroke-width="14"/><circle cx="'+size/2+'" cy="'+size/2+'" r="'+R+'" fill="none" stroke="'+(f>=1?'#1a8a52':'#0a5fb0')+'" stroke-width="14" stroke-linecap="round" stroke-dasharray="'+(C*f).toFixed(1)+' '+C.toFixed(1)+'" transform="rotate(-90 '+size/2+' '+size/2+')"/><text x="50%" y="48%" text-anchor="middle" dominant-baseline="middle" font-size="'+size*0.3+'" font-weight="800" fill="#0b1e33">'+done+'/'+total+'</text><text x="50%" y="70%" text-anchor="middle" font-size="'+size*0.11+'" fill="#42586f">'+label+'</text></svg>';}
function dots(done,total){let h='<div class="dots">';for(let i=0;i<total;i++)h+='<i class="'+(i<done?'on':i===done?'cur':'')+'"></i>';return h+'</div>'}
function weekStrip(planId,perDay){const out=[];for(let d=6;d>=0;d--){const a=new Date();a.setHours(0,0,0,0);a.setDate(a.getDate()-d);const t0=a.getTime(),n=myTrains.filter(x=>(!planId||x.planId===planId)&&x.ts>=t0&&x.ts<t0+864e5).length;
  out.push('<div class="wd"><small>'+['อา','จ','อ','พ','พฤ','ศ','ส'][a.getDay()]+'</small><span class="'+(n>=perDay?'full':n>0?'part':'')+'">'+(n>=perDay?'✓':n||'')+'</span></div>')}return '<div class="week">'+out.join('')+'</div>'}

/* ---------- patient home: two big buttons only ---------- */
const todayStart=()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()};
let myPlans=[],myTrains=[];
async function loadPlans(){
  if(DEMO_Q){const now=Date.now();myPlans=[{id:'pdemo',patientUid:'d1',doctorUid:'demo',title:'Breathing exercise',kind:'breathing',sessionsPerDay:3,reps:10,minutes:5,target:0,until:now+28*864e5,note:'',active:true}];myTrains=[];return}
  try{myPlans=(await SP.Plans.forPatient(ME.id)).filter(p=>p.active!==false&&(!p.until||p.until>Date.now()));
    myTrains=await SP.Trainings.forPatient(ME.id)}catch(e){myPlans=[];myTrains=[]}
}
function doneToday(planId){return myTrains.filter(t=>t.planId===planId&&t.ts>=todayStart()).length}
async function renderHome(){
  await loadPlans();
  const plan=myPlans[0],done=plan?doneToday(plan.id):0,left=plan?Math.max(0,plan.sessionsPerDay-done):0;
  const last=tests.slice().sort((a,b)=>b.ts-a.ts)[0];
  const hr=new Date().getHours(),first=String(ME.name||'').trim().split(/\s+/)[0]||'';
  const hi=lang==='th'?(hr<11?'อรุณสวัสดิ์':hr<16?'สวัสดีตอนบ่าย':hr<19?'สวัสดีตอนเย็น':'สวัสดีตอนค่ำ'):(hr<12?'Good morning':hr<18?'Good afternoon':'Good evening');
  const allDone=plan&&left===0;
  $('homeBox').innerHTML=`
  <div class="hello"><img src="icons/${hr>=6&&hr<18?'sun':'smiling_face_with_smiling_eyes'}.svg" alt="" width="84" height="84"><div>
    <h1>${hi} ${lang==='th'?'คุณ':''}${esc(first)}</h1>
    <p>${L0('วันนี้เป็นอย่างไรบ้างคะ เลือกสิ่งที่อยากทำได้เลย','How are you today? Choose what you would like to do.')}</p>
    ${allDone?`<span class="chip"><img src="icons/glowing_star.svg" alt="" width="22" height="22"> ${L0('วันนี้ฝึกครบแล้ว เก่งมาก','All done today, well done')}</span>`:''}</div></div>
  <div class="bigGrid">
    <button class="bigBtn" id="hTest"><span class="ic"><img src="icons/lungs.svg" alt=""></span><b>${L0('ตรวจคุณภาพปอด','Check my lungs')}</b><small>${L0('เป่าวัดปอด 3 ครั้ง','Blow 3 times')}</small><span class="go2">${L0('เริ่มตรวจ','Start')} →</span></button>
    <button class="bigBtn alt" id="hTrain"><span class="ic"><img src="icons/wind_face.svg" alt=""></span><b>${L0('ฝึกตามตารางแพทย์','Practice (doctor plan)')}</b>
      <small>${plan?(left>0?L0(`วันนี้เหลืออีก ${left} รอบ`,`${left} session(s) left today`):L0('วันนี้ฝึกครบแล้ว เก่งมาก','Done for today, well done')):L0('แพทย์ยังไม่ได้สั่งตาราง','No plan from your doctor yet')}</small><span class="go2">${L0('เริ่มฝึก','Start')} →</span></button>
  </div>
  ${plan?`<div class="card planCard" style="margin-top:20px"><div class="ringBox">${ringSvg(Math.min(done,plan.sessionsPerDay),plan.sessionsPerDay,150,L0('รอบวันนี้','today'))}</div><div style="flex:1;min-width:220px"><h2 class="ih"><img src="icons/calendar.svg" alt="" width="36" height="36">${L0('ตารางของฉัน','My plan')}</h2><p style="font-size:1.15rem;margin:0">${planText(plan)}</p>${weekStrip(plan.id,plan.sessionsPerDay)}</div></div>${plan.note?`<div class="card docNote" style="margin-top:16px"><span class="ic2"><img src="icons/stethoscope.svg" alt="" width="34" height="34"></span><div><b>${L0('ข้อความจากแพทย์','Note from your doctor')}</b><p>${esc(plan.note)}</p></div></div>`:''}`:''}
  ${last?`<div class="card" style="margin-top:16px"><h2 class="ih"><img src="icons/memo.svg" alt="" width="36" height="36">${L0('ผลล่าสุด','Latest result')}</h2><div class="kpis"><div class="kpi"><span>FEV1</span><b>${fmt(last.best.fev1)}<small style="font-size:16px"> L</small></b></div><div class="kpi"><span>FVC</span><b>${fmt(last.best.fvc)}<small style="font-size:16px"> L</small></b></div><div class="kpi"><span>FEV1/FVC</span><b>${fmt(last.best.ratio,0)}<small style="font-size:16px"> %</small></b></div></div><p class="note" style="margin:0">${fdate(last.ts)}</p></div>`:''}
  <p class="note" style="margin-top:14px">${L0('ผลนี้เป็นการคัดกรองเบื้องต้น ไม่ใช่การวินิจฉัย ถ้ามีอาการเหนื่อยหอบ ให้พบแพทย์','Screening only, not a diagnosis. If you feel short of breath, see a doctor.')}</p>`;
  $('hTest').onclick=()=>{startTest(ME.id);cur.checks=CHECKS.slice();setTab('test')};
  $('hTrain').onclick=()=>{if(!plan){alert(L0('แพทย์ยังไม่ได้สั่งตารางฝึก ให้ถามแพทย์ หรือเชื่อมแพทย์ที่เมนู "ข้อมูลของฉัน"','Your doctor has not set a plan. Ask your doctor, or link a doctor in "My profile".'));return}startTraining(plan)};
}
function planText(p){
  const kind=p.kind==='volume'?L0('เป่าให้ถึงเป้า','Blow to the target'):L0('หายใจเข้าออกช้าๆ','Slow breathing');
  return `${kind} · ${L0('วันละ','')} <b>${p.sessionsPerDay}</b> ${L0('รอบ','sessions/day')} · ${L0('รอบละ','')} <b>${p.reps}</b> ${L0('ครั้ง','breaths')} · ${L0('ประมาณ','about')} <b>${p.minutes}</b> ${L0('นาที','min')}${p.kind==='volume'&&p.target?` · ${L0('เป้า','target')} <b>${p.target}</b> L`:''}`;
}

/* ---------- voice + beeps for training (works in any modern phone browser; no data leaves the device) ---------- */
let sndOn=(()=>{try{return localStorage.sp_snd!=='0'}catch(e){return true}})(),actx=null,lastSay='';
function beep(f,ms,v){if(!sndOn)return;try{actx=actx||new (window.AudioContext||window.webkitAudioContext)();const o=actx.createOscillator(),g=actx.createGain();o.frequency.value=f;o.type='sine';g.gain.value=v||0.08;o.connect(g);g.connect(actx.destination);o.start();o.stop(actx.currentTime+ms/1000)}catch(e){}}
/* Nurse-style warm script. Each key can have a recorded file voice/<th|en>/<key>.mp3; if the file is missing the browser voice reads the same text. */
const VOICE={
 start:{th:'สวัสดีค่ะ เรามาเริ่มฝึกกันนะคะ นั่งหลังตรง ไหล่ผ่อนคลายค่ะ',en:'Hello! Let us begin. Sit up straight and relax your shoulders.'},
 in:{th:'หายใจเข้าช้าๆ ค่ะ',en:'Breathe in slowly.'},
 out:{th:'เป่าออกช้าๆ เรื่อยๆ ค่ะ',en:'Now blow out slowly and steadily.'},
 good:{th:'เก่งมากค่ะ',en:'Very good!'},
 weak:{th:'ไม่เป็นไรค่ะ ลองใหม่อีกครั้งนะคะ',en:'That is okay. Let us try once more.'},
 done:{th:'ยอดเยี่ยมเลยค่ะ ฝึกเสร็จแล้ว พักสักครู่นะคะ',en:'Wonderful! You have finished. Take a short rest.'},
 on:{th:'เปิดเสียงแล้วค่ะ',en:'Sound on.'}};
['ศูนย์','หนึ่ง','สอง','สาม','สี่','ห้า','หก','เจ็ด','แปด','เก้า','สิบ'].forEach((t,i)=>{VOICE['n'+i]={th:t,en:['zero','one','two','three','four','five','six','seven','eight','nine','ten'][i]}});
const NUMTH=['ศูนย์','หนึ่ง','สอง','สาม','สี่','ห้า','หก','เจ็ด','แปด','เก้า','สิบ'];
let curAudio=null;
function say(key){
  if(!sndOn||key===lastSay)return;lastSay=key;
  const v=VOICE[key],text=v?v[lang==='th'?'th':'en']:String(key);
  const tts=()=>{if(!('speechSynthesis' in window))return;try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.lang=lang==='th'?'th-TH':'en-US';u.rate=0.92;u.pitch=1.1;u.volume=1;
    const f=speechSynthesis.getVoices().filter(x=>x.lang&&x.lang.toLowerCase().startsWith(u.lang.slice(0,2).toLowerCase()));
    u.voice=f.find(x=>/female|premwadee|kanya|narisa|achara|google/i.test(x.name))||f[0]||null;speechSynthesis.speak(u)}catch(e){}};
  if(!v){tts();return}
  try{if(curAudio)curAudio.pause();const a=new Audio('voice/'+(lang==='th'?'th':'en')+'/'+key+'.mp3');curAudio=a;a.onerror=tts;a.play().catch(tts)}catch(e){tts()}
}
function buzz(ms){try{if(navigator.vibrate)navigator.vibrate(ms)}catch(e){}}
const numWord=n=>lang==='th'?(n<=10?NUMTH[n]:String(n)):String(n);
function toggleSound(){sndOn=!sndOn;try{localStorage.sp_snd=sndOn?'1':'0'}catch(e){}$('trainSnd').textContent=(sndOn?'🔊 ':'🔇 ')+L0(sndOn?'เสียงเปิด':'เสียงปิด',sndOn?'Sound on':'Sound off');if(!sndOn&&'speechSynthesis' in window)speechSynthesis.cancel();else say('on')}

/* ---------- guided training session (full screen) ---------- */
let tr=null;
function trainUi(msg,sub,pct,num,done,total){const o=$('trainOv');o.querySelector('.tdots').innerHTML=total?dots(done||0,total)+'<div class="tcount">'+L0('ครั้งที่','Breath')+' <b>'+Math.min((done||0)+1,total)+'</b> / '+total+'</div>':'';o.querySelector('.tmsg').textContent=msg;o.querySelector('.tsub').textContent=sub;o.querySelector('.tnum').textContent=num;o.querySelector('.tbar i').style.width=Math.max(0,Math.min(100,pct))+'%'}
function startTraining(plan){
  if(tr)return;
  tr={plan,rep:0,startTs:Date.now(),vols:[],sim:false,timer:null,phase:'',t0:0,lastRep:-1,lastPh:''};lastSay='';
  $('trainOv').classList.add('on');$('trainSnd').textContent=(sndOn?'🔊 ':'🔇 ')+L0(sndOn?'เสียงเปิด':'เสียงปิด',sndOn?'Sound on':'Sound off');
  beep(660,160);say('start');
  const cyc=Math.max(4,Math.min(15,plan.minutes*60/plan.reps));         // seconds per breath: the doctor's minutes / breaths
  tr.inh=cyc/3;tr.exh=cyc*2/3;                                          // breathe out about twice as long as in
  if(plan.kind==='volume'){
    tr.sim=!live.connected;
    trainUi(live.connected?L0('เป่าลมออกให้ถึงเป้า','Blow out to the target'):L0('ยังไม่ได้ต่อเครื่อง กดจำลองเพื่อฝึกใช้งาน','Device not connected: press Practice'),
      `${L0('เป้า','Target')} ${plan.target||'–'} L`,0,'0.0 L',0,plan.reps);
    $('trainSim').style.display=live.connected?'none':'';
  }else{
    $('trainSim').style.display='none';tr.t0=performance.now()+2500;tr.phase='in';trainTick();
  }
}
function trainTick(){
  if(!tr||tr.plan.kind==='volume')return;
  const p=tr.plan,el=(performance.now()-tr.t0)/1000;
  if(el<0){trainUi(L0('เตรียมตัว','Get ready'),L0('เริ่มใน','Starting in')+' '+Math.ceil(-el)+' '+L0('วินาที','s'),0,Math.ceil(-el),0,p.reps);tr.timer=requestAnimationFrame(trainTick);return}
  const total=tr.inh+tr.exh,k=el%total,rep=Math.floor(el/total);
  if(rep>=p.reps){tr.rep=p.reps;finishTraining();return}
  tr.rep=rep;
  const inh=k<tr.inh;
  if(tr.lastRep!==rep){tr.lastRep=rep;tr.lastPh='';if(rep>0)say(rep<=10?'n'+rep:String(rep))}
  if(tr.lastPh!==(inh?'i':'o')){tr.lastPh=inh?'i':'o';beep(inh?520:400,140);buzz(inh?60:30);if(rep>0||!inh||true)setTimeout(()=>say(inh?'in':'out'),rep>0&&inh?900:0)}
  trainUi(inh?L0('หายใจเข้าทางจมูก','Breathe in through the nose'):L0('เป่าออกช้าๆ ทางปากเหมือนเป่าเทียน','Breathe out slowly, lips like blowing a candle'),
    `${L0('รอบนี้ประมาณ','About')} ${p.minutes} ${L0('นาที','min')}`,inh?100*k/tr.inh:100-100*(k-tr.inh)/tr.exh,inh?L0('เข้า','IN'):L0('ออก','OUT'),rep,p.reps);
  tr.timer=requestAnimationFrame(trainTick);
}
function trainBreath(volL){            // volume kind: one blow measured (device or practice)
  if(!tr||tr.plan.kind!=='volume')return;
  tr.vols.push(volL);tr.rep++;const p=tr.plan;beep(volL>=(p.target||0)*0.8?760:300,200);say(tr.rep<=10?'n'+tr.rep:String(tr.rep));
  const hit=!p.target||volL>=p.target*0.8;
  trainUi(hit?L0('ดีมาก','Good'):L0('ลองอีกนิด','Try a little more'),`${volL.toFixed(2)} L`,Math.min(100,100*volL/(p.target||volL||1)),volL.toFixed(1)+' L',tr.rep,p.reps);
  if(tr.rep>=p.reps)setTimeout(finishTraining,900);
}
async function finishTraining(){
  if(!tr)return;cancelAnimationFrame(tr.timer);
  const p=tr.plan,rec={id:uid(),patientUid:ME.id,doctorUid:p.doctorUid||'',planId:p.id,ts:Date.now(),reps:Math.min(tr.rep,p.reps),durationSec:Math.round((Date.now()-tr.startTs)/1000),kind:p.kind,
    avgVol:tr.vols.length?+(tr.vols.reduce((a,b)=>a+b,0)/tr.vols.length).toFixed(2):0,maxVol:tr.vols.length?+Math.max(...tr.vols).toFixed(2):0,src:tr.sim?'sim':'self'};
  tr=null;
  if(!DEMO_Q){try{await SP.Trainings.add(rec)}catch(e){alert(e.message)}}
  myTrains.push(rec);
  beep(880,200);setTimeout(()=>beep(1100,260),240);buzz(200);lastSay='';say('done');
  trainUi(L0('เก่งมาก ฝึกเสร็จแล้ว','Well done, finished'),`${rec.reps} ${L0('ครั้ง','breaths')} · ${Math.floor(rec.durationSec/60)}:${String(rec.durationSec%60).padStart(2,'0')}`,100,'✓',rec.reps,p.reps);
  $('trainSim').style.display='none';
  yay(true);
  setTimeout(()=>{$('trainOv').classList.remove('on');yay(false);renderHome()},3200);
}
/* small CSS-only celebration (confetti + star); motion is switched off by prefers-reduced-motion in calm.css */
function yay(on){const o=$('trainOv');o.classList.toggle('yay',on);const old=o.querySelector('.yayBurst');if(old)old.remove();const s=o.querySelector('.yayStar');if(s)s.remove();
  if(!on)return;let h='';for(let i=0;i<28;i++)h+=`<i style="left:${(i*37)%97}%;top:${(i*53)%92}%;animation-delay:${(i%7)*0.1}s"></i>`;
  o.insertAdjacentHTML('afterbegin','<div class="yayBurst" aria-hidden="true">'+h+'</div><img class="yayStar" src="icons/party_popper.svg" alt="" width="120" height="120">')}
function stopTraining(){if(tr){cancelAnimationFrame(tr.timer);tr=null}try{speechSynthesis.cancel()}catch(e){}yay(false);$('trainOv').classList.remove('on');if(tab==='home')renderHome()}
function trainSimBlow(){if(!tr)return;const t=tr.plan.target||2;trainBreath(+(t*(0.7+Math.random()*0.5)).toFixed(2))}

/* ---------- doctor: prescribe a training plan for a linked patient ---------- */
const TEMPLATES={
  breathing:{kind:'breathing',sessionsPerDay:3,reps:10,minutes:5,target:0},
  volume:{kind:'volume',sessionsPerDay:3,reps:10,minutes:5,target:1.5}};
async function renderPlanBox(){
  const box=$('planBox');if(!box)return;
  const p=P(activeP);
  if(ROLE!=='doctor'||DEMO_Q||!p||!p.linked){box.innerHTML=ROLE==='doctor'&&p&&p.id&&!p.linked?`<p class="note">${L0('แผนฝึกสั่งได้เฉพาะผู้ป่วยที่เชื่อมบัญชีกับคุณ (ผู้ป่วยกรอกรหัสแพทย์ของคุณ)','Training plans can only be set for patients who linked their account to you (they enter your doctor code).')}</p>`:'';return}
  let plans=[],trains=[];try{plans=await SP.Plans.forPatient(p.id);trains=await SP.Trainings.forPatient(p.id)}catch(e){}
  const cur_=plans.find(x=>x.active!==false)||null;
  const wk=trains.filter(t=>t.ts>Date.now()-7*864e5);
  const v=cur_||Object.assign({until:Date.now()+28*864e5,note:'',title:''},TEMPLATES.breathing);
  const dt=ms=>new Date(ms).toISOString().slice(0,10);
  box.innerHTML=`<h3 style="margin-top:18px">${L0('แผนฝึกหายใจ','Breathing training plan')}</h3>
   <p class="note">${L0('แพทย์เป็นผู้กำหนด ไม่มีแนวทางสากลที่ระบุขนาดการฝึกตายตัว ตัวอย่างที่พบ: ฝึกหายใจแบบห่อปาก/ใช้กระบังลม 5–10 นาทีต่อวัน หรือประมาณ 10 นาที 3–4 ครั้งต่อวัน (เอกสารให้ความรู้ผู้ป่วย American Lung Association, HealthLink BC) และผู้ผลิตแนะนำให้แพทย์กำหนดความถี่ของ incentive spirometer ตามผู้ป่วย (AARC 2011 ไม่พบหลักฐานของความถี่ที่แน่นอน) ค่าเริ่มต้นจึงเป็นเพียงตัวอย่าง','The doctor decides. No guideline sets one fixed dose. Examples found: pursed-lip/diaphragmatic breathing 5-10 min a day, or about 10 min 3-4 times a day (patient-education material from the American Lung Association and HealthLink BC); the 2011 AARC guideline found no evidence for a specific incentive-spirometry frequency. Defaults are only examples.')}</p>
   <div class="form">
    <label>${L0('แบบฝึก','Type')}<select id="pl_kind"><option value="breathing" ${v.kind==='breathing'?'selected':''}>${L0('หายใจเข้าออกช้าๆ ตามจังหวะ','Paced slow breathing')}</option><option value="volume" ${v.kind==='volume'?'selected':''}>${L0('เป่าให้ถึงปริมาตรเป้า (ใช้เครื่อง)','Blow to a volume target (device)')}</option></select></label>
    <label>${L0('จำนวนรอบต่อวัน (1-6)','Sessions per day (1-6)')}<input id="pl_s" type="number" min="1" max="6" value="${v.sessionsPerDay}"></label>
    <label>${L0('ครั้งต่อรอบ (1-30)','Breaths per session (1-30)')}<input id="pl_r" type="number" min="1" max="30" value="${v.reps}"></label>
    <label>${L0('นาทีต่อรอบ (1-30)','Minutes per session (1-30)')}<input id="pl_m" type="number" min="1" max="30" value="${v.minutes}"></label>
    <label>${L0('ปริมาตรเป้า (ลิตร) เฉพาะแบบเป่า','Target volume (L), blow type only')}<input id="pl_t" type="number" step="0.1" min="0" max="6" value="${v.target||''}"></label>
    <label>${L0('ใช้ถึงวันที่','Until')}<input id="pl_u" type="date" value="${dt(v.until||Date.now()+28*864e5)}"></label></div>
   <label style="margin-top:10px">${L0('ข้อความถึงผู้ป่วย (ไม่บังคับ)','Note to patient (optional)')}<textarea id="pl_n" rows="2" maxlength="300">${esc(v.note||'')}</textarea></label>
   <div class="row" style="margin-top:10px"><button class="b pri" id="pl_save">${L0(cur_?'อัปเดตแผน':'สั่งแผนฝึก',cur_?'Update plan':'Prescribe plan')}</button>${cur_?`<button class="b danger" id="pl_del">${L0('ยกเลิกแผน','Cancel plan')}</button>`:''}<span class="note" id="pl_msg"></span></div>
   ${cur_?`<p class="note" style="margin-top:10px">${L0('7 วันล่าสุด: ฝึกแล้ว','Last 7 days: done')} <b>${wk.length}</b> / ${cur_.sessionsPerDay*7} ${L0('รอบ','sessions')}</p>`:''}
   ${wk.length?`<table><tr><th>${L0('วันที่','Date')}</th><th>${L0('ครั้ง','Breaths')}</th><th>${L0('เวลา','Time')}</th><th>${L0('เฉลี่ย (L)','Avg (L)')}</th><th></th></tr>`+wk.sort((a,b)=>b.ts-a.ts).slice(0,10).map(t=>`<tr><td>${fdate(t.ts)}</td><td>${t.reps}</td><td>${Math.floor(t.durationSec/60)}:${String(t.durationSec%60).padStart(2,'0')}</td><td>${t.avgVol||'–'}</td><td>${t.src==='sim'?L0('ฝึกใช้งาน','practice'):''}</td></tr>`).join('')+'</table>':''}`;
  $('pl_kind').onchange=()=>{const t=TEMPLATES[$('pl_kind').value];$('pl_s').value=t.sessionsPerDay;$('pl_r').value=t.reps;$('pl_m').value=t.minutes;$('pl_t').value=t.target||''};
  $('pl_save').onclick=async()=>{
    const n=(id,lo,hi)=>Math.max(lo,Math.min(hi,Math.round(+$(id).value||lo)));
    const plan={id:cur_?cur_.id:uid(),patientUid:p.id,doctorUid:ME.id,kind:$('pl_kind').value,title:$('pl_kind').value==='volume'?'Blow to target':'Slow breathing',
      sessionsPerDay:n('pl_s',1,6),reps:n('pl_r',1,30),minutes:n('pl_m',1,30),target:$('pl_kind').value==='volume'?Math.max(0.3,Math.min(6,+$('pl_t').value||1.5)):0,
      until:new Date($('pl_u').value+'T23:59:59').getTime()||Date.now()+28*864e5,note:$('pl_n').value.trim().slice(0,300),active:true,created:cur_?cur_.created:Date.now(),updated:Date.now()};
    try{await SP.Plans.save(plan);$('pl_msg').textContent=L0('บันทึกแล้ว ผู้ป่วยจะเห็นในหน้าหลักของเขา','Saved. The patient will see it on their home screen.');renderPlanBox()}catch(e){$('pl_msg').textContent=e.message}};
  if($('pl_del'))$('pl_del').onclick=async()=>{if(confirm(L0('ยกเลิกแผนฝึกนี้?','Cancel this plan?'))){await SP.Plans.remove(cur_.id);renderPlanBox()}};
}
