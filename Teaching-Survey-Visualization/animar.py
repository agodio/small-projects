import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

# --------------------------------------------------
# Leer CSV
# --------------------------------------------------

df = pd.read_csv(
    "datos.csv",
    sep=None,
    engine="python",
    encoding="utf-8-sig",
)

df.columns = df.columns.str.strip()

columnas = [
    "Período",
    "Desempeño Didáctico",
    "Valores",
    "Gestión de la materia",
    "Satisfacción General",
    "Rol",
]

faltantes = [c for c in columnas if c not in df.columns]
if faltantes:
    raise ValueError(f"Faltan columnas en datos.csv: {faltantes}")

df = df.dropna(subset=columnas).reset_index(drop=True)

periods = df["Período"].astype(str).tolist()
roles = df["Rol"].astype(str).tolist()

didactico = df["Desempeño Didáctico"].astype(float).tolist()
valores = df["Valores"].astype(float).tolist()
gestion = df["Gestión de la materia"].astype(float).tolist()
satisfaccion = df["Satisfacción General"].astype(float).tolist()

n = len(periods)

if n < 2:
    raise ValueError("Se necesitan al menos dos períodos.")

# --------------------------------------------------
# Colores
# --------------------------------------------------

role_colors = {
    "ATP": "#8ecae6",
    "JTP": "#b8a1e3",
    "PRM": "#8ac9a7",
    "Responsable": "#8ac9a7",
}

color_didactico = "#2878b5"
color_valores = "#e07a28"
color_gestion = "#299d8f"
color_satisfaccion = "#c65373"

# --------------------------------------------------
# Agrupar períodos consecutivos con el mismo rol
# --------------------------------------------------

segments = []
start = 0

for j in range(1, n + 1):
    if j == n or roles[j] != roles[start]:
        segments.append((start, j - 1, roles[start]))
        start = j

# --------------------------------------------------
# Figura: dos gráficos alineados
# --------------------------------------------------

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(15, 9),
    sharex=True,
    gridspec_kw={"height_ratios": [1, 1], "hspace": 0.12},
)

fig.suptitle(
    "Evolución de las encuestas docentes",
    fontsize=18,
    fontweight="bold",
)

ax1.set_xlim(-0.5, n - 0.5)
ax1.set_xticks(range(n))

# Solo el gráfico inferior muestra las etiquetas del eje X.
ax1.tick_params(axis="x", labelbottom=False)

ax2.set_xticks(range(n))
ax2.set_xticklabels(periods, rotation=45, ha="right")
ax2.set_xlabel("Período")

for ax in (ax1, ax2):
    ax.set_ylim(0, 10)
    ax.set_yticks(range(11))
    ax.set_ylabel("Puntaje")
    ax.set_axisbelow(True)
    ax.grid(True, axis="y", alpha=0.3)

# --------------------------------------------------
# Gráfico superior: evaluación individual
# --------------------------------------------------

ax1.set_title(
    "Evaluación individual",
    loc="center",
    fontweight="bold",
    fontsize=15,
)

line1, = ax1.plot(
    [], [],
    marker="o",
    linewidth=2,
    color=color_didactico,
    label="Desempeño Didáctico",
    zorder=3,
)

line2, = ax1.plot(
    [], [],
    marker="o",
    linewidth=2,
    color=color_valores,
    label="Valores",
    zorder=3,
)

ax1.legend(
    loc="lower right", ncol=2, fontsize=16,
    framealpha=0.95, facecolor="white",
)

# --------------------------------------------------
# Gráfico inferior: evaluación global de la materia
# --------------------------------------------------

ax2.set_title(
    "Evaluación global de la materia",
    loc="center",
    fontweight="bold",
    fontsize=15,
)

line3, = ax2.plot(
    [], [],
    marker="o",
    linewidth=2,
    color=color_gestion,
    label="Gestión de la materia",
    zorder=5,
)

line4, = ax2.plot(
    [], [],
    marker="o",
    linewidth=2,
    color=color_satisfaccion,
    label="Satisfacción General",
    zorder=5,
)

ax2.legend(
    loc="lower right", ncol=2, fontsize=16,
    framealpha=0.95, facecolor="white",
)

# --------------------------------------------------
# Franja de roles dentro del gráfico inferior
# Se dibuja entre y=2 e y=3, por encima de las curvas.
# --------------------------------------------------

role_bars = []
role_y = 2.5

for start_idx, end_idx, role in segments:
    bar, = ax2.plot(
        [], [],
        linewidth=15,
        solid_capstyle="butt",
        color=role_colors.get(role, "#cccccc"),
        clip_on=True,
        zorder=3,
    )

    label = ax2.text(
        0, role_y, "",
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        color="#202020",
        clip_on=True,
        zorder=4,
    )

    role_bars.append((start_idx, end_idx, role, bar, label))

# Marcar el comienzo de PRM y mostrar una anotación breve al llegar a ese punto.
responsable_indices = [
    i for i, role in enumerate(roles)
    if role in ("PRM", "Responsable")
]
annotation = None
inicio_responsable = None

if responsable_indices:
    inicio_responsable = responsable_indices[0]
    x_cambio = inicio_responsable - 0.5

    for ax in (ax1, ax2):
        ax.axvline(
            x_cambio,
            color="#555555",
            linestyle="--",
            linewidth=1.4,
            alpha=0.8,
            zorder=6,
        )

    annotation = ax2.annotate(
        "Asumo la responsabilidad",
        xy=(x_cambio, 8.0),
        xytext=(x_cambio + 0.25, 7.35),
        textcoords="data",
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="#444444",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9, "pad": 3},
        arrowprops={
            "arrowstyle": "->",
            "color": "#555555",
            "lw": 1.2,
            "connectionstyle": "arc3,rad=0.08",
        },
        zorder=7,
    )
    annotation.set_visible(False)

# --------------------------------------------------
# Animación
# --------------------------------------------------

frames = 240
fps = 30


def update(frame):
    progress = frame / (frames - 1) * (n - 1)

    last = int(progress)
    fraction = progress - last

    x = list(range(last + 1))

    y1 = didactico[:last + 1]
    y2 = valores[:last + 1]
    y3 = gestion[:last + 1]
    y4 = satisfaccion[:last + 1]

    # Interpolar el punto que se está dibujando
    if last < n - 1:
        x.append(progress)

        y1.append(
            didactico[last]
            + fraction * (didactico[last + 1] - didactico[last])
        )

        y2.append(
            valores[last]
            + fraction * (valores[last + 1] - valores[last])
        )

        y3.append(
            gestion[last]
            + fraction * (gestion[last + 1] - gestion[last])
        )

        y4.append(
            satisfaccion[last]
            + fraction * (
                satisfaccion[last + 1] - satisfaccion[last]
            )
        )

    line1.set_data(x, y1)
    line2.set_data(x, y2)
    line3.set_data(x, y3)
    line4.set_data(x, y4)

    # Dibujar las franjas de roles sin huecos.
    # La barra empieza en el borde izquierdo del primer período
    # y termina en el borde derecho del último período del rol.
    for start_idx, end_idx, role, bar, label in role_bars:

        if progress < start_idx:
            bar.set_data([], [])
            label.set_text("")
            continue

        visible_end = min(progress, end_idx)

        left = start_idx - 0.5
        right = visible_end + 0.5

        bar.set_data(
            [left, right],
            [role_y, role_y],
        )

        center = (left + right) / 2
        label.set_position((center, role_y))

        if right - left >= 0.8:
            label.set_text(role)
        else:
            label.set_text("")

    if annotation is not None:
        annotation.set_visible(progress >= inicio_responsable)

    return (
        line1,
        line2,
        line3,
        line4,
        *([annotation] if annotation is not None else []),
        *[
            item
            for _, _, _, bar, label in role_bars
            for item in (bar, label)
        ],
    )


ani = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=1000 / fps,
    blit=False,
)

# --------------------------------------------------
# Guardar video
# --------------------------------------------------

writer = FFMpegWriter(
    fps=fps,
    bitrate=3000,
)

ani.save("evolucion.mp4", writer=writer)

plt.close(fig)

print("Video generado: evolucion.mp4")

