(function () {
  "use strict";

  // ---------- Tema claro/oscuro ----------
  const root = document.documentElement;
  const btnTema = document.getElementById("toggle-tema");

  function aplicarTema(tema) {
    root.setAttribute("data-theme", tema);
    localStorage.setItem("tema", tema);
    btnTema.textContent = tema === "dark" ? "☀️" : "🌙";
    btnTema.setAttribute("aria-pressed", tema === "dark" ? "true" : "false");
    btnTema.setAttribute("aria-label", tema === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
  }

  aplicarTema(root.getAttribute("data-theme") || "light");

  btnTema.addEventListener("click", function () {
    const actual = root.getAttribute("data-theme");
    aplicarTema(actual === "dark" ? "light" : "dark");
  });

  // ---------- Resaltado de sintaxis mínimo, sin dependencias externas ----------
  function resaltarPython(codigo) {
    const esc = codigo
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    const palabrasClave = /\b(def|return|and|or|not|if|else|elif|for|in|import|from|True|False|None)\b/g;
    return esc
      .replace(/(#.*$)/gm, '<span class="tok-com">$1</span>')
      .replace(palabrasClave, '<span class="tok-kw">$1</span>')
      .replace(/\b(\d+)\b/g, '<span class="tok-num">$1</span>')
      .replace(/\bdef (\w+)/g, 'def <span class="tok-fn">$1</span>');
  }

  function ponerCodigo(id, codigo) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = resaltarPython(codigo);
  }

  async function cargarCodigo() {
    try {
      const resp = await fetch("/api/codigo");
      const datos = await resp.json();
      ponerCodigo("codigo-legacy", datos.legacy);
      ponerCodigo("codigo-legacy-vivo", datos.legacy);
      ponerCodigo("codigo-optimizado", datos.optimizado);
      ponerCodigo("codigo-optimizado-vivo", datos.legacy + "\n" + datos.optimizado);
    } catch (e) {
      document.getElementById("codigo-legacy").textContent = "No se pudo cargar el código.";
    }
  }

  async function cargarComparacion() {
    const cont = document.getElementById("comparacion-resumen");
    try {
      const resp = await fetch("/api/comparacion");
      const d = await resp.json();
      const filas = d.tabla.map(f => `
        <tr class="${f.coincide ? "fila-ok" : "fila-fail"}">
          <td>${f.i}</td><td>${f.A}</td><td>${f.B}</td><td>${f.C}</td>
          <td>${f.legacy}</td><td>${f.optimizado}</td><td>${f.coincide ? "✔" : "✘"}</td>
        </tr>`).join("");
      cont.innerHTML = `
        <h3>Operaciones lógicas</h3>
        <p>Legacy: <strong>${d.operaciones.legacy}</strong> &nbsp;·&nbsp;
           Optimizado: <strong>${d.operaciones.optimizado}</strong> &nbsp;·&nbsp;
           Reducción: <strong>${d.operaciones.reduccion_pct}%</strong></p>
        <p class="texto-suave">${d.operaciones.criterio}</p>
        <h3>Líneas de código</h3>
        <p>Legacy: ${d.lineas.legacy} líneas, ${d.lineas.variables_intermedias.legacy} variables intermedias &nbsp;·&nbsp;
           Optimizado: ${d.lineas.optimizado} línea, ${d.lineas.variables_intermedias.optimizado} variables intermedias</p>
        <h3>Benchmark (${d.benchmark.iteraciones.toLocaleString("es")} llamadas)</h3>
        <p>Legacy: ${d.benchmark.segundos_legacy.toFixed(4)} s &nbsp;·&nbsp;
           Optimizado: ${d.benchmark.segundos_optimizado.toFixed(4)} s</p>
        <p class="texto-suave">${d.benchmark.nota}</p>
        <h3>Tabla lado a lado</h3>
        <div class="tabla-scroll">
          <table>
            <thead><tr><th>#</th><th>A</th><th>B</th><th>C</th><th>legacy</th><th>optimizado</th><th>coincide</th></tr></thead>
            <tbody>${filas}</tbody>
          </table>
        </div>`;
    } catch (e) {
      cont.textContent = "No se pudo cargar la comparación.";
    }
  }

  // ---------- Velocidad ----------
  function velocidadActual() {
    return document.getElementById("velocidad").value;
  }

  // ---------- Manejo genérico de streams SSE con reconexión ----------
  function crearStream(nombre, onEvento, onFin) {
    const cajaEstado = document.querySelector(`[data-stream="${nombre}"]`);
    const punto = cajaEstado ? cajaEstado.querySelector(".punto") : null;
    const texto = cajaEstado ? cajaEstado.querySelector(".texto-estado") : null;
    let es = null;
    let intentos = 0;

    function marcar(estado, msg) {
      if (!punto || !texto) return;
      punto.classList.remove("activo", "error");
      if (estado === "ok") punto.classList.add("activo");
      if (estado === "error") punto.classList.add("error");
      texto.textContent = msg;
    }

    function conectar() {
      if (es) es.close();
      marcar("conectando", "conectando…");
      const url = `/api/stream/${nombre}?velocidad=${velocidadActual()}`;
      es = new EventSource(url);

      es.onopen = function () { intentos = 0; marcar("ok", "en vivo"); };

      es.onmessage = function (ev) {
        const data = JSON.parse(ev.data);
        if (data.fin || data.assert) {
          marcar("ok", "completado");
          es.close();
          if (onFin) onFin(data);
          return;
        }
        onEvento(data);
      };

      es.onerror = function () {
        marcar("error", "stream interrumpido — reintentando…");
        es.close();
        intentos += 1;
        if (intentos <= 5) {
          setTimeout(conectar, 1200);
        } else {
          marcar("error", "no se pudo conectar. Usa 'Repetir'.");
        }
      };
    }

    return { conectar, cerrar: () => es && es.close() };
  }

  // ---------- Sección 3: tabla de verdad ----------
  const cuerpoTabla = document.querySelector("#tabla-legacy tbody");
  function pintarFilaTabla(f) {
    const tr = document.createElement("tr");
    tr.className = f.legacy ? "fila-ok" : "";
    tr.innerHTML = `<td>${f.i}</td><td>${f.A}</td><td>${f.B}</td><td>${f.C}</td>
      <td>${f.opcion_1 ? "✔" : "—"}</td><td>${f.opcion_2 ? "✔" : "—"}</td><td>${f.opcion_3 ? "✔" : "—"}</td>
      <td><strong>${f.legacy}</strong></td>`;
    cuerpoTabla.appendChild(tr);
  }
  const streamTabla = crearStream("tabla", pintarFilaTabla, (fin) => {
    document.getElementById("conclusion-tabla").textContent = fin.conclusion || "";
  });

  function repetirTabla() {
    cuerpoTabla.innerHTML = "";
    document.getElementById("conclusion-tabla").textContent = "";
    streamTabla.conectar();
  }

  // ---------- Sección 4: demostración ----------
  const cuerpoDemo = document.querySelector("#tabla-demostracion tbody");
  const transcriptDemo = document.getElementById("transcript-demostracion");
  function pintarFilaDemo(p) {
    const tr = document.createElement("tr");
    const bits = p.columna.map(b => `<td class="bit bit-${b}">${b}</td>`).join("");
    tr.innerHTML = `<td>${p.n}</td><td>${p.expr}</td><td><span class="paso-ley">${p.ley}</span><br><small class="texto-suave">${p.detalle}</small></td>
      ${bits}<td>${p.igual_a_original ? '<span class="pill pill-ok">✔</span>' : '<span class="pill pill-fail">✘</span>'}</td>`;
    if (!p.igual_a_original) tr.classList.add("fila-fail");
    cuerpoDemo.appendChild(tr);

    const bloque = document.createElement("span");
    bloque.className = "paso-transcript";
    bloque.innerHTML = `<span class="tok-com"># paso ${p.n} — ${p.ley}</span>${p.expr}`;
    transcriptDemo.appendChild(bloque);
    transcriptDemo.scrollTop = transcriptDemo.scrollHeight;
  }
  const streamDemo = crearStream("demostracion", pintarFilaDemo, (fin) => {
    const el = document.getElementById("resultado-demostracion");
    el.innerHTML = fin.todos_los_pasos_validos
      ? `<span class="pill pill-ok">✔ Todos los pasos preservan la tabla de verdad</span> — forma final: <strong>${fin.forma_final}</strong>`
      : `<span class="pill pill-fail">✘ Algún paso no coincide con la expresión original</span>`;
  });

  function repetirDemo() {
    cuerpoDemo.innerHTML = "";
    transcriptDemo.innerHTML = "";
    document.getElementById("resultado-demostracion").innerHTML = "";
    streamDemo.conectar();
  }

  // ---------- Sección 7: validación ----------
  const cuerpoValidacion = document.querySelector("#tabla-validacion tbody");
  let contadorValidacion = 0;
  function pintarFilaValidacion(f) {
    contadorValidacion += 1;
    document.getElementById("barra-validacion").style.width = `${(contadorValidacion / 8) * 100}%`;
    document.getElementById("contador-validacion").textContent = `${contadorValidacion}/8`;
    const tr = document.createElement("tr");
    tr.className = f.coincide ? "fila-ok" : "fila-fail";
    tr.innerHTML = `<td>${f.i}</td><td>${f.A}</td><td>${f.B}</td><td>${f.C}</td>
      <td>${f.legacy}</td><td>${f.optimizado}</td><td>${f.coincide ? "✔" : "✘"}</td>`;
    cuerpoValidacion.appendChild(tr);
  }
  const streamValidacion = crearStream("validacion", pintarFilaValidacion, (fin) => {
    const el = document.getElementById("resultado-assert");
    if (fin.assert === "ok") {
      el.innerHTML = '<span class="pill pill-ok">✔ assert bool(legacy) == bool(optimizado) — las 8 combinaciones coinciden</span>';
    } else {
      el.innerHTML = `<span class="pill pill-fail">✘ assert falló: ${fin.detalle}</span>`;
    }
  });

  function repetirValidacion() {
    cuerpoValidacion.innerHTML = "";
    contadorValidacion = 0;
    document.getElementById("barra-validacion").style.width = "0%";
    document.getElementById("contador-validacion").textContent = "0/8";
    document.getElementById("resultado-assert").innerHTML = "";
    streamValidacion.conectar();
  }

  document.querySelectorAll("[data-repetir]").forEach(btn => {
    btn.addEventListener("click", () => {
      const cual = btn.getAttribute("data-repetir");
      if (cual === "tabla") repetirTabla();
      if (cual === "demostracion") repetirDemo();
      if (cual === "validacion") repetirValidacion();
    });
  });

  document.getElementById("btn-ejecutar-todo").addEventListener("click", async () => {
    repetirTabla();
    await new Promise(r => setTimeout(r, 300));
    repetirDemo();
    await new Promise(r => setTimeout(r, 300));
    repetirValidacion();
  });

  document.getElementById("velocidad").addEventListener("change", () => {
    // La próxima conexión (manual o "Ejecutar todo") usará la nueva velocidad.
  });

  // ---------- Navegación activa ----------
  const enlaces = Array.from(document.querySelectorAll("nav.pills a"));
  const secciones = enlaces.map(a => document.querySelector(a.getAttribute("href")));
  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach(e => {
      if (e.isIntersecting) {
        enlaces.forEach(a => a.classList.remove("activo"));
        const idx = secciones.indexOf(e.target);
        if (idx >= 0) enlaces[idx].classList.add("activo");
      }
    });
  }, { rootMargin: "-20% 0px -70% 0px" });
  secciones.forEach(s => s && observador.observe(s));

  // ---------- Altura real de la barra superior (header + nav) ----------
  const barra = document.querySelector(".barra-superior");
  function actualizarAltoBarra() {
    if (barra) root.style.setProperty("--barra-h", `${barra.offsetHeight}px`);
  }
  actualizarAltoBarra();
  window.addEventListener("resize", actualizarAltoBarra);
  if (window.ResizeObserver && barra) {
    new ResizeObserver(actualizarAltoBarra).observe(barra);
  }

  // ---------- Arranque ----------
  cargarCodigo();
  cargarComparacion();
  repetirTabla();
})();
