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
  $('homeBox').innerHTML=`
  <div class="bigGrid">
    <button class="bigBtn" id="hTest"><span class="ic">🫁</span><b>${L0('ตรวจคุณภาพปอด','Check my lungs')}</b><small>${L0('เป่าวัดปอด 3 ครั้ง','Blow 3 times')}</small></button>
    <button class="bigBtn alt" id="hTrain"><span class="ic">🌬️</span><b>${L0('ฝึกตามตารางแพทย์','Practice (doctor plan)')}</b>
      <small>${plan?(left>0?L0(`วันนี้เหลืออีก ${left} รอบ`,`${left} session(s) left today`):L0('วันนี้ฝึกครบแล้ว เก่งมาก','Done for today, well done')):L0('แพทย์ยังไม่ได้สั่งตาราง','No plan from your doctor yet')}</small></button>
  </div>
  ${plan?`<div class="card" style="margin-top:16px"><h2>${L0('ตารางของฉัน','My plan')}</h2><p style="font-size:1.15rem;margin:0">${planText(plan)}</p>${plan.note?`<p class="note">${L0('ข้อความจากแพทย์','Doctor note')}: ${esc(plan.note)}</p>`:''}</div>`:''}
  ${last?`<div class="card" style="margin-top:16px"><h2>${L0('ผลล่าสุด','Latest result')}</h2><div class="kpis"><div class="kpi"><span>FEV1</span><b>${fmt(last.best.fev1)}<small style="font-size:14px"> L</small></b></div><div class="kpi"><span>FVC</span><b>${fmt(last.best.fvc)}<small style="font-size:14px"> L</small></b></div><div class="kpi"><span>FEV1/FVC</span><b>${fmt(last.best.ratio,0)}<small style="font-size:14px"> %</small></b></div></div><p class="note">${fdate(last.ts)}</p></div>`:''}
  <p class="note" style="margin-top:14px">${L0('ผลนี้เป็นการคัดกรองเบื้องต้น ไม่ใช่การวินิจฉัย ถ้ามีอาการเหนื่อยหอบ ให้พบแพทย์','Screening only, not a diagnosis. If you feel short of breath, see a doctor.')}</p>`;
  $('hTest').onclick=()=>{startTest(ME.id);cur.checks=CHECKS.slice();setTab('test')};
  $('hTrain').onclick=()=>{if(!plan){alert(L0('แพทย์ยังไม่ได้สั่งตารางฝึก ให้ถามแพทย์ หรือเชื่อมแพทย์ที่เมนู "ข้อมูลของฉัน"','Your doctor has not set a plan. Ask your doctor, or link a doctor in "My profile".'));return}startTraining(plan)};
}
function planText(p){
  const kind=p.kind==='volume'?L0('เป่าให้ถึงเป้า','Blow to the target'):L0('หายใจเข้าออกช้าๆ','Slow breathing');
  return `${kind} · ${L0('วันละ','')} <b>${p.sessionsPerDay}</b> ${L0('รอบ','sessions/day')} · ${L0('รอบละ','')} <b>${p.reps}</b> ${L0('ครั้ง','breaths')} · ${L0('ประมาณ','about')} <b>${p.minutes}</b> ${L0('นาที','min')}${p.kind==='volume'&&p.target?` · ${L0('เป้า','target')} <b>${p.target}</b> L`:''}`;
}

/* ---------- guided training session (full screen) ---------- */
let tr=null;
function trainUi(msg,sub,pct,num){const o=$('trainOv');o.querySelector('.tmsg').textContent=msg;o.querySelector('.tsub').textContent=sub;o.querySelector('.tnum').textContent=num;o.querySelector('.tbar i').style.width=Math.max(0,Math.min(100,pct))+'%'}
function startTraining(plan){
  if(tr)return;
  tr={plan,rep:0,startTs:Date.now(),vols:[],sim:false,timer:null,phase:'',t0:0};
  $('trainOv').classList.add('on');
  const cyc=Math.max(4,Math.min(15,plan.minutes*60/plan.reps));         // seconds per breath: the doctor's minutes / breaths
  tr.inh=cyc/3;tr.exh=cyc*2/3;                                          // breathe out about twice as long as in
  if(plan.kind==='volume'){
    tr.sim=!live.connected;
    trainUi(live.connected?L0('เป่าลมออกให้ถึงเป้า','Blow out to the target'):L0('ยังไม่ได้ต่อเครื่อง กดจำลองเพื่อฝึกใช้งาน','Device not connected: press Practice'),
      `${L0('เป้า','Target')} ${plan.target||'–'} L · ${L0('ครั้งที่','Breath')} 1/${plan.reps}`,0,'0.0 L');
    $('trainSim').style.display=live.connected?'none':'';
  }else{
    $('trainSim').style.display='none';tr.t0=performance.now();tr.phase='in';trainTick();
  }
}
function trainTick(){
  if(!tr||tr.plan.kind==='volume')return;
  const p=tr.plan,el=(performance.now()-tr.t0)/1000;
  const total=tr.inh+tr.exh,k=el%total,rep=Math.floor(el/total);
  if(rep>=p.reps){finishTraining();return}
  tr.rep=rep;
  const inh=k<tr.inh;
  trainUi(inh?L0('หายใจเข้าทางจมูก','Breathe in through the nose'):L0('เป่าออกช้าๆ ทางปากเหมือนเป่าเทียน','Breathe out slowly, lips like blowing a candle'),
    `${L0('ครั้งที่','Breath')} ${rep+1}/${p.reps}`,inh?100*k/tr.inh:100-100*(k-tr.inh)/tr.exh,inh?L0('เข้า','IN'):L0('ออก','OUT'));
  tr.timer=requestAnimationFrame(trainTick);
}
function trainBreath(volL){            // volume kind: one blow measured (device or practice)
  if(!tr||tr.plan.kind!=='volume')return;
  tr.vols.push(volL);tr.rep++;const p=tr.plan;
  const hit=!p.target||volL>=p.target*0.8;
  trainUi(hit?L0('ดีมาก','Good'):L0('ลองอีกนิด','Try a little more'),`${L0('ครั้งที่','Breath')} ${Math.min(tr.rep+1,p.reps)}/${p.reps} · ${volL.toFixed(2)} L`,Math.min(100,100*volL/(p.target||volL||1)),volL.toFixed(1)+' L');
  if(tr.rep>=p.reps)setTimeout(finishTraining,900);
}
async function finishTraining(){
  if(!tr)return;cancelAnimationFrame(tr.timer);
  const p=tr.plan,rec={id:uid(),patientUid:ME.id,doctorUid:p.doctorUid||'',planId:p.id,ts:Date.now(),reps:Math.min(tr.rep,p.reps),durationSec:Math.round((Date.now()-tr.startTs)/1000),kind:p.kind,
    avgVol:tr.vols.length?+(tr.vols.reduce((a,b)=>a+b,0)/tr.vols.length).toFixed(2):0,maxVol:tr.vols.length?+Math.max(...tr.vols).toFixed(2):0,src:tr.sim?'sim':'self'};
  tr=null;
  if(!DEMO_Q){try{await SP.Trainings.add(rec)}catch(e){alert(e.message)}}
  myTrains.push(rec);
  trainUi(L0('เก่งมาก ฝึกเสร็จแล้ว','Well done, finished'),`${rec.reps} ${L0('ครั้ง','breaths')} · ${Math.floor(rec.durationSec/60)}:${String(rec.durationSec%60).padStart(2,'0')}`,100,'✓');
  $('trainSim').style.display='none';
  setTimeout(()=>{$('trainOv').classList.remove('on');renderHome()},2500);
}
function stopTraining(){if(tr){cancelAnimationFrame(tr.timer);tr=null}$('trainOv').classList.remove('on');if(tab==='home')renderHome()}
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
