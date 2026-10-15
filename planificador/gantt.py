import pandas as pd
import plotly.graph_objects as go

from planificador.constantes import COLOR_INACTIVO, PALETA


def color_de(pid):
    if pid == 0:
        return COLOR_INACTIVO
    return PALETA[(pid - 1) % len(PALETA)]


def cierre_de(tramos):
    fines = {}
    for tramo in tramos:
        if tramo["pid"] == 0:
            continue
        fines[tramo["pid"]] = max(fines.get(tramo["pid"], 0), tramo["fin"])
    return fines


def tabla_tareas(tareas, tramos=None, reloj=None):
    fines = cierre_de(tramos or [])
    filas = []
    for tarea in tareas:
        fin = fines.get(tarea["pid"])
        espera = None if fin is None else fin - tarea["llegada"] - tarea["ejecucion"]
        termino = ""
        if fin is not None and reloj is not None:
            termino = "SI" if reloj >= fin else "NO"
        filas.append(
            {
                "PID": tarea["pid"],
                "T.ll": tarea["llegada"],
                "T.exe": tarea["ejecucion"],
                "Prioridad": tarea["prioridad"],
                "FIN": termino,
                "T.Fin": "" if fin is None else fin,
                "T.Esp": "" if espera is None else espera,
            }
        )
    tabla = pd.DataFrame(filas, columns=["PID", "T.ll", "T.exe", "Prioridad", "FIN", "T.Fin", "T.Esp"])

    def pintar(columna):
        if columna.name != "PID":
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
        height=max(260, 150 + 52 * procesadores),
        margin=dict(l=56, r=24, t=28, b=72),
        plot_bgcolor="#fffdf8",
        paper_bgcolor="#fffdf8",
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
