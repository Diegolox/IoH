import codecs
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from re_etiquetador import Captura


HEADER = b"xiao_time_us;ax_g;ay_g;az_g;gx_dps;gy_dps;gz_dps;label;extra\r\n"
DATA = (
    b"4294967280;1.000;0;0;0;0;0;pase;a\r\n"
    b'4;2.000;0;0;0;0;0;undefined;"b;c"\r\n'
    b'24;3.000;0;0;0;0;0;tiro;"d\r\ne"'
)
ORIGINAL = codecs.BOM_UTF8 + HEADER + DATA


class CapturaTest(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "movimiento.csv"
        self.path.write_bytes(ORIGINAL)
        self.capture = Captura(self.path)

    def test_guarda_solo_etiquetas_y_conserva_la_primera_copia(self):
        self.capture.apply(1, 2, "manejo")
        self.assertEqual(self.path.read_bytes(), ORIGINAL)
        self.assertEqual(self.capture.save(), 2)
        self.assertEqual(
            self.path.read_bytes(),
            ORIGINAL.replace(b";undefined;", b";manejo;").replace(b";tiro;", b";manejo;"),
        )
        self.capture.apply(1, 1, "reposo")
        self.capture.save()
        self.assertEqual(self.capture.backup.read_bytes(), ORIGINAL)
        self.assertEqual(Captura(self.path).labels, ["pase", "reposo", "manejo"])

    def test_seleccion_invertida_y_clic_sobre_una_muestra(self):
        self.assertEqual(self.capture.times, [0, 0.000020, 0.000040])
        self.assertEqual(self.capture.selection(0.000039, 0.000019), (1, 2))
        self.assertEqual(self.capture.selection(0.000019, 0.000019), (1, 1))

    def test_deshacer_despues_de_guardar_vuelve_a_marcar_cambios(self):
        self.capture.apply(0, 1, "reposo")
        self.capture.save()
        self.assertFalse(self.capture.dirty)
        self.capture.undo()
        self.assertTrue(self.capture.dirty)
        self.capture.save()
        self.assertEqual(self.path.read_bytes(), ORIGINAL)

    def test_no_sobrescribe_cambios_externos(self):
        self.capture.apply(0, 0, "reposo")
        external = ORIGINAL.replace(b";pase;", b";tiro;")
        self.path.write_bytes(external)
        with self.assertRaises(ValueError):
            self.capture.save()
        self.assertEqual(self.path.read_bytes(), external)
        self.assertFalse(self.capture.backup.exists())


if __name__ == "__main__":
    unittest.main()
