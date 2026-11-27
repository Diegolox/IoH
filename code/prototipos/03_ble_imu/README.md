# Prototipo 03: IMU por BLE con aviso de batería

Basado en `02_ble_imu`, con etiquetado automático mediante teclas mantenidas
y aviso de batería en la aplicación Python para Windows. Usa una LiPo de
una celda de 3,7 V nominales y 250 mAh.

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

En Windows, abre `pc/` en el Explorador y haz doble clic en **IoH-Captura-03.exe**.
Al arrancar, escribe el nombre de la muestra y pulsa Enter. El programa
lo muestra en el panel y busca la XIAO. Cada CSV de esa ejecución empieza
por el nombre, seguido de la fecha, la hora y un identificador único.
Los espacios se convierten en guiones bajos. Si pulsas Enter sin escribir,
el prefijo es `imu`. Para cambiar de muestra, cierra y vuelve a abrir el programa.
El ejecutable incluye Python y sus dependencias.

## Batería durante la captura

La XIAO mide la tensión antes de anunciarse por BLE y actualiza la estimación
cada 10 s. La tarea de la IMU mantiene su configuración de 104 Hz nominales.
El PC consulta el último porcentaje al conectar y cada 10 s mediante el servicio
BLE Battery Service (`0x180F`, característica `0x2A19`). El panel señala
**Batería baja** al 25 % estimado o menos. El nivel aparece en la primera línea
del panel **IoH / Captura IMU 03**. Si la XIAO no expone la característica
de batería, el panel indica que hay que cargar el firmware 03. Si falla una
consulta, muestra **Sin lectura**. En ambos casos la captura sigue disponible.
El CSV conserva las columnas de movimiento y etiqueta.

La curva de tensión es orientativa. Comprueba la indicación con una descarga
usando el sensor alimentado por batería y transmitiendo, y mide cuánto tiempo
queda entre el aviso y el apagado. Valida el ritmo con dos capturas comparables,
una con el prototipo 02 y otra con el 03. Compara la tasa recibida, los intervalos
entre `xiao_time_us` y los saltos de `sequence`, incluidos los intervalos que
coinciden con las consultas de batería.

## Ejecución y registros

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

No se aplica calibración ni filtrado; la aceleración incluye gravedad.
No usa FIFO de la IMU: el contador no detecta conversiones perdidas antes de leerlas.
