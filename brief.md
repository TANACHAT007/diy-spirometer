# เครื่องวัดสมรรถภาพปอดพิมพ์ 3D (Spirometer)

Folder: `diy-spirometer` · Phase: A (interview / research)

## Research (sources)
-

## Functions
| # | Function (verb + object + target) | Principle chosen | Why |
|---|---|---|---|

## Research (2026-10-15)
Reference look: ndd Easy on-PC (01_reference). It uses an ultrasonic TrueFlow sensor with ±16 L/s range, 400 Hz sampling and 0.3 cmH2O/L/s resistance, connects over USB, takes disposable Spirette mouthpieces, and meets ATS/ERS 2019. Its industrial design is a pistol grip in one pastel colour, with a white tube and a smooth cable strain relief. https://nddmed.com/products/spirometers/easy-on-pc/
- MIR Spirobank II / Minispir: bidirectional turbine flow sensor, USB/BT, about 140 g, ±3% or 50 mL volume accuracy. https://spirometry.com/media/documents/2021/12/L_MIR_Catalogue_USA_Pocket_Size_202101-1_low.pdf
- 3D-printed Venturi + ESP32 + MXP5010DP sensor (Frontiers 2025): 1.53% error against a 2 L pump, FEV1 ICC 0.97, printed in PLA. This is the best validated DIY design. https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2025.1664127/abstract
- Instructables: TTGO T-Display ESP32 + Sensirion SDP816-125Pa, under $40. Sensor sensitivity is the key choice. https://instructables.com/3D-Printed-Spirometer
- Spir-O: M5Stack Core2 + turbine, gives FEV1/FVC/PEFR. https://www.electronicwings.com/users/NightR/projects/2115/spir-o-open-source-spirometry-for-all
- SFM3300 flow sensor is often out of stock. Printed parts must be leak-tested.
Takeaways: printed Venturi/orifice + SDP8xx (or MXP5010DP) + ESP32 USB/BLE; pastel pistol-grip housing with organic fillets; removable cleanable mouthpiece tube. Educational device only, NOT for diagnosis.

## Process flow
1.

## Parts the user already owns (มีแล้ว)
-

## Decisions (do not re-argue)
- 2026-10-15 (user): must be better than the ndd Easy on-PC and work like the user's earlier SmartLung project (IoT incentive spirometer: ESP32-S3 + cloud dashboard). It must be **IoT**, **rechargeable**, and **sit in a charging dock**.
- Body: medical sky-blue + white pistol grip (changed from lilac 2026-10-15 by user) like ndd; split into L/R halves with M3 countersunk screws into heat-set inserts. The white flow tube lifts out after removing a magnetic top cover, for washing. The printed mouthpiece is personal.
- Flow sensing: printed Venturi D28/d23 (bidirectional taps, used for exhale) + Sensirion SDP810-500Pa I2C.
- MCU: XIAO ESP32-S3 (Wi-Fi + BLE, has a LiPo charger). Battery: LiPo 603450 1000 mAh. Display: GC9A01 1.28" round. One button + status LED.
- Dock: printed stand holding the device by the grip. Two spring pogo pins touch brass inserts on the grip bottom; a magnet aligns the device. Power comes in through a USB-C breakout in the dock. The device also has its own USB-C at the grip bottom.
- Data: BLE live curve to a phone/web app; Wi-Fi upload to Firebase with a class dashboard.

## Assumptions
-

## Parameters
| name | value | meaning |
|---|---|---|

## Build log
- v1 (2026-10-15): model.py builds the ndd-style pistol grip (L/R halves + magnetic top cover), Venturi tube D28/d23, mouthpiece, XIAO ESP32-S3, SDP810, GC9A01 round TFT, LiPo 603450, button/LED, pogo dock with USB-C, and the STL/STEP. The build ran (ok) but the report shows **169 interferences, not yet fixed or checked** (wires, insert/screw, etc.). The renders have not been reviewed. Print ≈ 516 g / 29 h. **The user stopped the work at this point ("ปิดงานนี้")**. Next steps: fix the clashes, review the renders, write firmware + BLE/Wi-Fi + Firebase dashboard, BOM.
- 2026-10-15 v2: shell fixed (sleeve added after shell; 38 cm3 per half), inserts M3x5 + M3x20 csk on halves (engage 5 mm), IoT firmware 08_firmware/diy_spirometer + web 10_manual/web. Remaining clashes: housing<>dock 10 mm3 each, GC9A01 1 mm3, wire touches. Compile OK, hardware untested.
- 2026-10-15 v3 (assembly/manufacturing review, user request): manifold block + internal channel replaces kinked silicone runs (2 straight stubs); stop rings on flow tube; charge contacts moved off the seam (left w13 y-6 / right w37 y+6); dock screws y+-26 / plate 85x62 / feet y+-38; grip pocket +2 mm for finger ridges; pogo holes 2.2; LED retainer rib; floating rail lips fixed (join order) -> all 7 STL watertight, 1 shell each. Open: clashes <=2 mm3, never printed/assembled, K calibration, firmware untested.

- 2026-10-15 v4 (user request: speaker + disposable biodegradable mouthpiece): speaker Ø16 x 3.5 (E8) on the RIGHT wall at grip u78/w25 (ring boss + 3 retaining lips + 19 sound holes Ø1.4; moved up from u181 because the dock collar covers the lower grip), MAX98357A I2S amp (E9) slides onto 2 rails on the LEFT wall u151-170 (friction + dab of hot glue; end stop on the XIAO side), 3 I2S pigtails (not routed to the XIAO pads). Mouthpiece = disposable PLA (plant-based, green in the model): ~11 g, ~5 THB, replace per person / 20 blows / 7 days; firmware counts blows+days, warns on screen + soft tone, reset by holding the button 4 s or `mp new`; count uploaded as `mp`; dashboard shows it. Firmware v1.1 (S3 only): GC9A01 UI via LovyanGFX (3-wire: SCK D8, MOSI D10, DC D9, CS->GND, RST->3V3), I2S tones (BCLK D3, LRC D6, DIN D7), `vol` command. Compiles for S3 and C3 (C3 = no UI). BOM now 23 items. NOT tested on hardware. Previously the firmware had NO display driver at all; now it does.

- 2026-10-15 v5 (user: rounder + more complex): grip-end corners R12, white top cover + knob (two-tone), white display bezel (glued in a 0.6 mm rebate), white domed button cap (press-fit on the tact stem), 3 ring grooves on the sleeve (x 100/105.5/111) continuing over cover, wrist-strap hole Ø4.5 through both halves at grip u168/w7.5 (boss stops at the inner wall), dock corners R8 + engraved MEDTHAI plate. 10 STL. NEW web app `10_manual/web/clinic.html` (docs/clinic.html): patient register, test workflow (prepare -> >=3 blows -> repeatability 0.15 L -> summary), live flow-volume, patient coaching screen, A4 report, JSON/CSV export, cloud pull; data only in the browser. Firmware v1.2: tail extrapolation below the 0.25 L/s cut-off (FVC was ~12 % low for a healthy slow-tail blow, ratio falsely normal: see accuracy_check.md), 'short' < 2 s. Not validated.

## Handoff (2026-10-15, end of session — user switching account)
- Done: CAD v3 (STL x7 watertight), IoT firmware (S3/C3), dashboard (multi-device/doctor view/BLE live), product page with 3D viewer (solid / "เห็นวงจร" x-ray from exported internals STL), GitHub repo public, GitHub Pages live: https://tanachat007.github.io/diy-spirometer/ (served from docs/; after editing 10_manual/web run build_product_page.py, copy product_page.html -> docs/index.html with the dashboard link set to dashboard.html, and dashboard_artifact.html -> docs/dashboard.html, then push).
- Internals STL: 02_design/export_internals.py (run after model.py in Fusion) -> 10_manual/web/internals/.
- TODO (user wants for the competition): more "wow"/new technology in function + more complex-looking, harder design; richer website (real Firebase data, accounts, AI summary, trend/risk scoring, BLE app); round the device CAD edges (user finds it too angular/crude); apply reference style (grey/orange) if still wanted; IYS registration by 18 Oct; paper/poster in lowcost-spirometer/10_manual need the new renders + the venturi/SDP810 design (they still describe the old Lilly-screen design).
- Firebase: user will create it; paste DB URL in the dashboard gear.
- 2026-10-15: dashboard works without Firebase: BLE results are saved in the browser (localStorage 'localSessions') and shown as device 'local-ble'; CSV is a real download on the hosted site. Next for 'actually usable': Firebase (accounts + cloud), Web Bluetooth test with a real device, PWA/offline, AI summary.

- 2026-10-16 v6 (CAD): button + LED are soldered to a 13x29 mm perfboard FIRST; board drops onto two wall bosses (tact stem + LED body pass through wall holes) and is locked by 2 x M2x6 self-tapping screws. Removed the printed LED rib/button bracket that trapped the parts (could not be assembled). Backup model_v6_backup.py. Roles/Firebase: see FIREBASE.md; site = cloud mode (project spiro-medthai, Firestore + Auth), admin = tanachat.sr@gmail.com.

## Handoff 2026-10-16 (end of session)
- Live site (Firebase Hosting): https://medthai-spirometer.web.app  (project spiro-medthai; GitHub Pages is OFF). Deploy: copy 10_manual/web/{core.js,login.html,admin.html,clinic.html,calm.css,icons/} to docs/, then `npx firebase-tools deploy --only hosting --project spiro-medthai` (rules: `--only firestore:rules`). See FIREBASE.md.
- clinic.html is generated: edit clinic_pre_roles.bak / patch_roles.py / roles_me.js / roles_train.js, then `py patch_roles.py` (in 10_manual/web).
- Test accounts (password is trivial, delete before real patients): test.admin / test.doctor / test.patient @example.com. Admin: tanachat.sr@gmail.com.
- IYS essay (EN + TH) in 10_manual/iys_essay (make_essay.py, make_essay_th.py; CHECKLIST_TH.md). Team: leader Puttitada (Bodindecha), members Pimnara, Suchanan, Natnicha, Nabhat; advisor Tanachat Srinurat. Deadline 18 Oct 2026 (user submits).
- Done: v6 CAD (button/LED daughter board), 3-role Firebase web app, device pairing by code (web + rules), training plans (doctor prescribes, patient follows with voice/beeps), bright elderly-friendly UI.
- TODO next: (1) compile firmware v1.3 (08_firmware/diy_spirometer: device code on screen hold 8 s, BLE Wi-Fi setup characteristic 6e400004) for S3 and C3, then a Wi-Fi setup page in the web app; (2) nurse-style Thai/English voice script + MP3 playback with fallback to speechSynthesis; (3) test on a real phone; (4) real prototype: print, calibrate with 3 L syringe, straw-pulp mouthpiece; (5) delete test accounts before real use; (6) Gemini images for story cards (img/story/PROMPTS.md).
- 2026-10-21 v7: dock base smaller (slab 175x90 -> 145x72, feet moved in); backup model_v7_backup.py = v6 before the change.
- v8 (2026-10-21): dock slab 145x72 (smaller), rear feet moved to x132, shadow-reveal groove, 2 blue light-guide strips + status LED inlays (model_v8_backup.py = before)
- v9 (2026-10-21): dock honeycomb panel (17 cells, 1 mm engraved) on top face x124-139; fusion_detail loaded in model.py
- v9b (2026-10-21): dock text recentred x=108 (was 86, clipped at slab edge)
- v10 (2026-10-21): dock split in 3 prints: base (dock.stl), cradle (dock_cradle.stl, 4 x M3x12 csk + inserts from the cavity ceiling), bottom plate. check_joints.py: 10 print bodies, all 1 shell, fastener_check 0 clashes; unfastened contacts = cover(magnets), tube/cover(stop rings), mouthpiece (press-fit), all deliberate. Material: Bambu PETG white.
