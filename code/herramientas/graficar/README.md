# Graficar registros IMU

Desde esta carpeta:

```powershell
python -m pip install -r requirements.txt
python graficar.py
```

El menú busca CSV junto a `graficar.py`. Elige un número, T para todos o Enter
para el último archivo. También puedes indicar rutas de otros directorios y
separar las figuras de los originales con `--salida`.

```powershell
python graficar.py captura.csv --sin-ventana
python graficar.py --todos --sin-ventana --solo-frecuencia
```

Cada CSV conserva su nombre de captura como nombre de la subcarpeta de salida.

| Figura | Qué permite revisar |
| --- | --- |
| `movimiento.png` | Magnitudes de aceleración y de velocidad angular, con los tramos de gesto sombreados. Sirve para localizar picos y secuencias de movimiento. |
| `ejes.png` | Componentes con signo en los ejes X/Y/Z del sensor. Sirve para ver qué ejes dominan y cuándo cambia el sentido. |
| `aceleracion_xyz.png` | Un panel por eje de aceleración, con el mismo tiempo y escala en g. |
| `comparacion_gestos.png` | Superpone tramos de la misma etiqueta desde su inicio, conservando la duración en segundos. Separa las capturas en filas con escalas comunes. |
| `frecuencia_recepcion.png` | Llegadas al PC por segundo y frecuencia media. Omite la última fracción de segundo del trazado por ventanas. |

Los CSV del prototipo 01 se pueden graficar sin etiquetas. Los del 02 conservan
las etiquetas del teclado y los tramos `undefined` aparecen sin sombreado.
La referencia temporal del movimiento es el reloj de la XIAO. El inicio de la
etiqueta puede estar desplazado respecto al inicio físico del gesto.

La aceleración incluye gravedad y la velocidad angular mide giro. La herramienta
no estima la velocidad lineal del palo ni la de la pastilla. La frecuencia de
recepción utiliza el reloj del PC y no equivale al muestreo de la IMU. Si ese reloj
retrocede, la gráfica indica que no se puede estimar una frecuencia fiable.

Cada prueba tiene un `resumen.md` con duración, frecuencia media y estadísticas
de los seis ejes y las dos magnitudes. Incluye mínimo, máximo, media, desviación
estándar, RMS, percentil 95 del valor absoluto e instante del pico. Con etiquetas,
el resumen separa además las señales por clase y muestra la duración de cada una.
Si analizas varias pruebas, `resumen_pruebas.md` compara sus picos y enlaza cada detalle.

Los resultados se actualizan al repetir el análisis. Los CSV de entrada se
conservan intactos. La opción antigua `--guardar` sigue aceptada.
