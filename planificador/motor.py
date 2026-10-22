
def clave(tarea, orden, instante):
    valores = {
        # Una tarea que ya llegó tiene 0 pendiente en este criterio.
        "llegada": max(tarea["llegada"] - instante, 0),
        "ejecucion": tarea["ejecucion"],
        # La prioridad más alta debe producir la clave más pequeña.
        "prioridad": -tarea["prioridad"],
        "pid": tarea["pid"],
    }
    return tuple(valores[criterio] for criterio in orden)


def planificar(tareas, orden, procesadores=1):
    # Si no hay tareas, criterios u ordenadores válidos, no hay nada que planificar.
    if not tareas or not orden or procesadores < 1:
        return []

    # Copiamos las tareas para poder quitar las que ya fueron planificadas.
    pendientes = []
    for tarea in tareas:
        copia_tarea = dict(tarea)
        pendientes.append(copia_tarea)

    # Indica en qué instante queda libre cada procesador.
    libre = [0] * procesadores

    # Aquí guardaremos todos los tramos de ejecución.
    tramos = []

    # Repetimos hasta planificar todas las tareas.
    while pendientes:
        # Buscamos el procesador que queda libre primero.
        cpu = 0
        for indice in range(1, procesadores):
            procesador_actual = (libre[indice], indice)
            procesador_elegido = (libre[cpu], cpu)

            # En caso de empate, se conserva el procesador con menor índice.
            if procesador_actual < procesador_elegido:
                cpu = indice

        instante = libre[cpu]

        # Buscamos las tareas que ya llegaron y pueden ejecutarse.
        listos = []
        for tarea in pendientes:
            if tarea["llegada"] <= instante:
                listos.append(tarea)

        if not listos:
            # Si no hay tareas listas, el procesador permanece inactivo
            # hasta que llegue la siguiente tarea.
            siguiente = pendientes[0]["llegada"]
            for tarea in pendientes:
                if tarea["llegada"] < siguiente:
                    siguiente = tarea["llegada"]

            tramos.append(
                {"cpu": cpu + 1, "pid": 0, "nombre": "Inactivo", "inicio": instante, "fin": siguiente}
            )
            libre[cpu] = siguiente
            continue

        # Elegimos la tarea según el orden de criterios recibido.
        elegido = listos[0]
        for tarea in listos[1:]:
            clave_tarea = clave(tarea, orden, instante)
            clave_elegida = clave(elegido, orden, instante)

            if clave_tarea < clave_elegida:
                elegido = tarea

        fin = instante + elegido["ejecucion"]

        # Guardamos cuándo y dónde se ejecutó la tarea.
        tramos.append(
            {
                "cpu": cpu + 1,
                "pid": elegido["pid"],
                "nombre": f"P{elegido['pid']}",
                "inicio": instante,
                "fin": fin,
            }
        )

        # El procesador queda libre cuando termina la tarea.
        libre[cpu] = fin

        # La tarea ya fue planificada, así que la quitamos de pendientes.
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
    listos.sort(key=lambda tarea: clave(tarea, orden, reloj))
    return espera, listos
