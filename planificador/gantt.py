import pandas as pd
import plotly.graph_objects as go

from planificador.constantes import COLOR_INACTIVO, PALETA


def color_de(pid):
    if pid == 0:
        return COLOR_INACTIVO
    return PALETA[(pid - 1) % len(PALETA)]


def tabla_tareas(tareas):
    tabla = pd.DataFrame(tareas, columns=["pid", "llegada", "ejecucion", "prioridad"])

    def pintar(columna):
        if columna.name != "pid":
            return [""] * len(columna)
        return [
            f"background-color: {color_de(int(valor))}; color: #fffdf8; font-weight: 600"
            for valor in columna
        ]

    return tabla.style.apply(pintar, axis=0)


def recortar(tramos, reloj):
    visibles = []
    for tramo in tramos:
        if tramo["inicio"] >= reloj:
            continue
        visible = dict(tramo)
        visible["fin"] = min(tramo["fin"], reloj)
        if visible["fin"] > visible["inicio"]:
            visibles.append(visible)
    return visibles


def linea_estado(tramos, reloj, procesadores, segundos):
    partes = [f"t = {reloj} ({reloj * segundos:g} s)"]
    for cpu in range(1, procesadores + 1):
        nombre = "—"
        if reloj > 0:
            nombre = "libre"
            for tramo in tramos:
                if tramo["cpu"] == cpu and tramo["inicio"] < reloj <= tramo["fin"]:
                    nombre = "inactivo" if tramo["pid"] == 0 else tramo["nombre"]
                    break
        partes.append(f"CPU {cpu}: {nombre}")
    return " · ".join(partes)


def figura_gantt(tramos, procesadores, segundos, reloj):
    cpus = [f"CPU {indice}" for indice in range(1, procesadores + 1)]
    figura = go.Figure()
    for cpu in cpus:
        figura.add_trace(
            go.Scatter(
                x=[0],
                y=[cpu],
                mode="markers",
                marker_opacity=0,
                hoverinfo="skip",
                showlegend=False,
            )
        )
    for tramo in tramos:
        inicio_s = tramo["inicio"] * segundos
        fin_s = tramo["fin"] * segundos
        figura.add_trace(
            go.Bar(
                orientation="h",
                y=[f"CPU {tramo['cpu']}"],
                x=[tramo["fin"] - tramo["inicio"]],
                base=[tramo["inicio"]],
                marker_color=color_de(tramo["pid"]),
                marker_line_width=0,
                hovertext=(
                    f"CPU {tramo['cpu']} · {tramo['nombre']}: "
                    f"{tramo['inicio']}–{tramo['fin']} u · {inicio_s:g}–{fin_s:g} s"
                ),
                hoverinfo="text",
                showlegend=False,
                name=tramo["nombre"],
            )
        )
    if reloj > 0:
        figura.add_vline(x=reloj, line_width=1, line_dash="dot", line_color="#8a3b22")
    fin_eje = max([reloj, *[tramo["fin"] for tramo in tramos]], default=1)
    figura.update_layout(
        barmode="overlay",
        height=max(180, 78 + 46 * procesadores),
        margin=dict(l=8, r=8, t=8, b=8),
        plot_bgcolor="#fffdf8",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1c1915"),
        xaxis=dict(
            title=f"Tiempo (1 u = {segundos:g} s)",
            dtick=1 if fin_eje <= 30 else None,
            gridcolor="#eee6d8",
            zeroline=False,
            range=[0, max(fin_eje, 1)],
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=list(reversed(cpus)),
            fixedrange=True,
        ),
    )
    return figura
