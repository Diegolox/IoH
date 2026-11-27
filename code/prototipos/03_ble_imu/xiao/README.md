# Firmware XIAO del prototipo 03

Abre esta carpeta en PlatformIO y pulsa Build / Upload.
El programa está en `src/main.cpp` y las dependencias en `platformio.ini`.
Lee acelerómetro y giróscopo a 104 Hz nominales y envía muestras por BLE
con nombre `XIAO-IMU`. Usa la variante nRF52840 Sense y su bus interno Wire1.

Cambia `ACCEL_RANGE_G` (2, 4, 8 o 16 g) y `GYRO_RANGE_DPS`
(125, 245, 500, 1000 o 2000 grados/s) en main.cpp para ajustar los rangos ±.
Aumenta el rango si satura y vuelve a cargar. Python no necesita cambiar escalas.

La lectura corre en una tarea independiente con un búfer de 64 muestras.
Se transmite tiempo uint32, contador uint16 y seis int16: 18 bytes little-endian.
Aceleración en milésimas de g y giro en décimas de grado/s.
La IMU funciona sin calibración y sin FIFO.

La batería se mide fuera de la tarea de IMU. El ADC promedia ocho lecturas
del divisor de la placa y publica un porcentaje orientativo al arrancar y cada
10 s. El PC puede leer ese valor sin solicitar una conversión nueva.
El divisor permanece habilitado con `VBAT_ENABLE` en `LOW`, de acuerdo con
la [guía de Seeed](https://wiki.seeedstudio.com/XIAO_BLE/).

El receptor está en `../pc/`. Consulta también el README del prototipo.
