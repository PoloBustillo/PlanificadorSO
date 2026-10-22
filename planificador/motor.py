
def clave(tarea, orden, instante):
    valores = {
        # Una tarea que ya llegó tiene 0 pendiente en este criterio.
        "llegada": max(tarea["llegada"] - instante, 0),
        "ejecucion": tarea.get("restante", tarea["ejecucion"]),
        # La prioridad más alta debe producir la clave más pequeña.
        "prioridad": -tarea["prioridad"],
        "pid": tarea["pid"],
    }
    return tuple(valores[criterio] for criterio in orden)


def planificar(tareas, orden, procesadores=1):
    if not tareas or not orden or procesadores < 1:
        return []

    procesos = [dict(tarea, restante=tarea["ejecucion"]) for tarea in tareas]
    incorporados = set()
    listos = []
    espera = []
    tramos = []
    instante = 0
    ronda = 1

    while any(tarea["restante"] > 0 for tarea in procesos):
        for tarea in procesos:
            if tarea["pid"] not in incorporados and tarea["llegada"] <= instante:
                listos.append(tarea)
                incorporados.add(tarea["pid"])

        for cpu in range(procesadores):
            if not listos:
                if any(tarea["restante"] > 0 for tarea in procesos):
                    tramos.append(
                        {
                            "cpu": cpu + 1,
                            "pid": 0,
                            "nombre": "Inactivo",
                            "inicio": instante,
                            "fin": instante + 1,
                        }
                    )
                continue

            elegido = min(listos, key=lambda tarea: clave(tarea, orden, instante))
            tramos.append(
                {
                    "cpu": cpu + 1,
                    "pid": elegido["pid"],
                    "nombre": f"P{elegido['pid']}",
                    "inicio": instante,
                    "fin": instante + 1,
                    "ronda": ronda,
                }
            )
            elegido["restante"] -= 1
            listos.remove(elegido)
            if elegido["restante"] > 0:
                espera.append(elegido)

        # La espera vuelve a listos únicamente cuando la cola de listos fue
        # consumida por completo, y siempre para la siguiente unidad.
        if not listos and espera:
            listos = espera.copy()
            espera.clear()
            ronda += 1

        instante += 1
    return tramos


def estado_en(tareas, orden, reloj, procesadores=1):
    procesos = [dict(tarea, restante=tarea["ejecucion"]) for tarea in tareas]
    incorporados = set()
    listos = []
    espera = []

    for instante in range(reloj):
        for tarea in procesos:
            if tarea["pid"] not in incorporados and tarea["llegada"] <= instante:
                listos.append(tarea)
                incorporados.add(tarea["pid"])

        for _ in range(procesadores):
            if not listos:
                break
            elegido = min(listos, key=lambda tarea: clave(tarea, orden, instante))
            listos.remove(elegido)
            elegido["restante"] -= 1
            if elegido["restante"] > 0:
                espera.append(elegido)

        if not listos and espera:
            listos = espera.copy()
            espera.clear()

    for tarea in procesos:
        if tarea["pid"] not in incorporados and tarea["llegada"] <= reloj:
            listos.append(tarea)
            incorporados.add(tarea["pid"])

    listos.sort(key=lambda tarea: clave(tarea, orden, reloj))
    return espera, listos
