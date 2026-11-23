# Estado del proyecto IoH

Actualizado: **23/11/2026**. Memoria inicial contrastada con los archivos locales; las pruebas históricas se atribuyen a su documentación y no se han repetido en esta sesión.

## Objetivo y situación actual

Internet for Hockey, proyecto de LAB Sensores: explorar la detección de gestos de hockey mediante sensores inerciales. El protocolo propone una IMU en el stick para distinguir pase, recepción, tiro de muñeca, manejo y `undefined`.

Existe un primer prototipo de adquisición con XIAO nRF52840 Sense, receptor Python por BLE y herramienta de análisis de CSV. Hay revisión bibliográfica, documentación de hardware, STL de la carcasa y cuatro capturas exploratorias del experimento 1. En el código revisado no se ha identificado implementación de etiquetado temporal, entrenamiento ni inferencia; esas etapas figuran como trabajo previsto.

## Configuración y decisiones documentadas

- Prototipo actual: acelerómetro y giróscopo a **104 Hz nominales**; firmware Arduino mediante PlatformIO y core Seeed nRF52, sin mbed.
- El código actual configura **±16 g y ±2000 °/s**. Estos valores no acreditan los rangos usados en capturas anteriores, que no los incluyen como metadatos.
- Transporte implementado: BLE binario de 18 bytes, formato little-endian `<IH6h`, con tiempo de la XIAO, contador y seis ejes. Receptor y firmware coinciden en el formato. El PC guarda CSV mediante `start` y `stop`.
- Sin filtrado ni calibración; la aceleración incluye gravedad. El firmware no usa FIFO de la IMU y el contador no permite detectar conversiones perdidas antes de leerlas.
- El protocolo plantea etiquetado con teclado, separación por jugador antes de generar ventanas, entrenamiento con Edge Impulse e inferencia Python en PC. Reserva a Diego para test final. Son decisiones de diseño documentadas, pendientes de implementación y validación; la ventana de 2 s es una configuración inicial, no definitiva.
- La ubicación prevista entre las manos difiere de la colocación inferior usada en el experimento 1. Conservar esta distinción al interpretar resultados.

## Mapa de archivos

| Ruta | Uso |
| --- | --- |
| [README.md](README.md) | Presentación y acceso a documentación. |
| [code/README.md](code/README.md) | Organización del código y criterio para nuevos prototipos. |
| [code/prototipos/01_ble_imu/](code/prototipos/01_ble_imu/) | Firmware en `xiao/`; receptor `pc/imu_terminal.py`. |
| [code/herramientas/graficar/](code/herramientas/graficar/) | Análisis de CSV y generación de gráficas y estadísticas. |
| [doc/experimental/protocolo-experimental.md](doc/experimental/protocolo-experimental.md) | Diseño previsto y decisiones pendientes del piloto. |
| [doc/experimental/experimento_1/README.md](doc/experimental/experimento_1/README.md) | Montaje, capturas, resultados y límites de la prueba del 21/11/2026. |
| [doc/state_of_art/README.md](doc/state_of_art/README.md) | PICOS y enlaces a cribado, síntesis, entregables y matriz de evidencia. |
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

Dependencias: `numpy>=1.24,<3` y `matplotlib>=3.7,<4`. La herramienta solo busca CSV en su carpeta y actualiza las carpetas de resultados al repetir un análisis. Mantener los originales del experimento en su ubicación.

Firmware: abrir `code/prototipos/01_ble_imu/xiao/` en PlatformIO; configuración en `platformio.ini`, entorno `xiao_nrf52840_sense`. Compilar o cargar desde ese proyecto cuando la tarea lo requiera.

## Comprobaciones y límites

- **23/11/2026, revisión local:** repositorio Git en esta carpeta, rama `main`, sin cambios locales al comenzar. No existían `AGENTS.md` ni `ESTADO_PROYECTO.md` en el proyecto. Se revisaron README, protocolo, experimento 1, notas de carcasa, dependencias, configuración PlatformIO y formato BLE en firmware y receptor.
- **Resultado histórico documentado, 21/11/2026:** cuatro capturas con aproximadamente 106,4 Hz y cero saltos del contador. No recalculado en esta sesión. Las capturas denominadas reposo contienen movimiento y no son una referencia de inmovilidad continua ni clases temporales limpias.
- Las notas de carcasa indican correcciones aplicadas y encaje comprobado en Fusion; no se ha verificado el modelo ni el montaje físico en esta sesión.
- No se han compilado ni cargado firmware, probado BLE, entrenado modelos o repetido experimentos. La bibliografía y las hojas de cálculo no se han auditado en esta tarea de memoria.

## Pendientes y siguiente paso

1. Preparar un piloto reproducible: registrar versión de Git, rangos, posición exacta y orientación del dispositivo; incluir un tramo de reposo continuo y anotaciones temporales verificables.
2. Comprobar estabilidad del montaje y saturación para los gestos objetivo; verificar físicamente espacio para interruptor/cables, acceso USB y apriete de tornillos según las notas de carcasa.
3. Implementar y validar el etiquetado; concretar jugadores, cantidad de datos, métricas y tratamiento de ventanas mixtas antes de entrenar. Mantener el test de Diego separado del ajuste.

**Siguiente paso recomendado:** revisar el protocolo y preparar la captura piloto con esos metadatos. No tratar las cuatro capturas exploratorias como un conjunto ya validado para clasificar gestos.
