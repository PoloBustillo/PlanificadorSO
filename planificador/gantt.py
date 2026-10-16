from html import escape

import pandas as pd
import plotly.graph_objects as go

from planificador.constantes import COLOR_INACTIVO, PALETA
from planificador.csv_tareas import COLUMNAS, filas_tareas


def color_de(pid):
    if pid == 0:
        return COLOR_INACTIVO
    return PALETA[(pid - 1) % len(PALETA)]


def tabla_tareas(tareas, tramos=None, reloj=None):
    tabla = pd.DataFrame(filas_tareas(tareas, tramos, reloj), columns=COLUMNAS)

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
                marker_line=dict(width=3, color="#fffdf8"),
                text=["" if tramo["pid"] == 0 else tramo["nombre"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#fffdf8", size=12),
                hovertext=(
                    f"CPU {tramo['cpu']} · {tramo['nombre']}: "
                    f"{tramo['inicio']}–{tramo['fin']} u · {inicio_s:g}–{fin_s:g} s"
                ),
                hoverinfo="text",
                showlegend=False,
                name=tramo["nombre"],
                cliponaxis=False,
            )
        )
    if reloj > 0:
        figura.add_vline(x=reloj, line_width=1, line_dash="dot", line_color="#8a3b22")
    fin_eje = max([reloj, *[tramo["fin"] for tramo in tramos]], default=1)
    figura.update_layout(
        barmode="overlay",
        uniformtext=dict(minsize=9, mode="hide"),
        height=max(260, 150 + 52 * procesadores),
        margin=dict(l=56, r=24, t=28, b=96),
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


def _chip(pid, etiqueta, detalle, destacado=False, acento="#c4532a"):
    borde = acento if destacado else "#e7dccb"
    sombra = (
        "box-shadow:0 0 0 3px rgba(196,83,42,.16);"
        if destacado and acento == "#c4532a"
        else "box-shadow:0 0 0 3px rgba(36,91,134,.18);"
        if destacado
        else "box-shadow:0 1px 2px rgba(28,25,21,.05);"
    )
    marca = (
        f"<span style='color:{acento};font-size:.68rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase'>{escape(etiqueta)}</span>"
        if etiqueta
        else ""
    )
    return (
        "<div style='display:flex;align-items:center;gap:.5rem;background:#fff;border:1px solid "
        f"{borde};border-radius:14px;padding:.35rem .65rem .35rem .35rem;{sombra}'>"
        f"<span style='background:{color_de(pid)};color:#fffdf8;font-weight:700;border-radius:10px;"
        f"min-width:2.35rem;text-align:center;padding:.38rem .4rem;font-size:.92rem'>{escape(f'P{pid}')}</span>"
        "<span style='display:flex;flex-direction:column;line-height:1.2;gap:.05rem'>"
        f"{marca}"
        f"<span style='color:#1c1915;font-size:.78rem'>{escape(detalle)}</span>"
        "</span></div>"
    )


def _vacio(texto):
    return (
        "<div style='color:#8a8175;font-size:.84rem;border:1px dashed #e7dccb;border-radius:14px;"
        f"padding:.85rem .8rem;width:100%'>{escape(texto)}</div>"
    )


def panel_cola(titulo, ayuda, acento, fichas, vacio):
    cuerpo = "".join(fichas) if fichas else _vacio(vacio)
    return (
        "<section style='background:#fffdf8;border:1px solid #e7dccb;border-top:4px solid "
        f"{acento};border-radius:18px;padding:.85rem .9rem 1.45rem;min-height:158px;margin-bottom:1.15rem'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;gap:.5rem'>"
        f"<strong style='color:#1c1915;font-size:1.02rem'>{escape(titulo)}</strong>"
        "<span style='background:#1c1915;color:#fffdf8;border-radius:999px;min-width:1.6rem;"
        f"text-align:center;padding:.08rem .5rem;font-size:.75rem;font-weight:700'>{len(fichas)}</span>"
        "</div>"
        f"<div style='color:#6f675e;font-size:.78rem;margin:.2rem 0 .7rem'>{escape(ayuda)}</div>"
        f"<div style='display:flex;flex-wrap:wrap;gap:.45rem'>{cuerpo}</div>"
        "</section>"
    )


def fichas_listos(listos):
    fichas = []
    for indice, tarea in enumerate(listos):
        puesto = f"{indice + 1}º · " if indice else ""
        fichas.append(
            _chip(
                tarea["pid"],
                "Sigue" if indice == 0 else "",
                f"{puesto}exe {tarea['ejecucion']} · pri {tarea['prioridad']}",
                destacado=indice == 0,
            )
        )
    return fichas


def fichas_espera(espera, reloj):
    fichas = []
    for tarea, tramo in espera:
        falta = tramo["fin"] - reloj
        fichas.append(
            _chip(
                tarea["pid"],
                f"CPU {tramo['cpu']}",
                f"acaba en {tramo['fin']} · falta {falta}",
                destacado=True,
                acento="#245b86",
            )
        )
    return fichas
