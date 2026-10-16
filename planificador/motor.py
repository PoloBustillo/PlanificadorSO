def clave(tarea, orden):
    valores = {
        "llegada": tarea["llegada"],
        "ejecucion": tarea["ejecucion"],
        "prioridad": tarea["prioridad"],
        "pid": tarea["pid"],
    }
    return tuple(valores[criterio] for criterio in orden)


def planificar(tareas, orden, procesadores=1):
    if not tareas or not orden or procesadores < 1:
        return []
    pendientes = [dict(tarea) for tarea in tareas]
    libre = [0] * procesadores
    tramos = []
    while pendientes:
        cpu = min(range(procesadores), key=lambda indice: (libre[indice], indice))
        instante = libre[cpu]
        listos = [tarea for tarea in pendientes if tarea["llegada"] <= instante]
        if not listos:
            siguiente = min(tarea["llegada"] for tarea in pendientes)
            tramos.append(
                {"cpu": cpu + 1, "pid": 0, "nombre": "Inactivo", "inicio": instante, "fin": siguiente}
            )
            libre[cpu] = siguiente
            continue
        elegido = min(listos, key=lambda tarea: clave(tarea, orden))
        fin = instante + elegido["ejecucion"]
        tramos.append(
            {
                "cpu": cpu + 1,
                "pid": elegido["pid"],
                "nombre": f"P{elegido['pid']}",
                "inicio": instante,
                "fin": fin,
            }
        )
        libre[cpu] = fin
        pendientes.remove(elegido)
    return tramos


def estado_en(tareas, tramos, orden, reloj):
    por_pid = {tramo["pid"]: tramo for tramo in tramos if tramo["pid"]}
    espera = []
    listos = []
    for tarea in tareas:
        if tarea["llegada"] > reloj:
            continue
        tramo = por_pid.get(tarea["pid"])
        if tramo is None or tramo["fin"] <= reloj:
            continue
        if tramo["inicio"] <= reloj:
            espera.append((tarea, tramo))
        else:
            listos.append(tarea)
    espera.sort(key=lambda par: par[1]["cpu"])
    listos.sort(key=lambda tarea: clave(tarea, orden))
    return espera, listos
