# Cribado preliminar de artículos

> **Opinión de un agente de IA.** Las decisiones son provisionales y quedan pendientes de revisión por Diego.

Se revisaron los cinco PDF de la carpeta `papers` según el [PICOS del primer entregable](README.md). La propuesta es conservar tres para revisión detallada y descartar dos de la síntesis principal.

| Artículo | Decisión propuesta | Motivo |
| --- | --- | --- |
| [Sensor Technology for Ice Hockey and Skating](papers/utiles/Sensor%20Technology%20for%20Ice%20Hockey%20and%20Skating.pdf) | **Conservar para revisión** | El apartado *Gameplay Tracker* reconoce tiros de muñeca en un circuito con jugadores y vídeo de referencia. La figura 6 muestra los errores de clasificación. |
| [Ultra-Wideband Indoor Positioning and IMU-Based Activity Recognition for Ice Hockey Analytics](papers/utiles/Ultra-Wideband%20Indoor%20Positioning%20and%20IMU-Based%20Activity%20Recognition%20for%20Ice%20Hockey%20Analytics.pdf) | **Conservar para revisión** | Usa una IMU en el palo y evalúa tiros en secuencias continuas. Conviene comprobar si los resultados separan los errores del tiro de muñeca de los de otros tiros. |
| [A Deep Learning Approach to Automatically Classify Ice Hockey Shooting Actions Using Acceleration Signals](papers/utiles/A%20Deep%20Learning%20Approach%20to%20Automatically%20Classify%20Ice%20Hockey%20Shooting%20Actions%20Using%20Acceleration%20Signals.pdf) | **Conservar para revisión** | Clasifica pases y tiros de muñeca con acelerometría y vídeo sincronizado. Evalúa tramos delimitados previamente con el vídeo. |
| [Pilot Study of Embedded IMU Sensors and Machine Learning Algorithms for Automated Ice Hockey Stick Fitting](papers/descartados/Pilot%20Study%20of%20Embedded%20IMU%20Sensors%20and%20Machine%20Learning%20Algorithms%20for%20Automated%20Ice%20Hockey%20Stick%20Fitting.pdf) | **Descartar de la síntesis principal** | El clasificador recomienda características del palo a partir de tiros ya identificados. |
| [Sensor-Integrated Mobile Application for Inline Hockey Performance Monitoring](papers/descartados/Sensor-Integrated%20Mobile%20Application%20for%20Inline%20Hockey%20Performance%20Monitoring.pdf) | **Descartar de la síntesis principal** | Evalúa el diseño de una aplicación. La detección de gestos con jugadores queda pendiente de validación. |
