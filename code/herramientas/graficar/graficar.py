"""Graficas y resumen de los CSV de imu_terminal.py. Ver README.md."""
import argparse
import csv
from datetime import datetime
from pathlib import Path

import numpy as np

CARPETA = Path(__file__).resolve().parent
CHANNELS = ("ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps")


def cargar(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        required = {"pc_time_iso", "xiao_time_us", "sequence", *CHANNELS}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Cabecera incompatible: se espera el CSV original separado por ';'.")
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
    return values, sensor_time, pc_time, steps


def resumir(path, values, sensor_time, pc_time, steps):
    duration = sensor_time[-1]
    missing = int(np.maximum(steps - 1, 0).sum())
    duplicates = int((steps == 0).sum())
    read_hz = float(steps.sum()) / duration
    received_hz = (len(values) - 1) / duration
    dt = np.diff(sensor_time) * 1000
    # Normaliza por el salto del contador para no confundir perdidas con ODR.
    periods = dt[steps > 0] / steps[steps > 0]
    lines = [
        f"Archivo: {path.name}",
        f"Muestras: {len(values)} | Duracion XIAO: {duration:.3f} s",
        f"Frecuencia de lectura estimada: {read_hz:.2f} Hz",
        f"Muestras recibidas / tiempo XIAO: {received_hz:.2f} Hz",
        f"Saltos detectados: {missing} | Contadores repetidos: {duplicates}",
    ]
    if pc_time[-1] > 0:
        lines.append(f"Recepcion segun reloj PC: {(len(values)-1)/pc_time[-1]:.2f} Hz")
    if len(periods):
        lines.append(f"Periodo por paso del contador: mediana {np.median(periods):.3f} ms"
                     f" | desviacion {np.std(periods):.3f} ms")
    lines.append(f"Intervalo maximo entre lecturas recibidas: {dt.max():.3f} ms")
    if np.any(np.diff(pc_time) < 0):
        lines.append("AVISO: el reloj de pared del PC retrocede; su frecuencia no es fiable.")
    if duplicates or np.any(dt == 0):
        lines.append("AVISO: hay contadores o tiempos repetidos; revisa el registro.")
    lines += ["", f"{'Canal':<10} {'Media':>11} {'Desv.':>11} {'Minimo':>11} {'Maximo':>11} {'RMS':>11}"]
    for name, column in zip(CHANNELS, values.T):
        lines.append(f"{name:<10} {column.mean():11.4f} {column.std():11.4f}"
                     f" {column.min():11.4f} {column.max():11.4f}"
                     f" {np.sqrt(np.mean(column**2)):11.4f}")
    lines += ["", "Aceleracion incluye gravedad. No se ha filtrado ni calibrado la senal.",
              "La media del giro solo estima el offset si TODA la grabacion se hizo en reposo.",
              "Los saltos no detectan conversiones perdidas antes de leer la IMU.",
              "Los tiempos del PC son de recepcion; sus rafagas no implican muestreo irregular."]
    return "\n".join(lines)


def graficar(path, values, t, pc_time):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 2, figsize=(14, 10), layout="constrained")
    colors = ("#2563eb", "#ea580c", "#16a34a")
    for i, (label, color) in enumerate(zip("XYZ", colors)):
        axes[0, 0].plot(t, values[:, i], label=label, color=color, lw=0.8)
        axes[0, 1].plot(t, values[:, i+3], label=label, color=color, lw=0.8)
    axes[0, 0].set(title="Acelerometro", ylabel="Aceleracion [g]")
    axes[0, 1].set(title="Giroscopo", ylabel="Giro [grados/s]")
    axes[0, 0].legend(ncol=3)
    axes[0, 1].legend(ncol=3)
    axes[1, 0].plot(t, np.linalg.norm(values[:, :3], axis=1), color="#2563eb", lw=0.8)
    axes[1, 0].axhline(1, color="gray", ls="--", lw=0.8, label="1 g")
    axes[1, 0].set(title="Modulo de aceleracion (incluye gravedad)", ylabel="Modulo [g]")
    axes[1, 0].legend()
    axes[1, 1].plot(t, np.linalg.norm(values[:, 3:], axis=1), color="#ea580c", lw=0.8)
    axes[1, 1].set(title="Modulo de velocidad angular", ylabel="Modulo [grados/s]")
    axes[2, 0].plot(t[1:], np.diff(t)*1000, lw=0.7)
    axes[2, 0].axhline(1000/104, color="gray", ls="--", label="104 Hz nominales")
    axes[2, 0].set(title="Intervalos entre lecturas recibidas (reloj XIAO)", ylabel="Intervalo [ms]")
    axes[2, 0].legend()
    axes[2, 1].plot(t[1:], np.diff(pc_time)*1000, color="#9333ea", lw=0.7)
    axes[2, 1].set(title="Intervalos de llegada al PC (BLE)", ylabel="Intervalo [ms]")
    for axis in axes.flat:
        axis.set_xlabel("Tiempo desde primera muestra [s], reloj XIAO")
        axis.grid(alpha=0.25)
    fig.suptitle(path.name, fontsize=12)
    return fig


def guardar(path, fig, summary, values, t, pc_time):
    output = path.parent / path.stem
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "graficas.png", dpi=160)
    # Exporta tambien cada panel como imagen independiente.
    fig.canvas.draw()
    names = ("acelerometro", "giroscopo", "modulo_aceleracion",
             "modulo_giro", "intervalos_xiao", "intervalos_pc")
    for axis, name in zip(fig.axes, names):
        bounds = axis.get_tightbbox(fig.canvas.get_renderer())
        bounds = bounds.transformed(fig.dpi_scale_trans.inverted()).padded(0.1)
        fig.savefig(output / f"{name}.png", dpi=160, bbox_inches=bounds)
    (output / "resumen.txt").write_text(summary, encoding="utf-8")
    with (output / "estadisticas.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["canal", "media", "desviacion", "minimo", "maximo", "rms"])
        for name, column in zip(CHANNELS, values.T):
            writer.writerow([name, column.mean(), column.std(), column.min(), column.max(),
                             np.sqrt(np.mean(column**2))])
    with (output / "datos_analizados.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["tiempo_xiao_s", "tiempo_pc_s", *CHANNELS,
                         "modulo_aceleracion_g", "modulo_giro_dps",
                         "intervalo_xiao_ms", "intervalo_pc_ms"])
        for i, row in enumerate(values):
            writer.writerow([t[i], pc_time[i], *row, np.linalg.norm(row[:3]),
                             np.linalg.norm(row[3:]),
                             (t[i]-t[i-1])*1000 if i else "",
                             (pc_time[i]-pc_time[i-1])*1000 if i else ""])
    print(f"Analisis guardado en: {output.resolve()}")


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
    parser.add_argument("csv", nargs="*", type=Path, help="Nombres de CSV de esta carpeta; sin nombres muestra un menu.")
    parser.add_argument("--todos", action="store_true", help="Analiza todos los CSV junto al script.")
    parser.add_argument("--guardar", action="store_true", help="Compatible con versiones anteriores; ahora siempre guarda.")
    parser.add_argument("--sin-ventana", action="store_true", help="Guarda el analisis sin abrir las ventanas.")
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
                path = (CARPETA / name).resolve()
                if path.parent != CARPETA or path.suffix.lower() != ".csv":
                    raise ValueError("Solo se admiten CSV situados junto a graficar.py.")
                paths.append(path)
        else:
            paths = buscar_csv() if args.todos else elegir()
    except (ValueError, EOFError) as error:
        parser.error(str(error))
    failures = 0
    for path in paths:
        try:
            values, t, pc_time, steps = cargar(path)
            summary = resumir(path, values, t, pc_time, steps)
            print("\n" + summary + "\n")
            fig = graficar(path, values, t, pc_time)
            guardar(path, fig, summary, values, t, pc_time)
            if args.sin_ventana:
                import matplotlib.pyplot as plt
                plt.close(fig)
        except (ValueError, OSError) as error:
            failures += 1
            print(f"ERROR en {path}: {error}")
    if not args.sin_ventana:
        import matplotlib.pyplot as plt
        plt.show()
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
