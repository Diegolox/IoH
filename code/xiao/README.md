# XIAO nRF52840 Sense · IoH

Plantilla de PlatformIO con framework Arduino para la **Seeed Studio XIAO nRF52840 Sense**.

## Abrir y ejecutar

1. Instala la extension **PlatformIO IDE** en VS Code y Git si no lo tienes.
2. Abre esta carpeta (`code/xiao`), donde esta `platformio.ini`.
3. Conecta la placa con un cable USB-C de datos.
4. Pulsa **Build**, despues **Upload** y abre **Serial Monitor** a **115200 baudios**.

La primera compilacion descarga la plataforma de Seeed y sus herramientas; necesita Internet.
El programa mide la bateria cada 5 segundos y envia los datos por USB y Bluetooth LE.
Arranca sin esperar al ordenador. El LED rojo de usuario da un destello de 100 ms cada
segundo para comprobar que el programa sigue ejecutandose.

Desde la terminal de PlatformIO tambien puedes ejecutar:

```sh
pio run
pio run --target upload
pio device monitor --baud 115200
```

Si no detecta el puerto, revisa `pio device list` y configura `upload_port` o `monitor_port`
en `platformio.ini`. Cierra el monitor serie antes de cargar. Si la carga no conecta,
pulsa RESET dos veces rapidamente para entrar en el bootloader y vuelve a cargar;
el puerto COM puede cambiar.

## Estructura

```text
xiao/
|-- platformio.ini    # Placa, framework y comunicacion
|-- src/main.cpp      # setup() y loop()
|-- include/          # Cabeceras del proyecto
|-- lib/              # Bibliotecas propias
|-- test/             # Futuras pruebas
`-- README.md
```

## Medir la carga y descarga de la bateria

Preparado para la **LP502030-CI-JST: LiPo 1S de 3,7 V y 250 mAh**, con conector JST PH2.0.
La [ficha del proveedor](https://www.tiendatec.es/electronica/baterias-pilas-y-accesorios/bateras-li-po/959-bateria-litio-lipo-502030-37v-250mah-095wh-jst-ph20-8472496014960.html)
indica carga a 4,2 V, corriente normal de 50 mA y proteccion integrada.
La XIAO no incorpora una toma JST: suelda un conector compatible con cables a los pads
BAT+ y BAT- de la cara inferior, con la bateria y el USB desconectados.
Comprueba la polaridad con multimetro antes de enchufar la bateria; el formato JST
por si solo no garantiza la posicion del positivo. No conectes la bateria a 3V3 ni a 5V.
Se selecciona la corriente baja del cargador, aproximadamente **50 mA** (0,2 C),
coincidiendo con la corriente normal indicada por el proveedor.
Los 50 mA son una seleccion del cargador,
no una medida: la corriente real disminuye al final de la carga.

### Datos enviados

Cada linea es CSV, sin cabecera, con estas columnas:

```text
tiempo_ms,bateria_mV,usb_presente,chg_activo,estado
5000,3890,1,1,CHARGING
10000,3887,0,0,BATTERY
```

Las filas son ilustrativas. `chg_activo` es la lectura de la senal ~CHG, activa a nivel bajo.

| Estado | Interpretacion |
| --- | --- |
| CHARGING | USB presente y el cargador indica carga activa. |
| USB_IDLE | USB presente sin indicacion de carga activa. No demuestra bateria llena. |
| BATTERY | Sin alimentacion USB; con la bateria conectada, la placa funciona con ella. |

La placa no mide la corriente de bateria ni cuenta mAh. No se publica porcentaje
porque el voltaje por si solo no proporciona un estado de carga preciso.
Sin bateria, la lectura del nodo BAT no representa una bateria valida.

### Prueba por USB y Bluetooth

**Comprobacion sin movil:** tras cargar el programa, verifica que el LED rojo de usuario
parpadea una vez por segundo. Desconecta el USB dejando la bateria conectada y observa
durante 15 segundos. Si sigue parpadeando, la bateria alimenta la placa y el programa
sigue ejecutandose. Si deja de hacerlo, aun no sabemos si falta alimentacion o se ha
detenido el programa: comprueba la tension en BAT+ / BAT- y en 3V3 / GND sin USB.
Este destello no indica el estado de carga; es distinto del indicador del cargador.

1. Carga el programa y abre el monitor serie a 115200 para ver la carga con USB conectado.
2. En el movil, usa **Adafruit Bluefruit Connect**, conecta con **IoH-Battery** y abre **UART**.
   Es una conexion desde la app, no un emparejamiento de Bluetooth clasico.
3. Comprueba que llegan filas cada 5 segundos y desconecta el USB: los datos seguiran
   llegando por Bluetooth y el estado pasara a `BATTERY`.
4. Vuelve a conectar el USB para observar el estado del cargador y la evolucion del voltaje.

Para una primera comprobacion, observa unos minutos y compara el voltaje con un multimetro
en BAT+ / BAT-. El ADC y el divisor tienen tolerancias; no interpretes pequenos cambios
entre muestras como cambios seguros de carga. No agotes deliberadamente una bateria
sin proteccion: este programa no implementa corte por baja tension.
La autonomia observada incluye el consumo del LED, de Bluetooth y de este firmware; no es una
medida de autonomia con el equipo en reposo de bajo consumo.

### Detalles de la medida

Se mantiene `VBAT_ENABLE` (P0.14) a LOW, se lee `PIN_VBAT` (P0.31) con ADC de 12 bits,
referencia interna con escala de 3,6 V, adquisicion de 40 us y promedio de 16 muestras.
Se compensa el divisor de 1 Mohm / 510 kohm. Los numeros Arduino utilizados corresponden
al core Seeed/Adafruit configurado en este proyecto, no a la numeracion fisica del chip.

Referencias: [circuito y precaucion de lectura](https://wiki.seeedstudio.com/XIAO_BLE/#q3-what-are-the-considerations-when-using-xiao-nrf52840-sense-for-battery-charging),
[seleccion de corriente](https://wiki.seeedstudio.com/XIAO_BLE/#battery-charging-current)
y [app Bluefruit Connect](https://learn.adafruit.com/bluefruit-le-connect/uart).

## Ampliar el proyecto

Anade las bibliotecas externas mediante `lib_deps` en `platformio.ini`.
La IMU y el microfono quedan pendientes de implementar segun las necesidades del proyecto.
El servicio BLE UART utiliza la biblioteca Bluefruit incluida en el core; no necesita `lib_deps`.

Se utiliza la [configuracion publicada por Seeed](https://wiki.seeedstudio.com/xiao_nrf52840_with_platform_io/).
Aunque el identificador `seeed-xiao-afruitnrf52-nrf52840` no contiene la palabra
Sense, es el que Seeed indica para esta placa. El LED integrado es activo a nivel bajo.
