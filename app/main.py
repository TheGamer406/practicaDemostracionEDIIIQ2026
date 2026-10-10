"""Rutas FastAPI y streams SSE del motor de reglas optimizadoras."""
import asyncio
import json
import timeit
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app import logica
from app.demostracion import PASOS, verificar_pasos

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Motor de reglas optimizadoras")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

VELOCIDADES = {"lento": 1.0, "normal": 0.5, "rapido": 0.15}
SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


def _intervalo(request: Request) -> float:
    velocidad = request.query_params.get("velocidad", "normal")
    return VELOCIDADES.get(velocidad, VELOCIDADES["normal"])


def _evento(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/codigo")
def api_codigo():
    return {
        "legacy": logica.codigo_fuente(logica.evaluar_acceso_legacy),
        "optimizado": logica.codigo_fuente(logica.evaluar_acceso_optimizado),
    }


@app.get("/api/comparacion")
def api_comparacion():
    ops_legacy = logica.contar_operaciones(logica.evaluar_acceso_legacy)
    ops_optimizado = logica.contar_operaciones(logica.evaluar_acceso_optimizado)
    reduccion = round((1 - ops_optimizado / ops_legacy) * 100, 1)

    n_iter = 200_000
    t_legacy = timeit.timeit(
        "evaluar_acceso_legacy(True, False, True)",
        globals={"evaluar_acceso_legacy": logica.evaluar_acceso_legacy},
        number=n_iter,
    )
    t_optimizado = timeit.timeit(
        "evaluar_acceso_optimizado(True, False, True)",
        globals={"evaluar_acceso_optimizado": logica.evaluar_acceso_optimizado},
        number=n_iter,
    )

    return {
        "operaciones": {
            "legacy": ops_legacy,
            "optimizado": ops_optimizado,
            "reduccion_pct": reduccion,
            "criterio": (
                "Se recorre el AST de cada función: cada BoolOp (and/or) con n operandos "
                "cuenta n-1 operaciones, y cada UnaryOp 'not' cuenta 1 operación."
            ),
        },
        "lineas": {"legacy": 6, "optimizado": 1, "variables_intermedias": {"legacy": 3, "optimizado": 0}},
        "tabla": logica.tabla_comparacion(),
        "benchmark": {
            "iteraciones": n_iter,
            "segundos_legacy": t_legacy,
            "segundos_optimizado": t_optimizado,
            "nota": (
                "En Python la diferencia absoluta por llamada es pequeña: el intérprete domina el costo. "
                "El valor real está en legibilidad, menos ramas y menor costo acumulado a escala "
                "(millones de peticiones en un sistema de feature flags real)."
            ),
        },
    }


@app.get("/api/stream/tabla")
async def stream_tabla(request: Request):
    intervalo = _intervalo(request)

    async def generador():
        for fila in logica.tabla_verdad_legacy():
            if await request.is_disconnected():
                break
            yield _evento(fila)
            await asyncio.sleep(intervalo)
        yield _evento({"fin": True, "conclusion": "f es verdadera solo en las filas 011, 101 y 111."})

    return StreamingResponse(generador(), media_type="text/event-stream", headers=SSE_HEADERS)


@app.get("/api/stream/demostracion")
async def stream_demostracion(request: Request):
    intervalo = _intervalo(request)

    async def generador():
        resultados = verificar_pasos(PASOS)
        for r in resultados:
            if await request.is_disconnected():
                break
            yield _evento(r)
            await asyncio.sleep(intervalo)
        todos_ok = all(r["igual_a_original"] for r in resultados)
        yield _evento({
            "fin": True,
            "todos_los_pasos_validos": todos_ok,
            "forma_final": "C ∧ (A ∨ B)",
        })

    return StreamingResponse(generador(), media_type="text/event-stream", headers=SSE_HEADERS)


@app.get("/api/stream/validacion")
async def stream_validacion(request: Request):
    intervalo = _intervalo(request)

    async def generador():
        filas = logica.tabla_comparacion()
        for fila in filas:
            if await request.is_disconnected():
                break
            yield _evento(fila)
            await asyncio.sleep(intervalo)
        try:
            logica.probar_equivalencia()
            yield _evento({"assert": "ok"})
        except AssertionError as exc:
            yield _evento({"assert": "fail", "detalle": str(exc)})

    return StreamingResponse(generador(), media_type="text/event-stream", headers=SSE_HEADERS)
