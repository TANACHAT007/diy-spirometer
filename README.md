<!-- CREDIT-STAMP -->
> **Designed by Tanachat S. (TANACHAT007) / MEDTHAI, 2026** - please keep this credit when you use or share this work. See [CREDITS.md](CREDITS.md).
<!-- /CREDIT-STAMP -->

# DIY IoT Spirometer (MEDTHAI)

3D-printed handheld spirometer: printed venturi + Sensirion SDP810-500Pa + XIAO ESP32-S3/C3, BLE + Wi-Fi to a web dashboard, charging dock.
Prepared for International Youth Summit (IYS) 2026, sub-theme Health.

**Status: design prototype.** CAD, firmware (compiles for ESP32-S3 and C3) and web pages are done. Nothing has been printed, assembled or measured yet,
so all numbers are calculations or datasheet values. Not a certified medical device; learning / screening aid only.

| Folder | Contents |
|---|---|
| `brief.md` | research, decisions, build log |
| `02_design/` | `model.py` (Fusion 360 script), feasibility + accuracy analysis |
| `03_renders/` | CAD renders |
| `04_print_stl/` | STL for Bambu A1 PETG + `print_guide.md` |
| `06_cad_export/` | STEP assembly |
| `08_firmware/` | ESP32 firmware + wiring/calibration README |
| `09_bom/` | parts list with Shopee/Lazada search links |
| `10_manual/web/` | product page + dashboard (HTML) |

Calibrate the venturi constant K with a 3 L syringe before trusting any reading (see `08_firmware/README.md`).

**เว็บ:** https://tanachat007.github.io/diy-spirometer/
