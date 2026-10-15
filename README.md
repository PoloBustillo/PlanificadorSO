# Planificador de procesos

Pantalla en Streamlit para ordenar tareas en una o varias CPU que comparten la cola. El orden lo deciden llegada, ejecución, prioridad y PID: se encienden en un grupo y se arrastran. El de la izquierda desempata primero. Gana el número menor. No hay expropiación.

El diagrama no se muestra completo de una vez. Los controles avanzan el reloj de una unidad en una.

## Cómo abrirlo

```bash
cd planificador
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Barra

**Archivo** está arriba: Nuevo, Cargar ejemplo, Importar, Exportar y Descargar plantilla. Importar usa `PID`, `T.ll` (llegada), `T.exe` (ejecución) y `Prioridad`. `FIN`, `T.Fin` y `T.Esp` no entran al orden: se calculan. Si el archivo no trae PID, la aplicación numera desde 1. La vista previa no reemplaza la lista hasta pulsar **Usar estas tareas**.

**Configuración** está al lado: procesadores, de 1 a 8, y cuántos segundos vale cada unidad de tiempo. Eso solo traduce el eje y el cursor; no cambia el orden de las tareas.

Al agregar una tarea a mano, el PID es el mayor de la lista más uno.

## Reproducción

Encima del diagrama: Reiniciar, Retroceder, Play, Pausa, Avanzar e Ir al final. Play suma una unidad y se detiene al terminar. La velocidad (lento, normal, rápido) es solo de la animación.

## Ejemplo

El ejemplo son 12 procesos. Llegan en 0, 0, 0, 2, 3, 5, 6, 7, 3, 2, 1 y 1; sus ráfagas son 1, 1, 2, 3, 3, 3, 2, 2, 1, 3, 2 y 1; sus prioridades son 4, 4, 3, 2, 0, 1, 4, 3, 2, 1, 4 y 3. Con un procesador y el orden Llegada, Ejecución, Prioridad, PID, la tabla completa `FIN`, `T.Fin` y `T.Esp` al terminar la corrida.
