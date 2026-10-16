/* ---------- my profile (patient) ---------- */
async function renderMe(){
  const u=await SP.Users.get(ME.id),m=u.meta||{},doc=u.doctorId?{name:u.doctorName||''}:null;
  $('meBox').innerHTML=`<div class="grid2"><div style="display:grid;gap:16px">
   <div class="card"><h2>${L0('ข้อมูลของฉัน','My details')}</h2><div class="form">
    <label>${L0('ชื่อ-สกุล','Full name')}<input id="m_name" value="${esc(u.name)}"></label>
    <label>${t('sex')}<select id="m_sex"><option value="M" ${m.sex!=='F'?'selected':''}>${t('male')}</option><option value="F" ${m.sex==='F'?'selected':''}>${t('female')}</option></select></label>
    <label>${t('age')}<input id="m_age" type="number" value="${esc(m.age)}"></label><label>${t('ht')}<input id="m_ht" type="number" value="${esc(m.ht)}"></label>
    <label>${t('wt')}<input id="m_wt" type="number" value="${esc(m.wt)}"></label>
    <label>${t('smk')}<select id="m_smk"><option value="0">${t('s0')}</option><option value="1" ${m.smk==='1'?'selected':''}>${t('s1')}</option><option value="2" ${m.smk==='2'?'selected':''}>${t('s2')}</option></select></label></div>
    <p class="note" style="margin-top:8px">${L0('ค่าคาดการณ์ (ถ้าแพทย์ให้มา)','Predicted values (if your doctor gave them)')}</p>
    <div class="form"><label>${t('pf')}<input id="m_pf" type="number" step="0.01" value="${esc(m.pf)}"></label><label>${t('pv')}<input id="m_pv" type="number" step="0.01" value="${esc(m.pv)}"></label></div>
    <div class="row" style="margin-top:12px"><button class="b pri" id="m_save">${t('save')}</button></div><div id="m_msg" class="note"></div></div>
   <div class="card"><h2>${L0('บัญชี','Account')}</h2><p class="note">${esc(u.email)}</p>
    <div class="form"><label>${L0('รหัสผ่านปัจจุบัน','Current password')}<input id="m_pw0" type="password" autocomplete="current-password"></label><label>${L0('รหัสผ่านใหม่ (≥ 8 ตัว)','New password (≥ 8)')}<input id="m_pw" type="password" autocomplete="new-password"></label></div><p class="note">${L0('รหัสผ่านเป็นความลับ: ไม่ถูกเก็บ แสดง หรือส่งออกโดยเว็บนี้ (โหมดคลาวด์เก็บเฉพาะที่ Firebase Authentication แบบเข้ารหัส)','Passwords are secret: this site never stores, shows or exports them (cloud mode keeps them only inside Firebase Authentication, hashed)')}</p>
    <div class="row" style="margin-top:10px"><button class="b" id="m_pwgo">${L0('เปลี่ยนรหัสผ่าน','Change password')}</button><button class="b" id="m_exp">${t('exp')}</button><button class="b danger" id="m_del">${L0('ลบบัญชีและข้อมูลของฉัน','Delete my account and data')}</button></div></div></div>
   <div class="card"><h2>${L0('แชร์ผลกับแพทย์','Share with a doctor')}</h2>
    <p>${doc?L0('แพทย์ผู้ดูแล','Your doctor')+': <b>'+esc(doc.name)+'</b>':L0('ยังไม่ได้เชื่อมกับแพทย์','Not linked to a doctor')}</p>
    <p class="note">${L0('ใส่รหัสแพทย์ (เช่น DR-AB12) ที่แพทย์ให้ เพื่อให้แพทย์เห็นผลการเป่าของคุณ แพทย์ที่เชื่อมจะเห็นประวัติของคุณทั้งหมด เลิกเชื่อมได้ทุกเมื่อ','Enter the doctor code (e.g. DR-AB12) you were given so that doctor can see your results. A linked doctor sees your whole history. You can unlink any time.')}</p>
    <div class="row"><input id="m_code" placeholder="DR-XXXX" style="max-width:180px"><button class="b pri" id="m_link">${L0('เชื่อมต่อ','Link')}</button>${doc?`<button class="b danger" id="m_unlink">${L0('เลิกเชื่อม','Unlink')}</button>`:''}</div><div id="m_lmsg" class="note" style="margin-top:6px"></div></div></div>`;
  $('m_save').onclick=async()=>{const g=k=>$(k).value.trim();const name=g('m_name');if(name.length<2)return;
    await SP.Users.update(ME.id,{name,meta:{...m,sex:g('m_sex'),age:+g('m_age')||'',ht:+g('m_ht')||'',wt:+g('m_wt')||'',smk:g('m_smk'),pf:+g('m_pf')||'',pv:+g('m_pv')||''}});
    const nu=await SP.Users.get(ME.id);patients=[recOf(nu,'')];patients[0].self=true;$('m_msg').textContent=L0('บันทึกแล้ว','Saved')};
  const setDoc=async(id,name)=>{await SP.Users.update(ME.id,{doctorId:id,doctorName:name||''});await SP.Tests.setDoctor(ME.id,id);await SP.Audit.add(id?'link_doctor':'unlink_doctor',id);renderMe()};
  $('m_link').onclick=async()=>{const d=await SP.Users.doctorByCode($('m_code').value);if(!d){$('m_lmsg').textContent=L0('ไม่พบรหัสแพทย์นี้ (หรือบัญชียังไม่ได้อนุมัติ)','Doctor code not found (or not approved)');return}setDoc(d.id,d.name)};
  if($('m_unlink'))$('m_unlink').onclick=()=>setDoc('');
  $('m_pwgo').onclick=async()=>{try{await SP.Auth.changePassword(ME.id,$('m_pw').value,$('m_pw0').value);$('m_pw').value='';$('m_pw0').value='';alert(L0('เปลี่ยนรหัสผ่านแล้ว','Password changed'))}catch(e){alert(e.message)}};
  $('m_exp').onclick=async()=>dl('my_spirometry.json',JSON.stringify({profile:SP.Users.publicView(await SP.Users.get(ME.id)),tests:await SP.Tests.forPatient(ME.id)}),'application/json');
  $('m_del').onclick=async()=>{const pw=prompt(L0('พิมพ์รหัสผ่านเพื่อยืนยันการลบบัญชีและผลตรวจทั้งหมด (ลบแล้วกู้คืนไม่ได้)','Type your password to delete your account and all results (cannot be undone)'));if(!pw)return;
    if(!(await SP.Auth.verify(ME.id,pw))){alert(L0('รหัสผ่านไม่ถูกต้อง','Wrong password'));return}
    await SP.Tests.removeAllFor(ME.id);await SP.Audit.add('self_delete',ME.id);await SP.Auth.deleteSelf(ME.id);location.href='login.html'}}

/* ---------- my devices (claim by the code shown on the device screen) ---------- */
async function renderMyDev(){
  const box=$('myDev');if(!box||DEMO_Q)return;
  let list=[];try{list=await SP.Devices.mine()}catch(e){}
  box.innerHTML=`<h2>${L0('เครื่องของฉัน','My devices')}</h2>
   <p class="note">${L0('กดปุ่มที่เครื่องค้าง 8 วินาที จอจะแสดงรหัสเครื่อง (เช่น SP-7K4QW-M2X9R) กรอกรหัสนั้นที่นี่เพื่อผูกเครื่องกับบัญชีนี้ ใครเห็นรหัสบนจอเครื่องเท่านั้นที่ผูกได้ ผลที่เป่าจากเครื่องนี้จะเข้าบัญชีของคุณ','Hold the device button for 8 seconds; the screen shows its code (e.g. SP-7K4QW-M2X9R). Enter it here to link the device to this account. Only someone who can see the device screen can claim it; results from this device go to your account.')}</p>
   <div class="row"><input id="dv_code" placeholder="SP-XXXXX-XXXXX" style="max-width:220px;text-transform:uppercase"><input id="dv_label" placeholder="${L0('ชื่อเรียก (ไม่บังคับ)','Nickname (optional)')}" style="max-width:220px"><button class="b pri" id="dv_add">${L0('ผูกเครื่อง','Link device')}</button></div>
   <div id="dv_msg" class="note" style="margin-top:6px"></div>
   <div style="overflow:auto;margin-top:8px"><table>${list.length?`<tr><th>${L0('รหัสเครื่อง','Code')}</th><th>${L0('ชื่อเรียก','Nickname')}</th><th>${L0('ผูกเมื่อ','Linked')}</th><th></th></tr>`+list.map(d=>`<tr><td><code>${esc(d.code)}</code></td><td>${esc(d.label||'–')}</td><td>${fdate(d.claimed)}</td><td><button class="b danger" data-un="${esc(d.code)}" style="padding:2px 9px">${L0('เลิกผูก','Unlink')}</button></td></tr>`).join(''):`<tr><td class="empty">${L0('ยังไม่มีเครื่องที่ผูกไว้','No linked devices yet')}</td></tr>`}</table></div>`;
  $('dv_add').onclick=async()=>{try{await SP.Devices.claim($('dv_code').value,$('dv_label').value);renderMyDev()}catch(e){$('dv_msg').textContent=e.message}};
  box.querySelectorAll('[data-un]').forEach(b=>b.onclick=async()=>{if(confirm(L0('เลิกผูกเครื่องนี้?','Unlink this device?'))){await SP.Devices.release(b.dataset.un);renderMyDev()}});
}
