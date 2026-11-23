import asyncio
import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import imu_terminal as imu


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
