CRITERIOS = [
    {"id": "llegada", "nombre": "Llegada"},
    {"id": "ejecucion", "nombre": "Ejecución"},
    {"id": "prioridad", "nombre": "Prioridad"},
    {"id": "pid", "nombre": "PID"},
]
NOMBRE_A_ID = {criterio["nombre"]: criterio["id"] for criterio in CRITERIOS}
ID_A_NOMBRE = {criterio["id"]: criterio["nombre"] for criterio in CRITERIOS}
VELOCIDAD = {"Lento": 1.0, "Normal": 0.45, "Rápido": 0.2}

EJEMPLO = [
    {"pid": 1, "llegada": 0, "ejecucion": 1, "prioridad": 4},
    {"pid": 2, "llegada": 0, "ejecucion": 1, "prioridad": 4},
    {"pid": 3, "llegada": 0, "ejecucion": 2, "prioridad": 3},
    {"pid": 4, "llegada": 2, "ejecucion": 3, "prioridad": 2},
    {"pid": 5, "llegada": 3, "ejecucion": 3, "prioridad": 0},
    {"pid": 6, "llegada": 5, "ejecucion": 3, "prioridad": 1},
    {"pid": 7, "llegada": 6, "ejecucion": 2, "prioridad": 4},
    {"pid": 8, "llegada": 7, "ejecucion": 2, "prioridad": 3},
    {"pid": 9, "llegada": 3, "ejecucion": 1, "prioridad": 2},
    {"pid": 10, "llegada": 2, "ejecucion": 3, "prioridad": 1},
    {"pid": 11, "llegada": 1, "ejecucion": 2, "prioridad": 4},
    {"pid": 12, "llegada": 1, "ejecucion": 1, "prioridad": 3},
]

PALETA = [
    "#1b7a64",
    "#d4652f",
    "#2a6fad",
    "#8a5a12",
    "#7a4e86",
    "#0e7490",
    "#a33b3b",
    "#4d7c0f",
    "#1e3a8a",
    "#b45309",
    "#6d28d9",
    "#be185d",
    "#0f766e",
    "#9a3412",
    "#0369a1",
    "#3f6212",
]
COLOR_INACTIVO = "#c8c2b6"

ESTILO_ORDEN = """
.sortable-component {
    border: 0;
    background: transparent;
    padding: 0.45rem 0.15rem 0.65rem;
}
.sortable-container-body {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem;
    background: transparent;
    min-height: 0;
    padding: 0.15rem 0;
}
.sortable-item,
.sortable-item:hover {
    display: inline-block;
    width: auto;
    height: auto;
    cursor: move !important;
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
    transform: translateY(-1px);
}
.sortable-item:active,
.sortable-item.dragging {
    cursor: grabbing !important;
}
"""
