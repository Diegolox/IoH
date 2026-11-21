"""XIAO-IMU -> BLE -> terminal. Instalar: python -m pip install bleak"""
import asyncio
import struct
import time

from bleak import BleakClient, BleakScanner

NAME = "XIAO-IMU"
CHAR_UUID = "ac450002-8c4d-4e82-a36d-2715dca20104"
PACKET = struct.Struct("<IH6h")
PRINT_EVERY = 10  # 1: imprime todas; 10: una de cada diez, recibe y cuenta TODAS.


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
        try:
            queue.put_nowait((time.perf_counter(), PACKET.unpack(data)))
        except asyncio.QueueFull:
            pc_drops += 1

    async with BleakClient(device) as client:
        await client.start_notify(CHAR_UUID, receive)
        print("Conectado. A[g] incluye gravedad; G[grados/s]. Ctrl+C para salir.")
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
            if (count - 1) % PRINT_EVERY == 0:
                print(
                    f"{seq:5d} | A[g] {ax/1000:7.3f} {ay/1000:7.3f} {az/1000:7.3f}"
                    f" | G[dps] {gx/10:8.1f} {gy/10:8.1f} {gz/10:8.1f}"
                )
            if arrival - last_report >= 1:
                print(f"--- Lectura: {hz_read:.1f} Hz | PC: {hz_pc:.1f} Hz"
                      f" | Saltos: {lost} | Descartes cola PC: {pc_drops} ---")
                last_report = arrival


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nFin.")
    except Exception as error:
        print(f"Error BLE: {error}")
