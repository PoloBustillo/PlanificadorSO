import heapq
from collections import deque

from planificador.constantes import ALGORITMOS


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


def limpiar_ociosos(tramos):
    con_trabajo = {tramo["cpu"] for tramo in tramos if tramo["pid"] != 0}
    return [tramo for tramo in tramos if tramo["pid"] != 0 or tramo["cpu"] in con_trabajo]


def fusionar(tramos):
    if not tramos:
        return []
    ordenados = sorted(tramos, key=lambda tramo: (tramo["cpu"], tramo["inicio"]))
    salida = [dict(ordenados[0])]
    for tramo in ordenados[1:]:
        previo = salida[-1]
        if previo["cpu"] == tramo["cpu"] and previo["pid"] == tramo["pid"] and previo["fin"] == tramo["inicio"]:
            previo["fin"] = tramo["fin"]
        else:
            salida.append(dict(tramo))
    return salida


def planificar_expropiativo(tareas, procesadores, ranking):
    if not tareas or procesadores < 1:
        return []
    vivos = [dict(tarea, restante=tarea["ejecucion"]) for tarea in tareas]
    ahora = 0
    asignado = [None] * procesadores
    abiertos = [None] * procesadores
    tramos = []

    def cerrar(cpu, fin):
        tramo = abiertos[cpu]
        if tramo is None:
            return
        tramo["fin"] = fin
        if tramo["fin"] > tramo["inicio"]:
            tramos.append(tramo)
        abiertos[cpu] = None

    def abrir(cpu, pid, nombre, inicio):
        abiertos[cpu] = {"cpu": cpu + 1, "pid": pid, "nombre": nombre, "inicio": inicio}

    while any(tarea["restante"] > 0 for tarea in vivos):
        listos = [tarea for tarea in vivos if tarea["llegada"] <= ahora and tarea["restante"] > 0]
        if not listos:
            siguiente = min(tarea["llegada"] for tarea in vivos if tarea["restante"] > 0)
            for cpu in range(procesadores):
                if asignado[cpu] != 0:
                    cerrar(cpu, ahora)
                    abrir(cpu, 0, "Inactivo", ahora)
                    asignado[cpu] = 0
            ahora = siguiente
            continue
        elegidos = sorted(listos, key=ranking)[:procesadores]
        nuevo = [0] * procesadores
        sobrantes = []
        for tarea in elegidos:
            puesto = next((indice for indice, pid in enumerate(asignado) if pid == tarea["pid"]), None)
            if puesto is None:
                sobrantes.append(tarea["pid"])
            else:
                nuevo[puesto] = tarea["pid"]
        for cpu in range(procesadores):
            if nuevo[cpu] == 0 and sobrantes:
                nuevo[cpu] = sobrantes.pop(0)
        for cpu, pid in enumerate(nuevo):
            if pid != asignado[cpu]:
                cerrar(cpu, ahora)
                if pid == 0:
                    abrir(cpu, 0, "Inactivo", ahora)
                else:
                    abrir(cpu, pid, f"P{pid}", ahora)
                asignado[cpu] = pid
        proximas = [tarea["llegada"] for tarea in vivos if tarea["llegada"] > ahora and tarea["restante"] > 0]
        avance = min(tarea["restante"] for tarea in elegidos)
        if proximas:
            avance = min(avance, min(proximas) - ahora)
        if avance <= 0:
            break
        for tarea in elegidos:
            tarea["restante"] -= avance
        ahora += avance
    for cpu in range(procesadores):
        cerrar(cpu, ahora)
    return fusionar(limpiar_ociosos(tramos))


def planificar_rr(tareas, quantum, procesadores):
    if not tareas or quantum < 1 or procesadores < 1:
        return []
    quantum = int(quantum)
    info = {tarea["pid"]: dict(tarea, restante=tarea["ejecucion"]) for tarea in tareas}
    pendientes = sorted(tareas, key=lambda tarea: (tarea["llegada"], tarea["pid"]))
    cursor = 0
    cola = deque()
    ingresados = set()
    tramos = []
    eventos = []
    turno = 0

    def push(cuando, cpu, pid):
        nonlocal turno
        heapq.heappush(eventos, (cuando, turno, cpu, pid))
        turno += 1

    def ingresar(hasta):
        nonlocal cursor
        while cursor < len(pendientes) and pendientes[cursor]["llegada"] <= hasta:
            pid = pendientes[cursor]["pid"]
            if pid not in ingresados:
                cola.append(pid)
                ingresados.add(pid)
            cursor += 1

    for cpu in range(procesadores):
        push(0, cpu, 0)

    while eventos:
        instante = eventos[0][0]
        grupo = []
        while eventos and eventos[0][0] == instante:
            _, _, cpu, pid = heapq.heappop(eventos)
            grupo.append((cpu, pid))
        reencolar = [pid for _cpu, pid in sorted(grupo) if pid and info[pid]["restante"] > 0]
        ingresar(instante)
        cola.extend(reencolar)
        for cpu, _pid in sorted(grupo):
            if cola:
                pid = cola.popleft()
                correr = min(quantum, info[pid]["restante"])
                info[pid]["restante"] -= correr
                tramos.append(
                    {
                        "cpu": cpu + 1,
                        "pid": pid,
                        "nombre": f"P{pid}",
                        "inicio": instante,
                        "fin": instante + correr,
                    }
                )
                push(instante + correr, cpu, pid if info[pid]["restante"] > 0 else 0)
                continue
            futuro = []
            if cursor < len(pendientes):
                futuro.append(pendientes[cursor]["llegada"])
            if eventos:
                futuro.append(eventos[0][0])
            if not futuro:
                continue
            destino = min(futuro)
            if destino > instante:
                tramos.append(
                    {"cpu": cpu + 1, "pid": 0, "nombre": "Inactivo", "inicio": instante, "fin": destino}
                )
                push(destino, cpu, 0)
    return fusionar(limpiar_ociosos(tramos))


def simular(tareas, algoritmo, orden, procesadores, quantum, expropiar):
    if algoritmo not in ALGORITMOS:
        algoritmo = "Por criterios"
    if algoritmo == "Round Robin":
        return planificar_rr(tareas, quantum, procesadores)
    if algoritmo == "SRTF":
        return planificar_expropiativo(
            tareas, procesadores, lambda tarea: (tarea["restante"], tarea["llegada"], tarea["pid"])
        )
    if algoritmo == "Prioridad" and expropiar:
        return planificar_expropiativo(
            tareas, procesadores, lambda tarea: (tarea["prioridad"], tarea["llegada"], tarea["pid"])
        )
    ordenes = {
        "FCFS": ["llegada", "pid"],
        "SJF": ["ejecucion", "llegada", "pid"],
        "Prioridad": ["prioridad", "llegada", "pid"],
        "Por criterios": list(orden),
    }
    return planificar(tareas, ordenes[algoritmo], procesadores)
