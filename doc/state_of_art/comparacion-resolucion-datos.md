# Comparación de la resolución de los datos y el número de decimales

Este documento reúne la información disponible en los siete trabajos seleccionados sobre frecuencia de muestreo, resolución digital, rango de medida y redondeo de datos. El objetivo es concretar qué significa comparar distintas resoluciones en el prototipo de hockey línea y qué respaldo ofrece la bibliografía.

Los identificadores P1 a P7 corresponden al [estado del arte](estado-del-arte.md) y a la [matriz de evidencia](matriz-de-evidencia-hockey-inercial.xlsx). La revisión ha sido elaborada por un agente de IA a partir de la extracción disponible y contrastes puntuales con los PDF locales. Los campos N/D indican información pendiente de localizar o confirmar en las fuentes revisadas.

## Qué propiedades se deben distinguir

| Propiedad | Qué expresa | Ejemplo y efecto sobre los datos |
| --- | --- | --- |
| Frecuencia de muestreo | Número de muestras registradas por segundo. Se expresa en Hz. | A 100 Hz hay una muestra cada 10 ms. A 200 Hz hay una cada 5 ms. Modifica el detalle temporal de la señal. |
| Resolución digital en bits | Número de códigos que puede representar la conversión digital. | Un canal nominal de 16 bits dispone de hasta 65.536 códigos. Su separación en unidades físicas depende del rango. |
| Rango de medida | Intervalo de aceleración o giro que puede representar el canal. | Un acelerómetro configurado a ±16 g cubre un intervalo total de 32 g. El rango condiciona tanto el paso nominal como la posibilidad de saturación. |
| Número de decimales conservados | Redondeo de los valores en una unidad determinada. | Redondear a tres decimales en g fija un paso de 0,001 g. La misma cantidad de decimales en m/s² corresponde a otro paso físico. |
| Tipo numérico de almacenamiento | Representación utilizada por el programa o archivo. | int16, float32 y float64 tienen propiedades diferentes. Los bits del tipo numérico y los bits nominales del sensor describen etapas distintas. |
| Ruido y exactitud de medida | Variabilidad y proximidad a la magnitud física real. | La resolución nominal y los decimales escritos no bastan para conocer el ruido, el sesgo o la exactitud efectiva. |

El formato de visualización de Excel puede mostrar menos decimales y conservar el valor completo en la celda. Para ensayar el efecto del redondeo, la transformación debe aplicarse a los valores que realmente recibe el algoritmo.

## Información reportada por los papers

| Publicación | Frecuencia inercial | Intervalo entre muestras | Bits y rango reportados | Decimales de entrada al modelo | Comparación de resoluciones identificada |
| --- | --- | --- | --- | --- | --- |
| P1 · Tremblay 2026 | 240 Hz. | 4,17 ms. | Bits N/D. Aceleración ±160 m/s². | N/D. | Compara conjuntos de 17 y 2 sensores. En la extracción no se identifica un ensayo de redondeo o cambio de bits. |
| P2 · Phillips 2025 | 240 Hz. | 4,17 ms. | Bits y rango N/D en la extracción. | N/D. | Compara modelos y conjuntos de sensores. El efecto aislado de decimales o bits queda sin cuantificar. |
| P3 · Shahar 2025 | 128 Hz. | 7,81 ms. | Bits y rango N/D en la extracción. | N/D. | Reduce características de 432 a 83. Esa reducción modifica las variables de entrada y mantiene una cuestión distinta del redondeo de las muestras. |
| P4 · Léger 2022 | 200 Hz para las IMU de los guantes. | 5 ms. | Bits y rango N/D en la extracción. | N/D. | Utiliza PCA y compara canales de ambas manos. La reducción de componentes se debe interpretar como transformación de características. |
| P5 · Hardegger 2015 | Texto del artículo con IMU del palo y GameTracker a 100 Hz. | 10 ms. | Bits y rango N/D en la extracción. | N/D. | Los módulos utilizan distintas tecnologías y señales. El texto registra flexión del palo a 400 Hz. Esa frecuencia corresponde a otra magnitud medida. |
| P6 · Shahar 2020 | 200 Hz. | 5 ms. | Bits y rango N/D en la extracción. | N/D. | Compara ubicaciones y combinaciones de sensores a una frecuencia declarada. No se identifica una comparación de decimales en la extracción. |
| P7 · Vleugels 2021 | Adquisición a 400 Hz y reducción a 100 Hz para el modelo descrito. | 2,5 ms en adquisición y 10 ms tras reducción. | AX6 con resolución nominal de 16 bits. Aceleración ±16 g y giro ±2000 grados/s. | N/D. | Documenta reducción de frecuencia y señala buenos resultados a 100 Hz. La extracción no aporta una tabla de rendimiento por número de decimales o por bits. |

Los intervalos se calculan como 1000/frecuencia en Hz y se redondean para su presentación. Los localizadores contrastados son P1, PDF p. 4; P2, PDF p. 39; P3, PDF p. 6; P4, PDF p. 4; P5, PDF pp. 3 y 5; P6, sección 3.1; P7, PDF pp. 5–6. En P5, el texto y el esquema de hardware presentan frecuencias que requieren cotejo para atribuirlas a cada señal. La tabla conserva las frecuencias del texto para los canales inerciales.

La extracción inicial de NotebookLM dejó el rango de P7 como N/D. El contraste del agente con la sección 3.2.2, PDF p. 6, permite localizar ±16 g para aceleración y ±2000 grados/s para giro. Esta precisión se incorpora aquí con su fuente.

## Qué muestran los resultados sobre la frecuencia

| Trabajo y frecuencia utilizada por el modelo | Resultado de referencia | Alcance de la conclusión |
| --- | --- | --- |
| P1 · 240 Hz, dos manos | F1 global ponderado 93,5 ± 1,6 %. | Clasificación de segmentos recortados con separación por jugador. |
| P2 · 240 Hz, manos y esternón | F1 global ponderado 83,7 % con híbrido. | Otro conjunto de acciones y datos. Las diferencias con P1 no aíslan el efecto de la frecuencia. |
| P3 · 128 Hz, cuatro IMU | Exactitud 92,82 % para K-NN/RNCA y 94,13 % para MLP/RNCA. | Clasificación de ventanas de hockey hierba. Modelo, características y validación también condicionan el resultado. |
| P4 · 200 Hz, guantes | Exactitud 94,5–96,1 % en los modelos destacados de ajuste de palo para tiro de muñeca. | La salida es la respuesta a parámetros del palo a partir de tiros identificados. |
| P5 · 100 Hz, GameTracker | F1 global de eventos 0,70. | Detección de eventos en rondas continuas. |
| P6 · 200 Hz, cuatro IMU | Exactitud global 96,7 %. | Seis clases de hockey hierba y validación por ventanas. |
| P7 · 100 Hz, IMU en palo | Exactitud 76 % con jugador no visto. | Seis clases y un protocolo diferente a los otros trabajos. La señal original se adquirió a 400 Hz. |

Los resultados muestran funcionamiento con las frecuencias empleadas. La heterogeneidad de ubicaciones, clases, modelos y protocolos impide deducir una relación causal entre frecuencia y rendimiento a partir de esta tabla. La frecuencia mínima que conserva los cuatro gestos del proyecto requiere una comparación sobre el mismo conjunto de datos.

En P7, 400 Hz corresponde a adquisición y 100 Hz a la señal reducida utilizada en el modelo. El artículo indica que la reducción busca disminuir complejidad, memoria y consumo. Su resultado a 100 Hz aporta una referencia para diseñar el experimento. Una frecuencia óptima para hockey línea necesita validación propia. [P7](#referencias).

## Relación entre bits, rango y paso de cuantificación

Como aproximación ideal, para un canal bipolar uniforme con rango de −R a +R y B bits, el paso nominal es Δ ≈ 2R / 2^B. La codificación concreta, el ruido y la electrónica pueden modificar la resolución efectiva. El cálculo siguiente utiliza los valores nominales descritos para AX6 en P7.

| Canal de P7 | Rango total | Resolución nominal | Paso ideal calculado |
| --- | ---: | ---: | ---: |
| Acelerómetro a ±16 g | 32 g | 16 bits | 32/65.536 ≈ 0,000488 g. |
| Giróscopo a ±2000 grados/s | 4000 grados/s | 16 bits | 4000/65.536 ≈ 0,0610 grados/s. |

Estos pasos son cálculos del agente bajo un modelo ideal de cuantificación uniforme. El número de bits procede de la descripción del dispositivo y los rangos de la sección de adquisición. La comprobación de la codificación y la resolución efectiva requiere revisar el formato del dispositivo y sus registros. [P7](#referencias).

Guardar más decimales que los asociados al paso nominal puede conservar resultados de conversiones, calibraciones o filtros. Eso no aumenta por sí mismo la información física registrada por el sensor. El análisis del redondeo debe considerar en qué etapa se aplica y si la señal ya ha sido procesada.

## Qué significa variar el número de decimales

La extracción de los siete trabajos deja sin determinar una cantidad óptima de decimales para reconocer estos gestos. Los decimales de sus porcentajes publicados describen la presentación de resultados. Para estudiar el prototipo hay que modificar la señal de entrada y medir de nuevo sus resultados.

La tabla siguiente ilustra un redondeo uniforme de aceleración expresada en g. Se utiliza el rango ±16 g como referencia para calcular la relación con el paso nominal ideal de P7.

| Decimales conservados en g | Paso impuesto por el redondeo | Diferencia respecto al paso ideal de 0,000488 g |
| ---: | ---: | --- |
| 0 | 1 g | Redondeo unas 2048 veces más grueso. |
| 1 | 0,1 g | Redondeo unas 205 veces más grueso. |
| 2 | 0,01 g | Redondeo unas 20,5 veces más grueso. |
| 3 | 0,001 g | Redondeo unas 2,05 veces más grueso. |
| 4 | 0,0001 g | Paso de redondeo más fino que el paso nominal ideal. |

La comparación es teórica. Su efecto sobre la clasificación depende de la amplitud y duración de los gestos, el ruido, la unidad, el procesamiento y el algoritmo. El caso de cuatro decimales tampoco implica una exactitud física de 0,0001 g.

Las unidades son determinantes. Redondear a tres decimales en g produce un paso de 0,001 g, aproximadamente 0,00981 m/s². Redondear a tres decimales en m/s² produce un paso de 0,001 m/s², aproximadamente 0,000102 g. Ambos archivos muestran tres decimales y conservan distinto detalle físico. Se emplea la conversión convencional 1 g = 9,80665 m/s².

El giróscopo utiliza otra unidad y otro rango. Aplicarle automáticamente la cantidad de decimales elegida para aceleración no proporciona una reducción equivalente. Para comparar los canales con sentido físico conviene registrar el paso de cuantificación en g o m/s² para aceleración y en grados/s para giro.

## Propuesta de comparación para el proyecto

La propuesta metodológica del agente es conservar el registro original y generar variantes controladas, separando el cambio de frecuencia del cambio de paso de cuantificación. El archivo original permitirá repetir las transformaciones sin nuevas adquisiciones.

| Comparación | Variables que se modifican | Condiciones que deben documentarse |
| --- | --- | --- |
| Frecuencia temporal | Muestras por segundo. | Frecuencia original, frecuencias derivadas, filtrado previo a reducción y marcas temporales. |
| Redondeo de amplitud | Paso físico de cuantificación o decimales con unidad fija. | Unidad, regla de redondeo, canales afectados y etapa de aplicación. |
| Bits y rango de hardware | Configuración real de adquisición, cuando el dispositivo lo permita. | Rango, bits nominales, saturación y método de conversión a unidades físicas. |

Al reducir frecuencia se debe controlar el aliasing mediante filtrado adecuado. Para mantener comparable la tarea, las ventanas se deben definir en segundos y después convertir a número de muestras. Una ventana de un segundo contiene 100 muestras a 100 Hz y 200 a 200 Hz. Conservar el mismo número de muestras entre frecuencias cambiaría también la duración de información observada.

Cada variante debería evaluarse con las mismas particiones por jugador o sesión y el mismo vídeo de referencia. Entrenar y evaluar cada modelo con la variante correspondiente permite estudiar el rendimiento alcanzable con esa resolución. Redondear únicamente durante la prueba mide adicionalmente un cambio entre las condiciones de entrenamiento y uso. Ambos experimentos deben tener una definición explícita.

La preferencia del proyecto por pocas falsas detecciones requiere recoger precisión y sensibilidad por gesto, falsas detecciones por minuto y latencia. El número aceptable de decimales será el que conserve el comportamiento requerido con el menor coste útil para el sistema. Ese límite todavía necesita una decisión cuantitativa sobre omisiones y falsas detecciones.

## Conclusiones

1. **La bibliografía aporta frecuencias de referencia entre 100 y 240 Hz para los modelos examinados.** P7 distingue adquisición a 400 Hz y procesamiento a 100 Hz.
2. **La información sobre bits y rangos es incompleta en la extracción.** P7 permite localizar 16 bits, ±16 g y ±2000 grados/s. P1 informa ±160 m/s² para aceleración.
3. **El corpus no establece un número óptimo de decimales de entrada.** Esa variable debe estudiarse con el registro propio y unidades explícitas.
4. **Reducir características, frecuencia, bits o decimales plantea cambios diferentes.** Cada transformación necesita un protocolo que permita atribuir su efecto.
5. **La comparación más interpretable para el prototipo conserva los originales y modifica una variable cada vez.** La selección final debe atender a la detección por eventos y al control de falsas detecciones.

## Referencias

- **P1.** Tremblay et al. (2026). *A Deep Learning Approach to Automatically Classify Ice Hockey Shooting Actions Using Acceleration Signals*. Frecuencia y rango en PDF p. 4. [PDF](papers/utiles/A%20Deep%20Learning%20Approach%20to%20Automatically%20Classify%20Ice%20Hockey%20Shooting%20Actions%20Using%20Acceleration%20Signals.pdf).
- **P2.** Phillips (2025). *Assessing Deep Learning Techniques for Ice Hockey Human Activity Recognition from Game Simulated Inertial Measurement Unit Data: A Comparative Analysis of CNN, Transformer, and Hybrid Models*. Adquisición en PDF p. 39 y resultados en p. 62. [PDF](papers/utiles/Assessing%20Deep%20Learning%20Techniques%20for%20Ice%20Hockey%20Human%20Activity%20Recognition%20from.pdf).
- **P3.** Shahar et al. (2025). *Inertial Sensor-Based Recognition of Field Hockey Activities Using a Hybrid Feature Selection Framework*. Frecuencia en PDF p. 6 y resultados en pp. 17–18. [PDF](papers/utiles/Inertial%20Sensor-Based%20Recognition%20of%20Field%20Hockey%20Activities%20Using%20a%20Hybrid%20Feature%20Selection%20Framework.pdf).
- **P4.** Léger et al. (2022). *Pilot Study of Embedded IMU Sensors and Machine Learning Algorithms for Automated Ice Hockey Stick Fitting*. Frecuencia de las IMU y registro de 199 muestras en PDF p. 4. [PDF](papers/utiles/Pilot%20Study%20of%20Embedded%20IMU%20Sensors%20and%20Machine%20Learning%20Algorithms%20for%20Automated%20Ice%20Hockey%20Stick%20Fitting.pdf).
- **P5.** Hardegger et al. (2015). *Sensor Technology for Ice Hockey and Skating*. Frecuencias del texto en PDF pp. 3 y 5. [PDF](papers/utiles/Sensor%20Technology%20for%20Ice%20Hockey%20and%20Skating.pdf).
- **P6.** Shahar et al. (2020). *Wearable Inertial Sensor for Human Activity Recognition in Field Hockey: Influence of Sensor Combination and Sensor Location*. Adquisición en sección 3.1. [PDF](papers/utiles/Shahar%202020%20-%20Wearable%20Inertial%20Sensor%20for%20Human%20Activity%20Recognition%20in%20Field%20Hockey.pdf).
- **P7.** Vleugels et al. (2021). *Ultra-Wideband Indoor Positioning and IMU-Based Activity Recognition for Ice Hockey Analytics*. Resolución en PDF p. 5. Rangos, adquisición y reducción de frecuencia en p. 6. [PDF](papers/utiles/Ultra-Wideband%20Indoor%20Positioning%20and%20IMU-Based%20Activity%20Recognition%20for%20Ice%20Hockey%20Analytics.pdf).

[Volver al estado del arte](estado-del-arte.md) · [Comparación de ubicaciones](comparacion-ubicacion-sensores.md)
