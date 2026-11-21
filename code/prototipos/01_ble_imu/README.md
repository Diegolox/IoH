# Prototipo 01: medidas IMU por BLE

Primera prueba para comprobar la recepción de las medidas del sensor en el PC.

- **XIAO:** lee aceleración y giro en los tres ejes a 104 Hz nominales y envía
  las muestras en binario por BLE. La lectura y el envío funcionan por separado.
- **PC:** muestra medidas, frecuencia y saltos del contador en terminal.
  `start` inicia un CSV nuevo y `stop` lo cierra. No sobrescribe grabaciones.
- **Rangos:** se cambian en las variables `ACCEL_RANGE_G` y `GYRO_RANGE_DPS`
  al principio de `xiao/src/main.cpp`, y después se vuelve a cargar el firmware.

Abre `xiao/` como proyecto PlatformIO para compilar y cargar.
Desde `pc/`, instala las dependencias y ejecuta:

```powershell
python -m pip install -r requirements.txt
python imu_terminal.py
```

Los CSV se guardan en `pc/registros/`. La herramienta de gráficas está en
`../../herramientas/graficar/`; copia allí los CSV que quieras analizar.

En la prueba inicial optimizada se observaron unos 106,4 Hz y cero saltos del
contador. Es una comprobación inicial, no una garantía para todas las condiciones.
No se aplica calibración ni filtrado; la aceleración incluye gravedad.
No usa FIFO de la IMU: el contador no detecta conversiones perdidas antes de leerlas.
