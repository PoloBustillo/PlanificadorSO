import streamlit as st

from planificador.constantes import CRITERIOS, EJEMPLO, NOMBRE_A_ID


def iniciar():
    if "tareas" not in st.session_state:
        st.session_state.tareas = []
        st.session_state.orden = [criterio["id"] for criterio in CRITERIOS]
    if "activos" not in st.session_state:
        if any(f"activo_{criterio['id']}" in st.session_state for criterio in CRITERIOS):
            st.session_state.activos = [
                criterio["nombre"]
                for criterio in CRITERIOS
                if st.session_state.get(f"activo_{criterio['id']}", True)
            ]
        else:
            st.session_state.activos = [criterio["nombre"] for criterio in CRITERIOS]
    st.session_state.setdefault("procesadores", 1)
    st.session_state.setdefault("segundos", 1.0)
    st.session_state.setdefault("reloj", 0)
    st.session_state.setdefault("reproduciendo", False)
    st.session_state.setdefault("velocidad", "Normal")
    st.session_state.setdefault("ultimo_tick", 0.0)


def reiniciar_reloj():
    st.session_state.reloj = 0
    st.session_state.reproduciendo = False


def vigilar_reloj():
    firma = (
        tuple((tarea["pid"], tarea["llegada"], tarea["ejecucion"], tarea["prioridad"]) for tarea in st.session_state.tareas),
        tuple(st.session_state.orden),
        int(st.session_state.procesadores),
    )
    if st.session_state.get("firma_corrida") != firma:
        st.session_state.firma_corrida = firma
        reiniciar_reloj()


def sincronizar_activos():
    elegidos = [NOMBRE_A_ID[nombre] for nombre in st.session_state.activos]
    orden = [criterio for criterio in st.session_state.orden if criterio in elegidos]
    for criterio in elegidos:
        if criterio not in orden:
            orden.append(criterio)
    st.session_state.orden = orden


def siguiente_pid():
    if not st.session_state.tareas:
        return 1
    return max(tarea["pid"] for tarea in st.session_state.tareas) + 1


def vaciar_tareas():
    st.session_state.tareas = []


def cargar_ejemplo():
    st.session_state.tareas = [dict(tarea) for tarea in EJEMPLO]
