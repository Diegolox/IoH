EXPERIMENTO 1 — Primera prueba del sensor en un stick de hockey
Fecha: 21/11/2026
Prototipo: 01_ble_imu

OBJETIVO
Comprobar la sujeción y comodidad del montaje en el stick, verificar la
adquisición de medidas y explorar si la señal permite distinguir el reposo
del manejo del puck.

MONTAJE Y PROCEDIMIENTO
Se colocó el prototipo con la XIAO nRF52840 Sense en la zona inferior del
stick de hockey de Diego. Se realizaron capturas de aceleración y velocidad
angular en los tres ejes, tanto en reposo como durante el manejo de un puck
de hockey sobre hielo sobre una superficie de plástico.

Las lecturas se enviaron por BLE al ordenador y se guardaron en CSV para
su representación y análisis. Se utilizó el primer código de pruebas,
configurado a 104 Hz nominales (aproximadamente 100 muestras por segundo).
La frecuencia efectiva debe consultarse en el análisis de cada registro.

OBSERVACIONES PRELIMINARES
- El diseño mecánico pareció mantener el sensor sujeto durante la prueba.
- No se percibió una diferencia importante de peso al manejar el stick,
  pese a situar el prototipo en su parte inferior. Esta valoración es subjetiva.
- La inspección inicial de la señal sugiere diferencias entre el reposo
  y el manejo del puck sobre la superficie de plástico.
- No se observó saturación en los movimientos realizados. Esto no garantiza
  que el sensor no sature durante tiros, golpes u otras acciones más intensas.

CONCLUSIÓN
La prueba respalda continuar con este montaje para adquirir datos. La señal
obtenida parece útil para explorar la detección de actividad, pero todavía
no permite afirmar que se puedan clasificar gestos concretos con fiabilidad.

LIMITACIONES Y SIGUIENTES PASOS
La toma de datos fue exploratoria, sin un protocolo formal de etiquetado.
El ensayo sobre plástico no reproduce las condiciones de una pista de hielo.
Conviene repetir las capturas con movimientos definidos y documentar, para
cada sesión, los rangos de los sensores, su posición y orientación, la versión
del código y los archivos de datos utilizados. Las medidas originales deben
conservarse junto con sus gráficas y resultados de análisis.
