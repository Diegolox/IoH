#include <Arduino.h>
#include <Adafruit_TinyUSB.h>  // Puerto serie USB del core de Seeed/Adafruit.
#include <bluefruit.h>

namespace {
constexpr uint32_t kSerialBaud = 115200;
constexpr uint32_t kSampleIntervalMs = 5000;
constexpr uint32_t kHeartbeatPeriodMs = 1000;
constexpr uint32_t kHeartbeatPulseMs = 100;
// Indice Arduino del core Seeed/Adafruit: D23 corresponde a P0.17 (~CHG).
constexpr uint8_t kChargeStatusPin = 23;
constexpr uint8_t kAdcSamples = 16;
constexpr float kAdcFullScaleMv = 3600.0f;  // AR_INTERNAL: 0.6 V / (1/6).
constexpr float kBatteryDivider = (1000.0f + 510.0f) / 510.0f;
uint32_t lastSampleMs = 0;
bool firstSample = true;
BLEUart batteryUart;

uint32_t readBatteryMv() {
    // El divisor de 1 Mohm / 510 kohm requiere una adquisicion larga.
    analogRead(PIN_VBAT);  // Descarta la primera conversion.
    uint32_t total = 0;
    for (uint8_t i = 0; i < kAdcSamples; ++i) {
        total += analogRead(PIN_VBAT);
    }
    const float average = static_cast<float>(total) / kAdcSamples;
    return static_cast<uint32_t>(average * kAdcFullScaleMv * kBatteryDivider / 4095.0f + 0.5f);
}

void startBluetooth() {
    Bluefruit.begin();
    Bluefruit.autoConnLed(false);
    Bluefruit.setName("IoH-Battery");
    batteryUart.begin();
    Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
    Bluefruit.Advertising.addService(batteryUart);
    Bluefruit.ScanResponse.addName();
    Bluefruit.Advertising.restartOnDisconnect(true);
    Bluefruit.Advertising.setInterval(160, 1600);  // 100 ms / 1 s.
    Bluefruit.Advertising.setFastTimeout(30);
    Bluefruit.Advertising.start(0);
}
}  // namespace

void setup() {
    // Mantener LOW: Seeed desaconseja deshabilitar el divisor durante la carga.
    digitalWrite(VBAT_ENABLE, LOW);
    pinMode(VBAT_ENABLE, OUTPUT);
    // Alta impedancia, sin pull: selecciona aproximadamente 50 mA (0.2 C).
    pinMode(PIN_CHARGING_CURRENT, INPUT);
    pinMode(kChargeStatusPin, INPUT_PULLUP);
    analogReference(AR_INTERNAL);
    analogReadResolution(12);
    analogSampleTime(40);
    analogCalibrateOffset();
    delay(10);

    // LED activo a nivel bajo; el loop genera un pulso de vida cada segundo.
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    Serial.begin(kSerialBaud);
    startBluetooth();
}

void loop() {
    const uint32_t nowMs = millis();
    digitalWrite(LED_BUILTIN,
                 nowMs % kHeartbeatPeriodMs < kHeartbeatPulseMs ? LOW : HIGH);
    if (firstSample || nowMs - lastSampleMs >= kSampleIntervalMs) {
        firstSample = false;
        lastSampleMs = nowMs;
        const uint32_t batteryMv = readBatteryMv();
        const bool usbPresent = (NRF_POWER->USBREGSTATUS & POWER_USBREGSTATUS_VBUSDETECT_Msk) != 0;
        const bool charging = digitalRead(kChargeStatusPin) == LOW;
        const char* state = !usbPresent ? "BATTERY" : (charging ? "CHARGING" : "USB_IDLE");

        // CSV: tiempo_ms,voltaje_mV,usb_presente,chg_activo,estado.
        char line[96];
        snprintf(line, sizeof(line), "%lu,%lu,%u,%u,%s\r\n",
                 static_cast<unsigned long>(nowMs), static_cast<unsigned long>(batteryMv),
                 static_cast<unsigned>(usbPresent), static_cast<unsigned>(charging), state);
        if (Serial) Serial.print(line);
        if (Bluefruit.connected() && batteryUart.notifyEnabled()) batteryUart.print(line);
    }

    // No se mide corriente ni se estima un porcentaje de carga.
    delay(10);
}
