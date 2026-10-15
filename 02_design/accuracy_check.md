# ความแม่นยำของการวัดลม (venturi D28/d23 + SDP810-500Pa) — 2026-10-15

Sensor (Sensirion SDP810-500Pa, preliminary datasheet v0.5): zero-point accuracy ≈0.1 Pa, repeatability 0.05 Pa, span 3 % of reading, 16-bit. (ตรวจ datasheet ฉบับล่าสุดก่อนอ้างอิงจริง)
Model: Q = K·√ΔP, K ≈ 0.705 L/s/√Pa (Cd 0.97, β = 0.82) — ต้อง calibrate.

| Q (L/s) | ΔP (Pa) | error from 0.1 Pa zero offset | หมายเหตุ |
|---|---|---|---|
| 0.2 | 0.08 | +50 % | เกินใช้ได้ — ใช้ deadband |
| 0.5 | 0.50 | +9 % | |
| 1 | 2.0 | +2 % | |
| 2–15 | 8–500 | ≤ 1 % | span 3 %ΔP → ≈1.5 % Q (ผ่าน ATS 3 %) |
| 15.8 | 500 | saturate | เพดานของ -500Pa ≈ PEF 15.8 L/s (เป้า 16) |

## ข้อสรุป
1. **ช่วงไหล 1–15 L/s แม่น (~1.5–3 %)** ตรงตามข้อกำหนด FVC/FEV1/PEF — ถ้า calibrate K และ zero ทุกครั้ง
2. **ลมเบา (< 0.3 L/s) ไม่แม่น** เพราะกฎ √ΔP: ออฟเซ็ต 0.05 Pa ค้าง → อินทิเกรตหาง 6 s ได้ปริมาตรเกินจริง ≈ 0.9 L → เฟิร์มแวร์ใส่ deadband 0.15 Pa (≈0.27 L/s) + จบเทสเมื่อไหล < 0.25 L/s นาน 1 s (ATS ต้องการ 0.025 L/s จึง *ไม่ตรงมาตรฐาน* → ใช้คัดกรอง ไม่ใช่วินิจฉัย)
3. **Reynolds ต่ำ**: Re ≈ 48 000 ที่ 16 L/s (ต่ำกว่าช่วง ISO 5167 venturi 1.5·10⁵) และ Cd ตกที่ลมเบา → ใช้ K เดี่ยวมีความคลาดเคลื่อน ต้อง calibrate หลายอัตราไหล (syringe 3 L ช้า/กลาง/เร็ว) แล้วปรับเป็น K(Q) หรือ polynomial
4. **BTPS**: ลมหายใจอุ่น/ชื้น (ρ ≈ 1.12 vs 1.20) → อ่านสูงขึ้นราว 3.5 % ถ้า calibrate ด้วยอากาศห้อง — calibrate ด้วยกระบอกฉีดช่วยได้บางส่วน แต่ยังไม่ได้แปลง BTPS
5. **ความชื้น/คอนเดนเสท** ในสายซิลิโคน 3×5 mm ทำให้ ΔP เพี้ยน → ติดสายชี้ลง/ใส่ตัวกรองไฮโดรโฟบิก และเป่าล้างหลังใช้
6. **ท่อพิมพ์ 3D**: ผิวหยาบ/รั่วที่ tap ทำให้ Cd ไม่นิ่ง → ทดสอบรั่ว, ทาซีล
7. DIY ที่ validate แล้ว (Frontiers 2025, venturi + MXP5010DP): error 1.53 % — เป็นเป้าอ้างอิง ไม่ใช่ผลของเครื่องนี้ (ยังไม่มีการวัดจริง)

## ต้องวัดจริงก่อนอ้างค่า
- syringe 3 L ×5 ความเร็วต่าง → ค่า K, ความคลาดเคลื่อน %
- zero drift 10 นาที, ทดสอบรั่วที่ tap, ความซ้ำได้ (CV)

## Tail truncation of FVC (found 2026-10-15)
The firmware ends a test when flow stays below 0.25 L/s for 1 s (the 0.15 Pa deadband already zeroes flow below ~0.27 L/s). For a healthy blow with a slow tail
(3-exponential model: FVC 4.0 L, FEV1 2.9 L, PEF 10 L/s) the volume at the cut is 3.52 L, i.e. **FVC reads ~12 % low and FEV1/FVC reads 0.83 instead of 0.73**:
obstruction could be masked. v1.2 firmware estimates the tail as q_cut x tau (exponential fitted over the last second above the cut), capped at 0.5 L / 15 % of the volume.
This is an unvalidated correction; verify with the 3 L syringe and a healthy volunteer against a reference spirometer before trusting the ratio.
