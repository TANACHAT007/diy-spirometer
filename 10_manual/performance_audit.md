# Spiro (MEDTHAI) — Performance & Safety Audit vs ATS/ERS 2019 (+ ISO 26782)

Date: 2026-10-21 · Scope: brief.md, 02_design (model.py, feasibility*, accuracy_check.md), 08_firmware v1.3, 09_bom, 10_manual/web (clinic.html, core.js), docs/dashboard.html, firestore.rules, FIREBASE.md.
Method: read-only code review + recomputation (appendix A, script `audit_calc.py` kept in the session scratchpad). **No hardware exists yet; nothing was measured.** All accuracy numbers below are model estimates, not clinical accuracy.

## สรุป (Go / No-go)

| การใช้งาน | สถานะ |
|---|---|
| สาธิต/สอน/แข่งขัน (IYS) กับอาสาสมัครสุขภาพดีที่ยินยอม, ใช้ที่เป่า+filter ใหม่ทุกคน, ไม่แปลผล | **GO ได้ทันทีที่พิมพ์และประกอบเสร็จ** (หลังทำ B8, B9) |
| วัดผู้ป่วยจริงใน รพ. เพื่อตัดสินใจทางคลินิก/วินิจฉัย/คัดกรองที่มีผลต่อการรักษา | **NO-GO** — มี BLOCKER 9 ข้อ, ยังไม่มี hardware, ไม่มีการ validate, ไม่ได้ขึ้นทะเบียน อย. |
| งานวิจัยเทียบกับ spirometer มาตรฐานของ รพ. (ผล DIY ไม่ใช้รักษา) | **ทำได้หลัง** แก้ B1–B9 + ผ่าน 3-L syringe check (ภาค 4) + ได้รับอนุมัติ EC/IRB ของ รพ. |

ปัญหาหลัก 3 ข้อ: (1) **ฟิสิกส์ของ venturi ทำให้วัดลมต่ำ < 0.27 L/s ไม่ได้** → ตัดหาง FVC; จากแบบจำลอง ผู้ป่วยอุดกั้นปานกลาง FVC ต่ำจริง ~24 % และ FEV1/FVC ขึ้นจาก 52 % เป็น 68 % (อุดกั้นรุนแรง: 44 % → 74 % = **อ่านว่า "ไม่อุดกั้น"**) — ทำให้กลุ่มเป้าหมาย (COPD) ถูกมองข้าม; (2) ไม่มี BTPS, ไม่มี calibration curve, ไม่มี back-extrapolation/EOFE ตาม ATS; (3) ข้อมูลผู้ป่วย/สุขอนามัย/กฎหมาย (PDPA, test accounts รหัสอ่อนที่มีสิทธิ์ admin, ที่เป่า PETG ไม่ใช่วัสดุการแพทย์, ไม่มี bacterial/viral filter, tap หันลงล่างรับน้ำลาย).

---

## BLOCKERS (ต้องแก้ก่อนใช้กับผู้ป่วยทุกกรณี)

| # | ปัญหา | หลักฐาน | วิธีแก้ | แรง |
|---|---|---|---|---|
| B1 | **วัดลมต่ำไม่ได้ (ข้อจำกัดเชิงฟิสิกส์)**. ΔP ∝ Q²: 0.1 L/s = 0.019 Pa (1.1 count), 0.025 L/s (เกณฑ์ EOFE) = 0.0012 Pa (0.07 count). Deadband 0.15 Pa = ทิ้งทุก flow < **0.273 L/s**; จบเทสเมื่อ < 0.25 L/s นาน 1 s. ATS 2019 EOFE ต้องการ plateau < 0.025 L ใน 1 s (ละเอียดกว่า 11×). แบบจำลอง: healthy FVC −4.7 % (หลังเติมหาง), obstructive −24 %, severe −41 %; FEV1/FVC ผิด +4…+30 จุด | firmware `diy_spirometer.ino:41-42, 75, 350-351`; appendix A3 | ตัดสินใจระดับ design (ต้องให้ผู้ใช้ตัดสิน เพราะ brief บันทึก venturi ไว้): (a) เปลี่ยนเป็น **linear resistive pneumotach** (mesh/Lilly screen, ΔP ∝ Q; ถ้า 14 L/s = 400 Pa → 0.025 L/s = 0.71 Pa = 43 count, R ≈ 0.29 cmH2O/L/s) + filter กันชื้นด้านหน้า; หรือ (b) คง venturi แต่ระบุชัดว่า **"ไม่ผ่าน ATS EOFE, FEV1/FVC ใช้ไม่ได้ในผู้ป่วยอุดกั้น"** และห้ามแปลผล ratio | (a) 1–2 สัปดาห์ (CAD+calibration ใหม่) / (b) 1 ชม. |
| B2 | **Tail extrapolation ไม่ใช่วิธีตามมาตรฐาน** (ATS ไม่อนุญาตให้ "เดา" ปริมาตร) และสูตรผิด: `tail = qc/ln(qp/qc)` ขาดตัวคูณ Δt = 1.04 s (ต่ำไป 4 %) และ cap 0.5 L/15 % ทำให้ obstructive เติมได้แค่ 0.24 จาก 0.82 L ที่หายไป | `.ino:356-364` (บรรทัด 361) | ถ้าคง venturi: แก้สูตรเป็น `qc*1.04f/logf(qp/qc)`, ติด flag "FVC estimated" ในผลและรายงาน, ห้ามนำไปแปลผล ratio; ทางที่ถูกคือ B1(a) | 30 นาที |
| B3 | **ไม่มี BTPS / density correction**. calibrate ด้วยอากาศห้อง (ρ 1.176 @25 °C 60 %RH) แต่ลมหายใจ ρ 1.126 → อ่านต่ำ 2.1 %; ไม่แปลง BTPS (ก๊าซในท่อ 30–33 °C → factor 1.026–1.045). รวม ≈ −4…−7 % ต่อค่าปริมาตรทุกตัว เกินงบ ±3 % คนเดียว. accuracy_check.md บอกทิศผิด ("อ่านสูงขึ้น") | `.ino` ไม่อ่านอุณหภูมิ (bytes 3-5 ถูกทิ้ง `:64-73`); `accuracy_check.md:18` | ใช้ sensor temperature ของ SDP810 + อุณหภูมิห้อง/ความดัน (ป้อนเอง) คำนวณ BTPS factor ตาม ATS 2019/ISO 26782; หรืออย่างน้อย factor คงที่ที่ได้จากการเทียบกับเครื่องมาตรฐาน; แก้ทิศใน accuracy_check.md | 0.5–1 วัน + ทดสอบ |
| B4 | **Calibration เป็น K ตัวเดียว** แต่ Re ที่ throat 1 700 (0.5 L/s, laminar) → 48 000 (14 L/s) ต่ำกว่าช่วง ISO 5167 (≥1.5·10⁵) → Cd เปลี่ยนตาม flow; single-K คาดว่าผิดหลาย % ที่ flow ต่ำ/สูง (ยังไม่ได้วัด). README สั่ง calibrate แบบเร็วอย่างเดียว | `.ino:32,77`; `08_firmware/README.md:36` | ทำตาราง **K(ΔP) 6–8 จุด** (piecewise linear, เก็บใน Preferences) จาก syringe 3 อัตรา+ (ภาค 4), calibrate โดยใส่ filter+ที่เป่าจริง, ทำใหม่ทุกครั้งที่พิมพ์ท่อใหม่/ล้างด้วยความร้อน | 1 วัน code + 1 วันวัด |
| B5 | **ไม่มี back-extrapolated time zero (BEV), ไม่มี EOFE, acceptability หลวม**. t0 = จุดที่ flow > 0.3 L/s; FEV1 = vol ที่ t ≤ 1000 ms จาก t0 นั้น (ไม่ใช่ BEV t0) → FEV1 เพี้ยนตามความเร็วต้นเป่า, ปริมาตรก่อน trigger ถูกทิ้ง; ไม่คำนวณ BEV (< 5 % FVC หรือ 0.100 L ตาม ATS 2019; ค่า 0.150 L เป็นของ 2005), ไม่ตรวจไอ/ปิดกล่องเสียง; quality = แค่ FET ≥ 2 s และ PEF ≥ 1 L/s; ข้อความแอปยังอ้าง "≥ 6 s" (เกณฑ์ 2005) | `.ino:293-297, 338, 343`; `clinic.html:240, 320-321` | เก็บ flow buffer เต็ม (≥100 Hz, ~15 s = 1 500 samples × 4 B = 6 kB), หลังเป่าคำนวณ: slope สูงสุด → BEV t0, FEV1 จาก t0, BEV/EVol, FET, plateau; ส่ง flag ทั้งหมดไปแอป; ให้ผู้ตรวจดูกราฟเอง (ATS ต้อง operator review) | 1–2 วัน |
| B6 | **Integration เสียตัวอย่างเงียบๆ**: อ่าน sensor ไม่สำเร็จ → `continue` โดยไม่รวมช่วงเวลานั้น; วาดจอ (~10 ms ทุก 90 ms) ทำให้อ่านติดกันเร็วกว่า update 0.5 ms ของ sensor → อาจ NACK. ประมาณการเสียปริมาตร 0–7 % ขึ้นกับรูปเป่า (ยังไม่ได้วัด) | `.ino:334-342` | ใช้ `dt = micros()-tPrev` จริงต่อการอ่านที่สำเร็จ (หรือ hold ค่าเดิม), นับ read-fail และ abort ถ้า > 1 %; ห้ามวาดจอระหว่างเป่า (วาดหลังเป่า) หรือย้าย sampling ไป task/core แยก | 2–3 ชม. |
| B7 | **สุขอนามัย / ทางเดินลม**: (1) ไม่มี bacterial/viral filter ในระบบเลย (BOM 26 รายการไม่มี); (2) tap ทั้งสองเจาะ **ลงล่าง** จากผิวล่างของท่อ (`drill … 'z' … -12.0` → ปลายรูอยู่ก้นท่อ) น้ำลาย/ไอน้ำไหลลง tap → ช่อง 2.4 mm → SDP810 ซึ่งเป็น sensor แบบ flow-through (ทำความสะอาดไม่ได้, ΔP เพี้ยน); (3) ที่เป่าพิมพ์ PETG ไม่มีหลักฐาน ISO 10993, ผิวมีร่องชั้นพิมพ์ 0.2 mm กักเชื้อ; firmware ให้ใช้ 20 ครั้ง/7 วันต่อคน | `model.py:409-412`; `09_bom/bom.md`; `print_guide.md` (Mouthpiece row); `.ino:86-87` | ใช้ **single-use spirometry BVF (bacterial/viral filter) + ที่เป่ากระดาษสำเร็จรูป** ต่อผู้ป่วย 1 คน/1 session (ทำ adapter ให้เข้าซ็อกเก็ต Ø30.4 mm — ตรวจขนาด filter จริง), calibrate โดยใส่ filter; ย้าย tap ไปด้านบน/ด้านข้าง (≥ 45° เหนือแนวนอน) หรือใส่ hydrophobic PTFE 0.2 µm inline ทั้ง 2 สาย; ห้ามใช้ที่เป่า PETG กับผู้ป่วย | adapter 0.5 วัน; ย้าย tap 1 วัน (CAD+พิมพ์) |
| B8 | **Test accounts รหัสผ่านง่ายรวม admin** ยังอยู่ใน project จริง `spiro-medthai` (admin อ่านได้ทุก record) — ยังไม่ได้ตรวจว่าลบแล้วหรือไม่ | `FIREBASE.md:44-45`; `brief.md:63` | ลบ 3 บัญชีใน Firebase Console › Authentication **และ** ลบ doc `users/*`, `doctorCodes/DR-TEST`, tests demo; เปิด MFA ให้ admin | 15 นาที |
| B9 | **PDPA / ข้อมูลสุขภาพ**: ไม่มี consent flow, ไม่มี DPO/ROPA, ไม่รู้ region ของ Firestore (ถ้าอยู่นอกไทย = cross-border transfer), ชื่อ/HN ผู้ป่วยที่ไม่ได้ผูกบัญชีเก็บ **plain text ใน localStorage** ของเครื่องหมอ (`sp_patients_<uid>`), RTDB path ของ firmware ใช้ legacy DB secret ใน URL query + `setInsecure()` (ไม่ตรวจ cert) และ README แนะนำ rules `.read/.write: true`, ผลจากเครื่องไม่มี patient ID → ผู้ตรวจต้องเลือกคนไข้เองบนหน้าจอ (เสี่ยงสลับคน) | `clinic.html:303-304`; `.ino:239-241`; `08_firmware/README.md:25`; `clinic.html:531-533, 562` | ใช้กับผู้ป่วยจริง **เฉพาะเมื่อฝ่าย IT/DPO ของ รพ. อนุมัติระบบ**; ระหว่างนี้ใช้รหัสวิจัย (pseudonym) แทนชื่อ/HN; consent form; ปิด RTDB หรือใช้ Firebase Auth token แทน secret; ตรวจ region; เพิ่ม session ID/patient code ที่แสดงบนจอเครื่องเพื่อจับคู่ | 1–3 วัน + ขั้นตอนของ รพ. |

## SHOULD-FIX

| # | ปัญหา | หลักฐาน | วิธีแก้ | แรง |
|---|---|---|---|---|
| S1 | **การแปลผลใช้ fixed 70 % + % predicted ที่กรอกมือ + GOLD severity** — ไม่มีสมการอ้างอิง, ไม่มี LLN/z-score (ATS/ERS 2022 แนะนำ z-score, LLN = 5th percentile), GOLD ต้องเป็นค่าหลังยาขยายหลอดลม + การวินิจฉัยของแพทย์; ผู้ป่วยกรอกค่าคาดการณ์เองได้ | `clinic.html:233, 329-338, 575`; `docs/dashboard.html:223, 238-244` | ใส่ GLI (Global 2022 race-neutral หรือ GLI-2012 — **ถามห้อง PFT ของ รพ. ว่าใช้สมการใด** หลาย รพ. ไทยใช้สมการไทย Siriraj/Dejsomritrutai 2000 หรือ GLI); แสดง z-score + LLN; ตัด GOLD staging ออก | 1–2 วัน (ตาราง LMS ของ GLI) |
| S2 | **ถ้อยคำเชิงวินิจฉัย**: "สงสัยรูปแบบการอุดกั้นทางเดินหายใจ (ปานกลาง)", "ปกติ / Normal" ใน dashboard, จอเครื่องเป็นวงแหวนเขียว + เสียง "good" เมื่อ ratio ≥ 70 | `clinic.html:247, 332`; `docs/dashboard.html:215`; `.ino:177, 378` | ใช้คำ "ค่าที่วัดได้ (เครื่องต้นแบบ ไม่ใช่การวินิจฉัย) — ถ้าต้องการผลจริงให้ตรวจด้วยเครื่องมาตรฐาน"; ตัดสี/เสียงที่ผูกกับ ratio บนเครื่อง; ซ่อนการแปลผลจาก role patient | 2 ชม. |
| S3 | **ลมเข้าวัดเป็นลมออก**: venturi ให้ ΔP บวกทั้งสองทิศ (feasibility ระบุเอง) firmware ใช้ sign(ΔP) → การหายใจเข้าผ่านเครื่องจะ trigger และถูกบวกเป็นปริมาตรเป่าออก | `.ino:74-78`; `feasibility.md` ข้อจำกัด | บังคับ open-circuit (หายใจเข้านอกเครื่อง แล้วอม) ในคู่มือ+แอป (c4 มีแล้ว), ทดสอบ syringe ย้อนทิศเพื่อรู้ขนาด error, พิจารณา check valve ทางเดียว (เพิ่ม R — ต้องวัด) | 1 ชม. + ทดสอบ |
| S4 | **Zero/offset**: zero ครั้งเดียวตอนบูต (สมมติว่าไม่มีลม, ไม่มี sanity check), ไม่ re-zero ก่อนแต่ละเป่า; offset 0.1 Pa = flow error +10 % ที่ 0.5 L/s, +2.6 % ที่ 1 L/s | `.ino:223-228, 416` | auto-zero 0.5 s ก่อนสัญญาณ "BLOW" ทุกครั้ง; reject ถ้า |offset| > 0.3 Pa หรือ SD > 0.05 Pa (มีลม/น้ำใน tap) | 1 ชม. |
| S5 | **Sensor หาย/เสีย ไม่แจ้ง**: SDP810 NOT FOUND แค่ print serial; เทสวิ่ง 15 s แล้วขึ้น "NO BLOW"; zero() n=0 ใช้ offset เก่า | `.ino:414, 226, 336` | แสดง "SENSOR ERROR" บนจอ+BLE, ห้ามเริ่มเทส; นับ CRC fail | 1 ชม. |
| S6 | **Repeatability/grade ปนผู้ป่วย**: `histFvc/nHist` เป็น global ไม่ reset เมื่อเปลี่ยนคน; grade มีแค่ A/C; tolerance ในแอปใช้ "FVC ≤ 1 L → 0.10 L" แต่ ATS 2019 ใช้อายุ (> 6 ปี: 0.150 L; ≤ 6 ปี: 0.100 L หรือ 10 %) | `.ino:299-306`; `clinic.html:326` | reset เมื่อเริ่ม session ใหม่ (BLE command); ใช้ grading A–F ของ ATS 2019; tolerance ตามอายุ | 2 ชม. |
| S7 | **เวลาเป่าสูงสุด 15 s นับจากกดปุ่ม** ไม่ใช่จากเริ่มเป่า → ถ้ารอ 3 s ได้ FET สูงสุด 12 s (ATS ใช้ FET 15 s เป็นเกณฑ์จบ) | `.ino:330, 333` | นับ 15 s จาก t0 + timeout รอเป่าแยก 10 s | 15 นาที |
| S8 | **BLE ไม่ปลอดภัย/ไม่ครบ**: ไม่มี pairing/encryption, รหัส Wi-Fi ส่งเป็น plain text (มีแค่ device code + window 5 นาที), notify ไม่มี sequence/CRC — packet หายไม่รู้; กราฟเก็บแค่ 25 Hz แล้ว decimate เหลือ 12.5 Hz | `.ino:260-269, 344-349`; `clinic.html:445, 529-533` | ใส่ seq number + ส่งผลซ้ำจนแอป ack; เปิด BLE bonding (LE Secure Connections); เก็บ curve ≥ 50–100 Hz ไว้ทบทวน | 0.5–1 วัน |
| S9 | **Firestore rules**: patient สร้าง test ได้โดยตั้ง `doctorUid` อะไรก็ได้ (ไม่ตรวจ), patient ลบผลตัวเองได้ (เวชระเบียน/ข้อมูลวิจัยหาย), rules ยังไม่มี emulator test | `firestore.rules` match /tests create & delete; `FIREBASE.md:38` | ตรวจ `doctorUid == users/{me}.doctorId`; ใช้ soft-delete + audit; เขียน rules tests | 0.5 วัน |
| S10 | **ความต้านทานรวม filter ยังไม่รู้**: ท่อเปล่าดี (worst case ทั้งหมด ΔP สูญเสีย = 0.27 cmH2O/L/s ที่ 14 L/s, เกณฑ์ < 1.5) แต่ feasibility สมมติ loss 15 % เอง; filter+adapter ยังไม่รวม | `feasibility_check.py:27` | วัด ΔP ปากเป่า–บรรยากาศ ที่ ~12 L/s หลังใส่ filter (manometer/SDP ตัวที่ 2) | 1 ชม. |
| S11 | **Saturation ไม่มี flag**: clip ที่ 500 Pa ≈ 15.8–16.7 L/s (ขึ้นกับ Cd, ρ) — ผ่าน ATS ≥ 14 L/s (margin 13–19 %) แต่ถ้าเกินจะ cap PEF เงียบๆ | `.ino:64-73` | ถ้า |dp| ≥ 495 Pa → flag "PEF clipped" | 15 นาที |
| S12 | **LiPo/การชาร์จ**: XIAO charger ไม่มี NTC (ไม่มีตัดตามอุณหภูมิ), แบตอยู่ในกล่อง PETG ปิด, feasibility แนะนำชาร์จข้ามคืนบนแท่น; low battery แค่กะพริบ — เทสยังวิ่ง (brown-out กลางเทส = ผลหาย) | `.ino:79-82, 367`; `feasibility.md`; `bom.md` #4 (ต้องมี PCM — ดีแล้ว) | ใช้ cell ที่มี PCM จริง (ตรวจ), อย่าชาร์จทิ้งไว้ในหอผู้ป่วยโดยไม่มีคนดู, ใช้ adapter USB ที่ได้มาตรฐาน (มอก./IEC 62368-1), ห้ามเทสขณะวางบนแท่นชาร์จ, block เทสเมื่อแบต < 10 % | 1 ชม. |
| S13 | **PETG flow tube**: ชั้นพิมพ์ 0.2 mm ตั้งฉากกับทางลม (relative roughness ~0.5–1 % ของ d=23 mm) → Cd ต่างกันทุกชิ้นที่พิมพ์; PETG Tg ≈ 80 °C → ล้างน้ำร้อน/อบ/autoclave ไม่ได้ (รูปทรงเปลี่ยน = calibration หาย); ล้างแล้วน้ำค้างในรู tap 2 mm/ช่อง 2.4 mm | `print_guide.md` Known risks; `model.py:409-412` | ถือว่าท่อเป็น "ไม่สัมผัสผู้ป่วย" โดยมี BVF ทุกครั้ง; เช็ดภายนอกด้วย alcohol 70 %; ถ้าล้างภายใน ต้องเป่าแห้ง+re-zero+syringe check ก่อนใช้; ระบุเลข serial ท่อ + K ต่อท่อ | ขั้นตอน |

## NICE-TO-HAVE

| # | เรื่อง | หลักฐาน | วิธีแก้ | แรง |
|---|---|---|---|---|
| N1 | K ใน firmware (0.705, ρ = 1.20) ไม่ตรง feasibility (ρ = 1.15 → 0.727, ต่าง 3 %) | `.ino:32`; `feasibility_check.py:9` | ใช้ค่าเดียวกัน (ไม่มีผลหลัง calibrate) | 5 นาที |
| N2 | ตำแหน่ง tap1 อยู่ 6 mm (0.21 D) ก่อน convergent (ISO 5167 classical: 0.5 D ± 0.25 D = 7–21 mm), throat ยาว 0.5 d (ISO: 1 d), step 30.4→28 mm ห่าง tap แค่ 34 mm → Cd ไวต่อรูปปากเป่า/filter | `model.py:19-24` | ยอมรับได้ถ้า calibrate พร้อม filter+ที่เป่าจริง; ถ้าแก้ CAD ให้ tap1 ที่ 0.5 D | — |
| N3 | PEF = ค่าสูงสุดของ sample เดียวที่ 400 Hz (average-till-read ช่วยกรองแล้ว) | `.ino:341` | ใช้ max ของ moving average 10 ms; รายงาน time-to-PEF | 30 นาที |
| N4 | Upload ไม่มี fw/K/offset/serial ท่อ/flag ใน record | `.ino:243-245` | เพิ่ม K table version, offset, flags, tube serial เพื่อ traceability | 1 ชม. |
| N5 | OTA ไม่มี (C3 huge_app) | README | — | — |
| N6 | Dead space ท่อ ≈ 107 mL (+ที่เป่า ~20 mL + filter) — ไม่มีผลกับ open-circuit FVC; มีผลถ้าหายใจซ้ำในท่อ | appendix A6 | ห้าม rebreathe ผ่านเครื่อง | — |

---

## 4. Calibration / verification ที่ต้องมีก่อนใช้ทางคลินิก

**มีแล้ว**: คำสั่ง `k <value>` (single K), zero ด้วยปุ่ม 1.5 s, leak test ใน print_guide ข้อ 5, ข้อความเตือนในแอป.
**ยังไม่มี**: K(Q) curve, BTPS, BEV/EOFE, syringe log, ข้อมูลวัดจริงใดๆ, การเทียบกับเครื่องมาตรฐาน, waveform test (ISO 26782 ใช้ 24 ATS waveforms ผ่านเครื่องปั๊มควบคุมด้วยคอมพิวเตอร์ — โรงเรียนทำไม่ได้; ถามฝ่าย biomedical engineering ของ รพ.).

เกณฑ์ (ATS/ERS 2019 / ISO 26782): accuracy ±2.5 % (หรือ ±0.050 L ตาม ISO ±3 %/0.050 L เมื่อรวมความคลาดเคลื่อน syringe ±0.5 %) → **ผลอ่าน syringe 3 L ต้องอยู่ 2.91–3.09 L**; flow sensor ต้องเช็ค 3 อัตรา (ช่วง 0.5–12 L/s, เวลาดัน 3 L ≈ 6 s, ≈ 3 s, < 0.5–1 s) ทุกวันที่ใช้; resistance < 1.5 cmH2O/L/s ถึง 14 L/s.

### แผนทีละขั้น (มี syringe 3 L — ยืมจากห้อง PFT ของ รพ. ได้ เพราะเขาต้องมีไว้เช็คทุกวัน)
1. พิมพ์+ประกอบ, leak test (print_guide ข้อ 5), ใส่ **filter + ที่เป่าตัวที่จะใช้จริง**, วางเครื่องกับ syringe ไว้ห้องเดียวกัน ≥ 1 ชม. จดอุณหภูมิ/ความชื้น/ความดันห้อง.
2. Zero drift: เครื่องนิ่ง 10 นาที log ΔP → ต้อง |mean| < 0.05 Pa, SD < 0.05 Pa.
3. ทดสอบ sampling: ดัน 3 L แล้ว log จำนวน read-fail (ต้อง 0 หรือ < 0.1 %).
4. **สร้าง K(Q)**: ดัน 3 L ที่ 6 ระดับความเร็ว (≈ 0.5, 1, 2, 4, 8, 12 L/s peak; เวลาดัน ≈ 6, 3, 1.5, 0.8, 0.4, 0.25 s), ระดับละ 3 ครั้ง → ได้ K ต่อช่วง ΔP → ใส่ตาราง piecewise.
5. **Verification แยก** (คนละชุดกับข้อ 4): 3 อัตรา (ช้า/กลาง/เร็ว) × 3 ครั้ง → ทุกค่าต้อง 2.91–3.09 L. ไม่ผ่าน = ห้ามใช้, กลับข้อ 4.
6. Syringe ย้อนทิศ (ดูดผ่านเครื่อง) 1 ครั้ง → ดูว่า trigger/บวกปริมาตรเท่าไร (S3).
7. Linearity เพิ่ม: 1 L และ 2 L ที่ความเร็วกลาง (ถ้า syringe มีสเกล).
8. วัด resistance ที่ ~12 L/s พร้อม filter (S10).
9. ทำซ้ำข้อ 5 **ทุกวันที่ใช้** และหลังล้าง/เปลี่ยนท่อ; เก็บ log (วันที่, ผู้ทำ, ค่า, ผ่าน/ไม่ผ่าน).
10. เทียบกับเครื่องมาตรฐาน (ภายใต้ EC): อาสาสมัคร ≥ 30 คน รวมผู้มี obstruction, เป่าเครื่อง DIY ต่อ inline กับ sensor ของเครื่องมาตรฐาน (หรือสลับลำดับแบบสุ่ม) → Bland–Altman ของ FEV1, FVC, FEV1/FVC; เป้า bias < 0.1 L, limits of agreement ±0.2 L (เป้าที่ทีมตั้งเอง ไม่ใช่เกณฑ์ ATS) และ ratio ต้องจำแนก obstruction ตรงกับเครื่องมาตรฐาน.

### ถ้าไม่มี syringe
- ทางที่ดีที่สุด: **ยืมจาก รพ.** (ห้อง PFT/อายุรกรรมปอด/biomedical) — ไม่ต้องซื้อ.
- ทางรอง (การศึกษาเท่านั้น, ห้ามอ้างความแม่นยำ): ต่อ DIY inline กับ spirometer มาตรฐานแล้วเทียบกันทุกการเป่า; หรือถุง/กระบอกที่ทราบปริมาตรด้วยการแทนที่น้ำ (ความแม่นยำ ±3–5 % ขึ้นกับฝีมือ — วัดความไม่แน่นอนเอง).
- ห้ามใช้ "ค่าตามทฤษฎี K = 0.705" กับผู้ป่วย.

## 5. ความปลอดภัยผู้ป่วย/สุขอนามัย (สรุปการใช้งาน)
- ชิ้นที่สัมผัสลมหายใจ: ที่เป่า (ตรงปาก), flow tube ทั้งเส้น, manifold/tap, สายซิลิโคน, **SDP810 (ลมผ่านในตัว sensor)**. ชิ้นที่มือจับ: housing, ปุ่ม, จอ.
- กฎ: 1 ผู้ป่วย = 1 BVF ใหม่ + 1 ที่เป่าใหม่ (สำเร็จรูปเกรดการแพทย์), ทิ้งหลังจบ session; open-circuit เท่านั้น (หายใจเข้านอกเครื่อง); เช็ดภายนอกด้วย alcohol 70 % ระหว่างคน; ไม่ใช้กับผู้ป่วยวัณโรค/ติดเชื้อทางเดินหายใจเฉียบพลัน (ตามข้อห้ามทั่วไปของ spirometry และนโยบาย IC ของ รพ.); ปรึกษาหน่วยควบคุมการติดเชื้อ (IC) ของ รพ.
- ไฟฟ้า: ตัวเครื่องใช้แบต 3.7 V ไม่มีไฟบ้านในตัว — ความเสี่ยงไฟดูดต่ำ; จุดเชื่อมไฟบ้านคือ adapter USB ของแท่นชาร์จ → ใช้ adapter ที่ได้มาตรฐาน, ไม่เทสขณะชาร์จ. ยังไม่ผ่าน IEC 60601-1 / 60601-1-2 (EMC: เครื่องมี Wi-Fi/BLE ในพื้นที่ รพ.) — ให้ biomedical ของ รพ. ตรวจก่อนนำเข้าพื้นที่ผู้ป่วย.
- ข้อมูล: ดู B8, B9, S9. ใช้ pseudonym ระหว่างทดลอง.

## 6. กฎหมาย/ข้อกำหนดในไทย (ระบุตามที่รู้ — ต้องยืนยันกับ อย. และ รพ.)
- เครื่องวัดสมรรถภาพปอดที่ใช้วินิจฉัยเป็น "เครื่องมือแพทย์" ตาม พ.ร.บ.เครื่องมือแพทย์ พ.ศ. 2551 (แก้ไข ฉบับที่ 2 พ.ศ. 2562). อย. จัดประเภทตามความเสี่ยง 4 ระดับ (แนว ASEAN AMDD); spirometer น่าจะอยู่ระดับความเสี่ยงต่ำ-ปานกลาง (Class 2) — **verify กับกองควบคุมเครื่องมือแพทย์ อย.** การผลิตเพื่อจำหน่าย/ใช้ทางคลินิกต้องขึ้นทะเบียน/แจ้งรายการ และระบบคุณภาพ (ISO 13485 แนวทาง) — โครงงานนี้ยังไม่มีทั้งหมด.
- การผลิตเพื่อการศึกษาวิจัยมีช่องทางของ อย. แยก — **ต้องสอบถาม อย./ฝ่ายวิจัยของ รพ.** ว่าต้องขออนุญาตหรือไม่.
- งานวิจัยในคน (แม้แค่เทียบค่า): ต้องได้รับอนุมัติคณะกรรมการจริยธรรมการวิจัยในมนุษย์ (EC/IRB) ของ รพ., informed consent, ผู้วิจัยหลักควรเป็นแพทย์/บุคลากร รพ. (นักเรียนอายุต่ำกว่า 18 ไม่ควรเข้าถึงข้อมูลระบุตัวตนผู้ป่วย), ผลจากเครื่อง DIY **ห้ามใช้ตัดสินการรักษา**.
- PDPA พ.ศ. 2562: ข้อมูลสุขภาพเป็นข้อมูลอ่อนไหว (ม.26) ต้องได้ความยินยอมโดยชัดแจ้ง; การเก็บบนคลาวด์ต่างประเทศต้องเป็นไปตามเงื่อนไขการส่งข้อมูลข้ามประเทศ — ให้ DPO ของ รพ. ตัดสิน.
- สถานะที่พูดได้ตรงๆ ตอนนี้: **"เครื่องต้นแบบเพื่อการศึกษา (educational prototype) — ไม่ใช่เครื่องมือแพทย์ ยังไม่ผ่านการสอบเทียบหรือรับรอง"**.

---

## Appendix A — calculations (β = 0.821, 1−β⁴ = 0.5447, A_throat = 415.5 mm², ρ = 1.15, Cd = 0.98, SDP810 60 count/Pa)

**A1. ΔP = ½ρ(1−β⁴)(Q/(Cd·A_t))²**

| Q (L/s) | ΔP (Pa) | counts | v_throat (m/s) | Re_throat |
|---|---|---|---|---|
| 0.025 | 0.0012 | 0.07 | 0.06 | 86 |
| 0.1 | 0.019 | 1.1 | 0.24 | 344 |
| 0.273 (deadband) | 0.15 | 9 | 0.65 | 929 |
| 1 | 1.89 | 113 | 2.41 | 3 441 |
| 5 | 47.2 | 2 834 | 12.0 | 17 206 |
| 10 | 188.9 | 11 336 | 24.1 | 34 412 |
| 14 | 370.3 | 22 218 | 33.7 | 48 177 |

Saturation at 500 Pa: 15.8 L/s (ρ 1.20, Cd 0.97) … 16.7 L/s (ρ 1.13, Cd 1.00) → inside ATS ≥ 14 L/s range; no clip flag in firmware.

**A2. Zero offset → flow error = √(1+ε/ΔP) − 1**: ε = 0.1 Pa → +10.1 % @0.5 L/s, +2.6 % @1, +0.7 % @2, +0.1 % @5 L/s. (Sensor figures: zero accuracy ≈ 0.1 Pa from accuracy_check.md, which itself says "verify latest datasheet" — not verified here.)

**A3. Tail truncation (3-exponential blow models, firmware logic re-implemented: deadband 0.273 L/s, stop after 1 s below 0.25 L/s, firmware tail formula and caps)**

| model | true FVC / FEV1 / ratio | device FVC raw → +tail | device ratio | FVC error | FET |
|---|---|---|---|---|---|
| healthy (4.0 L; τ 0.22/1.1/2.6 s) | 4.00 / 3.01 / 75 % | 3.51 → 3.81 | 79 % | −4.7 % | 2.1 s |
| obstructive (2.5 L; τ 0.3/1.5/5 s) | 2.45 / 1.27 / 52 % | 1.63 → 1.87 | 68 % | −23.7 % | 2.0 s |
| severe (2.0 L; τ 0.35/2/7 s) | 1.89 / 0.83 / 44 % | 0.97 → 1.12 | 74 % | −41 % | 1.4 s (→ "short", rejected) |

Models are illustrative (not patient data); direction and size of the bias are the point. Correct-Δt uncapped tail would be 0.31 / 0.36 / 0.23 L — still far short.

**A4. Density/BTPS**: ρ room (25 °C, 60 % RH) = 1.176, ρ breath (34 °C sat.) = 1.126 → Q_device/Q_true = √(1.126/1.176) = 0.979 (−2.1 %). BTPS factor for gas at T (saturated, 760 mmHg): 22 °C 1.091, 25 °C 1.074, 30 °C 1.045, 33 °C 1.026.

**A5. Resistance**: worst case (no pressure recovery) 370.3 Pa / 14 L/s = 26.4 Pa·s/L = **0.27 cmH2O/L/s** < 1.5 limit; feasibility's 0.046 assumes 15 % permanent loss. Filter not included.

**A6. Dead space**: socket Ø30.4×20 mm (14.5 mL) + Ø28 bore ~150 mm ≈ 107 mL tube (venturi section slightly less) + mouthpiece ~20 mL.

**A7. Display blocking** (estimate): fillRect 160×100 px ×16 bit @40 MHz ≈ 6.4 ms + arc ≈ 2 ms + text ≈ 2 ms ≈ 10 ms every 90 ms → 4 sample slots/frame at risk → 0–7 % volume (depends on whether catch-up reads NACK; must be measured, B6).

## Not verified
Real hardware behaviour (nothing built), SDP810 current datasheet values, whether test accounts are already deleted, Firestore region, filter fit/resistance, actual Cd, reverse-flow ΔP, Thai FDA class and research-exemption procedure.
