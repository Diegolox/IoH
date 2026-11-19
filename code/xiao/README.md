# XIAO nRF52840 Sense · IoH

Plantilla de PlatformIO con framework Arduino para la **Seeed Studio XIAO nRF52840 Sense**.

## Abrir y ejecutar

1. Instala la extension **PlatformIO IDE** en VS Code y Git si no lo tienes.
2. Abre esta carpeta (`code/xiao`), donde esta `platformio.ini`.
3. Conecta la placa con un cable USB-C de datos.
4. Pulsa **Build**, despues **Upload** y abre **Serial Monitor** a **115200 baudios**.

La primera compilacion descarga la plataforma de Seeed y sus herramientas; necesita Internet.
El programa conmuta el LED integrado cada 500 ms y muestra el tiempo de ejecucion por USB.
La espera del puerto serie esta limitada a 3 segundos para permitir el arranque sin ordenador.

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

## Ampliar el proyecto

Anade las bibliotecas externas mediante `lib_deps` en `platformio.ini`.
La plantilla comprueba el arranque y la comunicacion USB; la IMU, el microfono
y Bluetooth quedan pendientes de implementar segun las necesidades del proyecto.

Se utiliza la [configuracion publicada por Seeed](https://wiki.seeedstudio.com/xiao_nrf52840_with_platform_io/).
Aunque el identificador `seeed-xiao-afruitnrf52-nrf52840` no contiene la palabra
Sense, es el que Seeed indica para esta placa. El LED integrado es activo a nivel bajo.
