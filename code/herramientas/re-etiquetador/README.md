# Re-etiquetador IoH

Abre `abrir_re_etiquetador.cmd` con doble clic en Windows. Requiere Python 3 con
Tkinter. Desde esta carpeta también puedes ejecutar `python re_etiquetador.py`
o abrir una captura directamente con `python re_etiquetador.py "ruta\captura.csv"`.

1. Pulsa **Abrir CSV** y elige una captura IoH con columna `label`.
2. Localiza el gesto en las gráficas de aceleración y giro. Los colores indican
   las etiquetas actuales. Usa la rueda para acercarte al cursor, el botón
   derecho para desplazar la vista y **Ver todo** para recuperar la captura completa.
3. Haz clic para seleccionar la muestra más cercana al cursor o arrastra para
   seleccionar todas las muestras entre los dos extremos, incluidos ambos.
4. Elige la etiqueta y pulsa **Aplicar a la selección**. Si te adelantaste,
   selecciona las muestras sobrantes y asigna **Sin etiqueta** (`undefined`).
   Si soltaste la tecla en mitad del gesto, selecciona el hueco y asigna el gesto.
   Puedes revertir la última corrección con **Deshacer**.
5. Pulsa **Guardar CSV** (o **Ctrl+S**) para actualizar el archivo abierto.
   Si está abierto en Excel y Windows impide guardarlo, cierra ese archivo en Excel.

El guardado modifica los campos `label` seleccionados y conserva los demás
datos y el formato del CSV. El primer guardado crea al lado una copia
`<nombre>.csv.original.bak`, que se conserva en las ediciones siguientes.
Si se detecta que el CSV cambió desde que se abrió, el editor rechaza el guardado.
