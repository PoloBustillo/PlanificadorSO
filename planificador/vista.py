import time

import streamlit as st
from streamlit_sortables import sort_items

from planificador.constantes import CRITERIOS, ESTILO_ORDEN, ID_A_NOMBRE, NOMBRE_A_ID, VELOCIDAD
from planificador.csv_tareas import entero, leer_csv, plantilla_csv, tareas_a_csv
from planificador.gantt import figura_gantt, linea_estado, recortar, tabla_tareas
from planificador.motor import planificar
from planificador.sesion import (
    cargar_ejemplo,
    iniciar,
    reiniciar_reloj,
    siguiente_pid,
    sincronizar_activos,
    vaciar_tareas,
    vigilar_reloj,
)


def criterios():
    with st.container(border=True):
        st.subheader("Criterios")
        st.caption("Arrastra los criterios encendidos")
        st.pills(
            "Criterios",
            [criterio["nombre"] for criterio in CRITERIOS],
            selection_mode="multi",
            key="activos",
            on_change=sincronizar_activos,
            label_visibility="collapsed",
        )
        orden = list(st.session_state.orden)
        if not orden:
            st.caption("Enciende al menos un criterio.")
            return
        lista, resumen = st.columns([1.4, 2], vertical_alignment="center")
        with lista:
            if len(orden) == 1:
                st.write(ID_A_NOMBRE[orden[0]])
            else:
                nombres = [ID_A_NOMBRE[criterio] for criterio in orden]
                resultado = sort_items(
                    nombres,
                    direction="horizontal",
                    key="orden-" + "-".join(sorted(orden)),
                    custom_style=ESTILO_ORDEN,
                )
                if isinstance(resultado, list) and set(resultado) == set(nombres):
                    orden = [NOMBRE_A_ID[nombre] for nombre in resultado]
                    st.session_state.orden = orden
        with resumen:
            st.markdown("**" + " → ".join(ID_A_NOMBRE[criterio] for criterio in orden) + "**")


@st.dialog("Importar tareas")
def dialogo_importar():
    st.caption("Se usan PID, T.ll, T.exe y Prioridad. FIN, T.Fin y T.Esp se calculan; si vienen en el archivo, se ignoran.")
    archivo = st.file_uploader("CSV", type=["csv"], key="archivo_csv")
    if archivo is None:
        return
    try:
        vista = leer_csv(archivo.getvalue())
    except ValueError as error:
        st.error(str(error))
        return
    st.dataframe(tabla_tareas(vista), hide_index=True, width="stretch")
    if st.button("Usar estas tareas", width="stretch"):
        st.session_state.tareas = vista
        st.rerun()


def barra():
    titulo, estado, archivo, configuracion = st.columns([1.6, 2.3, 0.8, 1.1], vertical_alignment="center")
    titulo.markdown("### Planificador")
    segundos = float(st.session_state.segundos)
    estado.caption(
        f"{len(st.session_state.tareas)} tareas · {int(st.session_state.procesadores)} CPU · 1 u = {segundos:g} s"
    )
    with archivo:
        with st.popover("Archivo", width="stretch"):
            st.button("Nuevo", on_click=vaciar_tareas, width="stretch")
            st.button("Cargar ejemplo", on_click=cargar_ejemplo, width="stretch")
            if st.button("Importar", width="stretch"):
                dialogo_importar()
            if st.session_state.tareas:
                tramos = []
                if st.session_state.orden:
                    tramos = planificar(
                        st.session_state.tareas,
                        st.session_state.orden,
                        int(st.session_state.procesadores),
                    )
                st.download_button(
                    "Exportar",
                    tareas_a_csv(st.session_state.tareas, tramos, int(st.session_state.reloj)),
                    file_name="tareas.csv",
                    mime="text/csv",
                    width="stretch",
                )
            st.download_button(
                "Descargar plantilla",
                plantilla_csv(),
                file_name="plantilla.csv",
                mime="text/csv",
                width="stretch",
            )
    with configuracion:
        with st.popover("Configuración", width="stretch"):
            st.number_input("Procesadores", min_value=1, max_value=8, step=1, key="procesadores")
            st.number_input(
                "Segundos por unidad",
                min_value=0.01,
                step=0.1,
                format="%.2f",
                key="segundos",
            )


def agregar_tarea(llegada, ejecucion, prioridad):
    try:
        llegada = entero(llegada, "llegada")
        ejecucion = entero(ejecucion, "ejecucion")
        prioridad = entero(prioridad, "prioridad")
    except ValueError as error:
        st.session_state.error_alta = str(error)
        return
    if llegada < 0:
        st.session_state.error_alta = "La llegada no puede ser negativa"
        return
    if ejecucion < 1:
        st.session_state.error_alta = "La ejecución debe ser de al menos 1"
        return
    st.session_state.tareas.append(
        {"pid": siguiente_pid(), "llegada": llegada, "ejecucion": ejecucion, "prioridad": prioridad}
    )
    st.session_state.error_alta = ""


def formulario_tareas():
    with st.form("alta", clear_on_submit=True):
        columnas = st.columns([1, 1, 1, 1])
        llegada = columnas[0].number_input("Llegada", min_value=0, step=1, value=0)
        ejecucion = columnas[1].number_input("Ejecución", min_value=1, step=1, value=1)
        prioridad = columnas[2].number_input("Prioridad", step=1, value=1)
        columnas[3].markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
        enviar = columnas[3].form_submit_button("Agregar", width="stretch")
    if enviar:
        agregar_tarea(llegada, ejecucion, prioridad)
    if st.session_state.get("error_alta"):
        st.error(st.session_state.error_alta)
    if not st.session_state.tareas:
        st.info("Todavía no hay tareas.")
        return
    tramos = []
    if st.session_state.orden:
        tramos = planificar(
            st.session_state.tareas,
            st.session_state.orden,
            int(st.session_state.procesadores),
        )
    st.dataframe(
        tabla_tareas(st.session_state.tareas, tramos, int(st.session_state.reloj)),
        hide_index=True,
        width="stretch",
    )


def tareas():
    with st.container(border=True):
        st.subheader("Tareas")
        formulario_tareas()


def avanzar_reloj(fin):
    if not st.session_state.reproduciendo or st.session_state.reloj >= fin:
        return
    espera = VELOCIDAD[st.session_state.velocidad]
    if time.monotonic() - float(st.session_state.ultimo_tick) < espera:
        return
    st.session_state.reloj += 1
    st.session_state.ultimo_tick = time.monotonic()
    if st.session_state.reloj >= fin:
        st.session_state.reproduciendo = False
        st.rerun()


def reproductor(tramos, fin, procesadores, segundos):
    avanzar_reloj(fin)
    reloj = int(st.session_state.reloj)
    with st.container(horizontal=True, vertical_alignment="center", gap="xsmall"):
        if st.button("", icon=":material/replay:", help="Reiniciar", type="tertiary", key="repro_reiniciar"):
            reiniciar_reloj()
            st.rerun()
        if st.button(
            "",
            icon=":material/skip_previous:",
            help="Retroceder",
            type="tertiary",
            disabled=reloj <= 0,
            key="repro_atras",
        ):
            st.session_state.reloj = reloj - 1
            st.session_state.reproduciendo = False
            st.rerun()
        if st.session_state.reproduciendo:
            icono, ayuda = ":material/pause:", "Pausa"
            detenido = False
        else:
            icono, ayuda = ":material/play_arrow:", "Play"
            detenido = reloj >= fin
        if st.button("", icon=icono, help=ayuda, type="primary", disabled=detenido, key="repro_play"):
            st.session_state.reproduciendo = not st.session_state.reproduciendo
            st.session_state.ultimo_tick = time.monotonic()
            st.rerun()
        if st.button(
            "",
            icon=":material/skip_next:",
            help="Avanzar",
            type="tertiary",
            disabled=reloj >= fin,
            key="repro_adelante",
        ):
            st.session_state.reloj = reloj + 1
            st.session_state.reproduciendo = False
            st.rerun()
        if st.button(
            "",
            icon=":material/last_page:",
            help="Ir al final",
            type="tertiary",
            disabled=reloj >= fin,
            key="repro_final",
        ):
            st.session_state.reloj = fin
            st.session_state.reproduciendo = False
            st.rerun()
        st.selectbox("Velocidad", list(VELOCIDAD), key="velocidad", label_visibility="collapsed")
    st.caption(linea_estado(tramos, int(st.session_state.reloj), procesadores, segundos))
    visibles = recortar(tramos, int(st.session_state.reloj))
    st.plotly_chart(
        figura_gantt(visibles, procesadores, segundos, int(st.session_state.reloj)),
        width="stretch",
        theme=None,
        config={"displayModeBar": False},
    )
    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)


def cuerpo_gantt():
    if not st.session_state.tareas:
        st.info("Agrega al menos una tarea para ver el diagrama.")
        return
    if not st.session_state.orden:
        st.info("Enciende al menos un criterio para ordenar la cola.")
        return
    procesadores = int(st.session_state.procesadores)
    segundos = float(st.session_state.segundos)
    tramos = planificar(st.session_state.tareas, st.session_state.orden, procesadores)
    if not tramos:
        st.info("No hay nada que dibujar con esta configuración.")
        return
    fin = max(tramo["fin"] for tramo in tramos)
    intervalo = 0.2 if st.session_state.reproduciendo and st.session_state.reloj < fin else None
    st.fragment(reproductor, run_every=intervalo)(tramos, fin, procesadores, segundos)


def gantt():
    with st.container(border=True):
        st.subheader("Tiempos de ejecución")
        cuerpo_gantt()


def main():
    st.set_page_config(page_title="Planificador de procesos", layout="wide", page_icon=	":robot:", menu_items={
        'About': "# SISTEMAS OPERATIVOS. Planificador de procesos."
    })
    iniciar()
    barra()
    criterios()
    tareas()
    vigilar_reloj()
    gantt()
