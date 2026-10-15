// DIY IoT Spirometer — XIAO ESP32-S3 + SDP810-500Pa (venturi D28/d23)
// Targets: XIAO ESP32-S3 or XIAO ESP32-C3 (same 21 x 17.8 footprint; pins switch automatically).
// Features: breath test (FVC/FEV1/FEV1-FVC/PEF), BLE live stream, Wi-Fi upload to Firebase RTDB (REST), battery %, NTP time.
// Button (D1 = GPIO2): short press = start test, long press (>1.5 s) = zero offset. LED on D2 = GPIO3.
// NOT a medical device. Venturi model Q = K*sqrt(dP); K from calibration with a 3 L syringe (see README).
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <Preferences.h>
#include <time.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// Config is stored in flash; set it over serial: "wifi SSID PASS", "db URL", "dev ID", "auth SECRET", "k 0.705"
Preferences prefs;
String WIFI_SSID = "", WIFI_PASS = "", DB_URL = "", DEV_ID = "spiro-01", DB_AUTH = "";
float K_VENT = 0.705f;                    // L/s per sqrt(Pa): theory Cd=0.97, D28/d23. CALIBRATE.
#if CONFIG_IDF_TARGET_ESP32C3             // XIAO ESP32-C3: D4=GPIO6, D5=GPIO7, D1=GPIO3, D2=GPIO4, D0=GPIO2
const int SDA_PIN = 6, SCL_PIN = 7, BTN_PIN = 3, LED_PIN = 4, BAT_PIN = 2;
#else                                     // XIAO ESP32-S3: D4=GPIO5, D5=GPIO6, D1=GPIO2, D2=GPIO3, D0=GPIO1
const int SDA_PIN = 5, SCL_PIN = 6, BTN_PIN = 2, LED_PIN = 3, BAT_PIN = 1;
#endif
const float DEADBAND_PA = 0.15f;          // |dP| below this -> 0 flow (sqrt law blows up zero-offset noise; ~0.27 L/s)
const float END_FLOW = 0.25f;             // end of test when flow stays below this for 1 s
const uint32_t SAMPLE_US = 2500;          // 400 Hz

float scalePa = 60.0f, offsetPa = 0;
struct Result { float fvc, fev1, ratio, pef; uint32_t ms; time_t ts; bool valid; } last;
BLECharacteristic* chLive = nullptr;
BLECharacteristic* chRes = nullptr;
bool bleOn = false;

uint8_t crc8(const uint8_t* d, int n) {
  uint8_t c = 0xFF;
  for (int i = 0; i < n; i++) { c ^= d[i]; for (int b = 0; b < 8; b++) c = (c & 0x80) ? (c << 1) ^ 0x31 : (c << 1); }
  return c;
}
bool sdpStart() {
  Wire.beginTransmission(0x25); Wire.write(0x36); Wire.write(0x15);   // continuous, differential pressure, averaged
  return Wire.endTransmission() == 0;
}
bool sdpRead(float& dp) {
  if (Wire.requestFrom(0x25, 9) != 9) return false;
  uint8_t b[9]; for (int i = 0; i < 9; i++) b[i] = Wire.read();
  if (crc8(b, 2) != b[2] || crc8(b + 6, 2) != b[8]) return false;
  int16_t raw = (int16_t)((b[0] << 8) | b[1]);
  int16_t sc = (int16_t)((b[6] << 8) | b[7]);
  if (sc) scalePa = sc;
  dp = raw / scalePa;
  return true;
}
float flowLps(float dp) {
  if (fabsf(dp) < DEADBAND_PA) return 0;
  float s = dp < 0 ? -1 : 1;
  return s * K_VENT * sqrtf(fabsf(dp));
}
float batteryPct() {
  float v = analogReadMilliVolts(BAT_PIN) * 2.0f / 1000.0f;
  return constrain((v - 3.3f) / (4.15f - 3.3f) * 100.0f, 0, 100);
}

void loadCfg() {
  prefs.begin("spiro", true);
  WIFI_SSID = prefs.getString("ssid", ""); WIFI_PASS = prefs.getString("pass", "");
  DB_URL = prefs.getString("db", ""); DEV_ID = prefs.getString("dev", "spiro-01"); DB_AUTH = prefs.getString("auth", "");
  K_VENT = prefs.getFloat("k", 0.705f); offsetPa = prefs.getFloat("off", 0);
  prefs.end();
}
void saveStr(const char* k, const String& v) { prefs.begin("spiro", false); prefs.putString(k, v); prefs.end(); }
void saveF(const char* k, float v) { prefs.begin("spiro", false); prefs.putFloat(k, v); prefs.end(); }

void zero() {
  float sum = 0, v; int n = 0;
  for (int i = 0; i < 400; i++) { if (sdpRead(v)) { sum += v; n++; } delayMicroseconds(SAMPLE_US); }
  if (n) { offsetPa = sum / n; saveF("off", offsetPa); }
  Serial.printf("zero offset %.3f Pa (n=%d)\n", offsetPa, n);
}
void wifiUp() {
  if (WiFi.status() == WL_CONNECTED || WIFI_SSID == "") return;
  WiFi.mode(WIFI_STA); WiFi.begin(WIFI_SSID.c_str(), WIFI_PASS.c_str());
  uint32_t t = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t < 8000) delay(100);
  if (WiFi.status() == WL_CONNECTED) configTime(7 * 3600, 0, "pool.ntp.org", "time.google.com");
}
bool upload(const Result& r) {
  wifiUp();
  if (WiFi.status() != WL_CONNECTED || DB_URL == "") return false;
  WiFiClientSecure cli; cli.setInsecure();      // no cert pinning: ok for a class demo
  HTTPClient http;
  String url = DB_URL + "/devices/" + DEV_ID + "/sessions.json" + (DB_AUTH.length() ? "?auth=" + DB_AUTH : "");
  char body[256];
  snprintf(body, sizeof body,
           "{\"ts\":%lld,\"fvc\":%.2f,\"fev1\":%.2f,\"ratio\":%.1f,\"pef\":%.2f,\"dur_ms\":%lu,\"bat\":%.0f,\"fw\":\"1.0\"}",
           (long long)r.ts * 1000LL, r.fvc, r.fev1, r.ratio, r.pef, (unsigned long)r.ms, batteryPct());
  if (!http.begin(cli, url)) return false;
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(body);
  http.end();
  Serial.printf("upload -> HTTP %d\n", code);
  return code >= 200 && code < 300;
}
void bleNotify(const char* s, BLECharacteristic* c) {
  if (bleOn && c) { c->setValue((uint8_t*)s, strlen(s)); c->notify(); }
}
class SrvCb : public BLEServerCallbacks {
  void onConnect(BLEServer*) { bleOn = true; }
  void onDisconnect(BLEServer* s) { bleOn = false; s->startAdvertising(); }
};
void bleInit() {
  BLEDevice::init(("Spiro-" + DEV_ID).c_str());
  BLEServer* s = BLEDevice::createServer();
  s->setCallbacks(new SrvCb());
  BLEService* sv = s->createService("6e400001-b5a3-f393-e0a9-e50e24dcca9e");
  chLive = sv->createCharacteristic("6e400002-b5a3-f393-e0a9-e50e24dcca9e", BLECharacteristic::PROPERTY_NOTIFY);
  chRes = sv->createCharacteristic("6e400003-b5a3-f393-e0a9-e50e24dcca9e",
                                   BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_READ);
  chLive->addDescriptor(new BLE2902());
  chRes->addDescriptor(new BLE2902());
  sv->start();
  BLEDevice::getAdvertising()->addServiceUUID(sv->getUUID());
  BLEDevice::startAdvertising();
}

// ---- quality: ATS/ERS-style checks that this firmware CAN do (no flow-time back-extrapolation yet)
const char* quality(const Result& r) {
  if (r.ms < 3000) return "short";            // < 3 s exhalation (adult)
  if (r.pef < 1.0f) return "weak";
  return "ok";
}
// repeatability over the last 3 valid tests: best two FVC and FEV1 within 0.15 L (ATS 2019) -> grade A
float histFvc[3] = {0, 0, 0}, histFev[3] = {0, 0, 0}; int nHist = 0;
char grade() {
  if (nHist < 2) return '-';
  int n = nHist < 3 ? nHist : 3; float a = 0, b = 0, c = 0, d = 0;
  for (int i = 0; i < n; i++) { if (histFvc[i] > a) { b = a; a = histFvc[i]; } else if (histFvc[i] > b) b = histFvc[i];
                                if (histFev[i] > c) { d = c; c = histFev[i]; } else if (histFev[i] > d) d = histFev[i]; }
  return (a - b <= 0.15f && c - d <= 0.15f) ? 'A' : 'C';
}
// offline queue: results that failed to upload are kept in flash (max 20) and sent with the next result
void queuePush(const Result& r) {
  prefs.begin("q", false);
  int n = prefs.getInt("n", 0); if (n >= 20) n = 19;
  char k[8]; snprintf(k, sizeof k, "r%d", n);
  prefs.putBytes(k, &r, sizeof r); prefs.putInt("n", n + 1); prefs.end();
}
void queueFlush() {
  prefs.begin("q", false); int n = prefs.getInt("n", 0); prefs.end();
  for (int i = 0; i < n; i++) {
    Result r; prefs.begin("q", true); char k[8]; snprintf(k, sizeof k, "r%d", i);
    size_t got = prefs.getBytes(k, &r, sizeof r); prefs.end();
    if (got != sizeof r || !upload(r)) return;
  }
  prefs.begin("q", false); prefs.putInt("n", 0); prefs.end();
}

void runTest() {
  digitalWrite(LED_PIN, HIGH);
  Serial.println("blow now (max 15 s)...");
  float vol = 0, pef = 0, fev1 = 0, dp;
  uint32_t t0 = 0, tNext = micros(), lastFlow = millis(), tStart = millis(), tl = 0;
  bool started = false;
  while (millis() - tStart < 15000) {
    while ((int32_t)(micros() - tNext) < 0) {}
    tNext += SAMPLE_US;
    if (!sdpRead(dp)) continue;
    float q = flowLps(dp - offsetPa);
    if (!started) { if (q > 0.3f) { started = true; t0 = millis(); lastFlow = millis(); } else continue; }
    uint32_t t = millis() - t0;
    vol += q * SAMPLE_US * 1e-6f;
    if (q > pef) pef = q;
    if (t <= 1000) fev1 = vol;
    if (t - tl >= 40) {
      tl = t;
      char s[40]; snprintf(s, sizeof s, "%lu,%.2f,%.2f", (unsigned long)t, q, vol);
      bleNotify(s, chLive);
      Serial.println(s);
    }
    if (q > END_FLOW) lastFlow = millis();
    if (millis() - lastFlow > 1000 && t > 1000) break;     // end: flow < END_FLOW for 1 s
  }
  digitalWrite(LED_PIN, LOW);
  if (batteryPct() < 15) for (int i = 0; i < 6; i++) { digitalWrite(LED_PIN, !digitalRead(LED_PIN)); delay(120); }  // low battery
  last = { vol, fev1, vol > 0 ? 100 * fev1 / vol : 0, pef, started ? millis() - t0 : 0, time(nullptr), started && vol > 0.2f };
  Serial.printf("RESULT FVC=%.2f L FEV1=%.2f L FEV1/FVC=%.0f%% PEF=%.1f L/s\n", last.fvc, last.fev1, last.ratio, last.pef);
  if (last.valid) {
    char s[96]; snprintf(s, sizeof s, "R,%.2f,%.2f,%.1f,%.2f,%s", last.fvc, last.fev1, last.ratio, last.pef, quality(last));
    bleNotify(s, chRes);
    histFvc[nHist % 3] = last.fvc; histFev[nHist % 3] = last.fev1; nHist++;
    Serial.printf("quality=%s grade=%c battery=%.0f%%\n", quality(last), grade(), batteryPct());
    if (upload(last)) { Serial.println("cloud: saved"); queueFlush(); }
    else { queuePush(last); Serial.println("cloud: offline -> queued in flash"); }
  }
}
void cmd(String l) {
  l.trim();
  if (l == "z") zero();
  else if (l == "s") runTest();
  else if (l.startsWith("wifi ")) {
    int i = l.indexOf(' ', 5);
    saveStr("ssid", l.substring(5, i)); saveStr("pass", l.substring(i + 1)); loadCfg(); Serial.println("wifi saved");
  }
  else if (l.startsWith("db ")) { saveStr("db", l.substring(3)); loadCfg(); Serial.println("db saved"); }
  else if (l.startsWith("auth ")) { saveStr("auth", l.substring(5)); loadCfg(); Serial.println("auth saved"); }
  else if (l.startsWith("dev ")) { saveStr("dev", l.substring(4)); loadCfg(); Serial.println("device id saved (reboot)"); }
  else if (l.startsWith("k ")) { K_VENT = l.substring(2).toFloat(); saveF("k", K_VENT); Serial.printf("K=%.4f\n", K_VENT); }
  else if (l == "info")
    Serial.printf("dev=%s wifi=%s db=%s K=%.4f off=%.3f bat=%.0f%%\n", DEV_ID.c_str(), WIFI_SSID.c_str(), DB_URL.c_str(),
                  K_VENT, offsetPa, batteryPct());
}
void setup() {
  Serial.begin(115200);
  pinMode(BTN_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  loadCfg();
  Wire.begin(SDA_PIN, SCL_PIN, 400000);
  Serial.println(sdpStart() ? "SDP810 ok" : "SDP810 NOT FOUND");
  delay(100);
  zero();
  bleInit();
  wifiUp();
  Serial.println("cmds: z s info | wifi SSID PASS | db https://<proj>.firebaseio.com | dev ID | auth SECRET | k 0.705");
}
void loop() {
  if (Serial.available()) cmd(Serial.readStringUntil('\n'));
  if (digitalRead(BTN_PIN) == LOW) {
    uint32_t t = millis();
    while (digitalRead(BTN_PIN) == LOW && millis() - t < 2000) delay(10);
    if (millis() - t > 1500) zero(); else runTest();
    while (digitalRead(BTN_PIN) == LOW) delay(10);
  }
}
