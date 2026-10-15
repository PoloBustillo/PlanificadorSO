import time

import streamlit as st
from streamlit_sortables import sort_items

from planificador.constantes import ALGORITMOS, CRITERIOS, ESTILO_ORDEN, ID_A_NOMBRE, NOMBRE_A_ID, VELOCIDAD
from planificador.csv_tareas import entero, leer_csv, plantilla_csv, tareas_a_csv
from planificador.gantt import figura_gantt, linea_estado, recortar, tabla_tareas
from planificador.motor import simular
from planificador.sesion import (
    cargar_ejemplo,
    iniciar,
    reiniciar_reloj,
    siguiente_pid,
    sincronizar_activos,
    vaciar_tareas,
    vigilar_reloj,
)


def texto_algoritmo():
    algoritmo = st.session_state.algoritmo
    if algoritmo == "FCFS":
        return "Sin expropiación. Entra el que llegó primero. Si empatan, gana el PID menor."
    if algoritmo == "SJF":
        return "Sin expropiación. Entra el de menor ejecución. Desempata llegada y luego PID."
    if algoritmo == "SRTF":
        return "Con expropiación. Corre el que menos tiempo le queda."
    if algoritmo == "Round Robin":
        return "Cada proceso usa la CPU un quantum y, si le falta, vuelve al final de la cola."
    if algoritmo == "Prioridad" and st.session_state.expropiar:
        return "Con expropiación. Si llega uno con mejor prioridad, ocupa la CPU. Gana el número menor."
    if algoritmo == "Prioridad":
        return "Sin expropiación. Gana la prioridad menor. Desempata llegada y luego PID."
    return "Sin expropiación. Arrastra los criterios encendidos: el de la izquierda desempata primero."


def criterios():
    with st.container(border=True):
        st.subheader("Algoritmo")
        st.segmented_control(
            "Algoritmo",
            ALGORITMOS,
            key="algoritmo",
            label_visibility="collapsed",
            width="stretch",
            required=True,
        )
        st.caption(texto_algoritmo())
        elegido = st.session_state.algoritmo
        if elegido == "Round Robin":
            quantum, _resto = st.columns([1, 3])
            quantum.number_input("Quantum", min_value=1, step=1, key="quantum")
        elif elegido == "Prioridad":
            st.toggle("Expropiar", key="expropiar")
        elif elegido == "Por criterios":
            st.divider()
            st.markdown("**Criterios**")
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
    st.caption("Columnas: llegada, ejecucion, prioridad. Si el archivo trae pid, se ignora.")
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
        f"{st.session_state.algoritmo} · {len(st.session_state.tareas)} tareas · {int(st.session_state.procesadores)} CPU · 1 u = {segundos:g} s"
    )
    with archivo:
        with st.popover("Archivo", width="stretch"):
            st.button("Nuevo", on_click=vaciar_tareas, width="stretch")
            st.button("Cargar ejemplo", on_click=cargar_ejemplo, width="stretch")
            if st.button("Importar", width="stretch"):
                dialogo_importar()
            if st.session_state.tareas:
                st.download_button(
                    "Exportar",
                    tareas_a_csv(st.session_state.tareas),
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
    st.dataframe(tabla_tareas(st.session_state.tareas), hide_index=True, width="stretch")


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
    )


def cuerpo_gantt():
    if not st.session_state.tareas:
        st.info("Agrega al menos una tarea para ver el diagrama.")
        return
    if st.session_state.algoritmo == "Por criterios" and not st.session_state.orden:
        st.info("Enciende al menos un criterio para ordenar la cola.")
        return
    procesadores = int(st.session_state.procesadores)
    segundos = float(st.session_state.segundos)
    tramos = simular(
        st.session_state.tareas,
        st.session_state.algoritmo,
        st.session_state.orden,
        procesadores,
        int(st.session_state.quantum),
        bool(st.session_state.expropiar),
    )
    if not tramos:
        st.info("No hay nada que dibujar con esta configuración.")
        return
    fin = max(tramo["fin"] for tramo in tramos)
    intervalo = 0.2 if st.session_state.reproduciendo and st.session_state.reloj < fin else None
    st.fragment(reproductor, run_every=intervalo)(tramos, fin, procesadores, segundos)


def gantt():
    with st.container(border=True):
        st.subheader("Diagrama de Gantt")
        cuerpo_gantt()


def main():
    st.set_page_config(page_title="Planificador de procesos", layout="wide")
    iniciar()
    barra()
    criterios()
    tareas()
    vigilar_reloj()
    gantt()
