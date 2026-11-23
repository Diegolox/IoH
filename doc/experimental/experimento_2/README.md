# Experimento 2 · Preparación de las capturas

- **Jugador:** tercer jugador, identificado como `jugador_03`.
- **Montaje:** IMU entre las dos manos, en el lado exterior del palo.
- **Superficie:** suelo de plástico para ambas tomas. El plástico amortigua los golpes.
- **Adquisición:** prototipo `02_ble_imu` con etiquetado por teclado.

| Toma prevista | Pastilla | Nombre sugerido al abrir el programa |
| --- | --- | --- |
| 1 | Hockey sobre hielo | `jugador_03_hielo` |
| 2 | Hockey en línea | `jugador_03_linea` |

Abrir el programa para cada toma e introducir su nombre antes de conectar.
Registrar junto a cada CSV la versión del código, los rangos de la IMU y la
orientación exacta del sensor usados en la captura.

## Gráficas de los registros disponibles

La herramienta ha encontrado cuatro CSV en los registros del prototipo 02.
Los cuatro contienen tramos de `manejo` y `undefined`; los nombres de archivo
identifican dos tomas de línea y dos de hielo con distintas indicaciones de
velocidad. Esas indicaciones no son velocidades medidas.

La [comparación de manejo](graficas/comparacion_gestos.png) alinea los tramos
por el inicio de la etiqueta y usa una escala común. En [las gráficas por
captura](graficas/) se pueden revisar el movimiento completo, sus componentes
por eje y la frecuencia de llegada al PC.

El [resumen de las cuatro pruebas](graficas/resumen_pruebas.md) compara la
duración, la frecuencia y los picos. Cada prueba enlaza a su tabla completa,
con un desglose por etiqueta. La gráfica `aceleracion_xyz.png` de cada toma
separa los ejes X, Y y Z en paneles con la misma escala.

## Conclusiones del piloto

[Versión breve](conclusiones.md) · [Acelerómetro y giroscopio en una hoja](graficas/acelerometro_y_giroscopio.png)

Se analizaron cuatro grabaciones con nueve tramos etiquetados como `manejo`,
que suman aproximadamente 66,5 s. El siguiente cuadro usa la **magnitud de
la velocidad angular** en cada muestra y compara las medianas por etiqueta.

| Prueba | Giro mediano en manejo [°/s] | Giro mediano en `undefined` [°/s] |
| --- | ---: | ---: |
| 1 · Línea, normal | 174,9 | 9,4 |
| 2 · Línea, alta | 211,3 | 12,9 |
| 3 · Hielo, media | 187,7 | 4,1 |
| 4 · Hielo, alta | 282,4 | 4,9 |

- **El giroscopio es una señal útil para detectar actividad del palo.** En
  las cuatro tomas, la mediana del giro fue mayor durante el manejo. La
  magnitud de aceleración también subió: sus medianas fueron de 1,27 a
  1,73 g en manejo y de 1,01 a 1,02 g en `undefined`. La aceleración
  registrada incluye gravedad.
- **`undefined` incluye movimiento.** En la prueba 2 llegó a unos
  1.381 °/s, frente a 1.444 °/s en manejo. En la prueba 1 se ven ráfagas
  que sobrepasan el final del primer tramo marcado. Conviene revisar
  las transiciones antes de usar `undefined` como clase de entrenamiento.
- **Las tomas llamadas «alta» mostraron más intensidad dentro de cada tipo de
  pastilla.** Subieron tanto la mediana del giro en manejo como el pico de
  aceleración. El mayor pico de aceleración fue **6,93 g** en la prueba 2 y
  el mayor pico de giro, **1.493,9 °/s** en la prueba 4. Con una grabación
  por condición y sin medir la velocidad de la pastilla, estas diferencias
  no se pueden atribuir al material ni convertir en una relación con la
  velocidad real.
- **La recepción media fue similar entre tomas**, de **106,35 a 106,50 Hz**
  según el reloj del PC. Es una medida de llegada por BLE que no determina
  la frecuencia efectiva de muestreo del sensor.

El piloto muestra que podemos observar el manejo con este montaje. Queda por
comprobar si se distingue de un pase, una recepción o un tiro de muñeca:
ninguno de esos tres gestos está etiquetado en estas grabaciones. Para la
próxima toma, la prioridad es repetir los cuatro gestos en condiciones
comparables y usar un vídeo sincronizado para revisar el inicio y el final
de las etiquetas. Una comparación entre pastillas necesita repeticiones
con el mismo ritmo o velocidad medida.
