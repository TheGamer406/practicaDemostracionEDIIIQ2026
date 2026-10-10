# Motor de reglas optimizadoras

Prueba de Demostración I, Matemática Discreta (CENFOTEC, FCP0, C3-2026).

Demuestra, paso a paso y en vivo, que la regla de acceso legacy de Feature Flags
`(¬A∧B∧C)∨(A∧B∧C)∨(A∧¬B∧C)` es equivalente a `C∧(A∨B)`, y lo verifica ejecutando
el código real (tabla de verdad, demostración algebraica y validación por fuerza
bruta de las 8 combinaciones).

**La página web es el documento escrito completo** (ver sección "Cómo ejecutar" abajo
para levantarla). Este README solo cubre cómo correr el proyecto.

## Ejecutar con Docker

```bash
docker compose up --build
# abrir http://localhost:8000
```

## Ejecutar el script de consola (sin dependencias)

```bash
python3 script_standalone.py
```

## Desarrollo local sin Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest
```

## Estructura

```
app/
├── main.py              # rutas FastAPI + streams SSE
├── logica.py            # legacy, optimizado, tabla, equivalencia, conteo de operaciones
├── demostracion.py      # pasos de la demostración con fn ejecutable
└── static/              # frontend (HTML/CSS/JS vanilla, sin build step)
script_standalone.py     # versión de consola pedida por la consigna
tests/test_logica.py
```
