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

**Archivo** está arriba: Nuevo, Cargar ejemplo, Importar, Exportar y Descargar plantilla. Importar pide un CSV con `llegada`, `ejecucion` y `prioridad`. El PID del archivo se ignora: la aplicación numera desde 1. La vista previa no reemplaza la lista hasta pulsar **Usar estas tareas**.

**Configuración** está al lado: procesadores, de 1 a 8, y cuántos segundos vale cada unidad de tiempo. Eso solo traduce el eje y el cursor; no cambia el orden de las tareas.

Al agregar una tarea a mano, el PID es el mayor de la lista más uno.

## Reproducción

Encima del diagrama: Reiniciar, Retroceder, Play, Pausa, Avanzar e Ir al final. Play suma una unidad y se detiene al terminar. La velocidad (lento, normal, rápido) es solo de la animación.

## Ejemplo

P1 a P4 llegan en 0, 1, 2 y 3, con ráfagas 5, 3, 8 y 6, y prioridades 4, 3, 1 y 2. Con un procesador y el orden Llegada, Ejecución, Prioridad, PID, la CPU queda: P1 de 0 a 5, P2 de 5 a 8, P3 de 8 a 16 y P4 de 16 a 22.

Con dos procesadores y ese mismo orden, P2 llega en 1, así que no entra junto con P1. CPU 1 corre P1 de 0 a 5 y P4 de 5 a 11. CPU 2 espera hasta 1, corre P2 de 1 a 4 y P3 de 4 a 12.
