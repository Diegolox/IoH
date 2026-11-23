# Prototipo 02: IMU por BLE con etiquetado de movimientos

Basado en `01_ble_imu`, con etiquetado automático mediante teclas mantenidas
en la aplicación Python para Windows. El firmware conserva su contenido original.
No incluye registros de experimentos anteriores.

- **XIAO:** lee aceleración y giro en los tres ejes a 104 Hz nominales y envía
  las muestras en binario por BLE. La lectura y el envío funcionan por separado.
- **PC:** muestra en un panel la conexión, la última muestra de los seis ejes,
  la etiqueta, las frecuencias, los saltos y el estado del CSV.
  Mientras la captura está conectada, P/R/T/M/Q se iluminan al mantenerlas
  pulsadas. La etiqueta de la última muestra usa el color del movimiento.
  Espacio inicia un CSV nuevo o cierra la grabación activa, sin pulsar Enter.
  No sobrescribe grabaciones. Ctrl+C cierra el CSV y termina el programa.
- **Rangos:** se cambian en las variables `ACCEL_RANGE_G` y `GYRO_RANGE_DPS`
  al principio de `xiao/src/main.cpp`, y después se vuelve a cargar el firmware.

En Windows, abre `pc/` en el Explorador y haz doble clic en **IoH-Captura.exe**.
Al arrancar, escribe el nombre de la muestra y pulsa Enter. El programa
lo muestra en el panel y busca la XIAO. Cada CSV de esa ejecución empieza
por el nombre, seguido de la fecha, la hora y un identificador único.
Los espacios se convierten en guiones bajos. Si pulsas Enter sin escribir,
el prefijo es `imu`. Para cambiar de muestra, cierra y vuelve a abrir el programa.
El ejecutable incluye Python y sus dependencias.

El binario se genera localmente. Para reproducirlo desde `pc/`:

```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller
.\compilar.cmd
```

Durante el desarrollo puedes iniciar el código con `python imu_terminal.py`.
Para ver el panel con datos de ejemplo, usa `python imu_terminal.py --vista-previa`.
Abre `xiao/` como proyecto PlatformIO si necesitas compilar y cargar el firmware.

Los CSV se guardan en `pc/registros/`. La herramienta de gráficas está en
`../../herramientas/graficar/`; copia allí los CSV que quieras analizar.

Cada notificación BLE recibida se decodifica y recibe una etiqueta según las
teclas mantenidas en ese instante. Los datos llegan en binario (`<IH6h`), no en
JSON. La etiqueta se guarda en la nueva columna `label` del CSV, junto a los
tiempos, el contador y los seis ejes. La terminal también muestra la etiqueta.

| Tecla mantenida | Movimiento | `label` |
| --- | --- | --- |
| P | Pase | `pase` |
| R | Recepción | `recepcion` |
| T | Tiro de muñeca | `tiro` |
| M | Manejo de puck | `manejo` |
| Q | Palo quieto, sostenido en posición de juego | `reposo` |
| Ninguna | Sin movimiento etiquetado | `undefined` |

Al soltar la tecla se vuelve a `undefined`; varias teclas de etiqueta a la
vez también producen `undefined` para evitar una elección ambigua. No depende
de mayúsculas, Bloq Mayús ni de la autorrepetición del teclado.

La consulta de P/R/T/M/Q es global en Windows: también detecta esas teclas si
cambias de ventana. Mantén la terminal activa para Espacio y Ctrl+C y dedica
el teclado a etiquetar durante la captura. La consulta usa `ctypes` y
[GetAsyncKeyState de Windows](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate).

La etiqueta corresponde a la recepción en el PC, sin compensar retrasos de BLE
ni el tiempo de reacción de quien etiqueta. No garantiza la alineación exacta
con el instante de medida de la IMU; se acepta esta aproximación para el prototipo.

Comprobaciones automáticas desde `pc/` (sin dispositivo BLE):

```powershell
python -m unittest discover -v
```

En la prueba inicial optimizada del prototipo 01 se documentaron unos 106,4 Hz
y cero saltos del contador. No se han repetido esas pruebas con el prototipo 02.
No se aplica calibración ni filtrado; la aceleración incluye gravedad.
No usa FIFO de la IMU: el contador no detecta conversiones perdidas antes de leerlas.
