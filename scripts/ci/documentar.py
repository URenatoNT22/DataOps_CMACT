#!/usr/bin/env python3
"""
Documentación automática generada desde el DACPAC y los resultados del pipeline.

  cambio  -> Reporte de un cambio (Pull Request): comentario Markdown para el PR + reporte HTML completo.
  sitio   -> Diccionario de datos navegable (HTML) del modelo vigente, para publicar en GitHub Pages.

No requiere conexión a la base: todo sale del modelo del DACPAC, del Deploy Report y de los JSON
que generan las otras etapas (riesgo, pruebas, smoke, jobs).
"""
import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modelo_dacpac as md  # noqa: E402

LIMITE_COMENTARIO = 60000
ICONO_RIESGO = {"ESTANDAR": "🟢", "SENSIBLE": "🟠", "PROHIBIDO": "🔴"}
TEXTO_RIESGO = {"ESTANDAR": "ESTÁNDAR", "SENSIBLE": "SENSIBLE", "PROHIBIDO": "PROHIBIDO"}
ICONO_ACCION = {"AGREGADO": "🆕", "MODIFICADO": "✏️", "ELIMINADO": "🗑️"}

CSS = """
:root{--bg:#f7f7f5;--card:#ffffff;--tx:#1d1d1b;--tx2:#5f5e5a;--bd:#e3e1da;--ac:#185fa5;--acbg:#e6f1fb;
--ok:#3b6d11;--okbg:#eaf3de;--warn:#854f0b;--warnbg:#faeeda;--err:#a32d2d;--errbg:#fcebeb;--code:#f1efe8;
--add:#eaf3de;--addtx:#27500a;--del:#fcebeb;--deltx:#791f1f}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#1f1f1d;--tx:#ecebe6;--tx2:#a9a79f;--bd:#34332f;
--ac:#85b7eb;--acbg:#0c2a47;--ok:#97c459;--okbg:#1d2e0e;--warn:#efa027;--warnbg:#3a2605;--err:#f09595;--errbg:#3d1515;
--code:#262624;--add:#1d2e0e;--addtx:#c0dd97;--del:#3d1515;--deltx:#f7c1c1}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 60px}
header.top{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:flex-end;margin-bottom:22px}
h1{font-size:24px;margin:0 0 4px;font-weight:600}h2{font-size:18px;margin:34px 0 12px;font-weight:600}
h3{font-size:15px;margin:0;font-weight:600}.sub{color:var(--tx2);font-size:14px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px 18px;margin-bottom:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.kpi .l{color:var(--tx2);font-size:12px;text-transform:uppercase;letter-spacing:.04em}.kpi .v{font-size:20px;font-weight:600;margin-top:2px}
.pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.p-ok{background:var(--okbg);color:var(--ok)}.p-warn{background:var(--warnbg);color:var(--warn)}.p-err{background:var(--errbg);color:var(--err)}
.p-info{background:var(--acbg);color:var(--ac)}.p-mut{background:var(--code);color:var(--tx2)}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--bd);vertical-align:top}
th{color:var(--tx2);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
code,pre{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:13px}code{background:var(--code);padding:1px 5px;border-radius:4px}
pre{background:var(--code);padding:12px;border-radius:8px;overflow:auto;max-height:520px;margin:8px 0 0}
.diff{background:var(--code);border-radius:8px;overflow:auto;max-height:560px;margin-top:10px;font-family:ui-monospace,Consolas,monospace;font-size:12.5px}
.diff div{padding:0 12px;white-space:pre}.diff .a{background:var(--add);color:var(--addtx)}.diff .d{background:var(--del);color:var(--deltx)}
.diff .h{color:var(--ac);padding-top:6px}
ul{margin:6px 0;padding-left:20px}a{color:var(--ac)}details>summary{cursor:pointer;color:var(--ac);margin-top:8px}
.obj-head{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}
.muted{color:var(--tx2)}.mermaid{background:var(--card)}
input.search{width:100%;padding:10px 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--tx);font-size:15px}
nav.toc{columns:3 220px;font-size:14px}nav.toc a{text-decoration:none;display:block;padding:1px 0}
footer{margin-top:40px;color:var(--tx2);font-size:12px}
"""

MERMAID_JS = """<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({startOnLoad:true,theme:window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'neutral'});
</script>"""


def e(t):
    return html.escape(str(t if t is not None else ""))


def leer_json(ruta):
    if ruta and Path(ruta).exists():
        try:
            return json.loads(Path(ruta).read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def simple(nombre):
    return ".".join(md._partes(nombre)) or nombre


def mermaid_id(nombre):
    return re.sub(r"\W", "_", simple(nombre))


def grafo_mermaid(cambiados, aristas, objetos, jobs):
    if not cambiados:
        return ""
    lineas = ["graph LR"]
    nodos = set(cambiados) | {a for a, _ in aristas} | {b for _, b in aristas}
    for n in sorted(nodos):
        tipo = objetos[n].tipo if n in objetos else ""
        etiqueta = f"{simple(n)}<br/>{tipo}"
        lineas.append(f'  {mermaid_id(n)}["{etiqueta}"]')
    for a, b in sorted(aristas):
        lineas.append(f"  {mermaid_id(a)} --> {mermaid_id(b)}")
    for j in jobs:
        jid = "job_" + re.sub(r"\W", "_", j["job"])
        lineas.append(f'  {jid}(["⏱ Job: {j["job"]}"])')
        lineas.append(f"  {mermaid_id(j['objeto'])} -.-> {jid}")
    for n in cambiados:
        lineas.append(f"  style {mermaid_id(n)} stroke:#d85a30,stroke-width:3px")
    return "\n".join(lineas)


def resumen_pruebas(*conjuntos):
    total = ok = adv = mal = 0
    for c in conjuntos:
        for r in (c or {}).get("resultados", []):
            total += 1
            if r["estado"] in ("OK", "OMITIDA"):
                ok += 1
            elif r["estado"] == "ADVERTENCIA":
                adv += 1
            else:
                mal += 1
    return total, ok, adv, mal


def advertencias_build(ruta):
    if not ruta or not Path(ruta).exists():
        return []
    vistos, salida = set(), []
    for linea in Path(ruta).read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.search(r"([^\s(]+\.sql)\((\d+),\d+(?:,\d+,\d+)?\):\s*(?:Build|StaticCodeAnalysis)?\s*warning\s+([A-Z]+\d+)\s*:\s*(.+?)(?:\s+\[.*\])?$", linea)
        if m:
            clave = (Path(m.group(1)).name, m.group(2), m.group(3))
            if clave not in vistos:
                vistos.add(clave)
                salida.append({"archivo": Path(m.group(1)).name, "linea": m.group(2), "regla": m.group(3), "mensaje": m.group(4)})
    return salida


# --------------------------------------------------------------------------------------------
#  cambio
# --------------------------------------------------------------------------------------------
def cmd_cambio(a):
    ctx = leer_json(a.contexto) or {}
    nuevo = md.cargar(a.dacpac_nuevo)
    base = md.cargar(a.dacpac_base) if a.dacpac_base and Path(a.dacpac_base).exists() else {}
    cambios = md.comparar(base, nuevo)
    riesgo = leer_json(a.riesgo) or {"nivel": "ESTANDAR", "motivos": [], "resumen_operaciones": {},
                                     "evaluado_contra_destino": False, "alertas": []}
    pruebas = leer_json(a.pruebas)
    smoke = leer_json(a.smoke)
    jobs = (leer_json(a.jobs) or {}).get("jobs", [])
    upgrade = leer_json(a.upgrade) or {}
    script = Path(a.script).read_text(encoding="utf-8-sig") if a.script and Path(a.script).exists() else ""
    avisos = advertencias_build(a.build_log)

    cambiados = [c["objeto"] for c in cambios if c["accion"] != "ELIMINADO"]
    universo = {**base, **nuevo}
    aguas_abajo, aristas = md.impacto(universo, set(c["objeto"] for c in cambios))
    jobs_rel = [j for j in jobs if j["objeto"] in set(c["objeto"] for c in cambios) | aguas_abajo]
    grafo = grafo_mermaid(set(c["objeto"] for c in cambios), aristas, universo, jobs_rel)
    total, ok, adv, mal = resumen_pruebas(pruebas, smoke)
    nivel = riesgo.get("nivel", "ESTANDAR")
    destino = riesgo.get("destino") or ctx.get("destino", "")
    evaluado = riesgo.get("evaluado_contra_destino")
    perdida = riesgo.get("perdida_datos_posible", False)

    # ---------------- Markdown (comentario del PR) ----------------
    md_l = ["<!-- reporte-dataops -->", "## 🤖 Reporte automático del cambio", ""]
    md_l += ["| | |", "|---|---|",
             f"| **Riesgo** | {ICONO_RIESGO.get(nivel,'')} **{TEXTO_RIESGO.get(nivel, nivel)}** |",
             (f"| **Destino evaluado** | `{destino}` (base real) |" if evaluado else
              f"| **Destino evaluado** | base efímera de CI · ⚠️ sin conexión a `{ctx.get('destino') or 'destino'}` (¿ngrok activo?) |"),
             f"| **Build y análisis de código** | ✅ compila · {len(avisos)} advertencia(s) de análisis |",
             f"| **Pruebas** | {'✅' if mal == 0 else '❌'} {ok}/{total} OK" + (f" · ⚠️ {adv} advertencia(s)" if adv else "") + (f" · ❌ {mal} falla(s)" if mal else "") + " |",
             f"| **Prueba de actualización con datos** | {upgrade.get('texto','n/d')} |",
             f"| **Posible pérdida de datos** | {'⚠️ **SÍ**' if perdida else 'No'} |",
             f"| **Objetos modificados / impactados** | {len(cambios)} / {len(aguas_abajo)} aguas abajo · {len(jobs_rel)} job(s) |", ""]
    if riesgo.get("motivos"):
        md_l.append("**Motivos de la clasificación**")
        md_l += [f"- {ICONO_RIESGO.get(m['nivel'],'')} {m['motivo']}" for m in riesgo["motivos"][:25]]
        md_l.append("")
    md_l.append("### Qué cambia")
    if cambios:
        md_l += ["| | Objeto | Tipo | Detalle |", "|---|---|---|---|"]
        for c in cambios:
            det = "<br>".join(c["detalle"]) if c["detalle"] else ("Objeto nuevo" if c["accion"] == "AGREGADO" else "Objeto eliminado" if c["accion"] == "ELIMINADO" else "")
            md_l.append(f"| {ICONO_ACCION[c['accion']]} {c['accion'].title()} | `{simple(c['objeto'])}` | {c['tipo']} | {det} |")
    else:
        md_l.append("_Sin cambios en el modelo de base de datos (el PR solo modifica otros archivos)._")
    md_l.append("")
    if aguas_abajo or jobs_rel:
        md_l.append("### Impacto aguas abajo")
        if aguas_abajo:
            md_l.append("Objetos que dependen de lo modificado (se validan en las pruebas): " +
                        ", ".join(f"`{simple(x)}`" for x in sorted(aguas_abajo)))
        if jobs_rel:
            md_l.append("")
            md_l.append("Jobs de SQL Agent en el destino que usan estos objetos:")
            md_l += [f"- ⏱ **{j['job']}** → paso _{j['paso']}_ usa `{simple(j['objeto'])}`" for j in jobs_rel]
        md_l.append("")
    if grafo:
        md_l += ["```mermaid", grafo, "```", ""]
    ops = riesgo.get("resumen_operaciones") or {}
    if ops:
        md_l.append("### Plan de despliegue (SqlPackage)")
        md_l.append(" · ".join(f"**{k}**: {v}" for k, v in sorted(ops.items())))
        md_l.append("")
    if pruebas or smoke:
        md_l += ["### Pruebas", "| Prueba | Resultado | Detalle |", "|---|---|---|"]
        for conj in (pruebas, smoke):
            for r in (conj or {}).get("resultados", []):
                icono = {"OK": "✅", "ADVERTENCIA": "⚠️", "OMITIDA": "➖"}.get(r["estado"], "❌")
                det = r.get("descripcion") or r.get("detalle") or ""
                if r.get("filas_con_falla"):
                    det += f" ({r['filas_con_falla']} filas)"
                md_l.append(f"| `{r['prueba']}` | {icono} {r['estado']} | {det} |")
        md_l.append("")
    if avisos:
        md_l.append("<details><summary>Advertencias del análisis de código ({})</summary>\n".format(len(avisos)))
        md_l += [f"- `{x['regla']}` {x['archivo']}:{x['linea']} — {x['mensaje']}" for x in avisos[:40]]
        md_l.append("\n</details>\n")
    if script:
        # se omite el preámbulo SQLCMD que genera SqlPackage: se muestra desde el USE de la base
        m_use = re.search(r"^USE \[\$\(DatabaseName\)\];\s*$", script, flags=re.M)
        cuerpo_script = script[m_use.end():].strip() if m_use else script
        recorte = cuerpo_script if len(cuerpo_script) < 25000 else cuerpo_script[:25000] + "\n-- ... (recortado, ver reporte HTML)"
        md_l += ["<details><summary>Script SQL que se ejecutará en el destino</summary>", "", "```sql", recorte, "```", "</details>", ""]
    md_l.append("### Siguiente paso")
    base_ref = ctx.get("base", "")
    if nivel == "PROHIBIDO":
        md_l.append("🔴 **Este cambio no puede desplegarse por el pipeline.** Retire lo indicado arriba; si se requiere, TI lo gestiona por su canal.")
    elif base_ref == "main":
        md_l.append("- [ ] Revisión y aprobación del **Jefe IN**")
        if nivel == "SENSIBLE":
            md_l.append("- [ ] Visto previo de **TI / DBA** (cambio sensible)")
            if perdida:
                md_l.append("- [ ] TI agrega la etiqueta `ti/autoriza-perdida-datos` si acepta la pérdida de datos señalada")
        md_l.append("- Al hacer merge: despliegue automático a **PROD**, release versionado y auditoría posterior de TI.")
    else:
        md_l.append("- [ ] Revisión y aprobación de **Data Engineering**")
        md_l.append("- Al hacer merge: despliegue automático a **DEV**.")
    if ctx.get("run_url"):
        md_l += ["", f"📄 [Reporte HTML completo y artefactos (DACPAC, script, deploy report)]({ctx['run_url']}) · generado {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC"]
    texto_md = "\n".join(md_l)
    if len(texto_md) > LIMITE_COMENTARIO:
        texto_md = texto_md[:LIMITE_COMENTARIO] + "\n\n_(reporte recortado: ver el HTML completo en los artefactos)_"
    Path(a.salida_md).write_text(texto_md, encoding="utf-8")

    # ---------------- HTML ----------------
    pill_r = {"ESTANDAR": "p-ok", "SENSIBLE": "p-warn", "PROHIBIDO": "p-err"}.get(nivel, "p-mut")
    h = [f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
         f"<title>Reporte de cambio {e(ctx.get('titulo',''))}</title><style>{CSS}</style></head><body><div class='wrap'>",
         "<header class='top'><div>",
         f"<div class='sub'>Reporte automático de cambio · {e(ctx.get('repo',''))}</div>",
         f"<h1>{('PR #' + str(ctx['pr']) + ' · ') if ctx.get('pr') else ''}{e(ctx.get('titulo','Cambio'))}</h1>",
         f"<div class='sub'>{e(ctx.get('head',''))} → {e(ctx.get('base',''))} · autor {e(ctx.get('autor',''))} · commit <code>{e((ctx.get('sha') or '')[:8])}</code></div>",
         f"</div><span class='pill {pill_r}' style='font-size:14px;padding:6px 14px'>Riesgo {TEXTO_RIESGO.get(nivel, nivel)}</span></header>",
         "<div class='grid'>"]
    for l, v in [("Objetos modificados", len(cambios)), ("Impactados aguas abajo", len(aguas_abajo)),
                 ("Jobs relacionados", len(jobs_rel)), ("Pruebas OK", f"{ok}/{total}"),
                 ("Pérdida de datos", "Posible" if perdida else "No"), ("Destino", destino or "n/d")]:
        h.append(f"<div class='card kpi'><div class='l'>{e(l)}</div><div class='v'>{e(v)}</div></div>")
    h.append("</div>")
    if riesgo.get("motivos"):
        h.append("<h2>Clasificación de riesgo</h2><div class='card'><ul>")
        for m in riesgo["motivos"]:
            cls = {"ESTANDAR": "p-ok", "SENSIBLE": "p-warn", "PROHIBIDO": "p-err"}[m["nivel"]]
            h.append(f"<li><span class='pill {cls}'>{m['nivel']}</span> {e(m['motivo'])}</li>")
        h.append("</ul></div>")
    h.append("<h2>Qué cambia</h2>")
    if not cambios:
        h.append("<div class='card muted'>Sin cambios en el modelo de base de datos.</div>")
    for c in cambios:
        acc = {"AGREGADO": "p-ok", "MODIFICADO": "p-info", "ELIMINADO": "p-err"}[c["accion"]]
        o = universo.get(c["objeto"])
        h.append(f"<div class='card'><div class='obj-head'><h3><code>{e(simple(c['objeto']))}</code> <span class='muted'>· {e(c['tipo'])}</span></h3>"
                 f"<span class='pill {acc}'>{c['accion']}</span></div>")
        if o and o.descripcion:
            h.append(f"<div class='muted' style='margin-top:4px'>{e(o.descripcion)}</div>")
        if c["detalle"]:
            h.append("<ul>" + "".join(f"<li>{e(d)}</li>" for d in c["detalle"]) + "</ul>")
        if c["diff"]:
            h.append("<div class='diff'>")
            for linea in c["diff"]:
                cls = "h" if linea.startswith(("@@", "---", "+++")) else "a" if linea.startswith("+") else "d" if linea.startswith("-") else ""
                h.append(f"<div class='{cls}'>{e(linea)}</div>")
            h.append("</div>")
        h.append("</div>")
    if grafo:
        h.append("<h2>Impacto y dependencias</h2><div class='card'><pre class='mermaid'>" + e(grafo) + "</pre></div>")
    if jobs_rel:
        h.append("<div class='card'><h3>Jobs de SQL Agent relacionados</h3><table><tr><th>Job</th><th>Paso</th><th>Objeto</th><th>Habilitado</th></tr>")
        for j in jobs_rel:
            h.append(f"<tr><td>{e(j['job'])}</td><td>{e(j['paso'])}</td><td><code>{e(simple(j['objeto']))}</code></td><td>{'Sí' if j['habilitado'] else 'No'}</td></tr>")
        h.append("</table></div>")
    if ops or riesgo.get("alertas"):
        h.append("<h2>Plan de despliegue (Deploy Report)</h2><div class='card'><table><tr><th>Operación</th><th>Objeto</th><th>Tipo</th></tr>")
        for op, items in sorted((riesgo.get("operaciones") or {}).items()):
            for it in items:
                h.append(f"<tr><td>{e(op)}</td><td><code>{e(it['objeto'])}</code></td><td>{e(it['tipo'])}</td></tr>")
        h.append("</table>")
        for al in riesgo.get("alertas", []):
            h.append(f"<p><span class='pill p-warn'>{e(al['alerta'])}</span> {e(al['detalle'])}</p>")
        h.append("</div>")
    if pruebas or smoke:
        h.append("<h2>Pruebas</h2><div class='card'><table><tr><th>Prueba</th><th>Resultado</th><th>Detalle</th></tr>")
        for conj in (pruebas, smoke):
            for r in (conj or {}).get("resultados", []):
                cls = {"OK": "p-ok", "ADVERTENCIA": "p-warn", "OMITIDA": "p-mut"}.get(r["estado"], "p-err")
                det = r.get("descripcion") or r.get("detalle") or ""
                muestra = r.get("muestra") if r.get("filas_con_falla") else None
                h.append(f"<tr><td><code>{e(r['prueba'])}</code></td><td><span class='pill {cls}'>{e(r['estado'])}</span></td><td>{e(det)}"
                         + (f"<pre>{e(json.dumps(muestra, ensure_ascii=False, default=str, indent=1))}</pre>" if muestra else "") + "</td></tr>")
        h.append("</table></div>")
    if avisos:
        h.append(f"<h2>Análisis de código ({len(avisos)} advertencias)</h2><div class='card'><table><tr><th>Regla</th><th>Archivo</th><th>Mensaje</th></tr>")
        for x in avisos:
            h.append(f"<tr><td><code>{e(x['regla'])}</code></td><td>{e(x['archivo'])}:{e(x['linea'])}</td><td>{e(x['mensaje'])}</td></tr>")
        h.append("</table></div>")
    if script:
        h.append(f"<h2>Script SQL que se ejecutará</h2><div class='card'><pre>{e(script)}</pre></div>")
    h.append(f"<footer>Generado automáticamente por el pipeline DataOps · {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC"
             + (f" · <a href='{e(ctx['run_url'])}'>ejecución</a>" if ctx.get("run_url") else "") + "</footer>")
    h.append("</div>" + MERMAID_JS + "</body></html>")
    Path(a.salida_html).write_text("\n".join(h), encoding="utf-8")
    Path(a.salida_html).with_suffix(".json").write_text(json.dumps(
        {"cambios": [{k: v for k, v in c.items() if k != "diff"} for c in cambios],
         "impactados": sorted(aguas_abajo), "jobs": jobs_rel, "riesgo": nivel}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reporte: {len(cambios)} cambios, {len(aguas_abajo)} impactados, riesgo {nivel}")


# --------------------------------------------------------------------------------------------
#  sitio (diccionario de datos)
# --------------------------------------------------------------------------------------------
def historial_git(ruta_proyecto, objetos):
    """Últimos commits que tocaron el archivo de cada objeto."""
    archivos = {}
    for sql in Path(ruta_proyecto).rglob("*.sql"):
        texto = sql.read_text(encoding="utf-8-sig", errors="ignore")
        for n, o in objetos.items():
            patron = rf"CREATE\s+(?:OR\s+ALTER\s+)?(?:TABLE|VIEW|PROCEDURE|PROC|FUNCTION)\s+\[?{re.escape(o.esquema)}\]?\.\[?{re.escape(o.corto)}\]?"
            if re.search(patron, texto, flags=re.I):
                archivos[n] = sql
    hist = {}
    for n, f in archivos.items():
        try:
            out = subprocess.run(["git", "log", "-n", "8", "--format=%h|%ad|%an|%s", "--date=short", "--", str(f)],
                                 capture_output=True, text=True, check=True).stdout
            hist[n] = [dict(zip(("sha", "fecha", "autor", "mensaje"), l.split("|", 3))) for l in out.splitlines() if l]
        except Exception:
            hist[n] = []
    return archivos, hist


def cmd_sitio(a):
    objetos = md.cargar(a.dacpac)
    inverso = md.usado_por(objetos)
    archivos, hist = historial_git(a.proyecto, objetos)
    releases = leer_json(a.releases) or []
    version = a.version or ""
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    por_esquema = {}
    for n, o in sorted(objetos.items()):
        por_esquema.setdefault(o.esquema, []).append(o)

    h = ["<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
         f"<title>Diccionario de datos BI</title><style>{CSS}</style></head><body><div class='wrap'>",
         "<header class='top'><div><div class='sub'>Ambiente analítico · documentación generada desde el DACPAC</div>",
         f"<h1>Diccionario de datos</h1><div class='sub'>Versión en producción <b>{e(version)}</b> · actualizado {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC</div></div>",
         f"<span class='pill p-info'>{len(objetos)} objetos</span></header>",
         "<input class='search' id='q' placeholder='Buscar tabla, vista, columna o descripción…' oninput='filtrar(this.value)'>",
         "<h2>Contenido</h2><div class='card'><nav class='toc'>"]
    for esq, objs in por_esquema.items():
        for o in objs:
            h.append(f"<a href='#{mermaid_id(o.nombre)}'><code>{e(o.nombre_simple)}</code> <span class='muted'>· {e(o.tipo)}</span></a>")
    h.append("</nav></div>")
    if releases:
        h.append("<h2>Historial de versiones en producción</h2><div class='card'><table><tr><th>Versión</th><th>Fecha</th><th>Resumen</th></tr>")
        for r in releases[:15]:
            h.append(f"<tr><td><a href='{e(r.get('url',''))}'>{e(r.get('tag',''))}</a></td><td>{e((r.get('fecha') or '')[:10])}</td><td>{e(r.get('titulo',''))}</td></tr>")
        h.append("</table></div>")
    for esq, objs in por_esquema.items():
        h.append(f"<h2>Esquema <code>{e(esq)}</code></h2>")
        for o in objs:
            h.append(f"<div class='card obj' id='{mermaid_id(o.nombre)}'><div class='obj-head'><h3><code>{e(o.nombre_simple)}</code></h3>"
                     f"<span class='pill p-mut'>{e(o.tipo)}</span></div>")
            h.append(f"<p class='{'muted' if not o.descripcion else ''}'>{e(o.descripcion) or '⚠️ Sin descripción (agregar MS_Description)'}</p>")
            if o.clave_primaria:
                h.append(f"<div class='sub'>Clave primaria: <code>{e(', '.join(o.clave_primaria))}</code></div>")
            if o.parametros:
                h.append(f"<div class='sub'>Parámetros: <code>{e(', '.join(o.parametros))}</code></div>")
            if o.columnas:
                h.append("<table style='margin-top:8px'><tr><th>Columna</th><th>Tipo</th><th>Nulo</th><th>Descripción</th></tr>")
                for c in o.columnas:
                    tipo = c.tipo or ("calculada" if c.calculada else "")
                    extra = (" · identidad" if c.identidad else "") + (f" · default {c.default}" if c.default else "")
                    pk = " 🔑" if c.nombre in o.clave_primaria else ""
                    h.append(f"<tr><td><code>{e(c.nombre)}</code>{pk}</td><td><code>{e(tipo)}</code>{e(extra)}</td>"
                             f"<td>{'Sí' if c.nulo else 'No'}</td><td>{e(c.descripcion)}</td></tr>")
                h.append("</table>")
            deps, usos = sorted(o.depende_de), sorted(inverso.get(o.nombre, []))
            if deps or usos:
                h.append("<div class='sub' style='margin-top:8px'>")
                if deps:
                    h.append("Depende de: " + ", ".join(f"<a href='#{mermaid_id(d)}'><code>{e(simple(d))}</code></a>" for d in deps) + "<br>")
                if usos:
                    h.append("Usado por: " + ", ".join(f"<a href='#{mermaid_id(u)}'><code>{e(simple(u))}</code></a>" for u in usos))
                h.append("</div>")
            if o.definicion and o.tipo_sql != "SqlTable":
                h.append(f"<details><summary>Ver definición</summary><pre>{e(o.definicion)}</pre></details>")
            if hist.get(o.nombre):
                h.append("<details><summary>Historial de cambios</summary><table><tr><th>Commit</th><th>Fecha</th><th>Autor</th><th>Mensaje</th></tr>")
                for c in hist[o.nombre]:
                    h.append(f"<tr><td><code>{e(c['sha'])}</code></td><td>{e(c['fecha'])}</td><td>{e(c['autor'])}</td><td>{e(c['mensaje'])}</td></tr>")
                h.append("</table></details>")
            h.append("</div>")
    h.append("<footer>Generado automáticamente desde el repositorio. No editar a mano: se regenera en cada despliegue a producción.</footer></div>")
    h.append("""<script>function filtrar(q){q=q.toLowerCase();document.querySelectorAll('.obj').forEach(function(d){
d.style.display=d.textContent.toLowerCase().indexOf(q)>=0?'':'none';});}</script></body></html>""")
    (out / "index.html").write_text("\n".join(h), encoding="utf-8")
    # catálogo en JSON para otros consumidores (ej. un catálogo corporativo)
    catalogo = [{"objeto": o.nombre_simple, "tipo": o.tipo, "descripcion": o.descripcion,
                 "columnas": [c.__dict__ for c in o.columnas], "depende_de": [simple(d) for d in sorted(o.depende_de)]}
                for o in objetos.values()]
    (out / "catalogo.json").write_text(json.dumps(catalogo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Diccionario generado en {out}/index.html ({len(objetos)} objetos)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cambio")
    c.add_argument("--dacpac-nuevo", required=True)
    c.add_argument("--dacpac-base")
    for x in ("riesgo", "pruebas", "smoke", "jobs", "upgrade", "script", "build-log", "contexto"):
        c.add_argument(f"--{x}")
    c.add_argument("--salida-md", default="reporte/comentario.md")
    c.add_argument("--salida-html", default="reporte/reporte_cambio.html")
    c.set_defaults(f=cmd_cambio)
    s = sub.add_parser("sitio")
    s.add_argument("--dacpac", required=True)
    s.add_argument("--proyecto", default="database")
    s.add_argument("--releases")
    s.add_argument("--version")
    s.add_argument("--salida", default="sitio")
    s.set_defaults(f=cmd_sitio)
    a = p.parse_args()
    for attr in ("salida_md", "salida_html"):
        if getattr(a, attr, None):
            Path(getattr(a, attr)).parent.mkdir(parents=True, exist_ok=True)
    a.f(a)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        print("::error title=Documentación automática::" + tb.replace("%", "%25").replace("\n", "%0A")[-3000:])
        sys.exit(1)
