# Código de IoH

Se ha desarrollado un primer código para probar cómo se reciben en el ordenador
las medidas del acelerómetro y el giróscopo de la XIAO nRF52840 Sense mediante BLE.
Permite ver la señal y la frecuencia en terminal, guardar las lecturas en CSV
y generar gráficas para revisar los resultados.

| Carpeta | Contenido |
| --- | --- |
| `prototipos/01_ble_imu/` | Primer prototipo: firmware XIAO y receptor del PC. |
| `prototipos/02_ble_imu/` | Adquisición BLE con etiquetado automático por teclas mantenidas en Python (Windows). |
| [`prototipos/03_ble_imu/`](prototipos/03_ble_imu/README.md) | Panel de captura de Windows `IoH-Captura-03.exe` con nivel estimado de batería y aviso. |
| `herramientas/graficar/` | Gráficas de movimiento, comparación de gestos y frecuencia de recepción. |
| [`herramientas/re-etiquetador/`](herramientas/re-etiquetador/README.md) | Corrección con el ratón de etiquetas por muestra o por tramo, con guardado en el CSV y copia de la captura original. |

Cada prototipo contiene su proyecto PlatformIO en `xiao/`, su programa de PC
en `pc/` y un README breve. Para una nueva prueba que cambie el funcionamiento,
añade `prototipos/02_nombre_prueba/`. Usa Git para las correcciones pequeñas.
Cuando exista una implementación definitiva, se ubicará en `sistema/`.

Los experimentos se documentan en `../doc/experimental/`, indicando el prototipo,
la versión de Git, los rangos y el montaje utilizados. Los registros existentes
se conservan en `prototipos/01_ble_imu/pc/registros/`.

Para graficar, indica las rutas de los CSV a `herramientas/graficar/graficar.py`
o usa su menú para seleccionar archivos de la carpeta de la herramienta.
Con `--salida` puedes guardar las figuras en el experimento correspondiente.
