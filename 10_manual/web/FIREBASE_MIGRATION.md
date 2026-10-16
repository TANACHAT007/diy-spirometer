# Moving Spiro from browser storage to Firebase

Status: the site runs in **local mode** (`core.js`, data in each browser's localStorage). Pages never touch storage directly; they call `SP.Auth / SP.Users / SP.Tests / SP.Audit / SP.Settings / SP.Data`, all `async`. Moving to Firebase = writing one adapter, not rewriting the pages.

## What local mode cannot do (why Firebase)
- A doctor and a patient on **different devices cannot see each other** (the link works only inside one browser).
- Passwords only gate the UI; anyone with dev tools can read/edit the data. Not acceptable for real patient data.
- No backup, no password reset by email.

## Plan
1. Firebase project (Spark plan is enough to start), enable **Authentication → Email/Password**, **Realtime Database** (region asia-southeast1).
2. Replace `Auth` with Firebase Auth (`createUserWithEmailAndPassword`, `signInWithEmailAndPassword`, `sendPasswordResetEmail`); keep the profile record in `/users/{uid}`.
3. Replace `Users / Tests / Audit / Settings` bodies with `get/set/push/update` on `/users`, `/tests`, `/audit`, `/settings` (same field names as today).
4. Admin = **custom claim** `admin: true` (Admin SDK script or Cloud Function). Never decide admin from a field the client can write.
5. Doctor approval: admin sets `/users/{uid}/status` to `active` (rules block self-approval).
6. Doctor code: store `/doctorCodes/{code} = doctorUid` when the doctor is approved, so patients can link without listing users.
7. Load `core.js` after the Firebase SDK (`firebase-app-compat`, `firebase-auth-compat`, `firebase-database-compat`) and read the config saved in Admin → Settings.
8. Rules: start from `firebase.rules.json` (**draft, untested**). Write rules unit tests with the emulator before any real data.
9. Migration of existing local data: Admin → Data → export JSON, then a one-off import script.

## Data model (today = tomorrow)
- `users/{uid}`: `{role: patient|doctor|admin, status: active|pending|disabled, name, email, doctorId?, code?, meta:{sex,age,ht,wt,smk,pf,pv,license,org}}` (password hashes disappear; Firebase Auth owns credentials)
- `tests/{id}`: `{patientUid, doctorUid, ts, best:{fvc,fev1,pef,ratio}, trials[], rep, comment, src: self|clinic, demo?}`
- `audit/{id}`: `{ts, actor, action, detail}`
- `settings`: registration / approval / announcement flags

## Privacy / legal (Thailand)
Health data is "sensitive personal data" under the PDPA: get explicit consent at sign-up, keep a retention/deletion policy (the patient page already has export + delete), restrict who reads what (rules above), and do not use the open public rules that the old dashboard README mentions for anything but made-up data.
