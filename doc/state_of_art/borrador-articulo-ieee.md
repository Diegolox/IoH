# Reconocimiento de gestos técnicos en hockey mediante sensores inerciales

**Borrador del entregable 5 · LAB Sensores · Proyecto IoH**

## Resumen

El reconocimiento automático de gestos mediante sensores inerciales permitiría cuantificar acciones técnicas durante el entrenamiento de hockey. Esta revisión examina las configuraciones con acelerómetro que se han evaluado para reconocer el pase, la recepción, el tiro de muñeca y el regate. A partir de búsquedas en IEEE Xplore y PubMed, junto con referencias complementarias, se analizaron provisionalmente siete publicaciones. Cuatro aportaron evidencia directa según el cribado inicial y tres se retuvieron por su utilidad metodológica. En hielo, los sistemas con sensores en ambas manos o en el palo mostraron resultados favorables en sus respectivos protocolos. En un estudio con una IMU en el palo, la exactitud con jugadores no vistos fue del 76 % frente al 99 % obtenido cuando entrenamiento y prueba compartían jugadores. Los estudios de hockey hierba aportaron métodos para estudiar la recepción, cuya transferencia al hockey en línea queda por evaluar. La evidencia orienta un piloto con una IMU en el palo y evaluación por eventos en grabaciones continuas. La sensibilidad, la precisión por gesto y las falsas detecciones por minuto permitirían cuantificar su rendimiento.

**Palabras clave** — acelerometría, hockey, reconocimiento de gestos, sensores inerciales, validación por jugador.

## I. Introducción

Un registro de pases, recepciones, tiros y regates puede ayudar a describir cómo se distribuyen las acciones técnicas durante un entrenamiento. Una unidad de medida inercial (IMU) instalada en el equipo deportivo ofrece una forma de registrar los movimientos asociados a esas acciones. La posición del sensor determina qué parte del movimiento se observa y qué señales están disponibles para distinguir un gesto de los movimientos que lo preceden o lo siguen.

Para el proyecto IoH interesa detectar acciones en una grabación continua de hockey en línea. El piloto previsto se centra en ejecuciones en estático sobre hormigón. En ese escenario, el sistema debe decidir cuándo ha ocurrido una acción, asignarle una clase y evitar alertas durante el resto del registro. La revisión plantea la siguiente pregunta: ¿qué configuraciones con acelerómetro se han evaluado para detectar pases, recepciones, tiros de muñeca o regates en hockey en línea o sobre hielo y qué aciertos y falsas detecciones reportan frente a una referencia etiquetada?

## II. Metodología

### A. Búsqueda y selección

El marco PICOS delimitó la evidencia directa a experimentos con jugadores reales de hockey en línea o sobre hielo, acelerometría sola o combinada con otros sensores, y una referencia de gestos anotados, como vídeo o etiquetado manual. El cribado inicial requirió que el sistema reconociera más de la mitad de las ejecuciones de al menos un gesto objetivo en varias secuencias etiquetadas y que el trabajo permitiera cuantificar falsas detecciones. En una ampliación posterior se retuvieron por separado dos publicaciones de hockey hierba y un estudio de ajuste del palo por su utilidad para el diseño experimental.

Se emplearon IEEE Xplore y PubMed, con referencias complementarias procedentes de Consensus y Elicit. Las consultas combinaron términos de hockey, acelerometría o IMU y, en las versiones refinadas, términos de gestos como *passing*, *wrist shot* y *stickhandling*. En IEEE Xplore, los resultados registrados el 13 de noviembre de 2026 fueron 24 y 12 para las dos consultas. En PubMed, la consulta amplia registró 36 resultados y la refinada cinco, ambas con un filtro de texto completo. Las cadenas completas y los avisos de PubMed constan en el registro de búsqueda. Los resultados de distintas consultas pueden solaparse. [Registro de búsqueda y cadenas](cribado-de-papers-ia.md).

El corpus organizado contiene 37 publicaciones y 36 PDF locales. El cribado inicial asistido por IA retuvo cuatro publicaciones y la revisión posterior añadió tres por su interés parcial o metodológico. La selección de siete publicaciones es provisional. El total de publicaciones tampoco determina cuántas cohortes independientes están representadas. [Registro de decisiones](cribado-de-papers.md).

> **Figura 1. Diagrama PRISMA pendiente.** Cotejar los 21 registros pendientes de la primera consulta de IEEE Xplore, confirmar el recuento de la consulta corregida de PubMed y revisar las decisiones de cribado pendientes. Conciliar duplicados, exclusiones por resumen, textos completos evaluados o sin recuperar y motivos de exclusión. Mantener visibles las inclusiones metodológicas posteriores.

### B. Extracción, evaluación de calidad y síntesis

Para cada publicación se registraron montaje, frecuencia de muestreo, gestos, unidad de evaluación, modelo y métricas. La evaluación de calidad aplicó ocho criterios: uso de datos reales, suficiencia de la muestra, métricas, comparador, reproducibilidad, declaración de limitaciones, generalización y declaración de financiación o conflictos. Cada criterio recibió 1, 0,5 o 0 puntos según la valoración. La matriz de evidencia recoge las justificaciones y las páginas de respaldo. Dadas las diferencias entre montajes, modalidades y unidades de evaluación, se realizó una síntesis narrativa. [Matriz de evidencia y evaluación de calidad](matriz-de-evidencia-hockey-inercial.xlsx).

## III. Resultados

**Tabla I. Comparación de las siete publicaciones retenidas.** Se indica la unidad de evaluación junto a cada resultado. La calidad corresponde a la rúbrica del entregable 4.

| Publicación | Montaje y contexto | Unidad de evaluación y resultado | Calidad / 8 |
| --- | --- | --- | ---: |
| Tremblay et al. [1] | Dos sensores en las manos, 240 Hz, hockey sobre hielo. 39 jugadores analizados. | Segmentos recortados y prueba por jugador. F1 ponderado 93,5 %. Sensibilidad del pase 88,5 % y del tiro de muñeca 97,2 %. | 6,5 |
| Phillips [2] | Tres IMU en manos y esternón, 240 Hz, hielo en condiciones de juego simulado. 48 registros de participantes analizados. | Eventos recortados y prueba por jugador. F1 ponderado 83,7 %. Pase con precisión 77,3 % y sensibilidad 93,5 %. | 6,5 |
| Hardegger et al. [3] | GameTracker con tres IMU corporales, 100 Hz, cuatro jugadores y diez rondas sobre hielo. | Eventos en continuo. F1 global 0,70, precisión 0,73 y sensibilidad aproximada 0,67. | 4,0 |
| Vleugels et al. [4] | Una IMU en el palo, 100 Hz, cinco jugadores de hockey sobre hielo. | Exactitud del 76 % en seis clases con jugadores no vistos. En una prueba continua diferenciada, 23 de 24 tiros correctos y un regate clasificado como tiro. | 5,0 |
| Shahar et al. [5] | Cuatro IMU corporales, 128 Hz, 43 participantes de hockey hierba. Apoyo metodológico. | Ventanas de seis clases, incluida la recepción. El MLP con selección RNCA obtuvo un macro F1 de 89,09 %. | 5,5 |
| Shahar et al. [6] | IMU corporales, 200 Hz, 11 jugadores de hockey hierba. Apoyo metodológico. | Ventanas de seis clases. Exactitud global 96,7 % con cuatro sensores y 86,2 % con el sensor de muñeca izquierda. | 5,0 |
| Léger et al. [7] | Dos IMU en guantes, 200 Hz, diez jugadores en laboratorio. Estudio de ajuste del palo. | Tiros de muñeca previamente identificados. Exactitud del 94,5 al 96,1 % en la clasificación de parámetros de ajuste del palo, según la salida y el canal. | 5,5 |

### A. Montaje y gestos cubiertos

Las configuraciones abarcan sensores corporales y sensores en el palo, con frecuencias entre 100 y 240 Hz en los montajes inerciales comparados. En hielo, dos sensores en las manos permitieron clasificar pases y tiros de muñeca en segmentos delimitados, mientras que un sensor en el palo se utilizó para clasificar tiros y regates [1], [4]. En hockey hierba, los trabajos de Shahar et al. distinguieron la recepción como clase propia [5], [6]. En Phillips, la clase de control del disco tiene una definición más amplia [2]. La recepción como evento independiente en hockey en línea sigue siendo una pregunta abierta en el corpus analizado.

### B. Validación y detección en continuo

La preparación de las entradas modifica la tarea que resuelve el clasificador. Tremblay et al. y Phillips evaluaron segmentos delimitados y presentan resultados por gesto [1], [2]. Hardegger et al. evaluaron eventos en rondas continuas y Vleugels et al. incluyeron una demostración de detección de tiros en grabaciones continuas [3], [4]. En este último trabajo, la exactitud de seis clases pasó del 99 % cuando los mismos jugadores aportaban datos a entrenamiento y prueba al 76 % cuando se evaluaban jugadores no vistos. Las dos cifras describen protocolos de evaluación distintos [4].

## IV. Discusión

La evidencia apoya probar una instrumentación reducida, aunque la elección entre palo y muñeca sigue abierta. El sensor en el palo aporta una referencia directa para IoH porque registra el movimiento del implemento y ya se ha evaluado sobre hielo [4]. La muñeca ofrece un montaje corporal de referencia [6]. Las diferencias de modalidades, gestos y protocolos impiden atribuir las cifras publicadas a la posición del sensor por sí sola. Una comparación en el piloto tendría que mantener los mismos jugadores, gestos, superficie y criterios de evaluación en ambas configuraciones.

La calidad de cada resultado depende también de los datos que entraron en la evaluación. Hardegger et al. obtuvieron la menor puntuación de la rúbrica. GameTracker se probó con cuatro jugadores y las pérdidas de datos durante algunos impactos obligaron a seleccionar un subconjunto de tiros para analizar el sistema del palo [3]. Vleugels et al. aportan una prueba con jugadores no vistos, con una cohorte de cinco [4]. En Shahar et al. (2020), el criterio de generalización queda limitado por la falta de una separación por jugador documentada en la evaluación por ventanas [6]. Estos tres trabajos cumplen plenamente tres criterios de la guía y conservan utilidad para orientar montajes o protocolos concretos.

Para IoH, la prioridad sería evaluar eventos en grabaciones continuas con periodos sin gestos objetivo. Se propone separar jugadores antes de generar ventanas y emparejar cada detección con una única anotación dentro de una tolerancia temporal definida antes del test. La sensibilidad cuantificaría los gestos anotados que el sistema recupera. La precisión describiría qué fracción de las detecciones corresponde a un gesto real de esa clase. Las falsas detecciones por minuto permitirían valorar el coste de los errores a lo largo de la sesión.

La interpretación está condicionada por la cobertura pendiente del cribado, el filtro de texto completo en PubMed y el uso de evidencia indirecta de hockey hierba. La transferencia al hockey en línea sobre hormigón requiere medir el rendimiento con el disco, la superficie y los jugadores del piloto. Las puntuaciones de calidad orientan la lectura de cada trabajo, junto con las diferencias de muestra, montaje y diseño de prueba.

## V. Conclusiones

La literatura revisada muestra que se pueden reconocer pases, tiros de muñeca y regates con montajes inerciales reducidos en los protocolos estudiados. La recepción cuenta con apoyo metodológico de hockey hierba y necesita una evaluación específica en hockey en línea. Las cifras más informativas para IoH proceden de pruebas con participantes separados y de ensayos en continuo, aunque estas últimas siguen siendo limitadas en el corpus.

Una IMU en el palo es un punto de partida razonable para el piloto. La evaluación debería medir si el sistema identifica los cuatro gestos durante una sesión completa, con jugadores reservados para prueba y un registro de sensibilidad, precisión y falsas detecciones por minuto.

## Referencias

[1] S. Tremblay, P. J. Renaud, S. M. Robbins, D. J. Pearsall y P. C. Dixon, “A Deep Learning Approach to Automatically Classify Ice Hockey Shooting Actions Using Acceleration Signals,” *Sensors*, vol. 26, art. 3361, 2026, doi: [10.3390/s26113361](https://doi.org/10.3390/s26113361).

[2] A. Phillips, “Assessing Deep Learning Techniques for Ice Hockey Human Activity Recognition from Game Simulated Inertial Measurement Unit Data: A Comparative Analysis of CNN, Transformer, and Hybrid Models,” tesis de máster, McGill University, Montréal, Canadá, 2025. [PDF](papers/utiles/Assessing%20Deep%20Learning%20Techniques%20for%20Ice%20Hockey%20Human%20Activity%20Recognition%20from.pdf).

[3] M. Hardegger *et al.*, “Sensor Technology for Ice Hockey and Skating,” en *IEEE 12th Int. Conf. Wearable and Implantable Body Sensor Networks (BSN)*, 2015, doi: [10.1109/BSN.2015.7299368](https://doi.org/10.1109/BSN.2015.7299368).

[4] R. Vleugels, B. Van Herbruggen, J. Fontaine y E. De Poorter, “Ultra-Wideband Indoor Positioning and IMU-Based Activity Recognition for Ice Hockey Analytics,” *Sensors*, vol. 21, art. 4650, 2021, doi: [10.3390/s21144650](https://doi.org/10.3390/s21144650).

[5] N. Shahar *et al.*, “Inertial Sensor-Based Recognition of Field Hockey Activities Using a Hybrid Feature Selection Framework,” *Sensors*, vol. 25, art. 7615, 2025, doi: [10.3390/s25247615](https://doi.org/10.3390/s25247615).

[6] N. Shahar *et al.*, “Wearable Inertial Sensor for Human Activity Recognition in Field Hockey: Influence of Sensor Combination and Sensor Location,” *J. Phys. Conf. Ser.*, vol. 1529, art. 022015, 2020, doi: [10.1088/1742-6596/1529/2/022015](https://doi.org/10.1088/1742-6596/1529/2/022015).

[7] T. Léger, P. J. Renaud, S. M. Robbins y D. J. Pearsall, “Pilot Study of Embedded IMU Sensors and Machine Learning Algorithms for Automated Ice Hockey Stick Fitting,” *Sensors*, vol. 22, art. 3419, 2022, doi: [10.3390/s22093419](https://doi.org/10.3390/s22093419).

## Nota para la revisión del borrador

- Conciliar el cribado antes de cerrar el diagrama PRISMA. Si se incorporan nuevos artículos que cumplan los criterios, actualizar la extracción, la evaluación de calidad, la tabla y el resumen. La guía pide un mínimo de diez publicaciones en la tabla comparativa.
- Revisar las afirmaciones, cifras y referencias contra los PDF antes de pasar el texto a la plantilla IEEE de 4–6 páginas. Además de la tabla y el diagrama, se puede usar la [figura de cobertura de gestos](figuras/cobertura-gestos.png) si se actualiza junto con la selección final.
- Completar la declaración de uso de IA en los agradecimientos de la versión final. En esta fase se usó IA para asistir al cribado, extraer datos con NotebookLM y preparar el borrador con Codex. La revisión y reescritura por el autor siguen pendientes.
