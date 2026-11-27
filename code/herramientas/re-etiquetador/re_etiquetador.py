"""Edición interactiva de las etiquetas de un CSV de captura IoH."""

import argparse
from bisect import bisect_left, bisect_right
import codecs
import csv
from io import StringIO
import math
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


CHANNELS = ("ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps")
LABELS = {
    "pase": ("Pase", "#80cbd6"),
    "recepcion": ("Recepción", "#86cda8"),
    "tiro": ("Tiro de muñeca", "#f4c484"),
    "manejo": ("Manejo", "#d9a4d4"),
    "reposo": ("Reposo", "#a5baf2"),
    "undefined": ("Sin etiqueta", "#e4e8ed"),
}
OTHER_LABEL = ("Otra etiqueta", "#dccdbd")
# Captura la posición de cada campo sin modificar el formato de los otros.
CSV_FIELD = re.compile(r'(?:^|;)("(?:[^"]|"")*"|[^;\r\n]*)')


class Captura:
    def __init__(self, path):
        self.path = path.resolve()
        self.backup = self.path.with_suffix(self.path.suffix + ".original.bak")
        self.saved_bytes = self.path.read_bytes()
        self.bom = codecs.BOM_UTF8 if self.saved_bytes.startswith(codecs.BOM_UTF8) else b""
        source = self.saved_bytes.decode("utf-8-sig")
        stream = StringIO(source, newline="")
        reader = csv.reader(stream, delimiter=";", strict=True)
        header = next(reader, [])
        if len(set(header)) != len(header) or not {"xiao_time_us", "label", *CHANNELS}.issubset(header):
            raise ValueError("Abre un CSV de captura IoH con columna label y separador punto y coma.")
        label_column = header.index("label")
        time_column = header.index("xiao_time_us")
        channels = [header.index(name) for name in CHANNELS]
        self.header = source[:stream.tell()]
        self.records = []
        self.original_labels = []
        self.times = []
        self.acceleration = []
        self.rotation = []
        elapsed = 0
        previous = None
        end = stream.tell()
        for row in reader:
            start, end = end, stream.tell()
            record = source[start:end]
            fields = list(CSV_FIELD.finditer(record))
            if len(row) != len(header) or len(fields) != len(header):
                raise ValueError(f"Fila incompleta o incompatible cerca de la línea {reader.line_num}.")
            try:
                stamp = int(row[time_column])
                values = [float(row[index]) for index in channels]
            except ValueError as error:
                raise ValueError(f"Tiempo o señal inválidos en la línea {reader.line_num}.") from error
            if not 0 <= stamp < 2**32 or not all(map(math.isfinite, values)):
                raise ValueError(f"Tiempo o señal fuera de rango en la línea {reader.line_num}.")
            if previous is not None:
                delta = (stamp - previous) % 2**32
                if delta > 2**31:
                    raise ValueError(f"Tiempo desordenado o reinicio de la XIAO en la línea {reader.line_num}.")
                elapsed += delta
            previous = stamp
            self.times.append(elapsed / 1e6)
            self.acceleration.append(math.hypot(*values[:3]))
            self.rotation.append(math.hypot(*values[3:]))
            left, right = fields[label_column].span(1)
            self.records.append((record[:left], record[left:right], record[right:]))
            self.original_labels.append(row[label_column])
        if not self.times:
            raise ValueError("El CSV no contiene muestras.")
        self.labels = self.original_labels.copy()
        self.saved_labels = self.labels.copy()
        self.history = []

    @property
    def dirty(self):
        return self.labels != self.saved_labels

    def nearest(self, time):
        index = bisect_left(self.times, time)
        if index == len(self.times):
            return index - 1
        if index and time - self.times[index - 1] <= self.times[index] - time:
            return index - 1
        return index

    def selection(self, first, last):
        return tuple(sorted((self.nearest(first), self.nearest(last))))

    def apply(self, start, stop, label):
        if label not in LABELS:
            raise ValueError("Etiqueta desconocida.")
        previous = self.labels[start:stop + 1]
        updated = [label] * len(previous)
        if updated != previous:
            self.history.append((start, previous))
            self.labels[start:stop + 1] = updated

    def undo(self):
        start, previous = self.history.pop()
        self.labels[start:start + len(previous)] = previous
        return start, start + len(previous) - 1

    def save(self):
        changed = sum(label != old for label, old in zip(self.labels, self.saved_labels))
        if not changed:
            return 0
        if self.path.read_bytes() != self.saved_bytes:
            raise ValueError("El CSV cambió fuera del editor. Vuelve a abrirlo antes de guardar.")
        records = [self.header]
        for (prefix, field, suffix), label, original in zip(self.records, self.labels, self.original_labels):
            records.append(prefix + (field if label == original else label) + suffix)
        data = self.bom + "".join(records).encode("utf-8")
        temporary = None
        try:
            with NamedTemporaryFile(dir=self.path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
            # La primera copia se crea una sola vez y conserva los bytes de la captura.
            try:
                backup = self.backup.open("xb")
            except FileExistsError:
                pass
            else:
                try:
                    with backup:
                        backup.write(self.saved_bytes)
                except OSError:
                    self.backup.unlink(missing_ok=True)
                    raise
            if self.path.read_bytes() != self.saved_bytes:
                raise ValueError("El CSV cambió fuera del editor. Vuelve a abrirlo antes de guardar.")
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        self.saved_bytes = data
        self.saved_labels = self.labels.copy()
        return changed


def label_style(label):
    return LABELS.get(label.strip().lower() or "undefined", OTHER_LABEL)


class Editor:
    def __init__(self, root):
        self.root = root
        self.capture = None
        self.selected = None
        self.anchor = None
        self.pan = None
        self.view = (0, 1)
        self.total = self.view
        self.filename = tk.StringVar(value="Ningún CSV abierto")
        self.status = tk.StringVar(value="Abre un CSV de captura IoH.")
        self.label = tk.StringVar(value=LABELS["undefined"][0])

        root.title("IoH · Re-etiquetador")
        root.geometry("1050x690")
        root.minsize(690, 430)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Control-o>", lambda event: self.open())
        root.bind("<Control-s>", lambda event: self.save())
        root.bind("<Control-z>", lambda event: self.undo())

        toolbar = ttk.Frame(root, padding=(12, 10))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Abrir CSV…", command=self.open).pack(side="left")
        self.save_button = ttk.Button(toolbar, text="Guardar CSV", command=self.save)
        self.save_button.pack(side="left", padx=(6, 0))
        self.undo_button = ttk.Button(toolbar, text="Deshacer", command=self.undo)
        self.undo_button.pack(side="left", padx=6)
        self.reset_button = ttk.Button(toolbar, text="Ver todo", command=self.reset_view)
        self.reset_button.pack(side="right")
        ttk.Label(toolbar, textvariable=self.filename).pack(side="left", padx=8)

        controls = ttk.Frame(root, padding=(12, 0, 12, 8))
        controls.pack(fill="x")
        ttk.Label(controls, text="Asignar etiqueta").pack(side="left")
        names = [name for name, _ in LABELS.values()]
        self.combo = ttk.Combobox(controls, values=names, textvariable=self.label, state="readonly", width=17)
        self.combo.pack(side="left", padx=6)
        self.apply_button = ttk.Button(controls, text="Aplicar a la selección", command=self.apply)
        self.apply_button.pack(side="left")

        legend = ttk.Frame(root, padding=(12, 0, 12, 6))
        legend.pack(fill="x")
        for name, color in LABELS.values():
            tk.Label(legend, text=name, background=color, padx=6, pady=2).pack(side="left", padx=(0, 5))

        self.canvas = tk.Canvas(root, background="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=12)
        self.canvas.bind("<Configure>", lambda event: self.draw())
        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.move_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.move_pan)
        ttk.Label(root, text="Clic para una muestra · Arrastra para un tramo · Rueda para acercar · Arrastra con botón derecho para desplazar",
                  padding=(12, 6)).pack(anchor="w")
        ttk.Label(root, textvariable=self.status, padding=(12, 0, 12, 10)).pack(anchor="w")
        self.update_controls()

    def update_controls(self, message=None):
        capture = self.capture
        self.save_button.state(["!disabled"] if capture and capture.dirty else ["disabled"])
        self.undo_button.state(["!disabled"] if capture and capture.history else ["disabled"])
        self.apply_button.state(["!disabled"] if self.selected else ["disabled"])
        self.reset_button.state(["!disabled"] if capture else ["disabled"])
        if not capture:
            return
        self.filename.set(capture.path.name + (" *" if capture.dirty else ""))
        if self.selected:
            first, last = self.selected
            selection = (f"Muestras {first + 1}–{last + 1} ({last - first + 1}) · "
                         f"{capture.times[first]:.6f}–{capture.times[last]:.6f} s")
            if first == last:
                selection += f" · {label_style(capture.labels[first])[0]}"
        else:
            selection = f"{len(capture.times):,} muestras"
        self.status.set(f"{message} · {selection}" if message else selection)

    def keep_changes(self):
        if not self.capture or not self.capture.dirty:
            return True
        answer = messagebox.askyesnocancel("Cambios pendientes", "¿Guardar los cambios en el CSV?", parent=self.root)
        return answer is False or (answer is True and self.save())

    def open(self, path=None):
        if path is None:
            filename = filedialog.askopenfilename(parent=self.root, filetypes=[("Capturas CSV", "*.csv")])
            if not filename:
                return
            path = Path(filename)
        if not self.keep_changes():
            return
        try:
            capture = Captura(path)
        except (OSError, ValueError, csv.Error) as error:
            messagebox.showerror("No se pudo abrir el CSV", str(error), parent=self.root)
            return
        self.capture = capture
        self.selected = None
        self.total = (0, max(capture.times[-1], 0.001))
        self.reset_view()
        self.update_controls()

    def close(self):
        if self.keep_changes():
            self.root.destroy()

    def apply(self):
        if self.selected is None:
            return
        label = next(key for key, (name, _) in LABELS.items() if name == self.label.get())
        self.capture.apply(*self.selected, label)
        self.update_controls()
        self.draw()

    def undo(self):
        if self.capture and self.capture.history:
            self.selected = self.capture.undo()
            self.update_controls("Cambio deshecho")
            self.draw()

    def save(self):
        if not self.capture or not self.capture.dirty:
            return True
        try:
            count = self.capture.save()
        except PermissionError:
            messagebox.showerror("No se pudo guardar", "Comprueba los permisos y cierra el CSV en Excel si está abierto.",
                                 parent=self.root)
            return False
        except (OSError, ValueError) as error:
            messagebox.showerror("No se pudo guardar", str(error), parent=self.root)
            return False
        self.update_controls(f"CSV guardado ({count} etiquetas modificadas)")
        return True

    def plot_width(self):
        return max(1, self.canvas.winfo_width() - 82)

    def time_at(self, x):
        left, right = self.view
        fraction = min(1, max(0, (x - 62) / self.plot_width()))
        return left + fraction * (right - left)

    def start_selection(self, event):
        if self.capture:
            self.anchor = self.time_at(event.x)
            self.move_selection(event)

    def move_selection(self, event):
        if self.anchor is not None:
            self.selected = self.capture.selection(self.anchor, self.time_at(event.x))
            self.update_controls()
            self.draw_selection()

    def end_selection(self, event):
        self.move_selection(event)
        self.anchor = None

    def reset_view(self):
        self.view = self.total
        self.draw()

    def set_view(self, left, width):
        left = max(0, min(left, self.total[1] - width))
        self.view = (left, left + width)
        self.draw()

    def zoom(self, event):
        if self.capture:
            left, right = self.view
            pointer = self.time_at(event.x)
            width = right - left
            new_width = min(self.total[1], max(0.0001, width * (0.8 if event.delta > 0 else 1.25)))
            self.set_view(pointer - (pointer - left) / width * new_width, new_width)

    def start_pan(self, event):
        self.pan = (event.x, *self.view)

    def move_pan(self, event):
        if self.capture and self.pan:
            x, left, right = self.pan
            width = right - left
            self.set_view(left + (x - event.x) * width / self.plot_width(), width)

    def x_at(self, time):
        left, right = self.view
        return 62 + (time - left) * self.plot_width() / (right - left)

    def draw(self):
        canvas = self.canvas
        canvas.delete("all")
        if not self.capture:
            return
        times = self.capture.times
        left, right = self.view
        first = bisect_left(times, left)
        stop = bisect_right(times, right)
        width = self.plot_width()
        scale = width / (right - left)
        height = canvas.winfo_height()
        middle = height // 2
        panels = (
            (25, middle - 14, "Aceleración |a| [g]", self.capture.acceleration),
            (middle + 25, height - 35, "Giro |ω| [°/s]", self.capture.rotation),
        )
        if any(bottom <= top for top, bottom, _, _ in panels):
            return
        labels = self.capture.labels
        run_start, run_last = self.capture.selection(left, right)
        for i in range(run_start + 1, run_last + 2):
            if i > run_last or labels[i] != labels[run_start]:
                a = 0 if not run_start else (times[run_start - 1] + times[run_start]) / 2
                b = self.total[1] if i == len(times) else (times[i - 1] + times[i]) / 2
                for top, bottom, _, _ in panels:
                    canvas.create_rectangle(62 + (max(left, a) - left) * scale, top,
                                            62 + (min(right, b) - left) * scale, bottom,
                                            fill=label_style(labels[run_start])[1], outline="")
                run_start = i

        for top, bottom, title, signal in panels:
            peak = max(signal[first:stop], default=0) or 1
            canvas.create_text(62, top - 7, text=title, anchor="sw", fill="#203449")
            for fraction in (0, 0.5, 1):
                y = bottom - (bottom - top) * fraction
                canvas.create_line(62, y, 62 + width, y, fill="#bbc6d1")
                canvas.create_text(55, y, text=f"{peak * fraction:.3g}", anchor="e", fill="#364b60")
            points = [(62 + (times[i] - left) * scale, bottom - signal[i] / peak * (bottom - top))
                      for i in range(first, stop)]
            if len(points) > 1:
                canvas.create_line(points, fill="#203449", width=1.3)
            elif points:
                x, y = points[0]
                canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#203449", outline="")
        for i in range(6):
            time = left + (right - left) * i / 5
            canvas.create_text(self.x_at(time), height - 24, text=f"{time:.4f}", fill="#364b60")
        canvas.create_text(62 + width / 2, height - 8, text="Tiempo desde el inicio [s]", fill="#364b60")
        self.draw_selection()

    def draw_selection(self):
        canvas = self.canvas
        canvas.delete("selection")
        if not self.selected:
            return
        first, last = self.selected
        times = self.capture.times
        left, right = self.view
        if times[last] < left or times[first] > right:
            return
        a = self.x_at(max(left, times[first]))
        b = self.x_at(min(right, times[last]))
        height = canvas.winfo_height()
        for top, bottom in ((25, height // 2 - 14), (height // 2 + 25, height - 35)):
            if bottom <= top:
                continue
            if b - a < 2:
                canvas.create_line(a, top, a, bottom, fill="#123d73", width=2, tags="selection")
            else:
                canvas.create_rectangle(a, top, b, bottom, outline="#123d73", width=2, tags="selection")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="?", type=Path, help="CSV de captura IoH")
    args = parser.parse_args()
    root = tk.Tk()
    app = Editor(root)
    if args.csv:
        root.after_idle(app.open, args.csv)
    root.mainloop()


if __name__ == "__main__":
    main()
