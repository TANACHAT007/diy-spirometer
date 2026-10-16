/* CREDIT-STAMP: DIY IoT Spirometer - designed by Tanachat S. (TANACHAT007) / MEDTHAI - 2026 */
/* Spiro core: accounts, roles, shared data and audit log behind ONE async API (window.SP).
   Two back ends with the same methods:
   - cloud  : Firebase Auth + Cloud Firestore, chosen when firebase-config.js defines window.SP_FIREBASE.apiKey
   - local  : this browser's localStorage (demo / offline / clones without a Firebase project). NOT SECURE:
              a "password" only gates the UI, and users on different devices cannot see each other.
   PASSWORDS: in cloud mode they go only to Firebase Auth (salted hash held by Google); this app never stores, logs,
   exports or shows them. In local mode only a PBKDF2 hash+salt is kept, and it is stripped from every export. */
(function () {
  'use strict';
  const CFG = window.SP_FIREBASE || {};
  const CLOUD = !!CFG.apiKey;
  const LS = {
    get(k, d) { try { const v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } },
    set(k, v) { localStorage.setItem(k, JSON.stringify(v)); }
  };
  const K = { users: 'sp2_users', session: 'sp2_session', tests: 'sp2_tests', audit: 'sp2_audit', settings: 'sp2_settings' };
  const DEFAULTS = { registrationOpen: true, doctorNeedsApproval: true, announcement: '', hasAdmin: false };
  const rnd = (n) => Array.from(crypto.getRandomValues(new Uint8Array(n))).map(b => 'abcdefghjkmnpqrstuvwxyz23456789'[b % 31]).join('');
  const uid = () => 'u' + rnd(9);
  const hex = (buf) => Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
  const strip = (u) => { if (!u) return u; const { passHash, salt, ...rest } = u; return rest; };
  const checkPw = (pw) => { if (String(pw || '').length < 8) throw new Error('รหัสผ่านต้องยาวอย่างน้อย 8 ตัวอักษร'); };
  const checkProfile = (email, name) => {
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('อีเมลไม่ถูกต้อง');
    if (String(name || '').trim().length < 2) throw new Error('กรุณากรอกชื่อ');
  };
  const DEVRE = /^SP-[A-HJ-NP-Z2-9]{5}-[A-HJ-NP-Z2-9]{5}$/;     // 10 random chars (about 50 bits), printed on the device screen on request
  const normCode = (c) => String(c || '').trim().toUpperCase().replace(/\s+/g, '');
  const checkCode = (c) => { c = normCode(c); if (!DEVRE.test(c)) throw new Error('รหัสเครื่องไม่ถูกต้อง (รูปแบบ SP-XXXXX-XXXXX)'); return c; };
  const home = (u) => !u ? 'login.html' : u.role === 'admin' ? 'admin.html' : 'clinic.html';

  /* ================= LOCAL BACK END ================= */
  async function hashPw(pw, salt) {
    if (crypto.subtle) {
      const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveBits']);
      const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt: new TextEncoder().encode(salt), iterations: 100000, hash: 'SHA-256' }, key, 256);
      return 'pbkdf2$' + hex(bits);
    }
    let h = 5381; const s = salt + pw; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
    return 'weak$' + (h >>> 0).toString(16);
  }
  function makeLocal() {
    const Settings = {
      async get() { const s = Object.assign({}, DEFAULTS, LS.get(K.settings, {})); s.hasAdmin = LS.get(K.users, []).some(u => u.role === 'admin'); return s; },
      async set(patch) { const s = Object.assign(LS.get(K.settings, {}), patch); LS.set(K.settings, s); return this.get(); }
    };
    const Audit = {
      async add(action, detail, actor) { const a = LS.get(K.audit, []); a.push({ ts: Date.now(), actor: actor || (Auth.cur && Auth.cur.id) || '', action, detail: detail || '' }); LS.set(K.audit, a.slice(-500)); },
      async list() { return LS.get(K.audit, []).slice().reverse(); }
    };
    const Users = {
      async list() { return LS.get(K.users, []).map(strip); },
      async get(id) { return strip(LS.get(K.users, []).find(u => u.id === id) || null); },
      async update(id, patch) { const us = LS.get(K.users, []), u = us.find(x => x.id === id); if (!u) return null; Object.assign(u, patch); LS.set(K.users, us); if (Auth.cur && Auth.cur.id === id) Auth.cur = strip(u); return strip(u); },
      async remove(id) { LS.set(K.users, LS.get(K.users, []).filter(u => u.id !== id)); },
      async doctorByCode(code) { code = String(code || '').trim().toUpperCase(); const d = LS.get(K.users, []).find(u => u.role === 'doctor' && u.code === code && u.status === 'active'); return d ? { id: d.id, name: d.name, code: d.code } : null; },
      async linkedPatients(doctorId) { return LS.get(K.users, []).filter(u => u.role === 'patient' && u.doctorId === doctorId).map(strip); },
      async adminCreate({ email, name, role, extra }) {
        const pw = rnd(10), u = await Auth.register({ email, name, password: pw, role, extra: extra || {}, adminCreate: true });
        const patch = { status: 'active' }; if (role === 'admin') patch.role = 'admin'; await this.update(u.id, patch);
        return { user: await this.get(u.id), tempPassword: pw };
      },
      publicView: strip
    };
    const Auth = {
      cur: null, mode: 'local',
      async init() { const s = LS.get(K.session, null); const u = s ? await Users.get(s.uid) : null; this.cur = u && u.status !== 'disabled' ? u : null; return this.cur; },
      async hasAdmin() { return LS.get(K.users, []).some(u => u.role === 'admin'); },
      async register({ email, name, password, role, extra, adminCreate }) {
        email = String(email || '').trim().toLowerCase(); name = String(name || '').trim(); checkProfile(email, name); checkPw(password);
        const us = LS.get(K.users, []);
        if (us.find(u => u.email === email)) throw new Error('อีเมลนี้ถูกใช้แล้ว');
        const st = await Settings.get(), firstAdmin = !us.some(u => u.role === 'admin');
        if (!firstAdmin && !st.registrationOpen && !adminCreate) throw new Error('ระบบปิดรับสมัครชั่วคราว');
        role = firstAdmin ? 'admin' : (role === 'doctor' ? 'doctor' : 'patient');
        const salt = rnd(16);
        const u = { id: uid(), email, name, role, salt, passHash: await hashPw(password, salt), created: Date.now(), lastLogin: 0,
          status: role === 'doctor' && st.doctorNeedsApproval ? 'pending' : 'active', meta: extra || {} };
        if (role === 'doctor') u.code = 'DR-' + rnd(4).toUpperCase();
        if (role === 'patient' && u.meta.doctorCode) { const d = await Users.doctorByCode(u.meta.doctorCode); if (d) { u.doctorId = d.id; u.doctorName = d.name; } delete u.meta.doctorCode; }
        us.push(u); LS.set(K.users, us); await Audit.add('register', role + ' ' + email, u.id); return strip(u);
      },
      async login(email, password) {
        email = String(email || '').trim().toLowerCase();
        const raw = LS.get(K.users, []).find(u => u.email === email);
        if (!raw || (await hashPw(password, raw.salt)) !== raw.passHash) { await Audit.add('login_fail', email); throw new Error('อีเมลหรือรหัสผ่านไม่ถูกต้อง'); }
        if (raw.status === 'disabled') throw new Error('บัญชีนี้ถูกระงับ ติดต่อผู้ดูแลระบบ');
        await Users.update(raw.id, { lastLogin: Date.now() }); LS.set(K.session, { uid: raw.id, ts: Date.now() });
        this.cur = await Users.get(raw.id); await Audit.add('login', email, raw.id); return this.cur;
      },
      async logout() { if (this.cur) await Audit.add('logout', this.cur.email); localStorage.removeItem(K.session); this.cur = null; },
      async changePassword(id, newPw, oldPw) {
        checkPw(newPw); if (oldPw !== undefined && !(await this.verify(id, oldPw))) throw new Error('รหัสผ่านปัจจุบันไม่ถูกต้อง');
        const salt = rnd(16); await Users.update(id, { salt, passHash: await hashPw(newPw, salt) }); await Audit.add('password_change', id);
      },
      async adminSetPassword(id, newPw) { return this.changePassword(id, newPw); },
      async verify(id, pw) { const u = LS.get(K.users, []).find(x => x.id === id); return !!u && (await hashPw(pw, u.salt)) === u.passHash; },
      async sendReset() { throw new Error('โหมดเครื่องนี้ไม่มีการส่งอีเมล ให้แอดมินตั้งรหัสผ่านใหม่'); },
      async deleteSelf(id) { await Users.remove(id); localStorage.removeItem(K.session); this.cur = null; }
    };
    const Tests = {
      async all() { return LS.get(K.tests, []); },
      async add(rec) { const a = LS.get(K.tests, []); a.push(rec); LS.set(K.tests, a); },
      async forPatient(id) { return LS.get(K.tests, []).filter(t => t.patientUid === id); },
      async forDoctor(id) { return LS.get(K.tests, []).filter(t => t.doctorUid === id); },
      async setDoctor(patientUid, doctorUid) { const a = LS.get(K.tests, []); a.forEach(t => { if (t.patientUid === patientUid) t.doctorUid = doctorUid; }); LS.set(K.tests, a); },
      async removeAllFor(patientUid) { LS.set(K.tests, LS.get(K.tests, []).filter(t => t.patientUid !== patientUid)); },
      async remove(id) { LS.set(K.tests, LS.get(K.tests, []).filter(t => t.id !== id)); }
    };
    const K_DEV = 'sp2_devices';
    const Devices = {
      async mine() { const me = Auth.cur && Auth.cur.id; return LS.get(K_DEV, []).filter(d => d.owner === me); },
      async all() { return LS.get(K_DEV, []); },
      async claim(code, label) {
        code = checkCode(code); const me = Auth.cur && Auth.cur.id; if (!me) throw new Error('ต้องเข้าสู่ระบบก่อน');
        const a = LS.get(K_DEV, []); if (a.find(d => d.code === code)) throw new Error('รหัสเครื่องนี้ถูกผูกกับบัญชีอื่นแล้ว');
        a.push({ code, owner: me, label: String(label || '').slice(0, 60), claimed: Date.now() }); LS.set(K_DEV, a); await Audit.add('device_claim', code);
      },
      async release(code) { const me = Auth.cur && Auth.cur.id; LS.set(K_DEV, LS.get(K_DEV, []).filter(d => !(d.code === code && (d.owner === me || (Auth.cur && Auth.cur.role === 'admin'))))); await Audit.add('device_release', code); }
    };
    const K_PLAN = 'sp2_plans', K_TRN = 'sp2_trainings';
    const Plans = {
      async forPatient(id) { return LS.get(K_PLAN, []).filter(p => p.patientUid === id); },
      async forDoctor(id) { return LS.get(K_PLAN, []).filter(p => p.doctorUid === id); },
      async save(plan) { const a = LS.get(K_PLAN, []); const i = a.findIndex(p => p.id === plan.id); if (i >= 0) a[i] = plan; else a.push(plan); LS.set(K_PLAN, a); await Audit.add('plan_save', plan.patientUid); },
      async remove(id) { LS.set(K_PLAN, LS.get(K_PLAN, []).filter(p => p.id !== id)); }
    };
    const Trainings = {
      async forPatient(id) { return LS.get(K_TRN, []).filter(t => t.patientUid === id); },
      async forDoctor(id) { return LS.get(K_TRN, []).filter(t => t.doctorUid === id); },
      async add(rec) { const a = LS.get(K_TRN, []); a.push(rec); LS.set(K_TRN, a); },
      async removeAllFor(id) { LS.set(K_TRN, LS.get(K_TRN, []).filter(t => t.patientUid !== id)); LS.set(K_PLAN, LS.get(K_PLAN, []).filter(p => p.patientUid !== id)); }
    };
    const Data = {
      async exportAll() { return { v: 2, ts: Date.now(), note: 'credentials are never exported', users: LS.get(K.users, []).map(strip), tests: LS.get(K.tests, []), audit: LS.get(K.audit, []), settings: LS.get(K.settings, {}) }; },
      async importAll(j) {
        if (!j || !Array.isArray(j.users)) throw new Error('ไฟล์ไม่ถูกต้อง');
        const us = LS.get(K.users, []), ts = LS.get(K.tests, []);
        for (const u of j.users) if (!us.find(x => x.id === u.id || x.email === u.email)) us.push(Object.assign({ salt: rnd(16), passHash: 'imported-needs-reset' }, u));
        for (const t of (j.tests || [])) if (!ts.find(x => x.id === t.id)) ts.push(t);
        LS.set(K.users, us); LS.set(K.tests, ts);
      },
      async wipe() { Object.values(K).forEach(k => localStorage.removeItem(k)); Object.keys(localStorage).filter(k => /^sp_(patients|tests|active|cfg)_/.test(k)).forEach(k => localStorage.removeItem(k)); },
      usage() { let n = 0; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); n += k.length + (localStorage.getItem(k) || '').length; } return n * 2; }
    };
    return { Auth, Users, Tests, Audit, Settings, Data, Devices, Plans, Trainings };
  }

  /* ================= CLOUD BACK END (Firebase Auth + Firestore) ================= */
  const SDK = 'https://www.gstatic.com/firebasejs/10.12.2/';
  const loadJs = (src) => new Promise((res, rej) => { const s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = () => rej(new Error('โหลด Firebase ไม่ได้: ' + src)); document.head.appendChild(s); });
  async function makeCloud() {
    for (const f of ['firebase-app-compat.js', 'firebase-auth-compat.js', 'firebase-firestore-compat.js']) await loadJs(SDK + f);
    const fb = window.firebase; fb.initializeApp(CFG);
    const auth = fb.auth(), db = fb.firestore(), FV = fb.firestore.FieldValue;
    const col = (n) => db.collection(n);
    const snap = (d) => d && d.exists ? Object.assign({ id: d.id }, d.data()) : null;
    const all = async (q) => (await q.get()).docs.map(snap);
    const E = (e) => { const m = { 'auth/email-already-in-use': 'อีเมลนี้ถูกใช้แล้ว', 'auth/invalid-credential': 'อีเมลหรือรหัสผ่านไม่ถูกต้อง', 'auth/wrong-password': 'อีเมลหรือรหัสผ่านไม่ถูกต้อง', 'auth/user-not-found': 'อีเมลหรือรหัสผ่านไม่ถูกต้อง', 'auth/too-many-requests': 'ลองหลายครั้งเกินไป รอสักครู่แล้วลองใหม่', 'auth/weak-password': 'รหัสผ่านอ่อนเกินไป', 'auth/invalid-email': 'อีเมลไม่ถูกต้อง', 'auth/requires-recent-login': 'ต้องยืนยันรหัสผ่านใหม่อีกครั้ง', 'auth/network-request-failed': 'เชื่อมต่ออินเทอร์เน็ตไม่ได้' }[e.code]; return new Error(m || (e.code === 'permission-denied' || /permission/i.test(e.message || '') ? 'ไม่มีสิทธิ์ทำรายการนี้' : e.message)); };
    const guard = (fn) => async (...a) => { try { return await fn(...a); } catch (e) { throw E(e); } };
    const waitUser = () => new Promise(res => { const off = auth.onAuthStateChanged(u => { off(); res(u); }); });

    const Settings = {
      get: guard(async () => { const d = snap(await col('settings').doc('public').get()); return Object.assign({}, DEFAULTS, d || {}); }),
      set: guard(async (patch) => { await col('settings').doc('public').set(patch, { merge: true }); return Settings.get(); })
    };
    const Audit = {
      async add(action, detail, actor) { try { await col('audit').add({ ts: Date.now(), actor: actor || (auth.currentUser && auth.currentUser.uid) || '', action, detail: String(detail || '').slice(0, 300) }); } catch (e) { /* audit must never block the user */ } },
      list: guard(async () => (await all(col('audit').orderBy('ts', 'desc').limit(200))))
    };
    const syncCode = async (u) => {              // doctorCodes/{code} exists only while the doctor is approved
      if (!u || u.role !== 'doctor' || !u.code) return;
      const ref = col('doctorCodes').doc(u.code);
      if (u.status === 'active') await ref.set({ uid: u.id, name: u.name }); else await ref.delete();
    };
    const Users = {
      list: guard(async () => all(col('users'))),
      get: guard(async (id) => snap(await col('users').doc(id).get())),
      update: guard(async (id, patch) => {
        await col('users').doc(id).set(patch, { merge: true }); const u = snap(await col('users').doc(id).get());
        if (Auth.cur && Auth.cur.id === id) Auth.cur = u;
        if (Auth.cur && Auth.cur.role === 'admin' && ('status' in patch || 'role' in patch || 'name' in patch)) await syncCode(u);
        return u;
      }),
      remove: guard(async (id) => { const u = snap(await col('users').doc(id).get()); if (u && u.code) await col('doctorCodes').doc(u.code).delete().catch(() => {}); await col('users').doc(id).delete(); }),
      doctorByCode: guard(async (code) => { code = String(code || '').trim().toUpperCase(); if (!/^DR-[A-Z0-9]{4}$/.test(code)) return null; const d = snap(await col('doctorCodes').doc(code).get()); return d ? { id: d.uid, name: d.name, code } : null; }),
      linkedPatients: guard(async (doctorId) => all(col('users').where('doctorId', '==', doctorId))),
      adminCreate: guard(async ({ email, name, role, extra }) => {
        email = String(email || '').trim().toLowerCase(); checkProfile(email, name);
        const sec = fb.apps.find(a => a.name === 'secondary') || fb.initializeApp(CFG, 'secondary'), sa = sec.auth();
        const cred = await sa.createUserWithEmailAndPassword(email, rnd(12) + 'A1');      // random, never shown: the user sets their own via the reset e-mail
        const id = cred.user.uid; await sa.signOut();
        const u = { email, name: String(name).trim(), role: ['admin', 'doctor'].includes(role) ? role : 'patient', status: 'active', created: Date.now(), lastLogin: 0, meta: extra || {} };
        if (u.role === 'doctor') u.code = 'DR-' + rnd(4).toUpperCase();
        await col('users').doc(id).set(u); await auth.sendPasswordResetEmail(email); await syncCode(Object.assign({ id }, u));
        await Audit.add('admin_create', u.role + ' ' + email); return { user: Object.assign({ id }, u), resetSent: true };
      }),
      publicView: strip
    };
    const Auth = {
      cur: null, mode: 'cloud',
      init: guard(async () => { const fu = await waitUser(); if (!fu) { Auth.cur = null; return null; } const u = snap(await col('users').doc(fu.uid).get()); if (!u || u.status === 'disabled') { await auth.signOut(); Auth.cur = null; return null; } Auth.cur = u; return u; }),
      async hasAdmin() { const s = await Settings.get(); return !!s.hasAdmin; },
      register: guard(async ({ email, name, password, role, extra }) => {
        email = String(email || '').trim().toLowerCase(); name = String(name || '').trim(); checkProfile(email, name); checkPw(password);
        const st = await Settings.get(); if (!st.registrationOpen) throw new Error('ระบบปิดรับสมัครชั่วคราว');
        role = role === 'doctor' ? 'doctor' : 'patient'; extra = Object.assign({}, extra || {});
        const cred = await auth.createUserWithEmailAndPassword(email, password), id = cred.user.uid;
        const u = { email, name, role, status: role === 'doctor' ? 'pending' : 'active', created: Date.now(), lastLogin: 0, meta: extra };
        if (role === 'doctor') u.code = 'DR-' + rnd(4).toUpperCase();
        if (role === 'patient' && extra.doctorCode) { const d = await Users.doctorByCode(extra.doctorCode); if (d) { u.doctorId = d.id; u.doctorName = d.name; } delete u.meta.doctorCode; }
        delete u.meta.doctorCode;
        await col('users').doc(id).set(u); Auth.cur = Object.assign({ id }, u); await Audit.add('register', role, id); return Auth.cur;
      }),
      login: guard(async (email, password) => {
        const cred = await auth.signInWithEmailAndPassword(String(email || '').trim(), password); const u = snap(await col('users').doc(cred.user.uid).get());
        if (!u) { await auth.signOut(); throw new Error('บัญชีนี้ไม่มีข้อมูลโปรไฟล์ ติดต่อผู้ดูแลระบบ'); }
        if (u.status === 'disabled') { await auth.signOut(); throw new Error('บัญชีนี้ถูกระงับ ติดต่อผู้ดูแลระบบ'); }
        await col('users').doc(u.id).set({ lastLogin: Date.now() }, { merge: true }); Auth.cur = u; await Audit.add('login', '', u.id); return u;
      }),
      async logout() { await auth.signOut(); Auth.cur = null; },
      changePassword: guard(async (id, newPw, oldPw) => {
        checkPw(newPw); const fu = auth.currentUser; if (!fu || fu.uid !== id) throw new Error('เปลี่ยนรหัสผ่านได้เฉพาะบัญชีของตัวเอง');
        if (!oldPw) throw new Error('กรอกรหัสผ่านปัจจุบันก่อน');
        await fu.reauthenticateWithCredential(fb.auth.EmailAuthProvider.credential(fu.email, oldPw)); await fu.updatePassword(newPw); await Audit.add('password_change', '', id);
      }),
      async adminSetPassword() { throw new Error('โหมดคลาวด์ไม่ให้แอดมินตั้งรหัสผ่านแทนผู้ใช้ ใช้การส่งอีเมลรีเซ็ตแทน'); },
      verify: guard(async (id, pw) => { const fu = auth.currentUser; if (!fu || fu.uid !== id) return false; try { await fu.reauthenticateWithCredential(fb.auth.EmailAuthProvider.credential(fu.email, pw)); return true; } catch (e) { return false; } }),
      sendReset: guard(async (email) => { await auth.sendPasswordResetEmail(String(email || '').trim()); await Audit.add('reset_email', ''); }),
      deleteSelf: guard(async (id) => { const fu = auth.currentUser; await Users.remove(id); await fu.delete(); Auth.cur = null; })
    };
    const Tests = {
      all: guard(async () => all(col('tests').orderBy('ts', 'desc').limit(1000))),
      add: guard(async (rec) => { await col('tests').doc(rec.id).set(rec); }),
      forPatient: guard(async (id) => all(col('tests').where('patientUid', '==', id))),
      forDoctor: guard(async (id) => all(col('tests').where('doctorUid', '==', id))),
      setDoctor: guard(async (patientUid, doctorUid) => { const rs = await all(col('tests').where('patientUid', '==', patientUid)); const b = db.batch(); rs.forEach(r => b.update(col('tests').doc(r.id), { doctorUid })); await b.commit(); }),
      removeAllFor: guard(async (patientUid) => { const rs = await all(col('tests').where('patientUid', '==', patientUid)); const b = db.batch(); rs.forEach(r => b.delete(col('tests').doc(r.id))); await b.commit(); }),
      remove: guard(async (id) => { await col('tests').doc(id).delete(); })
    };
    const Devices = {
      mine: guard(async () => all(col('devices').where('owner', '==', auth.currentUser.uid))),
      all: guard(async () => all(col('devices'))),
      claim: guard(async (code, label) => {
        code = checkCode(code); const me = auth.currentUser; if (!me) throw new Error('ต้องเข้าสู่ระบบก่อน');
        const ref = col('devices').doc(code);
        try { await ref.set({ code, owner: me.uid, label: String(label || '').slice(0, 60), claimed: Date.now() }); }
        catch (e) { throw new Error('ผูกเครื่องไม่สำเร็จ: รหัสนี้อาจถูกผูกกับบัญชีอื่นแล้ว หรือรหัสไม่ถูกต้อง'); }
        await Audit.add('device_claim', code);
      }),
      release: guard(async (code) => { await col('devices').doc(code).delete(); await Audit.add('device_release', code); })
    };
    const Plans = {
      forPatient: guard(async (id) => all(col('plans').where('patientUid', '==', id))),
      forDoctor: guard(async (id) => all(col('plans').where('doctorUid', '==', id))),
      save: guard(async (plan) => { await col('plans').doc(plan.id).set(plan); await Audit.add('plan_save', plan.patientUid); }),
      remove: guard(async (id) => { await col('plans').doc(id).delete(); })
    };
    const Trainings = {
      forPatient: guard(async (id) => all(col('trainings').where('patientUid', '==', id))),
      forDoctor: guard(async (id) => all(col('trainings').where('doctorUid', '==', id))),
      add: guard(async (rec) => { await col('trainings').doc(rec.id).set(rec); }),
      removeAllFor: guard(async (id) => {
        for (const c of ['trainings', 'plans']) { const rs = await all(col(c).where('patientUid', '==', id)); const b = db.batch(); rs.forEach(x => b.delete(col(c).doc(x.id))); await b.commit(); }
      })
    };
    const Data = {
      exportAll: guard(async () => ({ v: 2, ts: Date.now(), note: 'credentials are held by Firebase Auth and never exported', users: await Users.list(), tests: await Tests.all(), audit: await Audit.list(), settings: await Settings.get() })),
      importAll: guard(async (j) => { if (!j || !Array.isArray(j.tests)) throw new Error('ไฟล์ไม่ถูกต้อง'); for (const t of j.tests) if (t.id) await col('tests').doc(t.id).set(t, { merge: true }); }),
      async wipe() { throw new Error('โหมดคลาวด์: ลบข้อมูลทั้งหมดจาก Firebase Console เท่านั้น'); },
      usage() { return 0; }
    };
    return { Auth, Users, Tests, Audit, Settings, Data, Devices, Plans, Trainings };
  }

  /* ================= facade: pages call SP.* synchronously-available, methods wait for the back end ================= */
  const impl = {};
  const ready = (CLOUD ? makeCloud() : Promise.resolve(makeLocal())).then(m => { impl.m = m; return m; });
  const names = {
    Auth: ['init', 'hasAdmin', 'register', 'login', 'logout', 'changePassword', 'adminSetPassword', 'verify', 'sendReset', 'deleteSelf'],
    Users: ['list', 'get', 'update', 'remove', 'doctorByCode', 'linkedPatients', 'adminCreate'],
    Tests: ['all', 'add', 'forPatient', 'forDoctor', 'setDoctor', 'removeAllFor', 'remove'],
    Audit: ['add', 'list'], Settings: ['get', 'set'], Data: ['exportAll', 'importAll', 'wipe'],
    Devices: ['mine', 'all', 'claim', 'release'],
    Plans: ['forPatient', 'forDoctor', 'save', 'remove'],
    Trainings: ['forPatient', 'forDoctor', 'add', 'removeAllFor']
  };
  const SP = { mode: CLOUD ? 'cloud' : 'local', ready, rnd, uid, K, CFG };
  for (const g in names) { SP[g] = {}; for (const n of names[g]) SP[g][n] = async (...a) => (await ready)[g][n](...a); }
  Object.defineProperty(SP.Auth, 'cur', { get() { return impl.m ? impl.m.Auth.cur : null; }, set(v) { if (impl.m) impl.m.Auth.cur = v; } });
  SP.Auth.mode = SP.mode; SP.Auth.home = home;
  SP.Users.publicView = strip;
  SP.Data.usage = () => { try { return makeLocal().Data.usage(); } catch (e) { return 0; } };
  SP.Auth.require = async function (roles) {
    const u = await SP.Auth.init();
    if (!u) { location.replace('login.html?next=' + encodeURIComponent(location.pathname.split('/').pop() + location.search)); return new Promise(() => {}); }
    if (roles && !roles.includes(u.role)) { location.replace(home(u)); return new Promise(() => {}); }
    return u;
  };
  SP.normCode = normCode; SP.DEVRE = DEVRE;
  window.SP = SP;
})();
