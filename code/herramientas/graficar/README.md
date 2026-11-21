# Graficar registros IMU

Coloca los CSV junto a `graficar.py`. Solo busca en esta carpeta, sin entrar en
subcarpetas ni buscar en los registros del prototipo. Los CSV deben conservar
las columnas y el separador punto y coma del programa de captura.

Desde esta carpeta:

```powershell
python -m pip install -r requirements.txt
python graficar.py
```

Elige un número, T para todos o Enter para el último archivo de la lista.
Para analizar todos sin abrir ventanas:

```powershell
python graficar.py --todos --sin-ventana
```

También puedes indicar nombres de CSV de esta misma carpeta:

```powershell
python graficar.py muestra.csv
```

Cada CSV genera una carpeta con su mismo nombre sin la extensión, que contiene:
- `graficas.png` y seis gráficas individuales.
- `resumen.txt`: frecuencia, saltos del contador y estadísticas.
- `estadisticas.csv`: media, desviación, mínimo, máximo y RMS de cada eje.
- `datos_analizados.csv`: tiempos relativos, seis ejes, módulos e intervalos.

El CSV original no se modifica. Repetir un análisis actualiza sus resultados.
`--guardar` se mantiene por compatibilidad, pero ya se guarda automáticamente.

La aceleración incluye gravedad. No se filtra ni calibra. La media del giro
solo sirve para estimar su offset si toda la captura se hizo en reposo.
Los saltos no detectan conversiones perdidas antes de leer la IMU.
Se contemplan desbordamientos del tiempo y contador. El reloj del PC mide
recepción y puede ajustarse; para analizar la señal se usa el tiempo de la XIAO.
