"""XIAO-IMU -> BLE -> terminal. Instalar: python -m pip install bleak"""
import asyncio
import csv
from datetime import datetime
from pathlib import Path
import struct
import time
from uuid import uuid4

from bleak import BleakClient, BleakScanner

NAME = "XIAO-IMU"
CHAR_UUID = "ac450002-8c4d-4e82-a36d-2715dca20104"
PACKET = struct.Struct("<IH6h")
PRINT_EVERY = 10  # 1: imprime todas; 10: una de cada diez, recibe y cuenta TODAS.
SAVE_DIR = Path(__file__).resolve().parent / "registros"


class Recorder:
    """CSV por sesion y comandos sin bloquear BLE (terminal Windows)."""
    def __init__(self):
        self.file = None
        self.writer = None
        self.rows = 0
        self.text = ""

    def command(self, text):
        command = text.strip().lower()
        if command == "start":
            if self.file:
                print("Ya estas grabando. Escribe stop antes de iniciar otra sesion.")
                return
            SAVE_DIR.mkdir(parents=True, exist_ok=True)
            path = SAVE_DIR / f"imu_{datetime.now():%Y%m%d_%H%M%S_%f}_{uuid4().hex[:8]}.csv"
            # 'x' impide sobrescribir cualquier archivo existente.
            self.file = path.open("x", newline="", encoding="utf-8-sig", buffering=1)
            self.writer = csv.writer(self.file, delimiter=";")
            self.writer.writerow([
                "pc_time_iso", "xiao_time_us", "sequence",
                "ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps",
            ])
            self.rows = 0
            print(f"Grabando: {path}")
        elif command == "stop":
            self.stop()
        elif command:
            print("Comandos: start + Enter / stop + Enter / Ctrl+C para salir.")

    def stop(self):
        if self.file:
            self.file.close()
            self.file = self.writer = None
            print(f"CSV cerrado: {self.rows} muestras guardadas.")
        else:
            print("No hay ninguna grabacion activa.")

    def write(self, values):
        if self.file:
            stamp, seq, ax, ay, az, gx, gy, gz = values
            self.writer.writerow([
                datetime.now().astimezone().isoformat(timespec="milliseconds"),
                stamp, seq, ax/1000, ay/1000, az/1000, gx/10, gy/10, gz/10,
            ])
            self.rows += 1

    async def commands(self):
        import msvcrt
        while True:
            while msvcrt.kbhit():
                key = msvcrt.getwch()
                if key == "\x03":
                    raise KeyboardInterrupt
                if key in ("\x00", "\xe0"):
                    msvcrt.getwch()  # Ignora teclas especiales (flechas, etc.).
                elif key == "\r":
                    print()
                    text, self.text = self.text, ""
                    try:
                        self.command(text)
                    except OSError as error:
                        self.stop()
                        print(f"No se pudo grabar el CSV: {error}")
                elif key == "\b":
                    if self.text:
                        self.text = self.text[:-1]
                        print("\b \b", end="", flush=True)
                elif key.isprintable():
                    self.text += key
                    print(key, end="", flush=True)
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


async def main():
    print(f"Buscando {NAME}... Activa el Bluetooth del PC.")
    device = await BleakScanner.find_device_by_filter(
        lambda device, adv: adv.local_name == NAME, timeout=15
    )
    if device is None:
        print("No encontrada. Enciende la XIAO y cierra otras apps BLE.")
        return

    queue = asyncio.Queue(maxsize=1000)
    pc_drops = 0

    def receive(_, data):
        nonlocal pc_drops
        if len(data) != PACKET.size:
            print(f"Paquete inesperado: {len(data)} bytes")
            return
        values = PACKET.unpack(data)
        # Guarda TODAS las notificaciones, independientemente de PRINT_EVERY.
        try:
            recorder.write(values)
        except OSError as error:
            recorder.stop()
            print(f"Error escribiendo CSV: {error}")
        try:
            queue.put_nowait((time.perf_counter(), values))
        except asyncio.QueueFull:
            pc_drops += 1

    async with BleakClient(device) as client, Recorder() as recorder:
        await client.start_notify(CHAR_UUID, receive)
        print("Conectado. A[g] incluye gravedad; G[grados/s]. Ctrl+C para salir.")
        print("Escribe start + Enter para grabar; stop + Enter para cerrar el CSV.")
        first_pc = first_us = previous_seq = None
        previous_us = elapsed_us = count = lost = 0
        hz_pc = hz_read = 0.0
        last_report = time.perf_counter()
        while client.is_connected:
            try:
                arrival, (stamp, seq, ax, ay, az, gx, gy, gz) = await asyncio.wait_for(
                    queue.get(), timeout=2
                )
            except asyncio.TimeoutError:
                print("Sin muestras durante 2 s.")
                continue
            if first_pc is None:
                first_pc, first_us, previous_us = arrival, stamp, stamp
            else:
                elapsed_us += (stamp - previous_us) & 0xFFFFFFFF
                previous_us = stamp
            if previous_seq is not None:
                lost += ((seq - previous_seq) & 0xFFFF) - 1
            previous_seq = seq
            count += 1
            # Promedios desde la primera muestra; resisten llegada por rafagas.
            if count > 1 and arrival > first_pc and elapsed_us:
                hz_pc = (count - 1) / (arrival - first_pc)
                hz_read = (count - 1 + lost) * 1_000_000 / elapsed_us
            if not recorder.text and (count - 1) % PRINT_EVERY == 0:
                print(
                    f"{seq:5d} | A[g] {ax/1000:7.3f} {ay/1000:7.3f} {az/1000:7.3f}"
                    f" | G[dps] {gx/10:8.1f} {gy/10:8.1f} {gz/10:8.1f}"
                )
            if arrival - last_report >= 1:
                if not recorder.text:
                    print(f"--- Lectura: {hz_read:.1f} Hz | PC: {hz_pc:.1f} Hz"
                          f" | Saltos: {lost} | Descartes cola PC: {pc_drops}"
                          f" | CSV: {'ON' if recorder.file else 'OFF'} ---")
                last_report = arrival


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nFin.")
    except Exception as error:
        print(f"Error BLE: {error}")
