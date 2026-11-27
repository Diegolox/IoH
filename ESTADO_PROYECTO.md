# Estado del proyecto IoH

Actualizado: **27/11/2026**. Las pruebas históricas se atribuyen a su documentación.

## Objetivo y situación actual

Internet for Hockey, proyecto de LAB Sensores: explorar la detección de gestos de hockey mediante sensores inerciales. El protocolo propone una IMU en el stick para distinguir pase, recepción, tiro de muñeca, manejo y `undefined`.

Existe un primer prototipo de adquisición con XIAO nRF52840 Sense, receptor Python por BLE y herramienta de análisis de CSV. Hay revisión bibliográfica, documentación de hardware, STL de la carcasa y cuatro capturas exploratorias del experimento 1. El prototipo 02 incorpora etiquetado automático por teclado en recepción; entrenamiento e inferencia siguen pendientes.

Se ha creado `code/prototipos/02_ble_imu/` a partir del prototipo 01, sin registros ni artefactos locales. Conserva el firmware y modifica el receptor Python para Windows: cada notificación BLE recibe `label` según la tecla mantenida (P=`pase`, R=`recepcion`, T=`tiro`, M=`manejo`; ninguna o varias=`undefined`). Guarda la etiqueta en el CSV y la muestra en terminal. Espacio inicia/cierra cada CSV y Ctrl+C termina. La consulta de etiquetas es global en Windows; los controles de terminal requieren foco. Diego acepta el desfase del etiquetado al llegar los datos al PC, sin compensación temporal.

El prototipo 03 añade al panel la carga aproximada de la LiPo de 3,7 V y 250 mAh y un aviso al 25 % estimado o menos. El firmware y el receptor se han compilado. Falta probar el conjunto con la XIAO en batería.

El re-etiquetador permite corregir con el ratón las etiquetas de los CSV de captura. Guarda en la ruta abierta y conserva una copia previa a la primera edición para mantener la trazabilidad.

## Configuración y decisiones documentadas

- Etiquetado de reposo en el prototipo 02: mantener Q con el palo quieto guarda `reposo`. Al soltarla, o si se pulsan varias teclas de etiqueta, se guarda `undefined`. La herramienta de gráficas distingue ambas etiquetas. Los CSV anteriores al cambio conservan su etiquetado original.
- Prototipo actual: acelerómetro y giróscopo a **104 Hz nominales**; firmware Arduino mediante PlatformIO y core Seeed nRF52, sin mbed.
- El código actual configura **±16 g y ±2000 °/s**. Estos valores no acreditan los rangos usados en capturas anteriores, que no los incluyen como metadatos.
- Transporte implementado: BLE binario de 18 bytes, formato little-endian `<IH6h`, con tiempo de la XIAO, contador y seis ejes. Receptor y firmware coinciden en el formato. El PC guarda CSV mediante `start` y `stop` en el 01 y Espacio en el 02; este último añade `label` al recibir cada notificación, antes de la cola de visualización.
- Batería en el 03: ADC fuera de la tarea de la IMU al arrancar y cada 10 s, con una curva de descarga orientativa. El PC consulta Battery Level al conectar y cada 10 s, independientemente de la recepción de muestras. El porcentaje se muestra en el panel y el CSV conserva su esquema.
- Sin filtrado ni calibración; la aceleración incluye gravedad. El firmware no usa FIFO de la IMU y el contador no permite detectar conversiones perdidas antes de leerlas.
- El protocolo plantea etiquetado con teclado, separación por jugador antes de generar ventanas, entrenamiento con Edge Impulse e inferencia Python en PC. Reserva a Diego para test final. Son decisiones de diseño documentadas, pendientes de implementación y validación; la ventana de 2 s es una configuración inicial, no definitiva.
- La ubicación prevista entre las manos difiere de la colocación inferior usada en el experimento 1. Conservar esta distinción al interpretar resultados.

## Mapa de archivos

| Ruta | Uso |
| --- | --- |
| [README.md](README.md) | Presentación y acceso a documentación. |
| [code/README.md](code/README.md) | Organización del código y criterio para nuevos prototipos. |
| [code/prototipos/01_ble_imu/](code/prototipos/01_ble_imu/) | Firmware en `xiao/`; receptor `pc/imu_terminal.py`. |
| [code/prototipos/02_ble_imu/](code/prototipos/02_ble_imu/) | Firmware del 01 y receptor con etiquetado por teclas mantenidas en Python. |
| [code/prototipos/02_ble_imu/pc/compilar.cmd](code/prototipos/02_ble_imu/pc/compilar.cmd) | Genera `IoH-Captura.exe` para abrir el panel de captura por doble clic en Windows. |
| [code/prototipos/03_ble_imu/](code/prototipos/03_ble_imu/) | Firmware y receptor con la batería en la primera línea del panel. Ejecutable local en `pc/IoH-Captura-03.exe`. |
| [code/herramientas/graficar/](code/herramientas/graficar/) | Gráficas de movimiento y frecuencia de recepción, con comparación de tramos etiquetados. |
| [code/herramientas/re-etiquetador/](code/herramientas/re-etiquetador/) | Editor gráfico de etiquetas. En Windows se abre con `abrir_re_etiquetador.cmd` y usa Python 3 con Tkinter. |
| [doc/experimental/protocolo-experimental.md](doc/experimental/protocolo-experimental.md) | Diseño previsto y decisiones pendientes del piloto. |
| [doc/experimental/README.md](doc/experimental/README.md) | Resumen breve de los resultados de los experimentos 1 y 2. |
| [doc/experimental/experimento_1/README.md](doc/experimental/experimento_1/README.md) | Montaje, capturas, resultados y límites de la prueba del 21/11/2026. |
| [doc/experimental/experimento_2/README.md](doc/experimental/experimento_2/README.md) | Preparación de dos tomas con el tercer jugador y pastillas de hielo y línea sobre plástico. |
| [doc/state_of_art/README.md](doc/state_of_art/README.md) | PICOS y enlaces a cribado, síntesis, entregables y matriz de evidencia. |
| [doc/state_of_art/borrador-articulo-ieee.md](doc/state_of_art/borrador-articulo-ieee.md) | Borrador del entregable 5 con siete publicaciones evaluadas. Pendientes el cierre del cribado y PRISMA, el mínimo de diez publicaciones, la revisión de Diego y la maquetación IEEE. |
| [doc/hardware/](doc/hardware/) | Hojas de componentes y comparativa de placas. |
| [doc/doc_prof/](doc/doc_prof/) | Material metodológico del profesor. |
| [3d/Correcciones_carcasa.md](3d/Correcciones_carcasa.md) | Cotas, correcciones, referencias y comprobaciones físicas pendientes. |
| [3d/](3d/) | Base y tapa STL y referencias de montaje. |

## Comandos y entorno existentes

Los comandos siguientes están documentados; **no se han ejecutado en esta sesión**. No se ha comprobado la instalación local de dependencias ni de PlatformIO.

Desde `code/prototipos/01_ble_imu/pc/`:

```powershell
python -m pip install -r requirements.txt
python imu_terminal.py
```

Dependencia del receptor: `bleak>=1.0,<4`. Los nuevos registros se guardan en `pc/registros/`; comprobar su existencia local antes de asumir que contiene capturas.

Desde `code/herramientas/graficar/`, con los CSV copiados junto a `graficar.py`:

```powershell
python -m pip install -r requirements.txt
python graficar.py --todos --sin-ventana
```

Dependencias: `numpy>=1.24,<3` y `matplotlib>=3.7,<4`. El menú busca CSV locales. También admite rutas explícitas y `--salida` para guardar las figuras aparte. Mantener los originales en su ubicación.

Firmware: abrir `code/prototipos/01_ble_imu/xiao/` en PlatformIO; configuración en `platformio.ini`, entorno `xiao_nrf52840_sense`. Compilar o cargar desde ese proyecto cuando la tarea lo requiera.

## Comprobaciones y límites

- **27/11/2026, re-etiquetador:** cuatro pruebas del editor correctas. Se simularon clic, arrastre, zoom, guardado y deshacer en Tk sobre copias de las cuatro capturas etiquetadas del 02. Se verificó que solo cambiaran los campos seleccionados y que la copia inicial coincidiera con el original. No se probó el guardado con el CSV abierto en Excel.
- **27/11/2026, prototipo 03:** compilación PlatformIO para XIAO nRF52840 Sense con la plataforma Seeed instalada (1.1.1). El receptor pasó seis pruebas, incluidos el aviso bajo, la indicación cuando falta la característica BLE y la ubicación de la batería en un panel de 60 columnas. Se comprobó la vista previa de `IoH-Captura-03.exe` con una batería simulada al 23 %.
- **24/11/2026, entregable 4:** evaluadas las siete publicaciones con los ocho criterios de la guía. La pestaña «Calidad y sesgo» de la matriz incluye 56 justificaciones con páginas y puntuaciones por fórmula. El resumen quedó antes del Paso 5 en el Word original `doc/doc_prof/metodologia_EdC.docx`. Hardegger obtuvo la menor puntuación (4,0/8). Hardegger, Shahar (2020) y Vleugels cumplen plenamente tres criterios y quedan señalados para la discusión. Se verificaron los datos y la conservación del contenido previo. La paginación del Word queda sin revisión visual por falta de LibreOffice.
- **24/11/2026, entregable 3 en el Word del profesor:** incorporada una tabla de síntesis de las siete publicaciones antes del Paso 4 en `doc/doc_prof/metodologia_EdC.docx`, con montaje, muestreo, método, resultados, evaluación, localizadores y nivel de verificación. Remite al Excel de extracción completa y mantiene visibles los pendientes y el alcance metodológico o parcial de algunos artículos. Comprobadas las siete filas, la apertura estructural del DOCX y la conservación del contenido anterior y de las demás partes del paquete. No se completó la revisión visual de paginación: el renderizador no dispone de LibreOffice y se detuvo el intento con Word a petición de Diego, que indicó no tomar control de su PC. No se buscaron publicaciones nuevas; queda por resolver el mínimo de diez papers de la tabla final y cerrar el cribado antes de PRISMA.
- **23/11/2026, conclusiones del experimento 2:** cuatro capturas, nueve tramos de manejo y unos 66,5 s etiquetados como manejo. El giro mediano fue mayor durante el manejo en todas las tomas, pero hubo picos de giro en `undefined`. Se documentó el carácter exploratorio de la comparación entre pastillas y la falta de etiquetas de pase, recepción y tiro.
- **23/11/2026, resumen por prueba:** se añadieron paneles separados de aceleración X/Y/Z y resúmenes de los seis ejes y las dos magnitudes, por captura y por etiqueta. Se generó el índice de las cuatro pruebas del experimento 2. Se verificaron esas cuatro entradas, un CSV sin etiquetas, la opción de solo frecuencia y la integridad de los originales.
- **23/11/2026, gráficas de movimiento:** se generaron figuras para los cuatro CSV etiquetados del prototipo 02, que contienen manejo y `undefined`. La comparación alinea por el inicio de la etiqueta y usa escalas comunes. Se comprobó un CSV histórico sin etiquetas, el modo `--solo-frecuencia` y que los CSV de entrada conservaran sus hashes.
- **23/11/2026, nombre de muestra:** el receptor lo pide antes de conectar, lo muestra en el panel y lo usa como prefijo de los CSV de la ejecución. Se verificó el arranque y la vista previa del ejecutable regenerado. Las cuatro pruebas pasan, incluida la escritura de dos CSV con prefijo normalizado y sin sobrescritura. Pendiente comprobar la captura con la XIAO real.
- **23/11/2026, resaltado del teclado:** P/R/T/M tienen colores distintos al mantenerlas pulsadas durante la conexión. El panel consulta las teclas independientemente de la llegada de muestras. Se verificaron los cuatro estilos, la liberación y la pulsación simultánea con teclado simulado, además de las cuatro pruebas existentes. Se regeneró el ejecutable y se comprobó su vista previa.
- **23/11/2026, panel y ejecutable:** compilado `pc/IoH-Captura.exe` para Windows x64 con PyInstaller 6.20, Bleak 0.22.3 y Rich 13.9.4. Se verificaron la vista previa del binario, la inclusión del backend WinRT, los estados del panel a 60 y 100 columnas y las cuatro pruebas de teclado y CSV simuladas. Pendiente la captura completa con la XIAO y el teclado reales. El binario es local y se regenera con `pc/compilar.cmd`.
- **23/11/2026, prototipo 02:** `python -m unittest discover -s code/prototipos/02_ble_imu/pc -v`: 4 pruebas correctas (teclas mantenidas y liberación, ambigüedad, bit de pulsación pasada, CSV con etiquetas y sesiones independientes, control de autorrepetición de Espacio). Carga de `GetAsyncKeyState` comprobada; `git diff --check` sin errores. La prueba de controles usa pasos simulados: el inicio de un bucle `asyncio` real se bloqueó en el socket local de Windows del entorno restringido, antes de ejecutar los controles. No se ha validado la ejecución completa de la aplicación, el teclado físico ni BLE.
- **23/11/2026, revisión local:** repositorio Git en esta carpeta, rama `main`, sin cambios locales al comenzar. No existían `AGENTS.md` ni `ESTADO_PROYECTO.md` en el proyecto. Se revisaron README, protocolo, experimento 1, notas de carcasa, dependencias, configuración PlatformIO y formato BLE en firmware y receptor.
- **Resultado histórico documentado, 21/11/2026:** cuatro capturas con aproximadamente 106,4 Hz y cero saltos del contador. No recalculado en esta sesión. Las capturas denominadas reposo contienen movimiento y no son una referencia de inmovilidad continua ni clases temporales limpias.
- Las notas de carcasa indican correcciones aplicadas y encaje comprobado en Fusion; no se ha verificado el modelo ni el montaje físico en esta sesión.

## Pendientes y siguiente paso

1. Preparar un piloto reproducible: registrar versión de Git, rangos, posición exacta y orientación del dispositivo; incluir un tramo de reposo continuo y anotaciones temporales verificables.
2. Comprobar estabilidad del montaje y saturación para los gestos objetivo; verificar físicamente espacio para interruptor/cables, acceso USB y apriete de tornillos según las notas de carcasa.
3. Validar el etiquetado del prototipo 02 con teclado y BLE reales; concretar jugadores, cantidad de datos, métricas y tratamiento de ventanas mixtas antes de entrenar. Mantener el test de Diego separado del ajuste.

**Siguiente paso:** probar el prototipo 03 con la XIAO alimentada por batería. Comparar tasa recibida, intervalos y saltos frente al 02, verificar P/R/T/M/Q y los controles de grabación, y medir cuánto tarda en apagarse desde el aviso. Después, preparar la captura piloto con los metadatos indicados.
