import io

import pandas as pd

from planificador.constantes import EJEMPLO


def entero(valor, campo):
    if isinstance(valor, bool) or pd.isna(valor):
        raise ValueError(f"La columna {campo} debe ser un entero")
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"La columna {campo} debe ser un entero") from None
    if float(valor) != float(numero):
        raise ValueError(f"La columna {campo} debe ser un entero")
    return numero


ALIAS = {
    "pid": "pid",
    "t.ll": "llegada",
    "tll": "llegada",
    "llegada": "llegada",
    "t.exe": "ejecucion",
    "texe": "ejecucion",
    "ejecucion": "ejecucion",
    "prioridad": "prioridad",
    "fin": "fin",
    "t.fin": "t_fin",
    "tfin": "t_fin",
    "t.esp": "t_esp",
    "tesp": "t_esp",
}


def canonica(nombre):
    texto = str(nombre).strip().lower().replace(" ", "")
    return ALIAS.get(texto, texto)


def leer_csv(contenido):
    try:
        tabla = pd.read_csv(io.BytesIO(contenido))
    except Exception as error:
        raise ValueError("No se pudo leer el CSV") from error
    tabla.columns = [canonica(columna) for columna in tabla.columns]
    requeridas = ["llegada", "ejecucion", "prioridad"]
    if not set(requeridas).issubset(set(tabla.columns)):
        raise ValueError("El CSV debe tener llegada (T.ll), ejecucion (T.exe) y prioridad")
    if tabla.empty:
        raise ValueError("El CSV no trae tareas")
    tareas = []
    for indice, fila in enumerate(tabla.to_dict(orient="records"), start=1):
        llegada = entero(fila["llegada"], "llegada")
        ejecucion = entero(fila["ejecucion"], "ejecucion")
        prioridad = entero(fila["prioridad"], "prioridad")
        if llegada < 0:
            raise ValueError("La llegada no puede ser negativa")
        if ejecucion < 1:
            raise ValueError("La ejecución debe ser de al menos 1")
        pid = indice
        if "pid" in tabla.columns and not pd.isna(fila["pid"]):
            pid = entero(fila["pid"], "pid")
            if pid < 1:
                raise ValueError("El PID debe ser de al menos 1")
        tareas.append({"pid": pid, "llegada": llegada, "ejecucion": ejecucion, "prioridad": prioridad})
    if len({tarea["pid"] for tarea in tareas}) != len(tareas):
        raise ValueError("Hay PID repetidos")
    return tareas


def tareas_a_csv(tareas):
    return pd.DataFrame(tareas, columns=["pid", "llegada", "ejecucion", "prioridad"]).to_csv(index=False)


def plantilla_csv():
    filas = [
        {"llegada": tarea["llegada"], "ejecucion": tarea["ejecucion"], "prioridad": tarea["prioridad"]}
        for tarea in EJEMPLO
    ]
    return pd.DataFrame(filas).to_csv(index=False)
