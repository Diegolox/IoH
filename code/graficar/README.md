# Graficar y analizar registros IMU

En una terminal situada en `code/graficar`:

```powershell
python -m pip install -r requirements.txt
python graficar.py
```

Selecciona un archivo de `code/pc/registros` por su numero. Enter elige el ultimo.
Muestra seis paneles: aceleracion XYZ, giro XYZ, modulos de ambos sensores e
intervalos entre muestras en la XIAO y entre llegadas al PC. La barra de Matplotlib
permite ampliar, desplazar y guardar la figura. No modifica los datos originales.

Tambien puedes indicar uno o varios archivos:

```powershell
python graficar.py ../pc/registros/mi_registro.csv
python graficar.py ../pc/registros/mi_registro.csv --guardar
python graficar.py ../pc/registros/mi_registro.csv --guardar --sin-ventana
python graficar.py ../pc/registros/mi_registro.csv --sin-ventana
```

Cada ejecucion crea junto al CSV una carpeta con su mismo nombre (sin .csv).
Guarda graficas.png, seis paneles PNG independientes, resumen.txt, estadisticas.csv
y datos_analizados.csv (tiempos relativos, seis ejes, modulos e intervalos).
Repetir el analisis actualiza los resultados de esa carpeta; el CSV original no se toca.
Ya no hace falta --guardar; se mantiene por compatibilidad. --sin-ventana guarda
todo sin abrir ventanas. Con varios CSV crea una carpeta por registro.

La terminal muestra numero de muestras, duracion, frecuencia estimada de lectura,
frecuencia recibida, saltos y contadores repetidos; tambien media, desviacion
tipica poblacional, minimo, maximo y RMS de cada eje.

La frecuencia de lectura se estima mediante incremento del contador / tiempo XIAO.
La recibida usa numero de muestras / tiempo. Si no hay saltos coinciden.
Se contemplan los desbordamientos de tiempo uint32 y contador uint16; se rechazan
retrocesos grandes compatibles con reinicios o desorden. No se recuperan muestras
perdidas ni se detectan conversiones omitidas antes de leer los registros de la IMU.

La aceleracion incluye gravedad. No se resta la media, filtra ni calibra.
Solo interpreta la media del giro como offset si grabaste en reposo.
El CSV no contiene los rangos configurados: este script no declara saturacion.
El reloj del PC es de pared (puede ajustarse) y mide llegada, no conversion.
