#include <Arduino.h>
#include <Adafruit_TinyUSB.h>  // Puerto serie USB del core de Seeed/Adafruit.

namespace {
constexpr uint32_t kSerialBaud = 115200;
constexpr uint32_t kBlinkIntervalMs = 500;
uint32_t lastBlinkMs = 0;
bool statusLedOn = false;
}  // namespace

void setup() {
    // El LED integrado es activo a nivel bajo: LOW enciende, HIGH apaga.
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    Serial.begin(kSerialBaud);
    // Espera limitada: la placa tambien debe arrancar alimentada por bateria.
    const uint32_t startMs = millis();
    while (!Serial && millis() - startMs < 3000) {
        delay(10);
    }

    if (Serial) {
        Serial.println("IoH | XIAO nRF52840 Sense iniciada");
    }
}

void loop() {
    const uint32_t nowMs = millis();
    if (nowMs - lastBlinkMs >= kBlinkIntervalMs) {
        lastBlinkMs = nowMs;
        statusLedOn = !statusLedOn;
        digitalWrite(LED_BUILTIN, statusLedOn ? LOW : HIGH);

        if (Serial) {
            Serial.print("Tiempo (ms): ");
            Serial.println(nowMs);
        }
    }

    // Anade aqui la lectura de sensores y la logica de la aplicacion.
    delay(1);
}
