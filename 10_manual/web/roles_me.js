/* ---------- my profile (patient) ---------- */
async function renderMe(){
  const u=await SP.Users.get(ME.id),m=u.meta||{},doc=u.doctorId?await SP.Users.get(u.doctorId):null;
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
    <div class="form"><label>${L0('รหัสผ่านใหม่ (≥ 8 ตัว)','New password (≥ 8)')}<input id="m_pw" type="password" autocomplete="new-password"></label></div>
    <div class="row" style="margin-top:10px"><button class="b" id="m_pwgo">${L0('เปลี่ยนรหัสผ่าน','Change password')}</button><button class="b" id="m_exp">${t('exp')}</button><button class="b danger" id="m_del">${L0('ลบบัญชีและข้อมูลของฉัน','Delete my account and data')}</button></div></div></div>
   <div class="card"><h2>${L0('แชร์ผลกับแพทย์','Share with a doctor')}</h2>
    <p>${doc?L0('แพทย์ผู้ดูแล','Your doctor')+': <b>'+esc(doc.name)+'</b>':L0('ยังไม่ได้เชื่อมกับแพทย์','Not linked to a doctor')}</p>
    <p class="note">${L0('ใส่รหัสแพทย์ (เช่น DR-AB12) ที่แพทย์ให้ เพื่อให้แพทย์เห็นผลการเป่าของคุณ แพทย์ที่เชื่อมจะเห็นประวัติของคุณทั้งหมด เลิกเชื่อมได้ทุกเมื่อ','Enter the doctor code (e.g. DR-AB12) you were given so that doctor can see your results. A linked doctor sees your whole history. You can unlink any time.')}</p>
    <div class="row"><input id="m_code" placeholder="DR-XXXX" style="max-width:180px"><button class="b pri" id="m_link">${L0('เชื่อมต่อ','Link')}</button>${doc?`<button class="b danger" id="m_unlink">${L0('เลิกเชื่อม','Unlink')}</button>`:''}</div><div id="m_lmsg" class="note" style="margin-top:6px"></div></div></div>`;
  $('m_save').onclick=async()=>{const g=k=>$(k).value.trim();const name=g('m_name');if(name.length<2)return;
    await SP.Users.update(ME.id,{name,meta:{...m,sex:g('m_sex'),age:+g('m_age')||'',ht:+g('m_ht')||'',wt:+g('m_wt')||'',smk:g('m_smk'),pf:+g('m_pf')||'',pv:+g('m_pv')||''}});
    const nu=await SP.Users.get(ME.id);patients=[recOf(nu,'')];patients[0].self=true;$('m_msg').textContent=L0('บันทึกแล้ว','Saved')};
  const setDoc=async id=>{await SP.Users.update(ME.id,{doctorId:id});const mine=await SP.Tests.forPatient(ME.id);mine.forEach(x=>x.doctorUid=id);await SP.Tests.replaceFor(ME.id,mine);await SP.Audit.add(id?'link_doctor':'unlink_doctor',id);renderMe()};
  $('m_link').onclick=async()=>{const d=await SP.Users.doctorByCode($('m_code').value);if(!d){$('m_lmsg').textContent=L0('ไม่พบรหัสแพทย์นี้ (หรือบัญชียังไม่ได้อนุมัติ)','Doctor code not found (or not approved)');return}setDoc(d.id)};
  if($('m_unlink'))$('m_unlink').onclick=()=>setDoc('');
  $('m_pwgo').onclick=async()=>{try{await SP.Auth.changePassword(ME.id,$('m_pw').value);$('m_pw').value='';alert(L0('เปลี่ยนรหัสผ่านแล้ว','Password changed'))}catch(e){alert(e.message)}};
  $('m_exp').onclick=async()=>dl('my_spirometry.json',JSON.stringify({profile:SP.Users.publicView(await SP.Users.get(ME.id)),tests:await SP.Tests.forPatient(ME.id)}),'application/json');
  $('m_del').onclick=async()=>{const pw=prompt(L0('พิมพ์รหัสผ่านเพื่อยืนยันการลบบัญชีและผลตรวจทั้งหมด (ลบแล้วกู้คืนไม่ได้)','Type your password to delete your account and all results (cannot be undone)'));if(!pw)return;
    if(!(await SP.Auth.verify(ME.id,pw))){alert(L0('รหัสผ่านไม่ถูกต้อง','Wrong password'));return}
    await SP.Tests.replaceFor(ME.id,[]);await SP.Audit.add('self_delete',ME.id);await SP.Users.remove(ME.id);await SP.Auth.logout();location.href='login.html'}}
