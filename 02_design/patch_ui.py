# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
s = open('diy_spirometer.ino', encoding='utf-8').read()
blk = open('ui_block.txt', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b)


rep("// Button (D1 = GPIO2): short press = start test, long press (>1.5 s) = zero offset. LED on D2 = GPIO3.",
    "// Button (D1 = GPIO2): short press = start test, hold 1.5 s = zero offset, hold 4 s = new mouthpiece. LED on D2 = GPIO3.\n"
    "// ESP32-S3 only: GC9A01 round display (LovyanGFX) + MAX98357A I2S speaker (soft tones) + disposable-mouthpiece life counter.")
rep("#include <BLE2902.h>\n", """#include <BLE2902.h>
#if CONFIG_IDF_TARGET_ESP32C3
#define HAS_UI 0                          // C3: no display / speaker (fewer pins, one core)
#else
#define HAS_UI 1
#endif
#if HAS_UI
#define LGFX_USE_V1
#include <LovyanGFX.hpp>
#include <driver/i2s.h>
#endif
""")
rep("const float DEADBAND_PA", """#if HAS_UI                                // XIAO ESP32-S3: TFT SCK=D8, MOSI=D10, DC=D9 (CS->GND, RST->3V3: 3 pins only); I2S BCLK=D3, LRC=D6, DIN=D7
const int TFT_SCK = 7, TFT_MOSI = 9, TFT_DC = 8, I2S_BCLK = 4, I2S_LRC = 43, I2S_DIN = 44;
#endif
const float DEADBAND_PA""")
rep("void loadCfg() {", blk + "void loadCfg() {")
# config load
rep('K_VENT = prefs.getFloat("k", 0.705f); offsetPa = prefs.getFloat("off", 0);',
    'K_VENT = prefs.getFloat("k", 0.705f); offsetPa = prefs.getFloat("off", 0);\n'
    '  mpUses = prefs.getUShort("mpn", 0); mpStart = prefs.getUInt("mps", 0); volPct = prefs.getInt("vol", 40);')
# loadCfg is defined BEFORE the block -> move the mp variables to the top instead
open('diy_spirometer.ino', 'w', encoding='utf-8').write(s)
print('ok')
