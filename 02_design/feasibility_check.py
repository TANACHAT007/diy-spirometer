# diy-spirometer feasibility: Venturi D28/d23 + Sensirion SDP810-500Pa + XIAO ESP32-S3 + LiPo 603450 + dock
# run: py feasibility_check.py  -> feasibility.md
import math, os

RHO, CD = 1.15, 0.98          # exhaled air ~34 C saturated; Cd calibrated later with a syringe
D, d = 28.0, 23.0
beta = d / D
At = math.pi * (d / 2000) ** 2
k = 1 - beta ** 4
SDP_FS, SDP_SCALE = 500.0, 60.0          # SDP810-500Pa: +-500 Pa, 60 counts/Pa (datasheet)


def dp(q):
    v = q / 1000 / (CD * At)
    return 0.5 * RHO * k * v * v


ok = lambda c: '✅' if c else '❌'
rows = [(q, dp(q), dp(q) * SDP_SCALE) for q in (0.1, 0.2, 0.5, 1, 2, 5, 8, 10, 12, 14, 16)]
q_sat = CD * At * math.sqrt(2 * SDP_FS / (RHO * k)) * 1000
r_cm = 0.15 * dp(16) / 98.07 / 16
BAT_MAH, I_ACT, I_SLEEP = 1000, 95.0, 0.08          # mA: S3 Wi-Fi bursts + TFT + sensor ; deep sleep
tests_per_charge = BAT_MAH * 0.8 / (I_ACT * (90 / 3600))      # 90 s per test incl. upload
checks = [
    ('ช่วงวัด ≥ 16 L/s ก่อนเซนเซอร์อิ่มตัว (ndd = ±16)', f'อิ่มตัวที่ {q_sat:.1f} L/s', q_sat >= 16),
    ('ความต้านทานลม < 1.5 cmH2O/L/s (ATS/ERS 2019)', f'{r_cm:.3f} cmH2O/L/s', r_cm < 1.5),
    ('ความละเอียดที่ 0.2 L/s (ปลายการเป่า)', f'{dp(0.2):.3f} Pa = {dp(0.2) * SDP_SCALE:.1f} count', dp(0.2) * SDP_SCALE >= 2),
    ('อัตราสุ่ม ≥ 100 Hz', 'SDP810 continuous 0.5 ms → ใช้ 200 Hz', True),
    ('แบต 1000 mAh ต่อการชาร์จ', f'≈ {tests_per_charge:.0f} ครั้งเป่า / ชาร์จ, sleep ≈ {BAT_MAH * 0.8 / I_SLEEP / 24:.0f} วัน', tests_per_charge > 100),
    ('ชาร์จผ่านแท่น (XIAO S3 charger 100 mA)', f'≈ {BAT_MAH / 100 * 1.2:.0f} ชม. เต็ม (ตั้งไว้บนแท่นข้ามคืน)', True),
    ('ขั้วสปริง pogo 2 ขา 1 A', '5 V 0.5 A สูงสุด', True),
]
md = ['# Feasibility — DIY Spirometer (IoT, Venturi + SDP810)', '',
      f'Venturi D = {D} mm, d = {d} mm (β = {beta:.3f}), ρ = {RHO}, Cd = {CD}; Sensirion SDP810-500Pa (±500 Pa, I2C).', '',
      '| Q (L/s) | ΔP (Pa) | count SDP810 |', '|---|---|---|']
md += [f'| {q} | {p_:.3f} | {c:.0f} |' for q, p_, c in rows]
md += ['', '| ตรวจ | ค่า | ผล |', '|---|---|---|'] + [f'| {a} | {b} | {ok(c)} |' for a, b, c in checks]
md += ['', '## เทียบกับ ndd Easy on-PC',
       '| | ndd Easy on-PC | ของเรา |', '|---|---|---|',
       '| การเชื่อมต่อ | สาย USB เข้า PC | ไร้สาย BLE (มือถือ) + Wi-Fi → คลาวด์ + USB-C |',
       '| พลังงาน | ไฟจาก USB | แบต LiPo 1000 mAh + แท่นชาร์จ |',
       '| แสดงผล | บนคอมเท่านั้น | จอกลม 1.28" บนตัวเครื่อง + เว็บแอป + แดชบอร์ดห้องเรียน |',
       '| ข้อมูล | ซอฟต์แวร์ PC | Firebase: ประวัติรายคน, กราฟ, ส่งออก CSV |',
       '| ราคา | ~60,000+ บาท | ~2,000 บาท |',
       '| ความแม่นยำ | ±2.5 % (รับรอง ATS/ERS) | เป้าหมาย ±5 % หลังสอบเทียบ (ยังไม่รับรอง) |',
       '', '## ข้อจำกัด',
       '- ΔP ของ Venturi เป็นบวกทั้งสองทิศ → วัดลมออกเป็นหลัก (FVC, FEV1, PEF, FEV1/FVC, FEF25-75).',
       '- ต้องสอบเทียบ Cd กับกระบอกฉีด 3 L (หรือยืมจากโรงพยาบาล) ก่อนอ้างตัวเลข.',
       '- เป็นเครื่องมือเพื่อการเรียนรู้/คัดกรองเบื้องต้น ไม่ใช่เครื่องมือแพทย์.']
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feasibility.md')
open(out, 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print('\n'.join(md))
