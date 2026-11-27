import asyncio
import csv
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import imu_terminal as imu
from bleak.exc import BleakError
from rich.console import Console


class BatteryTests(unittest.TestCase):
    def test_panel_identifies_prototype_and_shows_battery_before_ble_status(self):
        readings = imu.Readings()
        recorder = imu.Recorder(imu.MovementKeyboard(lambda _: 0))
        output = StringIO()
        console = Console(file=output, width=60, color_system=None)

        console.print(imu.dashboard('Conectando…', readings, recorder))
        self.assertIn('Captura IMU 03', output.getvalue())
        self.assertIn('Esperando lectura', output.getvalue())

        output.seek(0)
        output.truncate()
        console.print(imu.dashboard('Recibiendo muestras', readings, recorder))
        panel = output.getvalue()
        self.assertLess(panel.index('Batería'), panel.index('Recibiendo muestras'))

    def test_panel_marks_low_battery_and_hides_invalid_or_unavailable_values(self):
        class Services:
            def get_characteristic(self, uuid):
                return uuid if payload is not None else None

        class BatteryClient:
            services = Services()

            async def read_gatt_char(self, uuid, *, use_cached):
                if uuid != '00002a19-0000-1000-8000-00805f9b34fb' or use_cached:
                    raise AssertionError('Se esperaba una lectura BLE actual de Battery Level')
                if isinstance(payload, Exception):
                    raise payload
                return payload

        readings = imu.Readings()
        recorder = imu.Recorder(imu.MovementKeyboard(lambda _: 0))
        for payload, expected in [
            (bytes([26]), '26 % estimado'),
            (bytes([25]), '25 % estimado · Batería baja'),
            (bytes([0]), '0 % estimado · Batería baja'),
            (bytes([101]), 'Sin lectura'),
            (bytes([25, 0]), 'Sin lectura'),
            (BleakError('Battery Service no disponible'), 'Sin lectura'),
            (None, 'Carga el firmware 03 en la XIAO'),
            (bytes([64]), '64 % estimado'),
        ]:
            with self.subTest(payload=payload):
                update = readings.update_battery(BatteryClient())
                # La lectura simulada termina sin suspender la corrutina.
                with self.assertRaises(StopIteration):
                    update.send(None)
                output = StringIO()
                Console(file=output, width=100, color_system=None).print(
                    imu.dashboard('Recibiendo muestras', readings, recorder)
                )
                self.assertIn(expected, output.getvalue())
                if expected == '26 % estimado':
                    self.assertNotIn('Batería baja', output.getvalue())


class LabelTests(unittest.TestCase):
    def test_held_keys_release_and_ambiguity(self):
        pressed = set()
        keyboard = imu.MovementKeyboard(lambda key: -32768 if key in pressed else 0)
        self.assertEqual(keyboard.label(), 'undefined')
        for key, label in [('P', 'pase'), ('R', 'recepcion'), ('T', 'tiro'),
                           ('M', 'manejo'), ('Q', 'reposo')]:
            pressed.add(ord(key))
            self.assertEqual(keyboard.label(), label)
            pressed.clear()
            self.assertEqual(keyboard.label(), 'undefined')
        pressed.update([ord('P'), ord('Q')])
        self.assertEqual(keyboard.label(), 'undefined')
        pressed.remove(ord('Q'))
        self.assertEqual(keyboard.label(), 'pase')

    def test_recent_press_bit_does_not_mean_held(self):
        keyboard = imu.MovementKeyboard(lambda key: 1)
        self.assertEqual(keyboard.label(), 'undefined')

    def test_space_autorepeat_does_not_toggle_recording_repeatedly(self):
        import msvcrt

        pending = [' ', ' ', ' ']
        frame = 0
        keyboard = imu.MovementKeyboard(lambda key: 0x8000 if key == 0x20 and frame < 2 else 0)
        recorder = imu.Recorder(keyboard)

        async def next_frame(_):
            nonlocal frame
            frame += 1
            if frame == 1:
                pending.extend([' ', ' '])  # Autorrepeticion: sigue mantenida.
            elif frame == 3:
                pending.append(' ')  # Nueva pulsacion despues de soltar.
            elif frame == 4:
                raise asyncio.CancelledError

        with tempfile.TemporaryDirectory() as directory, \
                patch.object(imu, 'SAVE_DIR', Path(directory)), \
                patch.object(msvcrt, 'kbhit', side_effect=lambda: bool(pending)), \
                patch.object(msvcrt, 'getwch', side_effect=lambda: pending.pop(0)), \
                patch.object(imu.asyncio, 'sleep', side_effect=next_frame), \
                patch.object(recorder, 'command', wraps=recorder.command) as command:
            controls = recorder.commands()
            try:
                with self.assertRaises(asyncio.CancelledError):
                    # Los pasos simulados no esperan E/S; no necesitan un event loop
                    # ni el socket local que asyncio crea al iniciarse en Windows.
                    controls.send(None)
                self.assertEqual([call.args[0] for call in command.call_args_list], ['start', 'stop'])
                self.assertIsNone(recorder.file)
            finally:
                controls.close()
                if recorder.file:
                    recorder.stop()

    def test_csv_labels_follow_each_notification_and_sessions_do_not_overwrite(self):
        pressed = set()
        keyboard = imu.MovementKeyboard(lambda key: 0x8000 if key in pressed else 0)
        with tempfile.TemporaryDirectory() as directory, patch.object(imu, 'SAVE_DIR', Path(directory)):
            recorder = imu.Recorder(keyboard, sample_name='../ Medición: hielo')
            recorder.command('start')
            values = (1234, 5, 1000, -2000, 500, 100, -200, 50)
            recorder.write(values)
            pressed.add(ord('R'))
            recorder.write(values)
            pressed.clear()
            pressed.add(ord('Q'))
            recorder.write(values)
            pressed.clear()
            recorder.write(values)
            recorder.stop()
            recorder.write(values)
            recorder.command('start')
            recorder.write(values)
            recorder.stop()
            files = sorted(Path(directory).glob('*.csv'))
            self.assertEqual(len(files), 2)
            self.assertTrue(all(path.name.startswith('Medicion_hielo_') for path in files))
            with files[0].open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.DictReader(stream, delimiter=';'))
            self.assertEqual([row['label'] for row in rows],
                             ['undefined', 'recepcion', 'reposo', 'undefined'])
            self.assertEqual(float(rows[0]['ax_g']), 1.0)
            self.assertEqual(float(rows[0]['gy_dps']), -20.0)
            self.assertEqual(rows[0]['xiao_time_us'], '1234')


if __name__ == '__main__':
    unittest.main()
