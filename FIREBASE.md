# Firebase setup (for you, and for anyone who clones this repo)

The site runs in **two modes**, chosen by `docs/firebase-config.js`:

| `window.SP_FIREBASE.apiKey` | Mode | Data | Passwords |
|---|---|---|---|
| set | **cloud** (Firebase Auth + Cloud Firestore) | on Google's servers, shared across devices, protected by `firestore.rules` | only inside Firebase Authentication (hashed by Google). This app never stores, logs, shows or exports them. Admins cannot read or set anyone's password; reset is by e-mail. |
| empty | **local demo** | this browser's localStorage only | PBKDF2 hash + salt, never exported. Not real security. |

## If you clone this repository
The committed `docs/firebase-config.js` points at the MEDTHAI project. **Do not use it for your own users.** Create your own:
1. https://console.firebase.google.com → Add project (Spark plan is enough).
2. Build → **Authentication** → Get started → Sign-in method → **Email/Password** → enable.
3. Build → **Firestore Database** → Create database (location near you, production mode).
4. Project settings → Your apps → Web → copy the SDK config into `docs/firebase-config.js` (template: `10_manual/web/firebase-config.example.js`).
5. Deploy the rules: `npx firebase-tools deploy --only firestore --project YOUR-PROJECT` (uses `firestore.rules`, `.firebaserc`, `firebase.json`; edit `.firebaserc` to your project id).
6. Create the public settings document once (Firestore console): collection `settings`, document `public`: `registrationOpen=true`, `doctorNeedsApproval=true`, `announcement=""`, `hasAdmin=false`.
7. Register yourself on `login.html`, then in the console open `users/<your uid>` and set `role="admin"`, `status="active"`; set `settings/public.hasAdmin=true`. (Nobody can make themselves admin through the app: the rules forbid it.)
8. Authentication → Settings → **Authorized domains**: add the domain you publish on (e.g. `YOURNAME.github.io`).
9. Optional hardening: Google Cloud console → APIs & Services → Credentials → restrict the browser API key to your site's HTTP referrer.

## What is a secret and what is not
- Firebase **web config** (apiKey, projectId…) identifies the project and is shipped to every browser by design. It is not a password; the rules are the lock.
- **Never commit**: service-account / Admin SDK JSON, `.env`, passwords, e-mail lists (`.gitignore` blocks the usual names).
- Patient health data is sensitive personal data (PDPA in Thailand): get consent, keep the minimum, let users export and delete their data (the patient page does), and do not put real patient data in a demo project.

## Who can see what (enforced in `firestore.rules`)
- Patient: own profile and results; can link/unlink a doctor with a doctor code.
- Doctor (approved by an admin): own account, patients who linked to them and those patients' results; can add results for a linked patient.
- Admin: everything, plus approving doctors and settings. The audit log is append-only.
- Not signed in: only `settings/public` (announcement, registration switch).

## Data model
`users/{uid}` `{role, status, name, email, doctorId?, doctorName?, code?, meta{...}}` · `doctorCodes/{DR-XXXX}` `{uid,name}` · `tests/{id}` `{patientUid, doctorUid, ts, best, trials, src, ...}` · `audit/{id}` · `settings/public`.

## Known limits
- Deleting a user in the admin page removes the profile and results; the login itself is removed in Console → Authentication (needs the Admin SDK to automate).
- Rules are not yet covered by automated emulator tests. Do that before a real deployment.
