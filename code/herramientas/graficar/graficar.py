"""Gráficas de movimiento y frecuencia de recepción de los CSV de la IMU."""
import argparse
import csv
from datetime import datetime
from pathlib import Path
import re

import numpy as np

CARPETA = Path(__file__).resolve().parent
CHANNELS = ("ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps")


def cargar(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        required = {"pc_time_iso", "xiao_time_us", "sequence", *CHANNELS}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Cabecera incompatible: se espera el CSV original separado por ';'.")
        has_labels = "label" in reader.fieldnames
        rows = list(reader)
    if len(rows) < 2:
        raise ValueError("Se necesitan al menos dos muestras.")
    try:
        raw_time = np.array([int(r["xiao_time_us"]) for r in rows], dtype=np.int64)
        seq = np.array([int(r["sequence"]) for r in rows], dtype=np.int64)
        values = np.array([[float(r[c]) for c in CHANNELS] for r in rows])
        pc = [datetime.fromisoformat(r["pc_time_iso"]) for r in rows]
        pc_time = np.array([(t - pc[0]).total_seconds() for t in pc])
    except (ValueError, TypeError, KeyError) as error:
        raise ValueError(f"Fila incompleta o valor invalido: {error}") from error
    if not np.isfinite(values).all():
        raise ValueError("La senal contiene NaN o infinito.")
    if np.any((raw_time < 0) | (raw_time > 0xFFFFFFFF)) or np.any((seq < 0) | (seq > 65535)):
        raise ValueError("Tiempo o contador fuera del rango del protocolo.")
    # Diferencias modulares: admite rollover de micros() y del contador uint16.
    delta_us = np.diff(raw_time) % (2**32)
    steps = np.diff(seq) % 65536
    if np.any(delta_us > 2**31) or np.any(steps > 32768):
        raise ValueError("Posible reinicio de la XIAO o muestras desordenadas; separa las sesiones.")
    sensor_time = np.r_[0, np.cumsum(delta_us)] / 1e6
    if sensor_time[-1] <= 0:
        raise ValueError("Los tiempos de la XIAO no avanzan.")
    labels = [((row.get("label") or "").strip().lower() or "undefined") for row in rows]
    return values, sensor_time, pc_time, labels if has_labels else None


GESTURES = {
    "pase": ("Pase", "#007b92"),
    "recepcion": ("Recepción", "#167d49"),
    "tiro": ("Tiro de muñeca", "#b15b00"),
    "manejo": ("Manejo", "#9d3a8e"),
    "reposo": ("Reposo", "#355bc4"),
}
SIGNALS = ("Aceleración [g]", "Velocidad angular [°/s]")
COLORS = ("#215fa6", "#9d3a53", "#15765d", "#ad620f", "#7447a5", "#237a83")


def nombre_corto(path):
    return re.sub(r"_\d{8}_\d{6}_\d{6}_[0-9a-f]{8}$", "", path.stem, flags=re.I)


def tramos(labels):
    if labels is None:
        return
    start = 0
    for stop in range(1, len(labels) + 1):
        if stop == len(labels) or labels[stop] != labels[start]:
            if labels[start] in GESTURES:
                yield labels[start], slice(start, stop)
            start = stop


def magnitudes(values):
    return np.column_stack((
        np.linalg.norm(values[:, :3], axis=1),
        np.linalg.norm(values[:, 3:], axis=1),
    ))


def estilo(axis):
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#a7b2c0")
    axis.grid(axis="y", color="#dae2eb", linewidth=0.7)
    axis.set_axisbelow(True)


def marcar_tramos(axes, t, labels):
    from matplotlib.patches import Patch

    visible = set()
    for label, span in tramos(labels):
        _, color = GESTURES[label]
        left = t[span.start]
        right = t[min(span.stop, len(t) - 1)]
        for axis in axes:
            axis.axvspan(left, right, color=color, alpha=0.14, linewidth=0)
        visible.add(label)
    if visible:
        handles = [Patch(facecolor=color, alpha=0.35, label=name)
                   for label, (name, color) in GESTURES.items() if label in visible]
        axes[0].legend(handles=handles, loc="upper right", title="Etiquetas de teclado", framealpha=1)
    else:
        note = "CSV sin etiquetas" if labels is None else "Sin tramos de gesto etiquetados"
        axes[0].set_title(note, loc="right", fontsize=9, color="#46566a")


def movimiento(path, values, t, labels, ejes=False):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(11, 6), layout="constrained")
    title = "Movimiento por eje" if ejes else "Magnitud del movimiento"
    fig.suptitle(f"{title} · {nombre_corto(path)}", fontsize=14, fontweight="bold")
    mod = magnitudes(values) if not ejes else None
    for i, axis in enumerate(axes):
        estilo(axis)
        axis.set_ylabel(SIGNALS[i])
        if ejes:
            for j, name in enumerate("XYZ"):
                axis.plot(t, values[:, 3*i+j], label=name, color=COLORS[j], lw=0.85)
            axis.legend(ncols=3, loc="upper left", framealpha=1)
            if i == 0:
                axis.add_artist(axis.get_legend())
        else:
            axis.plot(t, mod[:, i], color=COLORS[i], lw=0.95)
            axis.set_ylim(bottom=0)
            if i == 0:
                axis.axhline(1, color="#627085", linestyle="--", lw=0.75)
        axis.margins(x=0)
    marcar_tramos(axes, t, labels)
    axes[-1].set_xlabel("Tiempo desde el inicio [s] · reloj de la XIAO")
    axes[0].set_title("La aceleración incluye gravedad", loc="left", fontsize=9, color="#46566a")
    return fig


def aceleracion_por_eje(path, values, t, labels):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, sharex=True, sharey=True, figsize=(11, 7.5),
                             layout="constrained")
    fig.suptitle(f"Aceleración por eje · {nombre_corto(path)}", fontsize=14, fontweight="bold")
    limit = max(1.0, float(np.abs(values[:, :3]).max())) * 1.05
    for i, (axis, name) in enumerate(zip(axes, "XYZ")):
        estilo(axis)
        axis.axhline(0, color="#627085", lw=0.7)
        axis.plot(t, values[:, i], color=COLORS[i], lw=0.9)
        axis.set_ylabel(f"{name} [g]")
        axis.margins(x=0)
    axes[0].set_ylim(-limit, limit)
    marcar_tramos(axes, t, labels)
    axes[0].set_title("Escala común · la aceleración incluye gravedad", loc="left",
                      fontsize=9, color="#46566a")
    axes[-1].set_xlabel("Tiempo desde el inicio [s] · reloj de la XIAO")
    return fig


def frecuencia_media(pc_time):
    if pc_time[-1] > 0 and np.all(np.diff(pc_time) >= 0):
        return (len(pc_time) - 1) / pc_time[-1]
    return None


def frecuencia(path, pc_time):
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(10, 3.4), layout="constrained")
    fig.suptitle(f"Frecuencia de recepción · {nombre_corto(path)}", fontsize=14, fontweight="bold")
    estilo(axis)
    axis.set(xlabel="Tiempo desde la primera llegada al PC [s]", ylabel="Frecuencia [Hz]")
    mean_hz = frecuencia_media(pc_time)
    if mean_hz is None:
        axis.text(0.5, 0.5, "El reloj del PC no permite estimar una frecuencia fiable.",
                  transform=axis.transAxes, ha="center", va="center")
        return fig

    # Ventanas completas de un segundo a partir de la primera llegada,
    # que fija el origen del reloj.
    full_seconds = int(pc_time[-1])
    if full_seconds:
        edges = np.arange(full_seconds + 1)
        counts = np.diff(np.searchsorted(pc_time[1:], edges, side="left"))
        axis.stairs(counts, edges, baseline=None, lw=1.55,
                    color=COLORS[0], label="Llegadas por segundo")
    axis.axhline(mean_hz, color=COLORS[1], ls="--", lw=1.25, label=f"Media: {mean_hz:.1f} Hz")
    axis.set(xlim=(0, pc_time[-1]), ylim=(0, None))
    axis.legend(loc="lower right", framealpha=1)
    return fig


def tabla_senales(values, t):
    lines = [
        "| Señal | Mín. | Máx. | Media | Desv. estándar | RMS | P95 absoluto | t del pico [s] |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    names = [*(f"Aceleración {axis} [g]" for axis in "XYZ"),
             *(f"Velocidad angular {axis} [°/s]" for axis in "XYZ"),
             "Magnitud de aceleración [g]", "Magnitud de velocidad angular [°/s]"]
    signals = np.column_stack((values, magnitudes(values)))
    for name, signal in zip(names, signals.T):
        absolute = np.abs(signal)
        stats = (signal.min(), signal.max(), signal.mean(), signal.std(),
                 np.sqrt(np.mean(signal**2)), np.percentile(absolute, 95),
                 t[absolute.argmax()])
        lines.append(f"| {name} | " + " | ".join(f"{value:.3f}" for value in stats) + " |")
    return lines


def formato_hz(pc_time):
    hz = frecuencia_media(pc_time)
    return f"{hz:.2f} Hz" if hz is not None else "No estimable"


def guardar_resumen(path, output, values, t, pc_time, labels):
    lines = [
        f"# {nombre_corto(path)}", "",
        f"CSV de origen: `{path.name}`", "",
        "[Aceleración X/Y/Z](aceleracion_xyz.png) · [Magnitudes](movimiento.png) · "
        "[Ejes de aceleración y giro](ejes.png) · [Frecuencia](frecuencia_recepcion.png)", "",
        f"- Duración en el reloj de la XIAO: **{t[-1]:.2f} s**",
        f"- Frecuencia media de recepción: **{formato_hz(pc_time)}**", "",
        "## Captura completa", "",
        *tabla_senales(values, t), "",
    ]
    if labels is not None:
        labels = np.asarray(labels)
        durations = np.diff(t, append=t[-1])
        lines += ["## Por etiqueta", "",
                  "La duración suma los intervalos que empiezan en cada muestra etiquetada.", ""]
        for label in sorted(set(labels)):
            mask = labels == label
            title = GESTURES[label][0] if label in GESTURES else label
            lines += [f"### {title} · {durations[mask].sum():.2f} s", "",
                      *tabla_senales(values[mask], t[mask]), ""]
    lines += [
        "El tiempo del pico indica el instante del mayor valor absoluto, medido desde el inicio de la prueba.",
        "El P95 del valor absoluto describe la intensidad habitual de los valores altos sin depender de un solo pico.",
        "La aceleración incluye gravedad. La velocidad angular mide el giro del palo.", "",
    ]
    (output / "resumen.md").write_text("\n".join(lines), encoding="utf-8")


def guardar_indice(capturas, output):
    lines = [
        "# Resumen de las pruebas", "",
        "| Prueba | Duración [s] | Recepción | Pico abs. X [g] | Pico abs. Y [g] | Pico abs. Z [g] | Pico de aceleración [g] | Pico de giro [°/s] |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for path, values, t, _, pc_time, folder in capturas:
        if not folder.resolve().is_relative_to(output.resolve()):
            # Las rutas explícitas pueden apuntar a carpetas o unidades distintas.
            link = (folder.resolve() / "resumen.md").as_uri()
        else:
            link = (folder.resolve() / "resumen.md").relative_to(output.resolve()).as_posix()
            link = link.replace(" ", "%20").replace("#", "%23")
        x, y, z = np.abs(values[:, :3]).max(axis=0)
        accel, gyro = magnitudes(values).max(axis=0)
        lines.append(f"| [{nombre_corto(path)}]({link}) | {t[-1]:.2f} | {formato_hz(pc_time)} | "
                     f"{x:.2f} | {y:.2f} | {z:.2f} | {accel:.2f} | {gyro:.1f} |")
    lines += ["", "Los picos corresponden a la captura completa. Abre cada prueba para ver el desglose por etiqueta.", ""]
    (output / "resumen_pruebas.md").write_text("\n".join(lines), encoding="utf-8")


def comparar(capturas):
    import matplotlib.pyplot as plt

    grouped = {}
    for index, (_, values, t, labels, _, _) in enumerate(capturas):
        mod = magnitudes(values)
        for gesture, span in tramos(labels):
            grouped.setdefault((gesture, index), []).append((t[span] - t[span.start], mod[span]))
    if not grouped:
        return None

    rows = sorted(grouped, key=lambda pair: (list(GESTURES).index(pair[0]), pair[1]))
    fig, axes = plt.subplots(len(rows), 2, squeeze=False, sharex=True, sharey="col",
                             figsize=(12, 2.35*len(rows) + 1.1), layout="constrained")
    fig.suptitle("Comparación de tramos etiquetados", fontsize=15, fontweight="bold")
    for row, (gesture, index) in enumerate(rows):
        name = nombre_corto(capturas[index][0]).replace("_", " ")
        for column, axis in enumerate(axes[row]):
            estilo(axis)
            for elapsed, mod in grouped[gesture, index]:
                axis.plot(elapsed, mod[:, column], color=COLORS[index % len(COLORS)],
                          alpha=0.66, lw=0.95, marker="o" if len(elapsed) == 1 else None,
                          markersize=3)
            if column == 0:
                axis.set_title(f"{GESTURES[gesture][0]} · {name}", loc="left", fontsize=9)
            axis.set_ylabel(SIGNALS[column])
            axis.margins(x=0.01)
    for axis in axes[-1]:
        axis.set_ylim(bottom=0)
        axis.set_xlabel("Tiempo desde el inicio de la etiqueta [s]")
    return fig


def guardar(fig, path, sin_ventana):
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, facecolor="white")
    if sin_ventana:
        plt.close(fig)


def buscar_csv():
    # Solo CSV junto al script: no busca fuera ni dentro de subcarpetas.
    files = sorted(CARPETA.glob("*.csv"))
    if not files:
        raise ValueError(f"No hay CSV en {CARPETA}. Coloca los registros junto a graficar.py.")
    return files


def elegir():
    files = buscar_csv()
    for index, path in enumerate(files, 1):
        print(f"{index:3d}. {path.name}")
    selected = input("Numero de archivo, T = todos (Enter = ultimo): ").strip()
    if selected.lower() in ("t", "todos"):
        return files
    number = int(selected) if selected else len(files)
    if not 1 <= number <= len(files):
        raise ValueError("Numero fuera de la lista.")
    return [files[number-1]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="*", type=Path, help="Rutas de CSV; sin rutas muestra un menú de archivos locales.")
    parser.add_argument("--todos", action="store_true", help="Analiza todos los CSV junto al script.")
    parser.add_argument("--guardar", action="store_true", help="Compatible con versiones anteriores; ahora siempre guarda.")
    parser.add_argument("--sin-ventana", action="store_true", help="Guarda el analisis sin abrir las ventanas.")
    parser.add_argument("--salida", type=Path, help="Carpeta para los resultados; cada captura tendrá su subcarpeta.")
    parser.add_argument("--solo-frecuencia", action="store_true", help="Genera únicamente la frecuencia de recepción.")
    args = parser.parse_args()
    if args.todos and args.csv:
        parser.error("Usa rutas concretas o --todos, no ambas opciones.")
    if args.sin_ventana:
        import matplotlib
        matplotlib.use("Agg")
    try:
        if args.csv:
            paths = []
            for name in args.csv:
                path = name.resolve() if name.exists() or name.parent != Path(".") else CARPETA / name
                if path.suffix.lower() != ".csv":
                    raise ValueError(f"Se esperaba un archivo CSV: {name}")
                paths.append(path)
        else:
            paths = buscar_csv() if args.todos else elegir()
    except (ValueError, EOFError) as error:
        parser.error(str(error))
    if args.salida and len({path.stem.casefold() for path in paths}) != len(paths):
        parser.error("Hay capturas con el mismo nombre. Analízalas por separado para mantener sus gráficas.")

    failures = 0
    captures = []
    for path in paths:
        try:
            values, t, pc_time, labels = cargar(path)
            output = (args.salida or path.parent) / path.stem
            if not args.solo_frecuencia:
                guardar(movimiento(path, values, t, labels), output / "movimiento.png", args.sin_ventana)
                guardar(movimiento(path, values, t, labels, ejes=True), output / "ejes.png", args.sin_ventana)
                guardar(aceleracion_por_eje(path, values, t, labels),
                        output / "aceleracion_xyz.png", args.sin_ventana)
                guardar_resumen(path, output, values, t, pc_time, labels)
                captures.append((path, values, t, labels, pc_time, output))
            guardar(frecuencia(path, pc_time), output / "frecuencia_recepcion.png", args.sin_ventana)
            print(f"Gráficas: {output.resolve()}")
        except (ValueError, OSError) as error:
            failures += 1
            print(f"ERROR en {path}: {error}")

    if captures:
        source = captures[0][0]
        output = args.salida or source.parent
        if len(captures) > 1:
            try:
                guardar_indice(captures, output)
            except OSError as error:
                failures += 1
                print(f"ERROR al guardar el índice: {error}")
        fig = comparar(captures)
        if fig is not None:
            if len(captures) == 1:
                output /= source.stem
            try:
                target = output / "comparacion_gestos.png"
                guardar(fig, target, args.sin_ventana)
                print(f"Comparación: {target.resolve()}")
            except OSError as error:
                failures += 1
                print(f"ERROR al guardar la comparación: {error}")
    if not args.sin_ventana:
        import matplotlib.pyplot as plt
        plt.show()
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
