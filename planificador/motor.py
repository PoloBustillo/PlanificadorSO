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
        print(f"CPU {cpu + 1} elige tarea {elegido['pid']} en instante {instante}")
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
