# Protocolo experimental

Detección de gestos de hockey línea mediante un sensor en el stick.

## Participantes y gestos

| Aspecto | Definición |
| --- | --- |
| Jugadores | n jugadores zurdos, de 15–20 años y nivel intermedio–avanzado. |
| Condiciones | En estático, sobre hormigón, con patines y guantes de hockey línea. |
| Material | Disco de hockey línea y distintos sticks con el mismo dispositivo. |
| Clases | Pase, recepción, tiro de muñeca, manejo de disco y `undefined`. |
| Ejecución | Solo por el derecho de la pala, sin revés; gestos diferenciados. |
| Test final | Diego; sus datos quedan reservados fuera del entrenamiento y ajuste. |

## Hardware y adquisición

| Elemento | Configuración |
| --- | --- |
| Placa | Seeed Studio XIAO nRF52840 Sense. |
| Señales | Acelerómetro + giróscopo integrados: seis ejes, sin magnetómetro. |
| Muestreo | **104 Hz**, frecuencia nativa del sensor. |
| Batería | LiPo de 3,7 V y 250 mAh. |
| Montaje | Carcasa de plástico con electrónica y batería, encintada al stick entre las manos. |
| Registro | Continuo; JSON por Bluetooth al PC. Todas las muestras se guardan. |
| Metadatos | Jugador, sesión, lateralidad, stick, posición y orientación del montaje. |

## Etiquetado y clasificación

| Etapa | Procedimiento |
| --- | --- |
| Etiquetado manual | Mantener la tecla del gesto mientras dura; al soltar, `undefined`. |
| Operador | Diego durante la recogida; otra persona durante su test final. |
| Vídeo | Opcional para el test final; sin revisión habitual del entrenamiento. |
| Sincronización | Cuando haya vídeo: tres toques al inicio y al final, excluidos del análisis. |
| Ventanas | Tamaños fijos elegidos tras la recogida, dividiendo o recortando gestos; pueden contener solo inicio, desarrollo o final. |
| Configuración inicial | **2 s = 208 muestras**; avance de **250 ms = 26 muestras** (87,5 % de solapamiento). |
| Entrenamiento | Edge Impulse; separación por jugador antes de generar ventanas. |
| Inferencia | Python en el PC, en tiempo real. |
| Salida | Tabla con etiqueta por muestra, sin agrupar ni contar gestos. |
| Prioridad | Reducir falsas detecciones, aceptando algunas omisiones. |

## Pendiente para implementación y piloto

| Área | Por concretar |
| --- | --- |
| Adquisición | Rangos, marcas temporales, pérdidas de datos y estabilidad del montaje. |
| Modelo | Ventana definitiva, arquitectura, umbrales y etiquetas de ventanas mixtas. |
| Salida | Cómo convertir las predicciones del modelo en etiquetas por muestra. |
| Evaluación | n de jugadores, cantidad de datos y métricas; un test solo con Diego limita la generalización. |

**Referencia:** el teclado puede introducir desfases; los toques de sincronización no los corrigen.

[Estado del arte](../state_of_art/estado-del-arte.md) · [Hardware](../hardware/Componentes.xlsx) · [Sensor y placa](https://wiki.seeedstudio.com/XIAO-BLE-Sense-IMU-Usage/)
