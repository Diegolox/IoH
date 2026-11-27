// XIAO nRF52840 Sense. Core: Seeed nRF52 Boards (NO mbed).
// Libreria: Seeed Arduino LSM6DS3. Bluefruit viene con el core.
#include <Arduino.h>
#include <Adafruit_TinyUSB.h>
#include <bluefruit.h>
#include <LSM6DS3.h>
#include <math.h>
#include <Wire.h>

// CAMBIA ESTAS DOS VARIABLES y vuelve a cargar el programa:
const uint16_t ACCEL_RANGE_G = 16;   // +/- 2, 4, 8 o 16 g. Sube si satura.
const uint16_t GYRO_RANGE_DPS = 2000; // +/- 125, 245, 500, 1000 o 2000 grados/s.
// Mayor rango = admite movimientos mayores, pero menor sensibilidad.

LSM6DS3 imu(I2C_MODE, 0x6A);
BLEService service("ac450001-8c4d-4e82-a36d-2715dca20104");
BLECharacteristic imuData("ac450002-8c4d-4e82-a36d-2715dca20104");
BLEService batteryService(UUID16_SVC_BATTERY);
BLECharacteristic batteryLevel(UUID16_CHR_BATTERY_LEVEL);
constexpr uint32_t BATTERY_PERIOD_MS = 10000;
uint32_t lastBatteryReadMs = 0;

// 18 bytes little-endian. Python usa struct.Struct('<IH6h').
struct __attribute__((packed)) Sample {
  uint32_t time_us;
  uint16_t sequence;
  int16_t ax, ay, az; // milesimas de g
  int16_t gx, gy, gz; // decimas de grado/s
};
static_assert(sizeof(Sample) == 18, "Formato BLE incorrecto");
uint16_t sequence = 0;
QueueHandle_t samples;
volatile uint32_t queueDrops = 0;

uint8_t readBatteryPercent() {
  constexpr uint32_t readings = 8;
  uint32_t sum = 0;
  for (uint32_t i = 0; i < readings; ++i) {
    sum += analogRead(PIN_VBAT);
  }
  // R16 = 1 MΩ, R17 = 510 kΩ. Escala ADC de 3,0 V y 12 bits.
  const float millivolts = sum * (3000.0f / (4096 * readings)) * (1510.0f / 510.0f);
  // Curva orientativa para una LiPo de una celda en descarga.
  constexpr uint16_t voltage[] = {3300, 3600, 3700, 3800, 3900, 4000, 4100, 4200};
  constexpr uint8_t percent[] = {0, 10, 25, 50, 70, 85, 95, 100};
  if (millivolts <= voltage[0]) return 0;
  for (size_t i = 1; i < sizeof(percent); ++i) {
    if (millivolts <= voltage[i]) {
      const float fraction = (millivolts - voltage[i - 1]) / (voltage[i] - voltage[i - 1]);
      return lroundf(percent[i - 1] + fraction * (percent[i] - percent[i - 1]));
    }
  }
  return 100;
}

// Solo esta tarea toca la IMU. Bluetooth puede esperar sin detener la lectura.
void readIMU(void*) {
  while (true) {
    uint8_t status = 0;
    if (imu.readRegister(&status, 0x1E) == IMU_SUCCESS && (status & 3) == 3) {
      uint32_t stamp = micros();
      int16_t raw[6] = {};
      if (imu.readRegisterRegion((uint8_t*)raw, 0x22, sizeof(raw)) == IMU_SUCCESS) {
        Sample s;
        s.time_us = stamp;
        s.sequence = sequence++;
        s.ax = lroundf(imu.calcAccel(raw[3]) * 1000);
        s.ay = lroundf(imu.calcAccel(raw[4]) * 1000);
        s.az = lroundf(imu.calcAccel(raw[5]) * 1000);
        s.gx = lroundf(imu.calcGyro(raw[0]) * 10);
        s.gy = lroundf(imu.calcGyro(raw[1]) * 10);
        s.gz = lroundf(imu.calcGyro(raw[2]) * 10);
        if (Bluefruit.connected() && imuData.notifyEnabled()) {
          if (xQueueSend(samples, &s, 0) != pdTRUE) queueDrops++;
        }
      }
    }
    delay(1); // Cede CPU; no espera a Bluetooth ni marca la frecuencia de la IMU.
  }
}

void onConnect(uint16_t handle) {
  // Solicitud explicita: setConnInterval solo establece la preferencia.
  Bluefruit.Connection(handle)->requestConnectionParameter(12, 0); // 15 ms
}

void setup() {
  // Mantener el divisor habilitado. Seeed desaconseja poner P0.14 en HIGH al cargar.
  pinMode(VBAT_ENABLE, OUTPUT);
  digitalWrite(VBAT_ENABLE, LOW);
  analogReference(AR_INTERNAL_3_0);
  analogReadResolution(12);
  analogSampleTime(40); // Tiempo de adquisición para el divisor de alta impedancia.

  Serial.begin(115200); // No esperar al USB: funciona tambien con bateria.
  imu.settings.accelRange = ACCEL_RANGE_G;
  imu.settings.gyroRange = GYRO_RANGE_DPS;
  imu.settings.accelSampleRate = 104;
  imu.settings.gyroSampleRate = 104;
  if (imu.begin() != IMU_SUCCESS) {
    while (true) { Serial.println("Error al iniciar IMU"); delay(1000); }
  }
  Wire1.setClock(400000); // Bus interno de la Sense: I2C a 400 kHz.
  // BDU: evita mezclar bytes de dos lecturas. IF_INC: lectura consecutiva.
  uint8_t ctrl = 0;
  imu.readRegister(&ctrl, 0x12);
  imu.writeRegister(0x12, ctrl | 0x44);
  Serial.println("IMU OK: 104 Hz. BLE: XIAO-IMU");

  // Mas paquetes por evento y espacio para notificaciones pendientes.
  Bluefruit.configPrphConn(23, 6, 16, 1);
  Bluefruit.begin();
  Bluefruit.setName("XIAO-IMU");
  Bluefruit.Periph.setConnInterval(6, 12); // Solicita 7.5-15 ms; decide el PC.
  Bluefruit.Periph.setConnectCallback(onConnect);
  service.begin();
  imuData.setProperties(CHR_PROPS_NOTIFY);
  imuData.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  imuData.setFixedLen(sizeof(Sample));
  imuData.begin();
  batteryService.begin();
  batteryLevel.setProperties(CHR_PROPS_READ);
  batteryLevel.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  batteryLevel.setFixedLen(1);
  batteryLevel.begin();
  batteryLevel.write8(readBatteryPercent());
  lastBatteryReadMs = millis();
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addService(service);
  Bluefruit.ScanResponse.addName();
  Bluefruit.Advertising.restartOnDisconnect(true);
  samples = xQueueCreate(64, sizeof(Sample)); // Unos 0.6 s de margen a 104 Hz.
  if (!samples || xTaskCreate(readIMU, "imu", 1024, nullptr,
                             tskIDLE_PRIORITY + 2, nullptr) != pdPASS) {
    while (true) { Serial.println("Error creando tarea IMU"); delay(1000); }
  }
  Bluefruit.Advertising.start(0);
}

void loop() {
  Sample s;
  if (!Bluefruit.connected() || !imuData.notifyEnabled()) {
    xQueueReset(samples);
  } else if (xQueuePeek(samples, &s, 0) == pdTRUE) {
    // No retirar la muestra hasta que BLE la acepte; reintentar si esta ocupado.
    if (imuData.notify((uint8_t*)&s, sizeof(s))) xQueueReceive(samples, &s, 0);
  }
  const uint32_t now = millis();
  if (now - lastBatteryReadMs >= BATTERY_PERIOD_MS) {
    lastBatteryReadMs = now;
    batteryLevel.write8(readBatteryPercent());
  }
  delay(1);
}
