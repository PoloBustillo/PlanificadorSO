CRITERIOS = [
    {"id": "llegada", "nombre": "Llegada"},
    {"id": "ejecucion", "nombre": "Ejecución"},
    {"id": "prioridad", "nombre": "Prioridad"},
    {"id": "pid", "nombre": "PID"},
]
ALGORITMOS = ["FCFS", "SJF", "SRTF", "Round Robin", "Prioridad", "Por criterios"]
NOMBRE_A_ID = {criterio["nombre"]: criterio["id"] for criterio in CRITERIOS}
ID_A_NOMBRE = {criterio["id"]: criterio["nombre"] for criterio in CRITERIOS}
VELOCIDAD = {"Lento": 1.0, "Normal": 0.45, "Rápido": 0.2}

EJEMPLO = [
    {"pid": 1, "llegada": 0, "ejecucion": 5, "prioridad": 4},
    {"pid": 2, "llegada": 1, "ejecucion": 3, "prioridad": 3},
    {"pid": 3, "llegada": 2, "ejecucion": 8, "prioridad": 1},
    {"pid": 4, "llegada": 3, "ejecucion": 6, "prioridad": 2},
]

PALETA = ["#1f6f5b", "#c4532a", "#245b86", "#8a5a12", "#6b3f69", "#3d6b4f", "#8f3d3d"]
COLOR_INACTIVO = "#c8c2b6"

ESTILO_ORDEN = """
.sortable-component {
    border: 0;
    background: transparent;
    padding: 0;
}
.sortable-container-body {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem;
    background: transparent;
    min-height: 0;
    padding: 0;
}
.sortable-item {
    display: inline-block;
    width: auto;
    height: auto;
    cursor: grab;
    background: #fffdf8;
    border: 1px solid #e4daca;
    border-radius: 999px;
    padding: 0.2rem 0.75rem;
    margin: 0;
    color: #1c1915;
    font-weight: 600;
}
.sortable-item:hover {
    border-color: #c4532a;
    box-shadow: 0 4px 12px rgba(28, 25, 21, 0.12);
}
"""
