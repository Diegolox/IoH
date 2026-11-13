# Detección de gestos técnicos en hockey mediante sensores inerciales

**LAB Sensores · Estado de la cuestión · Entregable 1**

## Pregunta de investigación

¿Qué configuraciones con acelerómetro se han evaluado para detectar pases, recepciones de pase, tiros de muñeca o regates en hockey en línea y sobre hielo, y qué proporción de aciertos y falsas detecciones reportan al contrastar sus resultados con una referencia?

## Marco PICOS

| Componente | Alcance e inclusión | Exclusión |
| --- | --- | --- |
| **P · Población** | Jugadores de hockey en línea o sobre hielo. | Estudios de otros deportes o sin resultados identificables para jugadores de hockey. |
| **I · Tecnología** | Detección de al menos uno de los gestos objetivo con un acelerómetro, solo o combinado con otras señales. | Sistemas sin acelerometría o que solo miden carga física o desplazamiento. |
| **C · Comparador** | Se admiten estudios con una sola configuración si contrastan las detecciones con una referencia, como vídeo o anotaciones manuales. Si comparan configuraciones, se registran las diferencias de ubicación, resolución de los datos y combinación de sensores que reporten. | Estudios sin una referencia que permita comprobar las detecciones. |
| **O · Resultados** | En varias secuencias de prueba etiquetadas, el estudio detecta correctamente más de la mitad de las ejecuciones del gesto objetivo evaluado y permite cuantificar las falsas detecciones. | Estudios sin resultados cuantitativos suficientes, con una única secuencia de prueba o que no detectan correctamente más de la mitad de las ejecuciones del gesto evaluado. |
| **S · Diseño de los estudios** | Estudios experimentales con datos de jugadores reales en condiciones controladas o de juego. | Estudios basados exclusivamente en simulación. |

El criterio de acierto se comprueba por gesto mediante la sensibilidad, calculada como las ejecuciones correctamente detectadas divididas entre las ejecuciones anotadas en las secuencias de prueba. Se recoge también el número o la tasa de falsas detecciones. El máximo aceptable de falsas detecciones para el prototipo queda por definir.

## Diez términos de búsqueda en inglés

`inline hockey`, `roller hockey`, `ice hockey`, `inertial measurement unit`, `accelerometer`, `sports action recognition`, `passing`, `pass reception`, `wrist shot`, `stickhandling`.

## Justificación

Un registro automático permitiría al entrenador analizar el rendimiento del equipo después del partido y detectar patrones por jugador, como recibir el disco muchas veces y realizar pocos pases, sin anotar las acciones a mano. La revisión orientará la elección de sensores y su ubicación para una primera prueba de gestos en estático con jugadores de hockey en línea de 15 a 20 años, de nivel intermedio a avanzado, en una pista de hormigón.

[Preguntas y respuestas del proyecto](notas/preguntas-y-respuestas.md) · [Guía metodológica del profesor](../doc_prof/metodologia_EdC.docx)

## Entregable 2

[Cribado de papers](cribado-de-papers.md) · [Hoja de cribado](cribado-entregable-2.csv)
