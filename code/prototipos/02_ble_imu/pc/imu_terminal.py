"""XIAO-IMU -> BLE -> CSV etiquetado con teclas mantenidas (Windows)."""
import asyncio
import csv
import ctypes
from datetime import datetime
from pathlib import Path
import re
import struct
import sys
import time
import unicodedata
from uuid import uuid4

from bleak import BleakClient, BleakScanner
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

NAME = "XIAO-IMU"
CHAR_UUID = "ac450002-8c4d-4e82-a36d-2715dca20104"
PACKET = struct.Struct("<IH6h")
APP_DIR = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
SAVE_DIR = APP_DIR / "registros"
KEY_LABELS = {"P": "pase", "R": "recepcion", "T": "tiro", "M": "manejo", "Q": "reposo"}
KEY_MOVEMENTS = {"P": "Pase", "R": "Recepción", "T": "Tiro", "M": "Manejo", "Q": "Reposo"}
KEY_COLORS = {
    "P": "bright_cyan", "R": "bright_green", "T": "bright_yellow",
    "M": "bright_magenta", "Q": "bright_blue",
}
LABEL_COLORS = {label: KEY_COLORS[key] for key, label in KEY_LABELS.items()}


class MovementKeyboard:
    """Consulta el estado actual, sin confundir la autorrepeticion con pulsaciones."""

    def __init__(self, get_key_state=None):
        if get_key_state is None:
            # Solo el bit alto de GetAsyncKeyState indica tecla mantenida.
            self.user32 = ctypes.WinDLL("user32", use_last_error=True)
            get_key_state = self.user32.GetAsyncKeyState
            get_key_state.argtypes = [ctypes.c_int]
            get_key_state.restype = ctypes.c_short
        self.get_key_state = get_key_state

    def is_down(self, virtual_key):
        return bool(self.get_key_state(virtual_key) & 0x8000)

    def pressed_keys(self):
        return [key for key in KEY_LABELS if self.is_down(ord(key))]

    def label(self):
        pressed = self.pressed_keys()
        return KEY_LABELS[pressed[0]] if len(pressed) == 1 else "undefined"


class Recorder:
    """CSV por sesion y controles sin bloquear BLE (terminal Windows)."""
    def __init__(self, keyboard=None, sample_name="imu"):
        self.keyboard = keyboard if keyboard is not None else MovementKeyboard()
        ascii_name = unicodedata.normalize("NFKD", sample_name).encode("ascii", "ignore").decode()
        self.sample_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", ascii_name)[:64].strip("_-") or "imu"
        self.file = None
        self.writer = None
        self.rows = 0
        self.path = None
        self.message = ""

    def command(self, text):
        command = text.strip().lower()
        if command == "start":
            if self.file:
                self.message = "Ya hay una grabación activa."
                return
            SAVE_DIR.mkdir(parents=True, exist_ok=True)
            path = SAVE_DIR / f"{self.sample_name}_{datetime.now():%Y%m%d_%H%M%S_%f}_{uuid4().hex[:8]}.csv"
            # 'x' impide sobrescribir cualquier archivo existente.
            self.file = path.open("x", newline="", encoding="utf-8-sig", buffering=1)
            self.writer = csv.writer(self.file, delimiter=";")
            self.writer.writerow([
                "pc_time_iso", "xiao_time_us", "sequence",
                "ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps",
                "label",
            ])
            self.rows = 0
            self.path = path
            self.message = "Grabación iniciada."
        elif command == "stop":
            self.stop()

    def stop(self):
        if self.file:
            self.file.close()
            self.file = self.writer = None
            self.message = f"CSV cerrado. {self.rows} muestras guardadas."
        else:
            self.message = "No hay ninguna grabación activa."

    def write(self, values, label=None):
        if self.file:
            if label is None:
                label = self.keyboard.label()
            stamp, seq, ax, ay, az, gx, gy, gz = values
            self.writer.writerow([
                datetime.now().astimezone().isoformat(timespec="milliseconds"),
                stamp, seq, ax/1000, ay/1000, az/1000, gx/10, gy/10, gz/10,
                label,
            ])
            self.rows += 1

    async def commands(self):
        import msvcrt
        space_held = False
        while True:
            while msvcrt.kbhit():
                key = msvcrt.getwch()
                if key == "\x03":
                    raise KeyboardInterrupt
                if key in ("\x00", "\xe0"):
                    msvcrt.getwch()  # Ignora teclas especiales (flechas, etc.).
                elif key == " " and not space_held:
                    space_held = True
                    try:
                        self.command("stop" if self.file else "start")
                    except OSError as error:
                        self.stop()
                        self.message = f"No se pudo grabar el CSV: {error}"
                # Las teclas de etiqueta se consultan al recibir cada muestra BLE.
            if not self.keyboard.is_down(0x20):
                space_held = False
            await asyncio.sleep(0.02)

    async def __aenter__(self):
        self.task = asyncio.create_task(self.commands())
        return self

    async def __aexit__(self, *_):
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass
        finally:
            if self.file:
                self.stop()




class Readings:
    def __init__(self):
        self.latest = None
        self.label = "undefined"
        self.count = self.gaps = self.invalid = self.elapsed_us = 0
        self.first_arrival = self.last_arrival = 0.0

    def update(self, values, label, arrival):
        if self.latest is None:
            self.first_arrival = arrival
        else:
            self.elapsed_us += (values[0] - self.latest[0]) & 0xFFFFFFFF
            step = (values[1] - self.latest[1]) & 0xFFFF
            if step:
                self.gaps += step - 1
        self.latest, self.label = values, label
        self.last_arrival = arrival
        self.count += 1

    def frequencies(self):
        intervals = self.count - 1
        elapsed = self.last_arrival - self.first_arrival
        source = (intervals + self.gaps) * 1_000_000 / self.elapsed_us if self.elapsed_us else None
        received = intervals / elapsed if elapsed else None
        return source, received


def dashboard(status, readings, recorder):
    show_samples = status == "Recibiendo muestras"
    label_style = f"bold {LABEL_COLORS.get(readings.label, 'white')}"
    details = Text.assemble(
        ("BLE  ", "bold cyan"), status, "\n",
        ("Muestra  ", "bold cyan"), recorder.sample_name, "\n",
        ("Etiqueta de la muestra  ", "bold cyan"),
        (readings.label if show_samples else "—", label_style),
    )
    axes = Table(title="Última muestra", expand=True, box=None, padding=(0, 1))
    axes.add_column("Sensor")
    for axis in ("X", "Y", "Z"):
        axes.add_column(axis, justify="right")
    if show_samples and readings.latest:
        _, sequence, *values = readings.latest
        axes.add_row("Aceleración [g]", *(f"{v / 1000:+.3f}" for v in values[:3]))
        axes.add_row("Giro [°/s]", *(f"{v / 10:+.1f}" for v in values[3:]))
    else:
        sequence = "—"
        axes.add_row("Aceleración [g]", "—", "—", "—")
        axes.add_row("Giro [°/s]", "—", "—", "—")
    frequencies = [
        f"{hz:.1f} Hz" if hz is not None and show_samples else "—"
        for hz in readings.frequencies()
    ]
    telemetry = Text(
        f"XIAO {frequencies[0]}  ·  PC {frequencies[1]}  ·  Secuencia {sequence}\n"
        f"Recibidas {readings.count}  ·  Saltos {readings.gaps}  ·  Paquetes inválidos {readings.invalid}"
    )
    recording = Text.assemble(
        ("GRABANDO" if recorder.file else "CSV DETENIDO",
         "bold red" if recorder.file else "bold white"),
        f"   {recorder.rows} muestras guardadas",
    )
    if recorder.path:
        recording.append(f"\n{recorder.path.name}", style="dim")
    if recorder.message:
        recording.append(f"\n{recorder.message}")
    pressed = recorder.keyboard.pressed_keys()
    controls = Text()
    for index, (key, movement) in enumerate(KEY_MOVEMENTS.items()):
        if index:
            controls.append("  ")
        active = key in pressed
        key_style = f"bold black on {KEY_COLORS[key]}" if active else "bold cyan"
        controls.append(f" {key} " if active else f"[{key}]", style=key_style)
        controls.append(f" {movement}", style=f"bold {KEY_COLORS[key]}" if active else "")
    if len(pressed) > 1:
        controls.append("\nVarias teclas pulsadas: undefined", style="bold yellow")
    controls.append("\n[Espacio] Iniciar/parar CSV   [Ctrl+C] Salir", style="cyan")
    return Panel(
        Group(details, Text(), axes, Text(), telemetry, Text(), recording, Text(), controls),
        title="IoH / Captura IMU",
        border_style="cyan",
        padding=(1, 2),
    )


async def main(console, sample_name):
    keyboard = MovementKeyboard()
    recorder = Recorder(keyboard, sample_name)
    readings = Readings()
    with Live(dashboard(f"Buscando {NAME}…", readings, recorder),
              console=console, auto_refresh=False) as live:
        device = await BleakScanner.find_device_by_filter(
            lambda device, adv: adv.local_name == NAME, timeout=15
        )
        if device is None:
            live.update(dashboard("XIAO no encontrada", readings, recorder), refresh=True)
            return "Enciende la XIAO, activa Bluetooth y vuelve a abrir el programa."

        live.update(dashboard("Conectando…", readings, recorder), refresh=True)

        def receive(_, data):
            arrival = time.perf_counter()
            if len(data) != PACKET.size:
                readings.invalid += 1
                return
            values = PACKET.unpack(data)
            label = keyboard.label()
            readings.update(values, label, arrival)
            try:
                recorder.write(values, label)
            except OSError as error:
                recorder.stop()
                recorder.message = f"Error escribiendo el CSV: {error}"

        async with BleakClient(device) as client:
            await client.start_notify(CHAR_UUID, receive)
            async with recorder:
                while client.is_connected:
                    if not readings.count:
                        status = "Conectada · esperando la primera muestra"
                    elif time.perf_counter() - readings.last_arrival >= 2:
                        status = "Conectada · sin muestras durante 2 s"
                    else:
                        status = "Recibiendo muestras"
                    live.update(dashboard(status, readings, recorder), refresh=True)
                    await asyncio.sleep(0.08)
        live.update(dashboard("XIAO desconectada", readings, recorder), refresh=True)
    return "Se cerró la conexión BLE."


def run():
    console = Console()
    if sys.argv[1:] == ["--vista-previa"]:
        readings = Readings()
        readings.update((0, 10, 120, -40, 986, 2, -3, 1), "reposo", 1)
        readings.update((9615, 11, 121, -39, 985, 1, -2, 1), "reposo", 1.009615)
        keyboard = MovementKeyboard(lambda key: 0x8000 if key == ord("Q") else 0)
        recorder = Recorder(keyboard, "jugador_03_hielo")
        console.print(dashboard("Recibiendo muestras", readings, recorder), markup=False)
        console.print("Vista previa con datos de ejemplo. Carpeta de captura:", str(SAVE_DIR), markup=False)
        return 0

    exit_code = 0
    try:
        sample_name = console.input("Nombre de la muestra (Enter para usar imu): ")
        message = asyncio.run(main(console, sample_name))
    except KeyboardInterrupt:
        message = "Captura finalizada."
    except EOFError:
        message = "Captura cancelada antes de conectar."
    except Exception as error:
        message = f"No se pudo completar la captura: {error}"
        exit_code = 1
    console.print(message, markup=False)
    if getattr(sys, "frozen", False) and sys.stdin.isatty():
        try:
            input("Pulsa Enter para cerrar la ventana.")
        except (EOFError, KeyboardInterrupt):
            pass
    return exit_code


if __name__ == "__main__":
    raise SystemExit(run())
