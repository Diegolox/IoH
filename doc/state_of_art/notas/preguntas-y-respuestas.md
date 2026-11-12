# Preguntas y respuestas del marco PICOS

Estas notas recogen las preguntas iniciales sobre el prototipo y la validación. El alcance de la revisión bibliográfica y sus criterios de selección se concretan en el [primer entregable](../README.md).

## P — Población

**Pregunta**

¿Qué criterios de modalidad (hockey en línea o sobre hielo), edad y nivel de juego usarás para decidir si los participantes de un estudio pertenecen a tu población de interés?

**Respuesta**

Jugadores de hockey en línea de 15 a 20 años, con experiencia previa y conocimientos de nivel intermedio a avanzado. El contexto de entrenamiento es una pista con suelo de hormigón.

## I — Tecnología de detección

**Pregunta**

¿Qué señales podrá usar un sistema para que lo incluyas en la revisión: solo la del acelerómetro o también la del acelerómetro combinada con otros sensores?

**Respuesta**

El sistema de detección utiliza señales del acelerómetro, el giróscopo y el magnetómetro.

## C — Comparador

**Pregunta**

¿Con qué método o configuración quieres comparar el rendimiento del sistema que combina las tres señales?

**Respuesta**

Se comparará el rendimiento de las configuraciones de detección según tres factores:

- **Ubicación del sensor.** En el palo o en la muñeca.
- **Resolución de los datos.** Se compararán distintas resoluciones. El tipo de resolución y sus valores quedan por definir.
- **Combinación de sensores.** Se comparará la configuración completa con variantes que excluyan un sensor cada vez: magnetómetro, acelerómetro o giróscopo.

## O — Resultados

**Pregunta**

¿Qué movimientos concretos del entrenamiento debe distinguir el sistema como clases separadas?

**Respuesta**

El sistema debe distinguir, como mínimo, cuatro gestos ejecutados en estático: pase, recepción de pase, tiro de muñeca y regate.

La categoría `undefined` agrupa los tramos en los que no se ejecuta ninguno de los cuatro gestos objetivo.

**Pregunta de seguimiento**

¿El sistema recibirá un tramo ya recortado por cada gesto o tendrá que encontrar los gestos en una grabación continua del entrenamiento?

**Respuesta**

El sistema clasificará los movimientos a partir de una grabación continua. Emitirá una clasificación por ventana y avanzará la ventana en pasos de n milisegundos. La duración de la ventana y el valor de n quedan por definir.

**Referencia para la evaluación**

La grabación de los sensores se acompañará de un vídeo del entrenamiento, que servirá de referencia para comprobar los gestos detectados.

**Pregunta sobre la métrica de evaluación**

¿Qué métrica principal usarás para comparar las configuraciones a partir de los gestos detectados en la grabación continua?

**Respuesta**

Se prioriza evitar las falsas detecciones, aunque eso implique omitir gestos reales. La métrica principal queda por definir.

**Pregunta de seguimiento**

En una grabación de 10 minutos, ¿cuántas detecciones falsas aceptarías como máximo?

**Respuesta**

Se busca mantener bajas las falsas detecciones y limitar las omisiones de gestos reales. El máximo aceptable de falsas detecciones y el límite de omisiones quedan por definir.

## S — Diseño de los estudios

**Pregunta**

¿Exigirás que los estudios prueben el detector con datos recogidos de jugadores reales para incluirlos en el estado de la cuestión?

**Respuesta**

Para incluir un estudio en el estado de la cuestión, el detector debe haberse probado con datos recogidos de jugadores reales.
