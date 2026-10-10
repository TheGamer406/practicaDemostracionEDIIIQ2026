# Plan v2 (para Claude Code): Motor de reglas optimizadoras, web + Docker

Prueba de Demostración I, Matemática Discreta (CENFOTEC, FCP0, C3-2026). Entrega: **10 de octubre**.

> Este documento está pensado para dárselo a Claude Code como especificación. Léelo completo antes de escribir código.

## 0. Cambios respecto a la v1 (acordado con la profesora)

- **Se entrega la web + el código. No hay PDF ni video.**
- Como no hay PDF, **la página web ES el documento escrito**: debe contener la demostración paso a paso, la explicación de cómo se mejoró el código y los resultados obtenidos. Todo explicado en la página.
- La página tiene **modo claro y oscuro con toggle**.
- La **parte visual en tiempo real es obligatoria** (tabla de verdad, simplificación y validación se ejecutan en vivo).
- Se agregan los temas que faltaban de la consigna: **comparación código viejo vs nuevo** y **aplicación del código dentro de la simplificación** (cada paso algebraico se comprueba ejecutando código).

## 1. Qué pide la consigna (mapa de cumplimiento)

| Requisito de la consigna | Cómo se cubre en la web |
|---|---|
| Contexto: Feature Flags, A = Administrador, B = Premium, C = Beta global | Sección 1 de la página: problema y significado de cada variable |
| P1.1 Validador que genere la tabla de verdad de `evaluar_acceso_legacy` | Sección 3: tabla generada en vivo desde el código real |
| P1.2 `evaluar_acceso_optimizado(A,B,C)` con la menor cantidad de operaciones | Sección 6 + conteo de operaciones calculado automáticamente (ver 4.4) |
| P1.3 Bucle que compara ambas para todas las combinaciones con `assert` | Sección 7: validación en vivo, 8/8 y resultado del `assert` |
| P2 Demostrar con leyes/inferencias lógicas que f = C ∧ (A ∨ B) | Sección 4: demostración paso a paso, ley por línea, verificada en vivo |
| Documento escrito: paso a paso + cómo se mejoró el código con resultados | Toda la página, más la Sección 8 (comparación) y la Sección 9 (conclusiones) |
| Entregable: código en ZIP | `script_standalone.py` + proyecto web + `docker-compose.yml` en el ZIP |

**Rúbrica (4 criterios):** método de demostración formal, resultados matemáticos, procesos matemáticos de la demostración, entrega de las demostraciones. Todos se resuelven con lo mismo: **justificar cada paso con el nombre exacto de la ley**, sin saltarse ninguno, y sin errores.

## 2. Stack y decisiones

| Tema | Decisión |
|---|---|
| Backend | Python 3.12 + FastAPI + Uvicorn |
| Tiempo real | **SSE** (Server-Sent Events) |
| Frontend | HTML + CSS + JS vanilla, **sin build step** |
| Resaltado de código | highlight.js **local** en `static/vendor/` (con tema claro y tema oscuro, sin CDN) |
| Código mostrado | `inspect.getsource()` sobre las funciones reales (lo que se ve es lo que corre) |
| Tema claro/oscuro | CSS variables + atributo `data-theme` en `<html>` |
| Despliegue | Docker + docker compose; HTTPS con Cloudflare Tunnel o Caddy |

Nada de frameworks de frontend ni dependencias externas en tiempo de ejecución: el día de la revisión no se puede fallar por un CDN caído.

## 3. Estructura del repositorio

```
motor-reglas/
├── app/
│   ├── main.py              # rutas FastAPI + streams SSE
│   ├── logica.py            # legacy, optimizado, tabla, equivalencia, conteo de operaciones
│   ├── demostracion.py      # pasos: expresión, ley, explicación, fn ejecutable
│   └── static/
│       ├── index.html
│       ├── style.css        # variables de tema claro/oscuro
│       ├── app.js           # SSE, animaciones, toggle de tema
│       └── vendor/          # highlight.js + temas claro y oscuro
├── script_standalone.py     # versión de consola (la que pide la consigna), sin dependencias
├── tests/test_logica.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

`logica.py` es la fuente única de verdad: lo importan tanto `main.py` como `script_standalone.py`.

## 4. Backend

### 4.1 Endpoints

| Ruta | Tipo | Descripción |
|---|---|---|
| `GET /` | HTML | Página principal |
| `GET /api/codigo` | JSON | Código fuente de legacy y optimizado (`inspect.getsource`) |
| `GET /api/stream/tabla` | SSE | Una fila de la tabla de verdad de legacy cada ~600 ms |
| `GET /api/stream/demostracion` | SSE | Cada paso con su ley + su columna de verdad + si coincide con la original |
| `GET /api/stream/validacion` | SSE | Recorre las 8 combinaciones comparando legacy vs optimizado; al final, resultado del `assert` |
| `GET /api/comparacion` | JSON | Conteo de operaciones, tablas lado a lado, benchmark |
| `GET /health` | JSON | Healthcheck |

Parámetro opcional `?velocidad=lento|normal|rapido` para controlar el intervalo entre eventos.

Cabeceras de los streams: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `X-Accel-Buffering: no`.

### 4.2 Tabla de verdad (evento SSE)

```json
{"i": 5, "A": true, "B": false, "C": true, "opcion_1": false, "opcion_2": false, "opcion_3": true, "legacy": true}
```

Incluir `opcion_1`, `opcion_2`, `opcion_3` para que la UI muestre **qué término hizo verdadera la fila**. Esto conecta el código con la forma de la función f (los tres términos del OR).

### 4.3 Simplificación con código aplicado (tema que faltaba)

Cada paso de la demostración es un objeto con expresión, ley, explicación y **función ejecutable**:

```python
{"n": 4, "expr": "C ∧ [(B ∧ T) ∨ (A ∧ ¬B)]",
 "ley": "Complemento", "detalle": "¬A ∨ A ≡ T",
 "fn": lambda A, B, C: C and ((B and True) or (A and not B))}
```

Para cada paso, el backend evalúa `fn` en las 8 combinaciones y la compara con `f` original. Evento SSE:

```json
{"n": 4, "expr": "...", "ley": "Complemento", "detalle": "¬A ∨ A ≡ T",
 "columna": [0,0,0,1,0,1,0,1], "igual_a_original": true}
```

**Visual obligatoria:** matriz de pasos × 8 combinaciones. Cada paso agrega una fila con sus 8 bits; todas deben quedar idénticas a la fila de la función original. Se ve en vivo que **cada transformación algebraica preserva la tabla de verdad**. Si un paso no coincide, se marca en rojo (útil para probar que la verificación funciona: romper un paso a propósito en un test).

Al final del stream, un último evento confirma que la forma final `C ∧ (A ∨ B)` coincide con la original, y muestra que `f(A,B,C)` es verdadera solo en 011, 101 y 111.

### 4.4 Conteo de operaciones (automático, no hardcodeado)

Contar con el módulo `ast` sobre el código fuente de cada función:

- `BoolOp` con n operandos cuenta como **n − 1** operaciones (ej: `a and b and c` = 2).
- `UnaryOp(Not)` cuenta como **1**.

Resultado esperado: **legacy = 10 operaciones lógicas** (3 + 2 + 3 en las tres opciones, más 2 del `or`; 11 si se cuenta también el `if/else`), **optimizado = 2** (`or` y `and`). Mostrar el criterio de conteo en la página para que sea transparente.

### 4.5 Validación

El stream recorre las 8 combinaciones con `itertools.product`, compara `bool(legacy)` vs `bool(optimizado)` y emite un evento por combinación. Al terminar ejecuta realmente el `assert` y emite `{"assert": "ok"}` o `{"assert": "fail", "A":..,"B":..,"C":..}`.

### 4.6 Comparación (viejo vs nuevo)

`/api/comparacion` devuelve:

- Operaciones: legacy vs optimizado (de 4.4) y % de reducción.
- Tablas de verdad lado a lado (8 filas, columna `legacy`, columna `optimizado`, columna `coincide`).
- Benchmark con `timeit` (por ejemplo 1.000.000 de llamadas cada una). **Aclarar en la página** que en Python la diferencia absoluta es pequeña y que el valor real está en legibilidad, menos ramas y menor costo a escala (millones de peticiones), como plantea la consigna.
- Líneas de código y complejidad: 6 líneas con 3 variables intermedias vs 1 línea.

## 5. Frontend

### 5.1 Tema claro/oscuro con toggle

- Todos los colores como variables CSS en `:root` y `[data-theme="dark"]`.
- Tema inicial: preferencia guardada en `localStorage`; si no hay, `prefers-color-scheme`.
- Toggle accesible (`<button>` con `aria-label` y `aria-pressed`) fijo en la cabecera, icono sol/luna.
- El tema debe cubrir **todo**: tablas, bloques de código (cambiar el tema de highlight.js en caliente), diagramas SVG (usar `currentColor` o variables CSS, no colores fijos) y los estados verde/rojo con contraste suficiente en ambos modos (WCAG AA).
- Sin parpadeo al cargar: aplicar el tema con un script inline mínimo en `<head>` antes de pintar.
- Verificar ambos temas en cada sección antes de dar algo por terminado.

### 5.2 Estructura de la página (es el "documento escrito")

La página se lee de arriba hacia abajo como un informe. Cada sección explica en texto **y** muestra la ejecución en vivo.

1. **Contexto y problema.** Qué son los Feature Flags, qué hace el sistema y qué significan A, B y C. Cuál es el objetivo (simplificar y demostrar equivalencia).
2. **Código legacy.** Bloque con resaltado y explicación de las tres opciones (`opcion_1`, `opcion_2`, `opcion_3`) y de la función f en notación lógica.
3. **Tabla de verdad del legacy (en vivo).** Filas apareciendo una a una, resaltando qué opción se cumplió. Conclusión: f es verdadera solo en 011, 101 y 111.
4. **Demostración de la simplificación (en vivo).** Pasos con ley y justificación escrita, la matriz de 4.3 llenándose, y una leyenda con las leyes usadas (conmutativa, asociativa, distributiva, complemento, identidad) enunciadas formalmente.
5. **Interpretación.** En palabras: "tiene acceso quien tiene la funcionalidad en Beta (C) y es Administrador o Premium (A ∨ B)". Ayuda a la rúbrica y demuestra comprensión.
6. **Código optimizado.** Bloque con resaltado y explicación de cómo sale directamente de la demostración.
7. **Validación (en vivo).** Barra 0/8 → 8/8, fila por fila, y el panel final del `assert`.
8. **Comparación viejo vs nuevo.** Operaciones, líneas, tablas lado a lado, benchmark y diagrama de compuertas (SVG) de ambos circuitos.
9. **Conclusiones.** Qué se logró, cuánto se redujo, por qué es correcto (demostración formal + verificación exhaustiva con las 2³ = 8 combinaciones).
10. **Cómo ejecutar.** Comandos de Docker y del script, para que la profesora pueda correrlo localmente.

### 5.3 Controles

- Botón **Ejecutar todo** (corre las secciones 3, 4 y 7 en orden) y botón **Repetir** por sección.
- Selector de velocidad (lento / normal / rápido).
- Indicador de estado de conexión SSE y **reconexión automática**; si el stream falla, mostrar un mensaje claro y un botón para reintentar (no una sección vacía).
- Menú lateral o barra de navegación con las 10 secciones.
- Respetar `prefers-reduced-motion` (si está activo, mostrar los resultados sin animación pero igual provenientes del servidor).
- Diseño responsive (se debe leer bien en laptop y celular).
- Opcional barato: hoja de estilos `@media print` para que se pueda imprimir o guardar como PDF desde el navegador.

### 5.4 Requisito no negociable

Los datos de las secciones 3, 4 y 7 **deben venir del backend por SSE en el momento**, no estar precalculados en el HTML. Esa es la parte "en tiempo real" que se va a evaluar visualmente.

## 6. Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
services:
  motor-reglas:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
```

`requirements.txt`: `fastapi`, `uvicorn[standard]`.

Publicación: Cloudflare Tunnel (HTTPS sin abrir puertos) o Caddy/Nginx con dominio propio. Si hay proxy, desactivar el buffering para SSE.

## 7. Orden de trabajo para Claude Code

Cada fase debe quedar funcionando antes de pasar a la siguiente.

1. **`logica.py` y `script_standalone.py`:** legacy, optimizado, tabla de verdad, validación con `assert`, conteo de operaciones con `ast`. Tests con pytest.
2. **`demostracion.py`:** los 8 pasos del apéndice, cada uno con su `fn`. Test: todos los pasos son equivalentes a la original; un paso adulterado falla.
3. **`main.py`:** endpoints y streams SSE de la sección 4.
4. **Frontend base:** HTML con las 10 secciones, CSS con variables y **toggle claro/oscuro funcionando desde el inicio** (no dejarlo para el final).
5. **Conexión en vivo:** tabla, matriz de simplificación y validación animadas con SSE; botones y velocidad.
6. **Comparación:** tablas lado a lado, benchmark y diagrama de compuertas SVG.
7. **Pulido:** textos explicativos completos (es el documento), responsive, accesibilidad, revisión de ambos temas.
8. **Docker:** build, `docker compose up`, prueba local.
9. **Despliegue:** subir al servidor, exponer por HTTPS, probar desde otra red.
10. **ZIP:** armar el entregable y probarlo descomprimiéndolo en una carpeta limpia.

## 8. Criterios de aceptación

- [ ] `docker compose up` levanta todo sin pasos manuales; `python script_standalone.py` también funciona solo.
- [ ] Toggle claro/oscuro funciona, persiste y se ve bien en todas las secciones (incluidos código y SVG).
- [ ] Tabla de verdad, simplificación y validación se ven **en vivo** desde SSE y se pueden repetir.
- [ ] Cada paso de la demostración muestra su ley, su explicación y su verificación computacional (✔ por paso).
- [ ] La comparación viejo vs nuevo muestra operaciones (10 vs 2), líneas, tablas lado a lado, benchmark y compuertas.
- [ ] El código mostrado es idéntico al que se ejecuta (`inspect.getsource`).
- [ ] Alterar a propósito `evaluar_acceso_optimizado` hace fallar la validación y se ve en rojo en la página.
- [ ] La página se entiende completa sin ningún otro documento.
- [ ] La URL pública responde desde una red externa.

## 9. Riesgos

| Riesgo | Mitigación |
|---|---|
| Sin PDF ni video, si el servidor cae no hay respaldo | `restart: unless-stopped`, probar desde otra red, y el ZIP trae `docker-compose.yml` para correrlo localmente |
| SSE cortado por proxy | Cabeceras de no-buffering, reconexión automática, botón de reintento |
| Texto de la demostración con errores | Cada paso se valida con código; revisar cada ley contra los apuntes del curso |
| Se ve mal en uno de los dos temas | Revisar todas las secciones en ambos temas; colores solo vía variables |
| Benchmark que parezca "no mejora" | Explicarlo honestamente en la página (ver 4.6) |

## Apéndice: pasos de la demostración (datos para `demostracion.py`)

f(A,B,C) = (¬A ∧ B ∧ C) ∨ (A ∧ B ∧ C) ∨ (A ∧ ¬B ∧ C)  ⟹  C ∧ (A ∨ B)

| n | Expresión | Ley aplicada |
|---|---|---|
| 0 | (¬A ∧ B ∧ C) ∨ (A ∧ B ∧ C) ∨ (A ∧ ¬B ∧ C) | Expresión original |
| 1 | C ∧ [(¬A ∧ B) ∨ (A ∧ B) ∨ (A ∧ ¬B)] | Conmutativa, asociativa y distributiva (factorizar C) |
| 2 | C ∧ [(B ∧ ¬A) ∨ (B ∧ A) ∨ (A ∧ ¬B)] | Conmutativa |
| 3 | C ∧ [(B ∧ (¬A ∨ A)) ∨ (A ∧ ¬B)] | Distributiva (factorizar B) |
| 4 | C ∧ [(B ∧ T) ∨ (A ∧ ¬B)] | Complemento (¬A ∨ A ≡ T) |
| 5 | C ∧ [B ∨ (A ∧ ¬B)] | Identidad (B ∧ T ≡ B) |
| 6 | C ∧ [(B ∨ A) ∧ (B ∨ ¬B)] | Distributiva (∨ sobre ∧) |
| 7 | C ∧ [(B ∨ A) ∧ T] | Complemento (B ∨ ¬B ≡ T) |
| 8 | C ∧ (A ∨ B) | Identidad y conmutativa |

Si Claude Code ve conveniente dividir un paso en dos para mayor rigor (por ejemplo separar "conmutativa/asociativa" de "distributiva" en el paso 1), puede hacerlo, siempre que cada subpaso tenga su ley y su `fn` verificable.
