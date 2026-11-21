# Código de IoH

Se ha desarrollado un primer código para probar cómo se reciben en el ordenador
las medidas del acelerómetro y el giróscopo de la XIAO nRF52840 Sense mediante BLE.
Permite ver la señal y la frecuencia en terminal, guardar las lecturas en CSV
y generar gráficas para revisar los resultados.

| Carpeta | Contenido |
| --- | --- |
| `prototipos/01_ble_imu/` | Primer prototipo: firmware XIAO y receptor del PC. |
| `herramientas/graficar/` | Herramienta compartida para analizar CSV. |

Cada prototipo contiene su proyecto PlatformIO en `xiao/`, su programa de PC
en `pc/` y un README breve. Para una nueva prueba que cambie el funcionamiento,
añade `prototipos/02_nombre_prueba/`. Usa Git para las correcciones pequeñas.
Cuando exista una implementación definitiva, se ubicará en `sistema/`.

Los experimentos se documentan en `../doc/experimental/`, indicando el prototipo,
la versión de Git, los rangos y el montaje utilizados. Los registros existentes
se conservan en `prototipos/01_ble_imu/pc/registros/`.

Para graficar, coloca los CSV junto a `herramientas/graficar/graficar.py`.
Esta herramienta solo busca en su propia carpeta y genera una carpeta de análisis
por CSV. Los resultados se pueden incorporar después al experimento correspondiente.
