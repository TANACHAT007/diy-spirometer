# diy-spirometer — IoT system

Device (XIAO ESP32-S3 + SDP810-500Pa venturi) → **BLE** live curve, **Wi-Fi → Firebase Realtime DB (REST)** → web dashboard `10_manual/web/index.html` (patient / doctor view, TH/EN, dark theme, CSV export — same pattern as SmartLung/LungCare).

## Wiring (XIAO ESP32-S3)
| Part | XIAO pin |
|---|---|
| SDP810 SDA / SCL / 3V3 / GND | D4 (GPIO5) / D5 (GPIO6) / 3V3 / GND (4.7 k pull-ups) |
| Button (to GND) | D1 (GPIO2), internal pull-up |
| LED (+330 Ω) | D2 (GPIO3) |
| Battery sense | D0 (GPIO1) via 2 × 100 k divider from BAT+ |
| LiPo 603450 | BAT+/BAT− pads (on-board charger) |
| GC9A01 display (optional, SPI) | not in this firmware yet |

## Upload + configure
1. Arduino IDE / `arduino-cli`, board `XIAO_ESP32S3`, open `diy_spirometer/diy_spirometer.ino`.
2. Serial 115200, type: `wifi MySSID MyPass`, `db https://<project>-default-rtdb.<region>.firebasedatabase.app`, `dev spiro-01`, `info`.
3. Press the button (short = test, hold 1.5 s = zero). Result → serial, BLE, cloud.

## Firebase (you must create it — I cannot)
1. console.firebase.google.com → new project → Realtime Database → create.
2. Rules (class demo; tighten before real patients):
```
{ "rules": { "devices": { "$dev": { ".read": true, ".write": true } } } }
```
   Better: keep rules at `false` and use a database secret/auth token via the `auth <token>` serial command and the dashboard ⚙ field.
3. Host `10_manual/web/index.html` (Firebase Hosting / GitHub Pages / any static host), open ⚙, enter DB URL + device id.

Data path: `/devices/<dev>/sessions/<push-id> = {ts(ms), fvc, fev1, ratio, pef, dur_ms, bat, fw}`.

## BLE
Service `6e400001-…`: notify `…0002` live `t_ms,flow_Lps,vol_L`; notify/read `…0003` result `R,fvc,fev1,ratio,pef`. Use nRF Connect to test; web app via Web Bluetooth can be added.

## Calibration (required before any number is trusted)
`K` converts √ΔP to flow: theory 0.705 L/s·Pa^-½ (Cd 0.97, D28/d23). Inject 3 L with a calibration syringe 5× quickly; compare FVC; set `k <old K × 3.0/measured>`. Saturation: SDP810-500Pa clips at 500 Pa ≈ 15.8 L/s (covers 16 L/s target roughly).

## Status
Compiled only; **not tested on hardware**. Pin map assumed from the XIAO ESP32-S3 pinout. Not a certified medical device — education/screening only.

## ESP32-C3 (XIAO ESP32-C3) — ใช้ได้ (footprint 21×17.8 เท่า S3)
- ขา: SDA D4=GPIO6, SCL D5=GPIO7, ปุ่ม D1=GPIO3, LED D2=GPIO4, แบต D0=GPIO2 (สลับอัตโนมัติด้วย `CONFIG_IDF_TARGET_ESP32C3`)
- คอมไพล์: `--fqbn esp32:esp32:XIAO_ESP32C3:PartitionScheme=huge_app` (BLE+Wi-Fi+TLS ใหญ่เกิน partition ปกติ 1.3 MB; แลกกับไม่มี OTA)
- C3 คอร์เดียว 160 MHz: การสุ่ม 400 Hz ใน `runTest()` ทำได้ แต่ห้ามอัปโหลด/ซิงก์ระหว่างเป่า (โค้ดอัปโหลดหลังเป่าเสร็จอยู่แล้ว); จอ GC9A01 แบบเฟรมเต็มอาจกวนจังหวะ → วาดเฉพาะตอนไม่เป่า
- ฟังก์ชันเพิ่มที่ใส่แล้ว: deadband ลมเบา, ตัดสินคุณภาพ (สั้น/อ่อน), เกรดความซ้ำได้ A/C (3 ครั้ง ต่างกัน ≤0.15 L), คิวออฟไลน์ 20 รายการเก็บใน flash แล้วส่งเมื่อออนไลน์, LED เตือนแบตต่ำ
- ยังไม่ได้ทำ: OTA, Wi-Fi provisioning ผ่านมือถือ, แปลง BTPS, ค่าอ้างอิง (GLI-2012 % predicted), หน้าจอ
