# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# เครื่องวัดสมรรถภาพปอดพิมพ์ 3D (Spirometer) — BOM (python make_bom.py) → bom.md + bom.csv next to this file
import os, csv, urllib.parse as u
HERE = os.path.dirname(os.path.abspath(__file__))
H = 'have'
rows = [  # group, item, spec, qty, unit THB (est.), status 'buy'|'buy?'|H, search keyword, note
    ('อิเล็กทรอนิกส์', 'บอร์ดหลัก Seeed XIAO ESP32-S3 (หรือ ESP32-C3)', '21x17.8 mm, BLE+Wi-Fi, มีวงจรชาร์จ LiPo', 1, 350, 'buy', 'Seeed XIAO ESP32S3', 'C3 ใช้ได้เหมือนกัน (ถูกกว่า) ใส่ได้ footprint เดียวกัน'),
    ('อิเล็กทรอนิกส์', 'เซ็นเซอร์ความดันต่าง Sensirion SDP810-500Pa', 'I2C 0x25, บน breakout 26x14 + ขั้ว JST-GH 4 ขา', 1, 1200, 'buy?', 'SDP810-500Pa breakout', 'ตัวเดียวที่อาจไม่มีใน Shopee: ถ้าหาไม่ได้สั่ง Mouser/DigiKey/Element14 + breakout; ตัว SMD ต้องบัดกรีละเอียด'),
    ('อิเล็กทรอนิกส์', 'จอกลม GC9A01 1.28 นิ้ว', '240x240 SPI, PCB กลม Ø37', 1, 150, 'buy', 'GC9A01 1.28 inch round LCD', 'ตรวจว่าเป็นรุ่น 7 ขา (ไม่มีทัช)'),
    ('อิเล็กทรอนิกส์', 'แบตเตอรี่ LiPo 603450 1000 mAh', '3.7 V มีวงจร PCM, ขนาด 6x34x50 mm', 1, 150, 'buy', 'LiPo 603450 1000mAh 3.7V', 'ต้องมีวงจรป้องกัน; ขั้วต่อ JST 1.25/PH ให้ตรงกับบอร์ดหรือบัดกรีตรง'),
    ('อิเล็กทรอนิกส์', 'ลำโพงกลมบาง Ø16 x 3.5 mm 8 ohm 0.5 W', 'ติดผนังด้ามขวา เสียงออกรู Ø1.4 x 19 รู', 1, 25, 'buy', 'mini speaker 16mm 8ohm 0.5W', 'ตรวจขนาดจริงก่อนพิมพ์ (ถ้า Ø15/Ø20 ปรับ SPK_D ใน model.py); ติดเทปโฟมกันเสียงรั่ว'),
    ('อิเล็กทรอนิกส์', 'แอมป์เสียง I2S MAX98357A breakout', '3 W class-D, ~19 x 18 mm, ไม่ต้องมี DAC', 1, 90, 'buy', 'MAX98357A I2S amplifier module', 'ต่อ BCLK/LRC/DIN เข้า D3/D6/D7, ใช้ 3.3 V จากบอร์ด, SD/GAIN ปล่อยค่าเดิม'),
    ('อิเล็กทรอนิกส์', 'ปุ่ม tact switch 6x6 สูง 7 mm', 'ก้านยาว 7 mm', 2, 3, 'buy', 'tact switch 6x6x7', 'ซื้อเผื่อ 1'),
    ('อิเล็กทรอนิกส์', 'LED 3 mm', 'สีเขียว/ฟ้า + R 330 ohm', 2, 2, 'buy', 'LED 3mm', 'บวกตัวต้านทาน 330 ohm'),
    ('อิเล็กทรอนิกส์', 'ตัวต้านทาน 4.7 kohm', 'ดึงขึ้น I2C 2 ตัว + ตัวหาร R 100 kohm 2 ตัว (วัดแบต)', 6, 1, 'buy', 'resistor kit 1/4W', 'ซื้อเป็นชุด'),
    ('อิเล็กทรอนิกส์', 'สายไฟ 28-30 AWG / สาย silicone', 'หลายสี', 1, 40, 'buy', 'สายไฟ 28AWG silicone', ''),
    ('อิเล็กทรอนิกส์', 'USB-C breakout (แท่นชาร์จ)', 'ตัวเมีย 5 V', 1, 30, 'buy', 'USB-C breakout board', ''),
    ('กล/ตัวยึด', 'Pogo pin ก้าน Ø2.0', 'สปริง 2 ตัว ระยะยื่น ~2 mm', 2, 15, 'buy', 'pogo pin 2mm spring', 'วัดเส้นผ่าศูนย์กลางก้านให้ได้ 2.0 mm (รูเจาะ 2.2)'),
    ('กล/ตัวยึด', 'น็อตฝังทองเหลือง M3 x 5 (OD4.5)', 'heat-set insert', 4, 1, 'buy', 'heat set insert M3 5mm', 'ซื้อแพ็ค 50-100 ตัว'),
    ('กล/ตัวยึด', 'น็อตฝังทองเหลือง M3 x 4 (OD4.5)', 'heat-set insert', 6, 1, 'buy', 'heat set insert M3 4mm', 'แท่นชาร์จ 4 + หน้าสัมผัสบนเครื่อง 2'),
    ('กล/ตัวยึด', 'สกรู M3x20 หัวเตเปอร์ (flat head)', '', 4, 1, 'buy', 'M3x20 flat head screw', 'ตัวเครื่อง'),
    ('กล/ตัวยึด', 'สกรู M3x6 หัวเตเปอร์', '', 4, 1, 'buy', 'M3x6 flat head screw', 'ปิดแท่นชาร์จ'),
    ('กล/ตัวยึด', 'แม่เหล็กนีโอไดเมียม 5x2', '', 8, 3, 'buy', 'neodymium magnet 5x2', 'ฝาท่อ 4 คู่ (ตรวจขั้วตอนติดกาว)'),
    ('กล/ตัวยึด', 'แม่เหล็กนีโอไดเมียม 6x3', '', 2, 5, 'buy', 'neodymium magnet 6x3', 'นำทางด้ามเข้าแท่น'),
    ('กล/ตัวยึด', 'ท่อซิลิโคน ID3 OD5', 'ยาว ~50 mm 2 ท่อน', 1, 30, 'buy', 'silicone tube 3x5mm', ''),
    ('กล/ตัวยึด', 'ยางรองเท้า Ø10 x 3 mm', '', 4, 3, 'buy', 'rubber feet 10mm adhesive', 'ใต้แท่นชาร์จ'),
    ('วัสดุพิมพ์', 'เส้น PETG (สีขาว/ใส/เขียวอ่อน) สำหรับที่เป่าต้นแบบ', 'ที่เป่าใช้แล้วทิ้ง ชิ้นละ ~11 g (~5 บาท)', 1, 400, 'buy?', 'PETG filament 1kg', 'ใช้พิมพ์ที่เป่าอย่างเดียว; ไม่ย่อยสลาย รุ่นต่อไปเปลี่ยนเป็นวัสดุเศษพืช; ซื้อเป็นม้วน 250-500 g ก็ได้'),
    ('กล/ตัวยึด', 'กาวตะกั่ว/ซุปเปอร์กลู + สายคล้องมือ', 'ติดขอบจอและฝาปุ่ม; สายร้อยรู Ø4.5 ที่ท้ายด้าม', 1, 30, 'buy', 'super glue gel + wrist strap cord', 'ใช้กาวเจลหยดเล็กน้อย อย่าให้เข้าหน้าจอ'),
    ('วัสดุพิมพ์', 'เทปโฟมกาวสองหน้า 1 mm', 'ติดลำโพง/กันเสียงรั่ว', 1, 20, 'buy', 'foam tape 1mm double sided', ''),
    ('วัสดุพิมพ์', 'เส้น PETG', '≈ 520 g (รวม +10%)', 1, 450, 'buy?', 'PETG filament 1kg', 'ถ้ามีเส้นอยู่แล้วไม่ต้องซื้อ'),
]
def shopee(k): return 'https://shopee.co.th/search?keyword=' + u.quote(k) if k else ''
def lazada(k): return 'https://www.lazada.co.th/catalog/?q=' + u.quote(k) if k else ''
with open(os.path.join(HERE, 'bom.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['#', 'Group', 'Item', 'Spec', 'Qty', 'Unit THB (est.)', 'Total THB', 'Status', 'Shopee', 'Lazada', 'Note'])
    for i, (g, it, sp, q, up, st, k, n) in enumerate(rows, 1):
        w.writerow([i, g, it, sp, q, up, round(q * up), st, shopee(k), lazada(k), n])
total = sum(round(q * up) for g, it, sp, q, up, st, k, n in rows if st.startswith('buy'))
out = ['# เครื่องวัดสมรรถภาพปอดพิมพ์ 3D (Spirometer) — รายการอุปกรณ์ (BOM)', '', 'ราคาเป็นราคาประมาณ — ลิงก์เป็นหน้าค้นหา', '',
       '| # | กลุ่ม | รายการ | สเปก | จำนวน | ราคา/หน่วย | รวม | สถานะ | ลิงก์ |', '|---|---|---|---|---|---|---|---|---|']
for i, (g, it, sp, q, up, st, k, n) in enumerate(rows, 1):
    s = 'มีแล้ว' if st == H else ('ซื้อ (ถ้ายังไม่มี)' if st == 'buy?' else 'ซื้อ')
    lk = f'[Shopee]({shopee(k)}) · [Lazada]({lazada(k)})' if k else '—'
    out.append(f'| {i} | {g} | {it} | {sp}{" — " + n if n else ""} | {q} | {up:g} | {round(q * up):,} | {s} | {lk} |')
out += ['', f'**รวมต้องซื้อ ≈ {total:,} บาท**']
open(os.path.join(HERE, 'bom.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('items', len(rows), 'total', total)
