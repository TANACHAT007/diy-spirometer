/* CREDIT-STAMP: DIY IoT Spirometer - designed by Tanachat S. (TANACHAT007) / MEDTHAI - 2026 */
/* Spiro core: accounts, roles, shared data and audit log.
   ALL functions are async and go through one adapter, so the local (browser) store can later be swapped for Firebase
   (Auth + Realtime DB / Firestore) without touching the pages. See FIREBASE_MIGRATION.md.
   LOCAL MODE IS NOT SECURE: data lives in this browser's localStorage, a "password" only gates the UI, and users on
   different devices cannot see each other's data. It is for demos and development until the cloud adapter exists. */
(function () {
  'use strict';
  const LS = {
    get(k, d) { try { const v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } },
    set(k, v) { localStorage.setItem(k, JSON.stringify(v)); }
  };
  const K = { users: 'sp2_users', session: 'sp2_session', tests: 'sp2_tests', audit: 'sp2_audit', settings: 'sp2_settings' };
  const DEFAULTS = {
    mode: 'local',                 // 'local' now; 'firebase' once the adapter is written
    registrationOpen: true,        // anyone may create a patient account
    doctorNeedsApproval: true,     // new doctor accounts wait for an admin
    announcement: '',              // shown on the login page
    firebase: { apiKey: '', authDomain: '', databaseURL: '', projectId: '', appId: '' }
  };
  const rnd = (n) => Array.from(crypto.getRandomValues(new Uint8Array(n))).map(b => 'abcdefghjkmnpqrstuvwxyz23456789'[b % 31]).join('');
  const uid = () => 'u' + rnd(9);
  const hex = (buf) => Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');

  async function hashPw(pw, salt) {
    if (crypto.subtle) {
      const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveBits']);
      const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt: new TextEncoder().encode(salt), iterations: 100000, hash: 'SHA-256' }, key, 256);
      return 'pbkdf2$' + hex(bits);
    }
    let h = 5381; const s = salt + pw; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
    return 'weak$' + (h >>> 0).toString(16);       // only when the page is not a secure context
  }

  const Settings = {
    async get() { return Object.assign({}, DEFAULTS, LS.get(K.settings, {})); },
    async set(patch) { const s = Object.assign(await this.get(), patch); LS.set(K.settings, s); return s; }
  };

  const Audit = {
    async add(action, detail, actor) {
      const a = LS.get(K.audit, []); a.push({ ts: Date.now(), actor: actor || (Auth.cur && Auth.cur.id) || '', action, detail: detail || '' });
      LS.set(K.audit, a.slice(-500));
    },
    async list() { return LS.get(K.audit, []).slice().reverse(); }
  };

  const Users = {
    async list() { return LS.get(K.users, []); },
    async get(id) { return (await this.list()).find(u => u.id === id) || null; },
    async byEmail(email) { email = String(email || '').trim().toLowerCase(); return (await this.list()).find(u => u.email === email) || null; },
    async update(id, patch) { const us = await this.list(), u = us.find(x => x.id === id); if (!u) return null; Object.assign(u, patch); LS.set(K.users, us); if (Auth.cur && Auth.cur.id === id) Auth.cur = u; return u; },
    async remove(id) { LS.set(K.users, (await this.list()).filter(u => u.id !== id)); },
    async doctorByCode(code) { code = String(code || '').trim().toUpperCase(); return (await this.list()).find(u => u.role === 'doctor' && u.code === code && u.status === 'active') || null; },
    publicView(u) { if (!u) return null; const { passHash, salt, ...rest } = u; return rest; }
  };

  const Auth = {
    cur: null,
    async init() { const s = LS.get(K.session, null); this.cur = s ? await Users.get(s.uid) : null; if (this.cur && this.cur.status === 'disabled') { this.cur = null; } return this.cur; },
    async hasAdmin() { return (await Users.list()).some(u => u.role === 'admin'); },
    async register({ email, name, password, role, extra, adminCreate }) {
      email = String(email || '').trim().toLowerCase(); name = String(name || '').trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('อีเมลไม่ถูกต้อง');
      if (name.length < 2) throw new Error('กรุณากรอกชื่อ');
      if (String(password || '').length < 8) throw new Error('รหัสผ่านต้องยาวอย่างน้อย 8 ตัวอักษร');
      if (await Users.byEmail(email)) throw new Error('อีเมลนี้ถูกใช้แล้ว');
      const st = await Settings.get(), firstAdmin = !(await this.hasAdmin());
      if (!firstAdmin && !st.registrationOpen && !adminCreate) throw new Error('ระบบปิดรับสมัครชั่วคราว');
      role = firstAdmin ? 'admin' : (role === 'doctor' ? 'doctor' : 'patient');
      const salt = rnd(16), us = await Users.list();
      const u = { id: uid(), email, name, role, salt, passHash: await hashPw(password, salt), created: Date.now(), lastLogin: 0,
        status: role === 'doctor' && st.doctorNeedsApproval ? 'pending' : 'active', meta: extra || {} };
      if (role === 'doctor') u.code = 'DR-' + rnd(4).toUpperCase();
      if (role === 'patient' && u.meta.doctorCode) {
        const d = await Users.doctorByCode(u.meta.doctorCode); u.doctorId = d ? d.id : ''; delete u.meta.doctorCode;
      }
      us.push(u); LS.set(K.users, us);
      await Audit.add('register', role + ' ' + email, u.id);
      return u;
    },
    async login(email, password) {
      const u = await Users.byEmail(email);
      if (!u || (await hashPw(password, u.salt)) !== u.passHash) { await Audit.add('login_fail', String(email)); throw new Error('อีเมลหรือรหัสผ่านไม่ถูกต้อง'); }
      if (u.status === 'disabled') throw new Error('บัญชีนี้ถูกระงับ ติดต่อผู้ดูแลระบบ');
      u.lastLogin = Date.now(); await Users.update(u.id, { lastLogin: u.lastLogin });
      LS.set(K.session, { uid: u.id, ts: Date.now() }); this.cur = u; await Audit.add('login', u.email, u.id); return u;
    },
    async logout() { if (this.cur) await Audit.add('logout', this.cur.email); localStorage.removeItem(K.session); this.cur = null; },
    async changePassword(id, newPw) { if (String(newPw).length < 8) throw new Error('รหัสผ่านต้องยาวอย่างน้อย 8 ตัวอักษร'); const salt = rnd(16); await Users.update(id, { salt, passHash: await hashPw(newPw, salt) }); await Audit.add('password_change', id); },
    async verify(id, pw) { const u = await Users.get(id); return !!u && (await hashPw(pw, u.salt)) === u.passHash; },
    home(u) { return !u ? 'login.html' : u.role === 'admin' ? 'admin.html' : 'clinic.html'; },
    /* page guard: await Auth.require(['doctor','patient']) -> user, or redirects */
    async require(roles) {
      const u = await this.init();
      if (!u) { location.replace('login.html?next=' + encodeURIComponent(location.pathname.split('/').pop() + location.search)); return new Promise(() => {}); }
      if (roles && !roles.includes(u.role)) { location.replace(this.home(u)); return new Promise(() => {}); }
      return u;
    }
  };

  /* shared test results (patients' self tests, and anything a doctor wants linked to an account) */
  const Tests = {
    async all() { return LS.get(K.tests, []); },
    async add(rec) { const a = await this.all(); a.push(rec); LS.set(K.tests, a); },
    async replaceFor(patientUid, mine) { const a = (await this.all()).filter(t => t.patientUid !== patientUid).concat(mine); LS.set(K.tests, a); },
    async forPatient(id) { return (await this.all()).filter(t => t.patientUid === id); },
    async forDoctor(id) { return (await this.all()).filter(t => t.doctorUid === id); },
    async remove(id) { LS.set(K.tests, (await this.all()).filter(t => t.id !== id)); }
  };

  const Data = {
    async exportAll() { return { v: 2, ts: Date.now(), users: LS.get(K.users, []), tests: LS.get(K.tests, []), audit: LS.get(K.audit, []), settings: LS.get(K.settings, {}) }; },
    async importAll(j, merge) {
      if (!j || !Array.isArray(j.users)) throw new Error('ไฟล์ไม่ถูกต้อง');
      if (merge) { const us = LS.get(K.users, []), ts = LS.get(K.tests, []);
        for (const u of j.users) if (!us.find(x => x.id === u.id || x.email === u.email)) us.push(u);
        for (const t of (j.tests || [])) if (!ts.find(x => x.id === t.id)) ts.push(t);
        LS.set(K.users, us); LS.set(K.tests, ts);
      } else { LS.set(K.users, j.users); LS.set(K.tests, j.tests || []); LS.set(K.audit, j.audit || []); if (j.settings) LS.set(K.settings, j.settings); }
    },
    async wipe() { Object.values(K).forEach(k => localStorage.removeItem(k)); Object.keys(localStorage).filter(k => /^sp_(patients|tests|active|cfg)_/.test(k)).forEach(k => localStorage.removeItem(k)); },
    usage() { let n = 0; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); n += k.length + (localStorage.getItem(k) || '').length; } return n * 2; }
  };

  window.SP = { Auth, Users, Tests, Audit, Settings, Data, rnd, uid, K };
})();
